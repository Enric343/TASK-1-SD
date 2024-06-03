
class GroupChatReq:
    username: str = None
    message: str = None

    def __init__(self, username, message):
        self.username = username
        self.message = message

