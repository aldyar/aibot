from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🚪Личный кабинет')],
                                     [KeyboardButton(text= '💬Чат'),
                                     KeyboardButton(text='🖼Генерация картинок')],
                                     [KeyboardButton(text='Обратная связь 📩')]],
                           resize_keyboard=True,input_field_placeholder='Выберите пункт меню.')



cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = '❌Отмена')]],
                             resize_keyboard=True)
contact_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Обратная связь 📩', url='https://t.me/adiqa00')]
])

lc_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "💸Пополнить баланс", callback_data='add_funds' )],
    [InlineKeyboardButton(text = "📚Информация о моделях", callback_data='models_info' )]
])

back_lc = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "🔙Назад", callback_data='backlc' )],
    
])

add_funds = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "1$", callback_data='amount_1' ),
    InlineKeyboardButton(text = "2$", callback_data='amount_2' ),
    InlineKeyboardButton(text = "5$", callback_data='amount_5' ),
    InlineKeyboardButton(text = "10$", callback_data='amount_10' )],
    [InlineKeyboardButton(text = "🔙Назад", callback_data='backlc' )]

])

