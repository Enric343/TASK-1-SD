import time
import grpc
import redis
import chatServer_pb2, chatServer_pb2_grpc

from chat_menus import *
from chat_service import ChatService
from chat_service_servicer import ChatServiceServicer
from user_session import UserSession

def receive_requests(server, session:UserSession):
    # use the generated function `add_ChatServiceServicer_to_server`
    # to add the defined class to the server
    chatServer_pb2_grpc.add_ChatServiceServicer_to_server(ChatServiceServicer(ChatService(session)), server)

    # listen on port
    print(f'Starting server. Listening on port {session.origin_port}.')
    server.add_insecure_port(f'0.0.0.0:{session.origin_port}')
    server.start() # Inicia la espera de mensajes privados


def create_stub(target_socket):
     target_socket = target_socket.split(":")
     channel = grpc.insecure_channel(f'{target_socket[0]}:{target_socket[1]}')
     return chatServer_pb2_grpc.ChatServiceStub(channel)
     

def chat_private(session: UserSession, stub: chatServer_pb2_grpc.ChatServiceStub):
    refresh_chat_private(session.chat)
    try:
        while True:
            msg=input()
            message = chatServer_pb2.Message(text=msg)
            stub.SendMessage(message)
            session.chat.append(('me', msg))
            refresh_chat_private(session.chat)
            time.sleep(0.1)

    except KeyboardInterrupt:
        disconnected = chatServer_pb2.Message(text="*disconnected*")
        stub.SendMessage(disconnected)
        client_modal("Has cerrado el chat")

    except grpc._channel._InactiveRpcError:
        client_modal("El otro cliente ha cerrado el chat o se ha desconectado.")

    session.chatting_private = False
         

def open_chat_private(session: UserSession):
    try:
        found = False
        while not found:
            target = ask_who()

            # Si ha pulsado cancelar
            if target is None:
                 return None
            
            target_socket = session.redis.hget('users', target)
            if target_socket is None:
                client_modal("El usuario no existe")
            else:
                found = True

        stub = create_stub(target_socket.decode('utf-8'))

        socket = chatServer_pb2.Socket(ip=session.origin_ip, port=session.origin_port)
        stub.ConnectToUser(socket)

        session.chat = [] # Reinicia el chat
        session.chatting_private = True

        wait_private_response(session.chat)
        chat_private(session, stub)

    except redis.exceptions.ResponseError as e:
            client_modal("Algo ha salido mal :(")
            exit()


def response_chat_private(session: UserSession, target_socket: str):
    try:
        stub = create_stub(target_socket)

        socket = chatServer_pb2.Socket(ip=session.origin_ip, port=session.origin_port)
        stub.ConnectToUser(socket)

        session.chat = [] # Reinicia el chat
        session.chatting_private = True
        connected = chatServer_pb2.Message(text="*connected*")
        stub.SendMessage(connected)

        chat_private(session, stub)

    except redis.exceptions.ResponseError as e:
            client_modal("ERROR: La petición a caducado")       

          
         
