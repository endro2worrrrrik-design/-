import aiohttp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

TOKEN = "8340283001:AAE92AOiKWQWGoSSVkZNO6WAbRZFX1K0rm8"


# ---------- helpers ----------

async def get_coords(city: str):
    url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={city}&count=1&language=ru"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    if "results" not in data:
        return None

    result = data["results"][0]
    return result["latitude"], result["longitude"]


async def get_weather(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current_weather=true"
        "&timezone=auto"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()


async def get_tomorrow(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min"
        "&timezone=auto"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()


# ---------- handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! ☀️\n\n"
        "Напиши:\n"
        "/weather Город — погода сейчас\n"
        "/tomorrow Город — прогноз на завтра"
    )


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напиши город: /weather Киев")
        return

    city = " ".join(context.args)
    coords = await get_coords(city)

    if not coords:
        await update.message.reply_text("Не нашёл такой город 😕")
        return

    lat, lon = coords
    data = await get_weather(lat, lon)

    w = data["current_weather"]

    text = (
        f"🌤 Погода сейчас в {city}:\n"
        f"Температура: {w['temperature']}°C\n"
        f"Ветер: {w['windspeed']} м/с"
    )

    await update.message.reply_text(text)


async def tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напиши город: /tomorrow Киев")
        return

    city = " ".join(context.args)
    coords = await get_coords(city)

    if not coords:
        await update.message.reply_text("Не нашёл такой город 😕")
        return

    lat, lon = coords
    data = await get_tomorrow(lat, lon)

    temp_max = data["daily"]["temperature_2m_max"][1]
    temp_min = data["daily"]["temperature_2m_min"][1]

    text = (
        f"📅 Завтра в {city}:\n"
        f"Макс: {temp_max}°C\n"
        f"Мин: {temp_min}°C"
    )

    await update.message.reply_text(text)


# ---------- app ----------

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("tomorrow", tomorrow))

    app.run_polling()


if __name__ == "__main__":
    main()
