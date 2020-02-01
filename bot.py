import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
import html
import re
from config import CONFIG
from database import DBHelper
import deadline

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def add_old_listing(update, context, message):
    if("old_listings" not in context.chat_data):
        context.chat_data["old_listings"] = []
    context.chat_data["old_listings"].append(message.message_id)

def delete_old_listings(update, context):
    try:
        if ("old_listings" not in context.chat_data):
            context.chat_data["old_listings"] = []
        for m in context.chat_data["old_listings"]:
            context.bot.delete_message(chat_id=update.message.chat_id, message_id=m)
    except Exception as e:
        print(e)
    finally:
        context.chat_data["old_listings"] = []


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    msg = """Hi! I'm @{} and I'm here to help you keep track of deadlines.
Commands:
/newdl date time;comment – to insert a deadline
/remdl – to remove a deadline
/chkdl – to check deadlines""".format(context.bot.username)
    update.message.reply_text(msg)


def new_deadline(update, context):
    """Insert new deadline into deadline list"""
    db = DBHelper(CONFIG["db_name"])
    args = " ".join(context.args)
    try:
        dl = deadline.Deadline.parse(args)
        if dl.in_how_many_days() < -1:
            update.message.reply_text("You're a bit too late to submit something on {}".format(dl.time.strftime("%d %b %Y, %H:%M:%S")))
        else:
            # actually handle the deadline
            db.insert_deadline(update.effective_chat.id, dl)
            update.message.reply_text("Succesfully added {}".format(str(dl)))
    except ValueError as e:
        update.message.reply_text(str(e))

def check_deadline(update, context):
    db = DBHelper(CONFIG["db_name"])
    db.clear_old_deadlines()
    dls = db.fetch_deadlines(update.effective_chat.id)
    header = None
    message_string = "<b>Deadlines</b>\n"
    for _, dl in dls:
        if header != dl.friendly_date():
            header = dl.friendly_date()
            message_string += "\n<b>{}</b>\n".format(header)
        message_string += html.escape(str(dl))
        message_string += "\n"
    delete_old_listings(update, context)
    m=update.message.reply_html(message_string)
    add_old_listing(update, context, m)

CHOOSING = 0

def start_remove_deadline(update, context):
    db = DBHelper(CONFIG["db_name"])
    db.clear_old_deadlines()
    dls = db.fetch_deadlines(update.effective_chat.id)
    header = None
    message_string = "<b>Deadlines</b>\n"
    context.user_data["remove_list"] = {}
    for i, (dl_id, dl) in enumerate(dls):
        if header != dl.friendly_date():
            header = dl.friendly_date()
            message_string += "\n<b>{}</b>\n".format(header)
        message_string += "/{} {}".format(i+1, html.escape(str(dl)))
        context.user_data["remove_list"][i+1] = (dl_id, dl)
        message_string += "\n"
    m = update.message.reply_html(message_string)
    delete_old_listings(update, context)
    add_old_listing(update, context, m)
    return CHOOSING

def remove_deadline_by_index(update, context):
    db = DBHelper(CONFIG["db_name"])
    delete_old_listings(update, context)
    text = re.sub(r"/(\d+)(@{})?$".format(re.escape(context.bot.username)), r"\g<1>", update.message.text)
    try:
        index = int(text)
        dl_id, dl = context.user_data["remove_list"][index]
        db.delete_deadline(dl_id)
        update.message.reply_text(str(dl) +" removed!")
        check_deadline(update, context)
    except KeyError as ke:
        update.message.reply_text(str(index)+" not in list!")
    except ValueError as ve:
        update.message.reply_text(text+" is not a valid integer!")
    context.user_data["remove_list"] = None
    return -1

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    db = DBHelper(CONFIG["db_name"])
    db.setup()

    updater = Updater(CONFIG["bot_token"], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("newdl", new_deadline))
    dp.add_handler(CommandHandler("chkdl", check_deadline))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler("remdl", start_remove_deadline)],
        states={CHOOSING: [MessageHandler(Filters.regex(r"^/\d+(@shimekiribot)?$"),
                                          remove_deadline_by_index)]},
        fallbacks=[]
    ))

        # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
