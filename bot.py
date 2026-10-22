import asyncio
import logging
import os
import urllib.request
import csv
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = '8735041657:AAHILJgf72t9IzJswxlIUeJK2rsRbhsCNXs'
ADMIN_ID = 7927059374
ADMIN_USERNAME = "@Alaaa057"

SPREADSHEET_ID = "1ZKVQTAMGb70ptWjj5eE9QsHg2Fyn-P2UeSiyUKi5Wdc"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

user_balances = {}
user_purchases = {}
user_referrals = {}
sold_emails_set = set()

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

def fetch_emails_from_sheet(col_index):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Emails"
        web_page = urllib.request.urlopen(url)
        lines = [line.decode('utf-8') for line in web_page.readlines()]
        reader = csv.reader(lines)
        
        emails_list = []
        for row in reader:
            if len(row) > col_index and row[col_index].strip():
                val = row[col_index].strip().strip('"')
                if "@" in val and val not in sold_emails_set:
                    emails_list.append(val)
        return emails_list
    except Exception as e:
        logging.error(f"Error fetching emails: {e}")
        return []

def get_stock(cat):
    if cat == "cat_old":
        return fetch_emails_from_sheet(0)
    elif cat == "cat_new":
        return fetch_emails_from_sheet(1)
    elif cat == "cat_medium":
        return fetch_emails_from_sheet(2)
    return []

def main_menu(user_id):
    bal = get_user_balance(user_id)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 قائمة الإيميلات والمخزن", callback_data="list_emails")],
        [InlineKeyboardButton(text="💳 شحن الرصيد وطرق الدفع", callback_data="payment_methods")],
        [InlineKeyboardButton(text="🎁 نظام الإحالة والمكافآت", callback_data="referral_system")],
        [InlineKeyboardButton(text="🛠 الدعم الفني", callback_data="support_info")]
    ]), bal

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 0.0

    args = message.text.split()
    if len(args) > 1:
        try:
            referrer_id = int(args[1])
            if referrer_id != user_id and referrer_id not in user_referrals.get(user_id, []):
                user_referrals.setdefault(referrer_id, []).append(user_id)
        except ValueError:
            pass

    kb, bal = main_menu(user_id)
    await message.answer(f"أهلاً بك في متجر الإيميلات الفوري! 📧✨\n\n💰 **رصيدك الحالي:** `{bal:.2f}$`\n\nاختر الخدمة من الأزرار أدناه:", parse_mode="Markdown", reply_markup=kb)

@dp.message(Command("bc"))
async def broadcast_message(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    text_to_send = message.text.replace("/bc", "").strip()
    if not text_to_send:
        await message.answer("⚠️ يرجى كتابة النص بعد الأمر.")
        return
    all_users = list(user_balances.keys())
    for u_id in all_users:
        try:
            await bot.send_message(chat_id=u_id, text=f"📢 **إعلان من الإدارة:**\n\n{text_to_send}", parse_mode="Markdown")
            await asyncio.sleep(0.05)
        except:
            pass
    await message.answer("✅ تم الإرسال بنجاح.")

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
        stock = get_stock(data)
        count = len(stock)
        
        if data == "cat_old":
            details = (
                f"📌 **إيميلات قديمة**\n"
                f"💵 **السعر لكل منتج:** `0.60$`\n"
                f"📊 **الكمية المتاحة:** `{count}`\n"
                f"🗓 **تاريخ الإنشاء:** من نصف سنة حتى 5 سنين\n"
                f"🛡 **الكفالة:** يومين من تاريخ الشراء\n"
                f"⚠️ **تنبيه:** يجب إدخالهم أول مرة بإنترنت سوري، وفي حال طلب الإيميل تحقق يرجى التواصل مع الدعم."
            )
        elif data == "cat_new":
            details = (
                f"📌 **إيميلات جديدة**\n"
                f"💵 **السعر لكل منتج:** `0.35$`\n"
                f"📊 **الكمية المتاحة:** `{count}`\n"
                f"🛡 **الكفالة:** 24 ساعة من تاريخ الشراء"
            )
        else:
            details = (
                f"📌 **إيميلات (7-30 يوم)**\n"
                f"💵 **السعر لكل منتج:** `0.60$`\n"
                f"📊 **الكمية المتاحة:** `{count}`\n"
                f"🗓 **تاريخ الإنشاء:** من (7 - 30 أيام)\n"
                f"🛡 **الكفالة:** يومين من تاريخ الشراء"
            )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 شراء إيميلات", callback_data=f"buy_req_{data}")],
            [InlineKeyboardButton(text="🔙 العودة", callback_data="list_emails")]
        ])
        await callback.message.edit_text(f"{details}\n\nاضغط على **شراء إيميلات** لتحديد الكمية:", parse_mode="Markdown", reply_markup=kb)

    elif data.startswith("buy_req_"):
        cat = data.replace("buy_req_", "")
        stock = get_stock(cat)
        max_count = len(stock)
        
        if max_count == 0:
            await callback.answer("❌ عذراً، هذه الفئة نفدت من المخزن حالياً!", show_alert=True)
            return

        await state.update_data(selected_cat=cat)
        await state.set_state(BuyState.waiting_for_quantity)
        
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 إلغاء", callback_data="list_emails")]])
        await callback.message.edit_text(
            f"📥 **يرجى إدخال الكمية المطلوبة:**\nاكتب رقماً من `1` إلى `{max_count}` (العدد المتوفر):",
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
            [InlineKeyboardButton(text="✅ إرسال رقم العملية", callback_data="check_payment")],
            [InlineKeyboardButton(text="🔙 العودة", callback_data="payment_methods")]
        ])
        await callback.message.edit_text(
            "📌 **1️⃣ شام كاش**\n\n"
            "العنوان:\n`18a4c2941387daeaf0256639ffc705e8`\n\n"
            "💵 **سعر الصرف المعتمد:** يتم الاعتماد حصراً على سعر الصرف الرسمي المحدث وقت التحويل.\n\n"
            "⚠️ بعد التحويل اضغط على الزر أدناه وأرسل **رقم العملية** فقط.",
            parse_mode="Markdown",
            reply_markup=kb
        )

    elif data == "pay_crypto":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ إرسال رقم العملية", callback_data="check_payment")],
            [InlineKeyboardButton(text="🔙 العودة", callback_data="payment_methods")]
        ])
        await callback.message.edit_text(
            "📌 **2️⃣ عملات رقمية (USDT)**\n\n"
            "🔹 **BEP20:**\n`0xd22ccb682b5a8f1dbf6152882673b0130620cb11`\n\n"
            "🔹 **TRC20:**\n`TAuVtaQATX9TNyNQjKQK11pFKsx6X2hGJx`\n\n"
            "⚠️ بعد التحويل اضغط أدناه وأرسل **رقم العملية (TxID)** فقط.",
            parse_mode="Markdown",
            reply_markup=kb
        )

    elif data == "check_payment":
        await state.set_state(DepositState.waiting_for_proof)
        await callback.message.edit_text("📩 **يرجى إرسال رقم العملية فقط:**", parse_mode="Markdown")

    elif data.startswith("adm_app_"):
        client_id = int(data.replace("adm_app_", ""))
        admin_action_target[ADMIN_ID] = client_id
        await callback.message.answer("✍️ **أرسل المبلغ بالدولار لإضافته للزبون:**", parse_mode="Markdown")

    elif data.startswith("adm_rej_"):
        client_id = int(data.replace("adm_rej_", ""))
        try:
            await bot.send_message(chat_id=client_id, text="❌ **تم رفض طلب الشحن من قبل الإدارة.**", parse_mode="Markdown")
        except:
            pass
        await callback.message.edit_text(f"{callback.message.text}\n\n❌ **تم رفض الطلب.**", parse_mode="Markdown")

    elif data == "referral_system":
        await state.clear()
        bot_info = await bot.get_me()
        referred_users = user_referrals.get(user_id, [])
        completed_refs = sum(1 for ref_id in referred_users if user_purchases.get(ref_id, 0) > 0)
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
        await callback.message.edit_text(f"القائمة الرئيسية 📧:\n\n💰 **رصيدك الحالي:** `{bal:.2f}$`", parse_mode="Markdown", reply_markup=kb)
        
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

    stock = get_stock(cat)
    price = 0.35 if cat == "cat_new" else 0.60
    max_count = len(stock)

    if not message.text.isdigit():
        await message.answer(f"❌ يرجى كتابة رقم صحيح (من 1 إلى {max_count}):")
        return

    qty = int(message.text.strip())
    if qty <= 0 or qty > max_count:
        await message.answer(f"❌ الكمية غير صالحة. المتوفر: {max_count}")
        return

    total_cost = round(qty * price, 2)
    bal = get_user_balance(user_id)

    if bal < total_cost:
        await message.answer(f"❌ رصيدك غير كافٍ! (متوفر: {bal:.2f}$، المطلوب: {total_cost:.2f}$)")
        await state.clear()
        return

    new_bal = update_user_balance(user_id, -total_cost)
    
    purchased_emails = []
    for i in range(qty):
        email_item = stock[i]
        purchased_emails.append(email_item)
        sold_emails_set.add(email_item)

    user_purchases[user_id] = user_purchases.get(user_id, 0) + qty

    emails_str = "\n".join(purchased_emails)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]])
    await message.answer(
        f"✅ **تمت عملية الشراء بنجاح!**\n\n"
        f"📦 **الكمية:** {qty}\n"
        f"💰 **الرصيد المتبقي:** `{new_bal:.2f}$`\n\n"
        f"📧 **الإيميلات الخاصة بك:**\n`{emails_str}`",
        parse_mode="Markdown",
        reply_markup=kb
    )
    
    cat_name = "إيميلات قديمة" if cat == "cat_old" else ("إيميلات جديدة" if cat == "cat_new" else "إيميلات (7-30 يوم)")
    admin_notification = (
        f"🛒 **عملية شراء جديدة تمت!**\n\n"
        f"👤 **الزبون:** {message.from_user.full_name} (`{user_id}`)\n"
        f"📂 **الفئة:** {cat_name}\n"
        f"📦 **الكمية:** {qty}\n\n"
        f"📧 **الإيميلات المباعة (يرجى حذفها من الشيت):**\n`{emails_str}`"
    )
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_notification, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Failed to send admin notification: {e}")

    await state.clear()

@dp.message(DepositState.waiting_for_proof)
async def process_proof(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    text_content = (message.text or message.caption or "").strip()
    pending_operations[user_id] = text_content

    kb_back = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]])
    await message.answer("⏳ **تم استلام رقم العملية، جاري المراجعة...**", parse_mode="Markdown", reply_markup=kb_back)
    
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ قبول وتحديد المبلغ", callback_data=f"adm_app_{user_id}")],
        [InlineKeyboardButton(text="❌ رفض الطلب", callback_data=f"adm_rej_{user_id}")]
    ])
    
    await bot.send_message(chat_id=ADMIN_ID, text=f"📥 **طلب شحن جديد!**\n👤 من: {message.from_user.full_name}\n🆔 ID: `{user_id}`\n📝 العملية: `{text_content}`", parse_mode="Markdown", reply_markup=admin_kb)

@dp.message(lambda message: message.from_user.id == ADMIN_ID and ADMIN_ID in admin_action_target)
async def process_admin_amount_input(message: types.Message):
    client_id = admin_action_target.pop(ADMIN_ID, None)
    if not client_id:
        return

    try:
        amount_to_add = float(message.text.strip())
    except ValueError:
        await message.answer("❌ يرجى إرسال رقم صحيح للمبلغ:")
        admin_action_target[ADMIN_ID] = client_id
        return

    new_bal = update_user_balance(client_id, amount_to_add)
    try:
        await bot.send_message(chat_id=client_id, text=f"🎉 **تم قبول الإيداع وإضافة الرصيد!**\n➕ المضاف: `{amount_to_add:.2f}$`\n💰 رصيدك: `{new_bal:.2f}$`", parse_mode="Markdown")
    except:
        pass

    await message.answer(f"✅ تمت إضافة `{amount_to_add:.2f}$` للزبون بنجاح.")

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










