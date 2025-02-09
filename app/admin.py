from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command
from aiogram.fsm.context import FSMContext
from app.states import Newsletter
from app.database.requests import get_users, get_users
import asyncio
from aiogram import Bot
import app.text as txt
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError

admin = Router()

class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in [1075213318]
    

@admin.message(Admin(), Command('newsletter'))
async def newsletter(message: Message, state: FSMContext):
    await state.set_state(Newsletter.message)
    await message.answer('Введите сообщение рассылки')


@admin.message(Newsletter.message)
async def newsletter_message(message: Message, state:FSMContext):
    await state.clear()
    await message.answer('Рассылка началась')
    users = await get_users()
    for user in users:
        try:
            await message.send_copy(chat_id=user.tg_id)
        except Exception as e:
            print(e)
    await message.answer('Рассылка завершена')
    

@admin.message(Admin(), Command('news'))
async def send_broadcast(message:Message, bot: Bot):
    users = await get_users()
    user_ids = [user.tg_id for user in users]

    total_users = len(user_ids)
    success_count = 0
    blocked_count = 0
    failed_count = 0

    await message.answer(f"📢 Начинаю рассылку... Количество пользователей: {total_users}")

    for user_id in user_ids:
        try:
            await bot.send_message(
                user_id,txt.text,
                parse_mode="Markdown"
            )
            success_count += 1
        except TelegramForbiddenError:  # Пользователь заблокировал бота
            blocked_count += 1
        except TelegramAPIError as e:  # Любая другая ошибка
            failed_count += 1
            print(f"Ошибка отправки {user_id}: {e}")
        
        await asyncio.sleep(0.3)  # Задержка, чтобы избежать блокировки

    await message.answer(
        f"✅ Рассылка завершена!\n\n"
        f"📬 Успешно доставлено: {success_count}\n"
        f"🚫 Пользователей заблокировали бота: {blocked_count}\n"
        f"❌ Ошибки: {failed_count}"
    )


