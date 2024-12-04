# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = KeyboardButton('Рассчитать')
btn2 = KeyboardButton('Информация')
kb.add(btn1, btn2)

menu = InlineKeyboardMarkup(row_width=2)
kb1 = InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories')
kb2 = InlineKeyboardButton('Формула расчёта', callback_data='formulas')
menu.add(kb1, kb2)

class User_state(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)

@dp.message_handler(text = 'Информация')
async def info(message: types.Message):
    await message.answer('Информация о боте.', reply_markup=kb)

@dp.message_handler(text = 'Рассчитать')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию.', reply_markup=menu)

@dp.callback_query_handler(text = 'calories')
async def calories(call: types.CallbackQuery):
    await call.message.answer('Введите ваш возраст')
    await User_state.age.set()

@dp.message_handler(state=User_state.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('Введите ваш рост')
    await User_state.growth.set()

@dp.message_handler(state=User_state.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.answer('Введите ваш вес')
    await User_state.weight.set()

@dp.message_handler(state=User_state.weight)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data["age"])
    growth = int(data["growth"])
    weight = int(data["weight"])
    calories = (10*weight + 6.25*growth - 5*age + 5)*1.2
    await message.answer(f'Ваша суточная норма калорий: {calories}')
    await message.answer(f'Ваш индекс массы тела: {round(int(data["weight"])/((int(data["growth"])/100)**2),0)}')
    await message.answer('Выберите опцию.', reply_markup=kb)
    await state.finish()

@dp.callback_query_handler(text = 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer('Формула расчёта калорий: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.answer()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)