# main.py
# Windows için: Stockfish dizini = C:\Users\ahmet\Desktop\Projects\LLM_Chess\stockfish
# Gereksinimler: pygame, python-chess, stockfish (Python package)
import os
from chess_game import ChessGame


def main():
    # Update this path if your stockfish.exe is elsewhere
    stockfish_exe = r"C:\Users\ahmet\Desktop\Projects\LLM_Chess\stockfish.exe"
    pieces_folder = os.path.join(os.path.dirname(__file__), "pieces")
    game = ChessGame(stockfish_exe=stockfish_exe, pieces_folder=pieces_folder)
    game.run()


if __name__ == "__main__":
    main()
