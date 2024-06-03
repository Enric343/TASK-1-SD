from concurrent import futures
import time
import functools
import socket
import threading
import grpc, redis
import pika
from pika import BlockingConnection, ConnectionParameters
from chat_discovery_utils import chat_discovery, discovery_who, discovery_who_callback

# import the generated classes
from chat_group_utils import create_chat_group, open_chat_group, join_chat_group
from chat_private_utils import open_chat_private, receive_requests, response_chat_private

from chat_menus import *
from insult_channel_utils import insult_callback, insult_me, insult_someone
from user_session import UserSession


def sign_in(r:redis.Redis):
    try:
        user = login()
        if user is None:
            return None
        user_socket = r.hget('users', user)
        if user_socket is None:
            ip = str(socket.gethostbyname(socket.gethostname()))
            port = ask_port()
            if port is None:
                return None
            r.hset('users', user, f"{ip}:{port}")
            client_modal("Te has registrado correctamente")
        else:
            user_socket = user_socket.decode('utf-8').split(":")
            ip, port = user_socket[0], user_socket[1]

        return UserSession(user, ip, port, r)

    except redis.exceptions.ResponseError as e1:
            client_modal("Algo ha salido mal :(")
            exit()

# Establecer conexión con Redis
r = redis.Redis(host='localhost', port=7043)
session = sign_in(r)
if session is None:
    exit()

# Creates server to receive requests of private chatting
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
receive_requests(server, session)

# Se linkea con el exchange discovery
discovery_connection = BlockingConnection(ConnectionParameters(host='localhost', heartbeat=600))
discovery_channel = discovery_connection.channel()
result = discovery_channel.queue_declare(queue='', exclusive=True) 
queue_name = result.method.queue 
discovery_channel.queue_bind(exchange='discovery', queue=queue_name) # Vincula la cola al exchange de chat discovery
discover_callback_with_args = functools.partial(discovery_who_callback, args=(session))
discovery_channel.basic_consume(queue=queue_name, on_message_callback=discover_callback_with_args, auto_ack=True)

# Activa el thread consumidor de mensajes discovery
thread = threading.Thread(target=lambda: discovery_channel.start_consuming())
thread.start() 

opt1 = 1

# MENÚ PRINCIPAL
while opt1 is not None:
    opt1 = main_menu()

    # CHAT PRIVADO
    if opt1 == '1':
        opt2 = chat_private_menu()
        if opt2 == '1':
            open_chat_private(session)
        elif opt2 == '2':
            if len(session.requests) > 0:
                target = show_chat_requests(session.requests) 
                if target is not None:
                    response_chat_private(session, target)
            else:
                client_modal("No tienes ninguna petición de chat ;(")

    # CHAT GRUPAL
    elif opt1 == '2':
        opt2 = 0
        while opt2 is not None:
            opt2 = chat_group_menu()
            if opt2 == '1':
                if len(session.groupal_chats) > 0:
                    open_chat_group(session)
                else:
                    client_modal("No estás dentro de ningún grupo!")
            elif opt2 == '2':
                join_chat_group(session)
            elif opt2 == '3':
                create_chat_group(session)

    # DESCUBRIR CHATS
    elif opt1 == '3':
        chats = chat_discovery(session)
        if len(chats) != 0:
            show_discovered_chats(chats)
        else:
            client_modal("No hay nadie conectado :(")
            
    # INSULT CHANNEL
    elif opt1 == '4':
        opt2 = 0
        while opt2 is not None:
            opt2 = insult_channel_menu()
            if opt2 == '1':
                insult = write_an_insult()
                if insult is not None:
                    insult_someone(session, insult)
            elif opt2 == '2':
                insult_me(session)

client_modal("Has cerrado sessión correctamente, hasta otra!")

try:
    discovery_channel.stop_consuming()
except Exception as e:
    print('Esto va de puta madre.')

os.system('clear')
