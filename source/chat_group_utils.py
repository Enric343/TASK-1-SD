import pickle
import threading
import time

from chat_menus import *
from group_chat_req import GroupChatReq
from user_session import UserSession

def chat_exists(group_name: str, session: UserSession):
    if session.redis.hget('groups', group_name) is None:
        return False
    return True
    

def link_to_chat(group_name: str, session: UserSession):
    result = session.channel.queue_declare(queue='', exclusive=True) 
    queue_name = result.method.queue # Crea una nueva cola
    session.groupal_chats[group_name] = (queue_name, []) # Introduce el nuevo grupo en el diccionario de chats
    session.channel.queue_bind(exchange=group_name, queue=queue_name) # Vincula la cola a dicho grupo


def create_chat_group(session: UserSession):
    group_name = client_input('CHAT GROUP', 'Introduce el nombre del grupo que quieres crear:')

    if group_name is None:
        return

    if chat_exists(group_name, session):
        client_modal(f"ERROR: El grupo \'{group_name}\' ya existe.")
        return

    session.channel.exchange_declare(exchange=group_name, exchange_type='fanout') # Declara el grupo en rabbit
    session.redis.hset('groups', group_name, group_name) # Guarda el grupo en redis
    link_to_chat(group_name, session)
    client_modal(f"Has creado con exito el grupo \'{group_name}\'.")
    chat_group(session, group_name)


def open_chat_group(session: UserSession):
    group_name = show_chat_groups(session.groupal_chats)

    if group_name is None:
        return

    if not chat_exists(group_name, session):
        session.groupal_chats.pop(group_name)
        client_modal(f"ERROR: El grupo \'{group_name}\' ya NO existe.")
        return

    chat_group(session, group_name)


def join_chat_group(session: UserSession):
    group_name = client_input('CHAT GROUP', 'Introduce el nombre del grupo en el que quieres entrar:')

    if group_name is None:
        return

    if not chat_exists(group_name, session):
        client_modal(f"ERROR: El grupo \'{group_name}\' NO existe.")
        return

    link_to_chat(group_name, session)
    chat_group(session, group_name)


def fetch_messages(session:UserSession, group_name):

    # Define la función de callback
    def callback(ch, method, properties, body):
        group_req:GroupChatReq = pickle.loads(body)
        session.groupal_chats[group_name][1].append(GroupChatReq(group_req.username, group_req.message))
        refresh_chat_group(session, group_name)

    # Configura el consumidor para leer mensajes de la cola vinculada
    queue_name = session.groupal_chats[group_name][0]
    session.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    # Activa el thread consumidor de mensajes
    thread = threading.Thread(target=lambda: session.channel.start_consuming())
    thread.start() 


def send_message(channel, groupName, chatReq):
    # Realiza una operación con el canal
    channel.basic_publish(exchange=groupName,
                          routing_key='',
                          body=pickle.dumps(chatReq))


def chat_group(session: UserSession, groupName):
    refresh_chat_group(session, groupName)
    fetch_messages(session, groupName)

    try:
        while True:
            msg=input()
            chatReq = GroupChatReq(session.username, msg)
            session.connection.add_callback_threadsafe(lambda: send_message(session.connection.channel(), groupName, chatReq))
            refresh_chat_group(session, groupName)
            time.sleep(0.1)

    except KeyboardInterrupt:
        client_modal(f"Has cerrado el chat grupal \'{groupName}\'")
        session.connection.add_callback_threadsafe(lambda: session.channel.stop_consuming())

