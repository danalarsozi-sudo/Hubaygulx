import logging
import random
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# --- AYARLAR ---
API_TOKEN = '8319522123:AAG4LN2ReOxg_fHp2MdYaLgm7en-NNMCJi8'
ADMIN_ID = 7611297191
# Kanal kullanıcı adınız
CHANNEL_ID = '@onlybrazzz' 

# Logging
logging.basicConfig(level=logging.INFO)

# Bot Başlatma
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Basit Veritabanı
db = {
    "users": {},
    "videos": [],
    "upload_stats": {}
}

# --- RENDER UYKU ENGELLEYİCİ ---
async def handle(request):
    return web.Response(text="Aýgül Bot işläp dur!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()

# --- KANAL KONTROL FONKSİYONU ---
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        logging.error(f"Abuna barlagynda ýalňyşlyk: {e}")
        return False

# --- KLAVYELER ---
def get_subscribe_kb():
    channel_url = f"https://t.me/onlybrazzz"
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Kanalymyza goşul 📢", url=channel_url))
    kb.add(InlineKeyboardButton(text="Goşuldym / Barladym ✅", callback_data="check_sub"))
    return kb

def get_user_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🔥 Maňa wideo görkez"))
    kb.add(KeyboardButton("📤 Wideo ugrat"))
    return kb

def get_admin_kb():
    kb = get_user_kb()
    kb.add(KeyboardButton("👑 Admin Paneli"))
    return kb

# --- KOMUTLAR VE MESAJLAR ---

@dp.callback_query_handler(text="check_sub")
async def process_check_sub(callback_query: types.CallbackQuery):
    is_sub = await check_subscription(callback_query.from_user.id)
    if is_sub:
        await bot.answer_callback_query(callback_query.id, text="Sag bol, indi boty ulanyp bilersiň! 😊")
        await bot.send_message(callback_query.from_user.id, "Hoş geldiň! Düwmeleri ulanyp başla:", reply_markup=get_user_kb())
    else:
        await bot.answer_callback_query(callback_query.id, text="Heniz goşulmadyňyz! Haýyş, kanala goşulyň.", show_alert=True)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    db["users"][user_id] = message.from_user.username or "Nämälim"
    
    is_sub = await check_subscription(user_id)
    if not is_sub and user_id != ADMIN_ID:
        await message.reply(
            "Salam! Boty ulanmak üçin ilki bilen biziň kanalymyza goşulmaly. 🔒",
            reply_markup=get_subscribe_kb()
        )
        return

    welcome = "Salam! Men Aýgül. 🔥 Wideolary görmek üçin aşakdaky düwmeleri ulan!"
    kb = get_admin_kb() if user_id == ADMIN_ID else get_user_kb()
    await message.reply(welcome, reply_markup=kb)

@dp.message_handler(lambda m: m.text == "🔥 Maňa wideo görkez")
async def send_video(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscription(user_id) and user_id != ADMIN_ID:
        await message.reply("Wideolar üçin kanalymyza goşulmaly! 👇", reply_markup=get_subscribe_kb())
        return

    if not db["videos"]:
        await message.reply("Häzirlikçe wideo ýok... Maňa bir zatlar ugrat!")
        return
    await bot.send_video(message.chat.id, random.choice(db["videos"]), caption="Seniň üçin... 😉")

@dp.message_handler(content_types=['video'])
async def handle_vids(message: types.Message):
    db["videos"].append(message.video.file_id)
    db["upload_stats"][message.from_user.id] = db["upload_stats"].get(message.from_user.id, 0) + 1
    await message.reply("Wideo ýatda saklandy! Sag bol, janym. ❤️")

@dp.message_handler(lambda m: m.text == "👑 Admin Paneli")
async def admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        stats = f"👤 Ulanyjy: {len(db['users'])}\n🎬 Wideo: {len(db['videos'])}\n\n"
        stats += "📊 Aktiw ulanyjylar:\n"
        for uid, count in db["upload_stats"].items():
            uname = db["users"].get(uid, "Bilinmeýär")
            stats += f"- @{uname}: {count} wideo\n"
        await message.reply(stats)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_web_server())
    print("Bot we @onlybrazzz barlagy işläp başlady...")
    executor.start_polling(dp, skip_updates=True)
