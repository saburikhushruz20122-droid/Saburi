from telegram import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardButton, InlineKeyboardMarkup, Update
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import random, string, os

TOKEN = "7771251447:AAHaTR1HM_n5yIQMqWyi5AGr9P1L-KVuWt0" # Токени BotFather 
ADMIN_ID = 8676645713 # ID-и админ

# ===== МАҲСУЛОТ =====
PRODUCTS = {
    "Поёфзол": {
        "Мардона": [
            {"name": "Sneakers A", "price": 100, "colors": ["Сиёҳ","Сафед"], "sizes": [40,41,42], "image":"istockphoto-1221348467-612x612.jpg"},
            {"name": "Boots B", "price": 150, "colors": ["Қаҳваранг"], "sizes": [41,42,43], "image":"boots_b.jpg"}
        ],
        "Занона": [
            {"name": "Heels X", "price": 120, "colors": ["Сурх"], "sizes": [36,37,38], "image":"heels_x.jpg"}
        ]
    },
    "Либос": {
        "Мардона": [
            {"name": "T-Shirt M", "price": 50, "colors": ["Сиёҳ","Сафед"], "sizes": ["M","L","XL"], "image":"tshirt_m.jpg"}
        ],
        "Занона": [
            {"name": "Dress W", "price": 80, "colors": ["Сурх","Сабз"], "sizes": ["S","M","L"], "image":"dress_w.jpg"}
        ]
    }
}

SESSIONS = {}
ORDERS = {}
USER_ORDERS = {}
USER_PROFILE = {}
FAVORITES = {}

def generate_track():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

menu = ReplyKeyboardMarkup([
    ["📦 Категорияҳо"],
    ["📦 Заказҳои ман","🔍 Трек"],
    ["ℹ️ Дар бораи бот","💬 Ба админ"],
    ["👤 Профил","❤️ Избранное"]
], resize_keyboard=True)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if uid not in USER_PROFILE:
        SESSIONS[uid] = {"step":"profile_name","order":{}}
        await update.message.reply_text("Салом! Лутфан маълумоти худро ворид кунед.\nНом:")
    else:
        SESSIONS[uid] = {"step":"menu","order":{}}
        await update.message.reply_text("👋 Салом!", reply_markup=menu)

# ===== MESSAGE =====
async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text
    s = SESSIONS.get(uid, {"step":"menu","order":{}})
    step = s["step"]

    # ===== ПРОФИЛ =====
    if step.startswith("profile"):
        if step=="profile_name":
            USER_PROFILE[uid] = {"name": text}
            s["step"] = "profile_surname"
            await update.message.reply_text("Насаб:")
        elif step=="profile_surname":
            USER_PROFILE[uid]["surname"] = text
            s["step"] = "profile_phone"
            await update.message.reply_text("Рақами телефон:")
        elif step=="profile_phone":
            phone = text
            USER_PROFILE[uid]["phone"] = phone
            s["step"] = "menu"
            await update.message.reply_text("Профили шумо сабт шуд!", reply_markup=menu)
        SESSIONS[uid] = s
        return

    # ===== ПАЁМ БА АДМИН =====
    if step=="chat":
        await context.bot.send_message(ADMIN_ID,f"💬 {uid} ({USER_PROFILE.get(uid,{}).get('name','')}):\n{text}")
        await update.message.reply_text("📩 Фиристода шуд")
        s["step"]="menu"
        SESSIONS[uid] = s
        return

    # ===== TRACK =====
    if text.startswith("/track"):
        code = text.split()[-1]
        if code in ORDERS:
            o = ORDERS[code]
            await update.message.reply_text(
                f"📦 {o['product']['name']}\n"
                f"{o['category']} | {o['gender']}\n"
                f"Размер: {o['size']}\n"
                f"Ранг: {o['color']}\n"
                f"💰 {o['product']['price']}$\n"
                f"📊 {o['status']}"
            )
        else:
            await update.message.reply_text("❌ Ёфт нашуд")
        return

    # ===== MENU =====
    if step=="menu":
        if uid not in USER_PROFILE:
            await update.message.reply_text("⚠️ Лутфан аввал профилро пур кунед!")
            return

        if text == "📦 Категорияҳо":
            kb = [[KeyboardButton(cat)] for cat in PRODUCTS]
            await update.message.reply_text("Категория:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
            s["step"] = "category"

        elif text == "📦 Заказҳои ман":
            orders = USER_ORDERS.get(uid, [])
            if not orders:
                await update.message.reply_text("Заказ нест")
            else:
                for o in orders:
                    await update.message.reply_text(f"{o['product']['name']} | {o['tracking']} | {o['status']}")

        elif text=="💬 Ба админ":
            await update.message.reply_text("Паём навис:")
            s["step"]="chat"

        elif text == "🔍 Трек":
            await update.message.reply_text("Навис: /track CODE")

        elif text == "ℹ️ Дар бораи бот":
            await update.message.reply_text("🤖 Интернет-магазин бот, версия премиум.")

        elif text=="👤 Профил":
            p = USER_PROFILE.get(uid, {})
            await update.message.reply_text(
                f"👤 Профил:\nНом: {p.get('name','')}\nНасаб: {p.get('surname','')}\n📱 Рақам: {p.get('phone','')}"
            )

        elif text=="❤️ Избранное":
            fav = FAVORITES.get(uid,[])
            if not fav:
                await update.message.reply_text("Избранное холӣ аст")
            else:
                for o in fav:
                    product = o["product"]
                    caption = f"{product['name']} 💰{product['price']}$"
                    if os.path.exists(product["image"]):
                        with open(product["image"], "rb") as f:
                            await update.message.reply_photo(f, caption=caption)
                    else:
                        await update.message.reply_text(caption)

    # ===== CATEGORY =====
    elif step=="category":
        if text not in PRODUCTS:
            await update.message.reply_text("Хато")
            return
        s["order"]["category"] = text
        kb = [[KeyboardButton("Мардона")],[KeyboardButton("Занона")]]
        await update.message.reply_text("Ҷинс:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        s["step"] = "gender"

    # ===== GENDER =====
    elif step=="gender":
        s["order"]["gender"] = text
        products = PRODUCTS[s["order"]["category"]][text]
        for i,p in enumerate(products):
            caption = f"{p['name']}\n💰 {p['price']}$\nРазмерҳо: {p['sizes']}\nРангҳо: {p['colors']}"
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Интихоб", callback_data=f"select_{i}")]])
            if os.path.exists(p["image"]):
                with open(p["image"], "rb") as f:
                    await update.message.reply_photo(f, caption=caption, reply_markup=kb)
            else:
                await update.message.reply_text(caption, reply_markup=kb)
        s["step"]="wait_product"

    # ===== SIZE =====
    elif step=="size":
        s["order"]["size"] = text
        colors = s["order"]["product"]["colors"]
        kb = [[KeyboardButton(c)] for c in colors]
        await update.message.reply_text("Ранг:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        s["step"]="color"

    # ===== COLOR =====
    elif step=="color":
        s["order"]["color"] = text
        kb = ReplyKeyboardMarkup([["✅ Харидан"],["❌ Бекор"]], resize_keyboard=True)
        await update.message.reply_text("Тасдиқ:", reply_markup=kb)
        s["step"]="confirm"

    # ===== CONFIRM =====
    elif step=="confirm":
        if "Харидан" in text:
            o = s["order"]
            track = generate_track()
            o["tracking"] = track
            o["status"]="⏳ Дар интизорӣ"
            ORDERS[track]=o
            USER_ORDERS.setdefault(uid,[]).append(o)

            p = USER_PROFILE.get(uid,{})
            caption = (
                f"👤 USER: {p.get('name','')} {p.get('surname','')} | 📱 {p.get('phone')}\n"
                f"📦 Номи бор: {o['product']['name']}\n"
                f"📂 Категория: {o['category']}\n"
                f"👕 Ҷинс: {o['gender']}\n"
                f"📏 Размер: {o['size']}\n"
                f"🎨 Ранг: {o['color']}\n"
                f"💰 Нарх: {o['product']['price']}$\n"
                f"🆔 Track: {track}\n"
                f"📊 Статус: {o['status']}"
            )
            img = o['product']['image']
            if os.path.exists(img):
                with open(img,"rb") as f:
                    await context.bot.send_photo(
                        ADMIN_ID,
                        photo=f,
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💬 Ба user", callback_data=f"msg_{uid}")]])
                    )
            else:
                await context.bot.send_message(ADMIN_ID, caption)
            await update.message.reply_text(f"✅ Хариди шумо анҷом ёфт!\n🆔 Track: {track}\n📩 Админ ба шумо пайваст мешавад")
        else:
            await update.message.reply_text("❌ Бекор шуд")
        s["step"]="menu"
        s["order"]={}
        await update.message.reply_text("Menu:", reply_markup=menu)

    SESSIONS[uid]=s

# ===== CALLBACK =====
async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    s = SESSIONS[uid]

    if query.data.startswith("select_"):
        index = int(query.data.split("_")[1])
        category = s["order"]["category"]
        gender = s["order"]["gender"]
        product = PRODUCTS[category][gender][index]
        s["order"]["product"]=product
        sizes = product["sizes"]
        kb = [[KeyboardButton(str(x))] for x in sizes]
        await query.message.reply_text("Размерро интихоб кунед:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        s["step"]="size"

    elif query.data.startswith("msg_"):
        target_uid=int(query.data.split("_")[1])
        await context.bot.send_message(target_uid,"💬 Аз админ паём:\n")
        await query.message.reply_text("📩 Паём фиристода шуд!")

    SESSIONS[uid]=s

# ===== RUN =====
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), msg))
app.add_handler(CallbackQueryHandler(cb))

print("🔥 BOT PREMIUM READY")
app.run_polling()
