import asyncio
import logging
import os
import urllib.request
import aiohttp
import csv
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# استبدل هذا بالتوكن الخاص بك
API_TOKEN = '8735041657:AAFVtc6d_dyvh_udzVOsk2wlkbp-KKOTvnI'
ADMIN_ID = 7927059374
ADMIN_USERNAME = "@Alaaa057"

SPREADSHEET_ID = "1ZKVQTAMGb70ptWjj5eE9QsHg2Fyn-P2UeSiyUKi5Wdc"

# عناوين محفظتك الخاصة بالعملات الرقمية
TRC20_WALLET = "TAuVtaQATX9TNyNQjKQK11pFKsx6X2hGJx"
BEP20_WALLET = "0xd22ccb682b5a8f1dbf6152882673b0130620cb11"

# مفتاح API الخاص بـ BscScan (لشبكة BEP20) - يمكنك استخدامه بشكل مجاني
BSCSCAN_API_KEY = "G3YV8P1M4U9Y6W4T8I6R2F3X4U5A6B7C8D" # مثال لمفتاح API، يفضل استخدام مفتاح خاص بك

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

user_balances = {}
user_purchases = {}
user_referrals = {}

sold_emails_set = set()
processed_txids = set() # لحفظ العمليات التي تم استخدامها مسبقاً لمنع التكرار

def get_user_balance(user_id):
    return user_balances.get(user_id, 0.0)

def update_user_balance(user_id, amount):
    current = get_user_balance(user_id)
    new_bal = round(current + amount, 2)
    user_balances[user_id] = new_bal
    return new_bal

class DepositState(StatesGroup):
    waiting_for_proof = State()
    waiting_for_crypto_tx = State()

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
    return InlineKeyboardMarkup(inline







