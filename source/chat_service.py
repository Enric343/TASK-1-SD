from chat_private_utils import refresh_chat_group

from chat_menus import *
from user_session import UserSession

class ChatService:   

    def __init__(self, session:UserSession):
        self.session = session

    def connect_to_user(self, dest_ip, dest_port):
        self.session.requests.append(f'{dest_ip}:{dest_port}')
        return "Recieved"

    def send_message(self, msg):
        self.session.chat.append(('they', msg))
        if self.session.chatting_private is True:
            refresh_chat_private(self.session.chat)
        return "Recieved"
    





