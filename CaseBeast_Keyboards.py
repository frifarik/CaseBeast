from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

KeyBoardInline = types.InlineKeyboardButton

# Начальное меню:
StartMenu = ReplyKeyboardMarkup(resize_keyboard=False, one_time_keyboard=False)
AccountButton = KeyboardButton('Аккаунты 👥')
FarmButton = KeyboardButton('Фарм 🕹')
SettingsButton = KeyboardButton('Настройки ⚙️')
ServerButton = KeyboardButton('Сервер 💻')
StatisticsButton = KeyboardButton('Статистика 📔')
OtherButton = KeyboardButton('Другое 📎')
StartMenu.row(AccountButton, SettingsButton, FarmButton).row(ServerButton, StatisticsButton, OtherButton)

# Аккаунты
AccountFunction = types.InlineKeyboardMarkup()
AccountFunction.row(KeyBoardInline(text='Запустить ▶️', callback_data='Account_Start'),
                    KeyBoardInline(text='Остановить ⏹', callback_data='Account_Stop'))
AccountFunction.row(KeyBoardInline(text='Перезапустить 🔁', callback_data='Account_Reload'),
                    KeyBoardInline(text='Получить Guard 🔐', callback_data='Account_Guard'))
AccountFunction.row(KeyBoardInline(text='Профиль аккаунта 🔗', callback_data='Account_Profile'),
                    KeyBoardInline(text='Скриншот 🖼', callback_data='Account_Screen'))
AccountFunction.add(KeyBoardInline(text='⬅️ Назад', callback_data='Account_GoMenu'))

# Фарм
FarmKeyboard = types.InlineKeyboardMarkup()
FarmKeyboard.row(KeyBoardInline(text='Начать ▶️', callback_data='Farm_Start'),
                 KeyBoardInline(text='Остановить ⏹', callback_data='Farm_Stop'))
FarmKeyboard.row(KeyBoardInline(text='Свернуть окна ⤵️', callback_data='Farm_WinHide'),
                 KeyBoardInline(text='Развернуть окна ⤴️', callback_data='Farm_WinShow'))
FarmKeyboard.add(KeyBoardInline(text='Когда фармить ⁉️', callback_data='Farm_Info'))
FarmKeyboard.add(KeyBoardInline(text='❌', callback_data=f'Farm_Close'))

# Настройки
SettingsKeyboard = types.InlineKeyboardMarkup()
SettingsKeyboard.row(KeyBoardInline(text='Путь Steam 🛤', callback_data='Settings_Steam'),
                     KeyBoardInline(text='Путь IDLE 🛤', callback_data='Settings_IDLE'))
SettingsKeyboard.add(KeyBoardInline(text='Конфиг для игры ⚙️', callback_data='Settings_ConfigP'))
SettingsKeyboard.row(KeyBoardInline(text='Автозапуск бота 🛎', callback_data='Settings_AutoBot'),
                     KeyBoardInline(text='Автозапуск сервера 🛎', callback_data='Settings_AutoIDLE'))
SettingsKeyboard.add(KeyBoardInline(text='Оптимизация 📈', callback_data='Settings_Optimize'))
SettingsKeyboard.add(KeyBoardInline(text='❌', callback_data=f'Settings_Close'))

# Сервер
ServerKeyboard = types.InlineKeyboardMarkup()
ServerKeyboard.row(KeyBoardInline(text='Включить ▶️', callback_data='Server_ON'),
                   KeyBoardInline(text='Выключить ⏹', callback_data='Server_OFF'))
ServerKeyboard.add(KeyBoardInline(text='❌', callback_data='Server_Close'))

# Статистика

StatsKeyboard = types.InlineKeyboardMarkup()
StatsKeyboard.add(KeyBoardInline(text='Обновить ❇️', callback_data='Stats_Reload'))
StatsKeyboard.add(KeyBoardInline(text='❌', callback_data=f'Stats_Close'))

# Другое
OtherKeyboard = types.InlineKeyboardMarkup()
OtherKeyboard.row(KeyBoardInline(text='Поставить таймер ⏱', callback_data='Other_Timer'),
                  KeyBoardInline(text='Выключить таймер 🚫', callback_data='Other_TimerOFF'))
OtherKeyboard.add(KeyBoardInline(text='Характеристики ПК 🖥', callback_data='Other_Spec'))
OtherKeyboard.add(KeyBoardInline(text='❌', callback_data=f'Other_Close'))
