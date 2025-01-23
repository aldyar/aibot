import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from sqlalchemy import inspect
from app.database.models import User
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
        await conn.execute(text("ALTER TABLE users DROP COLUMN name"))


if __name__ == "__main__":
    asyncio.run(delete_database())
