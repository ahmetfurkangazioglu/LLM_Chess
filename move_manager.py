import json
import os
from datetime import datetime


class MoveManager:
    
    def __init__(self, move_file="move_history.json"):
        self.move_file = move_file
        self.moves = []
        self.move_counter = 0

        if os.path.exists(self.move_file):
            os.remove(self.move_file)
    
    def _save_history(self):
        with open(self.move_file, 'w', encoding='utf-8') as f:
            json.dump(self.moves, f, ensure_ascii=False, indent=2)
    
    def add_move(self, player, move_uci, move_san, fen):
        self.move_counter += 1
        move_data = {
            "move_number": self.move_counter,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "player": player,
            "move": move_uci,
            "san": move_san,
            "fen": fen
        }
        self.moves.append(move_data)
        self._save_history()
    
    def get_all_moves(self):
        return self.moves
    
    def get_recent_moves(self, count=5):
        return self.moves[-count:] if len(self.moves) > count else self.moves
    
    def get_move_history_text(self):
        lines = []
        for i in range(0, len(self.moves), 2):
            move_num = (i // 2) + 1
            white_move = self.moves[i]
            black_move = self.moves[i + 1] if i + 1 < len(self.moves) else None
            
            line = f"{move_num}. {white_move['san']}"
            if black_move:
                line += f" {black_move['san']}"
            lines.append(line)
        return " ".join(lines)
    
    def get_pgn_format(self):
        moves_text = []
        for i in range(0, len(self.moves), 2):
            move_num = (i // 2) + 1
            white_move = self.moves[i]
            black_move = self.moves[i + 1] if i + 1 < len(self.moves) else None
            
            move_str = f"{move_num}. {white_move['san']}"
            if black_move:
                move_str += f" {black_move['san']}"
            moves_text.append(move_str)
        return " ".join(moves_text)
    
    def delete_history_file(self):
        if os.path.exists(self.move_file):
            os.remove(self.move_file)
