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
pending_operations = {}  # حفظ رقم العملية للزبون
admin_action_target = {} # لتتبع العملية عندما يرسل المدير المبلغ

referrals = {}
user_purchases_count = {}
inviters = {}

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
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) > 1 and args[1].isdigit():
        inviter_id = int(args[1])
        if inviter_id != user_id and user_id not in inviters.values():
            if user_id not in inviters:
                inviters[user_id] = inviter_id
                if inviter_id not in referrals:
                    referrals[inviter_id] = []
                if user_id not in referrals[inviter_id]:
                    referrals[inviter_id].append(user_id)

    kb, bal = main_menu(user_id)
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
        cat = data.replace("buy_", "")
        price = 0.35 if cat == "cat_new" else 0.60
        bal = get_user_balance(user_id)
        
        if bal < price:
            await callback.answer(f"❌ رصيدك غير كافٍ ({bal:.2f}$)! يرجى شحن الرصيد.", show_alert=True)
            return
            
        stock = EMAILS_OLD if cat == "cat_old" else (EMAILS_NEW if cat == "cat_new" else EMAILS_MEDIUM)
        if not stock:
            await callback.answer("❌ عذراً، هذه الفئة نفدت من المخزن!", show_alert=True)
            return
            
        user_balances[user_id] -= price
        email_data = stock.pop(0)
        
        user_purchases_count[user_id] = user_purchases_count.get(user_id, 0) + 1
        
        if user_purchases_count[user_id] == 1 and user_id in inviters:
            inviter_id = inviters[user_id]
            valid_refs = [ref for ref in referrals.get(inviter_id, []) if user_purchases_count.get(ref, 0) >= 1]
            if len(valid_refs) == 5:
                user_balances[inviter_id] = get_user_balance(inviter_id) + 0.60
                try:
                    await bot.send_message(
                        chat_id=inviter_id,
                        text="🎁 **تهانينا!** لقد أتم أصدقاؤك الـ 5 المدعوون عملية الشراء الأولى بنجاح.\nتمت إضافة رصيد بقيمة `0.60$` إلى حسابك كهدية إحالة! 🎉",
                        parse_mode="Markdown"
                    )
                except:
                    pass

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
            [InlineKeyboardButton(text="✅ إرسال رقم عملية شام كاش", callback_data="check_payment")],
            [InlineKeyboardButton(text="🔙 العودة لطرق الدفع", callback_data="payment_methods")]
        ])
        await callback.message.edit_text(
            "📌 **1️⃣ شام كاش**\n\n"
            "يرجى التحويل إلى العنوان التالي:\n"
            "`18a4c2941387daeaf0256639ffc705e8`\n\n"
            "⚠️ بعد التحويل اضغط على الزر أدناه وأرسل **رقم العملية** فقط.",
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
            "⚠️ أرسل العملية ثم اضغط على الزر أدناه وأرسل **رقم العملية (TxID)** فقط.",
            parse_mode="Markdown",
            reply_markup=kb
        )

    elif data == "check_payment":
        await state.set_state(DepositState.waiting_for_proof)
        await callback.message.edit_text("📩 **يرجى إرسال رقم العملية فقط (بدون أي مبلغ أو صور):**", parse_mode="Markdown")

    elif data.startswith("adm_app_"):
        client_id = int(data.replace("adm_app_", ""))
        admin_action_target[ADMIN_ID] = client_id
        await callback.message.answer("✍️ **أرسل الآن المبلغ بالدولار (مثال: 0.65 أو 1.5) في رسالة جديدة ليتم إضافته لرصيد الزبون:**", parse_mode="Markdown")

    elif data.startswith("adm_rej_"):
        client_id = int(data.replace("adm_rej_", ""))
        try:
            await bot.send_message(chat_id=client_id, text="❌ **عذراً، تم رفض طلب الشحن من قبل الإدارة.**", parse_mode="Markdown")
        except:
            pass
        await callback.message.edit_text(f"{callback.message.text}\n\n❌ **تم رفض الطلب.**", parse_mode="Markdown")

    elif data == "referral_system":
        bot_info = await bot.get_me()
        completed_refs = len([ref for ref in referrals.get(user_id, []) if user_purchases_count.get(ref, 0) >= 1])
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

# استقبال المبلغ من المدير بعد النقر على زر قبول
@dp.message(lambda message: message.from_user.id == ADMIN_ID and ADMIN_ID in admin_action_target)
async def process_admin_amount_input(message: types.Message):
    client_id = admin_action_target.pop(ADMIN_ID, None)
    if not client_id:
        return

    try:
        amount_to_add = float(message.text.strip())
    except ValueError:
        await message.answer("❌ يرجى إرسال رقم صحيح للمبلغ (مثال: `0.65` أو `1`)")
        admin_action_target[ADMIN_ID] = client_id  # إعادة تعيين الهدف
        return

    # إضافة الرصيد للزبون
    user_balances[client_id] = get_user_balance(client_id) + amount_to_add
    
    try:
        await bot.send_message(
            chat_id=client_id, 
            text=f"🎉 **تم قبول الإيداع وإضافة الرصيد بنجاح!**\n➕ المبلغ المضاف: `{amount_to_add:.2f}$`\n💰 رصيدك الحالي: `{user_balances[client_id]:.2f}$`", 
            parse_mode="Markdown"
        )
    except:
        pass

    op_num = pending_operations.get(client_id, "غير متوفر")
    await message.answer(f"✅ **تمت الإنجاز بنجاح!**\nتمت إضافة `{amount_to_add:.2f}$` للزبون (رقم العملية: `{op_num}`).", parse_mode="Markdown")

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
