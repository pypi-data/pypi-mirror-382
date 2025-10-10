import os
import signal
import time
import copy
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Literal, Optional, Any
from decimal import Decimal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from collections import defaultdict
from nexustrader.base import ExchangeManager
from nexustrader.indicator import IndicatorManager, Indicator, IndicatorProxy
from nexustrader.core.entity import TaskManager, DataReady, is_redis_available
from nexustrader.core.cache import AsyncCache
from nexustrader.error import StrategyBuildError
from nexustrader.base import (
    ExecutionManagementSystem,
    PrivateConnector,
    PublicConnector,
)
from nexustrader.core.entity import OidGen
from nexustrader.core.nautilius_core import MessageBus, LiveClock, Logger
from nexustrader.schema import (
    BookL1,
    Trade,
    Kline,
    BookL2,
    Order,
    FundingRate,
    Ticker,
    IndexPrice,
    MarkPrice,
    InstrumentId,
    BaseMarket,
    AccountBalance,
    CreateOrderSubmit,
    TakeProfitAndStopLossOrderSubmit,
    # TWAPOrderSubmit,
    ModifyOrderSubmit,
    CancelOrderSubmit,
    CancelAllOrderSubmit,
    # CancelTWAPOrderSubmit,
    KlineList,
    BatchOrder,
    BatchOrderSubmit,
)
from nexustrader.constants import (
    DataType,
    BookLevel,
    OrderSide,
    OrderType,
    TimeInForce,
    # PositionSide,
    AccountType,
    SubmitType,
    ExchangeType,
    KlineInterval,
    TriggerType,
)


class Strategy:
    def __init__(self):
        self.log = Logger(name=type(self).__name__)

        self._subscriptions = {
            DataType.BOOKL1: set(),
            DataType.BOOKL2: defaultdict(set),
            DataType.TRADE: set(),
            DataType.KLINE: defaultdict(set),
            DataType.VOLUME_KLINE: {},
            DataType.FUNDING_RATE: set(),
            DataType.INDEX_PRICE: set(),
            DataType.MARK_PRICE: set(),
        }

        # Track which symbols use aggregator: {(interval, symbol): use_aggregator}
        self._kline_use_aggregator: list = []

        self._initialized = False
        self._scheduler = AsyncIOScheduler()
        self.indicator = IndicatorProxy()

    def _init_core(
        self,
        exchanges: Dict[ExchangeType, ExchangeManager],
        public_connectors: Dict[AccountType, PublicConnector],
        private_connectors: Dict[AccountType, PrivateConnector],
        cache: AsyncCache,
        msgbus: MessageBus,
        clock: LiveClock,
        task_manager: TaskManager,
        ems: Dict[ExchangeType, ExecutionManagementSystem],
        strategy_id: str = None,
        user_id: str = None,
        enable_cli: bool = False,
    ):
        if self._initialized:
            return

        self.cache = cache
        self.clock = clock
        self._oidgen = OidGen(clock)
        self._ems = ems
        self._task_manager = task_manager
        self._msgbus = msgbus
        self._private_connectors = private_connectors
        self._public_connectors = public_connectors
        self._exchanges = exchanges
        self._indicator_manager = IndicatorManager(self._msgbus)

        # Initialize state exporter if IDs are provided and Redis is fully available
        self._state_exporter = None
        if strategy_id and user_id and is_redis_available() and enable_cli:
            try:
                from nexustrader.cli.monitor.state_exporter import StrategyStateExporter

                self._state_exporter = StrategyStateExporter(
                    strategy_id=strategy_id, user_id=user_id, cache=cache, clock=clock
                )
                self.log.debug("CLI monitoring enabled with Redis")
            except Exception as e:
                self.log.debug(
                    f"State exporter initialization failed, CLI monitoring disabled: {e}"
                )
        elif strategy_id and user_id:
            self.log.debug("Redis not available, CLI monitoring disabled")

        self._msgbus.register(endpoint="pending", handler=self.on_pending_order)
        self._msgbus.register(endpoint="accepted", handler=self.on_accepted_order)
        self._msgbus.register(
            endpoint="partially_filled", handler=self.on_partially_filled_order
        )
        self._msgbus.register(endpoint="filled", handler=self.on_filled_order)
        self._msgbus.register(endpoint="canceling", handler=self.on_canceling_order)
        self._msgbus.register(endpoint="canceled", handler=self.on_canceled_order)
        self._msgbus.register(endpoint="failed", handler=self.on_failed_order)
        self._msgbus.register(
            endpoint="cancel_failed", handler=self.on_cancel_failed_order
        )

        self._msgbus.register(endpoint="balance", handler=self.on_balance)

        self._initialized = True

        self._subscriptions_ready: Dict[DataType | str, DataReady] = {}

    @property
    def ready(self):
        return all(
            data_ready.ready for data_ready in self._subscriptions_ready.values()
        )

    def api(self, account_type: AccountType):
        return self._private_connectors[account_type].api

    def register_indicator(
        self,
        symbols: str | List[str],
        indicator: Indicator,
        data_type: DataType,
        account_type: AccountType | None = None,
    ):
        if not self._initialized:
            raise StrategyBuildError(
                "Strategy not initialized, please use `register_indicator` in `on_start` method"
            )

        if isinstance(symbols, str):
            symbols = [symbols]

        # Create separate indicator instances for each symbol to avoid shared state
        for symbol in symbols:
            # Create a deep copy of the indicator for each symbol
            symbol_indicator = copy.deepcopy(indicator)

            # Register the symbol-specific indicator with the proxy
            self.indicator.register_indicator(indicator.name, symbol, symbol_indicator)

            match data_type:
                case DataType.BOOKL1:
                    self._indicator_manager.add_bookl1_indicator(
                        symbol, symbol_indicator
                    )
                case DataType.BOOKL2:
                    self._indicator_manager.add_bookl2_indicator(
                        symbol, symbol_indicator
                    )
                case DataType.KLINE:
                    self._indicator_manager.add_kline_indicator(
                        symbol, symbol_indicator
                    )
                    # Handle warmup for kline indicators
                    if symbol_indicator.requires_warmup:
                        if not account_type:
                            # Infer account type if not provided
                            account_type = self._infer_account_type(symbol)
                        self._perform_indicator_warmup(
                            symbol, symbol_indicator, account_type
                        )
                case DataType.TRADE:
                    self._indicator_manager.add_trade_indicator(
                        symbol, symbol_indicator
                    )
                case DataType.INDEX_PRICE:
                    self._indicator_manager.add_index_price_indicator(
                        symbol, symbol_indicator
                    )
                case DataType.FUNDING_RATE:
                    self._indicator_manager.add_funding_rate_indicator(
                        symbol, symbol_indicator
                    )
                case DataType.MARK_PRICE:
                    self._indicator_manager.add_mark_price_indicator(
                        symbol, symbol_indicator
                    )
                case _:
                    raise ValueError(f"Invalid data type: {data_type}")

    def _infer_account_type(self, symbol: str) -> AccountType:
        """
        Infer the account type based on the symbol's exchange and type.
        This is useful for methods that require an account type but don't have it explicitly provided.
        """
        instrument_id = InstrumentId.from_str(symbol)
        exchange = self._exchanges.get(instrument_id.exchange)
        if not exchange:
            raise ValueError(
                f"Exchange {instrument_id.exchange} not found, please add it to the config"
            )
        return exchange.instrument_id_to_account_type(instrument_id)

    def request_ticker(
        self,
        symbol: str,
        account_type: AccountType | None = None,
    ) -> Ticker:
        account_type = account_type or self._infer_account_type(symbol)
        connector = self._public_connectors.get(account_type)
        if not connector:
            raise ValueError(
                f"Account type {account_type} not found in public connectors"
            )
        return connector.request_ticker(symbol)

    def request_all_tickers(
        self,
        account_type: AccountType,
    ) -> Dict[str, Ticker]:
        connector = self._public_connectors.get(account_type)
        if not connector:
            raise ValueError(
                f"Account type {account_type} not found in public connectors"
            )
        return connector.request_all_tickers()

    def request_klines(
        self,
        symbol: str | List[str],
        interval: KlineInterval,
        limit: int | None = None,
        start_time: int | datetime | None = None,
        end_time: int | datetime | None = None,
        account_type: AccountType | None = None,
    ) -> KlineList:
        if isinstance(start_time, datetime):
            start_time = int(start_time.timestamp() * 1000)
        if isinstance(end_time, datetime):
            end_time = int(end_time.timestamp() * 1000)

        account_type = account_type or self._infer_account_type(symbol)
        connector = self._public_connectors.get(account_type)
        if not connector:
            raise ValueError(
                f"Account type {account_type} not found in public connectors"
            )

        if isinstance(symbol, str):
            symbol = [symbol]

        klines = KlineList([])
        for sym in symbol:
            res = connector.request_klines(
                symbol=sym,
                interval=interval,
                limit=limit,
                start_time=start_time,
                end_time=end_time,
            )
            klines.extend(res)
        return klines

    def request_index_klines(
        self,
        symbol: str | List[str],
        interval: KlineInterval,
        limit: int | None = None,
        start_time: int | datetime | None = None,
        end_time: int | datetime | None = None,
        account_type: AccountType | None = None,
    ) -> KlineList:
        if isinstance(start_time, datetime):
            start_time = int(start_time.timestamp() * 1000)
        if isinstance(end_time, datetime):
            end_time = int(end_time.timestamp() * 1000)
        account_type = account_type or self._infer_account_type(symbol)
        connector = self._public_connectors.get(account_type)
        if not connector:
            raise ValueError(
                f"Account type {account_type} not found in public connectors"
            )

        if isinstance(symbol, str):
            symbol = [symbol]

        klines = KlineList([])
        for sym in symbol:
            res = connector.request_index_klines(
                symbol=sym,
                interval=interval,
                limit=limit,
                start_time=start_time,
                end_time=end_time,
            )
            klines.extend(res)
        return klines

    def _perform_indicator_warmup(
        self, symbol: str, indicator: Indicator, account_type: AccountType
    ):
        """Automatically fetch historical data to warm up an indicator."""
        try:
            # Calculate how much historical data we need
            warmup_milliseconds = (
                indicator.warmup_period * indicator.kline_interval.milliseconds
            )
            start_time_ms = self.clock.timestamp_ms() - warmup_milliseconds

            # Fetch historical klines
            historical_klines = self.request_klines(
                symbol=symbol,
                account_type=account_type,
                interval=indicator.kline_interval,
                limit=indicator.warmup_period,
                start_time=start_time_ms,
            )

            # Process historical data for warmup (oldest first)
            for kline in historical_klines.values:
                if kline.symbol == symbol and kline.confirm:
                    indicator._process_warmup_kline(kline)

            self.log.debug(
                f"Warmed up indicator {indicator.name} for {symbol} with {len(historical_klines)} klines"
            )

        except Exception as e:
            self.log.error(
                f"Failed to warm up indicator {indicator.name} for {symbol}: {e}"
            )

    def get_warmup_status(self) -> dict[str, list[dict]]:
        """Get the warmup status of all indicators by symbol."""
        status = {}
        requirements = self._indicator_manager.get_warmup_requirements()

        for symbol, indicator_list in requirements.items():
            status[symbol] = []
            for indicator, period, interval in indicator_list:
                status[symbol].append(
                    {
                        "name": indicator.name,
                        "warmup_period": period,
                        "warmup_interval": interval.value,
                        "is_warmed_up": indicator.is_warmed_up,
                        "data_count": indicator._warmup_data_count,
                    }
                )

        return status

    def wait_for_warmup(self, timeout_seconds: int = 60) -> bool:
        """Wait for all indicators to complete warmup. Returns True if all warmed up."""
        start_time = self.clock.timestamp()
        while self.clock.timestamp() - start_time < timeout_seconds:
            if not self._indicator_manager.has_warmup_pending():
                return True

        return False

    def schedule(
        self,
        func: Callable,
        trigger: Literal["interval", "cron", "date"] = "interval",
        **kwargs,
    ):
        """
        There are three modes:

        - **cron**: run at a specific time second, minute, hour, day, month, year
        - **interval**: run at a specific interval  seconds, minutes, hours, days, weeks, months, years
        - **date**: run at a specific date and time, `run_date` must be provided

        kwargs:
            next_run_time: datetime, when to run the first time
            seconds/minutes/hours/days/weeks: int, interval between runs
            year/month/day/hour/minute/second: int, specific time to run
        """
        if not self._initialized:
            raise RuntimeError(
                "Strategy not initialized, please use `schedule` in `on_start` method"
            )
        self._scheduler.add_job(func, trigger=trigger, **kwargs)

    def market(self, symbol: str) -> BaseMarket:
        instrument_id = InstrumentId.from_str(symbol)
        exchange = self._exchanges[instrument_id.exchange]
        return exchange.market[instrument_id.symbol]

    def min_order_amount(self, symbol: str) -> Decimal:
        instrument_id = InstrumentId.from_str(symbol)
        ems = self._ems[instrument_id.exchange]
        return ems._get_min_order_amount(instrument_id.symbol, self.market(symbol))

    def amount_to_precision(
        self,
        symbol: str,
        amount: float,
        mode: Literal["round", "ceil", "floor"] = "round",
    ) -> Decimal:
        instrument_id = InstrumentId.from_str(symbol)
        ems = self._ems[instrument_id.exchange]
        return ems._amount_to_precision(instrument_id.symbol, amount, mode)

    def price_to_precision(
        self,
        symbol: str,
        price: float,
        mode: Literal["round", "ceil", "floor"] = "round",
    ) -> Decimal:
        instrument_id = InstrumentId.from_str(symbol)
        ems = self._ems[instrument_id.exchange]
        return ems._price_to_precision(instrument_id.symbol, price, mode)

    def create_batch_orders(
        self,
        orders: List[BatchOrder],
        account_type: AccountType | None = None,
    ):
        """
        Create a batch of orders.

        Args:
            orders (List[BatchOrder]): A list of BatchOrder objects to be submitted.
            account_type (AccountType | None): The account type for the orders. If None, it will auto selected the account_type, but for performance issue, recommend to set.
        """
        batch_orders: list[BatchOrderSubmit] = []
        for order in orders:
            batch_order = BatchOrderSubmit(
                symbol=order.symbol,
                instrument_id=InstrumentId.from_str(order.symbol),
                side=order.side,
                type=order.type,
                oid=self._oidgen.oid,
                amount=order.amount,
                price=order.price,
                time_in_force=order.time_in_force,
                reduce_only=order.reduce_only,
                kwargs=order.kwargs,
            )
            batch_orders.append(batch_order)
        self._ems[batch_orders[0].instrument_id.exchange]._submit_order(
            batch_orders, SubmitType.BATCH, account_type
        )
        return [order.oid for order in batch_orders]

    def create_tp_sl_order(
        self,
        symbol: str,
        side: OrderSide,
        type: OrderType,
        amount: Decimal,
        price: Decimal | None = None,
        time_in_force: TimeInForce | None = TimeInForce.GTC,
        tp_order_type: OrderType | None = None,
        tp_trigger_price: Decimal | None = None,
        tp_price: Decimal | None = None,
        tp_trigger_type: TriggerType = TriggerType.LAST_PRICE,
        sl_order_type: OrderType | None = None,
        sl_trigger_price: Decimal | None = None,
        sl_price: Decimal | None = None,
        sl_trigger_type: TriggerType = TriggerType.LAST_PRICE,
        account_type: AccountType | None = None,
        **kwargs,
    ):
        order = TakeProfitAndStopLossOrderSubmit(
            symbol=symbol,
            instrument_id=InstrumentId.from_str(symbol),
            side=side,
            type=type,
            oid=self._oidgen.oid,
            amount=amount,
            price=price,
            time_in_force=time_in_force,
            tp_order_type=tp_order_type,
            tp_trigger_price=tp_trigger_price,
            tp_price=tp_price,
            tp_trigger_type=tp_trigger_type,
            sl_order_type=sl_order_type,
            sl_trigger_price=sl_trigger_price,
            sl_price=sl_price,
            sl_trigger_type=sl_trigger_type,
            kwargs=kwargs,
        )
        self._ems[order.instrument_id.exchange]._submit_order(
            order, SubmitType.TAKE_PROFIT_AND_STOP_LOSS, account_type
        )
        return order.oid

    def create_order(
        self,
        symbol: str,
        side: OrderSide,
        type: OrderType,
        amount: Decimal,
        price: Decimal | None = None,
        time_in_force: TimeInForce | None = TimeInForce.GTC,
        reduce_only: bool = False,
        account_type: AccountType | None = None,
        **kwargs,
    ) -> str:
        order = CreateOrderSubmit(
            symbol=symbol,
            oid=self._oidgen.oid,
            instrument_id=InstrumentId.from_str(symbol),
            side=side,
            type=type,
            amount=amount,
            price=price,
            time_in_force=time_in_force,
            reduce_only=reduce_only,
            # position_side=position_side,
            kwargs=kwargs,
        )
        self._ems[order.instrument_id.exchange]._submit_order(
            order, SubmitType.CREATE, account_type
        )
        return order.oid

    def create_order_ws(
        self,
        symbol: str,
        side: OrderSide,
        type: OrderType,
        amount: Decimal,
        price: Decimal | None = None,
        time_in_force: TimeInForce | None = TimeInForce.GTC,
        reduce_only: bool = False,
        account_type: AccountType | None = None,
        **kwargs,
    ) -> str:
        order = CreateOrderSubmit(
            symbol=symbol,
            oid=self._oidgen.oid,
            instrument_id=InstrumentId.from_str(symbol),
            side=side,
            type=type,
            amount=amount,
            price=price,
            time_in_force=time_in_force,
            reduce_only=reduce_only,
            # position_side=position_side,
            kwargs=kwargs,
        )
        self._ems[order.instrument_id.exchange]._submit_order(
            order, SubmitType.CREATE_WS, account_type
        )
        return order.oid

    def cancel_order(
        self, symbol: str, oid: str, account_type: AccountType | None = None, **kwargs
    ) -> str:
        order = CancelOrderSubmit(
            symbol=symbol,
            instrument_id=InstrumentId.from_str(symbol),
            oid=oid,
            kwargs=kwargs,
        )
        self._ems[order.instrument_id.exchange]._submit_order(
            order, SubmitType.CANCEL, account_type
        )
        return order.oid

    def cancel_order_ws(
        self, symbol: str, oid: str, account_type: AccountType | None = None, **kwargs
    ) -> str:
        order = CancelOrderSubmit(
            symbol=symbol,
            instrument_id=InstrumentId.from_str(symbol),
            oid=oid,
            kwargs=kwargs,
        )
        self._ems[order.instrument_id.exchange]._submit_order(
            order, SubmitType.CANCEL_WS, account_type
        )
        return order.oid

    def cancel_all_orders(
        self, symbol: str, account_type: AccountType | None = None
    ) -> str:
        order = CancelAllOrderSubmit(
            symbol=symbol,
            instrument_id=InstrumentId.from_str(symbol),
        )
        self._ems[order.instrument_id.exchange]._submit_order(
            order, SubmitType.CANCEL_ALL, account_type
        )

    def modify_order(
        self,
        symbol: str,
        oid: str,
        side: OrderSide | None = None,
        price: Decimal | None = None,
        amount: Decimal | None = None,
        account_type: AccountType | None = None,
        **kwargs,
    ) -> str:
        order = ModifyOrderSubmit(
            symbol=symbol,
            instrument_id=InstrumentId.from_str(symbol),
            oid=oid,
            side=side,
            price=price,
            amount=amount,
            kwargs=kwargs,
        )
        self._ems[order.instrument_id.exchange]._submit_order(
            order, SubmitType.MODIFY, account_type
        )
        return order.oid

    # def create_twap(
    #     self,
    #     symbol: str,
    #     side: OrderSide,
    #     amount: Decimal,
    #     duration: int,
    #     wait: int,
    #     check_interval: float = 0.1,
    #     position_side: PositionSide | None = None,
    #     account_type: AccountType | None = None,
    #     **kwargs,
    # ) -> str:
    #     order = TWAPOrderSubmit(
    #         symbol=symbol,
    #         instrument_id=InstrumentId.from_str(symbol),
    #         side=side,
    #         amount=amount,
    #         duration=duration,
    #         wait=wait,
    #         check_interval=check_interval,
    #         position_side=position_side,
    #         kwargs=kwargs,
    #     )
    #     self._ems[order.instrument_id.exchange]._submit_order(
    #         order, SubmitType.TWAP, account_type
    #     )
    #     return order.uuid

    # def cancel_twap(
    #     self, symbol: str, uuid: str, account_type: AccountType | None = None
    # ) -> str:
    #     order = CancelTWAPOrderSubmit(
    #         symbol=symbol,
    #         instrument_id=InstrumentId.from_str(symbol),
    #         uuid=uuid,
    #     )
    #     self._ems[order.instrument_id.exchange]._submit_order(
    #         order, SubmitType.CANCEL_TWAP, account_type
    #     )
    #     return order.uuid

    def subscribe_bookl1(
        self, symbols: str | List[str], ready_timeout: int = 60, ready: bool = True
    ):
        """
        Subscribe to level 1 book data for the given symbols.

        Args:
            symbols (List[str]): The symbols to subscribe to.
            ready_timeout (int): The timeout for the data to be ready.
            ready (bool): default is True. Whether the data is ready. If True, the data will be ready immediately. When you use event driven strategy, you can set it to True. Otherwise, set it to False.
        """
        if not self._initialized:
            raise StrategyBuildError(
                "Strategy not initialized, please use `subscribe_bookl1` in `on_start` method"
            )

        self._msgbus.subscribe(topic="bookl1", handler=self._on_bookl1)
        if isinstance(symbols, str):
            symbols = [symbols]

        for symbol in symbols:
            self._subscriptions[DataType.BOOKL1].add(symbol)

        if DataType.BOOKL1 in self._subscriptions_ready:
            raise ValueError(
                "You should subscribe all symbols at once for BookL1 data type"
            )

        self._subscriptions_ready[DataType.BOOKL1] = DataReady(
            symbols,
            name="bookl1",
            timeout=ready_timeout,
            permanently_ready=ready,
        )

    def subscribe_trade(
        self, symbols: str | List[str], ready_timeout: int = 60, ready: bool = True
    ):
        """
        Subscribe to trade data for the given symbols.

        Args:
            symbols (List[str]): The symbols to subscribe to.
            ready_timeout (int): The timeout for the data to be ready.
            ready (bool): default is True. Whether the data is ready. If True, the data will be ready immediately. When you use event driven strategy, you can set it to True. Otherwise, set it to False.
        """
        if not self._initialized:
            raise StrategyBuildError(
                "Strategy not initialized, please use `subscribe_trade` in `on_start` method"
            )

        self._msgbus.subscribe(topic="trade", handler=self._on_trade)

        if isinstance(symbols, str):
            symbols = [symbols]

        for symbol in symbols:
            self._subscriptions[DataType.TRADE].add(symbol)

        if DataType.TRADE in self._subscriptions_ready:
            raise ValueError(
                "You should subscribe all symbols at once for Trade data type"
            )

        self._subscriptions_ready[DataType.TRADE] = DataReady(
            symbols,
            name="trade",
            timeout=ready_timeout,
            permanently_ready=ready,
        )

    def subscribe_kline(
        self,
        symbols: str | List[str],
        interval: KlineInterval,
        ready_timeout: int = 60,
        ready: bool = True,
        use_aggregator: bool = False,
        build_with_no_updates: bool = True,
    ):
        """
        Subscribe to kline data for the given symbols.

        Args:
            symbols (List[str]): The symbols to subscribe to.
            interval (str): The interval of the kline data
            ready_timeout (int): The timeout for the data to be ready.
            ready (bool): default is True. Whether the data is ready. If True, the data will be ready immediately. When you use event driven strategy, you can set it to True. Otherwise, set it to False.
            use_aggregator (bool): If True, use TimeKlineAggregator instead of exchange native klines. Useful when exchange doesn't support certain intervals.
        """
        if not self._initialized:
            raise StrategyBuildError(
                "Strategy not initialized, please use `subscribe_kline` in `on_start` method"
            )

        self._msgbus.subscribe(topic="kline", handler=self._on_kline)

        if isinstance(symbols, str):
            symbols = [symbols]

        for symbol in symbols:
            if use_aggregator:
                # Track aggregator subscription separately
                self._kline_use_aggregator.append(
                    {
                        "symbol": symbol,
                        "interval": interval,
                        "no_updates": build_with_no_updates,
                    }
                )
            else:
                # Regular kline subscription
                self._subscriptions[DataType.KLINE][interval].add(symbol)

        if interval.value in self._subscriptions_ready:
            raise ValueError(
                f"You should subscribe all symbols at once for Kline `{interval.value}` data type"
            )

        self._subscriptions_ready[interval.value] = DataReady(
            symbols,
            name=f"kline_{interval.value}",
            timeout=ready_timeout,
            permanently_ready=ready,
        )

    def subscribe_volume_kline(
        self,
        symbols: str | List[str],
        volume_threshold: float,
        volume_type: Literal["DEFAULT", "BUY", "SELL"] = "DEFAULT",
        ready_timeout: int = 60,
        ready: bool = True,
    ):
        """
        Subscribe to volume-based kline data for the given symbols.

        Args:
            symbols (List[str]): The symbols to subscribe to.
            volume_threshold (float): The volume threshold for creating new klines
            ready_timeout (int): The timeout for the data to be ready.
            ready (bool): default is True. Whether the data is ready. If True, the data will be ready immediately. When you use event driven strategy, you can set it to True. Otherwise, set it to False.
        """
        if not self._initialized:
            raise StrategyBuildError(
                "Strategy not initialized, please use `subscribe_volume_kline` in `on_start` method"
            )

        self._msgbus.subscribe(topic="kline", handler=self._on_kline)

        if isinstance(symbols, str):
            symbols = [symbols]

        for symbol in symbols:
            self._subscriptions[DataType.VOLUME_KLINE][symbol] = {
                "volume_threshold": volume_threshold,
                "volume_type": volume_type,
            }

            if symbol in self._subscriptions_ready:
                raise ValueError(
                    f"Symbol {symbol} already subscribed to volume kline with a different threshold. Only one volume threshold per symbol is allowed."
                )

            self._subscriptions_ready[symbol] = DataReady(
                symbols,
                name=f"volume_kline_{volume_threshold}",
                timeout=ready_timeout,
                permanently_ready=ready,
            )

    def subscribe_bookl2(
        self,
        symbols: str | List[str],
        level: BookLevel,
        ready_timeout: int = 60,
        ready: bool = True,
    ):
        """
        Subscribe to level 2 book data for the given symbols.

        Args:
            symbols (List[str]): The symbols to subscribe to.
            level (BookLevel): The level of the book data
            ready_timeout (int): The timeout for the data to be ready.
            ready (bool): default is True. Whether the data is ready. If True, the data will be ready immediately. When you use event driven strategy, you can set it to True. Otherwise, set it to False.
        """
        if not self._initialized:
            raise StrategyBuildError(
                "Strategy not initialized, please use `subscribe_bookl2` in `on_start` method"
            )

        self._msgbus.subscribe(topic="bookl2", handler=self._on_bookl2)

        if isinstance(symbols, str):
            symbols = [symbols]

        for symbol in symbols:
            self._subscriptions[DataType.BOOKL2][level].add(symbol)

        if DataType.BOOKL2 in self._subscriptions_ready:
            raise ValueError(
                "You should subscribe all symbols at once for BookL2 data type"
            )

        self._subscriptions_ready[DataType.BOOKL2] = DataReady(
            symbols,
            name="bookl2",
            timeout=ready_timeout,
            permanently_ready=ready,
        )

    def subscribe_funding_rate(
        self, symbols: str | List[str], ready_timeout: int = 60, ready: bool = True
    ):
        """
        Subscribe to funding rate data for the given symbols.

        Args:
            symbols (List[str]): The symbols to subscribe to.
            ready_timeout (int): The timeout for the data to be ready.
            ready (bool): default is True. Whether the data is ready. If True, the data will be ready immediately. When you use event driven strategy, you can set it to True. Otherwise, set it to False.
        """
        if not self._initialized:
            raise StrategyBuildError(
                "Strategy not initialized, please use `subscribe_funding_rate` in `on_start` method"
            )

        self._msgbus.subscribe(topic="funding_rate", handler=self._on_funding_rate)

        if isinstance(symbols, str):
            symbols = [symbols]

        for symbol in symbols:
            self._subscriptions[DataType.FUNDING_RATE].add(symbol)

        if DataType.FUNDING_RATE in self._subscriptions_ready:
            raise ValueError(
                "You should subscribe all symbols at once for Funding Rate data type"
            )

        self._subscriptions_ready[DataType.FUNDING_RATE] = DataReady(
            symbols,
            name="funding_rate",
            timeout=ready_timeout,
            permanently_ready=ready,
        )

    def subscribe_index_price(
        self, symbols: str | List[str], ready_timeout: int = 60, ready: bool = True
    ):
        """
        Subscribe to index price data for the given symbols.

        Args:
            symbols (List[str]): The symbols to subscribe to.
            ready_timeout (int): The timeout for the data to be ready.
            ready (bool): default is True. Whether the data is ready. If True, the data will be ready immediately. When you use event driven strategy, you can set it to True. Otherwise, set it to False.
        """
        if not self._initialized:
            raise StrategyBuildError(
                "Strategy not initialized, please use `subscribe_index_price` in `on_start` method"
            )

        self._msgbus.subscribe(topic="index_price", handler=self._on_index_price)

        if isinstance(symbols, str):
            symbols = [symbols]

        for symbol in symbols:
            self._subscriptions[DataType.INDEX_PRICE].add(symbol)

        if DataType.INDEX_PRICE in self._subscriptions_ready:
            raise ValueError(
                "You should subscribe all symbols at once for Index Price data type"
            )

        self._subscriptions_ready[DataType.INDEX_PRICE] = DataReady(
            symbols,
            name="index_price",
            timeout=ready_timeout,
            permanently_ready=ready,
        )

    def subscribe_mark_price(
        self, symbols: str | List[str], ready_timeout: int = 60, ready: bool = True
    ):
        """
        Subscribe to mark price data for the given symbols.

        Args:
            symbols (List[str]): The symbols to subscribe to.
            ready_timeout (int): The timeout for the data to be ready.
            ready (bool): default is True. Whether the data is ready. If True, the data will be ready immediately. When you use event driven strategy, you can set it to True. Otherwise, set it to False.
        """
        if not self._initialized:
            raise StrategyBuildError(
                "Strategy not initialized, please use `subscribe_mark_price` in `on_start` method"
            )

        self._msgbus.subscribe(topic="mark_price", handler=self._on_mark_price)

        if isinstance(symbols, str):
            symbols = [symbols]

        for symbol in symbols:
            self._subscriptions[DataType.MARK_PRICE].add(symbol)

        if DataType.MARK_PRICE in self._subscriptions_ready:
            raise ValueError(
                "You should subscribe all symbols at once for Mark Price data type"
            )

        self._subscriptions_ready[DataType.MARK_PRICE] = DataReady(
            symbols,
            name="mark_price",
            timeout=ready_timeout,
            permanently_ready=ready,
        )

    def linear_info(
        self,
        exchange: ExchangeType,
        base: str | None = None,
        quote: str | None = None,
        exclude: List[str] | None = None,
    ) -> List[str]:
        exchange: ExchangeManager = self._exchanges[exchange]
        return exchange.linear(base, quote, exclude)

    def spot_info(
        self,
        exchange: ExchangeType,
        base: str | None = None,
        quote: str | None = None,
        exclude: List[str] | None = None,
    ) -> List[str]:
        exchange: ExchangeManager = self._exchanges[exchange]
        return exchange.spot(base, quote, exclude)

    def future_info(
        self,
        exchange: ExchangeType,
        base: str | None = None,
        quote: str | None = None,
        exclude: List[str] | None = None,
    ) -> List[str]:
        exchange: ExchangeManager = self._exchanges[exchange]
        return exchange.future(base, quote, exclude)

    def inverse_info(
        self,
        exchange: ExchangeType,
        base: str | None = None,
        quote: str | None = None,
        exclude: List[str] | None = None,
    ) -> List[str]:
        exchange: ExchangeManager = self._exchanges[exchange]
        return exchange.inverse(base, quote, exclude)

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def _on_start(self):
        # Start state exporter if available
        if self._state_exporter:
            self._state_exporter.start()
        self.on_start()

    def _on_stop(self):
        # Stop state exporter if available
        if self._state_exporter:
            self._state_exporter.stop()
        self.on_stop()

    def on_trade(self, trade: Trade):
        pass

    def on_bookl1(self, bookl1: BookL1):
        pass

    def on_bookl2(self, bookl2: BookL2):
        pass

    def on_kline(self, kline: Kline):
        pass

    def on_funding_rate(self, funding_rate: FundingRate):
        pass

    def on_index_price(self, index_price: IndexPrice):
        pass

    def on_mark_price(self, mark_price: MarkPrice):
        pass

    def on_pending_order(self, order: Order):
        pass

    def on_accepted_order(self, order: Order):
        pass

    def on_partially_filled_order(self, order: Order):
        pass

    def on_filled_order(self, order: Order):
        pass

    def on_canceling_order(self, order: Order):
        pass

    def on_canceled_order(self, order: Order):
        pass

    def on_failed_order(self, order: Order):
        pass

    def on_cancel_failed_order(self, order: Order):
        pass

    def on_balance(self, balance: AccountBalance):
        pass

    def stop(self):
        time.sleep(0.2)  # wait for 200ms to ensure all messages are processed
        os.kill(os.getpid(), signal.SIGINT)

    def wait(self, seconds: int):
        time.sleep(seconds)

    def _on_trade(self, trade: Trade):
        self.on_trade(trade)
        self._subscriptions_ready[DataType.TRADE].input(trade)

    def _on_bookl2(self, bookl2: BookL2):
        self.on_bookl2(bookl2)
        self._subscriptions_ready[DataType.BOOKL2].input(bookl2)

    def _on_kline(self, kline: Kline):
        self.on_kline(kline)
        if kline.interval == KlineInterval.VOLUME:
            self._subscriptions_ready[kline.symbol].input(kline)
        else:
            self._subscriptions_ready[kline.interval.value].input(kline)

    def _on_funding_rate(self, funding_rate: FundingRate):
        self.on_funding_rate(funding_rate)
        self._subscriptions_ready[DataType.FUNDING_RATE].input(funding_rate)

    def _on_bookl1(self, bookl1: BookL1):
        self.on_bookl1(bookl1)
        self._subscriptions_ready[DataType.BOOKL1].input(bookl1)

    def _on_index_price(self, index_price: IndexPrice):
        self.on_index_price(index_price)
        self._subscriptions_ready[DataType.INDEX_PRICE].input(index_price)

    def _on_mark_price(self, mark_price: MarkPrice):
        self.on_mark_price(mark_price)
        self._subscriptions_ready[DataType.MARK_PRICE].input(mark_price)

    def param(
        self, name: str, value: Optional[Any] = None, default: Optional[Any] = None
    ) -> Any:
        """
        Get or set a parameter in the cache.

        Args:
            name: The parameter name
            value: The parameter value to set. If None, will get the parameter.

        Returns:
            The parameter value if getting, None if setting.

        Examples:
            # Set a parameter
            self.param('rolling_n', 10)

            # Get a parameter
            rolling_n = self.param('rolling_n')
        """
        if value is not None:
            # Set parameter
            self.cache.set_param(name, value)
            return None
        else:
            # Get parameter
            return self.cache.get_param(name, default)

    def clear_param(self, name: Optional[str] = None) -> None:
        """
        Clear parameter(s) from the cache.

        Args:
            name: The parameter name to clear. If None, clears all parameters.

        Examples:
            # Clear a specific parameter
            self.clear_param('rolling_n')

            # Clear all parameters
            self.clear_param()
        """
        self.cache.clear_param(name)

    def set_timer(
        self,
        callback: Callable,
        interval: timedelta,
        name: str | None = None,
        start_time: datetime | None = None,
        stop_time: datetime | None = None,
    ):
        """
        Set a timer that calls a callback function at regular intervals.

        Args:
            callback: The function to call
            interval: Time interval between calls
            name: Optional timer name. If not provided, uses the callback function name.
            start_time: When to start the timer (defaults to now + interval)
            stop_time: When to stop the timer (optional)
        """
        if name is None:
            name = callback.__name__

        if start_time is None:
            start_time = self.clock.utc_now() + interval

        self.clock.set_timer(
            name=name,
            interval=interval,
            start_time=start_time,
            stop_time=stop_time,
            callback=callback,
        )
