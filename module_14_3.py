from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    InputFile
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
import asyncio
from aiogram.types import FSInputFile

API_TOKEN = '7243782313:AAGE5Qm7NBFbdBUyZKxiXE-6bD2RKrhgg5s'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    age = State()
    growth = State()
    weight = State()

main_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text='Рассчитать')],
        [KeyboardButton(text='Информация')],
        [KeyboardButton(text='Купить')]
    ]
)

buying_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Product1', callback_data='product_buying')],
        [InlineKeyboardButton(text='Product2', callback_data='product_buying')],
        [InlineKeyboardButton(text='Product3', callback_data='product_buying')],
        [InlineKeyboardButton(text='Product4', callback_data='product_buying')]
    ]
)

@dp.message(F.text.lower() == 'привет')
async def greet(message: types.Message):
    await message.answer("Введите команду /start, чтобы начать общение.")

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью.", reply_markup=main_keyboard)

@dp.message(F.text == 'Рассчитать')
async def main_menu(message: types.Message):
    await message.reply("Выберите опцию:", reply_markup=inline_keyboard)

@dp.message(F.text == 'Купить')
async def get_buying_list(message: types.Message):
    for i in range(1, 5):
        product_info = (
            f"Название: Product{i} | "
            f"Описание: описание {i} | "
            f"Цена: {i * 100}"
        )
        photo = FSInputFile(f'images/product{i}.jpg')  # Используем FSInputFile для локального файла
        await message.answer_photo(
            photo=photo,
            caption=product_info
        )
    await message.answer("Выберите продукт для покупки:", reply_markup=buying_inline_keyboard)

@dp.callback_query(F.data == 'product_buying')
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()

@dp.callback_query(F.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    formula_text = (
        "Формула Миффлина-Сан Жеора для расчёта калорий:\n\n"
        "Мужчины: 10 × вес (кг) + 6.25 × рост (см) - 5 × возраст + 5\n"
        "Женщины: 10 × вес (кг) + 6.25 × рост (см) - 5 × возраст - 161"
    )
    await call.message.answer(formula_text)
    await call.answer()

@dp.callback_query(F.data == 'calories')
async def set_age(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите свой возраст:")
    await state.set_state(Form.age)
    await call.answer()

@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await message.reply("Введите свой рост:")
    await state.set_state(Form.growth)

@dp.message(Form.growth)
async def process_growth(message: types.Message, state: FSMContext):
    await state.update_data(growth=int(message.text))
    await message.reply("Введите свой вес:")
    await state.set_state(Form.weight)

@dp.message(Form.weight)
async def process_weight(message: types.Message, state: FSMContext):
    data = await state.get_data()
    weight = int(message.text)
    age = data['age']
    growth = data['growth']

    calories = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.reply(f"Ваша норма калорий: {calories:.2f}")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
