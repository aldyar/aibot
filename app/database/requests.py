from app.database.models import async_session
from app.database.models import User, AiType, AiModel, Order
from sqlalchemy import select, update, delete, desc
from decimal import Decimal


def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner


@connection
async def set_user(session, tg_id):
    #async with async_session() as session:
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    if not user:
        session.add(User(tg_id=tg_id, balance='0.05'))
        await session.commit()


@connection
async def get_user(session, tg_id):
    #async with async_session() as session:
    async with async_session.begin():
        return await session.scalar(select(User).where(User.tg_id == tg_id))
    

@connection
async def get_users(session):
    async with async_session.begin():
        return await session.scalars(select(User))


@connection
async def calculate_text(session, tg_id, usage, model_name, user):
    model = await session.scalar(select(AiModel).where(AiModel.name == model_name))
    
    # Цены токенов
    input_price = 0.0000025  # Цена за один входной токен
    output_price = 0.00001   # Цена за один выходной токен
    markup = 1.4             # Наценка 40%
    
    # Расчет токенов
    prompt_tokens = usage['prompt_tokens']
    completion_tokens = usage['completion_tokens']
    
    # Расчет стоимости
    input_cost = prompt_tokens * input_price * markup
    output_cost = completion_tokens * output_price * markup
    total_cost = input_cost + output_cost

    print(f"Input tokens: {prompt_tokens}, Output tokens: {completion_tokens}")
    print(f"Input cost: {input_cost}, Output cost: {output_cost}, Total cost: {total_cost}")
    
    # Обновляем баланс пользователя
    new_balance = Decimal(user.balance) - Decimal(total_cost)
    new_balance = round(new_balance, 7)  # Округляем до 7 знаков
    print(f"Новый баланс: {new_balance}")
    await session.execute(update(User).where(User.id == user.id).values(balance=str(new_balance)))
    await session.commit()


@connection
async def calculate_image(session, tg_id, summ, model_name, user):
    model = await session.scalar(select(AiModel).where(AiModel.name == model_name))
    print(f"Использовано токенов: {summ}, Цена модели: {model.price}")  # Логируем
    new_balance = Decimal(Decimal(user.balance) - (Decimal(model.price) * Decimal(summ)))
    print(f"Новый баланс: {new_balance}")  # Логируем
    await session.execute(update(User).where(User.id == user.id).values(balance=str(new_balance)))
    await session.commit()


@connection
async def get_user_lc(session, tg_id):
    result = await session.execute(
        select(User.tg_id, User.balance)
        .where(User.tg_id == tg_id)
    )
    user = result.first()  # Получаем первую строку результата
    if user:
        tg_id, balance = user.tg_id, user.balance  # Получаем tg_id и balance
        return tg_id, balance  # Возвращаем данные
    return None  # Если пользователь не найден, возвращаем None
