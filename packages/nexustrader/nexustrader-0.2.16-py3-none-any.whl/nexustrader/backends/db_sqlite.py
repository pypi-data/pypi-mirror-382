import aiosqlite
import sqlite3
from pathlib import Path
from typing import Dict, Set, List, Optional, Any

from nexustrader.backends.db import StorageBackend
from nexustrader.schema import Order, Position, AlgoOrder, Balance, AccountBalance
from nexustrader.constants import AccountType, ExchangeType


class SQLiteBackend(StorageBackend):
    def __init__(
        self,
        strategy_id: str,
        user_id: str,
        table_prefix: str,
        log,
        db_path: str = ".keys/cache.db",
        **kwargs,
    ):
        super().__init__(strategy_id, user_id, table_prefix, log, **kwargs)
        self.db_path = db_path
        self._db_async = None
        self._db = None

    async def _init_conn(self) -> None:
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db_async = await aiosqlite.connect(str(db_path))
        self._db = sqlite3.connect(str(db_path))

    async def _init_table(self) -> None:
        async with self._db_async.cursor() as cursor:
            await cursor.executescript(f"""
                CREATE TABLE IF NOT EXISTS {self.table_prefix}_orders (
                    timestamp INTEGER,
                    oid TEXT PRIMARY KEY,
                    eid TEXT,
                    symbol TEXT,
                    side TEXT, 
                    type TEXT,
                    amount TEXT,
                    price REAL,
                    status TEXT,
                    fee TEXT,
                    fee_currency TEXT,
                    data BLOB
                );
                
                CREATE INDEX IF NOT EXISTS idx_orders_symbol 
                ON {self.table_prefix}_orders(symbol);
                
                CREATE TABLE IF NOT EXISTS {self.table_prefix}_algo_orders (
                    timestamp INTEGER,
                    oid TEXT PRIMARY KEY,
                    symbol TEXT,
                    data BLOB
                );
                
                CREATE INDEX IF NOT EXISTS idx_algo_orders_symbol 
                ON {self.table_prefix}_algo_orders(symbol);
                
                CREATE TABLE IF NOT EXISTS {self.table_prefix}_positions (
                    symbol PRIMARY KEY,
                    exchange TEXT,
                    side TEXT,
                    amount TEXT,
                    data BLOB
                );
                
                CREATE TABLE IF NOT EXISTS {self.table_prefix}_open_orders (
                    oid PRIMARY KEY,
                    eid TEXT,
                    exchange TEXT,
                    symbol TEXT
                );
                
                CREATE TABLE IF NOT EXISTS {self.table_prefix}_balances (
                    asset TEXT,
                    account_type TEXT,
                    free TEXT,
                    locked TEXT,
                    PRIMARY KEY (asset, account_type)
                );
                
                CREATE TABLE IF NOT EXISTS {self.table_prefix}_pnl (
                    timestamp INTEGER PRIMARY KEY,
                    pnl REAL,
                    unrealized_pnl REAL
                );
                
                CREATE TABLE IF NOT EXISTS {self.table_prefix}_params (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    timestamp INTEGER DEFAULT (strftime('%s', 'now') * 1000)
                );
            """)
            await self._db_async.commit()

    def _get_cursor(self):
        """Get a thread-safe SQLite cursor, creating new connection if needed."""
        try:
            return self._db.cursor()
        except sqlite3.ProgrammingError:
            # SQLite connection is from different thread, create new one
            db_path = Path(self.db_path)
            return sqlite3.connect(str(db_path)).cursor()

    async def close(self) -> None:
        if self._db_async:
            await self._db_async.close()
        if self._db:
            self._db.close()

    async def sync_orders(self, mem_orders: Dict[str, Order]) -> None:
        async with self._db_async.cursor() as cursor:
            for oid, order in mem_orders.copy().items():
                await cursor.execute(
                    f"INSERT OR REPLACE INTO {self.table_prefix}_orders "
                    "(timestamp, oid, eid, symbol, side, type, amount, price, status, fee, fee_currency, data) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        order.timestamp,
                        order.oid,
                        order.eid,
                        order.symbol,
                        order.side.value if order.side is not None else None,
                        order.type.value if order.type is not None else None,
                        str(order.amount),
                        order.price or order.average,
                        order.status.value,
                        str(order.fee) if order.fee is not None else None,
                        order.fee_currency,
                        self._encode(order),
                    ),
                )
            await self._db_async.commit()

    async def sync_algo_orders(self, mem_algo_orders: Dict[str, AlgoOrder]) -> None:
        async with self._db_async.cursor() as cursor:
            for oid, algo_order in mem_algo_orders.copy().items():
                await cursor.execute(
                    f"INSERT OR REPLACE INTO {self.table_prefix}_algo_orders "
                    "(timestamp, oid, symbol, data) VALUES (?, ?, ?, ?)",
                    (
                        algo_order.timestamp,
                        oid,
                        algo_order.symbol,
                        self._encode(algo_order),
                    ),
                )
            await self._db_async.commit()

    async def sync_positions(self, mem_positions: Dict[str, Position]) -> None:
        async with self._db_async.cursor() as cursor:
            await cursor.execute(f"SELECT symbol FROM {self.table_prefix}_positions")
            db_positions = {row[0] for row in await cursor.fetchall()}

            positions_to_delete = db_positions - set(mem_positions.keys())
            if positions_to_delete:
                await cursor.executemany(
                    f"DELETE FROM {self.table_prefix}_positions WHERE symbol = ?",
                    [(symbol,) for symbol in positions_to_delete],
                )
                self._log.debug(
                    f"Deleted {len(positions_to_delete)} stale positions from database"
                )

            for symbol, position in mem_positions.copy().items():
                await cursor.execute(
                    f"INSERT OR REPLACE INTO {self.table_prefix}_positions "
                    "(symbol, exchange, side, amount, data) VALUES (?, ?, ?, ?, ?)",
                    (
                        symbol,
                        position.exchange.value,
                        position.side.value if position.side else "FLAT",
                        str(position.amount),
                        self._encode(position),
                    ),
                )
            await self._db_async.commit()

    async def sync_open_orders(
        self,
        mem_open_orders: Dict[ExchangeType, Set[str]],
        mem_orders: Dict[str, Order],
    ) -> None:
        async with self._db_async.cursor() as cursor:
            await cursor.execute(f"DELETE FROM {self.table_prefix}_open_orders")

            for exchange, oids in mem_open_orders.copy().items():
                for oid in oids.copy():
                    order = mem_orders.get(oid)
                    if order:
                        await cursor.execute(
                            f"INSERT INTO {self.table_prefix}_open_orders "
                            "(oid, eid, exchange, symbol) VALUES (?, ?, ?, ?)",
                            (oid, order.eid, exchange.value, order.symbol),
                        )
            await self._db_async.commit()

    async def sync_balances(
        self, mem_account_balance: Dict[AccountType, AccountBalance]
    ) -> None:
        async with self._db_async.cursor() as cursor:
            for account_type, balance in mem_account_balance.copy().items():
                for asset, amount in balance.balances.items():
                    await cursor.execute(
                        f"INSERT OR REPLACE INTO {self.table_prefix}_balances "
                        "(asset, account_type, free, locked) VALUES (?, ?, ?, ?)",
                        (
                            asset,
                            account_type.value,
                            str(amount.free),
                            str(amount.locked),
                        ),
                    )
            await self._db_async.commit()

    def get_order(
        self,
        oid: str,
        mem_orders: Dict[str, Order],
        mem_algo_orders: Dict[str, AlgoOrder],
    ) -> Optional[Order | AlgoOrder]:
        if order := mem_orders.get(oid):
            return order
        if algo_order := mem_algo_orders.get(oid):
            return algo_order

        cursor = self._get_cursor()
        try:
            # Try regular orders first
            cursor.execute(
                f"SELECT data FROM {self.table_prefix}_orders WHERE oid = ?",
                (oid,),
            )
            if row := cursor.fetchone():
                order = self._decode(row[0], Order)
                mem_orders[oid] = order
                return order

            # Try algo orders
            cursor.execute(
                f"SELECT data FROM {self.table_prefix}_algo_orders WHERE oid = ?",
                (oid,),
            )
            if row := cursor.fetchone():
                algo_order = self._decode(row[0], AlgoOrder)
                mem_algo_orders[oid] = algo_order
                return algo_order

            return None

        except sqlite3.Error as e:
            self._log.error(f"Error getting order from SQLite: {e}")
            return None

    def get_symbol_orders(self, symbol: str) -> Set[str]:
        cursor = self._get_cursor()
        cursor.execute(
            f"SELECT oid FROM {self.table_prefix}_orders WHERE symbol = ?",
            (symbol,),
        )
        return {row[0] for row in cursor.fetchall()}

    def get_all_positions(self, exchange_id: ExchangeType) -> Dict[str, Position]:
        positions = {}
        cursor = self._get_cursor()
        cursor.execute(
            f"SELECT symbol, data FROM {self.table_prefix}_positions WHERE exchange = ?",
            (exchange_id.value,),
        )
        for row in cursor.fetchall():
            position = self._decode(row[1], Position)
            if position.side:
                positions[position.symbol] = position
        return positions

    def get_all_balances(self, account_type: AccountType) -> List[Balance]:
        from decimal import Decimal

        balances = []
        cursor = self._get_cursor()
        cursor.execute(
            f"SELECT asset, free, locked FROM {self.table_prefix}_balances WHERE account_type = ?",
            (account_type.value,),
        )
        for row in cursor.fetchall():
            balances.append(
                Balance(asset=row[0], free=Decimal(row[1]), locked=Decimal(row[2]))
            )
        return balances

    async def sync_params(self, mem_params: Dict[str, Any]) -> None:
        import msgspec

        async with self._db_async.cursor() as cursor:
            for key, value in mem_params.copy().items():
                try:
                    serialized_value = self._encode_param(value)
                    await cursor.execute(
                        f"INSERT OR REPLACE INTO {self.table_prefix}_params "
                        "(key, value) VALUES (?, ?)",
                        (key, serialized_value),
                    )
                except msgspec.EncodeError as e:
                    self._log.error(f"Error serializing parameter {key}: {e}")
                except sqlite3.Error as e:
                    self._log.error(f"Error storing parameter {key}: {e}")
            await self._db_async.commit()

    def get_param(self, key: str, default: Any = None) -> Any:
        import msgspec

        try:
            cursor = self._get_cursor()
            cursor.execute(
                f"SELECT value FROM {self.table_prefix}_params WHERE key = ?", (key,)
            )
            if row := cursor.fetchone():
                try:
                    return self._decode_param(row[0])
                except msgspec.DecodeError as e:
                    self._log.error(f"Error deserializing parameter {key}: {e}")
                    return default
            return default
        except sqlite3.Error as e:
            self._log.error(f"Error getting parameter {key}: {e}")
            return default

    def get_all_params(self) -> Dict[str, Any]:
        import msgspec

        params = {}
        try:
            cursor = self._get_cursor()
            cursor.execute(f"SELECT key, value FROM {self.table_prefix}_params")
            for row in cursor.fetchall():
                try:
                    params[row[0]] = self._decode_param(row[1])
                except msgspec.DecodeError as e:
                    self._log.error(f"Error deserializing parameter {row[0]}: {e}")
        except sqlite3.Error as e:
            self._log.error(f"Error getting all parameters: {e}")
        return params
