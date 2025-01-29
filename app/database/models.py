from sqlalchemy import ForeignKey, String, BigInteger, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime


engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3',
                             echo=True)
    
    
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    balance: Mapped[str] = mapped_column(String(15))

class AiType(Base):
    __tablename__ = 'ai_types'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))


class AiModel(Base):
    __tablename__ = 'ai_models'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))
    ai_type: Mapped[int] = mapped_column(ForeignKey('ai_types.id'))
    price:Mapped[str] = mapped_column(String(25))


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # ID счета Cryptomus
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # Статус платежа
    tg_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'), nullable=False)  # ID пользователя
    amount: Mapped[str] = mapped_column(String(15), nullable=False)  # Сумма платежа
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)  # Обработан ли платеж
    processed_at: Mapped[datetime] = mapped_column(DateTime,nullable=False)





async def async_main():
    async with engine.begin() as conn:
        """await conn.run_sync(Base.metadata.create_all)"""