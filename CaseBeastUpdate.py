import os

# os.system('python.exe -m pip install --upgrade pip')
# os.system('pip install requests')
# os.system('pip install urllib3')


url = 'https://raw.githubusercontent.com/frifarik/CaseBeast/main/'


def Modules():
    modules = requests.get("https://pastebin.com/raw/EnSM2hcZ").text.split('\n')
    for module in modules:
        os.system(f"pip install {module}")


def Folders():
    folders = requests.get("https://pastebin.com/raw/EhQZ7t5Q").text.split('\n')
    for folder in folders:
        folder = folder.replace('\r', '')
        if os.path.exists(folder) is False: os.mkdir(folder[2:])


def Files():
    files = requests.get("https://pastebin.com/raw/1tnduXaX").text.split('\n')
    for file in files:
        file = file.strip()
        if os.path.exists(file) is False:
            response = requests.get(url + file)
            with open(file, 'wb') as f: f.write(response.content)


if __name__ == "__main__":
    import requests
    from urllib.parse import urlencode

    url = 'https://raw.githubusercontent.com/frifarik/CaseBeast/main/'
    Modules()
    Folders()
    Files()
    print("Загрузка окончена!!!\n" * 3)
    input()
