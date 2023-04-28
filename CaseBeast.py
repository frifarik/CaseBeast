import ctypes
import json
import os
import sys

try:
    if ctypes.windll.shell32.IsUserAnAdmin():
        from urllib.parse import urlencode
        import requests

        data = {}
        base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
        if os.path.exists('./maFiles') is False: os.mkdir('maFiles')
        if os.path.exists('./json') is False: os.mkdir('json')
        if os.path.exists('./Settings') is False: os.mkdir('Settings')
        if os.path.exists('json/logpass.txt') is False: open('json/logpass.txt', 'wb').close()
        if os.path.exists('json/Telegram.json') is False:
            open('json/Telegram.json', 'wb').close()
            with open('json/Telegram.json', 'w', encoding='utf-8') as outfile:
                json.dump({'Telegram': {'Token_Bot': 'None', 'Chat_ID': 'None'}}, outfile, indent=4)
        if os.path.exists('json/accounts.json') is False:  # Создание файла accounts.json
            open('json/accounts.json', 'wb').close()
            with open('json/accounts.json', 'w', encoding='utf-8') as outfile: json.dump(data, outfile, indent=4)
        if os.path.exists('json/launched_accounts.json') is False:  # Создание файла launched_accounts.json
            open('json/launched_accounts.json', 'wb').close()
            with open('json/launched_accounts.json', 'w', encoding='utf-8') as outfile: json.dump(data, outfile,
                                                                                                  indent=4)
        if os.path.exists('json/AccountCase.json') is False:
            open('json/AccountCase.json', 'wb').close()
            with open('json/AccountCase.json', 'w', encoding='utf-8') as outfile: json.dump(data, outfile, indent=4)
        if os.path.exists('Settings/settings.json') is False:
            open('Settings/settings.json', 'wb').close()
            with open('Settings/settings.json', 'w', encoding='utf-8') as outfile: json.dump(data, outfile, indent=4)
        file = requests.get("https://pastebin.com/raw/1tnduXaX").text.split('\n')
        for temp in file:
            temp = temp.strip()
            url = temp.split('|')
            if os.path.exists(url[0]) is False:
                response = requests.get(base_url + urlencode(dict(public_key=f'https://disk.yandex.ru/d/{url[1]}')))
                download_response = requests.get(response.json()['href'])
                with open(url[0], 'wb') as f: f.write(download_response.content)

        os.system('CLS')
        info = json.loads(open(os.path.abspath('json/Telegram.json'), encoding='utf-8').read())
        if info["Telegram"]["Token_Bot"] == "None" or info["Telegram"]["Chat_ID"] == "None":
            print('У вас не указан Token_Bot или Chat_ID в json/Telegram.json')
            input('')
        else:
            from CaseBeast_Function import *

            executor.start_polling(dp, skip_updates=True, on_startup=BotOn, on_shutdown=BotOff)
    else:
        import py_win_keyboard_layout

        py_win_keyboard_layout.change_foreground_window_keyboard_layout(0x04090409)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
except Exception as ex:
    input(ex)
    time.sleep(3)
