import logging
import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Load tokens from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Debug log to check if token is loading
print("DEBUG: TELEGRAM_TOKEN =", TELEGRAM_TOKEN, file=sys.stderr)

# Fail early if token is missing
if not TELEGRAM_TOKEN or TELEGRAM_TOKEN.startswith("your") or ":" not in TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN is not set properly! Please check your StackHost environment variables.")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("👋 Hi! I'm a Gemini-powered AI bot. Mention me in a group or DM me to chat!")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    chat_type = message.chat.type

    # In group chats, only respond if mentioned
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
        logger.error(f"❌ Error generating response: {e}")
        await message.reply_text("⚠️ Sorry, I had trouble responding. Try again!")

# Main entry point
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
