from datetime import datetime
from telebot import types
from emoji import emojize

from app import bot, db
from models import User, Album


def check_user(user_info):
    user = User.query.filter_by(username=user_info.username).first()
    if user is None:
        user = init_user_db(user_info)
    return user


def add_to_favourite(query):
    try:
        user = check_user(query.from_user)
        album = Album.query.filter_by(id=user.current).first()
        if album is None:
            bot.answer_callback_query(query.id, 'Последний элемент', show_alert=False)
            raise Exception("'add_to_favourite (album not found)' error with '{}'")
        if album in user.albums:
            bot.answer_callback_query(query.id, 'Уже есть в вашем списке')
        else:
            user.albums.append(album)
            db.session.commit()
            bot.answer_callback_query(query.id, 'Добавленно в избранное', show_alert=False)
    except Exception as e:
        raise Exception("'add_to_favourite' error with '{}'".format(e))


def make_keyboard(download_url):
    keyboard = types.InlineKeyboardMarkup()
    prev_item = types.InlineKeyboardButton(text=emojize(':left_arrow:'), callback_data='back')
    download = types.InlineKeyboardButton(text=emojize(':down_arrow:'), url=download_url)
    favourite = types.InlineKeyboardButton(text=emojize(':star:', use_aliases=True), callback_data='favourite')
    next_item = types.InlineKeyboardButton(text=emojize(':right_arrow:'), callback_data='next')
    keyboard.row(prev_item, download, favourite, next_item)
    return keyboard


def init_user_db(user_info):
    try:
        user = User(chat_id=user_info.id,
                    username=user_info.username,
                    name=user_info.first_name
                    )
        user.connected_date = datetime.today()
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        raise Exception("'init_user_db' error with '{}'".format(e))
    return user


def show_post(user_info):
    user = check_user(user_info)
    album = Album.filter_by(id=user.current).first()
    return album if album else None


@bot.message_handler(commands=['start'])
def greeting(message):
    try:
        bot.send_message(message.chat.id, 'Привет, ' + message.from_user.first_name +
                         '!\nДля начала работы мне нужно сделать снимок.\n'
                         'Подожди немного и ты сможешь начать просмотр последних новинок!')
        check_user(message.from_user)
        bot.send_message(message.chat.id, 'Теперь можешь пользоваться всеми моими возможностями!')
    except Exception as e:
        if bot.debug():
            bot.msg_error(message.chat.id, e, message.text)


@bot.message_handler(commands=['show'])
def show_post(message):
    try:
        user = check_user(message.from_user)
        album = Album.query.filter_by(id=user.current).first()
        bot.send_post(message.chat.id, album,
                      reply_markup=make_keyboard(album.download_link))
    except Exception as e:
        if bot.debug():
            bot.msg_error(message.chat.id, e, message.text)


@bot.callback_query_handler(func=lambda call: True)
def button_click(call):
    try:
        if call.message:
            if call.data == "back":
                user = check_user(call.from_user)
                user.prev()
                album = Album.query.filter_by(id=user.current).first()
                bot.send_new_post(call.from_user.id, call.message.message_id, album,
                                  make_keyboard(album.download_link))
            elif call.data == "favourite":
                add_to_favourite(call)
            elif call.data == "next":
                user = check_user(call.from_user)
                user.next()
                album = Album.query.filter_by(id=user.current).first()
                bot.send_new_post(call.from_user.id, call.message.message_id, album,
                                  make_keyboard(album.download_link))
    except Exception as e:
        if bot.debug():
            bot.msg_error(call.message.chat.id, e, 'button {}'.format(call.data))
        bot.send_message(call.message.chat.id, 'Что-т пошло не так!')


@bot.message_handler(commands=['search'])
def search_song(message):
    try:
        text = message.text.split()
        text = '+'.join(text[1:len(message.text)])
        bot.send_message(message.chat.id, 'Мне нужна минутка, для того чтоб найти данные')
        bot.search.start(text)
        bot.send_message(message.chat.id, 'Найденно {} элементов по вашему запросу'.format(bot.search.result))
        bot.send_post(message.chat.id, bot.search.parser.items[0])

    except Exception as e:
        if bot.debug():
            bot.msg_error(message.chat.id, e, message.text)


@bot.message_handler(commands=['favourite'])
def favourite_list(message):
    try:
        user = check_user(message.from_user)
        bot.send_message(message.chat.id, user.favourite_list())
    except Exception as e:
        if bot.debug():
            bot.msg_error(message.chat.id, e, message.text)


@bot.message_handler(content_types=['text'])
def send_message(message):
    bot.send_message(message.chat.id, 'Я не против поговорить, но сейчас я не разговорчив. ' +
                     emojize(':zipper-mouth_face:'))
