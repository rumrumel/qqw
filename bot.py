# from msilib.schema import Error
import sqlite3
import telebot
import config
import random
import copy

from telebot import types

bot = telebot.TeleBot(config.TOKEN)

sqlite_connection = sqlite3.connect('final.db', check_same_thread=False)


def user_exists(user_id):
    cursor = sqlite_connection.cursor()
    result = cursor.execute("SELECT 'id' FROM 'users' WHERE user_id = ?", (user_id,))
    return bool(len(result.fetchall()))


def get_user_id(user_id):
    cursor = sqlite_connection.cursor()
    result = cursor.execute("SELECT 'id' FROM 'users' WHERE user_id = ?", (user_id,))
    return result.fetchone()[0]


def add_user(user_id):
    cursor = sqlite_connection.cursor()
    cursor.execute("INSERT INTO 'users' ('user_id') VALUES (?)", (user_id,))
    return sqlite_connection.commit()


def add_record(user_id, name):
    cursor = sqlite_connection.cursor()
    cursor.execute("INSERT INTO 'records' ('users_id', 'name') VALUES (?, ?)", (name, user_id))
    return sqlite_connection.commit()


def How_much(user_id):
    cursor = sqlite_connection.cursor()
    cursor.execute("select count(*) from 'records' WHERE users_id = ?", (user_id,))
    result, = cursor.fetchone()
    return result


def New_game(user_id):
    cursor = sqlite_connection.cursor()
    cursor.execute("DELETE FROM 'records' WHERE users_id = ?", (user_id,))
    return sqlite_connection.commit()


def read_row(user_id):
    cursor = sqlite_connection.cursor()
    cursor.execute("SELECT * FROM 'records' where users_id = ?", (user_id,))
    record = cursor.fetchall()
    return (record[-1][-1])


def Is_there(text):
    cursor = sqlite_connection.cursor()
    name = text
    cursor.execute("SELECT rowid FROM 'main' WHERE name = ?", (name,))
    data = cursor.fetchone()
    if data is None:
        x = 0
    else:
        x = 1
    return x


def Was(text, user_id):
    cursor = sqlite_connection.cursor()
    name = text
    cursor.execute("SELECT rowid FROM 'records' WHERE name = ? AND users_id = ?", (name, user_id,))
    data = cursor.fetchone()
    if data is None:
        x = 0
    else:
        x = 1
    return x


def Print_answer(user_id):
    cursor = sqlite_connection.cursor()
    cursor.execute("select * from 'records' WHERE users_id = ?", (user_id,))
    id_last_word = How_much(user_id)
    z = cursor.fetchall()
    last_word = z[id_last_word - 1][2]

    cursor = sqlite_connection.cursor()
    cursor.execute("select * from 'main'")
    result = cursor.fetchall()
    cursor.close()

    if last_word[-1] == 'ь' or last_word[-1] == 'ъ' or last_word[-1] == 'ы':
        for x in result:
            if last_word[-2].upper() == x[1][0] and Was(x[-2], user_id) == 0:
                return x[1]
    else:
        for x in result:
            if last_word[-1].upper() == x[1][0] and Was(x[-1], user_id) == 0:
                return x[1]


@bot.message_handler(commands=['start'])
def welcome(message):
    if (not user_exists(message.chat.id)):
        add_user(message.chat.id)

    sti = open('./hello.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)

    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("начать игру")
    item2 = types.KeyboardButton("закончить игру")

    markup.add(item1, item2)
    bot.send_message(message.chat.id,"привет, {0.first_name}! меня зовут '{1.first_name}'. \nя создан для того, чтобы играть в слова в тематике аниме-сериалов. поиграем?".format(message.from_user, bot.get_me()), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def lalala(message):
    if message.text != 'начать игру' and message.text != 'закончить игру' and (
            Is_there(message.text + '\n') or Is_there(message.text) == 0):
        bot.send_message(message.chat.id, "прости, я не знаю такого аниме. можешь назвать другое?")

    elif message.text != 'начать игру' and message.text != 'закончить игру' and (
            Was(message.text + '\n', message.chat.id) == 1 or Was(message.text, message.chat.id) == 1):
        bot.send_message(message.chat.id, "такое аниме уже было. можешь назвать другое?")

    elif message.text == 'начать игру':
        sti = open('./lets_start.webp', 'rb')
        bot.send_sticker(message.chat.id, sti)
        bot.send_message(message.chat.id, "ты начинаешь! назови любое название аниме.")
        # Очистить бд использованных слов
        New_game(message.chat.id)

    elif message.text == 'закончить игру':
        sti = open('./bye.webp', 'rb')
        bot.send_sticker(message.chat.id, sti)
        bot.send_message(message.chat.id, "спасибо за игру. надеюсь, тебе понравилось и ты узнал для себя больше новых аниме.")
        # Очистить бд использованных слов
        New_game(message.chat.id)

    elif How_much(message.chat.id) != 0 and message.text[0].upper() != read_row(message.chat.id)[-1].upper() and \
            read_row(message.chat.id)[-1].upper() != 'Ъ' and read_row(message.chat.id)[-1].upper() != 'Ь' and read_row(message.chat.id)[-1].upper() != 'Ы':
        bot.send_message(message.chat.id, "похоже, что ты сказал название аниме не на ту букву.")

    elif How_much(message.chat.id) != 20000:
        # print(message.chat.id)
        add_record(message.text, message.chat.id)
        x = Print_answer(message.chat.id)
        bot.send_message(message.chat.id, x)
        add_record(x, message.chat.id)

    else:
        bot.send_message(message.chat.id, "поздравляю, ты победил! \nчтобы начать новую игру нажми 'начать игру'")


# RUN
bot.polling(none_stop=True)