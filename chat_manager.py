import json
import os
from datetime import datetime


class ChatManager:
  
    def __init__(self, chat_file="chat_history.json"):
        self.chat_file = chat_file
        self.messages = []

        if os.path.exists(self.chat_file):
            os.remove(self.chat_file)
    

    
    def _save_history(self):
        with open(self.chat_file, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)
    
    def add_message(self, sender, message):
        msg = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sender": sender,
            "message": message
        }
        self.messages.append(msg)
        self._save_history()
    
    def get_all_messages(self):
        return self.messages
    
    def get_recent_messages(self, count=10):
        return self.messages[-count:] if len(self.messages) > count else self.messages
    
    def get_formatted_history(self):
        lines = []
        for msg in self.messages:
            sender_label = "Sen" if msg["sender"] == "player" else "AI"
            lines.append(f"[{msg['timestamp']}] {sender_label}: {msg['message']}")
        return "\n".join(lines)
    
    def clear_history(self):
        self.messages = []
        self._save_history()
    
    def delete_history_file(self):
        
        if os.path.exists(self.chat_file):
            os.remove(self.chat_file)
