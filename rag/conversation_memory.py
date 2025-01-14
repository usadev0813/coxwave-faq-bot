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
        """
        대화 메시지를 추가하는 메서드.

        - 입력된 사용자 메시지(`user_message`)와 AI 응답 메시지(`ai_message`)를 저장합니다.
        - 최대 3건까지만 저장되며, 이를 초과할 경우 가장 오래된 메시지가 삭제됩니다.
        """
        if len(self.history) >= 3:
            self.history.pop(0)
        self.history.append({"user": user_message, "ai": ai_message})

    def get_history(self):
        """현재 히스토리를 반환"""
        return self.history

    def clear_history(self):
        """히스토리를 초기화"""
        self.history = []
