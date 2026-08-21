import logging
import config
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
import datetime

from telegram_bot_calendar import WYearTelegramCalendar
from salondb import Sqlight



logging.basicConfig(level=logging.INFO)
db = Sqlight('db.db')
MyStep = {'y': 'год', 'm': 'месяц', 'd': 'день'}
bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
secretcode = 2929

class KlientReg(StatesGroup):
    serv = State()
    procedura = State()
    master = State()
    date = State()
    time = State()
    usercontact = State()

class MoiZapisi(StatesGroup):
    vibor = State()
    deleteorback = State()

class MasterReg(StatesGroup):
    code = State()
    spec = State()
    name = State()
    surname = State()

class MasterMenuPick(StatesGroup):
    pick = State()

class MasterMenuCalendar(StatesGroup):
    calendar = State()
    timechoice = State()
    deleteorback = State()

    createfirst = State()
    createsecond = State()
    createthird = State()



class Masterdelete(StatesGroup):
    yesorno = State()



#start1
@dp.message_handler(commands='start', state='*')
async def command_start(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if not db.master_exists(message.chat.id):
        markup.add('Записаться', 'Мои записи')
    else:
        markup.add('Записаться', 'Мои записи', 'Меню мастера')


    db.temp_adduser_id(message.chat.id)
    #await Form.default.set()
    await message.reply('Hi there', reply_markup=markup)


#unused
@dp.message_handler(lambda message: message.text in ['Отменить регистрацию'], state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
     current_state = await state.get_state()
     print(current_state)

#start2
@dp.message_handler(lambda message: message.text in ['Записаться', 'Мои записи', 'Меню мастера'], state='*')
async def bum(message: types.Message, state: FSMContext):
    #klient1
    if message.text == 'Записаться':
        markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton('Ногтевой сервис', callback_data='nogtserv')
        item2 = types.InlineKeyboardButton('Брови и ресницы', callback_data='brovserv')

        markup.add(item1, item2)

        await KlientReg.serv.set()

        await bot.send_message(message.chat.id, 'Выберите сервис', reply_markup=markup)
    #mymenu1
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

                    await MoiZapisi.vibor.set()
                    await bot.send_message(message.chat.id, 'Тут вы можете посмотреть свои записи', reply_markup=markup)

                    db.temp_addusername(message.chat.id, name)
                    db.temp_adduserphone(message.chat.id, phone)
            else:
                item1 = types.InlineKeyboardButton('Записатсься', callback_data='startzapis')
                markup.add(item1)

                await bot.send_message(message.chat.id, 'У вас нету записей', reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup(row_width=1)
            item1 = types.InlineKeyboardButton('Записатсься', callback_data='startzapis')
            markup.add(item1)
            await bot.send_message(message.chat.id, 'У вас нету записей', reply_markup=markup)
    #mastermenu1
    elif message.text == 'Меню мастера':
        if not db.master_exists(message.chat.id):
            pass
        else:
            master = db.master_exists(message.chat.id)[0]
            markup = types.InlineKeyboardMarkup(row_width=1)

            item1 = types.InlineKeyboardButton('Просмотреть полный календарь моих записей', callback_data='fullcalendar')
            item2 = types.InlineKeyboardButton('Просмотреть календари других мастеров', callback_data='otherscalendar')
            item3 = types.InlineKeyboardButton('Стереть эту учетную запись', callback_data='masterdelete')
            # D List
            # d.append(db.master_exists(message.chat.id)[0][2:4])
            db.temp_addmastername(message.chat.id, db.master_exists(message.chat.id)[0][2])
            db.temp_addmastersurname(message.chat.id, db.master_exists(message.chat.id)[0][3])
            markup.add(item1, item2, item3)
            await bot.send_message(message.chat.id, f'Добро пожаловать, {master[2]} {master[3]}', reply_markup=markup)
            await MasterMenuPick.pick.set()

#klient2
@dp.callback_query_handler(lambda call: call.data in ['nogtserv', 'brovserv'], state=KlientReg.serv)
async def servproc(callbackQuery: types.CallbackQuery):
    if callbackQuery.data == 'nogtserv':

        markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton('Маникюр', callback_data='manik')
        item2 = types.InlineKeyboardButton('Педикюр', callback_data='ped')



        back = types.InlineKeyboardButton('Назад', callback_data='startzapis')
        markup.add(item1, item2, back)

        await KlientReg.next()
        await bot.edit_message_text('Выберите процедуру', callbackQuery.message.chat.id, callbackQuery.message.message_id, reply_markup=markup)
#klient3
@dp.callback_query_handler(lambda call: call.data in ['manik', 'ped'], state=KlientReg.procedura)
async def proceduraproc(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'manik':
        spec = 'Мастер маникюра'
        async with state.proxy() as data:
            data['procedura'] = 'Маникюр'

        kind = 'manikmaster'
        back = 'nogtserv'
    elif call.data == 'ped':
        spec = 'Мастер маникюра'
        async with state.proxy() as data:
            data['procedura'] = 'Педикюр'

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
    await KlientReg.next()
    await bot.edit_message_text('Выберите мастера:', call.message.chat.id, call.message.message_id, reply_markup=markup)

#back
@dp.callback_query_handler(lambda call: call.data in ['startzapis'], state=KlientReg.procedura)
async def backproc(call: types.CallbackQuery, state: FSMContext):
    markup = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton('Ногтевой сервис', callback_data='nogtserv')
    item2 = types.InlineKeyboardButton('Брови и ресницы', callback_data='brovserv')

    markup.add(item1, item2)

    await KlientReg.previous()

    await bot.edit_message_text('Выберите сервис', call.message.chat.id, call.message.message_id, reply_markup=markup)



manikmasters = [f'manikmaster{str(x)}' for x in range(len(db.select_all_masters_by_spec('Мастер маникюра')))]

#klient4
@dp.callback_query_handler(lambda call: call.data in manikmasters, state=KlientReg.master)
async def manikmasterproc(call: types.CallbackQuery, state: FSMContext):

    ind = int(str(call.data).replace('manikmaster', ''))
    calendar, step = WYearTelegramCalendar(calendar_id=1, locale='ru', min_date=datetime.date.today()).build()
    async with state.proxy() as data:
        data['mastername'] = db.select_all_masters_by_spec('Мастер маникюра')[ind][2]
        data['mastersurname'] = db.select_all_masters_by_spec('Мастер маникюра')[ind][3]

    await KlientReg.next()
    await bot.edit_message_text(f"Выберите {MyStep[step]}", call.message.chat.id, call.message.message_id, reply_markup=calendar)


#back


#klient5
@dp.callback_query_handler(WYearTelegramCalendar.func(calendar_id=1), state=KlientReg.date)
async def call(c: types.CallbackQuery, state: FSMContext):
    result, key, step = WYearTelegramCalendar(calendar_id=1, locale='ru', min_date=datetime.date.today()).process(c.data)
    if not result and key:
        await bot.edit_message_text(f"Выберите {MyStep[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        await bot.edit_message_text(f"Вы выбрали {result}",
                              c.message.chat.id,
                              c.message.message_id)

        markup = types.InlineKeyboardMarkup(row_width=1)
        n = 9


        #Создание списка доступных времен для клиента *Баги*
        async with state.proxy() as data:
            data['date'] = result
            for i in range(7):
                if db.check_zapis_time_u_mastera(data['mastername'], data['mastersurname'], result, f'{str(n)}:00') == False:
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

            await bot.edit_message_text('Выберите время записи:', c.message.chat.id, c.message.message_id, reply_markup=markup)
        await KlientReg.next()

#klient6
@dp.callback_query_handler(lambda call: call.data in ['9:00', '11:00', '13:00', '15:00', '17:00', '19:00', '21:00'], state=KlientReg.time)
async def timeproc(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(f'Вы выбрали {call.data}', call.message.chat.id, call.message.message_id)



    if db.klient_exists(call.message.chat.id) != True:

        markup = types.ReplyKeyboardMarkup()
        somebodyoncetoldme = types.KeyboardButton('отправить контакт', request_contact=True)
        markup.add(somebodyoncetoldme)
        await KlientReg.next()
        await bot.send_message(call.message.chat.id, 'Теперь нажмите на кнопку Отправить контакт', reply_markup=markup)

        #Удалить yep nop proc
    else:
        async with state.proxy() as data:

            await bot.edit_message_text('Поздравляю, вы записались на ' + str(data['date']) + ' ' + str(call.data) + ', процедура - ' + str(data['procedura']) + '.', call.message.chat.id, call.message.message_id)
            name = db.find_klient_by_id(call.message.chat.id)[0][2]
            phone = db.find_klient_by_id(call.message.chat.id)[0][3]

            data['time'] = call.data
            data['username'] = name
            data['userphone'] = phone

            date = data['date']

            procedura = data['procedura']
            db.zapis(data['mastername'], data['mastersurname'], data['date'], call.data, data['username'], data['userphone'], data['procedura'])

            await bot.send_message(db.select_all_masters_by_name(data['mastername'], data['mastersurname'])[0][1], f'Клиент под именем {name} и с номером телефона {phone} записался на {date} {call.data}, процедура - {procedura}')
            await state.finish()
#klient7
@dp.message_handler(content_types=['contact'], state=KlientReg.usercontact)
async def usernameproc(message: types.Message, state: FSMContext):
    if message.contact.user_id == message.chat.id:

        async with state.proxy() as data:

            data['username'] = message.contact.full_name
            data['userphone'] = message.contact.phone_number
            date = data['date']
            time = data['time']
            procedura = data['procedura']
            db.zapis(data['mastername'], data['mastersurname'], data['date'], data['time'], data['username'], data['userphone'], data['procedura'])
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            if not db.master_exists(message.chat.id):
                markup.add('Записаться', 'Мои записи')
            else:
                markup.add('Записаться', 'Мои записи', 'Меню мастера')

            db.add_klient(message.chat.id, data['username'], data['userphone'])
            await bot.send_message(message.chat.id, 'Поздравляю, вы записались на ' + str(data['date']) + ' ' + str(data['time']) + ', процедура - ' + data['procedura'] + '.', reply_markup=markup)
            await bot.send_message(db.select_all_masters_by_name(data['mastername'], data['mastersurname'])[0][1], f'Клиент под именем {message.contact.full_name} и с номером телефона {message.contact.phone_number} записался на {date} {time}, процедура - {procedura}')
            await state.finish()
    else:

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if not db.master_exists(message.chat.id):
            markup.add('Записаться', 'Мои записи')
        else:
            markup.add('Записаться', 'Мои записи', 'Меню мастера')
        await bot.send_message(message.chat.id, 'something wrong', reply_markup=markup)
        await state.finish()
#moizapisi2
@dp.callback_query_handler(lambda call: call.data in [f'moizapisi{str(x)}' for x in range(len(db.select_zapisi_from_klient(db.temp_selectusername(call.message.chat.id), db.temp_selectuserphone(call.message.chat.id))))], state=MoiZapisi.vibor)
async def moizapisiprocc(call: types.CallbackQuery, state: FSMContext):
    #клиент может удалить запись



    ind = str(call.data).replace('moizapisi', '')
    zapis = db.select_zapisi_from_klient(db.temp_selectusername(call.message.chat.id), db.temp_selectuserphone(call.message.chat.id))[int(ind)]
    #j.clear()
    #k.append(zapis)
    async with state.proxy() as data:

        data['tempid'] = zapis[0]
        data['date'] = zapis[1]
        data['time'] = zapis[2]
        data['mastername'] = zapis[3]
        data['mastersurname'] = zapis[4]
        data['username'] = zapis[5]
        data['userphone'] = zapis[6]
        data['procedura'] = zapis[7]



    markup = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton('Удалить запись', callback_data='moizapisidelete')
    item2 = types.InlineKeyboardButton('Назад', callback_data='moizapisiback')
    markup.add(item1, item2)

    await bot.edit_message_text(f'Дата - {zapis[1]}, {zapis[2]}, мастер - {zapis[3]} {zapis[4]}, процедура - {zapis[7]}', call.message.chat.id, call.message.message_id, reply_markup=markup)
    await MoiZapisi.next()
#moizapisi3
@dp.callback_query_handler(lambda call: call.data in ['moizapisidelete', 'moizapisiback'], state=MoiZapisi.deleteorback)
async def moizapisideleteorback(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'moizapisidelete':

        async with state.proxy() as data:

            db.delte_zapis(data['tempid'])
            await bot.edit_message_text('Запись удалена', call.message.chat.id, call.message.message_id)
            masteruserid = db.select_all_masters_by_name(data['mastername'], data['mastersurname'])[0][1]
            await bot.send_message(masteruserid, f'Клиент под именем {data["username"]}, телефоном {data["userphone"]} удалил запись на дату {data["date"]}, {data["time"]}, процедура - {data["procedura"]}')

        await state.finish()
    elif call.data == 'moizapisiback':
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

                    await MoiZapisi.previous()
                    await bot.edit_message_text('Тут вы можете посмотреть свои записи', call.message.chat.id, call.message.message_id, reply_markup=markup)

                    db.temp_addusername(call.message.chat.id, name)
                    db.temp_adduserphone(call.message.chat.id, phone)
            else:
                item1 = types.InlineKeyboardButton('Записатсься', callback_data='startzapis')
                markup.add(item1)

                await bot.send_message(call.message.chat.id, 'У вас нету записей', reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup(row_width=1)
            item1 = types.InlineKeyboardButton('Записатсься', callback_data='startzapis')
            markup.add(item1)
            await bot.send_message(call.message.chat.id, 'У вас нету записей', reply_markup=markup)

#mastermenureg1
@dp.message_handler(commands='code', state='*')
async def masterregcmd(message: types.Message):
    await bot.send_message(message.chat.id, 'Введите код')
    await MasterReg.code.set()
#mastermenureg2
@dp.message_handler(state=MasterReg.code)
async def codeproc(message: types.Message):
    if message.text == str(secretcode):
        markup = types.InlineKeyboardMarkup(row_width=1)

        item1 = types.InlineKeyboardButton('Мастер маникюра', callback_data='codemanik')
        item2 = types.InlineKeyboardButton('Парикмахер', callback_data='codepar')
        item3 = types.InlineKeyboardButton('Косметолог', callback_data='codecosm')
        markup.add(item1, item2, item3)

        await bot.send_message(message.chat.id, 'Вы успешно ввели код, выберите специальность', reply_markup=markup)
        await MasterReg.next()
    else:
        await bot.send_message(message.chat.id, 'Неверный код!')


#mastermenureg3
@dp.callback_query_handler(lambda call: call.data in ['codemanik', 'codepar', 'codecosm'], state=MasterReg.spec)
async def masterregspec(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data == 'codemanik':
            data['spec'] = 'Мастер маникюра'
        elif call.data == 'codepar':
            data['spec'] = 'Парикмахер'

    await bot.edit_message_text('Введите имя:', call.message.chat.id, call.message.message_id)
    await MasterReg.next()

#mastermenureg4
@dp.message_handler(state=MasterReg.name)
async def masterregname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await bot.send_message(message.chat.id, 'Введите фамилию')
    await MasterReg.next()

#mastermenureg5
@dp.message_handler(state=MasterReg.surname)
async def masterregsurname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:

        db.add_master(message.chat.id, data['name'], message.text, data['spec'])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if not db.master_exists(message.chat.id):
            markup.add('Записаться', 'Мои записи')
        else:
            markup.add('Записаться', 'Мои записи', 'Меню мастера')

        await bot.send_message(message.chat.id, f'Ваше имя - {data["name"]}, фамилия - {message.text}', reply_markup=markup)
    await state.finish()


#mastermenu2
@dp.callback_query_handler(lambda call: call.data in ['fullcalendar', 'otherscalendar', 'masterdelete'], state=MasterMenuPick.pick)
async def mastermenu2(call: types.CallbackQuery, state: FSMContext):
    #masterfullcalendar1
    if call.data == 'fullcalendar':
        calendar, step = WYearTelegramCalendar(calendar_id=2, locale='ru', min_date=datetime.date.today()).build()
        await state.finish()
        await bot.edit_message_text(f"Выберите {MyStep[step]}", call.message.chat.id, call.message.message_id, reply_markup=calendar)
        await MasterMenuCalendar.calendar.set()
    #otherscalendar1
    elif call.data == 'otherscalendar':
        markup = types.InlineKeyboardMarkup(row_width=1)

        for i in db.select_all_masters():
            if str(call.message.chat.id) != i[1]:
                ink = types.InlineKeyboardButton(f'{i[2]} {i[3]}', callback_data=f'othermaster{str(i[0])}')
                markup.add(ink)
        else:
            back = types.InlineKeyboardButton('Назад', callback_data='othermasterback')
            markup.add(back)

        await bot.edit_message_text('Выберите мастера', call.message.chat.id, call.message.message_id, reply_markup=markup)
    #masterdelete1
    elif call.data == 'masterdelete':
        await state.finish()
        await bot.edit_message_text('Вы уверенны что хотите стереть эту учетную запись мастера? Напишите Да или Нет', call.message.chat.id, call.message.message_id)
        await Masterdelete.yesorno.set()


#masterfullcalendar2
@dp.callback_query_handler(WYearTelegramCalendar.func(calendar_id=2), state=MasterMenuCalendar.calendar)
async def cal(c: types.CallbackQuery, state: FSMContext):

    result, key, step = WYearTelegramCalendar(calendar_id=2, locale='ru', min_date=datetime.date.today()).process(c.data)
    if not result and key:
        await bot.edit_message_text(f"Выберите {MyStep[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        await bot.edit_message_text(f"Вы выбрали {result}",
                              c.message.chat.id,
                              c.message.message_id)

        async with state.proxy() as data:
            data['date'] = result


            markup = types.InlineKeyboardMarkup(row_width=1)
            n = 9

            for i in range(7):
                if db.check_zapis_time_u_mastera(db.master_exists(c.message.chat.id)[0][2], db.master_exists(c.message.chat.id)[0][3], result, f'{str(n)}:00') == True:
                    p = db.get_zapis_from_master_and_time(db.master_exists(c.message.chat.id)[0][2], db.master_exists(c.message.chat.id)[0][3], result, f'{str(n)}:00')[0]
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

        await MasterMenuCalendar.next()
        await bot.send_message(c.message.chat.id, 'Вы можете выбрать одну из записей и взаемодействовать с нею', reply_markup=markup)
#masterfullcalendar3(1)
@dp.callback_query_handler(lambda call: call.data in [f'zapis{str(x)}' for x in range(7)], state=MasterMenuCalendar.timechoice)
async def callendarchoiceproc(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data == 'zapis0':
            zapis = db.get_zapis_from_master_and_time(db.master_exists(call.message.chat.id)[0][2], db.master_exists(call.message.chat.id)[0][3], data["date"], '9:00')[0]
        elif call.data == 'zapis1':
            zapis = db.get_zapis_from_master_and_time(db.master_exists(call.message.chat.id)[0][2], db.master_exists(call.message.chat.id)[0][3], data["date"], '11:00')[0]
        elif call.data == 'zapis2':
            zapis = db.get_zapis_from_master_and_time(db.master_exists(call.message.chat.id)[0][2], db.master_exists(call.message.chat.id)[0][3], data["date"], '13:00')[0]
        elif call.data == 'zapis3':
            zapis = db.get_zapis_from_master_and_time(db.master_exists(call.message.chat.id)[0][2], db.master_exists(call.message.chat.id)[0][3], data["date"], '15:00')[0]
        elif call.data == 'zapis4':
            zapis = db.get_zapis_from_master_and_time(db.master_exists(call.message.chat.id)[0][2], db.master_exists(call.message.chat.id)[0][3], data["date"], '17:00')[0]
        elif call.data == 'zapis5':
            zapis = db.get_zapis_from_master_and_time(db.master_exists(call.message.chat.id)[0][2], db.master_exists(call.message.chat.id)[0][3], data["date"], '19:00')[0]
        elif call.data == 'zapis6':
            zapis = db.get_zapis_from_master_and_time(db.master_exists(call.message.chat.id)[0][2], db.master_exists(call.message.chat.id)[0][3], data["date"], '21:00')[0]


        data['tempid'] = zapis[0]
        data['date'] = zapis[1]
        data['time'] = zapis[2]
        data['username'] = zapis[5]
        data['userphone'] = zapis[6]

    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Удалить', callback_data='deletezapis')
    item2 = types.InlineKeyboardButton('Назад', callback_data='choiceback')
    markup.add(item1, item2)
    await bot.edit_message_text(f'Время - {zapis[2]}, Имя клиента - {zapis[5]}, телефон клиента - {zapis[6]}, процедура - {zapis[7]}', call.message.chat.id, call.message.message_id, reply_markup=markup)
    await MasterMenuCalendar.next()

#masterfullcalendar4(1)
@dp.callback_query_handler(lambda call: call.data in ['deletezapis', 'choiceback'], state=MasterMenuCalendar.deleteorback)
async def buuuum(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'deletezapis':
        async with state.proxy() as data:

            db.delte_zapis(data['tempid'])
            await bot.edit_message_text('Запись удалена!', call.message.chat.id, call.message.message_id)
            klient = db.get_user_id_from_klient(data['username'], data['userphone'])[0]
            await bot.send_message(klient[1], f'Ваша запись на дату {data["date"]}, {data["time"]} удалена')
        await state.finish()

    elif call.data == 'choiceback':
        async with state.proxy() as data:
            markup = types.InlineKeyboardMarkup(row_width=1)
            n = 9

            for i in range(7):
                if db.check_zapis_time_u_mastera(db.master_exists(call.message.chat.id)[0][2], db.master_exists(call.message.chat.id)[0][3], data["date"], f'{str(n)}:00') == True:
                    p = db.get_zapis_from_master_and_time(db.master_exists(call.message.chat.id)[0][2], db.master_exists(call.message.chat.id)[0][3], data["date"], f'{str(n)}:00')[0]
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

        await MasterMenuCalendar.previous()
        await bot.edit_message_text('Вы можете выбрать одну из записей и взаемодействовать с нею', call.message.chat.id, call.message.message_id, reply_markup=markup)




#masterfullcalendar3(2)
@dp.callback_query_handler(lambda call: call.data in ['9:00menu', '11:00menu', '13:00menu', '15:00menu', '17:00menu', '19:00menu', '21:00menu'], state=MasterMenuCalendar.timechoice)
async def procccc(call: types.CallbackQuery, state: FSMContext):

    #Мастер создает запись
    time = str(call.data).replace('menu', '')

    async with state.proxy() as data:
        data['time'] = time
    markup = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton('Создать запись', callback_data='menucreatezapis')
    item2 = types.InlineKeyboardButton('Назад', callback_data='menucreateback')
    markup.add(item1, item2)
    await bot.edit_message_text(f'Время - {time}, Вы можете создать запись здесь', call.message.chat.id, call.message.message_id, reply_markup=markup)
    await MasterMenuCalendar.createfirst.set()

#masterfullcalendar4(2)
@dp.callback_query_handler(lambda call: call.data in ['menucreatezapis', 'menucreateback'], state=MasterMenuCalendar.createfirst)
async def bumshakalaka(call: types.CallbackQuery, state: FSMContext):
    #menucreate1
    if call.data == 'menucreatezapis':
        markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton('Выбрать клиента из базы данных', callback_data='clientbase')
        item2 = types.InlineKeyboardButton('Ввести самому', callback_data='menucreat')

        markup.add(item1, item2)



        await bot.edit_message_text('Выберите способ создания записи', call.message.chat.id, call.message.message_id, reply_markup=markup)
        await MasterMenuCalendar.createsecond.set()



    elif call.data == 'menucreateback':
        async with state.proxy() as data:
            markup = types.InlineKeyboardMarkup(row_width=1)
            n = 9

            for i in range(7):
                if db.check_zapis_time_u_mastera(db.master_exists(call.message.chat.id)[0][2], db.master_exists(call.message.chat.id)[0][3], data["date"], f'{str(n)}:00') == True:
                    p = db.get_zapis_from_master_and_time(db.master_exists(call.message.chat.id)[0][2], db.master_exists(call.message.chat.id)[0][3], data["date"], f'{str(n)}:00')[0]
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

        await MasterMenuCalendar.timechoice.set()
        await bot.edit_message_text('Вы можете выбрать одну из записей и взаемодействовать с нею', call.message.chat.id, call.message.message_id, reply_markup=markup)

@dp.callback_query_handler(lambda call: call.data in ['clientbase', 'menucreat'], state=MasterMenuCalendar.createsecond)
async def clientbaseproc(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'clientbase':
        pass
    elif call.data == 'menucreat':
        pass



#masterdelete2
@dp.message_handler(state=Masterdelete.yesorno)
async def masterdeleteproc(message: types.Message, state: FSMContext):
    if str(message.text).lower() == 'да':
        db.delete_master_by_userid(message.chat.id)
        await bot.send_message(message.chat.id, 'Учетная запись мастера удалена')
        await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)