import functools
import pickle
import threading
import time
from pika import BasicProperties, DeliveryMode, BlockingConnection, ConnectionParameters

from chat_menus import * 
from user_session import UserSession  

def insult_me(session: UserSession):
    show_chat_header('(insult channel)', 'SUICIDAL')

    insult_channel = session.connection.channel()
    insult_channel.queue_declare(queue='insults', durable=True)
    insult_channel.basic_qos(prefetch_count=1)
    insult_callback_with_args = functools.partial(insult_callback, args=session)
    insult_channel.basic_consume(queue='insults', on_message_callback=insult_callback_with_args, auto_ack=True)
    insult_thread = threading.Thread(target=lambda: insult_channel.start_consuming())

    insult_thread.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        session.connection.add_callback_threadsafe(lambda: insult_channel.stop_consuming())
        client_modal("Has salido del insult channel... cobarde.")

# Función de callback para cuando un cliente recibe un insulto
def insult_callback(ch, method, properties, body, args):
    session: UserSession = args
    print(colored(f' --> {pickle.loads(body)}', 'red'))

def insult_someone(session: UserSession, insult: str):
    insult_channel = session.connection.channel()
    insult_channel.queue_declare(queue='insults', durable=True)
    insult_channel.basic_publish(
        exchange='',
        routing_key='insults',
        body=pickle.dumps(insult),
        properties=BasicProperties(
            delivery_mode=DeliveryMode.Persistent 
        ))
    insult_channel.close()
