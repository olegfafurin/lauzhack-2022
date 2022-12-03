import logging
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ApplicationBuilder
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

WISHLIST_BOT_TOKEN = os.environ["WISHLIST_BOT_TOKEN"]
ROLE_CHOICE, MAKE_A_WISH, SEE_WISHES = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [["Make a wish", "See wishes", ]]

    await update.message.reply_text(
        "Hi! Would you like to add your own wish or to see your friend's wish?\n\n",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Wish or search?"
        ),
    )

    return ROLE_CHOICE


async def role_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Role of %s: %s", user.name, update.message.text)

    choice = update.message.text

    if choice == "Make a wish":
        await update.message.reply_text(
            "TODO Make a wish...",
        )
        return MAKE_A_WISH
    elif choice == "See wishes":
        await update.message.reply_text(
            "TODO See wishes...",
        )
        return SEE_WISHES
    else:
        logger.info("Unknown choice, terminating state machine")
        return ConversationHandler.END


async def see_wishes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(f"User {user.name} requested a list of wishes for ", update.message.text)
    await update.message.reply_text(
        f"TODO Showing wishes for {update.message.text}"
    )
    return ConversationHandler.END


async def make_wish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(f"User {user.name} requested a new wish creating")
    await update.message.reply_text(
        f"TODO Making a new wish for {user}"
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main():
    application = ApplicationBuilder().token(WISHLIST_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ROLE_CHOICE: [MessageHandler(filters.Regex("^(Make a wish|See wishes)$"), role_choice)],
            MAKE_A_WISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, make_wish)],
            SEE_WISHES: [MessageHandler(filters.TEXT & ~filters.COMMAND, see_wishes)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
