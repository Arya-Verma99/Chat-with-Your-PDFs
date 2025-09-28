import os
import json
from datetime import datetime

class ChatHistoryManager:
    def __init__(self, save_dir="chat_history"):
        self.history = []
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def add(self, question, answer):
        self.history.append({
            "user": question,
            "bot": answer
        })

    def load(self, session_name):
        path = os.path.join(self.save_dir, f"{session_name}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                self.history = json.load(f)
        else:
            self.history = []
        return self.history

    def save(self, name: str = None):
        if not self.history:
            return None
        if not name:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"session_{ts}.json"
        path = os.path.join(self.save_dir, name)
        with open(path, "w") as f:
            json.dump(self.history, f, indent=2)
        return path