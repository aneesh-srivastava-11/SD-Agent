class ConversationManager:
    def __init__(self):
        self.history = []
        self.is_active = False

    def start(self):
        self.is_active = True
        self.history = []

    def stop(self):
        self.is_active = False

    def add_turn(self, user_text, assistant_text):
        self.history.append({"user": user_text, "assistant": assistant_text})
        # Keep history manageable
        if len(self.history) > 10:
            self.history.pop(0)

    def get_history(self):
        return self.history
