import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import asyncio

load_dotenv()

DATABASE_CONN_STR = os.getenv("DATABASE_CONN_STR", "postgresql://user:password@localhost/order_db")

class Database:
    def __init__(self):
        self.conn = None
    
    async def connect(self, max_attempts=30, delay=1):
        for attempt in range(1, max_attempts+1):
            try:
                self.conn = await psycopg.AsyncConnection.connect(
                    DATABASE_CONN_STR,
                    row_factory=dict_row
                )
                print("Database connection established")
                return
            except psycopg.OperationalError as e:
                if attempt < max_attempts:
                    print(f"Database connection failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay} second(s)...")
                    await asyncio.sleep(delay)
                else:
                    print(f"Failed to connect to database after {max_attempts} attempts: {e}")
                    raise
    
    async def disconnect(self):
        if self.conn:
            await self.conn.close()
    
    @asynccontextmanager
    async def transaction(self):
        if not self.conn:
            await self.connect()
        async with self.conn.transaction():
            yield

    async def execute(self, query: str, *args):
        async with self.conn.cursor() as cur:
            await cur.execute(query, args)
            return cur.rowcount
    
    async def fetch(self, query: str, *args):
        async with self.conn.cursor() as cur:
            await cur.execute(query, args)
            return await cur.fetchall()
    
    async def fetchrow(self, query: str, *args):
        async with self.conn.cursor() as cur:
            await cur.execute(query, args)
            return await cur.fetchone()
    
    async def fetchval(self, query: str, *args):
        async with self.conn.cursor() as cur:
            await cur.execute(query, args)
            result = await cur.fetchone()
            return list(result.values())[0] if result else None

db = Database()