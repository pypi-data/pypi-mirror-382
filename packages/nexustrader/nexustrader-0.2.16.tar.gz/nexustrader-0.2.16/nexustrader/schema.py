import pandas as pd
from decimal import Decimal
from typing import Dict, List, Any
from typing import Optional
from msgspec import Struct, field
from nexustrader.core.nautilius_core import UUID4
from nexustrader.constants import (
    OrderSide,
    OrderType,
    TimeInForce,
    OrderStatus,
    PositionSide,
    InstrumentType,
    ExchangeType,
    AlgoOrderStatus,
    KlineInterval,
    TriggerType,
)


class BatchOrder(Struct, kw_only=True):
    symbol: str
    side: OrderSide
    type: OrderType
    amount: Decimal
    price: Decimal | None = None  # for market order, the price is None
    time_in_force: TimeInForce | None = TimeInForce.GTC
    reduce_only: bool = False
    kwargs: Dict[str, Any] = field(default_factory=dict)


class Symbol(str):
    """Symbol class that inherits from string with all InstrumentId methods."""

    def __new__(cls, value: str):
        instance = str.__new__(cls, value)
        instance._instrument_id = None
        return instance

    def __init__(self, value: str):
        super().__init__()
        self._instrument_id = InstrumentId.from_str(value)

    @property
    def is_spot(self) -> bool:
        return self._instrument_id.is_spot

    @property
    def is_linear(self) -> bool:
        return self._instrument_id.is_linear

    @property
    def is_inverse(self) -> bool:
        return self._instrument_id.is_inverse

    @property
    def id(self) -> str:
        """Get the id from the symbol."""
        return self._instrument_id.id

    @property
    def exchange(self) -> ExchangeType:
        """Get the exchange from the symbol."""
        return self._instrument_id.exchange

    @property
    def type(self) -> InstrumentType:
        """Get the instrument type from the symbol."""
        return self._instrument_id.type


class InstrumentId(Struct):
    id: str
    symbol: str
    exchange: ExchangeType
    type: InstrumentType

    @property
    def is_spot(self) -> bool:
        return self.type == InstrumentType.SPOT

    @property
    def is_linear(self) -> bool:
        return self.type == InstrumentType.LINEAR

    @property
    def is_inverse(self) -> bool:
        return self.type == InstrumentType.INVERSE

    @classmethod
    def from_str(cls, symbol: str):
        """
        BTCETH.BINANCE -> SPOT
        BTCUSDT-PERP.BINANCE -> LINEAR
        BTCUSD.BINANCE -> INVERSE
        BTCUSD-241227.BINANCE
        """
        symbol_prefix, exchange = symbol.split(".")

        # if numirical number in id, then it is a future
        if "-" in symbol_prefix:
            prefix, _ = symbol_prefix.split("-")
            if prefix.endswith("USD"):
                type = InstrumentType.INVERSE
            else:
                type = InstrumentType.LINEAR
        else:
            type = InstrumentType.SPOT

        return cls(
            id=symbol_prefix,
            symbol=symbol,
            exchange=ExchangeType(exchange.lower()),
            type=type,
        )


class BookL1(Struct, gc=False, frozen=True):
    exchange: ExchangeType
    symbol: str
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    timestamp: int

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2

    @property
    def spread(self) -> float:
        return self.ask - self.bid

    @property
    def weighted_mid(self) -> float:
        return (self.bid * self.ask_size + self.ask * self.bid_size) / (
            self.ask_size + self.bid_size
        )


class BookOrderData(Struct, gc=False, frozen=True):
    price: float
    size: float


class BookL2(Struct, frozen=True):
    exchange: ExchangeType
    symbol: str
    bids: List[BookOrderData]  # desc order
    asks: List[BookOrderData]  # asc order
    timestamp: int


class Trade(Struct, gc=False, frozen=True):
    exchange: ExchangeType
    side: OrderSide
    symbol: str
    price: float
    size: float
    timestamp: int


class Kline(Struct, gc=False, kw_only=True, frozen=True):
    exchange: ExchangeType
    symbol: str
    interval: KlineInterval
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None
    quote_volume: float | None = None  # only for binance and okx
    taker_volume: float | None = None  # only for binance
    taker_quote_volume: float | None = None  # only for binance
    turnover: float | None = None  # only for bybit
    start: int
    timestamp: int
    confirm: bool


class MarkPrice(Struct, gc=False, frozen=True):
    exchange: ExchangeType
    symbol: str
    price: float
    timestamp: int


class FundingRate(Struct, gc=False, frozen=True):
    exchange: ExchangeType
    symbol: str
    rate: float
    timestamp: int
    next_funding_time: int


class Ticker(Struct, gc=False, kw_only=True):
    """
    Universal ticker data structure supporting all exchanges.
    volumeCcy: for linear and spot markets, it is the volume in quote currency.
    For inverse markets, it is the volume in base currency.
    """

    exchange: ExchangeType
    symbol: str
    last_price: float
    timestamp: int
    volume: float
    volumeCcy: float


class IndexPrice(Struct, gc=False, frozen=True):
    exchange: ExchangeType
    symbol: str
    price: float
    timestamp: int


class OrderSubmit(Struct):
    symbol: str
    instrument_id: InstrumentId
    kwargs: Dict[str, Any] = field(default_factory=dict)


class BatchOrderSubmit(OrderSubmit, kw_only=True):
    oid: str
    side: OrderSide
    type: OrderType
    amount: Decimal
    price: Decimal | None = None  # for market order, the price is None
    time_in_force: TimeInForce | None = TimeInForce.GTC
    reduce_only: bool = False


class CreateOrderSubmit(OrderSubmit, kw_only=True):
    oid: str
    side: OrderSide
    type: OrderType
    amount: Decimal
    price: Decimal | None = None  # for market order, the price is None
    time_in_force: TimeInForce | None = TimeInForce.GTC
    reduce_only: bool = False
    # position_side: PositionSide | None = None


class CancelOrderSubmit(OrderSubmit, kw_only=True):
    oid: str


class CancelAllOrderSubmit(OrderSubmit, kw_only=True):
    pass


class TakeProfitAndStopLossOrderSubmit(CreateOrderSubmit, kw_only=True):
    tp_order_type: OrderType
    tp_trigger_price: Decimal | None = None
    tp_price: Decimal | None = None
    tp_trigger_type: TriggerType = TriggerType.LAST_PRICE
    sl_order_type: OrderType
    sl_trigger_price: Decimal | None = None
    sl_price: Decimal | None = None
    sl_trigger_type: TriggerType = TriggerType.LAST_PRICE


class TWAPOrderSubmit(OrderSubmit, kw_only=True):
    uuid: str = field(default_factory=lambda: f"ALGO-{UUID4().value}")
    side: OrderSide
    amount: Decimal
    duration: int
    wait: int
    position_side: PositionSide
    check_interval: float = 0.1


class CancelTWAPOrderSubmit(OrderSubmit, kw_only=True):
    uuid: str


class ModifyOrderSubmit(OrderSubmit, kw_only=True):
    oid: str
    side: OrderSide
    price: Decimal
    amount: Decimal


class Order(Struct):
    exchange: ExchangeType
    symbol: str
    status: OrderStatus
    oid: Optional[str] = None
    eid: Optional[str] = None
    amount: Optional[Decimal] = None
    filled: Optional[Decimal] = None
    timestamp: Optional[int] = None
    type: Optional[OrderType] = None
    side: Optional[OrderSide] = None
    time_in_force: Optional[TimeInForce] = None
    price: Optional[float] = None
    trigger_price: Optional[float] = None
    average: Optional[float] = None
    last_filled_price: Optional[float] = None
    last_filled: Optional[Decimal] = None
    remaining: Optional[Decimal] = None
    fee: Optional[Decimal] = None
    fee_currency: Optional[str] = None
    cost: Optional[Decimal] = None
    cum_cost: Optional[Decimal] = None
    reduce_only: Optional[bool] = None
    position_side: Optional[PositionSide] = None

    @property
    def success(self) -> bool:
        return self.status not in [OrderStatus.FAILED, OrderStatus.CANCEL_FAILED]

    @property
    def is_filled(self) -> bool:
        return self.status == OrderStatus.FILLED

    @property
    def is_pending(self) -> bool:
        return self.status == OrderStatus.PENDING

    @property
    def is_accepted(self) -> bool:
        return self.status == OrderStatus.ACCEPTED

    @property
    def is_partially_filled(self) -> bool:
        return self.status == OrderStatus.PARTIALLY_FILLED

    @property
    def is_partially_canceled(self) -> bool:
        return self.status == OrderStatus.CANCELED and self.filled > Decimal("0")

    @property
    def is_canceled(self) -> bool:
        return self.status == OrderStatus.CANCELED

    @property
    def is_closed(self) -> bool:
        return self.status in [
            OrderStatus.FILLED,
            OrderStatus.CANCELED,
            OrderStatus.EXPIRED,
            OrderStatus.CANCEL_FAILED,
            OrderStatus.FAILED,
        ]

    @property
    def is_opened(self) -> bool:
        return self.status in [
            OrderStatus.PENDING,
            OrderStatus.CANCELING,
            OrderStatus.PARTIALLY_FILLED,
            OrderStatus.ACCEPTED,
        ]

    @property
    def on_flight(self) -> bool:
        return self.status in [
            OrderStatus.PENDING,
            OrderStatus.CANCELING,
        ]

    @property
    def is_buy(self) -> bool:
        return self.side == OrderSide.BUY

    @property
    def is_sell(self) -> bool:
        return self.side == OrderSide.SELL

    @property
    def is_maker(self) -> bool:
        return self.type == OrderType.LIMIT

    @property
    def is_taker(self) -> bool:
        return self.type == OrderType.MARKET

    @property
    def is_post_only(self) -> bool:
        return self.type == OrderType.POST_ONLY


class AlgoOrder(Struct, kw_only=True):
    symbol: str
    oid: str  # start with "ALGO-"
    side: OrderSide
    amount: Optional[Decimal] = None
    duration: int
    wait: int
    status: AlgoOrderStatus
    exchange: ExchangeType
    timestamp: int
    orders: List[str] = field(default_factory=list)  # [uuid1, uuid2, ...]
    position_side: PositionSide | None = None
    filled: Optional[Decimal] = None
    cost: Optional[float] = None
    average: Optional[float] = None

    @property
    def success(self) -> bool:
        return not self.is_failed

    @property
    def is_running(self) -> bool:
        return self.status == AlgoOrderStatus.RUNNING

    @property
    def is_finished(self) -> bool:
        return self.status == AlgoOrderStatus.FINISHED

    @property
    def is_canceled(self) -> bool:
        return self.status == AlgoOrderStatus.CANCELED

    @property
    def is_failed(self) -> bool:
        return self.status == AlgoOrderStatus.FAILED

    @property
    def is_closed(self) -> bool:
        return self.status in [
            AlgoOrderStatus.CANCELED,
            AlgoOrderStatus.FAILED,
            AlgoOrderStatus.FINISHED,
        ]

    @property
    def is_opened(self) -> bool:
        return self.status in [AlgoOrderStatus.RUNNING, AlgoOrderStatus.CANCELING]


class Balance(Struct):
    """
    Buy BTC/USDT: amount = 0.01, cost: 600

    OrderStatus.INITIALIZED: BTC(free: 0.0, locked: 0.0) USDT(free: 1000, locked: 0)
    OrderStatus.PENDING: BTC(free: 0.0, locked: 0) USDT(free: 400, locked: 600) USDT.update_locked(600) USDT.update_free(-600)

    OrderStatus.PARTIALLY_FILLED: BTC(free: 0.005, locked: 0) USDT(free: 400, locked: 300) BTC.update_free(0.005) USDT.update_locked(-300)
    OrderStatus.FILLED: BTC(free: 0.01, locked: 0.0) USDT(free: 400, locked: 0) BTC.update_free(0.005) USDT.update_locked(-300)

    Buy BTC/USDT: amount = 0.01, cost: 200

    OrderStatus.INITIALIZED: BTC(free: 0.01, locked: 0.0) USDT(free: 400, locked: 0)
    OrderStatus.PENDING: BTC(free: 0.01, locked: 0.0) USDT(free: 200, locked: 200) USDT.update_locked(200) USDT.update_free(-200)
    OrderStatus.FILLED: BTC(free: 0.02, locked: 0.0) USDT(free: 200, locked: 0) BTC.update_free(0.01) USDT.update_locked(-200)

    Sell BTC/USDT: amount = 0.01, cost: 300
    OrderStatus.INITIALIZED: BTC(free: 0.02, locked: 0.0) USDT(free: 200, locked: 0)
    OrderStatus.PENDING: BTC(free: 0.01, locked: 0.01) USDT(free: 200, locked: 0) BTC.update_locked(0.01) BTC.update_free(-0.01)
    OrderStatus.PARTIALLY_FILLED: BTC(free: 0.01, locked: 0.005) USDT(free: 350, locked: 0) BTC.update_locked(-0.005) USDT.update_free(150)
    OrderStatus.FILLED: BTC(free: 0.01, locked: 0.0) USDT(free: 500, locked: 0) BTC.update_locked(-0.005) USDT.update_free(150)
    """

    asset: str
    free: Decimal = field(default=Decimal("0.0"))
    locked: Decimal = field(default=Decimal("0.0"))

    @property
    def total(self) -> Decimal:
        return self.free + self.locked


class AccountBalance(Struct):
    balances: Dict[str, Balance] = field(default_factory=dict)

    def _apply(self, balances: List[Balance]):
        for balance in balances:
            self.balances[balance.asset] = balance

    def _update_free(self, asset: str, amount: Decimal):
        if asset not in self.balances:
            raise ValueError(
                f"Asset {asset} not found in balances. Please add it in MockConnectorConfig"
            )
        self.balances[asset].free += amount

    def _update_locked(self, asset: str, amount: Decimal):
        if asset not in self.balances:
            raise ValueError(
                f"Asset {asset} not found in balances. Please add it in MockConnectorConfig"
            )
        self.balances[asset].locked += amount

    @property
    def balance_total(self) -> Dict[str, Decimal]:
        return {asset: balance.total for asset, balance in self.balances.items()}

    @property
    def balance_free(self) -> Dict[str, Decimal]:
        return {asset: balance.free for asset, balance in self.balances.items()}

    @property
    def balance_locked(self) -> Dict[str, Decimal]:
        return {asset: balance.locked for asset, balance in self.balances.items()}


class Precision(Struct):
    """
     "precision": {
      "amount": 0.0001,
      "price": 1e-05,
      "cost": null,
      "base": 1e-08,
      "quote": 1e-08
    },
    """

    amount: float | None = None
    price: float | None = None
    cost: float | None = None
    base: float | None = None
    quote: float | None = None


class LimitMinMax(Struct):
    """
    "limits": {
      "amount": {
        "min": 0.0001,
        "max": 1000.0
      },
      "price": {
        "min": 1e-05,
        "max": 1000000.0
      },
      "cost": {
        "min": 0.01,
        "max": 1000000.0
      }
    },
    """

    min: float | None
    max: float | None


class Limit(Struct):
    leverage: LimitMinMax = None
    amount: LimitMinMax = None
    price: LimitMinMax = None
    cost: LimitMinMax = None
    market: LimitMinMax = None


class MarginMode(Struct):
    isolated: bool | None
    cross: bool | None


class BaseMarket(Struct):
    """Base market structure for all exchanges."""

    id: str
    lowercaseId: str | None
    symbol: str
    base: str
    quote: str
    settle: str | None
    baseId: str
    quoteId: str
    settleId: str | None
    type: InstrumentType
    spot: bool
    margin: bool | None
    swap: bool
    future: bool
    option: bool
    index: bool | str | None
    active: bool
    contract: bool
    linear: bool | None
    inverse: bool | None
    subType: InstrumentType | None
    taker: float
    maker: float
    contractSize: float | None
    expiry: int | None
    expiryDatetime: str | None
    strike: float | str | None
    optionType: str | None
    precision: Precision
    limits: Limit
    marginModes: MarginMode
    created: int | None
    tierBased: bool | None
    percentage: bool | None
    # feeSide: str  # not supported by okx exchanges


"""
class Position(Struct):

    one-way mode:
    > order (side: buy) -> side: buy | pos_side: net/both | reduce_only: False [open long position]
    > order (side: sell) -> side: sell | pos_side: net/both | reduce_only: False [open short position]
    > order (side: buy, reduce_only=True) -> side: buy | pos_side: net/both | reduce_only: True [close short position]
    > order (side: sell, reduce_only=True) -> side: sell | pos_side: net/both | reduce_only: True [close long position]

    hedge mode:
    > order (side: buy, pos_side: long) -> side: buy | pos_side: long | reduce_only: False [open long position]
    > order (side: sell, pos_side: short) -> side: sell | pos_side: short | reduce_only: False [open short position]
    > order (side: sell, pos_side: long) -> side: sell | pos_side: long | reduce_only: True [close long position]
    > order (side: buy, pos_side: short) -> side: buy | pos_side: short | reduce_only: True [close short position]

    
"""


class Position(Struct):
    symbol: str
    exchange: ExchangeType
    signed_amount: Decimal = Decimal("0")
    entry_price: float = 0
    side: Optional[PositionSide] = None
    unrealized_pnl: float = 0
    realized_pnl: float = 0

    @property
    def amount(self, contract_size: Decimal = Decimal("1")) -> Decimal:
        return abs(self.signed_amount) * contract_size

    @property
    def is_opened(self) -> bool:
        return self.amount != Decimal("0")

    @property
    def is_closed(self) -> bool:
        return not self.is_opened

    @property
    def is_long(self) -> bool:
        return self.side == PositionSide.LONG

    @property
    def is_short(self) -> bool:
        return self.side == PositionSide.SHORT


class KlineList(list[Kline]):
    def __init__(self, klines: list[Kline], fields: list[str] | None = None):
        super().__init__(klines)
        self._fields = fields or [
            "timestamp",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "confirm",
        ]
        # Validate that all fields exist in Kline
        for item in self._fields:
            if not hasattr(Kline, item) and item != "timestamp":
                raise ValueError(f"Field {item} does not exist in Kline")

    @property
    def df(self):
        data = {}
        for item in self._fields:
            if item == "timestamp":
                data[item] = [kline.start for kline in self]
            else:
                data[item] = [getattr(kline, item) for kline in self]

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("date", inplace=True)
        return df

    @property
    def values(self):
        return sorted(self, key=lambda x: x.timestamp)
