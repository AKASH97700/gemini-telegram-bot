import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("👋 Hi! I'm a Gemini-powered AI chatbot. Mention me in a group or DM to chat!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    chat_type = message.chat.type

    if chat_type in ['group', 'supergroup'] and f"@{context.bot.username}" not in message.text:
        return

    try:
        user_input = message.text.replace(f"@{context.bot.username}", "").strip()
        if not user_input:
            return

        response = model.generate_content(user_input)
        reply_text = response.text if hasattr(response, 'text') else str(response)
        await message.reply_text(reply_text)
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.reply_text("⚠️ Sorry, I had an issue generating a response.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
