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

# معرف ملف Google Sheets السحابي الخاص بك
SPREADSHEET_ID = "1ZKVQTAMGb70ptWjj5eE9QsHg2Fyn-P2UeSiyUKi5Wdc"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ذاكرة تخزين الأرصدة والمشتريات
user_balances = {}
user_purchases = {}

def get_user_balance(user_id):
    return user_balances.get(user_id, 0.0)

def update_user_balance(user_id, amount):
    current = get_user_balance(user_id)
    new_bal = round(current + amount, 2)
    user_balances[user_id] = new_bal
    return new_bal

class DepositState(StatesGroup):
    waiting_for_proof = State()

class BuyState(StatesGroup):
    waiting_for_quantity = State()

pending_operations = {}
admin_action_target = {}

EMAILS_OLD = [
    "mk2915564@gmail.com:orange2006#",
    "millmaize@gmail.com:orange2006#",
    "goldendome63@gmail.com:orange2006#"
]

EMAILS_NEW = [
    "hoiphonop7@gmail.com:orange2006#",
    "arsenyefim01@gmail.com:orange2006#",
    "enginaltan276@gmail.com:orange2006#"
]

EMAILS_MEDIUM = [
    "fathserifalkadi@gmail.com:orange2006#",
    "kiza46809@gmail.com:orange2006#",
    "salehmardani355@gmail.com:orange2006#"
]

def main_menu(user_id):
    bal = get_user_balance(user_id)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 قائمة الإيميلات والمخزن", callback_data="list_emails")],
        [InlineKeyboardButton(text="💳 شحن الرصيد وطرق الدفع", callback_data="payment_methods")],
        [InlineKeyboardButton(text="🎁 نظام الإحالة", callback_data="referral_system")],
        [InlineKeyboardButton(text="🛠 الدعم الفني", callback_data="support_info")]
    ]), bal

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 0.0

    kb, bal = main_menu(user_id)
    await message.answer(f"أهلاً بك في متجر الإيميلات الفوري! 📧✨\n\n💰 **رصيدك الحالي:** `{bal:.2f}$`\n\nاختر الخدمة من الأزرار أدناه:", parse_mode="Markdown", reply_markup=kb)

@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "list_emails":
        await state.clear()
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1️⃣ إيميلات قديمة (0.6$)", callback_data="cat_old")],
            [InlineKeyboardButton(text="2️⃣ إيميلات جديدة (0.35$)", callback_data="cat_new")],
            [InlineKeyboardButton(text="3️⃣ إيميلات (7-30 يوم) (0.6$)", callback_data="cat_medium")],
            [InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]
        ])
        await callback.message.edit_text("📦 **اختر فئة الإيميلات المطلوبة:**", parse_mode="Markdown", reply_markup=kb)
        
    elif data in ["cat_old", "cat_new", "cat_medium"]:
        await state.clear()
        if data == "cat_old":
            count = len(EMAILS_OLD)
            details = (
                f"📌 **إيميلات قديمة**\n"
                f"💵 **السعر لكل منتج:** `0.60 USDT`\n"
                f"📊 **الكمية المتاحة:** `{count}`\n"
                f"🗓 **تاريخ الإنشاء:** من نصف سنة حتى 5 سنين\n"
                f"🛡 **الكفالة:** مدة يومين من تاريخ الشراء\n"
                f"⚠️ **تنبيه:** يجب إدخالهم أول مرة بإنترنت سوري، وفي حال طلب الإيميل تحقق يرجى التواصل مع الدعم لإكمالها فوراً."
            )
        elif data == "cat_new":
            count = len(EMAILS_NEW)
            details = (
                f"📌 **إيميلات جديدة**\n"
                f"💵 **السعر لكل منتج:** `0.35 USDT`\n"
                f"📊 **الكمية المتاحة:** `{count}`\n"
                f"🛡 **الكفالة:** 24 ساعة من تاريخ الشراء"
            )
        else:
            count = len(EMAILS_MEDIUM)
            details = (
                f"📌 **إيميلات (7-30 يوم)**\n"
                f"💵 **السعر لكل منتج:** `0.60 USDT`\n"
                f"📊 **الكمية المتاحة:** `{count}`\n"
                f"🗓 **تاريخ الإنشاء:** من (7 - 30 أيام)\n"
                f"🛡 **الكفالة:** يومين من تاريخ الشراء"
            )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 شراء إيميلات", callback_data=f"buy_req_{data}")],
            [InlineKeyboardButton(text="🔙 العودة لفئات الإيميلات", callback_data="list_emails")]
        ])
        await callback.message.edit_text(f"{details}\n\nاضغط على **شراء إيميلات** لتحديد الكمية:", parse_mode="Markdown", reply_markup=kb)

    elif data.startswith("buy_req_"):
        cat = data.replace("buy_req_", "")
        stock = EMAILS_OLD if cat == "cat_old" else (EMAILS_NEW if cat == "cat_new" else EMAILS_MEDIUM)
        max_count = len(stock)
        
        if max_count == 0:
            await callback.answer("❌ عذراً، هذه الفئة نفدت من المخزن حالياً!", show_alert=True)
            return

        await state.update_data(selected_cat=cat)
        await state.set_state(BuyState.waiting_for_quantity)
        
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 إلغاء والعودة", callback_data="list_emails")]])
        await callback.message.edit_text(
            f"📥 **يرجى إدخال الكمية المطلوبة:**\n"
            f"اكتب رقماً من `1` إلى `{max_count}` (العدد المتوفر حالياً بالمتجر):",
            parse_mode="Markdown",
            reply_markup=kb
        )

    elif data == "payment_methods":
        await state.clear()
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1️⃣ شام كاش", callback_data="pay_sham")],
            [InlineKeyboardButton(text="2️⃣ عملات رقمية (USDT)", callback_data="pay_crypto")],
            [InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]
        ])
        await callback.message.edit_text(f"💳 **شحن الرصيد وطرق الدفع:**\n\n💰 **رصيدك الحالي:** `{get_user_balance(user_id):.2f}$`", parse_mode="Markdown", reply_markup=kb)

    elif data == "pay_sham":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ إرسال رقم عملية شام كاش", callback_data="check_payment")],
            [InlineKeyboardButton(text="🔙 العودة لطرق الدفع", callback_data="payment_methods")]
        ])
        await callback.message.edit_text(
            "📌 **1️⃣ شام كاش**\n\n"
            "يرجى التحويل إلى العنوان التالي:\n"
            "`18a4c2941387daeaf0256639ffc705e8`\n\n"
            "⚠️ بعد التحويل اضغط على الزر أدناه وأرسل **رقم العملية** فقط بدون صور أو مبالغ.",
            parse_mode="Markdown",
            reply_markup=kb
        )

    elif data == "pay_crypto":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ إرسال رقم عملية USDT", callback_data="check_payment")],
            [InlineKeyboardButton(text="🔙 العودة لطرق الدفع", callback_data="payment_methods")]
        ])
        await callback.message.edit_text(
            "📌 **2️⃣ عملات رقمية (USDT)**\n\n"
            "🔹 **USDT (BEP20):**\n`0xd22ccb682b5a8f1dbf6152882673b0130620cb11`\n\n"
            "🔹 **USDT (TRC20):**\n`TAuVtaQATX9TNyNQjKQK11pFKsx6X2hGJx`\n\n"
            "⚠️ أرسل العملية ثم اضغط على الزر أدناه وأرسل **رقم العملية (TxID)** فقط بدون صور أو مبالغ.",
            parse_mode="Markdown",
            reply_markup=kb
        )

    elif data == "check_payment":
        await state.set_state(DepositState.waiting_for_proof)
        await callback.message.edit_text("📩 **يرجى إرسال رقم العملية فقط (بدون أي مبلغ أو صور):**", parse_mode="Markdown")

    elif data.startswith("adm_app_"):
        client_id = int(data.replace("adm_app_", ""))
        admin_action_target[ADMIN_ID] = client_id
        await callback.message.answer("✍️ **أرسل الآن المبلغ بالدولار (مثال: 0.65) في رسالة جديدة لإضافته لرصيد الزبون:**", parse_mode="Markdown")

    elif data.startswith("adm_rej_"):
        client_id = int(data.replace("adm_rej_", ""))
        try:
            await bot.send_message(chat_id=client_id, text="❌ **عذراً، تم رفض طلب الشحن من قبل الإدارة.**", parse_mode="Markdown")
        except:
            pass
        await callback.message.edit_text(f"{callback.message.text}\n\n❌ **تم رفض الطلب.**", parse_mode="Markdown")

    elif data == "referral_system":
        await state.clear()
        bot_info = await bot.get_me()
        completed_refs = 0
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]])
        await callback.message.edit_text(
            f"🎁 **برنامج الإحالة والمكافآت:**\n\n"
            f"دعوة أصدقائك تمنحك إيميل قديم مجاناً (0.60$) عندما يقوم **5 من أصدقائك المدعوين** بإتمام **عملية شراء واحدة** على الأقل!\n\n"
            f"📊 **تقدمك الحالي:** `{completed_refs} / 5` أصدقاء أتموا الشراء.\n\n"
            f"🔗 **رابط الدعوة الخاص بك:**\n`{ref_link}`",
            parse_mode="Markdown",
            reply_markup=kb
        )

    elif data == "support_info":
        await state.clear()
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]])
        await callback.message.edit_text(f"🛠 **الدعم الفني:**\nتواصل مع المالك: {ADMIN_USERNAME}", parse_mode="Markdown", reply_markup=kb)

    elif data == "back_to_main":
        await state.clear()
        kb, bal = main_menu(user_id)
        await callback.message.edit_text(f"القائمة الرئيسية للمتجر 📧:\n\n💰 **رصيدك الحالي:** `{bal:.2f}$`", parse_mode="Markdown", reply_markup=kb)
        
    await callback.answer()

@dp.message(BuyState.waiting_for_quantity)
async def process_buy_quantity(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    cat = user_data.get("selected_cat")
    
    if not cat:
        await state.clear()
        await message.answer("❌ حدث خطأ، يرجى المحاولة من جديد.")
        return

    stock = EMAILS_OLD if cat == "cat_old" else (EMAILS_NEW if cat == "cat_new" else EMAILS_MEDIUM)
    price = 0.35 if cat == "cat_new" else 0.60
    max_count = len(stock)

    if not message.text.isdigit():
        await message.answer(f"❌ يرجى كتابة رقم صحيح للكمية (مثال: `1` إلى `{max_count}`):", parse_mode="Markdown")
        return

    qty = int(message.text.strip())

    if qty <= 0:
        await message.answer("❌ يجب إدخال كمية تساوي 1 أو أكثر.")
        return

    if qty > max_count:
        await message.answer(f"❌ الكمية المطلوبة ({qty}) أكبر من المتوفر حالياً في المخزن ({max_count}). يرجى كتابة كمية أقل.")
        return

    total_cost = round(qty * price, 2)
    bal = get_user_balance(user_id)

    if bal < total_cost:
        await message.answer(
            f"❌ **رصيدك غير كافٍ!**\n\n"
            f"💰 تكلفة الشراء لـ `{qty}` إيميل: `{total_cost:.2f}$`\n"
            f"💵 رصيدك الحالي: `{bal:.2f}$`\n\n"
            f"يرجى شحن حسابك أولاً.",
            parse_mode="Markdown"
        )
        await state.clear()
        return

    new_bal = update_user_balance(user_id, -total_cost)
    
    purchased_emails = []
    for _ in range(qty):
        purchased_emails.append(stock.pop(0))

    user_purchases[user_id] = user_purchases.get(user_id, 0) + qty

    emails_str = "\n`.`\n".join(purchased_emails)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]])
    
    await message.answer(
        f"✅ **تمت عملية الشراء بنجاح!**\n\n"
        f"📦 **الكمية:** `{qty}` إيميل\n"
        f"💰 **المبلغ المخصوم:** `{total_cost:.2f}$`\n"
        f"💵 **الرصيد المتبقي:** `{new_bal:.2f}$`\n\n"
        f"📧 **الإيميلات الخاصة بك:**\n`{emails_str}`",
        parse_mode="Markdown",
        reply_markup=kb
    )
    await state.clear()

@dp.message(DepositState.waiting_for_proof)
async def process_proof(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    text_content = (message.text or message.caption or "").strip()
    
    pending_operations[user_id] = text_content

    kb_back = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]])
    await message.answer("⏳ **تم استلام رقم العملية بنجاح!**\nجاري مراجعته من قبل الإدارة...", parse_mode="Markdown", reply_markup=kb_back)
    
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ قبول وتحديد المبلغ", callback_data=f"adm_app_{user_id}")],
        [InlineKeyboardButton(text="❌ رفض الطلب", callback_data=f"adm_rej_{user_id}")]
    ])
    
    admin_text = (
        f"📥 **طلب شحن جديد!**\n"
        f"👤 الزبون: {message.from_user.full_name}\n"
        f"🆔 ID: `{user_id}`\n"
        f"📝 رقم العملية المرسل: `{text_content}`"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown", reply_markup=admin_kb)
    except Exception as e:
        logging.error(f"Admin error: {e}")

@dp.message(lambda message: message.from_user.id == ADMIN_ID and ADMIN_ID in admin_action_target)
async def process_admin_amount_input(message: types.Message):
    client_id = admin_action_target.pop(ADMIN_ID, None)
    if not client_id:
        return

    try:
        amount_to_add = float(message.text.strip())
    except ValueError:
        await message.answer("❌ يرجى إرسال رقم صحيح للمبلغ (مثال: `0.65`)")
        admin_action_target[ADMIN_ID] = client_id
        return

    new_bal = update_user_balance(client_id, amount_to_add)
    
    try:
        await bot.send_message(
            chat_id=client_id, 
            text=f"🎉 **تم قبول الإيداع وإضافة الرصيد بنجاح!**\n➕ المبلغ المضاف: `{amount_to_add:.2f}$`\n💰 رصيدك الحالي: `{new_bal:.2f}$`", 
            parse_mode="Markdown"
        )
    except:
        pass

    op_num = pending_operations.get(client_id, "غير متوفر")
    await message.answer(f"✅ **تمت العملية بنجاح!**\nتمت إضافة `{amount_to_add:.2f}$` للزبون (رقم العملية: `{op_num}`).", parse_mode="Markdown")

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await start_web_server()
    await dp.start_polling(bot, handle_signals=False)

if __name__ == '__main__':
    asyncio.run(main())

