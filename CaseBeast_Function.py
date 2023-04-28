import re
import autoit
import json
import os
import py_win_keyboard_layout
import requests
import signal
import subprocess
import time
import a2s
import wmi
import math
import win32gui
import win32con
from datetime import datetime, timedelta
from urllib.parse import urlencode
from threading import Thread
import ctypes
import mss.tools

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, Message
from bs4 import BeautifulSoup
from psutil import process_iter
from steampy.guard import generate_one_time_code

from CaseBeast_Keyboards import *

StartStatus = False
starting = []
page = 0
posX = 0
posY = 0
acc = ''
ip_address = ''


# region Обычные функции

def readJson(path):  # Чтение JSON файлов
    file = open(os.path.abspath(path), encoding='utf-8')
    info = json.loads(file.read())
    file.close()
    return info


TG = readJson('json/Telegram.json')
TOKEN_API = TG["Telegram"]["Token_Bot"]
CHAT_ID = TG["Telegram"]["Chat_ID"]
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=MemoryStorage())


def writeJson(path, dictionary):  # Запись JSON файлов
    json.dump({**json.load(open(path, encoding='utf-8')), **dictionary}, open(path, 'w', encoding='utf-8'), indent=4)


def deleteJson(path, dictionary):  # Перезапись JSON файлов
    file = open(path, 'w', encoding='utf-8')
    file.write(json.dumps(dictionary, indent=4))
    file.close()


def getCode(share):  # Получение Steam Guard
    return generate_one_time_code(share)


def getStatusServer():  # Получение статуса сервера ON\OFF
    idle_path = readJson('Settings/settings.json')['auto_server_ip']
    if idle_path != 'None':  # Указан ли путь до IDLE
        enum = []
        for x in process_iter():  # Поиск нужного процесса
            enum.append(x.name())
        if enum.count('srcds.exe') > 0:  # Если сервер активен/не активен
            return 'ON'
        else:
            return 'OFF'
    else:
        return 'Not IDLE path'


def CreateCFG():
    csgo_cfg = readJson("settings/settings.json")["steam_path"][:-10] + \
               r"\steamapps\common\Counter-Strike Global Offensive\csgo\cfg"
    cfg_path = csgo_cfg + r'\panel.cfg'
    if os.path.exists(cfg_path) is False:
        cfg_settings = open(os.path.abspath("settings/panel.cfg")).read()
        cfg_file = open(cfg_path, "w")
        cfg_file.write(cfg_settings)
        cfg_file.close()


def getPrice(Case):
    url = 'https://steamcommunity.com/market/priceoverview/?'
    CaseID = readJson('json/cases.json')
    for number in CaseID:
        if int(number) == Case:
            params = {'market_hash_name': CaseID[str(number)]["case_name_market"],
                      'appid': '730',
                      'currency': '5',
                      'format': 'json'}
            r = requests.get(url, params=params)
            data = r.json()
            if r.status_code == 200:
                data = data['lowest_price']
                return CaseID[str(number)]["case_name_market"], data[:-5]
            else:
                return CaseID[str(number)]["case_name_market"], 0


# endregion


# region Ассинхронные функции


async def LaunchSelect(User):
    global posX, posY
    global ip_address
    info = readJson("json/accounts.json")
    remove_msg = await bot.send_message(chat_id=CHAT_ID, text=f'<b>{User} | Запуск аккаунта:\n\n'
                                                              f'⏳ Получение всех данных...\n </b>',
                                        parse_mode='HTML')
    login = info[User]['login']
    password = info[User]['password']
    shared_secret = info[User]['shared_secret']
    win_csgo_title = f'[{login}] # Counter-Strike: Global Offensive - Direct3D 9'
    settings = readJson('Settings/settings.json')
    remove_msg = await remove_msg.edit_text(f'<b>{User} | Запуск аккаунта:\n\n'
                                            f'✅ Получение всех данных\n'
                                            f'⏳ Запуск Steam...\n</b>', parse_mode='HTML')
    if settings['server_log_pass'] != 'None':
        autoit.run(f'{settings["steam_path"]} '
                   f'-login {login} {password} '
                   f'-applaunch 730 '
                   f'-low '
                   f'-console '
                   f'-d3d9ex '
                   f'-nohltv '
                   f'-nojoy '
                   f'-nomouse '
                   f'-nosound '
                   f'-noubershader '
                   f'-novid '
                   f'+fps_max 30 '
                   f'+exec panel.cfg '
                   f'-window -w 640 -h 480 '
                   f'+connect {settings["server_log_pass"]}')
    elif settings['auto_server_ip'] != 'None':
        if ip_address == '':
            ip_address = await Startup_IDLE()
        autoit.run(f'{settings["steam_path"]} '
                   f'-login {login} {password} '
                   f'-applaunch 730 '
                   f'-low '
                   f'-console '
                   f'-d3d9ex '
                   f'-nohltv '
                   f'-nojoy '
                   f'-nomouse '
                   f'-nosound '
                   f'-noubershader '
                   f'-novid '
                   f'+fps_max 30 '
                   f'+exec panel.cfg '
                   f'-window -w 640 -h 480 '
                   f'+connect {ip_address}')
    else:
        autoit.run(f'{settings["steam_path"]} '
                   f'-login {login} {password} '
                   f'-applaunch 730 '
                   f'-low '
                   f'-console '
                   f'-d3d9ex '
                   f'-nohltv '
                   f'-nojoy '
                   f'-nomouse '
                   f'-nosound '
                   f'-noubershader '
                   f'-novid '
                   f'+fps_max 30 '
                   f'+exec panel.cfg '
                   f'-window -w 640 -h 480 ')
    while autoit.win_exists("Вход в Steam") == 0: pass
    if autoit.win_exists("Вход в Steam"): time.sleep(5)
    while autoit.win_exists("Вход в Steam") == 0: pass
    autoit.win_activate("Вход в Steam")
    autoit.win_wait_active("Вход в Steam")
    win_steam_PID = autoit.win_get_process("Вход в Steam")
    remove_msg = await remove_msg.edit_text(f'<b>{User} | Запуск аккаунта:\n\n'
                                            f'✅ Получение всех данных\n'
                                            f'✅ Запуск Steam\n'
                                            f'⏳ Ввод Steam Guard...\n</b>', parse_mode='HTML')
    while autoit.win_exists('Вход в Steam'):
        try:
            time.sleep(5)
            autoit.win_activate('Вход в Steam')
            for _ in range(5):
                autoit.send('{BACKSPACE}')
            autoit.send(getCode(shared_secret))
            py_win_keyboard_layout.change_foreground_window_keyboard_layout(0x04090409)
            autoit.send('{Enter}')
        except:
            pass
        finally:
            time.sleep(3)
    autoit.win_wait_close('Вход в Steam')
    remove_msg = await remove_msg.edit_text(f'<b>{User} | Запуск аккаунта:\n\n'
                                            f'✅ Получение всех данных\n'
                                            f'✅ Запуск Steam\n'
                                            f'✅ Ввод Steam Guard\n'
                                            f'⏳ Запуск CS:GO...\n</b>', parse_mode='HTML')
    while autoit.win_exists(win_csgo_title) == 0:
        time.sleep(3)
        if autoit.win_exists('Диалоговое окно Steam') == 1:
            autoit.win_activate('Диалоговое окно Steam')
            autoit.win_wait_active('Диалоговое окно Steam')
            position = autoit.win_get_pos('Диалоговое окно Steam')
            ctypes.windll.user32.SetCursorPos(position[0] + 107, position[1] + 352)
            ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
        if autoit.win_exists("Обновление Counter-Strike: Global Offensive") == 1:
            await remove_msg.delete()
            await SendMSG('Запуск аккаунта завершен, обновите CS:GO и попробуйте снова!')
            break
        if autoit.win_exists("Ошибка службы Steam") == 1:
            await remove_msg.delete()
            await SendMSG('Программа запущена не от имени администратора!')
            break
        if autoit.win_exists('Counter-Strike: Global Offensive - Direct3D 9') == 1:
            autoit.win_wait('Counter-Strike: Global Offensive - Direct3D 9')
            autoit.win_activate('Counter-Strike: Global Offensive - Direct3D 9')
            autoit.win_wait_active('Counter-Strike: Global Offensive - Direct3D 9')
            autoit.win_set_title('Counter-Strike: Global Offensive - Direct3D 9', win_csgo_title)
    autoit.win_activate(win_csgo_title)
    autoit.win_move(win_csgo_title, posX, posY)
    win_csgo_PID = autoit.win_get_process(win_csgo_title)
    status = 'On'
    await remove_msg.delete()
    await SendMSG(f'<b>{User} | Запуск аккаунта:\n\n'
                  f'✅ Получение всех данных\n'
                  f'✅ Запуск Steam\n'
                  f'✅ Ввод Steam Guard\n'
                  f'✅ Запуск CS:GO\n\n'
                  f'{User} | Аккаунт успешно запущен!</b>')
    await UpdateAccountsJSON(status, login, password, shared_secret, win_csgo_title, win_csgo_PID, win_steam_PID)
    posX += 236
    if posX == 2124:
        posX = 0
        posY += 120


async def StoppingAll():
    info = readJson('json/launched_accounts.json')
    if info != {}:
        for User in info.copy():
            if autoit.win_exists(info[User]["win_csgo_title"]) == 1:
                try:
                    os.kill(info[User]["win_steam_PID"], signal.SIGTERM)
                    os.kill(info[User]["win_csgo_PID"], signal.SIGTERM)
                except:
                    pass
            info.pop(User)
            await SendMSG(f'{User} | Теперь выключен')
        deleteJson('json/launched_accounts.json', info)
    else:
        await SendMSG(f'Нет активных аккаунтов')


async def StoppingSelect(User):
    info = readJson('json/launched_accounts.json')
    value = list(info.keys())
    if value.count(User):
        if autoit.win_exists(info[User]["win_csgo_title"]) == 1:
            try:
                os.kill(info[User]["win_steam_PID"], signal.SIGTERM)
                os.kill(info[User]["win_csgo_PID"], signal.SIGTERM)
            except:
                pass
        info.pop(User)
        deleteJson('json/launched_accounts.json', info)


async def Startup_IDLE():
    global ip_address
    idle_path = readJson('Settings/settings.json')['auto_server_ip']
    pather = f'{idle_path[0:-10]}\csgo\logs'
    for proc in process_iter():
        if proc.name() == 'srcds.exe': proc.terminate()
    try:
        for path_remove in os.listdir(pather): os.remove(f'{pather}\\{path_remove}')
    except Exception as e:
        print(f'Ошибка - {e}')
    subprocess.Popen(idle_path, cwd=idle_path[0:-10])
    time.sleep(10)
    pather = os.listdir(pather)
    ip_adrs = ''
    count = 0
    for ip in pather:
        ip = ip[1:35].split('_')
        for x in ip:
            count += 1
            x = x.replace('0', '') if x.startswith('0') else x
            if count != 6:
                ip_adrs += f'.{x}'
                ip_adrs = ip_adrs.lstrip('.')
            else:
                break
    ip_address = ip_adrs[:-6] + ':' + ip_adrs[-5:]
    return ip_address


async def UpdateAccountsJSON(status, login, password, shared_secret, win_csgo_title, win_csgo_PID,
                             win_steam_PID):
    info = readJson('json/launched_accounts.json')
    if status == 'Off':
        info.pop(login)
    else:
        info[login] = {
            'login': login,
            'password': password,
            'shared_secret': shared_secret,
            'win_csgo_title': win_csgo_title,
            'win_csgo_PID': win_csgo_PID,
            'win_steam_PID': win_steam_PID,
            'status': status
        }
    file = open('json/launched_accounts.json', 'w', encoding='utf-8')
    file.write(json.dumps(info, indent=4))
    file.close()


async def SendMSG(text, rmp=0):
    if rmp == 0:
        await bot.send_message(chat_id=CHAT_ID,
                               text=f'<b>{text}</b>',
                               parse_mode='HTML')
    else:
        await bot.send_message(chat_id=CHAT_ID,
                               text=f'<b>{text}</b>',
                               parse_mode='HTML',
                               reply_markup=rmp)


# endregion


# region Классы FSM


class Timer_Setup(StatesGroup):
    TimerINT = State()


class Settings_json(StatesGroup):
    Steam_Path = State()
    Choice_IP = State()
    Server_Idle = State()
    Server_IP = State()
    Video_Choice = State()
    FirstSettings = State()


class Account_Farm(StatesGroup):
    Account_Choice = State()


class Account_Menu(StatesGroup):
    Account_maFiles = State()
    Account_logpass = State()


# endregion


# region Меню


@dp.message_handler(filters.IDFilter(user_id=CHAT_ID), text='Аккаунты 👥')
async def Beast_Account(message: types.message):
    AccountMenu = types.InlineKeyboardMarkup()
    account = list(readJson('json/accounts.json'))
    status_account = list(readJson('json/launched_accounts.json'))
    for login in range((page * 10), (page + 1) * 9 + (page + 1)):
        try:
            if login % 2 == 0:
                if account[login] in status_account:
                    status_1 = f'{account[login]} | 🟢\n'
                else:
                    status_1 = f'{account[login]} | 🔴\n'
                if account[login + 1] in status_account:
                    status_2 = f'{account[login + 1]} | 🟢\n'
                else:
                    status_2 = f'{account[login + 1]} | 🔴\n'
                AccountMenu.row(
                    KeyBoardInline(text=status_1, callback_data=f'Select_Acc {account[login]}'),
                    KeyBoardInline(text=status_2, callback_data=f'Select_Acc {account[login + 1]}'))
            elif login % 2 != 0 and len(account) <= int(f'{login + page}'):
                login += 1
                if account[login] in status_account:
                    status = f'{account[login]} | 🟢\n'
                else:
                    status = f'{account[login]} | 🔴\n'
                AccountMenu.add(KeyBoardInline(text=status, callback_data=f'Select_Acc {account[login]}'))
        except IndexError:
            pass
    if len(account) <= 10:
        pass
    elif page == 0:
        AccountMenu.add(KeyBoardInline(text='Вперед ➡️', callback_data='Select_Acc NextPage'))
    elif page == len(account) // 10:
        AccountMenu.add(KeyBoardInline(text='⬅️ Назад', callback_data='Select_Acc PrevPage'))
    else:
        AccountMenu.row(KeyBoardInline(text='⬅️ Назад', callback_data='Select_Acc PrevPage'),
                        KeyBoardInline(text='Вперед ➡️', callback_data='Select_Acc NextPage'))

    AccountMenu.row(KeyBoardInline(text='Загрузить maFile', callback_data=f'Select_Acc maFile'),
                    KeyBoardInline(text='Добавить логин и пароль', callback_data=f'Select_Acc LogPass'))
    AccountMenu.add(KeyBoardInline(text='Обновить аккаунты', callback_data=f'Select_Acc Update_Account'))
    AccountMenu.add(KeyBoardInline(text='❌', callback_data=f'Select_Acc Closed_Menu'))

    global page_account
    page_account = await bot.send_message(chat_id=CHAT_ID,
                                          text=f'<b>Общее количество аккаунтов: {len(account)}\n'
                                               f'Страница [{page + 1} / {len(account) // 10 + 1}]</b>\n',
                                          parse_mode='HTML',
                                          reply_markup=AccountMenu)
    try:
        await message.delete()
    except AttributeError:
        pass


@dp.message_handler(filters.IDFilter(user_id=CHAT_ID), text='Фарм 🕹')
async def Beast_Farm(message: types.message):
    await message.delete()
    await SendMSG('Фарм 🕹\nВыберите действие:', FarmKeyboard)


@dp.message_handler(filters.IDFilter(user_id=CHAT_ID), text='Настройки ⚙️')
async def Beast_Settings(message: types.message):
    await message.delete()
    await SendMSG('Настройки ⚙️\nВыберите действие:', SettingsKeyboard)


@dp.message_handler(filters.IDFilter(user_id=CHAT_ID), text='Сервер 💻')
async def Beast_Server(message: types.message):
    await message.delete()
    enum = []
    for x in process_iter(): enum.append(x.name())
    if enum.count('srcds.exe') > 0 and ip_address != '':
        adrs = ip_address.split(':')
        adrs = str(adrs[0]), int(adrs[1])
        if len(a2s.players(adrs)) > 0:
            out = 'Сервер 💻\n\nВ данный момент на сервер:\n'
            for i in range(len(a2s.players(adrs))):
                nick = str(a2s.players(adrs)[i]).split('name=')[-1].split(',')[0].replace("'", "")
                timer = str(a2s.players(adrs)[i]).split('duration=')[-1].split(',')[0].replace("'", "").replace(')','').split('.')
                timer = int(timer[0])
                out += f'\n👤{nick} | Провел на сервере: {time.strftime("%H:%M:%S", time.gmtime(timer))}'
            await SendMSG(f'{out}\n\n Выберите действие:', ServerKeyboard)
        else:
            out = 'Сервер 💻\n\nВ данный момент на сервер:\n\nПусто :('
            await SendMSG(f'{out}\n\n Выберите действие:', ServerKeyboard)
    else:
        await SendMSG('Сервер 💻\nВ данный момент выключен!\nВыберите действие:', ServerKeyboard)


@dp.message_handler(filters.IDFilter(user_id=CHAT_ID), text='Статистика 📔')
async def Beast_Stats(message: types.message):
    await message.delete()
    out = '✨ Статистика ваших кейсов ✨\n'
    out += '\nЗа всё время вам выпало:'
    Case = readJson('json/AccountCase.json')
    all_cost = 0
    temp_cases = []
    all_cases = []
    for data in Case:
        all_cost += float(Case[data]['Price'])
        temp_cases.append(Case[data]['Case'])
    for check in temp_cases:
        count = temp_cases.count(check)
        if check not in all_cases:
            all_cases.append(check)
            out += f'\n{check}: {count} шт.'
    out += f'\n\n🔸Общая стоимость кейсов: {math.ceil(all_cost)}₽\n'
    out += f'\nЗа неделю вам выпало:'
    all_cost = 0
    temp_cases = []
    all_cases = []
    now = datetime.now()
    now = now.replace(microsecond=0)
    delta = timedelta(days=7)
    for data in Case:
        data = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
        if data > (now - delta):
            all_cost += float(Case[str(data)]['Price'])
            temp_cases.append(Case[str(data)]['Case'])
    for check in temp_cases:
        count = temp_cases.count(check)
        if check not in all_cases:
            all_cases.append(check)
            out += f'\n{check}: {count} шт.'
    out += f'\n\n🔸Стоимость недельного дропа {math.ceil(all_cost)}₽'
    await SendMSG(out, StatsKeyboard)


@dp.message_handler(filters.IDFilter(user_id=CHAT_ID), text='Другое 📎')
async def Beast_Other(message: types.message):
    await message.delete()
    await SendMSG('Другое 📎\nВыберите действие:', OtherKeyboard)


# endregion


# region Аккаунты


@dp.callback_query_handler(lambda c: c.data.startswith('Select_Acc'))
async def Beast_CallBack_Selected(callback: types.CallbackQuery):
    global acc, page
    acc = callback.data.replace('Select_Acc', '').strip()
    if acc == 'maFile':
        await callback.message.edit_text(text=f'<b>Отправьте maFile</b>', parse_mode='HTML')
        await Account_Menu.Account_maFiles.set()
    elif acc == 'LogPass':
        await callback.message.edit_text(text=f'<b>Напишите логин и пароль в формате <i>login:password</i></b>',
                                         parse_mode='HTML')
        await Account_Menu.Account_logpass.set()
    elif acc == 'NextPage':
        page += 1
        await page_account.delete()
        await Beast_Account(0)
    elif acc == 'PrevPage':
        page -= 1
        await page_account.delete()
        await Beast_Account(0)
    elif acc == 'Update_Account':
        await callback.message.edit_text(text='<b>Создание аккаунтов, это займет некоторое время!</b>', parse_mode='HTML')
        accounts = {}
        dir_name = os.path.abspath("./maFiles")
        file_logpass = open('json/logpass.txt')
        for account, mafile in product(file_logpass, os.listdir(dir_name)):
            if account != '\n':
                account_pair = account.split(':')
                info = readJson(f'{dir_name}/{mafile}')
                if info['account_name'].lower() == account_pair[0].lower():
                    SteamID = info['Session']['SteamID']  # Получение SteamID
                    Secret = info['shared_secret']  # Получение SharedSecret
                    link = f'https://steamid.pro/ru/lookup/{SteamID}'
                    responce = requests.get(link).text
                    soup = BeautifulSoup(responce, 'lxml')
                    result = soup.find('div', {'class': 'col-lg-6 col-12'}).find_all('tr')
                    AccountID = result[1].text  # Получение AccountID
                    Steam2ID = result[3].text  # Получение Steam2ID
                    AccountID = AccountID.replace('AccountID', '').strip()
                    Steam2ID = Steam2ID.replace('Steam2 ID', '').strip()[-9:]
                    accounts[account_pair[0].lower()] = {'login': str(account_pair[0].lower()),
                                                         'password': str(account_pair[1].replace('\n', '')),
                                                         'UserData': str(AccountID),
                                                         'SteamID': str(SteamID),
                                                         'Steam2 ID': str(Steam2ID),
                                                         'shared_secret': str(Secret)}
        writeJson('json/accounts.json', accounts)
        await callback.message.delete()
        await SendMSG('Список аккаунтов обновлен')
    elif acc == 'Closed_Menu':
        await callback.message.delete()
    else:
        await callback.message.edit_text(text=f'<b>{acc} | Выберите действие:</b>', parse_mode='HTML',
                                         reply_markup=AccountFunction)


@dp.message_handler((filters.IDFilter(user_id=CHAT_ID)), lambda message: message.document, content_types=['document'],
                    state=Account_Menu.Account_maFiles)
async def Beast_FSM_Mafile(message: types.Message, state: FSMContext):
    await bot.download_file_by_id(file_id=message.document.file_id, destination=f'maFiles/{message.document.file_name}')
    await SendMSG(f'Файл <i>{message.document.file_name}</i> загружен.')
    await message.delete()
    await state.finish()


@dp.message_handler(state=Account_Menu.Account_logpass)
async def Beast_FSM_LogPass(message: types.Message, state: FSMContext):
    await state.update_data(Account_logpass=message.text)
    data = await state.get_data()
    data = data['Account_logpass']
    if data.find(':') > 0:
        f = open('json/logpass.txt', 'a')
        f.write(f'{data}\n')
        f.close()
        await SendMSG('Аккаунт добавлен!')
    else:
        await SendMSG('Ошибка 🚫\n'
                      'Неправильный формат')
    await message.delete()
    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith('Account'))
async def Beast_CallBack_Account(callback: types.CallbackQuery):
    Status = []
    for temp in readJson('json/launched_accounts.json'): Status.append(temp)
    call = callback.data.replace('Account_', '').strip()
    if call == 'Start':
        if Status.count(acc):
            await callback.message.edit_text(f'<b>{acc} | Включен!</b>', parse_mode='HTML')
        else:
            await callback.message.delete()
            await LaunchSelect(acc)
    elif call == 'Stop':
        if Status.count(acc):
            await StoppingSelect(acc)
            await callback.message.edit_text(f'<b>{acc} | Выключение аккаунта!</b>', parse_mode='HTML')
        else:
            await callback.message.edit_text(f'<b>{acc} | Уже выключен!</b>', parse_mode='HTML')
    elif call == 'Reload':
        if Status.count(acc):
            await callback.message.edit_text(f'<b>{acc} | Перезагрузка аккаунта!</b>', parse_mode='HTML')
            await StoppingSelect(acc)
            await LaunchSelect(acc)
        else:
            await callback.message.edit_text(f'<b>{acc} | Аккаунт не запущен!</b>', parse_mode='HTML')
    elif call == 'Guard':
        Steam_Guard = generate_one_time_code(readJson("json/accounts.json")[acc]["shared_secret"])
        await callback.message.edit_text(f'<b>{acc} | Steam Guard - <code>{Steam_Guard}</code></b>', parse_mode='HTML')
    elif call == 'Profile':
        info = readJson('json/accounts.json')
        URLMark = types.InlineKeyboardMarkup()
        URLButton = InlineKeyboardButton(text='Открыть',
                                         url=f'https://steamcommunity.com/profiles/{info[acc]["SteamID"]}/')
        URLMark.add(URLButton)
        await callback.message.edit_text(f'<b>{acc} | Ссылка на аккаунт!</b>', parse_mode='HTML', reply_markup=URLMark)
    elif call == 'GoMenu':
        await callback.message.delete()
        await Beast_Account(0)
    elif call == 'Screen':
        await callback.message.delete()
        info = readJson('json/launched_accounts.json')
        if list(info).count(acc):
            try:
                with mss.mss() as sct:
                    autoit.win_activate(info[acc]["win_csgo_title"])
                    autoit.win_wait_active(info[acc]["win_csgo_title"])
                    time.sleep(1)
                    left, top, width, height = autoit.win_get_pos(info[acc]["win_csgo_title"])
                    monitor = {"top": top, "left": left, "width": 240, "height": 149}
                    output = f"{acc}.png"
                    sct_img = sct.grab(monitor)
                    mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
                await bot.send_photo(chat_id=CHAT_ID, photo=open(f'{acc}.png', 'rb'))
                os.remove(f'{acc}.png')
            except Exception as e:
                await SendMSG(f'Ошибка: {e}')
        else:
            await SendMSG('Аккаунт не запущен!')


# endregion


# region Фарм

def ParsingSummoner():
    path = readJson('Settings/settings.json')['auto_server_ip'][0:-10] + \
           '\\csgo\\addons\\sourcemod\\logs\\DropsSummoner.log'
    Status = readJson('json/DataCase.json')
    account = readJson('json/accounts.json')
    pattern = r'L (?P<data>\d{2}/\d{2}/\d{4} - \d{2}:\d{2}):\d{2}[^\s<]+.*<STEAM_\d:\d:(?P<Steam2ID>\d*)'
    current_time = datetime.now()
    Result = {}
    Information = {}
    line = open(path, 'r', encoding='utf-8').readlines()
    if line:
        Count = {}
        for log, acc_login in product(line, account):
            finder = re.search(pattern, log)
            Steam2 = finder.group('Steam2ID')
            data = finder.group('data')
            if account[acc_login]['Steam2 ID'] == Steam2 and list(readJson('json/DataCase.json')).count(acc_login) == 0:
                data = data.replace('/', '.').replace(' - ', ' ').replace(' ', '.').replace(':', '.')
                Count.update({acc_login: {"data": data}})
        if Count != {}:
            writeJson('json/DataCase.json', Count)
    if line:
        for log, acc_login, acc_time in product(line, account, Status):
            finder = re.search(pattern, log)
            data = finder.group('data')
            Steam2 = finder.group('Steam2ID')
            timing = data.replace('/', '.').replace(' - ', ' ').replace(' ', '.').replace(':', '.')
            if account[acc_login]["Steam2 ID"] == Steam2:
                login = account[acc_login]['login']
                account_time = Status[acc_time]['data']
                check = (login == acc_time)
                l_month, l_day, l_year, l_hour, l_minute = account_time.split('.')
                t_month, t_day, t_year, t_hour, t_minute = timing.split('.')
                json_time = datetime(int(l_year), int(l_month), int(l_day), int(l_hour), int(l_minute))
                log_time = datetime(int(t_year), int(t_month), int(t_day), int(t_hour), int(t_minute))
                t_delta = timedelta(days=6, hours=21, minutes=55)
                diff_time = json_time + t_delta
                if diff_time < log_time and check:  # прошла ли неделя и запись в json
                    Result[login] = {'data': timing}
                if diff_time < current_time and check:  # Запуск, если прошла неделя
                    Information[login] = {'Status': 'ON'}
                if diff_time > current_time and check:  # Ожидание, если не прошла неделя
                    Information[login] = {'Status': 'OFF'}
    if Result != {}:
        writeJson('json/DataCase.json', Result)
        ParsingSummoner()
    else:
        return Information


def Farm_Start():
    Result = {}
    Information = ParsingSummoner()
    if Information is None: Information = ParsingSummoner()
    if Information is not None and Information != {}:
        for login in Information:
            if Information[login]['Status'] == 'ON':
                Result[login] = {"Status": 'ON'}
        if Result == {}:
            return 'NotFarmAccount'
        else:
            return Result
    elif Information == {}:
        return 'NotAccount'


@dp.callback_query_handler(lambda c: c.data.startswith('Farm_'))
async def Beast_CallBack_Selected(callback: types.CallbackQuery):
    global Farm_Call
    Farm_Call = callback.data.replace('Farm_', '').strip()
    if Farm_Call == 'Start':
        if readJson('Settings/settings.json')['auto_server_ip'] != 'None':
            info = Farm_Start()
            await callback.message.delete()
            if info == 'NotAccount':
                await SendMSG('Аккаунты в DropsSummoner отсутствуют!')
            elif info == 'NotFarmAccount':
                await SendMSG('В данный момент, нет аккаунтов для фарма!')
            else:
                out = 'Аккаунты которые будут фармить:\n'
                for login in info:
                    out += f'\n👤 {login}'
                out += '\n\n⚠️Производится запуск аккаунтов\nПожалуйста не трогайте компьютер!'
                await SendMSG(out)
                for login in info:
                    await LaunchSelect(login)
        else:
            await callback.message.delete()
            await SendMSG('Ошибка 🚫\n'
                          'У Вас не указан путь до IDLE сервера!\n'
                          'Указать его можно перейдя по пути:\n'
                          'Настройки > Пути > IDLE')
    elif Farm_Call == 'Stop':
        await callback.message.edit_text(f'<b>Производится остановка аккаунтов!</b>', parse_mode='HTML')
        await StoppingAll()
    elif Farm_Call == 'Info':
        ParsingSummoner()
        info = readJson('json/DataCase.json')
        if info != {}:
            now = datetime.now()
            t_delta = timedelta(days=6, hours=21, minutes=55)
            out = 'Время дропа:\n'
            for login in info:
                month, day, year, hour, minute = info[login]['data'].split('.')
                account_time = datetime(int(year), int(month), int(day), int(hour), int(minute))
                diff_time = account_time + t_delta
                result_time = diff_time - now
                if result_time.days < 0:
                    a_time = account_time
                    out += f'\n┌{login} ✅\n├Аккаунт готов фармить!\n└Последний дроп: {a_time.day}.{a_time.month}.{a_time.year} {a_time.hour}:{a_time.minute}\n'
                elif result_time.days > 0:
                    a_time = account_time
                    day = result_time.days
                    res_sec = time.strftime("%H:%M:%S", time.gmtime(result_time.seconds))
                    out += f'\n┌{login} ⏳\n├Осталось {day} дн. {res_sec}\n└Последний дроп: {a_time.day}.{a_time.month}.{a_time.year} {a_time.hour}:{a_time.minute}\n'
                elif result_time.days == 0:
                    a_time = account_time
                    res_sec = time.strftime("%H:%M:%S", time.gmtime(result_time.seconds))
                    out += f'\n┌{login} ⏳\n├Осталось {res_sec}\n└Последний дроп: {a_time.day}.{a_time.month}.{a_time.year} {a_time.hour}:{a_time.minute}\n'
                else:
                    out += f'\n┌{login} 🚫\n└Не удалось получить информацию о аккаунте!'
            await callback.message.edit_text(f'<b>{out}</b>', parse_mode='HTML')
    elif Farm_Call == 'WinHide':
        launched = readJson('json/launched_accounts.json')
        for login in launched:
            hwnd = win32gui.FindWindow(None, launched[login]["win_csgo_title"])
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        await callback.message.edit_text(text='<b>Аккаунты свернуты!\nВыберите действие:</b>',
                                         parse_mode='HTML',
                                         reply_markup=FarmKeyboard)
    elif Farm_Call == 'WinShow':
        launched = readJson('json/launched_accounts.json')
        for login in launched:
            hwnd = win32gui.FindWindow(None, launched[login]["win_csgo_title"])
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        await callback.message.edit_text(text='<b>Аккаунты развернуты!\nВыберите действие:</b>',
                                         parse_mode='HTML',
                                         reply_markup=FarmKeyboard)
    elif Farm_Call == 'Close':
        await callback.message.delete()


# endregion


# region Настройки

@dp.callback_query_handler(lambda c: c.data.startswith('Settings_'))
async def Beast_CallBack_Selected(callback: types.CallbackQuery):
    global Settings_Call
    Settings_Call = callback.data.replace('Settings_', '').strip()
    if Settings_Call == 'Steam':
        await callback.message.edit_text(f'<b>Введите новый путь до Steam\nПример: C:\Program Files (x86)\Steam</b>', parse_mode='HTML')
        await Settings_json.Steam_Path.set()
    elif Settings_Call == 'IDLE':
        await callback.message.edit_text(f'<b>Введите новый путь до IDLE\nПример: C:\Server\Steam\steamapps\common\Counter-Strike Global Offensive Beta - Dedicated Server</b>', parse_mode='HTML')
        await Settings_json.Server_Idle.set()
    elif Settings_Call == 'ConfigP':
        out = 'Аккаунты где созданы настройки под фарм:\n'
        info = readJson('json/accounts.json')
        accountID_dirs = os.listdir(readJson("settings/settings.json")["steam_path"][:-10] + "\\userdata")
        for account in info:
            uid = info[account]["Steam2 ID"]
            if uid in accountID_dirs:
                folder = readJson("settings/settings.json")["steam_path"][:-10] + f"\\userdata\\{uid}\\730\\local\\cfg"
                video = open(f'{folder}\\video.txt', "w")
                video_panel = open(f'Settings/video_panel.txt', "r")
                video.write(video_panel.read())
                videodefaults = open(f'{folder}\\videodefaults.txt', "w")
                videodefaults_panel = open(f'Settings/videodefaults_panel.txt', "r")
                videodefaults.write(videodefaults_panel.read())
                out += f'\n👤 {account}'
        await callback.message.edit_text(f'<b>{out}</b>', parse_mode='HTML')
    elif Settings_Call == 'AutoBot':
        await callback.message.edit_text(f'<b>Ошибка 🚫\nФункция в разработке.</b>', parse_mode='HTML')
    elif Settings_Call == 'AutoIDLE':
        await callback.message.delete()
        info = readJson('Settings/settings.json')
        if info['auto_server_ip'] == 'None':
            await SendMSG('Ошибка 🚫\n'
                          'У Вас не указан путь до IDLE сервера')
        elif info['auto_start_server'] == 'OFF' and info['auto_server_ip'] != 'None':
            settings = {'auto_start_server': 'ON'}
            writeJson('Settings/settings.json', settings)
            await SendMSG('Автозапуск сервера включен')
        elif info['auto_start_server'] == 'ON' and info['auto_server_ip'] != 'None':
            settings = {'auto_start_server': 'OFF'}
            writeJson('Settings/settings.json', settings)
            await SendMSG('Автозапуск сервера выключен')
    elif Settings_Call == 'Optimize':
        await callback.message.edit_text(f'<b>Запуск оптимизации!</b>', parse_mode='HTML')
        out = 'Результаты оптимизации:\n'
        CreateCFG()
        accountID_dirs = os.listdir(readJson("settings/settings.json")["steam_path"][:-10] + "\\userdata")
        info = readJson("json/accounts.json")
        for account in info:
            if info[account]["shared_secret"]:
                uid = info[account]["UserData"]
                if uid not in accountID_dirs:
                    os.makedirs(
                        readJson("settings/settings.json")["steam_path"][:-10] + f"\\userdata\\{uid}\\730\\local\\cfg")
                    folder = readJson("settings/settings.json")["steam_path"][
                             :-10] + f"\\userdata\\{uid}\\730\\local\\cfg"
                    video = open(f'{folder}\\video.txt', "w")
                    video_panel = open(f'Settings/video_panel.txt', "r")
                    video.write(video_panel.read())
                    videodefaults = open(f'{folder}\\videodefaults.txt', "w")
                    videodefaults_panel = open(f'Settings/videodefaults_panel.txt', "r")
                    videodefaults.write(videodefaults_panel.read())
                    out += f'\n{account} | Настройки созданы'
                else:
                    out += f'\n{account} | Уже настроен'
            else:
                out += f'\n{account} | Отсутствует maFile'
        await callback.message.edit_text(f'<b>{out}</b>', parse_mode='HTML')
    elif Settings_Call == 'Close':
        await callback.message.delete()


@dp.message_handler(state=Settings_json.Steam_Path)
async def Beast_FSM_SteamPath(message: types.Message, state: FSMContext):
    await state.update_data(Steam_Path=message.text)
    await message.delete()
    settings = {}
    data = await state.get_data()
    data = data['Steam_Path']
    if data[-9:] == 'steam.exe':
        settings['steam_path'] = data
    else:
        data += '\\steam.exe'
    settings['steam_path'] = data
    writeJson('Settings/settings.json', settings)
    await SendMSG(f'Новый путь до Steam:\n'
                  f'{data}')
    await state.finish()


@dp.message_handler(state=Settings_json.Server_Idle)
async def Beast_FSM_ServerIDLE(message: types.Message, state: FSMContext):
    await state.update_data(Server_Idle=message.text)
    await message.delete()
    settings = {}
    data = await state.get_data()
    data = data['Server_Idle']
    if data[-9:] == 'start.bat':
        pass
    else:
        data += '\\start.bat'
    settings['auto_server_ip'] = data
    writeJson('Settings/settings.json', settings)
    await SendMSG(f'Новый путь до IDLE сервера:\n'
                  f'{data}')
    await state.finish()


# endregion


# region Сервер

@dp.callback_query_handler(lambda c: c.data.startswith('Server_'))
async def Beast_CallBack_Selected(callback: types.CallbackQuery):
    global Server_Call
    Server_Call = callback.data.replace('Server_', '').strip()
    if Server_Call == 'ON':
        await callback.message.delete()
        idle_path = readJson('Settings/settings.json')['auto_server_ip']
        if idle_path != 'None':
            enum = []
            for x in process_iter(): enum.append(x.name())
            if enum.count('srcds.exe') > 0:
                await SendMSG('Сервер включен')
            else:
                await SendMSG('Запуск сервера')
                await Startup_IDLE()
        else:
            await SendMSG('Ошибка 🚫\n'
                          'У вас не указан путь до IDLE')
    elif Server_Call == 'OFF':
        await callback.message.delete()
        idle_path = readJson('Settings/settings.json')['auto_server_ip']
        if idle_path != 'None':
            enum = []
            for x in process_iter():
                enum.append(x.name())
            if enum.count('srcds.exe') == 0:
                await SendMSG('Сервер выключен')
            else:
                await SendMSG('Выключение сервера')
                for proc in process_iter():
                    if proc.name() == 'srcds.exe':
                        proc.terminate()
                global ip_address
                ip_address = ''
        else:
            await SendMSG('Ошибка 🚫\n'
                          'У Вас не указан путь до IDLE')
    elif Server_Call == 'Close':
        await callback.message.delete()


# endregion


# region Статистика

@dp.callback_query_handler(lambda c: c.data.startswith('Stats_'))
async def Beast_CallBack_Stats(callback: types.CallbackQuery):
    global Stats_Call
    Stats_Call = callback.data.replace('Stats_', '').strip()
    if Stats_Call == 'Reload':
        path = readJson('Settings/settings.json')['auto_server_ip'][0:-10] + \
               '\\csgo\\addons\\sourcemod\\logs\\DropsSummoner.log'
        pattern = r'L (?P<data>\d{2}/\d{2}/\d{4} - \d{2}:\d{2}):\d{2}[^\s<]+.*<STEAM_\d:\d:(?P<Steam2ID>\d*)[^\s<]+.*\[(?P<Case>\d+)-\d+-\d+-\d+\]'
        line = open(path, 'r', encoding='utf-8').readlines()
        TimeCase = readJson('json/AccountCase.json')
        Result = {}
        if line:
            await callback.message.edit_text(text=f'<b>Обновление статистики..</b>', parse_mode='HTML')
            for log in line:
                finder = re.search(pattern, log)
                data = finder.group("data")
                Case = finder.group("Case")
                data = data.replace(' - ', '/').split('/')
                data = f"{data[2]}-{data[0]}-{data[1]} {data[3]}:00"
                if list(TimeCase).count(data) == 0:
                    Cases, Price = getPrice(int(Case))
                    Price = Price.replace(',', '.').strip()
                    Result[data] = {"Case": str(Cases), "Price": str(Price)}
                    writeJson('json/AccountCase.json', Result)
                    time.sleep(5)
            await callback.message.delete()
            await Beast_Stats(0)
    elif Stats_Call == 'Close':
        await callback.message.delete()


# endregion


# region Другое

@dp.callback_query_handler(lambda c: c.data.startswith('Other_'))
async def Beast_CallBack_Selected(callback: types.CallbackQuery):
    global Other_Call
    Other_Call = callback.data.replace('Other_', '').strip()
    if Other_Call == 'Timer':
        await callback.message.edit_text(f'<b>Через сколько хотите завершить сеанс?\n'
                                         f'Ответ в секундах, пример:\n'
                                         f'1ч - 3600\n'
                                         f'3ч - 10800\n'
                                         f'5ч - 18000</b>', parse_mode='HTML')
        await Timer_Setup.TimerINT.set()
    elif Other_Call == 'TimerOFF':
        os.system('shutdown -a')
        await callback.message.edit_text(f'<b>Таймер выключен</b>', parse_mode='HTML')
    elif Other_Call == 'Spec':
        await callback.message.edit_text(f'<b>Сбор информации.. ⏳</b>', parse_mode='HTML')
        computer = wmi.WMI()
        os_info = computer.Win32_OperatingSystem()[0]
        proc_info = computer.Win32_Processor()[0]
        gpu_info = computer.Win32_VideoController()[0]
        os_name = os_info.Caption
        os_version = ' '.join([os_info.Version, os_info.BuildNumber])
        system_ram = math.ceil(float(os_info.TotalVisibleMemorySize) / 1048576)
        await callback.message.edit_text(f'<b>Характеристики ПК 🖥\n\n'
                                         f'Операционная система: {os_name}\n'
                                         f'Версия системы: {os_version}\n'
                                         f'Процессор: {proc_info.Name}'
                                         f'Ядер: {proc_info.NumberOfCores}\n'
                                         f'Потоков: {proc_info.NumberOfLogicalProcessors}\n</b>'
                                         f'Оперативной памяти: {system_ram}\n'
                                         f'Видеокарта: {gpu_info.Name}', parse_mode='HTML')
    elif Other_Call == 'Close':
        await callback.message.delete()


@dp.message_handler(state=Timer_Setup.TimerINT)
async def Beast_FSM(message: types.Message, state: FSMContext):
    await state.update_data(TimerINT=message.text)
    await message.delete()
    data = await state.get_data()
    if int(data['TimerINT']) >= 0:
        os.system(f'shutdown -s -t {data["TimerINT"]}')
        await SendMSG(f'Ваш сеанс будет завершен через {data["TimerINT"]} секунд')
    else:
        await SendMSG(f'{data["TimerINT"]} не является числом!')
    await state.finish()


# endregion


# region Начальное меню
@dp.message_handler(filters.IDFilter(user_id=CHAT_ID), commands=['start'])
async def Beast_Start(message: types.message):
    await SendMSG(f'Приветствую тебя {message.from_user.first_name}!\n'
                  f'Очень надеемся что все понравится!', StartMenu)
    await message.delete()


async def BotOn(_):
    await SendMSG('Бот готов к работе! 🤖', StartMenu)


async def BotOff(_):
    await SendMSG('Бот завершает работу')

# endregion
