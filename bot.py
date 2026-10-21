import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8735041657:AAFVtc6d_dyvh_udzVOsk2wlkbp-KKOTvnI'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def buy_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 شراء إيميل (فوري)", callback_data="buy_email")]
    ])

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "أهلاً بك في متجر الإيميلات الفوري! 📧\nاضغط على الزر أدناه لشراء واستلام إيميلك فوراً:",
        reply_markup=buy_keyboard()
    )

@dp.callback_query(lambda c: c.data == 'buy_email')
async def process_buy(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    sample_email = "test_user_2026@gmail.com:Password123"

    await bot.send_message(
        chat_id=user_id,
        text=f"✅ **تم الشراء بنجاح!**\n\n📧 **بيانات الإيميل:**\n`{sample_email}`\n\n*اضغط على النص لنسخه مباشرة.*",
        parse_mode="Markdown"
    )
    await callback_query.answer("تم تسليم الإيميل بنجاح!")

async def main():
    print("🚀 البوت شغال هلق وعم يستمع للرسائل...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
