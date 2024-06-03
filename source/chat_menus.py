import os
import time
from typing import List
from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog, message_dialog
from termcolor import colored

def client_input(ttl, txt):
    return input_dialog(
        title=ttl,
        text=txt).run()

def login():
    return input_dialog(
        title='Inicia Sesión',
        text='Introduce tu nombre de usuario:').run()

def ask_port():
    return input_dialog(
        title='Regístrate',
        text='Introduce tu puerto:').run()

def ask_who():
    return input_dialog(
        title='Chat privado',
        text='Introduce el nombre del usuario con el que quieres hablar:').run()

def write_an_insult():
    return input_dialog(
        title='Insult channel',
        text='Introduce un insulto para arruinarle la vida a alguien:').run()

def client_modal(txt):
    return message_dialog(
        title= 'AVISO',
        text= txt + '\nPulsa ENTER para volver al menú.').run()

def main_menu():
    return radiolist_dialog(
        title="MAIN MENU",
        text="Elige una opción:", 
        cancel_text="Salir",
        values=[
            ('1', '[1] Chat Privado'),
            ('2', '[2] Chat Grupal'),
            ('3', '[3] Descubrir Chats'),
            ('4', '[4] Insult channel')
        ]
    ).run()

def chat_private_menu():
    return radiolist_dialog(
        title="PRIVATE CHAT",
        text="Elige una opción:", 
        cancel_text="Salir",
        values=[
            ('1', '[1] Abrir petición de chat'),
            ('2', '[2] Consultar peticiones')
        ]
    ).run()

def chat_group_menu():
    return radiolist_dialog(
        title="CHAT GROUP",
        text="Elige una opción:", 
        cancel_text="Salir",
        values=[
            ('1', '[1] Mis grupos'),
            ('2', '[2] Unirse a un nuevo chat grupal'),
            ('3', '[3] Crear un chat grupal')
        ]
    ).run()


def insult_channel_menu():
    return radiolist_dialog(
        title="INSULT_CHANNEL",
        text="Elige una opción:", 
        cancel_text="Salir",
        values=[
            ('1', '[1] Insult someone'),
            ('2', '[2] Insult me')
        ]
    ).run()


def show_chat_requests(requests:List[str]):
    options = []
    for rq in requests:
        options.append((rq, rq))

    return radiolist_dialog(
            title="PRIVATE CHAT",
            text="Con quién quieres hablar?:", 
            cancel_text="Salir",
            values=options
        ).run()

def show_chat_groups(groups:List[str]):
    options = []
    for group in groups:
        options.append((group, '-> '+group))

    return radiolist_dialog(
            title="CHAT GROUP",
            text="A qué chat grupal quieres acceder?",
            cancel_text="Salir",
            values=options
        ).run()


def show_discovered_chats(users:List[str]):
    message = ''
    for user in users:
        message += f' -> {user}\n'

    return message_dialog(
        title= 'Chats Encontrados',
        text= message).run()


def show_chat_header(name, type):
    # Hace un clear de la consola
    os.system('clear')
    print(colored(f' {type} CHAT ', 'yellow'), end='')
    print(colored(f'{name}', 'blue'))
    print(colored('---------------------------------\n', 'yellow'))


def refresh_chat_private(chat):
    show_chat_header('PRIVATE', '')
    # Por cada mensaje enviado en este chat
    for message in chat:
        # Muestra el prompt del sender con el mensaje
        if message[0] == 'me':
            print(colored('-->  You: ' + message[1], 'green'))
        else:
            print(colored('<--  Other: ' + message[1], 'red'))

    print(colored('-->  You: ', 'green'), end='')


def refresh_chat_group(session, groupName):
    show_chat_header(groupName, 'GROUP')
    # Por cada mensaje enviado en este chat
    for chatReq in session.groupal_chats[groupName][1]:
        # Muestra el prompt del sender con el mensaje
        if chatReq.username == session.username:
            print(colored('-->  You: ' + chatReq.message, 'green'))
        else:
            print(colored(f'<--  {chatReq.username}: {chatReq.message}', 'magenta'))

    print(colored('-->  You: ', 'green'), end='')


def wait_private_response(chat: List[str]):
    count = 0
    try:
        while len(chat) == 0:
            show_chat_header('PRIVATE', '')
            print("Waiting for response" + ("." * count))
            count = (count + 1) % 4
            time.sleep(0.3)
    except KeyboardInterrupt:
        client_modal("Has cerrado el chat")   

def wait_discovey_response():
    count = 0
    time_count = 0
    while time_count < 3:
        os.system('clear')
        print("\nWaiting for response" + ("." * count))
        count = (count + 1) % 4
        time_count += 0.33
        time.sleep(0.33)


