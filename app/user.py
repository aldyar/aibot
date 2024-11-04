from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from app.states import Chat, Image
from aiogram.fsm.context import FSMContext
import app.keybords as kb
from app.generators import gpt_text, gpt_image, gpt_vision
from app.database.requests import set_user, get_user, calculate
import uuid
import os

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from decimal import Decimal

user = Router()


@user.message(F.text == 'Отмена')
@user.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id)
    await message.answer('Добро Пожаловать!', reply_markup=kb.main)


@user.message(F.text == 'Чат')
async def chatting(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance)>0:
        await state.set_state(Chat.text)
        await message.answer('Введите ваш запрос', reply_markup=kb.cancel)
    else:
        await message.answer('Недостаточно средств на балансе.')


#GPT Vision
@user.message(Chat.text, F.photo)
async def chat_vision(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    logger.info(f"Получено сообщение от пользователя: {user.id}")
    if Decimal(user.balance)>0:
        await state.set_state(Chat.wait)
        logger.info(f"Баланс пользователя {user.id} достаточен: {user.balance}")

        file = await message.bot.get_file(message.photo[-1].file_id)
        file_path = file.file_path
        file_name = uuid.uuid4()
        await message.bot.download_file(file_path, f'{file_name}.jpeg')
        logger.info(f"Файл загружен: {file_name}")
        
        caption = message.text.strip() if message.text else "What is in this image?"
        try:
        #caption <-> text
            response = await gpt_vision(caption, 'gpt-4o', f'{file_name}.jpeg')
            logger.info(f"Ответ от gpt_vision: {response}")  # Логируем ответ
            if hasattr(response, 'usage') and hasattr(response, 'response'):
                await calculate(message.from_user.id, response.usage, 'gpt-4o', user)
                await message.answer(response['response'])
                logger.info(f"Ответ отправлен пользователю {user.id}: {response['response']}")
            else:
                logger.error(f"Неверный формат ответа: {response}")
                await message.answer("Произошла ошибка при обработке вашего запроса. Попробуйте еще раз.")
        except Exception as e:
            logger.error(f"Ошибка при обработке изображения: {str(e)}")
            await message.answer("Произошла ошибка при обработке вашего запроса. Попробуйте еще раз.")
        finally:
            os.remove(f'{file_name}.jpeg')
            logger.info(f"Файл удалён: {file_name}")
    else:
        await message.answer('Недостаточно средств на балансе.')


@user.message(Chat.text)
async def chat_response(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance)>0:
        await state.set_state(Chat.wait)
        response = await gpt_text(message.text, 'gpt-4o')
        await calculate(message.from_user.id, response['usage'], 'gpt-4o', user)
        await message.answer(response['response'])
    else:
        await message.answer('Недостаточно средств на балансе.')


@user.message(Image.wait)
@user.message(Chat.wait)
async def wait_wait(message:Message):
    await message.answer('Ваше сообщение генеируется, подождите.')


@user.message(F.text == 'Генерация картинок')
async def chatting(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance)>0:
        await state.set_state(Image.text)
        await message.answer('Введите ваш запрос', reply_markup=kb.cancel)
    else:
        await message.answer('Недостаточно средств на балансе.')


@user.message(Image.text)
async def chat_response(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance)>0:
        await state.set_state(Image.wait)
        response = await gpt_image(message.text, 'dall-e-3')
        await calculate(message.from_user.id, response['usage'], 'dall-e-3', user)
        print(response)
        try:
            await message.answer_photo(photo=response['response'])
        except Exception as e:
            print(e)
            await message.answer(response['response'])
        await state.set_state(Image.text)
    else:
        await message.answer('Недостаточно средств на балансе.')



"""@user.message(Chat.text, F.photo)
async def chat_response(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    logger.info(f"Получено сообщение от пользователя: {user.id}")
    if Decimal(user.balance)>0:
        await state.set_state(Chat.wait)
        logger.info(f"Баланс пользователя {user.id} достаточен: {user.balance}")

        file = await message.bot.get_file(message.photo[-1].file_id)
        file_path = file.file_path
        file_name = uuid.uuid4()
        await message.bot.download_file(file_path, f'{file_name}.jpeg')
        logger.info(f"Файл загружен: {file_name}")
        
        caption = message.text.strip() if message.text else "What is in this image?"
        try:
        #caption <-> text
            response = await gpt_vision(caption, 'gpt-4o', f'{file_name}.jpeg')
            await calculate(message.from_user.id, response['usage'], 'gpt-4o', user)
            await message.answer(response['response'])
            logger.info(f"Ответ отправлен пользователю {user.id}: {response['response']}")
        except Exception as e:
            logger.error(f"Ошибка при обработке изображения: {str(e)}")
            await message.answer("Произошла ошибка при обработке вашего запроса. Попробуйте еще раз.")
        finally:
            os.remove(f'{file_name}.jpeg')
            logger.info(f"Файл удалён: {file_name}")
    else:
        await message.answer('Недостаточно средств на балансе.')"""