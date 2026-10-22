import asyncio
import logging
import os
import urllib.request
import csv
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
        return []

def get_stock(cat):
    if cat == "cat_old": return fetch_emails_from_sheet(0)
    elif cat == "cat_new": return fetch_emails_from_sheet(1)
    elif cat == "cat_medium": return fetch_emails_from_sheet(2)
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
    if user_id not in user_balances: user_balances[user_id] = 0.0
    kb, bal = main_menu(user_id)
    await message.answer(f"أهلاً بك في متجر الإيميلات الفوري! 📧✨\n\n💰 **رصيدك الحالي:** `{bal:.2f}$`", parse_mode="Markdown", reply_markup=kb)

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
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 شراء إيميلات", callback_data=f"buy_req_{data}")],
            [InlineKeyboardButton(text="🔙 العودة", callback_data="list_emails")]
        ])
        await callback.message.edit_text(f"📌 **الفئة المتاحة:** `{count}` إيميل\nاضغط شراء لتحديد الكمية:", parse_mode="Markdown", reply_markup=kb)
    elif data.startswith("buy_req_"):
        cat = data.replace("buy_req_", "")
        stock = get_stock(cat)
        if len(stock) == 0:
            await callback.answer("❌ نفدت الكمية!", show_alert=True)
            return
        await state.update_data(selected_cat=cat)
        await state.set_state(BuyState.waiting_for_quantity)
        await callback.message.edit_text(f"📥 أرسل الكمية المطلوبة (متوفر {len(stock)}):", parse_mode="Markdown")
    elif data == "payment_methods":
        await state.clear()
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ إرسال رقم العملية", callback_data="check_payment")],
            [InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_main")]
        ])
        await callback.message.edit_text("💳 أرسل رقم العملية لشحن الرصيد:", parse_mode="Markdown", reply_markup=kb)
    elif data == "check_payment":
        await state.set_state(DepositState.waiting_for_proof)
        await callback.message.edit_text("📩 أرسل رقم العملية الآن:", parse_mode="Markdown")
    elif data == "referral_system":
        await state.clear()
        bot_info = await bot.get_me()
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_main")]])
        await callback.message.edit_text(f"🎁 رابط الدعوة الخاص بك:\nhttps://t.me/{bot_info.username}?start={user_id}", parse_mode="Markdown", reply_markup=kb)
    elif data == "support_info":
        await state.clear()
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_main")]])
        await callback.message.edit_text(f"🛠 الدعم الفني: {ADMIN_USERNAME}", parse_mode="Markdown", reply_markup=kb)
    elif data == "back_to_main":
        await state.clear()
        kb, bal = main_menu(user_id)
        await callback.message.edit_text(f"القائمة الرئيسية 📧:\n💰 رصيدك: `{bal:.2f}$`", parse_mode="Markdown", reply_markup=kb)
    await callback.answer()

@dp.message(BuyState.waiting_for_quantity)
async def process_buy_quantity(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    cat = user_data.get("selected_cat")
    stock = get_stock(cat)
    price = 0.35 if cat == "cat_new" else 0.60
    if not message.text.isdigit():
        await message.answer("❌ أرسل رقم صحيح:")
        return
    qty = int(message.text.strip())
    if qty <= 0 or qty > len(stock):
        await message.answer("❌ الكمية غير صالحة.")
        return
    total_cost = round(qty * price, 2)
    bal = get_user_balance(user_id)
    if bal < total_cost:
        await message.answer("❌ رصيدك غير كافٍ.")
        await state.clear()
        return
    new_bal = update_user_balance(user_id, -total_cost)
    purchased = [stock[i] for i in range(qty)]
    for e in purchased: sold_emails_set.add(e)
    emails_str = "\n".join(purchased)
    await message.answer(f"✅ تمت الشراء بنجاح!\n\n{emails_str}", parse_mode="Markdown")
    await state.clear()

@dp.message(DepositState.waiting_for_proof)
async def process_proof(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    text_content = (message.text or message.caption or "").strip()
    await message.answer("⏳ تم الاستلام، جاري المراجعة.", parse_mode="Markdown")
    await bot.send_message(chat_id=ADMIN_ID, text=f"📥 طلب شحن من `{user_id}`:\n{text_content}", parse_mode="Markdown")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, handle_signals=False)

if __name__ == '__main__':
    asyncio.run(main())




