import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = '8735041657:AAFVtc6d_dyvh_udzVOsk2wlkbp-KKOTvnI'
ADMIN_ID = 7927059374
ADMIN_USERNAME = "@Alaaa057"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class DepositState(StatesGroup):
    waiting_for_proof = State()

# مخازن الإيميلات حسب الفئات
EMAILS_OLD = [
    "old_user1_2026@gmail.com:Pass1234",
    "old_user2_2026@gmail.com:Pass5678"
]

EMAILS_NEW = [
    "new_user1_2026@gmail.com:Pass1234",
    "new_user2_2026@gmail.com:Pass5678"
]

EMAILS_MEDIUM = [
    "med_user1_2026@gmail.com:Pass1234",
    "med_user2_2026@gmail.com:Pass5678"
]

def main_menu():
    btn1 = InlineKeyboardButton(text="📧 قائمة الإيميلات والمخزن", callback_data="list_emails")
    btn2 = InlineKeyboardButton(text="💳 طرق الدفع والشحن", callback_data="payment_methods")
    btn3 = InlineKeyboardButton(text="🎁 نظام الإحالة", callback_data="referral_system")
    btn4 = InlineKeyboardButton(text="🛠 الدعم الفني", callback_data="support_info")
    return InlineKeyboardMarkup(inline_keyboard=[[btn1], [btn2], [btn3], [btn4]])

def email_categories_menu():
    btn1 = InlineKeyboardButton(text="1️⃣ إيميلات قديمة (0.6$)", callback_data="cat_old")
    btn2 = InlineKeyboardButton(text="2️⃣ إيميلات جديدة (0.35$)", callback_data="cat_new")
    btn3 = InlineKeyboardButton(text="3️⃣ إيميلات (7-30 يوم) (0.6$)", callback_data="cat_medium")
    btn_back = InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")
    return InlineKeyboardMarkup(inline_keyboard=[[btn1], [btn2], [btn3], [btn_back]])

def buy_menu(category_code):
    btn_buy = InlineKeyboardButton(text="🛒 تأكيد الشراء الآن", callback_data=f"buy_{category_code}")
    btn_back = InlineKeyboardButton(text="🔙 العودة لفئات الإيميلات", callback_data="list_emails")
    return InlineKeyboardMarkup(inline_keyboard=[[btn_buy], [btn_back]])

def payment_menu():
    btn_sham = InlineKeyboardButton(text="1️⃣ شام كاش", callback_data="pay_sham")
    btn_crypto = InlineKeyboardButton(text="2️⃣ عملات رقمية (USDT)", callback_data="pay_crypto")
    btn_back = InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")
    return InlineKeyboardMarkup(inline_keyboard=[[btn_sham], [btn_crypto], [btn_back]])

def check_pay_menu():
    btn_check = InlineKeyboardButton(text="✅ التحقق من الدفع", callback_data="check_payment")
    btn_back = InlineKeyboardButton(text="🔙 العودة لطرق الدفع", callback_data="payment_methods")
    return InlineKeyboardMarkup(inline_keyboard=[[btn_check], [btn_back]])

def back_menu():
    btn = InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")
    return InlineKeyboardMarkup(inline_keyboard=[[btn]])

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "أهلاً بك في متجر الإيميلات الفوري! 📧✨\nاختر من القائمة أدناه الخدمة التي تريدها:",
        reply_markup=main_menu()
    )

@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    
    if data == "list_emails":
        text = "📦 **يرجى اختيار فئة الإيميلات المطلوبة من القائمة أدناه:**"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=email_categories_menu())
        
    elif data == "cat_old":
        count = len(EMAILS_OLD)
        text = (
            f"📌 **1️⃣ إيميلات قديمة:**\n\n"
            f"💵 **السعر:** 0.6$\n"
            f"📅 **العمر:** تاريخ إنشاء من نصف سنة إلى 5 سنين\n"
            f"📊 **المتوفر:** `{count}` إيميل\n"
            f"🛡 **الكفالة:** لمدة يومين من تاريخ الشراء\n\n"
            f"⚠️ **ملاحظة هامة:** يجب إضافتها أول مرة على إنترنت سوري.\n"
            f"في حال طلب الإيميل تحقق، يرجى التواصل مع الدعم وسنكمل عملية التحقق فوراً.\n\n"
            f"👇 اضغط على **تأكيد الشراء الآن** للشراء:"
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=buy_menu("old"))

    elif data == "cat_new":
        count = len(EMAILS_NEW)
        text = (
            f"📌 **2️⃣ إيميلات جديدة:**\n\n"
            f"💵 **السعر:** 0.35$\n"
            f"📊 **المتوفر:** `{count}` إيميل\n"
            f"🛡 **الكفالة:** لمدة 24 ساعة من تاريخ الشراء\n\n"
            f"👇 اضغط على **تأكيد الشراء الآن** للشراء:"
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=buy_menu("new"))

    elif data == "cat_medium":
        count = len(EMAILS_MEDIUM)
        text = (
            f"📌 **3️⃣ إيميلات (من 7 أيام إلى 30 يوم):**\n\n"
            f"💵 **السعر:** 0.6$\n"
            f"📅 **العمر:** من 7 أيام إلى 30 يوم\n"
            f"📊 **المتوفر:** `{count}` إيميل\n"
            f"🛡 **الكفالة:** لمدة يومين من تاريخ الشراء\n\n"
            f"👇 اضغط على **تأكيد الشراء الآن** للشراء:"
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=buy_menu("medium"))
        
    elif data.startswith("buy_"):
        cat = data.split("_")[1]
        target_list = EMAILS_OLD if cat == "old" else (EMAILS_NEW if cat == "new" else EMAILS_MEDIUM)
        
        if target_list:
            email_data = target_list.pop(0)
            text = (
                f"✅ **تم الشراء بنجاح!**\n\n"
                f"📧 **بيانات الإيميل:**\n`{email_data}`\n\n"
                f"*اضغط على النص أعلاه لنسخه مباشرة.*"
            )
        else:
            text = "❌ **عذراً، هذه الفئة فارغة حالياً!**\nيرجى التواصل مع الدعم لتعبئة المخزن."
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    elif data == "payment_methods":
        await state.clear()
        text = "💳 **اختر طريقة الدفع المناسبة لك من الأسفل:**"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=payment_menu())

    elif data == "pay_sham":
        text = (
            "📌 **1️⃣ شام كاش**\n\n"
            "يرجى التحويل إلى العنوان التالي:\n"
            "`18a4c2941387daeaf0256639ffc705e8`\n\n"
            "✅ **العملات المقبولة:** الدولار الأمريكي (USD) والليرة السورية (SYP)\n"
            "💱 **سعر الصرف الحالي في البوت:**\n`1 USD = 141 SYP`\n\n"
            "⚠️ بعد إتمام التحويل اضغط على **التحقق من الدفع** لتسجيل رقم العملية."
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=check_pay_menu())

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

    elif data == "check_payment":
        await state.set_state(DepositState.waiting_for_proof)
        text = "📩 **يرجى كتابة رقم العملية (أو إرسال صورة إشعار التحويل) الآن في المحادثة:**"
        await callback.message.edit_text(text, parse_mode="Markdown")

    elif data == "referral_system":
        bot_info = await bot.get_me()
        user_id = callback.from_user.id
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        text = f"🎁 **برنامج الإحالة:**\n\nشارك رابط الدعوة الخاص بك وحصل على مكافآت عند إرساله لأصدقائك:\n\n`{ref_link}`"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    elif data == "support_info":
        text = f"🛠 **الدعم الفني:**\nللتواصل والشحن أرسل للمالك مباشرة: {ADMIN_USERNAME}"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    elif data == "back_to_main":
        await state.clear()
        await callback.message.edit_text("القائمة الرئيسية للمتجر 📧:", reply_markup=main_menu())
        
    await callback.answer()

@dp.message(DepositState.waiting_for_proof)
async def process_proof(message: types.Message, state: FSMContext):
    await state.clear()
    
    user_text = (
        "⏳ **تم استلام بيانات التحويل بنجاح!**\n\n"
        "جاري التحقق من العملية وتأكيد الشحن..\n"
        "⏱ **سيتم إضافة الرصيد إلى حسابك خلال 5 إلى 15 دقيقة.**\n\n"
        "شكراً لانتظارك! 🌹"
    )
    await message.answer(user_text, parse_mode="Markdown", reply_markup=back_menu())
    
    try:
        admin_text = (
            f"📥 **طلب إيداع جديد!**\n\n"
            f"👤 **الزبون:** {message.from_user.full_name} (@{message.from_user.username})\n"
            f"🆔 **ID الزبون:** `{message.from_user.id}`\n\n"
            f"📝 **بيانات العملية / النص المرسل:**\n{message.text if message.text else 'أرسل صورة إشعار'}"
        )
        if message.photo:
            await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=admin_text, parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Failed to send admin notification: {e}")

async def handle_ping(request):
    return web.Response(text="Bot is active and running 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    print("🚀 البوت يعمل مع خادم الاستجابة...")
    await bot.delete_webhook(drop_pending_updates=True)
    await start_web_server()
    await dp.start_polling(bot, handle_signals=False)

if __name__ == '__main__':
    asyncio.run(main())

