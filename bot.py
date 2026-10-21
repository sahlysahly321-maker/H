import asyncio
import logging
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
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

# إعداد Google Sheets
SPREADSHEET_ID = "1ZKVQTAMGb70ptWjj5eE9QsHg2Fyn-P2UeSiyUKi5Wdc"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

def get_sheet_connection():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # استخدام المتغيرات البيئية أو الاتصال المباشر
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        if creds_json:
            creds_dict = json.loads(creds_json)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            return client.open_by_key(SPREADSHEET_ID).worksheet("Users")
    except Exception as e:
        logging.error(f"Sheet connection error: {e}")
    return None

def get_user_balance(user_id):
    # جلب الرصيد من الذاكرة السحابية المؤقتة لتسريع البوت، ويمكن ربطه لاحقاً بالشيت مباشرة
    return user_balances_cache.get(user_id, 0.0)

user_balances_cache = {}

def update_user_balance(user_id, amount):
    current = user_balances_cache.get(user_id, 0.0)
    new_bal = round(current + amount, 2)
    user_balances_cache[user_id] = new_bal
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
    "goldendome63@gmail.com:orange2006#",
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
    if user_id not in user_balances_cache:
        user_balances_cache[user_id] = 0.0

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
            details = f"📌 **إيميلات قديمة**\n💵 **السعر لكل منتج:** `0.60 USDT`\n📊 **الكمية المتاحة:** `{count}`\n🛡 **الكفالة:** مدة يومين"
        elif data == "cat_new":
            count = len(EMAILS_NEW)
            details = f"📌 **إيميلات جديدة**\n💵 **السعر لكل منتج:** `0.35 USDT`\n📊 **الكمية المتاحة:** `{count}`\n🛡 **الكفالة:** 24 ساعة"
        else:
            count = len(EMAILS_MEDIUM)
            details = f"📌 **إيميلات (7-30 يوم)**\n💵 **السعر لكل منتج:** `0.60 USDT`\n📊 **الكمية المتاحة:** `{count}`\n🛡 **الكفالة:** يومين"
        
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
        await callback.message.edit_text(f"📥 **يرجى إدخال الكمية المطلوبة (من 1 إلى {max_count}):**", parse_mode="Markdown", reply_markup=kb)

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
        await callback.message.edit_text("📌 **شام كاش:**\nالعنوان: `18a4c2941387daeaf0256639ffc705e8`\n\nاضغط أدناه لإرسال رقم العملية فقط.", parse_mode="Markdown", reply_markup=kb)

    elif data == "pay_crypto":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ إرسال رقم العملية", callback_data="check_payment")],
            [InlineKeyboardButton(text="🔙 العودة", callback_data="payment_methods")]
        ])
        await callback.message.edit_text("📌 **USDT:**\nBEP20: `0xd22ccb682b5a8f1dbf6152882673b0130620cb11`\n\nاضغط أدناه لإرسال رقم العملية فقط.", parse_mode="Markdown", reply_markup=kb)

    elif data == "check_payment":
        await state.set_state(DepositState.waiting_for_proof)
        await callback.message.edit_text("📩 **يرجى إرسال رقم العملية فقط:**", parse_mode="Markdown")

    elif data.startswith("adm_app_"):
        client_id = int(data.replace("adm_app_", ""))
        admin_action_target[ADMIN_ID] = client_id
        await callback.message.answer("✍️ **أرسل الآن المبلغ بالدولار لإضافته لرصيد الزبون:**", parse_mode="Markdown")

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
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]])
        await callback.message.edit_text(f"🎁 **نظام الإحالة:**\nرابطك:\n`{ref_link}`", parse_mode="Markdown", reply_markup=kb)

    elif data == "support_info":
        await state.clear()
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]])
        await callback.message.edit_text(f"🛠 **الدعم الفني:** {ADMIN_USERNAME}", parse_mode="Markdown", reply_markup=kb)

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

    stock = EMAILS_OLD if cat == "cat_old" else (EMAILS_NEW if cat == "cat_new" else EMAILS_MEDIUM)
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
    purchased_emails = [stock.pop(0) for _ in range(qty)]
    emails_str = "\n`.`\n".join(purchased_emails)

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]])
    await message.answer(f"✅ **تمت عملية الشراء بنجاح!**\n\n📦 الكمية: {qty}\n💰 المتبقي: `{new_bal:.2f}$`\n\n📧 الإيميلات:\n`{emails_str}`", parse_mode="Markdown", reply_markup=kb)
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



