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

user_balances = {}
pending_deposits = {}

EMAILS_OLD = [
    "mk2915564@gmail.com:orange2006#",
    "millmaize@gmail.com:orange2006#",
    "goldendome63@gmail.com:orange2006#"
]

EMAILS_NEW = [
    "new_user1_2026@gmail.com:Pass1234",
    "new_user2_2026@gmail.com:Pass5678"
]

EMAILS_MEDIUM = [
    "med_user1_2026@gmail.com:Pass1234",
    "med_user2_2026@gmail.com:Pass5678"
]

def get_user_balance(user_id):
    return user_balances.get(user_id, 0.0)

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
    kb, bal = main_menu(message.from_user.id)
    await message.answer(f"أهلاً بك في متجر الإيميلات الفوري! 📧✨\n\n💰 **رصيدك الحالي:** `{bal:.2f}$`\n\nاختر الخدمة من الأزرار أدناه:", parse_mode="Markdown", reply_markup=kb)

@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "list_emails":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1️⃣ إيميلات قديمة (0.6$)", callback_data="cat_old")],
            [InlineKeyboardButton(text="2️⃣ إيميلات جديدة (0.35$)", callback_data="cat_new")],
            [InlineKeyboardButton(text="3️⃣ إيميلات (7-30 يوم) (0.6$)", callback_data="cat_medium")],
            [InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]
        ])
        await callback.message.edit_text("📦 **اختر فئة الإيميلات المطلوبة:**", parse_mode="Markdown", reply_markup=kb)
        
    elif data in ["cat_old", "cat_new", "cat_medium"]:
        cat_name = "إيميلات قديمة" if data == "cat_old" else ("إيميلات جديدة" if data == "cat_new" else "إيميلات متوسطة")
        price = 0.35 if data == "cat_new" else 0.60
        count = len(EMAILS_OLD) if data == "cat_old" else (len(EMAILS_NEW) if data == "cat_new" else len(EMAILS_MEDIUM))
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 شراء الآن بالرصيد", callback_data=f"buy_{data}")],
            [InlineKeyboardButton(text="🔙 العودة لفئات الإيميلات", callback_data="list_emails")]
        ])
        await callback.message.edit_text(f"📌 **{cat_name}**\n💵 **السعر:** {price}$\n📊 **المتوفر:** `{count}` إيميل\n\nاضغط للشراء المباشر:", parse_mode="Markdown", reply_markup=kb)

    elif data.startswith("buy_"):
        cat = data.replace("buy_cat_", "")
        price = 0.35 if cat == "new" else 0.60
        bal = get_user_balance(user_id)
        
        if bal < price:
            await callback.answer(f"❌ رصيدك غير كافٍ ({bal:.2f}$)! يرجى شحن الرصيد.", show_alert=True)
            return
            
        stock = EMAILS_OLD if cat == "old" else (EMAILS_NEW if cat == "new" else EMAILS_MEDIUM)
        if not stock:
            await callback.answer("❌ عذراً، هذه الفئة نفدت من المخزن!", show_alert=True)
            return
            
        user_balances[user_id] -= price
        email_data = stock.pop(0)
        
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]])
        await callback.message.edit_text(f"✅ **تمت عملية الشراء بنجاح!**\n\n💰 **المخصوم:** `{price}$`\n💵 **المتبقي:** `{user_balances[user_id]:.2f}$`\n\n📧 **الإيميل الخاص بك:**\n`{email_data}`", parse_mode="Markdown", reply_markup=kb)

    elif data == "payment_methods":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1️⃣ شام كاش", callback_data="pay_sham")],
            [InlineKeyboardButton(text="2️⃣ عملات رقمية (USDT)", callback_data="pay_crypto")],
            [InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]
        ])
        await callback.message.edit_text(f"💳 **شحن الرصيد وطرق الدفع:**\n\n💰 **رصيدك الحالي:** `{get_user_balance(user_id):.2f}$`", parse_mode="Markdown", reply_markup=kb)

    elif data == "pay_sham":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ أرسل إشعار التحويل لشحن الرصيد", callback_data="check_payment")],
            [InlineKeyboardButton(text="🔙 العودة لطرق الدفع", callback_data="payment_methods")]
        ])
        await callback.message.edit_text("📌 **شام كاش**\n\nالحساب:\n`18a4c2941387daeaf0256639ffc705e8`\n\n⚠️ بعد التحويل اضغط أرسل إشعار التحويل.", parse_mode="Markdown", reply_markup=kb)

    elif data == "pay_crypto":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ أرسل إشعار التحويل لشحن الرصيد", callback_data="check_payment")],
            [InlineKeyboardButton(text="🔙 العودة لطرق الدفع", callback_data="payment_methods")]
        ])
        await callback.message.edit_text("📌 **عملات رقمية (USDT)**\n\nBEP20:\n`0xd22ccb682b5a8f1dbf6152882673b0130620cb11`\n\nTRC20:\n`TAuVtaQATX9TNyNQjKQK11pFKsx6X2hGJx`\n\n⚠️ **الحد الأدنى للإيداع:** `0.2 USDT`", parse_mode="Markdown", reply_markup=kb)

    elif data == "check_payment":
        await state.set_state(DepositState.waiting_for_proof)
        await callback.message.edit_text("📩 **يرجى إرسال رقم العملية أو صورة إشعار التحويل الآن:**", parse_mode="Markdown")

    elif data.startswith("adm_app_"):
        dep_id = data.replace("adm_app_", "")
        client_id = pending_deposits.get(dep_id)
        if client_id:
            user_balances[client_id] = get_user_balance(client_id) + 0.60
            try:
                await bot.send_message(chat_id=client_id, text=f"🎉 **تم قبول الإيداع وإضافة الرصيد!**\n💰 رصيدك الحالي: `{user_balances[client_id]:.2f}$`", parse_mode="Markdown")
            except:
                pass
            await callback.message.edit_text(f"{callback.message.text}\n\n✅ **تم قبول الطلب بنجاح.**", parse_mode="Markdown")

    elif data.startswith("adm_rej_"):
        dep_id = data.replace("adm_rej_", "")
        client_id = pending_deposits.get(dep_id)
        if client_id:
            try:
                await bot.send_message(chat_id=client_id, text="❌ **عذراً، تم رفض طلب الشحن من قبل الإدارة.**")
            except:
                pass
            await callback.message.edit_text(f"{callback.message.text}\n\n❌ **تم رفض الطلب.**", parse_mode="Markdown")

    elif data == "referral_system":
        bot_info = await bot.get_me()
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]])
        await callback.message.edit_text(f"🎁 **برنامج الإحالة:**\nاحصل على إيميل مجاني عند دعوة 5 أشخاص!\n🔗 رابطك:\n`https://t.me/{bot_info.username}?start={user_id}`", parse_mode="Markdown", reply_markup=kb)

    elif data == "support_info":
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]])
        await callback.message.edit_text(f"🛠 **الدعم الفني:**\nتواصل مع المالك: {ADMIN_USERNAME}", parse_mode="Markdown", reply_markup=kb)

    elif data == "back_to_main":
        await state.clear()
        kb, bal = main_menu(user_id)
        await callback.message.edit_text(f"القائمة الرئيسية للمتجر 📧:\n\n💰 **رصيدك الحالي:** `{bal:.2f}$`", parse_mode="Markdown", reply_markup=kb)
        
    await callback.answer()

@dp.message(DepositState.waiting_for_proof)
async def process_proof(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    dep_id = str(user_id)
    pending_deposits[dep_id] = user_id

    kb_back = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]])
    await message.answer("⏳ **تم استلام طلبك بنجاح!**\nجاري التحقق وإضافة الرصيد...", parse_mode="Markdown", reply_markup=kb_back)
    
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ قبول وتأكيد الشحن", callback_data=f"adm_app_{dep_id}")],
        [InlineKeyboardButton(text="❌ رفض الطلب", callback_data=f"adm_rej_{dep_id}")]
    ])
    
    admin_text = f"📥 **طلب شحن جديد!**\n👤 الزبون: {message.from_user.full_name}\n🆔 ID: `{user_id}`\n📝 التفاصيل: {message.text or 'صورة إشعار'}"
    
    try:
        if message.photo:
            await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=admin_text, parse_mode="Markdown", reply_markup=admin_kb)
        else:
            await bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown", reply_markup=admin_kb)
    except Exception as e:
        logging.error(f"Admin error: {e}")

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
