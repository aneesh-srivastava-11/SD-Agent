import json
import os
from shadowdragon.config import MEMORY_FILE

class MemoryStore:
    def __init__(self):
        self.memory_path = MEMORY_FILE
        self.data = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_memory(self, key, value):
        self.data[key] = value
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        temp_path = self.memory_path + ".tmp"
        try:
            with open(temp_path, 'w') as f:
                json.dump(self.data, f, indent=4)
            os.replace(temp_path, self.memory_path)
        except Exception as e:
            print(f"Error saving memory atomically: {e}")
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

    def get_memory(self, key=None):
        if key:
            return self.data.get(key, "I don't remember that.")
        return self.data

    def get_all_context(self):
        if not self.data:
            return ""
        context = "Information I remember about the user:\n"
        for k, v in self.data.items():
            context += f"- {k}: {v}\n"
        return context
