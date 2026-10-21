import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8735041657:AAFVtc6d_dyvh_udzVOsk2wlkbp-KKOTvnI'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- مخزن الإيميلات (ضع إيميلاتك الحقيقية هنا) ---
AVAILABLE_EMAILS = [
    "user1_2026@gmail.com:Pass1234",
    "user2_2026@gmail.com:Pass5678",
    "user3_2026@gmail.com:Pass9999"
]

# --- القائمة الرئيسية (تم حذف زر الشراء الفوري منها) ---
def main_menu():
    btn1 = InlineKeyboardButton(text="📧 قائمة الإيميلات والمخزن", callback_data="list_emails")
    btn2 = InlineKeyboardButton(text="💳 طرق الدفع والشحن", callback_data="payment_methods")
    btn3 = InlineKeyboardButton(text="🎁 نظام الإحالة", callback_data="referral_system")
    btn4 = InlineKeyboardButton(text="🛠 الدعم الفني", callback_data="support_info")
    
    return InlineKeyboardMarkup(inline_keyboard=[[btn1], [btn2], [btn3], [btn4]])

# --- لوحة أزرار قسم الإيميلات (تحتوي على زر الشراء وزر العودة) ---
def emails_menu():
    btn_buy = InlineKeyboardButton(text="🛒 تأكيد الشراء الآن", callback_data="buy_email")
    btn_back = InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")
    return InlineKeyboardMarkup(inline_keyboard=[[btn_buy], [btn_back]])

# --- زر العودة البسيط ---
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
    
    # عند الضغط على قائمة الإيميلات
    if data == "list_emails":
        count = len(AVAILABLE_EMAILS)
        text = (
            f"📦 **مخزن الإيميلات المتوفرة:**\n\n"
            f"• عدد الإيميلات المتاحة للبيع: `{count}` إيميل\n"
            f"• النوع: Gmail جاهز ومفعل\n"
            f"• السعر: 1$ لكل إيميل\n\n"
            f"👇 اضغط على زر **تأكيد الشراء الآن** للظفر بإيميلك فوراً:"
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=emails_menu())
        
    # عند إتمام عملية الشراء داخل قسم الإيميلات
    elif data == "buy_email":
        if AVAILABLE_EMAILS:
            email_data = AVAILABLE_EMAILS.pop(0)
            text = (
                f"✅ **تم الشراء بنجاح!**\n\n"
                f"📧 **بيانات الإيميل:**\n`{email_data}`\n\n"
                f"*اضغط على النص أعلاه لنسخه مباشرة.*"
            )
        else:
            text = "❌ **عذراً، المخزن فارغ حالياً!**\nيرجى التواصل مع الدعم لتعبئة المخزن."
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    # طرق الدفع
    elif data == "payment_methods":
        text = (
            "💳 **طرق الدفع المتاحة:**\n\n"
            "1️⃣ **USDT (TRC20):** `TYourWalletAddressHere`\n"
            "2️⃣ **Payeer:** `P123456789`\n"
            "3️⃣ **شام كاش / سيريتل كاش:** `09xxxxx`\n\n"
            "📌 *بعد التحويل، أرسل الإشعار للدعم الفني لتعبئة رصيدك.*"
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    # نظام الإحالة
    elif data == "referral_system":
        bot_info = await bot.get_me()
        user_id = callback.from_user.id
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        text = f"🎁 **برنامج الإحالة:**\n\nشارك رابط الدعوة الخاص بك وحصل على مكافآت عند إرساله لأصدقائك:\n\n`{ref_link}`"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    # الدعم الفني
    elif data == "support_info":
        text = "🛠 **الدعم الفني:**\nللتواصل والشحن أرسل للمالك مباشرة: @YourTelegramUsername"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    # العودة للقائمة الرئيسية
    elif data == "back_to_main":
        await callback.message.edit_text("القائمة الرئيسية للمتجر 📧:", reply_markup=main_menu())
        
    await callback.answer()

async def main():
    print("🚀 البوت المطور شغال...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
