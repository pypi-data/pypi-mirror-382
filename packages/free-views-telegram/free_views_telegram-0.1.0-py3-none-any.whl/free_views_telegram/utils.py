from configparser import ConfigParser
from threading import active_count
from time import sleep as swait
from os import system, name
from .telegram import Api
from re import search
from sys import exit


THREADS = 400
LOGO = '''
def print_d(text, color='white'):
    print(f"\033[38;5;51m{' ' * ((80 - len(text)) // 2)}{text}\033[0m")


n_color = "white"  

print_d("- - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
print_d(f"[ library - Views_Telegram - ]", n_color)
print_d("- - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
print_d("[ programmer  - @O_O_P_V - ]",n_color)
print_d("- - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
print_d("[ VERSION - 1V - ]", n_color)
print_d("- - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
'''

error_file = open('errors.txt', 'a+', encoding='utf-8')
logger = lambda error: error_file.write(f'{error}\n')


def config_loader():
    try: 
        cfg = ConfigParser(interpolation=None)
        cfg.read("config.ini", encoding="utf-8")
        return (
            cfg["HTTP"].get("Sources").splitlines(), 
            cfg["SOCKS4"].get("Sources").splitlines(), 
            cfg["SOCKS5"].get("Sources").splitlines()
        )
    except KeyError: 
        print(' [ Error ] config.ini not found!')
        swait(3)
        exit()


def input_loader():
    url_input = search(r'(https?:\/\/t\.me\/)?([^/]+)/(\d+)', input(' [ INPUT ] Enter Post URL: '))
    if url_input: 
        _, channel, post = url_input.groups()
        return channel, post
    else: 
        print(' [ ERROR ] Channel Or Post Not Found!')
        swait(3)
        exit()


def display():
    print(' [ OUTPUT ] Started ( Wait few seconds to run threads )');swait(7)
    while int(active_count()) < THREADS-100: swait(0.05)
    system('cls' if name == 'nt' else 'clear')
    
    def inner():
        print(LOGO)
        print(f'''
    [ Live Views ]: {Api.real_views}
        ''')
    
    return inner


