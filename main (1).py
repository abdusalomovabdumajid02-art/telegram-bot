import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# =============================================
# SOZLAMALAR
# =============================================

TELEGRAM_TOKEN = "8990294068:AAEOxa5dL_6CyC4J_HQtwow1Y8s0d-JBLdc"
GEMINI_API_KEY = "AIzaSyC7k1z_IlubFTHLwLVXaa-7Vme320itrfQ"

SYSTEM_PROMPT = """Siz do'stona va yordam beruvchi virtual assistantsiz.
Uzbek tilida javob bering (agar foydalanuvchi boshqa tilda yozsa, o'sha tilda javob bering).
Qisqa, aniq va foydali javoblar bering.
Har doim muloyim va professional bo'ling."""

# =============================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Gemini sozlash
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# Har bir foydalanuvchi uchun suhbat tarixi
user_chats = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_chats[user_id] = model.start_chat(history=[])
    await update.message.reply_text(
        "Salom! 👋 Men Gemini AI assistantman.\n"
        "Menga istalgan savolingizni bering!\n\n"
        "Suhbatni qayta boshlash: /reset"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_chats[user_id] = model.start_chat(history=[])
    await update.message.reply_text("✅ Suhbat tarixi tozalandi!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    user_name = update.effective_user.first_name

    logger.info(f"Xabar [{user_id}] {user_name}: {user_text}")

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])

    try:
        response = user_chats[user_id].send_message(user_text)
        reply = response.text
        await update.message.reply_text(reply)
        logger.info(f"Javob [{user_id}]: {reply[:100]}...")

    except Exception as e:
        logger.error(f"Xato: {e}")
        await update.message.reply_text("❌ Kechirasiz, xatolik yuz berdi. Keyinroq urinib ko'ring.")


def main():
    print("🤖 Gemini Telegram bot ishga tushmoqda...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
