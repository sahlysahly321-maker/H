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

# قاعدة بيانات مؤقتة لرصيد المستخدمين {user_id: balance}
user_balances = {}

# مخازن الإيميلات
EMAILS_OLD = [
    "mk2915564@gmail.com:orange2006#",
    "millmaize@gmail.com:orange2006#",
    "goldendome63@gmail.com:orange2006#"
]

EMAILS_NEW = [
    "hoiphonop7@gmail.com:orange2006#",
"arsenyefim01@gmail.com:orange2006#"
"enginaltan276@gmail.com:orange2006#"  
]

EMAILS_MEDIUM = [
    "fathserifalkadi@gmail.com:orange2006#",
"kiza46809@gmail.com:orange2006#"
"salehmardani355@gmail.com:orange2006#"
]

# طلبات الشحن المعلقة {deposit_id: user_id}
pending_deposits = {}

def get_user_balance(user_id):
    return user_balances.get(user_id, 0.0)

def main_menu(user_id):
    balance = get_user_balance(user_id)
    btn1 = InlineKeyboardButton(text="📧 قائمة الإيميلات والمخزن", callback_data="list_emails")
    btn2 = InlineKeyboardButton(text="💳 شحن الرصيد وطرق الدفع", callback_data="payment_methods")
    btn3 = InlineKeyboardButton(text="🎁 نظام الإحالة", callback_data="referral_system")
    btn4 = InlineKeyboardButton(text="🛠 الدعم الفني", callback_data="support_info")
    return InlineKeyboardMarkup(inline_keyboard=[[btn1], [btn2], [btn3], [btn4]]), balance

def email_categories_menu():
    btn1 = InlineKeyboardButton(text="1️⃣ إيميلات قديمة (0.6$)", callback_data="cat_old")
    btn2 = InlineKeyboardButton(text="2️⃣ إيميلات جديدة (0.35$)", callback_data="cat_new")
    btn3 = InlineKeyboardButton(text="3️⃣ إيميلات (7-30 يوم) (0.6$)", callback_data="cat_medium")
    btn_back = InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")
    return InlineKeyboardMarkup(inline_keyboard=[[btn1], [btn2], [btn3], [btn_back]])

def buy_menu(category_code):
    btn_buy = InlineKeyboardButton(text="🛒 شراء الآن بالرصيد", callback_data=f"buy_{category_code}")
    btn_back = InlineKeyboardButton(text="🔙 العودة لفئات الإيميلات", callback_data="list_emails")
    return InlineKeyboardMarkup(inline_keyboard=[[btn_buy], [btn_back]])

def payment_menu():
    btn_sham = InlineKeyboardButton(text="1️⃣ شام كاش", callback_data="pay_sham")
    btn_crypto = InlineKeyboardButton(text="2️⃣ عملات رقمية (USDT)", callback_data="pay_crypto")
    btn_back = InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")
    return InlineKeyboardMarkup(inline_keyboard=[[btn_sham], [btn_crypto], [btn_back]])

def check_pay_menu():
    btn_check = InlineKeyboardButton(text="✅ أرسل إشعار التحويل لشحن الرصيد", callback_data="check_payment")
    btn_back = InlineKeyboardButton(text="🔙 العودة لطرق الدفع", callback_data="payment_methods")
    return InlineKeyboardMarkup(inline_keyboard=[[btn_check], [btn_back]])

def back_menu():
    btn = InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")
    return InlineKeyboardMarkup(inline_keyboard=[[btn]])

def admin_approval_menu(deposit_id):
    btn_approve = InlineKeyboardButton(text="✅ قبول وتأكيد الشحن", callback_data=f"adm_app_{deposit_id}")
    btn_reject = InlineKeyboardButton(text="❌ رفض الطلب", callback_data=f"adm_rej_{deposit_id}")
    return InlineKeyboardMarkup(inline_keyboard=[[btn_approve], [btn_reject]])

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    kb, bal = main_menu(message.from_user.id)
    text = (
        f"أهلاً بك في متجر الإيميلات الفوري! 📧✨\n\n"
        f"💰 **رصيدك الحالي:** `{bal:.2f}$`\n\n"
        f"اختر الخدمة التي تريدها من الأزرار أدناه:"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=kb)

@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    user_id = callback.from_user.id
    
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
            f"👇 اضغط للشراء المباشر بالرصيد:"
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=buy_menu("old"))

    elif data == "cat_new":
        count = len(EMAILS_NEW)
        text = (
            f"📌 **2️⃣ إيميلات جديدة:**\n\n"
            f"💵 **السعر:** 0.35$\n"
            f"📊 **المتوفر:** `{count}` إيميل\n"
            f"🛡 **الكفالة:** لمدة 24 ساعة من تاريخ الشراء\n\n"
            f"👇 اضغط للشراء المباشر بالرصيد:"
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
            f"👇 اضغط للشراء المباشر بالرصيد:"
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=buy_menu("medium"))

    elif data.startswith("buy_"):
        cat = data.replace("buy_", "")
        price = 0.60 if cat in ["old", "medium"] else 0.35
        bal = get_user_balance(user_id)

        if bal < price:
            await callback.answer(f"❌ رصيدك غير كافٍ ({bal:.2f}$)! يرجى شحن الرصيد أولاً.", show_alert=True)
            return

        stock = EMAILS_OLD if cat == "old" else (EMAILS_NEW if cat == "new" else EMAILS_MEDIUM)
        
        if not stock:
            await callback.answer("❌ عذراً، هذه الفئة نفدت من المخزن حالياً!", show_alert=True)
            return

        user_balances[user_id] -= price
        email_data = stock.pop(0)
        
        text = (
            f"✅ **تمت عملية الشراء بنجاح!**\n\n"
            f"💰 **المبلغ المخصوم:** `{price}$`\n"
            f"💵 **رصيدك المتبقي:** `{user_balances[user_id]:.2f}$`\n\n"
            f"📧 **بيانات الإيميل الخاص بك:**\n`{email_data}`\n\n"
            f"*اضغط على النص أعلاه لنسخه مباشرة.*"
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())

    elif data == "payment_methods":
        await state.clear()
        text = (
            f"💳 **شحن الرصيد وطرق الدفع:**\n\n"
            f"💰 **رصيدك الحالي:** `{get_user_balance(user_id):.2f}$`\n\n"
            f"اختر طريقة الدفع المناسبة لك للتحويل والتعبئة:"
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=payment_menu())

    elif data == "pay_sham":
        text = (
            "📌 **1️⃣ شام كاش**\n\n"
            "يرجى التحويل إلى العنوان التالي:\n"
            "`18a4c2941387daeaf0256639ffc705e8`\n\n"
            "✅ **العملات المقبولة:** الدولار الأمريكي (USD) والليرة السورية (SYP)\n"
            "💱 **سعر الصرف الحالي في البوت:**\n`1 USD = 141 SYP`\n\n"
            "⚠️ بعد التحويل اضغط على **أرسل إشعار التحويل لشحن الرصيد**."
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=check_pay_menu())

    elif data == "pay_crypto":
        text = (
            "📌 **2️⃣ عملات رقمية (USDT)**\n\n"
            "🔹 **USDT (BEP20):**\n`0xd22ccb682b5a8f1dbf6152882673b0130620cb11`\n\n"
            "🔹 **USDT (TRC20):**\n`TAuVtaQATX9TNyNQjKQK11pFKsx6X2hGJx`\n\n"
            "⚠️ **الحد الأدنى للإيداع:** `0.2 USDT`\n\n"
            "⚠️ أرسل العملية ثم اضغط على زر **أرسل إشعار التحويل لشحن الرصيد**."
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=check_pay_menu())

    elif data == "check_payment":
        await state.set_state(DepositState.waiting_for_proof)
        text = "📩 **يرجى كتابة قيمة المبلغ والرقم الإشعاري (أو إرسال صورة إشعار التحويل) الآن:**"
        await callback.message.edit_text(text, parse_mode="Markdown")

    elif data.startswith("adm_app_"):
        dep_id = data.replace("adm_app_", "")
        client_id = pending_deposits.get(dep_id)
        
        if client_id:
            # إضافة قيمة افتراضية للشحن (مثلاً 0.60$ ثمن إيميل) أو يمكنك تعديل الرصيد
            add_amount = 0.60 
            user_balances[client_id] = get_user_balance(client_id) + add_amount
            try:
                await bot.send_message(
                    chat_id=client_id,
                    text=(
                        f"🎉 **تم تأكيد الإيداع وإضافة الرصيد بنجاح!**\n\n"
                        f"➕ **المبلغ المضاف:** `{add_amount:.2f}$`\n"
                        f"💰 **رصيدك الحالي:** `{user_balances[client_id]:.2f}$`\n\n"
                        f"يمكنك الآن التوجه لمخزن الإيميلات للشراء مباشرة! 🛒"
                    ),
                    parse_mode="Markdown"
                )
            except Exception as e:
                logging.error(f"Failed to send notify: {e}")
            await callback.message.edit_text(f"{callback.message.text}\n\n✅ **تم قبول الطلب وإضافة الرصيد للزبون!**", parse_mode="Markdown")

    elif data.startswith("adm_rej_"):
        dep_id = data.replace("adm_rej_", "")
        client_id = pending_deposits.get(dep_id)
        if client_id:
            try:
                await bot.send_message(
                    chat_id=client_id,
                    text="❌ **عذراً، تعذر التحقق من عملية الدفع الخاصة بك.**\nيرجى التواصل مع الدعم الفني."
                )
            except Exception as e:
                logging.error(f"Failed to notify: {e}")
        await callback.message.edit_text(f"{callback.message.text}\n\n❌ **تم رفض طلب الشحن.**", parse_mode="Markdown")

    elif data == "referral_system":
        bot_info = await bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        text = (
            f"🎁 **برنامج الإحالة والمكافآت:**\n\n"
            f"احصل على **إيميل قديم مجاناً (0.60$)** عند دعوة 5 من أصدقائك!\n\n"
            f"🔗 **رابط الدعوة الخاص بك:**\n`{ref_link}`"
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    elif data == "support_info":
        text = f"🛠 **الدعم الفني:**\nللتواصل والشحن أرسل للمالك مباشرة: {ADMIN_USERNAME}"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_menu())
        
    elif data == "back_to_main":
        await state.clear()
        kb, bal = main_menu(user_id)
        text = (
            f"القائمة الرئيسية للمتجر 📧:\n\n"
            f"💰 **رصيدك الحالي:** `{bal:.2f}$`"
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
        
    await callback.answer()

@dp.message(DepositState.waiting_for_proof)
async def process_proof(message: types.Message, state: FSMContext):
    await state.clear()
    
    user_id = message.from_user.id
    dep_id = str(user_id)
    pending_deposits[dep_id] = user_id

    user_text = (
        "⏳ **تم استلام بيانات التحويل بنجاح!**\n\n"
        "جاري التحقق من التحويل وتعبئة الرصيد..\n"
        "⏱ **سيتم إشعارك فور تعبئة الرصيد.**\n\n"
        "شكراً لانتظارك! 🌹"
    )
    await message.answer(user_text, parse_mode="Markdown", reply_markup=back_menu())
    
    try:
        admin_text = (
            f"📥 **طلب شحن رصيد جديد!**\n\n"
            f"👤 **الزبون:** {message.from_user.full_name} (@{message.from_user.username})\n"
            f"🆔 **ID الزبون:** `{user_id}`\n\n"
            f"📝 **بيانات العملية:**\n{message.text if message.text else 'أرسل صورة إشعار'}"
        )
        if message.photo:
            await bot.send_photo(
                chat_id=ADMIN_ID,
                photo=message.photo[-1].file_id,
                caption=admin_text,
                parse_mode="Markdown",
                reply_markup=admin_approval_menu(dep_id)
            )
        else:
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_text,
                parse_mode="Markdown",
                reply_markup=admin_approval_menu(dep_id)
            )
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
    print("🚀 البوت يعمل مع خادم الاستجابة ونظام الرصيد...")
    await bot.delete_webhook(drop_pending_updates=True)
    await start_web_server()
    await dp.start_polling(bot, handle_signals=False)

if __name__ == '__main__':
    asyncio.run(main())

