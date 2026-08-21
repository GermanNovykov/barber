import telebot
import config
import datetime
import time
from telebot import types
from salondb import Sqlight

from telegram_bot_calendar import WYearTelegramCalendar
from apscheduler.schedulers.background import BackgroundScheduler


MyStep = {'y': 'год', 'm': 'месяц', 'd': 'день'}
# создание бота

bot = telebot.TeleBot(config.TOKEN)





#1st - mastername, 2nd - mastersurname, 3rd - date, 4th - time, 5th - username, 6th - userphone, 7th - procedura
#b = []


def klientreg1(message):
    #b.append(message.text)
    db = Sqlight('db.db')
    db.temp_addusername(message.chat.id, message.text)
    bot.send_message(message.chat.id, 'Теперь введите номер телефона')
    bot.register_next_step_handler(message, klientreg2)

def klientreg2(message):
    db = Sqlight('db.db')
    db.temp_adduserphone(message.chat.id, message.text)
    #bot.edit_message_text(f'Вы записались на дату {b[2]}, {b[3]}, процедура - {g[0]}', message.chat.id, message.message_id)
    bot.send_message(message.chat.id, f'Вы записались на дату {db.temp_selectdate(message.chat.id)}, {db.temp_selecttime(message.chat.id)}, процедура - {db.temp_selectprocedura(message.chat.id)}')


    #делаем проверку?
    db.add_klient(message.chat.id, db.temp_selectusername(message.chat.id), db.temp_selectuserphone(message.chat.id))

    db.zapis(db.temp_selectmastername(message.chat.id), db.temp_selectmastersurname(message.chat.id), db.temp_selectdate(message.chat.id), db.temp_selecttime(message.chat.id), db.temp_selectusername(message.chat.id), db.temp_selectuserphone(message.chat.id), db.temp_selectprocedura(message.chat.id))
    bot.send_message(db.select_all_masters_by_name(db.temp_selectmastername(message.chat.id), db.temp_selectmastersurname(message.chat.id))[0][1], f'Клиент под именем {db.temp_selectusername(message.chat.id)} и с номером телефона {db.temp_selectuserphone(message.chat.id)} записался на {db.temp_selectdate(message.chat.id)} {db.temp_selecttime(message.chat.id)}, процедура - {db.temp_selectprocedura(message.chat.id)}')



def codeproc(message):
    if message.text == str(secretcode):
        markup = types.InlineKeyboardMarkup(row_width=1)

        item1 = types.InlineKeyboardButton('Мастер маникюра', callback_data='codemanik')
        item2 = types.InlineKeyboardButton('Парикмахер', callback_data='codepar')
        item3 = types.InlineKeyboardButton('Косметолог', callback_data='codecosm')
        markup.add(item1, item2, item3)

        bot.send_message(message.chat.id, 'Вы успешно ввели код, выберите специальность', reply_markup=markup)

def mastereg1(message, spec):
    #proc imya mastera
    name = message.text


    bot.send_message(message.chat.id, 'Введите фамилию:')

    bot.register_next_step_handler(message, mastereg2, spec, name)

def mastereg2(message, spec, name):
    #proc surname
    surname = message.text

    # add to database
    db = Sqlight('db.db')

    db.add_master(message.chat.id, name, surname, spec)
    bot.send_message(message.chat.id, f'Ваше имя - {name}, фамилия - {surname}')


#start
@bot.message_handler(commands=['start'])
def startmenu(message):
    markup2 = types.ReplyKeyboardMarkup()
    db = Sqlight('db.db')
    db.temp_adduser_id(message.chat.id)
    markup2.add('Записаться', 'Мои записи', 'Меню мастера', row_width=1)

    bot.send_message(message.chat.id, 'Здравствуйте, это бот, который может записать вас в салон', reply_markup=markup2)

#starttextproc
@bot.message_handler()
def keyboardproc(message):
    db = Sqlight('db.db')

    if message.text == 'Записаться':
        markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton('Ногтевой сервис', callback_data='nogtserv')
        item2 = types.InlineKeyboardButton('Брови и ресницы', callback_data='brovserv')

        markup.add(item1, item2)
        #bot.edit_message_text('Выберите сервис', call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.send_message(message.chat.id, 'Выберите сервис', reply_markup=markup)

    elif message.text == 'Мои записи':
        if db.find_klient_by_id(message.chat.id):
            klient = db.find_klient_by_id(message.chat.id)[0]
            name = klient[2]
            phone = klient[3]
            markup = types.InlineKeyboardMarkup(row_width=1)
            if db.select_zapisi_from_klient(name, phone):
                n = 0
                for i in db.select_zapisi_from_klient(name, phone):
                    p = types.InlineKeyboardButton(f'Дата - {i[1]}, {i[2]}, мастер - {i[3]} {i[4]}, процедура - {i[7]}',
                                                   callback_data=f'moizapisi{str(n)}')
                    markup.add(p)
                    n += 1

                else:

                    bot.send_message(message.chat.id, 'Тут вы можете посмотреть свои записи', reply_markup=markup)
                    db.temp_addusername(message.chat.id, name)
                    db.temp_adduserphone(message.chat.id, phone)
            else:
                item1 = types.InlineKeyboardButton('Записатсься', callback_data='startzapis')
                markup.add(item1)

                bot.send_message(message.chat.id, 'У вас нету записей', reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup(row_width=1)
            item1 = types.InlineKeyboardButton('Записатсься', callback_data='startzapis')
            markup.add(item1)
            bot.send_message(message.chat.id, 'У вас нету записей', reply_markup=markup)


    elif message.text == 'Меню мастера':
        if not bool(db.master_exists(message.chat.id)):

            bot.send_message(message.chat.id, 'Введите код:')
            bot.register_next_step_handler(message, codeproc)

        else:
            master = db.master_exists(message.chat.id)[0]
            markup = types.InlineKeyboardMarkup(row_width=1)

            item1 = types.InlineKeyboardButton('Просмотреть полный календарь моих записей', callback_data='fullcalendar')
            item2 = types.InlineKeyboardButton('Просмотреть календари других мастеров', callback_data='otherscalendar')
            item3 = types.InlineKeyboardButton('Стереть эту учетную запись', callback_data='masterdelete')
            #D List
            #d.append(db.master_exists(message.chat.id)[0][2:4])
            db.temp_addmastername(message.chat.id, db.master_exists(message.chat.id)[0][2])
            db.temp_addmastersurname(message.chat.id, db.master_exists(message.chat.id)[0][3])
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, f'Добро пожаловать, {master[2]} {master[3]}', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ['startzapis', 'moizapisi', 'nogtserv', 'brovserv', 'codestart', 'otherscalendar', 'othermasterback', 'masterdelete'])
def startproc(call):
    if call.data == 'startzapis':

        markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton('Ногтевой сервис', callback_data='nogtserv')
        item2 = types.InlineKeyboardButton('Брови и ресницы', callback_data='brovserv')

        markup.add(item1, item2)
        bot.edit_message_text('Выберите сервис', call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == 'moizapisi':
        #Показать записи как кнопки
        db = Sqlight('db.db')

        if db.find_klient_by_id(call.message.chat.id):
            klient = db.find_klient_by_id(call.message.chat.id)[0]
            name = klient[2]
            phone = klient[3]
            markup = types.InlineKeyboardMarkup(row_width=1)
            if db.select_zapisi_from_klient(name, phone):
                n = 0
                for i in db.select_zapisi_from_klient(name, phone):
                    p = types.InlineKeyboardButton(f'Дата - {i[1]}, {i[2]}, мастер - {i[3]} {i[4]}, процедура - {i[7]}', callback_data=f'moizapisi{str(n)}')
                    markup.add(p)
                    n += 1

                else:
                    mal = types.InlineKeyboardButton('Назад', callback_data='moizapisiback')
                    markup.add(mal)
                    bot.edit_message_text('Тут вы можете посмотреть свои записи', call.message.chat.id, call.message.message_id, reply_markup=markup)
                    db.temp_addusername(call.message.chat.id, name)
                    db.temp_adduserphone(call.message.chat.id, phone)
                    #j list
            else:
                item1 = types.InlineKeyboardButton('Записатсься', callback_data='startzapis')
                markup.add(item1)

                bot.edit_message_text('У вас нету записей', call.message.chat.id, call.message.message_id, reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup(row_width=1)
            item1 = types.InlineKeyboardButton('Записатсься', callback_data='startzapis')
            markup.add(item1)
            bot.edit_message_text('Вы не зарегистрированы', call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == 'otherscalendar':
        markup = types.InlineKeyboardMarkup(row_width=1)
        db = Sqlight('db.db')
        for i in db.select_all_masters():
            if str(call.message.chat.id) != i[1]:
                ink = types.InlineKeyboardButton(f'{i[2]} {i[3]}', callback_data=f'othermaster{str(i[0])}')
                markup.add(ink)
        else:
            back = types.InlineKeyboardButton('Назад', callback_data='othermasterback')
            markup.add(back)

        bot.edit_message_text('Выберите мастера', call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == 'othermasterback':
        db = Sqlight('db.db')
        master = db.master_exists(call.message.chat.id)[0]
        markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton('Просмотреть полный календарь моих записей', callback_data='fullcalendar')
        item2 = types.InlineKeyboardButton('Просмотреть календари других мастеров', callback_data='otherscalendar')
        item3 = types.InlineKeyboardButton('Стереть эту учетную запись', callback_data='masterdelete')
#        d.append(db.master_exists(call.message.chat.id)[0][2:4])
        db.temp_addmastername(call.message.chat.id, db.master_exists(call.message.chat.id)[0][2])
        db.temp_addmastersurname(call.message.chat.id, db.master_exists(call.message.chat.id)[0][3])

        markup.add(item1, item2, item3)
        bot.edit_message_text(f'Добро пожаловать, {master[2]} {master[3]}', call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif call.data == 'nogtserv':

        markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton('Маникюр', callback_data='manik')
        item2 = types.InlineKeyboardButton('Педикюр', callback_data='ped')



        back = types.InlineKeyboardButton('Назад', callback_data='startzapis')
        markup.add(item1, item2, back)

        bot.edit_message_text('Выберите процедуру', call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif call.data == 'masterdelete':
        bot.edit_message_text('Вы уверенны что хотите стереть эту учетную запись мастера? Напишите Да или Нет', call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, deletemaster)


def deletemaster(message):
    if str(message.text).lower() == 'да':
        db = Sqlight('db.db')
        db.delete_master_by_userid(message.chat.id)
        bot.send_message(message.chat.id, 'Учетная запись мастера удалена')



@bot.callback_query_handler(func=lambda call: call.data in [f'othermaster{str(x[0])}' for x in Sqlight('db.db').select_all_masters()])
def othermasterproc(call):
    db = Sqlight('db.db')
    masterid = str(call.data).replace('othermaster', '')
    master = db.select_master_by_id(masterid)
    db.temp_addmastername(call.message.chat.id, master[0][2])
    db.temp_addmastersurname(call.message.chat.id, master[0][3])
    calendar, step = WYearTelegramCalendar(calendar_id=3, locale='ru', min_date=datetime.date.today()).build()
    bot.edit_message_text(f"Выберите {MyStep[step]}", call.message.chat.id, call.message.message_id, reply_markup=calendar)

@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id=3))
def othercalendar(c):

    db = Sqlight('db.db')
    result, key, step = WYearTelegramCalendar(calendar_id=3, locale='ru', min_date=datetime.date.today()).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {MyStep[step]}",
                                c.message.chat.id,
                                c.message.message_id,
                                reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                                c.message.chat.id,
                                c.message.message_id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        n = 9
        for i in range(7):
            if db.check_zapis_time_u_mastera(db.temp_selectmastername(c.message.chat.id),
                                             db.temp_selectmastersurname(c.message.chat.id), result,
                                             f'{str(n)}:00') == True:
                p = db.get_zapis_from_master_and_time(db.temp_selectmastername(c.message.chat.id),
                                                      db.temp_selectmastersurname(c.message.chat.id), result,
                                                      f'{str(n)}:00')[0]
                i = types.InlineKeyboardButton(
                    f'Время - {p[2]}, Имя клиента - {p[5]}, телефон клиента - {p[6]}, процедура - {p[7]}',
                    callback_data=f'ortherzapis{str(i)}')
                n += 2
                markup.add(i)
            else:
                i = types.InlineKeyboardButton(f'{str(n)}:00', callback_data=f'{str(n)}:00menuohter')
                n += 2
                markup.add(i)

        bot.send_message(c.message.chat.id, 'Вы можете выбрать одну из записей и взаемодействовать с нею',
                         reply_markup=markup)
    #Показать время для записи





@bot.callback_query_handler(func=lambda call: call.data in ['9:00menuother', '11:00menuother', '13:00menuother', '15:00menuother', '17:00menuother', '19:00menuother', '21:00menuother'])
def othermastertimeproc(call):
    time = str(call.data).replace('menuother', '')
    #h.append(time)
    db = Sqlight('db.db')
    db.temp_addtime(call.message.chat.id, time)
    markup = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton('Создать запись', callback_data='menucreatezapis')
    markup.add(item1)
    bot.send_message(call.message.chat.id, f'Время - {time}, Вы можете создать запись здесь', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['manik', 'ped'])
def procedurproc(call):
    db = Sqlight('db.db')
    if call.data == 'manik':
        spec = 'Мастер маникюра'
        #g.append('Маникюр')
        db.temp_addprocedura(call.message.chat.id, 'Маникюр')
        kind = 'manikmaster'
        back = 'nogtserv'
    elif call.data == 'ped':
        spec = 'Мастер маникюра'
        #g.append('Педикюр')
        db.temp_addprocedura(call.message.chat.id, 'Педикюр')
        kind = 'manikmaster'
        back = 'nogtserv'

    masters = db.select_all_masters_by_spec(spec)
    result = []
    for i in masters:
        result.append(i[2])
        result.append(i[3])

    markup = types.InlineKeyboardMarkup(row_width=1)
    n = 0

    for i in range(len(db.select_all_masters_by_spec(spec))):

        ink = types.InlineKeyboardButton(str(result[n:n + 2]).replace('[', '').replace(']', '').replace('\'', '').replace(',', ''), callback_data=f'{kind}{str(i)}')
        markup.add(ink)
        n += 2
    else:
        dd = types.InlineKeyboardButton('Назад', callback_data=back)
        markup.add(dd)
    bot.edit_message_text('Выберите мастера:', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in [f'manikmaster{str(x)}' for x in range(len(Sqlight('db.db').select_all_masters_by_spec('Мастер маникюра')))])
def manikmasterproc(call):
    db = Sqlight('db.db')
    ind = int(str(call.data).replace('manikmaster', ''))
    calendar, step = WYearTelegramCalendar(calendar_id=1, locale='ru', min_date=datetime.date.today()).build()
    #B List
    db.temp_addmastername(call.message.chat.id, db.select_all_masters_by_spec('Мастер маникюра')[ind][2])
    db.temp_addmastersurname(call.message.chat.id, db.select_all_masters_by_spec('Мастер маникюра')[ind][3])

    #b.append(db.select_all_masters_by_spec('Мастер маникюра')[ind][2])
    #b.append(db.select_all_masters_by_spec('Мастер маникюра')[ind][3])
    bot.edit_message_text(f"Выберите {MyStep[step]}", call.message.chat.id, call.message.message_id, reply_markup=calendar)
@bot.callback_query_handler(func=lambda call: call.data in ['codemanik', 'codepar', 'codecosm', 'fullcalendar'])
def callbackproc(call):
    if call.data == 'fullcalendar':
        calendar, step = WYearTelegramCalendar(calendar_id=2, locale='ru', min_date=datetime.date.today()).build()
        bot.edit_message_text(f"Выберите {MyStep[step]}", call.message.chat.id, call.message.message_id, reply_markup=calendar)

    elif call.data == 'codemanik':
        spec = 'Мастер маникюра'
        bot.send_message(call.message.chat.id, 'Введите ваше имя')
        bot.register_next_step_handler(call.message, mastereg1, spec)

    elif call.data == 'codepar':
        spec = 'Парикмахер'
        bot.send_message(call.message.chat.id, 'Введите ваше имя')
        bot.register_next_step_handler(call.message, mastereg1, spec)

    elif call.data == 'codecosm':
        spec = 'Косметолог'
        bot.send_message(call.message.chat.id, 'Введите ваше имя')
        bot.register_next_step_handler(call.message, mastereg1, spec)
#menucalendar
@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id=2))
def cal(c):
    db = Sqlight('db.db')
    result, key, step = WYearTelegramCalendar(calendar_id=2, locale='ru', min_date=datetime.date.today()).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {MyStep[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                              c.message.chat.id,
                              c.message.message_id)

        #E List
        #e.append(name)
        #e.append(surname)
        #e.append(result)
        #db.temp_addmastername(c.message.chat.id, name)
        #db.temp_addmastersurname(c.message.chat.id, surnamename)
        db.temp_adddate(c.message.chat.id, result)

        markup = types.InlineKeyboardMarkup(row_width=1)
        n = 9

        for i in range(7):
            if db.check_zapis_time_u_mastera(db.temp_selectmastername(c.message.chat.id), db.temp_selectmastersurname(c.message.chat.id), result, f'{str(n)}:00') == True:
                p = db.get_zapis_from_master_and_time(db.temp_selectmastername(c.message.chat.id), db.temp_selectmastersurname(c.message.chat.id), result, f'{str(n)}:00')[0]
                i = types.InlineKeyboardButton(f'Время - {p[2]}, Имя клиента - {p[5]}, телефон клиента - {p[6]}, процедура - {p[7]}', callback_data=f'zapis{str(i)}')
                n += 2
                markup.add(i)
            else:
                i = types.InlineKeyboardButton(f'{str(n)}:00', callback_data=f'{str(n)}:00menu')
                n += 2
                markup.add(i)
        else:
            som = types.InlineKeyboardButton('Назад', callback_data='back2')
            markup.add(som)


        bot.send_message(c.message.chat.id, 'Вы можете выбрать одну из записей и взаемодействовать с нею', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['zapis0', 'zapis1', 'zapis2', 'zapis3', 'zapis4', 'zapis5', 'zapis6'])
def choiceproc(call):
    db = Sqlight('db.db')
    if call.data == 'zapis0':
        zapis = db.get_zapis_from_master_and_time(db.temp_selectmastername(call.message.chat.id), db.temp_selectmastersurname(call.message.chat.id), db.temp_selectdate(call.message.chat.id), '9:00')[0]
    elif call.data == 'zapis1':
        zapis = db.get_zapis_from_master_and_time(db.temp_selectmastername(call.message.chat.id), db.temp_selectmastersurname(call.message.chat.id), db.temp_selectdate(call.message.chat.id), '11:00')[0]
    elif call.data == 'zapis2':
        zapis = db.get_zapis_from_master_and_time(db.temp_selectmastername(call.message.chat.id), db.temp_selectmastersurname(call.message.chat.id), db.temp_selectdate(call.message.chat.id), '13:00')[0]
    elif call.data == 'zapis3':
        zapis = db.get_zapis_from_master_and_time(db.temp_selectmastername(call.message.chat.id), db.temp_selectmastersurname(call.message.chat.id), db.temp_selectdate(call.message.chat.id), '15:00')[0]
    elif call.data == 'zapis4':
        zapis = db.get_zapis_from_master_and_time(db.temp_selectmastername(call.message.chat.id), db.temp_selectmastersurname(call.message.chat.id), db.temp_selectdate(call.message.chat.id), '17:00')[0]
    elif call.data == 'zapis5':
        zapis = db.get_zapis_from_master_and_time(db.temp_selectmastername(call.message.chat.id), db.temp_selectmastersurname(call.message.chat.id), db.temp_selectdate(call.message.chat.id), '19:00')[0]
    elif call.data == 'zapis6':
        zapis = db.get_zapis_from_master_and_time(db.temp_selectmastername(call.message.chat.id), db.temp_selectmastersurname(call.message.chat.id), db.temp_selectdate(call.message.chat.id), '21:00')[0]

    #F List
    db.temp_addtempid(call.message.chat.id, zapis[0])
    db.temp_adddate(call.message.chat.id, zapis[1])
    db.temp_addtime(call.message.chat.id, zapis[2])


    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Удалить', callback_data='deletezapis')
    markup.add(item1)
    bot.edit_message_text(f'Время - {zapis[2]}, Имя клиента - {zapis[5]}, телефон клиента - {zapis[6]}, процедура - {zapis[7]}', call.message.chat.id, call.message.message_id, reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data in ['9:00menu', '11:00menu', '13:00menu', '15:00menu', '17:00menu', '19:00menu', '21:00menu'])
def procccc(call):
    db = Sqlight('db.db')
    #Мастер создает запись
    time = str(call.data).replace('menu', '')
    #H List
    #h.append(time)
    db.temp_addtime(call.message.chat.id, time)
    markup = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton('Создать запись', callback_data='menucreatezapis')
    markup.add(item1)
    bot.send_message(call.message.chat.id, f'Время - {time}, Вы можете создать запись здесь', reply_markup=markup)




@bot.callback_query_handler(func=lambda call: call.data in ['deletezapis', 'menucreatezapis'])
def zapisproc(call):
    db = Sqlight('db.db')
    if call.data == 'deletezapis':
        db.delte_zapis(db.temp_selecttempid(call.message.chat.id))
        bot.edit_message_text('Запись удалена!', call.message.chat.id, call.message.message_id)
        klient = db.get_user_id_from_klient(db.temp_selectusername(call.message.chat.id), db.temp_selectuserphone(call.message.chat.id))[0]
        bot.send_message(klient[1], f'Ваша запись на дату {db.temp_selectdate(call.message.chat.id)}, {db.temp_selecttime(call.message.chat.id)} удалена')

    elif call.data == 'menucreatezapis':
        markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton('Маникюр', callback_data='menumanik')
        markup.add(item1)
        bot.send_message(call.message.chat.id, 'Выберите процедуру', reply_markup=markup)

@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id=1))
def call(c):
    result, key, step = WYearTelegramCalendar(calendar_id=1, locale='ru', min_date=datetime.date.today()).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {MyStep[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                              c.message.chat.id,
                              c.message.message_id)
        #добавляем дату
        #b.append(result)

        markup = types.InlineKeyboardMarkup(row_width=1)
        n = 9
        db = Sqlight('db.db')
        db.temp_adddate(c.message.chat.id, result)
        #Создание списка доступных времен для клиента *Баги*
        for i in range(7):
            if db.check_zapis_time_u_mastera(db.temp_selectmastername(c.message.chat.id), db.temp_selectmastersurname(c.message.chat.id), db.temp_selectdate(c.message.chat.id), f'{str(n)}:00') == False:
                i = types.InlineKeyboardButton(f'{str(n)}:00', callback_data=f'{str(n)}:00')
                n += 2
                markup.add(i)
            else:
                i = types.InlineKeyboardButton('------', callback_data='nothing')
                n += 2
                markup.add(i)
        else:
            som = types.InlineKeyboardButton('Назад', callback_data='back')
            markup.add(som)
        bot.edit_message_text('Выберите время записи:', c.message.chat.id, c.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ['9:00', '11:00', '13:00', '15:00', '17:00', '19:00', '21:00'])
def timeproc(call):
    bot.edit_message_text(f'Вы выбрали {call.data}', call.message.chat.id, call.message.message_id)
    #b list
    #b.append(call.data)
    db = Sqlight('db.db')
    db.temp_addtime(call.message.chat.id, call.data)
    if db.klient_exists(call.message.chat.id) != True:
        bot.send_message(call.message.chat.id, 'Супер! Введите свое имя')
        bot.register_next_step_handler(call.message, klientreg1)

    #Удалить yep nop proc
    else:

        #*********
        bot.edit_message_text(f'Поздравляю, вы записались на {db.temp_selectdate(call.message.chat.id)} {db.temp_selecttime(call.message.chat.id)}, процедура - {db.temp_selectprocedura(call.message.chat.id)}.', call.message.chat.id,
                              call.message.message_id)
        name = db.find_klient_by_id(call.message.chat.id)[0][2]
        phone = db.find_klient_by_id(call.message.chat.id)[0][3]
        # B List
        #b.append(name)
        #b.append(phone)
        db.temp_addusername(call.message.chat.id, name)
        db.temp_adduserphone(call.message.chat.id, phone)


        db.zapis(db.temp_selectmastername(call.message.chat.id), db.temp_selectmastersurname(call.message.chat.id), db.temp_selectdate(call.message.chat.id), db.temp_selecttime(call.message.chat.id), db.temp_selectusername(call.message.chat.id), db.temp_selectuserphone(call.message.chat.id), db.temp_selectprocedura(call.message.chat.id))
        bot.send_message(db.select_all_masters_by_name(db.temp_selectmastername(call.message.chat.id), db.temp_selectmastersurname(call.message.chat.id))[0][1], f'Клиент под именем {db.temp_selectusername(call.message.chat.id)} и с номером телефона {db.temp_selectuserphone(call.message.chat.id)} записался на {db.temp_selectdate(call.message.chat.id)} {db.temp_selecttime(call.message.chat.id)}, процедура - {db.temp_selectprocedura(call.message.chat.id)}')



@bot.callback_query_handler(func=lambda call: call.data in ['back', 'back2', 'menumanik', 'moizapisidelete', 'moizapisiback2'])
def sdsa(call):
    if call.data == 'back':

        calendar, step = WYearTelegramCalendar(calendar_id=1, locale='ru', min_date=datetime.date.today()).build()
        bot.edit_message_text(f"Выберите {MyStep[step]}", call.message.chat.id, call.message.message_id, reply_markup=calendar)
        #b.pop()
    elif call.data == 'back2':
        calendar, step = WYearTelegramCalendar(calendar_id=2, locale='ru', min_date=datetime.date.today()).build()
        bot.send_message(call.message.chat.id, f"Выберите {MyStep[step]}", reply_markup=calendar)

    elif call.data == 'menumanik':
        #g.append('Маникюр')
        db = Sqlight('db.db')
        db.temp_addprocedura(call.message.chat.id, 'Маникюр')

        bot.send_message(call.message.chat.id, 'Введите имя клиента')
        #B List
        #db.temp_addmastername(call.message.chat.id, name)
        #db.temp_addmastersurname(call.message.chat.id, surname)

        #b.append(name)
        #b.append(surname)
        #b.append(e[2])
        #b.append(h[0])
        bot.register_next_step_handler(call.message, klientreg1)

    elif call.data == 'moizapisidelete':
        db = Sqlight('db.db')
        db.delte_zapis(db.temp_selecttempid(call.message.chat.id))
        bot.edit_message_text('Запись удалена', call.message.chat.id, call.message.message_id)
        masteruserid = db.select_all_masters_by_name(db.temp_selectmastername(call.message.chat.id), db.temp_selectmastersurname(call.message.chat.id))[0][1]
        bot.send_message(masteruserid, f'Клиент под именем {db.temp_selectusername(call.message.chat.id)}, телефоном {db.temp_selectuserphone(call.message.chat.id)} удалил запись на дату {db.temp_selectdate(call.message.chat.id)}, {db.temp_selecttime(call.message.chat.id)}, процедура - {db.temp_selectprocedura(call.message.chat.id)}')

    elif call.data == 'moizapisiback2':
        db = Sqlight('db.db')

        if db.find_klient_by_id(call.message.chat.id):
            klient = db.find_klient_by_id(call.message.chat.id)[0]
            name = klient[2]
            phone = klient[3]
            markup = types.InlineKeyboardMarkup(row_width=1)
            if db.select_zapisi_from_klient(name, phone):
                n = 0
                for i in db.select_zapisi_from_klient(name, phone):
                    p = types.InlineKeyboardButton(f'Дата - {i[1]}, {i[2]}, мастер - {i[3]} {i[4]}, процедура - {i[7]}',
                                                   callback_data=f'moizapisi{str(n)}')
                    markup.add(p)
                    n += 1

                else:


                    bot.edit_message_text('Тут вы можете посмотреть свои записи', call.message.chat.id,
                                          call.message.message_id, reply_markup=markup)

                    db.temp_addusername(call.message.chat.id, name)
                    db.temp_adduserphone(call.message.chat.id, phone)
                    #j.append(name)
                    #j.append(phone)
            else:
                item1 = types.InlineKeyboardButton('Записатсься', callback_data='startzapis')
                markup.add(item1)

                bot.edit_message_text('У вас нету записей', call.message.chat.id, call.message.message_id,
                                      reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup(row_width=1)
            item1 = types.InlineKeyboardButton('Записатсься', callback_data='startzapis')
            markup.add(item1)
            bot.edit_message_text('Вы не зарегистрированы', call.message.chat.id, call.message.message_id,
                                  reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in [f'moizapisi{str(x)}' for x in range(len(Sqlight('db.db').select_zapisi_from_klient(Sqlight('db.db').temp_selectusername(call.message.chat.id), Sqlight('db.db').temp_selectuserphone(call.message.chat.id))))])
def moizapisiprocc(call):
    #клиент может удалить запись
    db = Sqlight('db.db')
    ind = str(call.data).replace('moizapisi', '')
    zapis = db.select_zapisi_from_klient(db.temp_selectusername(call.message.chat.id), db.temp_selectuserphone(call.message.chat.id))[int(ind)]
    #j.clear()
    #k.append(zapis)

    db.temp_addtempid(call.message.chat.id, zapis[0])

    db.temp_adddate(call.message.chat.id, zapis[1])
    db.temp_addtime(call.message.chat.id, zapis[2])

    db.temp_addmastername(call.message.chat.id, zapis[3])
    db.temp_addmastersurname(call.message.chat.id, zapis[4])

    db.temp_addusername(call.message.chat.id, zapis[5])
    db.temp_adduserphone(call.message.chat.id, zapis[6])

    db.temp_addprocedura(call.message.chat.id, zapis[7])


    markup = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton('Удалить запись', callback_data='moizapisidelete')
    item2 = types.InlineKeyboardButton('Назад', callback_data='moizapisiback2')
    markup.add(item1, item2)

    bot.edit_message_text(f'Дата - {zapis[1]}, {zapis[2]}, мастер - {zapis[3]} {zapis[4]}, процедура - {zapis[7]}', call.message.chat.id, call.message.message_id, reply_markup=markup)


def deleteoldzapisi():
    db = Sqlight('db.db')

    for i in db.select_all_zapisi():
        year, month, day = i[1].split('-')
        if datetime.date(int(year), int(month), int(day)) < datetime.date.today():
            db.delte_zapis(i[0])
            print('Just deleted a zapis')



if __name__ == '__main__':
    db = Sqlight('db.db')

    sched = BackgroundScheduler()
    sched.add_job(deleteoldzapisi, 'interval', seconds=5)

    sched.start()
    while True:
        try:
            bot.polling(none_stop=True)

        except Exception as e:
            print(e)



