import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
import textwrap

TOKEN = "8096361528:AAGifPEXIZ7FrefyI5CzqewRIa-0vuBF1fM"
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

EQUIPMENT = {
    "Палатка 2-местная": 400,
    "Шатер-палатка 2.4×2.4×1.7 м": 900,
    "Сапборд 3.2×76×15 (до 150 кг)": 1200,
    "Туристический стул": 250,
}

DEPOSIT = 2000

class OrderState(StatesGroup):
    choosing_item = State()
    entering_days = State()

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    items = "\n".join([f"• {name} — {price}₽/сутки" for name, price in EQUIPMENT.items()])
    await message.answer(
        textwrap.dedent(f"""        👋 Привет! Это бот для аренды туристического снаряжения.

        📦 Доступное оборудование:
        {items}

        💰 Залог: {DEPOSIT}₽ (фиксированный)

        Напиши <b>название снаряжения</b>, которое хочешь арендовать.
        """)
    )
    await state.set_state(OrderState.choosing_item)

@dp.message(OrderState.choosing_item)
async def choose_item(message: Message, state: FSMContext):
    item = message.text.strip()
    if item not in EQUIPMENT:
        return await message.answer("❌ Такого снаряжения нет. Попробуй скопировать название из списка.")
    await state.update_data(item=item)
    await message.answer("📆 На сколько суток хотите арендовать?")
    await state.set_state(OrderState.entering_days)

@dp.message(OrderState.entering_days)
async def enter_days(message: Message, state: FSMContext):
    try:
        days = int(message.text.strip())
        if days <= 0:
            raise ValueError
    except ValueError:
        return await message.answer("❌ Введите корректное количество суток (целое число больше 0).")

    data = await state.get_data()
    item = data["item"]
    price_per_day = EQUIPMENT[item]
    total_rent = price_per_day * days
    total = total_rent + DEPOSIT

    await message.answer(
        textwrap.dedent(f"""        ✅ <b>Бронирование подтверждено</b>

        🧾 Оборудование: {item}  
        📅 Срок: {days} суток  
        💵 Аренда: {total_rent}₽  
        💰 Залог: {DEPOSIT}₽  
        🧮 <b>Итого: {total}₽</b>

        Спасибо за бронирование!
        """)
    )
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
Pip install aiogram
Python main.py

