import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from sqlalchemy import inspect
from app.database.models import User, Order
from sqlalchemy import Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///db.sqlite3"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

#===================================================================================================
#===================================================================================================
#===================================================================================================
async def update_database():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE users ADD COLUMN age INTEGER DEFAULT NULL"))

async def delete_database():
    async with engine.begin() as conn:
        #await conn.execute(text("ALTER TABLE users DROP COLUMN name"))
        await conn.execute(text("DROP TABLE IF EXISTS orders"))

async def create_order_table():
    async with engine.begin() as conn:
        await conn.run_sync(Order.__table__.create)  # Создаем только таблицу для модели Order


if __name__ == "__main__":
    asyncio.run(create_order_table())
