from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from app.states import Chat, Image
from aiogram.fsm.context import FSMContext
import app.keybords as kb
from app.generators import gpt_text, gpt_image
from app.database.requests import set_user, get_user, calculate_image, calculate_text, get_user_lc, create_order,check_status, update_user_balance
from decimal import Decimal
from aiogram.enums import ChatAction
from app.cryptomus import create_invoice, get_invoice
import data 

from aiogram.utils.keyboard import InlineKeyboardBuilder


import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


user = Router()
is_button_enabled = False


@user.message(F.text == '❌Отмена')
@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
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
        await message.bot.send_chat_action(chat_id=message.from_user.id,action=ChatAction.TYPING)
        data = await state.get_data()
        history = data.get('history', [])
        history.append({"role": "user", "content": message.text})
        history = history[-20:]
        await state.set_state(Chat.wait)
        response = await gpt_text(history, 'gpt-4o')
        await calculate_text(message.from_user.id, response['usage'], 'gpt-4o', user)
        history.append({"role": "assistant", "content": response['response']})
        await state.update_data(history=history)
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
    if Decimal(user.balance)>=0.06:
        await state.set_state(Image.text)
        await message.answer('Введите ваш запрос', reply_markup=kb.cancel)
    else:
        await message.answer('Недостаточно средств на балансе.')


@user.message(Image.text)
async def chat_response(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance)>=0.06:
        await state.set_state(Image.wait)
        await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.UPLOAD_PHOTO)
        response = await gpt_image(message.text, 'dall-e-3')
        await calculate_image(message.from_user.id, response['usage'], 'dall-e-3', user)
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



@user.message(F.text == '🚪Личный кабинет')
async def personal_cab(message: Message):
    user_id = message.from_user.id
    user_data = await get_user_lc(user_id)
    
    if user_data:
        tg_id, balance = user_data
        cabinet_text = (
            "*Добро пожаловать в ваш личный кабинет!* 😎 \n\n"
            "Здесь вы можете управлять своим балансом и следить за расходами. 💰\n\n"
            "*Ваши данные:* \n"
            f"• **ID пользователя**: `{tg_id}` 🆔\n"
            f"• **Баланс**: `{balance}$` 💵 \n\n"
            "Используйте возможности кабинета с умом! 🔧"
        )
    else:
        cabinet_text = "*Ошибка:* Не удалось найти данные о вашем аккаунте. ❌"

    await message.answer(cabinet_text,reply_markup=kb.lc_inline, parse_mode='Markdown')


@user.callback_query(F.data == 'models_info')
async def models_info(callback_query: CallbackQuery):
    gpt_4_text = (
        "*✨ Модель GPT-4:*\n\n"
        "🚀 **GPT-4** — мощная языковая модель для создания текста и общения с ИИ.\n"
        "📚 **Создание текста**: статьи, стихи, сценарии.\n"
        "💬 **Чат с ИИ**: ведение диалогов.\n"
        "🧠 **Помощь в обучении**: ответы на вопросы и помощь в решении задач.\n\n"
        "GPT-4 использует передовые алгоритмы для работы с текстами. 🌟"
    )

    dalle_3_text = (
        "*🎨 Модель DALL·E 3:*\n\n"
        "🖼️ **DALL·E 3** — модель для создания изображений по текстовому запросу.\n"
        "✏️ **Генерация изображений**: создание уникальных картинок.\n"
        "🌍 **Многообразие стилей**: от реализма до абстракции.\n\n"
        "DALL·E 3 превращает ваши идеи в потрясающие изображения. 🎨"
    )

    #await callback_query.message.delete()
    await callback_query.answer("Информация о моделях отправлена.")
    await callback_query.message.answer(gpt_4_text + "\n\n" + dalle_3_text,reply_markup=kb.back_lc, parse_mode="Markdown")


@user.callback_query(F.data == 'backlc')
async def go_back(callback_query: CallbackQuery):
    #user_id = callback_query.message.from_user.id
    await callback_query.message.delete()
    #await personal_cab(callback_query.message, user_id=user_id)
    await callback_query.answer()

@user.callback_query(F.data == 'add_funds')
async def add_funds(callback_query: CallbackQuery):
    balance_top_up_text = (
    "💸 **Пополнение через криптовалюту**:\n"
    "Для пополнения баланса используйте удобный сервис **Cryptomus**. 🪙\n\n"
    "🔗 После выбора суммы, следуйте инструкциям на экране для завершения транзакции.\n\n"
    "💰 Пополняйте баланс с комфортом!"

)
    #await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(balance_top_up_text,reply_markup=kb.add_funds, parse_mode="Markdown")


@user.callback_query(F.data.in_(['amount_1', 'amount_2', 'amount_5', 'amount_10']))
async def handle_amount_selection(callback: CallbackQuery):
    # Извлекаем выбранную сумму из callback_data
    selected_amount = callback.data.split('_')[1]

    # Формируем сообщение с выбранной суммой
    confirmation_text = (
        f"💸 Вы выбрали пополнение на {selected_amount}$.\n"
        "Для подтверждения пополнения следуйте дальнейшим инструкциям."
    )

    # Отправляем сообщение пользователю
    await callback.answer()
    await callback.message.answer(confirmation_text, parse_mode="Markdown")

    # Здесь можно добавить логику для создания счета или дальнейших действий
    #invoice = data.data1
    invoice = await create_invoice(callback.from_user.id, selected_amount)
    markup = InlineKeyboardBuilder().button(
        text="Проверить", callback_data=f"o_{invoice['result']['uuid']}"
    )
    await create_order(invoice['result']['uuid'],invoice['result']['status'],callback.from_user.id,selected_amount)

    # Отправляем ссылку на оплату
    await callback.message.answer(
        f"💰 *Ваш счет успешно создан!* \n\n"
        f"🔗 Для оплаты перейдите по следующей ссылке: [Оплатить счет]({invoice['result']['url']}) \n\n"
        f"💳 *Используйте эту ссылку для завершения транзакции.*\n\n"
        f"⚡ *Не забывайте проверять статус счета.*",
        reply_markup=markup.as_markup(),
        parse_mode="Markdown"
    )


@user.callback_query(F.data.startswith('o_'))
async def check_order(query:CallbackQuery):
    #invoice = data.data1
    invoice = await get_invoice(query.data.split("_")[1])
    order = await check_status( 'uuid',invoice['result']['uuid'] )

    if 'result' not in invoice:
        await query.answer("Не удалось получить данные по счету.")
        await query.message.answer("К сожалению, не удалось получить информацию о платеже.")
        return
        
    if invoice["result"]["status"] in {"paid", "paid_over"}:
        if order.is_processed == False:
            await update_user_balance(query.from_user.id, invoice['result']['uuid'],invoice['result']['amount'])
            await query.answer()
            await query.message.answer('Оплата прошла успешно! Сумма была зачислена на ваш баланс.')
        else:
            await query.message.answer('Ваши деньги уже зачислены на баланс. Спасибо за оплату!')
    else:
        await query.answer()
        await query.message.answer('Ваш счет еще не оплачен. Пожалуйста, завершите оплату, чтобы продолжить.')


@user.message(F.text =='Обратная связь 📩')
async def support(message: Message):
    await message.answer('Мы всегда рядом, чтобы поддержать вас! Если у вас есть вопросы, идеи или вам просто нужна помощь — напишите нам. Мы ценим вашу обратную связь и готовы помочь в любое время!', reply_markup=kb.contact_inline)






@user.message(Command('test'))
async def test_cryptomus(message: Message):
    invoice = await create_invoice(message.from_user.id)
    markup = InlineKeyboardBuilder().button(
        text= "Проверить", callback_data=f"o_{invoice['result']['uuid']}"
    )

    await message.answer(
        f"💰 *Ваш счет успешно создан!* \n\n"
        f"🔗 Для оплаты перейдите по следующей ссылке: [Оплатить счет]({invoice['result']['url']}) \n\n"
        f"💳 *Используйте эту ссылку для завершения транзакции.*\n\n"
        f"⚡ *Не забывайте проверять статус счета.*",
        reply_markup=markup.as_markup(),
        parse_mode="Markdown"
    )
    

@user.callback_query(F.data == 'void')
async def void (callback: CallbackQuery):
    await callback.answer('🔒 Платежная система в процессе подключения.', show_alert=True)
    #await callback.message.answer('Вы открыли каталог')