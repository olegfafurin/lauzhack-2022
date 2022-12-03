import collections
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
from wish import Wish

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

WISHLIST_BOT_TOKEN = os.environ["WISHLIST_BOT_TOKEN"]
ROLE_CHOICE, MAKE_A_WISH, SEE_WISHES_FOR_USER, NEW_WISH_NAME_REQUEST, NEW_WISH_PHOTO_REQUEST, \
NEW_WISH_PRICE_REQUEST, EDIT_WISH, ADD_NAME, ADD_PHOTO, NEW_WISH_DESC_REQUEST = range(10)

local_storage = collections.defaultdict(lambda: None)

skip_keyboard = [["Skip"]]
skip_markup = ReplyKeyboardMarkup(skip_keyboard, one_time_keyboard=True)


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
            f"What do you wish?",
        )
        local_storage[user.id] = Wish()
        return NEW_WISH_NAME_REQUEST
    elif choice == "See wishes":
        await update.message.reply_text(
            "Please type a target username",
        )
        return SEE_WISHES_FOR_USER
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
    logger.info(f"[TODO] DB request here", update.message.text)
    # TODO DB request
    await update.message.reply_text(
        f"[TODO] Showing wishes for {update.message.text}"
    )
    return ConversationHandler.END


async def new_wish_name_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    wish_name = update.message.text
    logger.info(f"user {update.message.from_user.name} wants a {wish_name}")
    user_id = update.message.from_user.id
    tmp_wish: Wish = local_storage[user_id]
    if tmp_wish is not None:
        tmp_wish.update_name(wish_name)
    await update.message.reply_text(
        f"Ok, you want a {wish_name}.\n\nDo you have a picture of it?",
        reply_markup=skip_markup,
    )
    return NEW_WISH_PHOTO_REQUEST


async def new_wish_photo_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    tmp_wish: Wish = local_storage[user.id]
    if tmp_wish is not None:
        tmp_wish.update_photo(photo_file)
    await update.message.reply_text(
        "Thanks for a pic!\n\nHow much does your wish cost?",
        reply_markup=skip_markup,
    )
    return NEW_WISH_PRICE_REQUEST


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info(f"User {user.name} with id={user.id} did not send a photo.")
    await update.message.reply_text(
        "How much does your wish cost?",
        reply_markup=skip_markup,
    )
    return NEW_WISH_PRICE_REQUEST


async def new_wish_price_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    wish_price = update.message.text
    user = update.message.from_user
    logger.info(f"user {user.name}'s wish price is {wish_price}")
    tmp_wish = local_storage[user.id]
    if tmp_wish is not None:
        tmp_wish.update_price(wish_price)
    await update.message.reply_text(
        f"Ok, estimated price for your wish is {wish_price}\n\nFeel free to add a quick description to your wish!",
        reply_markup=skip_markup,
    )
    return NEW_WISH_DESC_REQUEST


async def skip_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info(f"User {user.name} with id={user.id} did not provide a price for their wish.")
    await update.message.reply_text(
        "Feel free to add a quick description to your wish!",
        reply_markup=skip_markup,
    )
    return NEW_WISH_DESC_REQUEST


async def new_wish_desc_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    desc = update.message.text
    logger.info(f"User {user.name} added a description {desc} of their new wish")
    tmp_wish = local_storage[user.id]
    if tmp_wish is not None:
        tmp_wish.update_desc(desc)
    await update.message.reply_text(
        "Please review your wish before adding:[TODO]",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def skip_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(f"User {user.name} with id={user.id} did not provide a desc for their wish.")
    await update.message.reply_text(
        "No problem! Please review your wish before adding:[TODO]",
        reply_markup=ReplyKeyboardRemove(),
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
    del local_storage[user.id]
    logger.info(f"User {user.name} with id={user.id} canceled the conversation.")
    await update.message.reply_text(
        "Bye! Come back soon!", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main():
    application = ApplicationBuilder().token(WISHLIST_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ROLE_CHOICE: [MessageHandler(filters.Regex("^(Make a wish|See wishes|Edit wishes)$"), role_choice)],
            EDIT_WISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_wish)],
            NEW_WISH_NAME_REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_wish_name_request)],
            NEW_WISH_PHOTO_REQUEST: [MessageHandler(filters.PHOTO, new_wish_photo_request),
                                     MessageHandler(filters.Regex("^Skip$"), skip_photo),
                                     CommandHandler("skip", skip_photo)],
            NEW_WISH_PRICE_REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_wish_price_request),
                                     MessageHandler(filters.Regex("^Skip$"), skip_photo),
                                     CommandHandler("skip", skip_price)],
            NEW_WISH_DESC_REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_wish_desc_request),
                                    MessageHandler(filters.Regex("^Skip$"), skip_photo),
                                    CommandHandler("skip", skip_desc)],
            SEE_WISHES_FOR_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, see_wishes)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],

    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
