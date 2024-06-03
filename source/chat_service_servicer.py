# import the original chat_service.py
from chat_service import ChatService

# import the generated classes
import chatServer_pb2
import chatServer_pb2_grpc


# create a class to define the server functions, derived from
# chatServer_pb2_grpc.ChatServiceServicer
class ChatServiceServicer(chatServer_pb2_grpc.ChatServiceServicer):

    def __init__(self, chat_service:ChatService) -> None:
        super().__init__()
        self.chat_service = chat_service

    def ConnectToUser(self, socket, context):
        self.chat_service.connect_to_user(socket.ip, socket.port)
        response = chatServer_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
        return response

    def SendMessage(self, msg, context):
        self.chat_service.send_message(msg.text)
        response = chatServer_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
        return response