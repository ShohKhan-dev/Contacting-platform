# Example code for telegrambot.py module
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
from django_telegrambot.apps import DjangoTelegramBot
from telegram import Update, Bot, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove

from .models import Conversation, ConversationMessage, User, Notification

# from django.contrib.auth.models import User


from django.conf import settings

import io
import requests


import logging
logger = logging.getLogger(__name__)


FirstName, LastName, InnoEmail, COURSE, LOCATION, CONFIRMATION = range(6)

def start(update, context):

    user = update.message.from_user

    if User.objects.filter(username = user.id).exists():
        User.objects.filter(username = user.id).update(username=user.id, telegram_first_name=user.first_name, telegram_last_name=user.last_name, telegram_username=user.username)
    else:
        User.objects.create_user(username=user.id, telegram_first_name=user.first_name, telegram_last_name=user.last_name, telegram_username=user.username)

    update.message.reply_text('Welcome to Innopolis Contact Bot. \nYou can contact with Student Affairs via this bot. \nYou need to tell us some of your infromation!\n\nFirst, what is your First Name?')
    
    return FirstName


def first_name(update, context):
    user = update.message.from_user

    if update.message.text:
        User.objects.filter(username = user.id).update(first_name=update.message.text)
    
    print("First Name of {} is {}".format(user.first_name, update.message.text))
    
    update.message.reply_text('I see! Please tell me your Last Name.')

    return LastName


def last_name(update, context):

    user = update.message.from_user

    if update.message.text:
        User.objects.filter(username = user.id).update(last_name=update.message.text)

    print("Last Name of {} is {}".format(user.first_name, update.message.text))
    update.message.reply_text('I see! Please tell me your Innopolis Email now.')

    return InnoEmail


def inno_email(update, context):

    user = update.message.from_user

    reply_keyboard = [['International', 'Russian', 'CIS']]

    if update.message.text:
        User.objects.filter(username = user.id).update(inno_email=update.message.text)


    message = "Ok, Please tell me what type of student you are?"

    # print("Innopolis Email of {} is {}".format(user.first_name, update.message.text))

    update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return LOCATION


def location(update, context):

    reply_keyboard = [['Bachelor 1st', 'Bachelor 2nd'], 
                      ['Bachelor 3rd', 'Bachelor 4th'], 
                      ['Master 1st', 'Master 2nd', 'Phd']]

    user = update.message.from_user

    if update.message.text and update.message.text in ['International', 'Russian', 'CIS']:

        User.objects.filter(username = user.id).update(location=update.message.text)

    message = "I see, Please tell me which course do you study in?"

    update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


    return COURSE


def course(update, context):

    user = update.message.from_user

    reply_keyboard = [['Yes', 'No']]

    courses = ['Bachelor 1st', 'Bachelor 2nd', 'Bachelor 3rd', 'Bachelor 4th', 'Master 1st', 'Master 2nd', 'Phd']

    if update.message.text and update.message.text in courses:

        User.objects.filter(username = user.id).update(course=update.message.text)

    cur_user = User.objects.get(username=user.id)

    message = "First name: "+cur_user.first_name + "\nLast name: " + cur_user.last_name + "\nEmail: " + cur_user.inno_email \
        + "\nType: "+cur_user.location + "\nCourse: "+cur_user.course + "\n\nIs all Information Correct?"

    # print("Innopolis Email of {} is {}".format(user.first_name, update.message.text))

    update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return CONFIRMATION

    

def confirm(update, context):

    user = update.message.from_user

    if update.message.text == "Yes":

        update.message.reply_text('Thank you for you Informations! Our team will review your Infromation soon and confirms for safety!',
                              reply_markup=ReplyKeyboardRemove())
        
        cur_user = User.objects.get(username = update.message.from_user.id)

        admin = User.objects.filter(is_superuser=True)[0]

        Notification.objects.create(to_user=admin, notification_type='new_join', created_by=cur_user)


        return ConversationHandler.END
    

    update.message.reply_text('Ok, Now, Enter your Informations from beginning. \n\nWhat is your First Name?',
                              reply_markup=ReplyKeyboardRemove())

    return FirstName

    
                            

def cancel(update, context):
    user = update.message.from_user
    print("User {} canceled the conversation.".format(user.first_name))
    update.message.reply_text('Bye! I hope we can talk again some day.')

    return ConversationHandler.END

# def help(bot, update):
#     bot.sendMessage(update.message.chat_id, text='Help!')

# def echo(bot, update):
#     bot.sendMessage(update.message.chat_id, text=update.message.text)

def send_message(message, user_id):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    # print(message)
    # print(user_id)
    # print(type(user_id))
    # if not user_id:
    #     user_id = settings.DJANGO_TELEGRAMBOT['TELEGRAM_BOT_ADMIN']
    return bot.send_message(chat_id=user_id, text=message)


def request_new_info(user_id):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    message = "Your data is not confirmed! Please update your information ASAP using /config command!"

    # print(message)
    # print(user_id)
    # print(type(user_id))
    # if not user_id:
    #     user_id = settings.DJANGO_TELEGRAMBOT['TELEGRAM_BOT_ADMIN']
    return bot.send_message(chat_id=user_id, text=message)


def reply_to_message(message, message_id, user_id):
    bot = Bot(token=settings.DJANGO_TELEGRAMBOT['BOTS'][0]['TOKEN'])
    return bot.send_message(chat_id=user_id, text=message, reply_to_message_id=message_id)


def forward_message(from_user_id, message_id, user_id=None):
    bot = Bot(token=settings.DJANGO_TELEGRAMBOT['BOTS'][0]['TOKEN'])
    if not user_id:
        user_id = settings.DJANGO_TELEGRAMBOT['TELEGRAM_BOT_ADMIN']
    return bot.forward_message(user_id, from_user_id, message_id)
    

def send_photo(photo, caption, remote=True, user_id=None):
    bot = Bot(token=settings.DJANGO_TELEGRAMBOT['BOTS'][0]['TOKEN'])
    if not user_id:
        user_id = settings.DJANGO_TELEGRAMBOT['TELEGRAM_BOT_ADMIN']
    if remote:
        remote_image = requests.get(photo)
        photo = io.BytesIO(remote_image.content)
    return bot.send_photo(chat_id=user_id, photo=photo, caption=caption)


def command_help(update, context):
    update.message.reply_text("Assalomu alaykum, \n\nAgar ma'lumot izlamoqchi bo'lsangiz orginfo.uz dan izlang", parse_mode=ParseMode.MARKDOWN)


def get_user_response(update, context):
    text = update.message.text

    user = User.objects.get(username = update.message.from_user.id)

    if not user.inno_email:
        update.message.reply_text('Sorry! You need to update your information first with /config command!')
    
    else:
        admin = User.objects.filter(is_superuser=True)[0]

        conversations = Conversation.objects.filter(users__in=[admin.id])
        conversations = conversations.filter(users__in=[user.id])

        if conversations.count() == 1:
            conversation = conversations[0]
        else:
            recipient = User.objects.get(id=user.id)
            conversation = Conversation.objects.create()
            conversation.users.add(admin)
            conversation.users.add(recipient)
            conversation.save()

        ConversationMessage.objects.create(conversation=conversation, content=text, created_by=user)

        Notification.objects.create(to_user=admin, notification_type='message', created_by=user)

        
        update.message.reply_text('Hello! \nThank you for your message! The employee will proceed it soon.')

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    logger.info("Loading handlers for telegram bot")

    # Default dispatcher (this is related to the first bot in settings.DJANGO_TELEGRAMBOT['BOTS'])
    dp = DjangoTelegramBot.dispatcher
    # To get Dispatcher related to a specific bot
    # dp = DjangoTelegramBot.getDispatcher('BOT_n_token')     #get by bot token
    # dp = DjangoTelegramBot.getDispatcher('BOT_n_username')  #get by bot username


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('config', start)],

        states={
            FirstName: [MessageHandler(Filters.text, first_name)],

            LastName: [MessageHandler(Filters.text, last_name)],

            InnoEmail: [MessageHandler(Filters.text, inno_email)],

            LOCATION: [MessageHandler(Filters.regex('^(International|Russian|CIS)$'), location)],

            COURSE: [MessageHandler(Filters.regex('^(Bachelor 1st|Bachelor 2nd|Bachelor 3rd|Bachelor 4th|Master 1st|Master 2nd|Phd)$'), course)],

            CONFIRMATION: [MessageHandler(Filters.regex('^(Yes|No)$'), confirm)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler("help", command_help,  Filters.text))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, get_user_response))


    # log all errors
    dp.add_error_handler(error)