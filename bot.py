import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8735041657:AAFVtc6d_dyvh_udzVOsk2wlkbp-KKOTvnI'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# قائمة الإيميلات الجاهزة
AVAILABLE_EMAILS = [
    "user1_2026@gmail.com:Pass1234",
    "user2_2026@gmail.com:Pass5678",
    "user3_2026@gmail.com:Pass9999"
]

# الأزرار الرئيسية
def main_menu():
    btn1 = InlineKeyboardButton(text="📧 قائمة الإيميلات", callback_data="list_emails")
    btn2 = InlineKeyboardButton(text="🛒 شراء إيميل (فوري)", callback_data="buy_email")
    btn3 = InlineKeyboardButton(text="💳 طرق الدفع والشحن", callback_data="payment_methods")
    btn4 = InlineKeyboardButton(text="🎁 نظام الإحالة", callback_data="referral_system")
    btn5 = InlineKeyboardButton(text="🛠 الدعم الفني", callback_data="support_info")
    
    return InlineKeyboardMarkup(inline_keyboard=[[btn1], [btn2], [btn3], [btn4], [btn5]])

# زر العودة
def back_menu():
    btn = InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")
    return InlineKeyboardMarkup(inline_keyboard=[[btn]])

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "أهلاً بك في متجر الإيميلات الفوري! 📧✨\nاختر من القائمة أدناه الخدمة التي تريدها:",
        reply_markup=main_menu()
    )

@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    data = callback.data
    
    if data == "list_emails":
        count = len(AVAILABLE_EMAILS)
        text = f"📦 **المخزن الحالي:**\n\n• عدد الإيميلات المتوفرة: `{count}` إيميل\n• السعر: 1$ لكل إيميل"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    elif data == "buy_email":
        if AVAILABLE_EMAILS:
            email_data = AVAILABLE_EMAILS.pop(0)
            text = f"✅ **تم الشراء بنجاح!**\n\n📧 **بيانات الإيميل:**\n`{email_data}`"
        else:
            text = "❌ **المخزن فارغ حالياً!**"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    elif data == "payment_methods":
        text = "💳 **طرق الدفع المتاحة:**\n\n1️⃣ USDT (TRC20)\n2️⃣ Payeer\n3️⃣ شام كاش / سيريتل كاش"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    elif data == "referral_system":
        bot_info = await bot.get_me()
        user_id = callback.from_user.id
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        text = f"🎁 **رابط الدعوة الخاص بك:**\n`{ref_link}`"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    elif data == "support_info":
        text = "🛠 **الدعم الفني:**\nللتواصل والشحن ارسل للمالك هنا."
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    elif data == "back_to_main":
        await callback.message.edit_text("القائمة الرئيسية للمتجر 📧:", reply_markup=main_menu())
        
    await callback.answer()

async def main():
    print("🚀 البوت شغال...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())


