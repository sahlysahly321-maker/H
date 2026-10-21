import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8735041657:AAFVtc6d_dyvh_udzVOsk2wlkbp-KKOTvnI'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- مخزن الإيميلات ---
AVAILABLE_EMAILS = [
    "user1_2026@gmail.com:Pass1234",
    "user2_2026@gmail.com:Pass5678",
    "user3_2026@gmail.com:Pass9999"
]

# --- القائمة الرئيسية ---
def main_menu():
    btn1 = InlineKeyboardButton(text="📧 قائمة الإيميلات والمخزن", callback_data="list_emails")
    btn2 = InlineKeyboardButton(text="💳 طرق الدفع والشحن", callback_data="payment_methods")
    btn3 = InlineKeyboardButton(text="🎁 نظام الإحالة", callback_data="referral_system")
    btn4 = InlineKeyboardButton(text="🛠 الدعم الفني", callback_data="support_info")
    
    return InlineKeyboardMarkup(inline_keyboard=[[btn1], [btn2], [btn3], [btn4]])

# --- أزرار قائمة الإيميلات ---
def emails_menu():
    btn_buy = InlineKeyboardButton(text="🛒 تأكيد الشراء الآن", callback_data="buy_email")
    btn_back = InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")
    return InlineKeyboardMarkup(inline_keyboard=[[btn_buy], [btn_back]])

# --- أزرار طرق الدفع ---
def payment_menu():
    btn_sham = InlineKeyboardButton(text="1️⃣ شام كاش", callback_data="pay_sham")
    btn_crypto = InlineKeyboardButton(text="2️⃣ عملات رقمية (USDT)", callback_data="pay_crypto")
    btn_back = InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")
    return InlineKeyboardMarkup(inline_keyboard=[[btn_sham], [btn_crypto], [btn_back]])

# --- زر العودة مع التحقق ---
def check_pay_menu():
    btn_check = InlineKeyboardButton(text="✅ التحقق من الدفع", callback_data="check_payment")
    btn_back = InlineKeyboardButton(text="🔙 العودة لطرق الدفع", callback_data="payment_methods")
    return InlineKeyboardMarkup(inline_keyboard=[[btn_check], [btn_back]])

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
    
    # قائمة الإيميلات
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
        
    # شراء إيميل
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
        
    # اختيار طريقة الدفع
    elif data == "payment_methods":
        text = "💳 **اختر طريقة الدفع المناسبة لك من الأسفل:**"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=payment_menu())

    # الدفع عبر شام كاش
    elif data == "pay_sham":
        text = (
            "📌 **1️⃣ شام كاش**\n\n"
            "يرجى التحويل إلى العنوان التالي:\n"
            "`18a4c2941387daeaf0256639ffc705e8`\n\n"
            "✅ **العملات المقبولة:** الدولار الأمريكي (USD) والليرة السورية (SYP)\n"
            "💱 **سعر الصرف الحالي في البوت:**\n`1 USD = 141 SYP`\n\n"
            "⚠️ بعد إتمام التحويل اضغط على **تحقق من الدفع** ثم أرسل رقم العملية من تطبيق شام كاش."
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=check_pay_menu())

    # الدفع عبر العملات الرقمية
    elif data == "pay_crypto":
        text = (
            "📌 **2️⃣ عملات رقمية (USDT)**\n\n"
            "🔹 **USDT (BEP20):**\n"
            "عنوان الاستقبال:\n`0xd22ccb682b5a8f1dbf6152882673b0130620cb11`\n"
            "⚠️ *الحد الأدنى للإيداع 0.2 USDT*\n\n"
            "───────────────────\n\n"
            "🔹 **USDT (TRC20):**\n"
            "عنوان الاستقبال:\n`TAuVtaQATX9TNyNQjKQK11pFKsx6X2hGJx`\n"
            "⚠️ *الحد الأدنى للإيداع 0.2 USDT*\n\n"
            "⚠️ أرسل العملية ثم اضغط على زر **التحقق من الدفع**."
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=check_pay_menu())

    # زر التحقق من الدفع
    elif data == "check_payment":
        text = (
            "📩 **تحقق من عملية الدفع:**\n\n"
            "يرجى إرسال رقم العملية (أو صورة عن إشعار التحويل) إلى حساب الدعم الفني ليتم تأكيد إيداعك وإضافة الرصيد فوراً.\n\n"
            "🛠 **للتواصل مع الدعم:** أرسل إشعارك هنا."
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
        text = "🛠 **الدعم الفني:**\nللتواصل والشحن أرسل للمالك مباشرة."
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
