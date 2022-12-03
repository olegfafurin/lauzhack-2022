import os
import logging
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram import Update

WISHLIST_BOT_TOKEN = os.environ["WISHLIST_BOT_TOKEN"]


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.log(logging.INFO, f"start handler called by {update.effective_user.name}")
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="That's a start method of the LauzHack Wishlist bot!")


def main():
    application = ApplicationBuilder().token(WISHLIST_BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
