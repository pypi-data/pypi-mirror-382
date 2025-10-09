import asyncio
import datetime
import itertools
from datetime import timedelta
from decimal import Decimal
from enum import Enum, auto
from typing import List, Dict, Any, Type, Set, Optional, Callable

import httpx
import numpy
from async_lru import alru_cache
from pydantic import ConfigDict
from scipy.stats import norm

from sirius import common
from sirius.common import DataClass, Currency
from sirius.exceptions import OperationNotSupportedException
from sirius.http_requests import AsyncHTTPSession, HTTPResponse, ServerSideException

_account_list: List["IBKRAccount"] = []
_account_list_lock = asyncio.Lock()

base_url: str = common.get_environmental_secret("IBKR_SERVICE_BASE_URL", "https://ibkr-service:5000/v1/api/")
session: AsyncHTTPSession = AsyncHTTPSession(base_url)
session.client = httpx.AsyncClient(verify=False, timeout=60)
OPTIONS_DATE_FORMAT: str = "%b%y"


def calculate_annualized_return(starting: Decimal, ending: Decimal, number_of_days: int) -> Decimal:
    daily_return = (ending / starting)
    annualization_factor = Decimal("365") / Decimal(number_of_days)
    annualized_return = daily_return ** annualization_factor - Decimal("1")
    return annualized_return


class ContractType(Enum):
    STOCK = "STK"
    OPTION = "OPT"
    FUTURE = "FUT"
    FUTURE_OPTION = "FOP"
    BOND = "BND"


class OptionContractType(Enum):
    PUT = auto()
    CALL = auto()


class Exchange(Enum):
    NASDAQ = "NASDAQ"


class IBKRAccount(DataClass):
    id: str
    name: str

    @staticmethod
    async def get_all_ibkr_accounts() -> List["IBKRAccount"]:
        global _account_list
        if len(_account_list) == 0:
            async with _account_list_lock:
                if len(_account_list) == 0:
                    response: HTTPResponse = await session.get(f"{base_url}/portfolio/accounts/")
                    _account_list = [IBKRAccount(id=data["id"], name=data["accountAlias"] if data["accountAlias"] else data["id"]) for data in response.data]

        return _account_list


class Contract(DataClass):
    id: int
    name: str
    symbol: str
    currency: Currency

    @staticmethod
    def _get_contract_subclass(contract_type_str: str) -> Type["Contract"]:
        try:
            return {  # type: ignore[return-value]
                "STK": StockContract,
                "OPT": OptionContract,
                "FUT": FutureContract,
                "FOP": FuturesOptionContract,
                "BOND": BondContract,
            }[contract_type_str]
        except KeyError:
            raise OperationNotSupportedException(f"Unknown contract type string: {contract_type_str}")

    @staticmethod
    async def get(contract_id: int) -> "Contract":
        response: HTTPResponse = await session.get(f"{base_url}iserver/contract/{contract_id}/info")
        cls: Type[Contract] = Contract._get_contract_subclass(response.data["instrument_type"])
        return cls(
            id=contract_id,
            name=response.data["company_name"],
            symbol=response.data["symbol"],
            currency=Currency(response.data["currency"]),
        )

    @staticmethod
    async def find_contract_id(ticker: str, contract_type: ContractType) -> List[int]:
        response: HTTPResponse = await session.get(f"{base_url}iserver/secdef/search?symbol={ticker}&secType={contract_type.value}")
        valid_result_list: List[Dict[str, Any]] = list(filter(lambda d: d["description"] in Exchange, response.data))
        return [int(data["conid"]) for data in valid_result_list]

    @staticmethod
    async def find_contract(ticker: str, contract_type: ContractType) -> List["Contract"]:
        contract_id_list: List[int] = await Contract.find_contract_id(ticker, contract_type)
        return [await Contract.get(contract_id) for contract_id in contract_id_list]


class StockContract(Contract):
    model_config = ConfigDict(frozen=True)  # Makes this immutable, needed for the alru_cache


class FutureContract(Contract):
    pass


class BondContract(Contract):
    pass


class OptionContract(Contract):
    strike_price: Decimal
    expiry_date: datetime.date
    type: OptionContractType
    underlying_contract: StockContract | FutureContract

    @staticmethod
    async def get_all_expiry_month_list(underlying_contract: StockContract, number_of_days_to_expiry: int | None = None) -> List[datetime.date]:
        number_of_days_to_expiry = 3 if not number_of_days_to_expiry else number_of_days_to_expiry
        response: HTTPResponse = await session.get(f"{base_url}iserver/secdef/search?symbol={underlying_contract.symbol}&secType={ContractType.STOCK.value}")
        data: Dict[str, Any] = next(filter(lambda c: int(c["conid"]) == underlying_contract.id, response.data))
        option_data: Dict[str, Any] = next(filter(lambda o: ContractType(o["secType"]) == ContractType.OPTION, data["sections"]))
        all_expiry_month_str_list: List[str] = option_data["months"].split(";")
        all_expiry_month_list: List[datetime.date] = [datetime.datetime.strptime(expiry_month, OPTIONS_DATE_FORMAT).date() for expiry_month in all_expiry_month_str_list]

        return [date for date in all_expiry_month_list if (date - datetime.datetime.now().date()).days <= number_of_days_to_expiry]

    @staticmethod
    async def get_all(underlying_contract: StockContract, expiry_month: datetime.date, strike_price: Decimal) -> List["OptionContract"]:
        expiry_month_str: str = expiry_month.strftime(OPTIONS_DATE_FORMAT).upper()
        response: HTTPResponse = await session.get(
            f"{base_url}iserver/secdef/info",
            query_params={
                "conid": underlying_contract.id,
                "sectype": ContractType.OPTION.value,
                "month": expiry_month_str,
                "strike": float(strike_price)}
        )

        return [OptionContract(
            **underlying_contract.model_dump(exclude={"id"}),
            id=data["conid"],
            strike_price=strike_price,
            expiry_date=datetime.datetime.strptime(data["maturityDate"], '%Y%m%d').date(),
            type=OptionContractType.CALL if data["right"] == "C" else OptionContractType.PUT,
            underlying_contract=underlying_contract
        ) for data in response.data]

    @staticmethod
    @alru_cache(maxsize=50, ttl=43_200)  # 12 hour cache
    async def find_all(underlying_contract: StockContract, number_of_days_to_expiry: int | None = None) -> List["OptionContract"]:
        option_contract_list: List[OptionContract] = []
        expiry_month_list: List[datetime.date] = await OptionContract.get_all_expiry_month_list(underlying_contract, number_of_days_to_expiry)
        expiry_month_str_list: List[str] = [expiry_month.strftime(OPTIONS_DATE_FORMAT).upper() for expiry_month in expiry_month_list]

        responses: List[HTTPResponse] = await asyncio.gather(*[
            session.get(f"{base_url}iserver/secdef/strikes", query_params={"conid": underlying_contract.id, "sectype": ContractType.OPTION.value, "month": expiry_month_str})
            for expiry_month_str in expiry_month_str_list
        ])
        for expiry_month, response in zip(expiry_month_list, responses):
            all_strike_price_set: Set[Decimal] = set([Decimal(str(strike_price)) for strike_price in response.data.get("call", [])])
            all_strike_price_set.update([Decimal(str(strike_price)) for strike_price in response.data.get("put", [])])
            all_option_contract_list: List[OptionContract] = list(itertools.chain.from_iterable(await asyncio.gather(*[
                OptionContract.get_all(underlying_contract, expiry_month, strike_price)
                for strike_price in all_strike_price_set
            ])))

            option_contract_list.extend(
                [option
                 for option in all_option_contract_list
                 if (option.expiry_date - datetime.datetime.now().date()).days == number_of_days_to_expiry]
            )

        return option_contract_list


class FuturesOptionContract(Contract):
    pass


class MarketData(DataClass):
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    date: datetime.date

    @staticmethod
    def _get_from_ohlc_data(ohlc_data: Dict[str, float]) -> "MarketData":
        return MarketData(
            open=Decimal(str(ohlc_data["o"])),
            high=Decimal(str(ohlc_data["h"])),
            low=Decimal(str(ohlc_data["l"])),
            close=Decimal(str(ohlc_data["c"])),
            volume=Decimal(str(ohlc_data["v"])),
            date=datetime.datetime.fromtimestamp(ohlc_data["t"] / 1000).date(),
        )

    @staticmethod
    async def _get_ohlc_data(contract_id: int, to_date: Optional[datetime.date] = None) -> List[Dict[str, float]]:
        DATE_FORMAT: str = "%Y%m%d-%H:%M:%S"
        to_date = to_date or datetime.datetime.now().date()

        try:
            response = await session.get(
                f"{base_url}iserver/marketdata/history",
                query_params={
                    "conid": contract_id,
                    "period": "999d",
                    "bar": "1d",
                    "startTime": to_date.strftime(DATE_FORMAT),
                    "direction": "-1"
                }
            )
        except ServerSideException as e:
            raise ServerSideException("Did not retrieve any historical market data due to: " + str(e))

        data = response.data.get("data", [])
        response_from_time = datetime.datetime.strptime(response.data["startTime"], DATE_FORMAT).date()

        if (datetime.datetime.now().date() - response_from_time).days < (365.25 * 10):  # 10 years
            more_data = await MarketData._get_ohlc_data(contract_id, response_from_time)
            return list(itertools.chain(data, more_data))

        return data

    @staticmethod
    @alru_cache(maxsize=50, ttl=43_200)  # 12 hour cache
    async def get(contract_id: int) -> Dict[datetime.date, "MarketData"]:
        market_data_list: List[MarketData] = [MarketData._get_from_ohlc_data(ohlc_data) for ohlc_data in await MarketData._get_ohlc_data(contract_id)]
        return {market_data.date: market_data for market_data in market_data_list}

    @staticmethod
    @alru_cache(maxsize=50, ttl=600)  # 5 min cache
    async def get_latest_price(contract_id: int) -> Decimal:
        is_response_valid: Callable = lambda r: "31" in r.data[0].keys() and r.data[0]["31"] != ""
        number_of_tries: int = 1
        response: HTTPResponse = await session.get(f"{base_url}iserver/marketdata/snapshot", query_params={"conids": contract_id, "fields": "7295,70,71,31,87"})
        while number_of_tries < 5 and not is_response_valid(response):
            await asyncio.sleep(0.1)
            response = await session.get(f"{base_url}iserver/marketdata/snapshot", query_params={"conids": contract_id, "fields": "7295,70,71,31,87"})
            number_of_tries = number_of_tries + 1

        if not is_response_valid(response):
            raise ServerSideException("Did not retrieve any market data.")

        return Decimal(response.data[0]["31"].replace("H", "").replace("C", ""))


class ContractPerformance(DataClass):
    position_open: MarketData
    position_close: MarketData
    absolute_return: Decimal
    annualized_return: Decimal

    @staticmethod
    def _construct(position_open: MarketData, position_close: MarketData) -> "ContractPerformance":
        absolute_return: Decimal = (position_close.close - position_open.close) / position_open.close
        number_of_days = Decimal((position_close.date - position_open.date).days)
        annualized_return = calculate_annualized_return(position_open.close, position_close.close, int(number_of_days))

        return ContractPerformance(
            position_open=position_open,
            position_close=position_close,
            absolute_return=absolute_return,
            annualized_return=annualized_return
        )

    @staticmethod
    async def get(contract_id: int, position_start_date: datetime.date, number_of_days: int) -> Optional["ContractPerformance"]:
        position_close_date: datetime.date = position_start_date + timedelta(days=number_of_days)
        market_data_map: Dict[datetime.date, MarketData] = await MarketData.get(contract_id)
        position_open = market_data_map.get(position_start_date)
        position_close = market_data_map.get(position_close_date)

        if not position_open or not position_close:
            return None

        return ContractPerformance._construct(position_open, position_close)


class ContractPerformanceAnalysis(DataClass):
    contract_performance_list: List[ContractPerformance]
    standard_deviation_absolute_return: Decimal
    standard_deviation_annualized_return: Decimal
    mean_absolute_return: Decimal
    mean_annualized_return: Decimal
    median_absolute_return: Decimal
    median_annualized_return: Decimal
    min_absolute_return: Decimal
    min_annualized_return: Decimal
    max_absolute_return: Decimal
    max_annualized_return: Decimal

    @staticmethod
    async def _get_contract_performance_list(contract_id: int, number_of_days_invested: int, number_of_days_to_analyse: int, analysis_end_date: datetime.date) -> List["ContractPerformance"]:
        analysis_dates_list = [analysis_end_date - datetime.timedelta(days=day) for day in range(number_of_days_to_analyse)]
        performances_tasks = [ContractPerformance.get(contract_id, date, number_of_days_invested) for date in analysis_dates_list]
        contract_performance_results = await asyncio.gather(*performances_tasks)

        return [result for result in contract_performance_results if result is not None]

    @staticmethod
    @alru_cache(maxsize=50, ttl=600)  # 5 min cache
    async def get(contract_id: int, number_of_days_invested: int, number_of_days_to_analyse: int, analysis_end_date: datetime.date | None = None) -> "ContractPerformanceAnalysis":
        analysis_end_date = analysis_end_date if analysis_end_date else datetime.datetime.now().date()
        contract_performance_list: List[ContractPerformance] = await ContractPerformanceAnalysis._get_contract_performance_list(contract_id, number_of_days_invested, number_of_days_to_analyse, analysis_end_date)

        if not contract_performance_list:
            raise ServerSideException("Did not retrieve any Market Data")

        absolute_return_list: List[Decimal] = [contract_performance.absolute_return for contract_performance in contract_performance_list]
        annualized_return_list: List[Decimal] = [contract_performance.annualized_return for contract_performance in contract_performance_list]
        standard_deviation_absolute_return: Decimal = Decimal(str(numpy.std(absolute_return_list)))  # type: ignore[arg-type]
        standard_deviation_annualized_return: Decimal = Decimal(str(numpy.std(annualized_return_list)))  # type: ignore[arg-type]
        mean_absolute_return: Decimal = Decimal(str(numpy.mean(absolute_return_list)))  # type: ignore[arg-type]
        mean_annualized_return: Decimal = Decimal(str(numpy.mean(annualized_return_list)))  # type: ignore[arg-type]
        median_absolute_return: Decimal = Decimal(str(numpy.median(absolute_return_list)))  # type: ignore[arg-type]
        median_annualized_return: Decimal = Decimal(str(numpy.median(annualized_return_list)))  # type: ignore[arg-type]
        min_absolute_return: Decimal = Decimal(str(numpy.min(absolute_return_list)))  # type: ignore[arg-type]
        min_annualized_return: Decimal = Decimal(str(numpy.min(annualized_return_list)))  # type: ignore[arg-type]
        max_absolute_return: Decimal = Decimal(str(numpy.max(absolute_return_list)))  # type: ignore[arg-type]
        max_annualized_return: Decimal = Decimal(str(numpy.max(annualized_return_list)))  # type: ignore[arg-type]

        return ContractPerformanceAnalysis(
            contract_performance_list=contract_performance_list,
            standard_deviation_absolute_return=standard_deviation_absolute_return,
            standard_deviation_annualized_return=standard_deviation_annualized_return,
            mean_absolute_return=mean_absolute_return,
            mean_annualized_return=mean_annualized_return,
            median_absolute_return=median_absolute_return,
            median_annualized_return=median_annualized_return,
            min_absolute_return=min_absolute_return,
            min_annualized_return=min_annualized_return,
            max_absolute_return=max_absolute_return,
            max_annualized_return=max_annualized_return
        )


class OptionPerformanceAnalysis(DataClass):
    option_contract: OptionContract
    contract_performance_analysis: ContractPerformanceAnalysis
    itm_probability: Decimal

    @staticmethod
    async def get(option_contract: OptionContract) -> "OptionPerformanceAnalysis":
        today: datetime.date = datetime.datetime.now().date()
        number_of_days_to_analyse: int = (today - today.replace(year=today.year - 10)).days
        number_of_days_invested: int = (option_contract.expiry_date - datetime.datetime.now().date()).days
        underlying_price: Decimal = await MarketData.get_latest_price(option_contract.underlying_contract.id)
        itm_required_absolute_return: Decimal = (option_contract.strike_price - underlying_price) / underlying_price
        contract_performance_analysis: ContractPerformanceAnalysis = await ContractPerformanceAnalysis.get(option_contract.underlying_contract.id, number_of_days_invested, number_of_days_to_analyse)
        itm_probability_func: Callable[[], Decimal] = lambda: Decimal(str(norm.cdf(float(itm_required_absolute_return), float(contract_performance_analysis.mean_absolute_return), float(contract_performance_analysis.standard_deviation_absolute_return))))
        itm_probability: Decimal = itm_probability_func() if option_contract.type == OptionContractType.PUT else Decimal("1") - itm_probability_func()

        return OptionPerformanceAnalysis(
            option_contract=option_contract,
            contract_performance_analysis=contract_performance_analysis,
            itm_probability=itm_probability
        )
