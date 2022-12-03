import logging
import os
from typing import Dict

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ApplicationBuilder
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from db import create_tables_dict, TableName
from wishdata import WishData

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

WISHLIST_BOT_TOKEN = os.environ["WISHLIST_BOT_TOKEN"]
ROLE_CHOICE, MAKE_A_WISH, SEE_WISHES_FOR_USER, NEW_WISH_NAME_REQUEST, NEW_WISH_PHOTO_REQUEST, \
NEW_WISH_PRICE_REQUEST, EDIT_WISH, ADD_NAME, ADD_PHOTO, NEW_WISH_DESC_REQUEST, NEW_WISH_CONFIRMATION, \
BACK_TO_MAIN, WHOSE_LIST = range(13)

wish_dict: Dict[int, WishData] = dict()

tables = create_tables_dict()

skip_keyboard = [["Skip"]]
back_main_keyboard = [["Back to main menu"]]
skip_markup = ReplyKeyboardMarkup(skip_keyboard, one_time_keyboard=True)
back_markup = ReplyKeyboardMarkup(back_main_keyboard, one_time_keyboard=True)


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
    logger.info(f"Role of {user.name}: {update.message.text}")

    choice = update.message.text

    if choice == "Make a wish":
        await update.message.reply_text(
            f"What do you wish?",
        )
        wish_dict[user.id] = WishData(creator_name=user.username, booked=False, presented=False)
        return NEW_WISH_NAME_REQUEST
    elif choice == "See wishes":
        await update.message.reply_text(
            "Please type a target username",
        )
        return WHOSE_LIST
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
    logger.info(f"User {user.name} requested a list of wishes for {update.message.text}")

    logger.info(f"found: {tables[TableName.WISH].search_by_creator(creator_name=update.message.text)}")
    # TODO add other properties
    #  with picture reverting bytearray

    await update.message.reply_text(
        f"[TODO] Showing wishes for {update.message.text}\n\n"
    )
    return ConversationHandler.END


async def new_wish_name_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    wish_name = update.message.text
    username = update.message.from_user.username
    logger.info(f"user {username} wants a {wish_name}")
    user_id = update.message.from_user.id

    tmp_wish: WishData = wish_dict[user_id]
    tmp_wish.name = wish_name

    await update.message.reply_text(
        f"Ok, you want a {wish_name}.\n\nDo you have a picture of it?",
        reply_markup=skip_markup,
    )
    return NEW_WISH_PHOTO_REQUEST


async def new_wish_photo_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    buf = bytearray()
    await photo_file.download_as_bytearray(buf=buf)

    tmp_wish: WishData = wish_dict[user.id]
    tmp_wish.photo = buf

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

    tmp_wish = wish_dict[user.id]
    tmp_wish.price = wish_price

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

    tmp_wish = wish_dict[user.id]
    tmp_wish.desc = desc

    wish_confirmation_keyboard = [["Reject", "Confirm"]]
    wish_confirmation_markup = ReplyKeyboardMarkup(wish_confirmation_keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        f"Please review your wish before adding:\n\n{tmp_wish}",
        reply_markup=wish_confirmation_markup
    )
    return NEW_WISH_CONFIRMATION


async def check_who(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(f"User {user.name} finds a friend's list")
    # TODO check if the name exists in the DB
    await update.message.reply_text(
        "This user has not created a list so far. Please try again",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def skip_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(f"User {user.name} did not provide a desc for their wish.")
    wish = wish_dict[user.id]

    wish_confirmation_keyboard = [["Reject", "Confirm"]]
    wish_confirmation_markup = ReplyKeyboardMarkup(wish_confirmation_keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        f"No problem! Please review your wish before adding:\n\n{wish}",
        reply_markup=wish_confirmation_markup,
    )
    return NEW_WISH_CONFIRMATION


async def new_wish_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    user = update.message.from_user

    reply_keyboard = [["Make a wish", "See wishes", "Edit wishes"]]

    if choice == "Confirm":
        wish = wish_dict[user.id]
        tables[TableName.WISH].add(user.username, wish.name)
        await update.message.reply_text(
            f"Your wish is saved!",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Wish or search?"
            ),
        )
    elif choice == "Reject":
        await update.message.reply_text(
            f"Your wish is discarded",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Wish or search?"
            ),
        )
    return ROLE_CHOICE


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
    del wish_dict[user.id]
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
                                     MessageHandler(filters.Regex("^Skip$"), skip_price),
                                     CommandHandler("skip", skip_price)],
            NEW_WISH_DESC_REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_wish_desc_request),
                                    MessageHandler(filters.Regex("^Skip$"), skip_desc),
                                    CommandHandler("skip", skip_desc)],
            SEE_WISHES_FOR_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, see_wishes)],
            NEW_WISH_CONFIRMATION: [
                MessageHandler(filters.Regex("^(Confirm|Reject)$"), new_wish_confirmation)
            ],

            WHOSE_LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_who)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
