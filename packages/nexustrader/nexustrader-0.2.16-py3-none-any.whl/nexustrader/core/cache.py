import msgspec
import asyncio
import threading
import re
from typing import Dict, Set, Type, List, Optional, Any
from collections import defaultdict
from returns.maybe import maybe
from pathlib import Path

from nexustrader.schema import (
    Order,
    Position,
    ExchangeType,
    Kline,
    BookL1,
    Trade,
    AlgoOrder,
    AccountBalance,
    Balance,
    FundingRate,
    IndexPrice,
    MarkPrice,
    BookL2,
)
from nexustrader.constants import STATUS_TRANSITIONS, AccountType, KlineInterval
from nexustrader.core.entity import TaskManager
from nexustrader.core.nautilius_core import LiveClock, MessageBus, Logger
from nexustrader.constants import StorageType
from nexustrader.backends import SQLiteBackend, PostgreSQLBackend


class AsyncCache:
    _backend: SQLiteBackend | PostgreSQLBackend

    def __init__(
        self,
        strategy_id: str,
        user_id: str,
        msgbus: MessageBus,
        clock: LiveClock,
        task_manager: TaskManager,
        storage_backend: StorageType = StorageType.SQLITE,
        db_path: str = ".keys/cache.db",
        sync_interval: int = 60,  # seconds
        expired_time: int = 3600,  # seconds
    ):
        parent_dir = Path(db_path).parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)

        self.strategy_id = strategy_id
        self.user_id = user_id
        self._storage_backend = storage_backend
        self._db_path = db_path

        self._log = Logger(name=type(self).__name__)
        self._clock = clock

        # in-memory save
        self._mem_orders: Dict[str, Order] = {}  # oid -> Order
        self._mem_algo_orders: Dict[str, AlgoOrder] = {}  # oid -> AlgoOrder
        self._mem_open_orders: Dict[ExchangeType, Set[str]] = defaultdict(
            set
        )  # exchange_id -> set(oid)
        self._mem_symbol_open_orders: Dict[str, Set[str]] = defaultdict(
            set
        )  # symbol -> set(oid)
        self._mem_symbol_orders: Dict[str, Set[str]] = defaultdict(
            set
        )  # symbol -> set(oid)
        self._mem_positions: Dict[str, Position] = {}  # symbol -> Position
        self._mem_account_balance: Dict[AccountType, AccountBalance] = defaultdict(
            AccountBalance
        )
        self._mem_params: Dict[str, Any] = {}  # params cache
        self._cancel_intent_oids: Set[str] = (
            set()
        )  # oids currently pending cancel intent

        # set params
        self._sync_interval = sync_interval  # sync interval
        self._expired_time = expired_time  # expire time
        self._task_manager = task_manager

        self._kline_cache: Dict[str, Kline] = {}
        self._bookl1_cache: Dict[str, BookL1] = {}
        self._trade_cache: Dict[str, Trade] = {}
        self._bookl2_cache: Dict[str, BookL2] = {}
        self._funding_rate_cache: Dict[str, FundingRate] = {}
        self._index_price_cache: Dict[str, IndexPrice] = {}
        self._mark_price_cache: Dict[str, MarkPrice] = {}

        self._msgbus = msgbus
        self._msgbus.subscribe(topic="kline", handler=self._update_kline_cache)
        self._msgbus.subscribe(topic="bookl1", handler=self._update_bookl1_cache)
        self._msgbus.subscribe(topic="trade", handler=self._update_trade_cache)
        self._msgbus.subscribe(topic="bookl2", handler=self._update_bookl2_cache)
        self._msgbus.subscribe(
            topic="funding_rate", handler=self._update_funding_rate_cache
        )
        self._msgbus.subscribe(
            topic="index_price", handler=self._update_index_price_cache
        )
        self._msgbus.subscribe(
            topic="mark_price", handler=self._update_mark_price_cache
        )

        self._storage_initialized = False
        self._table_prefix = self.safe_table_name(f"{self.strategy_id}_{self.user_id}")
        self._backend = None

        self._position_lock = threading.RLock()  # Lock for position updates
        self._order_lock = threading.RLock()  # Lock for order updates
        self._balance_lock = threading.RLock()  # Lock for balance updates
        self._param_lock = threading.RLock()  # Lock for parameter updates

    ################# # base functions ####################

    @staticmethod
    def safe_table_name(name: str) -> str:
        name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        return name.lower()

    def _encode(self, obj: Order | Position | AlgoOrder) -> bytes:
        return msgspec.json.encode(obj)

    def _decode(
        self, data: bytes, obj_type: Type[Order | Position | AlgoOrder]
    ) -> Order | Position | AlgoOrder:
        return msgspec.json.decode(data, type=obj_type)

    async def _init_storage(self):
        """Initialize the storage backend"""
        if self._storage_backend == StorageType.SQLITE:
            self._backend = SQLiteBackend(
                strategy_id=self.strategy_id,
                user_id=self.user_id,
                table_prefix=self._table_prefix,
                log=self._log,
                db_path=self._db_path,
            )
        elif self._storage_backend == StorageType.POSTGRESQL:
            self._backend = PostgreSQLBackend(
                strategy_id=self.strategy_id,
                user_id=self.user_id,
                table_prefix=self._table_prefix,
                log=self._log,
            )

        assert self._backend is not None

        await self._backend.start()
        self._storage_initialized = True

    async def _load_params_from_db(self):
        """Load existing parameters from database"""
        try:
            existing_params = self._backend.get_all_params()
            self._mem_params.update(existing_params)
            if existing_params:
                self._log.debug(
                    f"Loaded {len(existing_params)} parameters from database"
                )
        except Exception as e:
            self._log.error(f"Error loading parameters from database: {e}")

    async def start(self):
        """Start the cache"""
        await self._init_storage()
        # Load existing parameters from database
        await self._load_params_from_db()
        self._task_manager.create_task(self._periodic_sync())

    async def _periodic_sync(self):
        """Periodically sync the cache"""
        while True:
            await self._backend.sync_orders(self._mem_orders)
            await self._backend.sync_algo_orders(self._mem_algo_orders)
            await self._backend.sync_positions(self._mem_positions)
            await self._backend.sync_open_orders(
                self._mem_open_orders, self._mem_orders
            )
            await self._backend.sync_balances(self._mem_account_balance)
            await self._backend.sync_params(self._mem_params)
            self._cleanup_expired_data()
            await asyncio.sleep(self._sync_interval)

    async def sync_orders(self):
        with self._order_lock:
            await self._backend.sync_orders(self._mem_orders)

    async def sync_algo_orders(self):
        with self._order_lock:
            await self._backend.sync_algo_orders(self._mem_algo_orders)

    async def sync_positions(self):
        with self._position_lock:
            await self._backend.sync_positions(self._mem_positions)

    async def sync_open_orders(self):
        with self._order_lock:
            await self._backend.sync_open_orders(
                self._mem_open_orders, self._mem_orders
            )

    async def sync_balances(self):
        with self._balance_lock:
            await self._backend.sync_balances(self._mem_account_balance)

    async def sync_params(self):
        await self._backend.sync_params(self._mem_params)

    def _cleanup_expired_data(self):
        """Cleanup expired data"""
        current_time = self._clock.timestamp_ms()
        expire_before = current_time - self._expired_time * 1000

        with self._order_lock:
            expired_orders = []
            for oid, order in self._mem_orders.copy().items():
                if order.timestamp < expire_before:
                    expired_orders.append(oid)

                    if not order.is_closed:
                        self._log.warning(f"order {oid} is not closed, but expired")

            for oid in expired_orders:
                del self._mem_orders[oid]
                self._log.debug(f"removing order {oid} from memory")
                for symbol, order_set in self._mem_symbol_orders.copy().items():
                    self._log.debug(f"removing order {oid} from symbol {symbol}")
                    order_set.discard(oid)

            expired_algo_orders = [
                oid
                for oid, algo_order in self._mem_algo_orders.copy().items()
                if algo_order.timestamp < expire_before
            ]
            for oid in expired_algo_orders:
                del self._mem_algo_orders[oid]
                self._log.debug(f"removing algo order {oid} from memory")

    async def close(self):
        """关闭缓存"""
        if self._storage_initialized and self._backend:
            try:
                await self._backend.sync_orders(self._mem_orders)
                await self._backend.sync_algo_orders(self._mem_algo_orders)
                await self._backend.sync_positions(self._mem_positions)
                await self._backend.sync_open_orders(
                    self._mem_open_orders, self._mem_orders
                )
                await self._backend.sync_balances(self._mem_account_balance)
                await self._backend.sync_params(self._mem_params)
            except Exception as e:
                # Never let cache close crash shutdown; log and continue
                self._log.error(f"Error closing cache (sync phase): {e}")
            finally:
                try:
                    await self._backend.close()
                except Exception as e:
                    self._log.error(f"Error closing storage backend: {e}")

    ################ # cache public data  ###################

    def _update_kline_cache(self, kline: Kline):
        key = f"{kline.symbol}-{kline.interval.value}"
        self._kline_cache[key] = kline

    def _update_bookl1_cache(self, bookl1: BookL1):
        self._bookl1_cache[bookl1.symbol] = bookl1

    def _update_trade_cache(self, trade: Trade):
        self._trade_cache[trade.symbol] = trade

    def _update_bookl2_cache(self, bookl2: BookL2):
        self._bookl2_cache[bookl2.symbol] = bookl2

    def _update_funding_rate_cache(self, funding_rate: FundingRate):
        self._funding_rate_cache[funding_rate.symbol] = funding_rate

    def _update_index_price_cache(self, index_price: IndexPrice):
        self._index_price_cache[index_price.symbol] = index_price

    def _update_mark_price_cache(self, mark_price: MarkPrice):
        self._mark_price_cache[mark_price.symbol] = mark_price

    def kline(self, symbol: str, interval: KlineInterval) -> Optional[Kline]:
        """
        Retrieve a Kline object from the cache by symbol.

        :param symbol: The symbol of the Kline to retrieve.
        :return: The Kline object if found, otherwise None.
        """
        key = f"{symbol}-{interval.value}"
        return self._kline_cache.get(key, None)

    def bookl1(self, symbol: str) -> Optional[BookL1]:
        """
        Retrieve a BookL1 object from the cache by symbol.

        :param symbol: The symbol of the BookL1 to retrieve.
        :return: The BookL1 object if found, otherwise None.
        """
        return self._bookl1_cache.get(symbol, None)

    def bookl2(self, symbol: str) -> Optional[BookL2]:
        """
        Retrieve a BookL2 object from the cache by symbol.
        """
        return self._bookl2_cache.get(symbol, None)

    def trade(self, symbol: str) -> Optional[Trade]:
        """
        Retrieve a Trade object from the cache by symbol.

        :param symbol: The symbol of the Trade to retrieve.
        :return: The Trade object if found, otherwise None.
        """
        return self._trade_cache.get(symbol, None)

    def funding_rate(self, symbol: str) -> Optional[FundingRate]:
        """
        Retrieve a FundingRate object from the cache by symbol.
        """
        return self._funding_rate_cache.get(symbol, None)

    def index_price(self, symbol: str) -> Optional[IndexPrice]:
        """
        Retrieve an IndexPrice object from the cache by symbol.
        """
        return self._index_price_cache.get(symbol, None)

    def mark_price(self, symbol: str) -> Optional[MarkPrice]:
        """
        Retrieve a MarkPrice object from the cache by symbol.
        """
        return self._mark_price_cache.get(symbol, None)

    ################ # cache private data  ###################

    def _check_status_transition(self, order: Order):
        previous_order = self._mem_orders.get(order.oid)
        if not previous_order:
            return True

        if order.status not in STATUS_TRANSITIONS[previous_order.status]:
            self._log.warning(
                f"Order id: {order.oid} Invalid status transition: {previous_order.status} -> {order.status}"
            )
            return False

        return True

    def _apply_position(self, position: Position):
        with self._position_lock:
            if position.is_closed:
                self._mem_positions.pop(position.symbol, None)
            else:
                self._mem_positions[position.symbol] = position

    def _apply_balance(self, account_type: AccountType, balances: List[Balance]):
        with self._balance_lock:
            self._mem_account_balance[account_type]._apply(balances)

    def get_balance(self, account_type: AccountType) -> AccountBalance:
        with self._balance_lock:
            return self._mem_account_balance[account_type]

    @maybe
    def get_position(self, symbol: str) -> Optional[Position]:
        with self._position_lock:
            if position := self._mem_positions.get(symbol, None):
                return position

    def get_all_positions(
        self, exchange: Optional[ExchangeType] = None
    ) -> Dict[str, Position]:
        with self._position_lock:
            positions = {
                symbol: position
                for symbol, position in self._mem_positions.copy().items()
                if (
                    (exchange is None or position.exchange == exchange)
                    and position.is_opened
                )
            }
            return positions

    def _order_status_update(self, order: Order | AlgoOrder) -> bool:
        with self._order_lock:
            if isinstance(order, AlgoOrder):
                self._mem_algo_orders[order.oid] = order
            else:
                if not self._check_status_transition(order):
                    return False
                self._mem_orders[order.oid] = order

                # Ensure order is tracked in all sets if it's open (handles WebSocket arriving before REST API)
                if not order.is_closed:
                    self._mem_open_orders[order.exchange].add(order.oid)
                    self._mem_symbol_orders[order.symbol].add(order.oid)
                    self._mem_symbol_open_orders[order.symbol].add(order.oid)
                else:
                    self._mem_open_orders[order.exchange].discard(order.oid)
                    self._mem_symbol_open_orders[order.symbol].discard(order.oid)
                    self._cancel_intent_oids.discard(order.oid)
                return True

    def mark_all_cancel_intent(self, symbol: str) -> None:
        with self._order_lock:
            oids = self._mem_symbol_open_orders.get(symbol, set())
            self._cancel_intent_oids.update(oids)

    def mark_cancel_intent(self, oid: str) -> None:
        with self._order_lock:
            self._cancel_intent_oids.add(oid)

    # NOTE: this function is not for user to call, it is for internal use
    def _get_all_balances_from_db(self, account_type: AccountType) -> List[Balance]:
        with self._balance_lock:
            return self._backend.get_all_balances(account_type)

    # NOTE: this function is not for user to call, it is for internal use
    def _get_all_positions_from_db(
        self, exchange_id: ExchangeType
    ) -> Dict[str, Position]:
        return self._backend.get_all_positions(exchange_id)

    @maybe
    def get_order(self, oid: str) -> Optional[Order | AlgoOrder]:
        with self._order_lock:
            return self._backend.get_order(oid, self._mem_orders, self._mem_algo_orders)

    def get_symbol_orders(self, symbol: str, in_mem: bool = True) -> Set[str]:
        """Get all orders for a symbol from memory and storage"""
        with self._order_lock:
            memory_orders = self._mem_symbol_orders.get(symbol, set())
            if not in_mem:
                storage_orders = self._backend.get_symbol_orders(symbol)
                return memory_orders.union(storage_orders)
            return memory_orders

    def get_open_orders(
        self,
        symbol: str | None = None,
        exchange: ExchangeType | None = None,
        *,
        include_canceling: bool = False,
    ) -> Set[str]:
        with self._order_lock:
            if symbol is not None:
                orders = self._mem_symbol_open_orders[symbol].copy()
            elif exchange is not None:
                orders = self._mem_open_orders[exchange].copy()
            else:
                raise ValueError("Either `symbol` or `exchange` must be specified")

            if include_canceling:
                return orders

            return orders.difference(self._cancel_intent_oids)

    ################ # parameter cache  ###################

    def get_param(self, key: str, default: Any = None) -> Any:
        """Get a parameter from the cache"""
        with self._param_lock:
            return self._mem_params.get(key, default)

    def set_param(self, key: str, value: Any) -> None:
        """Set a parameter in the cache"""
        with self._param_lock:
            self._mem_params[key] = value

    def get_all_params(self) -> Dict[str, Any]:
        """Get all parameters from the cache"""
        with self._param_lock:
            return self._mem_params.copy()

    def clear_param(self, key: Optional[str] = None) -> None:
        """Clear parameter(s) from the cache"""
        with self._param_lock:
            if key is None:
                # Clear all parameters
                self._mem_params.clear()
            else:
                # Clear specific parameter
                self._mem_params.pop(key, None)
