import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- AYARLAR ---
# Token ve Admin ID'niz buraya doğru şekilde yerleştirildi
API_TOKEN = '8319522123:AAG4LN2ReOxg_fHp2MdYaLgm7en-NNMCJi8'
ADMIN_ID = 7611297191

# Günlük kaydı (Hataları görmek için)
logging.basicConfig(level=logging.INFO)

# Botu başlat
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Veritabanı simülasyonu (Bellek içi)
# Not: Bot kapanırsa bu veriler silinir. Gerçek kullanımda SQLite önerilir.
db = {
    "users": {}, # {user_id: username}
    "videos": [], # Video file_id listesi
    "upload_stats": {} # {user_id: gönderilen_video_sayısı}
}

# --- KLAVYELER (Türkmençe) ---
def get_user_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🔥 Maňa wideo görkez"))
    kb.add(KeyboardButton("📤 Wideo ugrat"))
    return kb

def get_admin_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🔥 Maňa wideo görkez"))
    kb.add(KeyboardButton("📤 Wideo ugrat"))
    kb.add(KeyboardButton("👑 Admin Paneli"))
    return kb

# --- KOMUTLAR ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Nämälim"
    
    # Kullanıcıyı kaydet
    db["users"][user_id] = username
    
    welcome_text = (
        f"Salam, süýji oglan! Men Aýgül. 💋\n\n"
        f"Meniň dünýäme hoş geldiň. Bu ýerde iň gyzykly we gyzgyn wideolary görüp bilersiň. "
        f"Wideolaryňy maňa ugrat, menem saňa iň gowularyny görkezeýin..."
    )
    
    if user_id == ADMIN_ID:
        await message.reply(welcome_text, reply_markup=get_admin_kb())
    else:
        await message.reply(welcome_text, reply_markup=get_user_kb())

@dp.message_handler(lambda message: message.text == "🔥 Maňa wideo görkez")
async def send_random_video(message: types.Message):
    if not db["videos"]:
        await message.reply("Häzirlikçe mende täze wideo ýok... Maňa bir zatlar ugrat, garaşýaryn! 😉")
        return
    
    random_video = random.choice(db["videos"])
    await bot.send_video(
        message.chat.id, 
        random_video, 
        caption="Ine, seniň üçin saýlan wideom... Lezzet al! 🔥"
    )

@dp.message_handler(lambda message: message.text == "📤 Wideo ugrat")
async def ask_for_video(message: types.Message):
    await message.reply("Hany, maňa iň gyzykly wideolaryňy ugrat, men olary ýatda saklaryn... ✨")

@dp.message_handler(content_types=['video'])
async def handle_video(message: types.Message):
    user_id = message.from_user.id
    video_id = message.video.file_id
    
    # Videoyu listeye ekle
    db["videos"].append(video_id)
    
    # İstatistikleri güncelle
    db["upload_stats"][user_id] = db["upload_stats"].get(user_id, 0) + 1
    
    await message.reply("Bu wideo örän gowy! Ony ýatda sakladym. Sag bol, janym! ❤️")

@dp.message_handler(lambda message: message.text == "👑 Admin Paneli")
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    user_count = len(db["users"])
    video_count = len(db["videos"])
    
    report = "👑 **ADMIN HASABATY**\n\n"
    report += f"👤 Jemi ulanyjy: {user_count}\n"
    report += f"🎬 Jemi wideo: {video_count}\n\n"
    report += "📊 **Aktiýul ulanyjylar:**\n"
    
    for uid, count in db["upload_stats"].items():
        uname = db["users"].get(uid, "Bilinmeýär")
        report += f"- @{uname} (ID: {uid}): {count} wideo\n"
    
    if not db["upload_stats"]:
        report += "_Häzirlikçe hiç kim wideo ugratmady._"
        
    await message.reply(report, parse_mode="Markdown")

if __name__ == '__main__':
    print("Aýgül bot işläp başlady...")
    executor.start_polling(dp, skip_updates=True)
