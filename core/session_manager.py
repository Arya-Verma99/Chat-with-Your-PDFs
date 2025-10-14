import uuid

class SessionManager:
    def __init__(self):
        self.chat_sessions = {}

    def new_session(self):
        session_id = str(uuid.uuid4())
        self.chat_sessions[session_id] = []
        return session_id

    def get_or_create(self, session_id):
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = []
        return self.chat_sessions[session_id]

    def append_user(self, session_id, user_input):
        self.chat_sessions[session_id].append({"role": "human", "content": user_input})

    def append_bot(self, session_id, bot_response):
        self.chat_sessions[session_id].append({"role": "ai", "content": bot_response})

    def reset(self, session_id):
        self.chat_sessions[session_id] = []