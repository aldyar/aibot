from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from app.states import Chat, Image
from aiogram.fsm.context import FSMContext
import app.keybords as kb
from app.generators import gpt_text, gpt_image
from app.database.requests import set_user, get_user, calculate
from decimal import Decimal


import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


user = Router()


@user.message(F.text == '❌Отмена')
@user.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id)
    await message.answer('🤖 Добро пожаловать!\n\nЯ AI GPT-4 Bot, выбери кнопку ниже и попробуй самые продвинутые ИИ модели!', reply_markup=kb.main)


@user.message(F.text == '💬Чат')
async def chatting(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance)>0:
        await state.set_state(Chat.text)
        await message.answer('Введите ваш запрос', reply_markup=kb.cancel)
    else:
        await message.answer('Недостаточно средств на балансе.')


@user.message(Chat.text)
async def chat_response(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance)>0:
        await state.set_state(Chat.wait)
        response = await gpt_text(message.text, 'gpt-4o')
        await calculate(message.from_user.id, response['usage'], 'gpt-4o', user)
        await message.answer(response['response'],parse_mode='Markdown')
        await state.set_state(Chat.text)
    else:
        await message.answer('Недостаточно средств на балансе.')


@user.message(Chat.wait, ~F.text.startswith('/'))
async def wait_wait(message:Message):
    await message.answer('Ваше сообщение генеируется, подождите.')


@user.message(Image.wait, ~F.text.startswith('/'))
async def wait_wait(message:Message):
    await message.answer('Ваше сообщение генеируется, подождите.')


@user.message(F.text == '🖼Генерация картинок')
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



@user.message(Command('contact'))
async def contact(message: Message):
    await message.answer('Если у вас есть вопросы или предложения, буду рад помочь!  Нажмите на кнопку ниже, чтобы связаться со мной напрямую 👇',reply_markup=kb.contact_inline)



"""@user.message(F.text == 'Личный кабинет')
async def personal_cab(message: Message):
    """