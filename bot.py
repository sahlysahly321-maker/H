import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8735041657:AAFVtc6d_dyvh_udzVOsk2wlkbp-KKOTvnI'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- قائمة الإيميلات المتوفرة في المخزن ---
AVAILABLE_EMAILS = [
    "user1_2026@gmail.com:Pass1234",
    "user2_2026@gmail.com:Pass5678",
    "user3_2026@gmail.com:Pass9999"
]

# --- لوحة القائمة الرئيسية ---
def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 قائمة الإيميلات المتوفرة", callback_data="list_emails")],
        [InlineKeyboardButton(text="🛒 شراء إيميل (فوري)", callback_data="buy_email")],
        [InlineKeyboardButton(text="💳 طرق الدفع والشحن", callback_data="payment_methods")],
        [InlineKeyboardButton(text="🎁 نظام الإحالة (أرباحك)", callback_data="referral_system")],
        [InlineKeyboardButton(text="🛠 الدعم الفني والتواصل", callback_data="support_info")]
    ])

# --- زر العودة للقائمة الرئيسية ---
def back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]
    ])

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"أهلاً بك يا {user_name} في متجر الإيميلات الفوري! 📧✨\n"
        f"اختر من القائمة أدناه الخدمة التي تريدها:",
        reply_markup=main_keyboard()
    )

# 1. عرض قائمة الإيميلات
@dp.callback_query(lambda c: c.data == 'list_emails')
async def show_emails(callback: types.CallbackQuery):
    count = len(AVAILABLE_EMAILS)
    text = (
        f"📦 **المخزن الحالي:**\n\n"
        f"• عدد الإيميلات المتوفرة جاهزة للتسليم: `{count}` إيميل\n"
        f"• النوع: Gmail جاهز ومفعل\n"
        f"• السعر: 1$ لكل إيميل\n\n"
        f"اضغط على **شراء إيميل** من القائمة للشراء الفوري."
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_keyboard())

# 2. عملية الشراء الفوري
@dp.callback_query(lambda c: c.data == 'buy_email')
async def process_buy(callback: types.CallbackQuery):
    if AVAILABLE_EMAILS:
        email_data = AVAILABLE_EMAILS.pop(0)  # سحب أول إيميل من القائمة
        text = (
            f"✅ **تم الشراء بنجاح!**\n\n"
            f"📧 **بيانات الإيميل:**\n`{email_data}`\n\n"
            f"*اضغط على النص السكني أعلاه لنسخه مباشرة.*"
        )
    else:
        text = "❌ **عذراً، المخزن فارغ حالياً!**\nيرجى التواصل مع الدعم لشحن المخزن."
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_keyboard())

# 3. طرق الدفع
@dp.callback_query(lambda c: c.data == 'payment_methods')
async def show_payment(callback: types.CallbackQuery):
    text = (
        "💳 **طرق الدفع المتاحة للشحن:**\n\n"
        "1️⃣ **USDT (TRC20):** `TYourWalletAddressHere`\n"
        "2️⃣ **Payeer:** `P123456789`\n"
        "3️⃣ **Syriatel Cash / Sham Cash:** `09xxxxx`\n\n"
        "📌 *بعد تحويل المبلغ، يرجى إرسال صورة الإشعار للدعم الفني لتعبئة رصيدك.*"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_keyboard())

# 4. نظام الإحالة (دعوة الأصدقاء)
@dp.callback_query(lambda c: c.data == 'referral_system')
async def show_referral(callback: types.CallbackQuery):
    bot_info = await bot.get_me()
    user_id = callback.from_user.id
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    
    text = (
        "🎁 **برنامج الإحالة والمكافآت:**\n\n"
        "شارك رابط الدعوة الخاص بك مع أصدقائك واحصل على إيميل مجاني لكل 5 أصدقاء يسجلون في البوت!\n\n"
        f"🔗 **رابط الدعوة الخاص بك:**\n`{ref_link}`"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_keyboard())

# 5. الدعم الفني
@dp.callback_query(lambda c: c.data == 'support_info')
async def show_support(callback: types.CallbackQuery):
    text = (
        "🛠 **الدعم الفني والخدمة:**\n\n"
        "إذا واجهتك أي مشكلة أو أردت الشحن السريع، يمكنك التواصل مباشرة مع المالك عبر المعرف التالي:\n\n"
        "👤 **صاحب المتجر:** @YourTelegramUsername"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_keyboard())

# الرجوع للقائمة الرئيسية
@dp.callback_query(lambda c: c.data == 'back_to_main')
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "القائمة الرئيسية للمتجر 📧:",
        reply_markup=main_keyboard()
    )

async def main():
    print("🚀 البوت المطور شغال الآن...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

