import functools
import pickle
import threading

from pika import BlockingConnection, ConnectionParameters

from chat_menus import *
from user_session import UserSession


# Función principal para realizar cdescubrimiento de chats
def chat_discovery(session:UserSession):
    session.discovered_chats = []

    # Parámetros de connexión de este cliente
    myParams = session.get_connection()

    # Crea un canal nuevo en el que recibir los parámetros de connexión del resto
    new_connection = BlockingConnection(ConnectionParameters(host='localhost', heartbeat=600))
    new_channel = new_connection.channel()
    result = new_channel.queue_declare(queue='', exclusive=True) 
    queue_name = result.method.queue 
    new_channel.exchange_declare(exchange=myParams, exchange_type='fanout')
    new_channel.queue_bind(exchange=myParams, queue=queue_name)

    discovery_ack_callback_args = functools.partial(discovery_ack_callback, args=(session))
    new_channel.basic_consume(queue=queue_name, on_message_callback=discovery_ack_callback_args, auto_ack=True)

    # Activa el thread consumidor de mensajes
    thread = threading.Thread(target = lambda: new_channel.start_consuming())
    thread.start()
    # Envía la petició a todos los usuarios
    new_connection.add_callback_threadsafe(lambda: discovery_who(session))

    wait_discovey_response()

    new_connection.add_callback_threadsafe(lambda: new_channel.exchange_delete(exchange=myParams))
    new_connection.add_callback_threadsafe(lambda: new_channel.stop_consuming())

    return session.discovered_chats


# Función de callback que se ejecuta cuando otro usuario hace chat_discovery
def discovery_who_callback(ch, method, properties, body, args):
    session: UserSession = args
    requestParams = pickle.loads(body)

    # Si NO es él mismo quien ha hecho el discovery
    if requestParams != session.get_connection():
        responseParams = f'{session.username} ({session.get_connection()})'
        discovery_ack(session.connection.channel(), requestParams, responseParams)


# Función de callback que se ejecuta cuando un usuario ha hecho discovery y otro le responde
def discovery_ack_callback(ch, method, properties, body, args):
    session: UserSession = args
    session.discovered_chats.append(pickle.loads(body))
    


# Un usuario solicita a todos los demás sus parámetros de connexión
def discovery_who(session: UserSession):
    session.connection.channel().basic_publish(exchange='discovery',
                          routing_key='',
                          body=pickle.dumps(session.get_connection()))
    

# Un usuario envía sus parámetros de connexión al solicitante
def discovery_ack(channel, reqParams, resParams):
    channel.basic_publish(exchange=reqParams,
                          routing_key='',
                          body=pickle.dumps(resParams))



