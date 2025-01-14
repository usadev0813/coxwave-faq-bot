class ConversationMemory:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "history"):
            self.history = []

    def add_message(self, user_message: str, ai_message: str):
        """대화 메시지를 추가"""
        self.history.append({"user": user_message, "ai": ai_message})

    def get_history(self):
        """현재 히스토리를 반환"""
        return self.history

    def clear_history(self):
        """히스토리를 초기화"""
        self.history = []
