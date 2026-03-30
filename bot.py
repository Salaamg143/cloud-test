import os
import logging
import anthropic
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# =============================================
# APNA TOKEN YAHAN DAALO
# =============================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8680921366:AAE0HV3W-zNOj1fqjwwLxcg-6eU8TgcIE6A")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "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")

# =============================================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Har user ki chat history store karne ke liye
user_histories = {}

SYSTEM_PROMPT = """Tum ek helpful AI assistant ho jo Hinglish (Hindi + English mix) mein baat karta hai.
Tum friendly, funny aur helpful ho. Short aur clear jawab do.
Agar koi English mein pooche toh English mein jawab do, agar Hinglish/Hindi mein pooche toh Hinglish mein jawab do."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_histories[user_id] = []  # history reset
    await update.message.reply_text(
        f"Assalam-o-Alaikum {user.first_name}! 👋\n\n"
        "Main aapka AI Assistant hoon jo Claude (Anthropic) se powered hai! 🤖\n\n"
        "Mujhse kuch bhi poochh sakte ho!\n\n"
        "Commands:\n"
        "/start - Naya conversation shuru karo\n"
        "/clear - Chat history saaf karo\n"
        "/help - Help dekho"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *Help Menu*\n\n"
        "• Koi bhi sawaal poochho — main jawab dunga!\n"
        "• /start — Naya chat shuru karo\n"
        "• /clear — Purani history hataao\n"
        "• /help — Yeh message dobara dekho\n\n"
        "Main Claude AI se powered hoon! 🚀",
        parse_mode="Markdown"
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text("✅ Chat history saaf ho gayi! Naya conversation shuru karo.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    # Typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # History initialize karo agar nahi hai
    if user_id not in user_histories:
        user_histories[user_id] = []

    # User ka message history mein add karo
    user_histories[user_id].append({
        "role": "user",
        "content": user_text
    })

    # Last 20 messages hi rakho (memory ke liye)
    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = user_histories[user_id][-20:]

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=user_histories[user_id]
        )

        assistant_reply = response.content[0].text

        # Assistant reply bhi history mein add karo
        user_histories[user_id].append({
            "role": "assistant",
            "content": assistant_reply
        })

        await update.message.reply_text(assistant_reply)

    except anthropic.APIError as e:
        logger.error(f"Anthropic API Error: {e}")
        await update.message.reply_text("❌ AI se error aayi. Thodi der baad try karo.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Kuch gadbad ho gayi. Dobara try karo!")


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot chal raha hai... 🚀")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
