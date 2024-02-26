import sqlite3
import threading
from aiogram import Bot, Dispatcher, types,executor
from aiogram.types import Message
from ChatGPT import gpt

TOKEN = ''
bot = Bot(TOKEN)            
dp = Dispatcher(bot)


def create_table():
    with sqlite3.connect('gpt_us.db') as connect:
        cursor = connect.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ChatGPT (
            id INTEGER PRIMARY KEY,
            con TEXT,
            con2 TEXT
            )
        """)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    with sqlite3.connect('gpt_us.db') as connect:
        cursor = connect.cursor()
        cursor.execute("INSERT OR IGNORE INTO ChatGPT(id, con, con2) VALUES (?, ?, ?)",
                       (message.from_user.id, '', ''))
    await message.answer('Привет, Я помощник главы EVOLUTE AI 🔥\nПриступим!')

@dp.message_handler(commands=['reset'])
async def reset(message: types.Message):
    with sqlite3.connect('gpt_us.db') as connect:
        cursor = connect.cursor()
        cursor.execute("UPDATE ChatGPT SET con = '', con2 = '' WHERE id = ?", (message.from_user.id,))
    await message.answer('✅История диалога очищена✅')

@dp.message_handler(content_types=types.ContentType.TEXT)
async def mes(message: types.Message):
    thread = threading.Thread(target=gpt, args=(message.text, message.from_user.id, message.message_id))
    thread.start()

if __name__ == '__main__':
    create_table()
    executor.start_polling(dp)
