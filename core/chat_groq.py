from .session_manager import SessionManager
from .rag_pipeline import RAGPipeline

class ChatWithGroq:
    def __init__(self, retriever, groq_api_key):
        self.session_manager = SessionManager()
        self.session_id = self.session_manager.new_session()
        self.rag = RAGPipeline(retriever, groq_api_key)

    def ask(self, question):
        # Retrieve history for this session
        history = self.session_manager.get_or_create(self.session_id)
        # Ask question
        response = self.rag.get_response(question, history)
        # Save to memory
        self.session_manager.append_user(self.session_id, question)
        self.session_manager.append_bot(self.session_id, response)
        return {"answer": response}

    def get_history(self):
        return self.session_manager.get_or_create(self.session_id)

    def reset(self):
        self.session_manager.reset(self.session_id)