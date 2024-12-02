from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Личный кабинет')],
                                     [KeyboardButton(text= '💬Чат'),
                                     KeyboardButton(text='🖼Генерация картинок')]],
                           resize_keyboard=True,input_field_placeholder='Выберите пункт меню.')



cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = '❌Отмена')]],
                             resize_keyboard=True)
contact_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Написать администратору', url='https://t.me/adiqa00')]
])

