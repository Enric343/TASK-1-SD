from typing import Dict, List, Tuple
from redis import Redis
from pika import BlockingConnection, ConnectionParameters
from group_chat_req import GroupChatReq


class UserSession:
    username: str = None
    origin_port: str = None
    origin_ip: str = None
    redis: Redis = None
    chat: List[str] = list()
    requests: List[str] = list()
    chatting_private: bool = False
    connection: BlockingConnection = None
    channel: BlockingConnection.channel = None
    groupal_chats: Dict[str, Tuple[str, List[GroupChatReq]]] = {}
    discovered_chats: List[str]
    

    def __init__(self, username, origin_ip, origin_port, redis):
        self.username = username
        self.origin_ip = origin_ip
        self.origin_port = origin_port
        self.redis = redis
        self.connection = BlockingConnection(ConnectionParameters(host='localhost', heartbeat=600))
        self.channel = self.connection.channel()

    def get_connection(self):
        return f'{self.origin_ip}:{self.origin_port}'
