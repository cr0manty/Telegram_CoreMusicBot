from datetime import datetime
from telebot import types
from emoji import emojize

from app import bot, db
from models import User, Album


def add_to_favourite(user_info):
    try:
        user = User.query.filter_by(username=user_info.username).first()
        if user is None:
            init_user_db(user_info)
        album = Album(bot.get_item())
        if album in user.albums:
            bot.answer_callback_query(user_info.id, 'Уже есть в вашем списке', show_alert=False)
        else:
            user.albums.append(album)
            db.session.commit()
            bot.answer_callback_query(user_info.id, 'Добавленно в избранное', show_alert=False)
    except Exception as e:
        raise Exception("'add_to_favourite' error with '{}'".format(e))


def make_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    prev_item = types.InlineKeyboardButton(text=emojize(':left_arrow:'), callback_data='back')
    download = types.InlineKeyboardButton(text=emojize(':down_arrow:'), url=bot.get_item().get('download'))
    favourite = types.InlineKeyboardButton(text=emojize(':star:', use_aliases=True), callback_data='favourite')
    next_item = types.InlineKeyboardButton(text=emojize(':right_arrow:'), callback_data='next')
    keyboard.row(prev_item, download, favourite, next_item)
    return keyboard


def init_user_db(user_info):
    try:
        user = User.query.filter_by(username=user_info.username).first()
        if user is None:
            user = User(chat_id=user_info.id,
                        username=user_info.username,
                        name=user_info.first_name,
                        )
        user.last_update = datetime.today()
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        raise Exception("'init_user_db' error with '{}'".format(e))
    return user


@bot.message_handler(commands=['start'])
def greeting_msg(message):
    try:
        bot.send_message(message.chat.id, 'Привет, ' + message.from_user.first_name +
                         '!\nДля начала работы мне нужно сделать снимок.\n'
                         'Подожди немного и ты сможешь начать просмотр последних новинок!')
        init_user_db(message.from_user)
        bot.send_message(message.chat.id, 'Теперь можешь пользоваться всеми моими возможностями!')
    except Exception as e:
        if bot.debug():
            bot.msg_error(message.chat.id, e, message.text)


@bot.message_handler(commands=['show'])
def greeting_msg(message):
    try:
        bot.send_post(message.chat.id, bot.get_item(), reply_markup=make_keyboard())
    except Exception as e:
        if bot.debug():
            bot.msg_error(message.chat.id, e, message.text)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == "back":
                if bot.index > 0:
                    bot.index -= 1
                    bot.send_new_post(call.from_user.id, call.message.message_id, make_keyboard())
            elif call.data == "favourite":
                add_to_favourite(call.from_user)
            elif call.data == "next":
                if bot.index < 19:
                    bot.index += 1
                    bot.send_new_post(call.from_user.id, call.message.message_id, make_keyboard())
    except Exception as e:
        if bot.debug():
            bot.msg_error(call.message.chat.id, e, 'button {}'.format(call.data))


@bot.message_handler(commands=['search'])
def search_song(message):
    pass


@bot.message_handler(commands=['favourite'])
def favourite_list(message):
    try:
        user = User.query.filter_by(username=message.chat.username).first()
        bot.send_message(message.chat.id, user.favourite_list())
    except Exception as e:
        if bot.debug():
            bot.msg_error(message.chat.id, e, message.text)


@bot.message_handler(content_types=['text'])
def send_message(message):
    bot.send_message(message.chat.id, 'Я не против поговорить, но сейчас я разговорчив. ' +
                     emojize(':zipper-mouth_face:'))
