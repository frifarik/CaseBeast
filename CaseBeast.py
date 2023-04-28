import ctypes
import json
import os
import sys

try:
    if ctypes.windll.shell32.IsUserAnAdmin():
        info = json.loads(open(os.path.abspath('json/Telegram.json'), encoding='utf-8').read())
        if info["Telegram"]["Token_Bot"] == "None" or info["Telegram"]["Chat_ID"] == "None":
            print('У вас не указан Token_Bot или Chat_ID в json/Telegram.json')
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
