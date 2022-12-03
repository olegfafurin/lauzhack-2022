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
ROLE_CHOICE, MAKE_A_WISH, SEE_WISHES, NEW_WISH_CHOICE, EDIT_WISH, ADD_NAME, ADD_PHOTO, ADD_DESC = range(8)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their choice."""
    reply_keyboard = [["Make a wish", "See wishes", "Edit wishes"]]

    await update.message.reply_text(
        "Hi! Would you like to add/edit your own wish or to see your friend's wish?\n\n",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Wish or search?"
        ),
    )

    return ROLE_CHOICE


async def role_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Role of %s: %s", user.name, update.message.text)

    choice = update.message.text

    if choice == "Make a wish":
        await update.message.reply_text(
            f"User {user.name} requested a new wish creating",
        )
        return MAKE_A_WISH
    elif choice == "See wishes":
        await update.message.reply_text(
            "TODO See wishes...",
        )
        return SEE_WISHES
    elif choice == "Edit wishes":
        await update.message.reply_text(
            "TODO edit wishes...",
        )
        return EDIT_WISH
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
    make_keyboard = [["Add a name", "Add a photo", "Add a description"]]
    user = update.message.from_user
    logger.info(f"User {user.name} requested a new wish creating")
    await update.message.reply_text(
        f"TODO Making a new wish for {user}", reply_markup=ReplyKeyboardMarkup(
            make_keyboard, one_time_keyboard=True, input_field_placeholder="..."
        ),
    )
    return NEW_WISH_CHOICE


async def new_wish_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    logger.info("A user wants to %s: %s", choice.name, update.message.text)

    if choice == "Add a name":
        await update.message.reply_text(
            "TODO add a name...",
        )
        return ADD_NAME
    elif choice == "Add a photo":
        await update.message.reply_text(
            "TODO add a name...",
        )
        return ADD_PHOTO
    elif choice == "Add a description":
        await update.message.reply_text(
            "TODO add a description...",
        )
        return ADD_DESC
    else:
        logger.info("Unknown choice, terminating state machine")
        return ConversationHandler.END

async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        logger.info(f"User {user.name} added a name of a new wish")
        await update.message.reply_text(
            f"TODO Naming a new wish for {user}"
        )
        return ConversationHandler.END


async def add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(f"User {user.name} added a picture of a new wish")
    await update.message.reply_text(
        f"TODO Adding a pic of a new wish for {user}"
    )
    return ConversationHandler.END

async def add_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(f"User {user.name} added a description of a new wish")
    await update.message.reply_text(
        f"TODO Adding a desc of a new wish for {user}"
    )
    return ConversationHandler.END

async def edit_wish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(f"User {user.name} requested a new wish editing")
    await update.message.reply_text(
        f"TODO Editing a new wish for {user}"
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
            ROLE_CHOICE: [MessageHandler(filters.Regex("^(Make a wish|See wishes|Edit wishes)$"), role_choice)],
            EDIT_WISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_wish)],
            MAKE_A_WISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, make_wish)],
            NEW_WISH_CHOICE: [MessageHandler(filters.Regex("^(Add a name|Add a photo|Add a description)$"), new_wish_choice)],
            ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_name)],
            ADD_PHOTO:[MessageHandler(filters.PHOTO & ~filters.COMMAND, add_photo)],
            ADD_DESC:[MessageHandler(filters.TEXT & ~filters.COMMAND, add_desc)],
            SEE_WISHES: [MessageHandler(filters.TEXT & ~filters.COMMAND, see_wishes)],

        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()