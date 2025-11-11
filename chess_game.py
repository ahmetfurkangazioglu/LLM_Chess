import os
import sys
import random
import time
import pygame
import chess
from stockfish import Stockfish
from chat_manager import ChatManager
from move_manager import MoveManager


class ChessGame:
    

    def __init__(self, stockfish_exe, pieces_folder,
                 square_size=80, board_margin=20, stockfish_skill=10,
                 ai_min_think=2.0, ai_max_think=5.0, fps=60):
        self.STOCKFISH_EXE = stockfish_exe
        self.PIECES_FOLDER = pieces_folder
        self.SQUARE_SIZE = square_size
        self.BOARD_MARGIN = board_margin
        self.BOARD_PIXEL = square_size * 8
        self.CHAT_WIDTH = 300
        self.WINDOW_WIDTH = self.BOARD_PIXEL + board_margin * 2 + self.CHAT_WIDTH
        self.WINDOW_HEIGHT = self.BOARD_PIXEL + board_margin * 2 + 60
        self.FPS = fps
        self.AI_MIN_THINK = ai_min_think
        self.AI_MAX_THINK = ai_max_think
        self.STOCKFISH_SKILL = stockfish_skill

        # Init pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("LLM satranç")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        # Load images
        self.images = {}
        self._load_piece_images()

        # Chess board and engine
        self.board = chess.Board()
        self.stockfish = Stockfish(path=self.STOCKFISH_EXE)
        self.stockfish.update_engine_parameters({"Skill Level": self.STOCKFISH_SKILL})

        # State
        self.selected_square = None
        self.legal_destinations = []
        self.ai_thinking = False
        self.ai_think_end_time = 0.0
        self.game_over = False
        self.info_message = "Sen (Beyaz) oynuyor."
        
        # Chat
        self.chat_manager = ChatManager()
        self.chat_input = ""
        self.chat_scroll = 0
        
        # Move tracking
        self.move_manager = MoveManager()

    def _load_piece_images(self):
        mapping = {
            'P': 'pawn_white.png','R': 'rook_white.png','N': 'knight_white.png','B': 'bishop_white.png','Q': 'queen_white.png','K': 'king_white.png',
            'p': 'pawn_black.png','r': 'rook_black.png','n': 'knight_black.png','b': 'bishop_black.png','q': 'queen_black.png','k': 'king_black.png',
        }
        for sym, fname in mapping.items():
            path = os.path.join(self.PIECES_FOLDER, fname)
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (self.SQUARE_SIZE, self.SQUARE_SIZE))
            self.images[sym] = img

    # Coordinate helpers
    def sq_to_xy(self, square):
        rank = 7 - chess.square_rank(square)
        file = chess.square_file(square)
        x = self.BOARD_MARGIN + file * self.SQUARE_SIZE
        y = self.BOARD_MARGIN + rank * self.SQUARE_SIZE
        return x, y

    def xy_to_sq(self, x, y):
        rx = x - self.BOARD_MARGIN
        ry = y - self.BOARD_MARGIN
        if rx < 0 or ry < 0 or rx >= self.BOARD_PIXEL or ry >= self.BOARD_PIXEL:
            return None
        file = int(rx // self.SQUARE_SIZE)
        rank = 7 - int(ry // self.SQUARE_SIZE)
        return chess.square(file, rank)

    def draw_board(self):
        colors = [(240, 217, 181), (181, 136, 99)]
        for rank in range(8):
            for file in range(8):
                square = chess.square(file, 7 - rank)
                rect = pygame.Rect(self.BOARD_MARGIN + file * self.SQUARE_SIZE,
                                   self.BOARD_MARGIN + rank * self.SQUARE_SIZE,
                                   self.SQUARE_SIZE, self.SQUARE_SIZE)
                color = colors[(file + rank) % 2]
                pygame.draw.rect(self.screen, color, rect)

        if self.selected_square is not None:
            sx, sy = self.sq_to_xy(self.selected_square)
            sel_rect = pygame.Rect(sx, sy, self.SQUARE_SIZE, self.SQUARE_SIZE)
            pygame.draw.rect(self.screen, (255, 255, 0, 50), sel_rect, 4)

        for dest in self.legal_destinations:
            dx, dy = self.sq_to_xy(dest)
            highlight = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
            highlight.fill((50, 205, 50, 120))
            self.screen.blit(highlight, (dx, dy))

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece is not None:
                sym = piece.symbol()
                img = self.images.get(sym)
                if img:
                    x, y = self.sq_to_xy(square)
                    self.screen.blit(img, (x, y))

        info_surf = self.font.render(self.info_message, True, (10, 10, 10))
        self.screen.blit(info_surf, (self.BOARD_MARGIN, self.BOARD_MARGIN + self.BOARD_PIXEL + 10))
        
        # Chat alanını çiz
        self.draw_chat()

    def start_ai_thinking(self):
        self.ai_thinking = True
        think = random.uniform(self.AI_MIN_THINK, self.AI_MAX_THINK)
        self.ai_think_end_time = time.time() + think
        self.info_message = f"Rakip düşünüyor ({think:.1f}s)"

    def ai_make_move(self):
        self.stockfish.set_fen_position(self.board.fen())
        best = self.stockfish.get_best_move()
        move = chess.Move.from_uci(best)
        
        # SAN'ı hamleden önce al
        move_san = self.board.san(move)
        
        self.board.push(move)
        
        # Hamleyi kaydet
        self.move_manager.add_move(
            player="black",
            move_uci=best,
            move_san=move_san,
            fen=self.board.fen()
        )
        
        self.info_message = f"Rakip oynadı: {best}"
        self.ai_thinking = False

        if self.board.is_game_over():
            self.game_over = True
            self.info_message = f"Oyun bitti: {self.board.result()}"

    def draw_chat(self):
        """Chat alanını sağ tarafta çizer."""
        chat_x = self.BOARD_PIXEL + self.BOARD_MARGIN * 2
        chat_y = self.BOARD_MARGIN
        chat_h = self.BOARD_PIXEL + 40
        
        # Chat arka plan
        chat_bg = pygame.Rect(chat_x, chat_y, self.CHAT_WIDTH, chat_h)
        pygame.draw.rect(self.screen, (240, 240, 240), chat_bg)
        pygame.draw.rect(self.screen, (100, 100, 100), chat_bg, 2)
        
        # Başlık
        title = self.font.render("Chat", True, (0, 0, 0))
        self.screen.blit(title, (chat_x + 10, chat_y + 5))
        
        # Mesaj alanı
        msg_area = pygame.Rect(chat_x + 5, chat_y + 35, self.CHAT_WIDTH - 10, chat_h - 90)
        pygame.draw.rect(self.screen, (255, 255, 255), msg_area)
        pygame.draw.rect(self.screen, (150, 150, 150), msg_area, 1)
        
        # Mesajları göster
        messages = self.chat_manager.get_all_messages()
        y_offset = msg_area.y + 5
        small_font = pygame.font.SysFont(None, 18)
        
        for msg in messages[-15:]:  # Son 15 mesaj
            sender_label = "Sen: " if msg["sender"] == "player" else "AI: "
            text_color = (0, 100, 0) if msg["sender"] == "player" else (0, 0, 150)
            msg_surf = small_font.render(sender_label + msg["message"][:35], True, text_color)
            if y_offset + 20 < msg_area.bottom:
                self.screen.blit(msg_surf, (msg_area.x + 5, y_offset))
                y_offset += 20
        
        # Input alanı
        input_area = pygame.Rect(chat_x + 5, chat_y + chat_h - 50, self.CHAT_WIDTH - 10, 30)
        pygame.draw.rect(self.screen, (255, 255, 255), input_area)
        pygame.draw.rect(self.screen, (100, 100, 100), input_area, 2)
        
        # Input text
        input_surf = small_font.render(self.chat_input, True, (0, 0, 0))
        self.screen.blit(input_surf, (input_area.x + 5, input_area.y + 8))
        
        # Send butonu
        send_btn = pygame.Rect(chat_x + 5, chat_y + chat_h - 15, 60, 20)
        pygame.draw.rect(self.screen, (100, 200, 100), send_btn)
        pygame.draw.rect(self.screen, (50, 150, 50), send_btn, 2)
        send_text = small_font.render("Gönder", True, (0, 0, 0))
        self.screen.blit(send_text, (send_btn.x + 8, send_btn.y + 3))
        
        self.send_button_rect = send_btn
        self.chat_input_rect = input_area
    
    def handle_chat_click(self, mx, my):
        """Chat input'a tıklanma kontrolü."""
        if hasattr(self, 'chat_input_rect') and self.chat_input_rect.collidepoint(mx, my):
            return True
        if hasattr(self, 'send_button_rect') and self.send_button_rect.collidepoint(mx, my):
            if self.chat_input.strip():
                self.chat_manager.add_message("player", self.chat_input)
                # Şimdilik AI otomatik cevap vermiyor, sadece kaydediyor
                self.chat_input = ""
            return True
        return False

    def handle_mouse(self, mx, my):
        # Önce chat alanına tıklama kontrolü
        if self.handle_chat_click(mx, my):
            return
        
        sq = self.xy_to_sq(mx, my)
        if sq is None:
            return
        piece = self.board.piece_at(sq)
        
        if self.selected_square is not None and sq in self.legal_destinations:
            mv = chess.Move(self.selected_square, sq)
            if self.board.piece_at(self.selected_square).piece_type == chess.PAWN and (chess.square_rank(sq) in [0,7]):
                mv = chess.Move(self.selected_square, sq, promotion=chess.QUEEN)
            
            # SAN'ı hamleden önce al (board.san() hamlede sonra kullanılamaz)
            move_san = self.board.san(mv)
            move_uci = mv.uci()
            
            self.board.push(mv)
            
            # Hamleyi kaydet
            self.move_manager.add_move(
                player="white",
                move_uci=move_uci,
                move_san=move_san,
                fen=self.board.fen()
            )
            
            self.selected_square = None
            self.legal_destinations = []
            if self.board.is_game_over():
                self.game_over = True
                self.info_message = f"Oyun bitti: {self.board.result()}"
            else:
                self.start_ai_thinking()
        else:
            if piece is not None and piece.color == chess.WHITE:
                self.selected_square = sq
                self.legal_destinations = [mv.to_square for mv in self.board.legal_moves if mv.from_square == sq]
                self.info_message = f"Seçili: {chess.square_name(sq)}" if self.legal_destinations else "Seçili taş."
            else:
                self.selected_square = None
                self.legal_destinations = []

    def run(self):
        running = True
        while running:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    if not self.handle_chat_click(mx, my) and not self.ai_thinking and not self.game_over:
                        self.handle_mouse(mx, my)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Enter tuşu - mesaj gönder
                        if self.chat_input.strip():
                            self.chat_manager.add_message("player", self.chat_input)
                            self.chat_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        # Backspace - son karakteri sil
                        self.chat_input = self.chat_input[:-1]
                    else:
                        # Normal karakter girişi
                        if len(self.chat_input) < 50:
                            self.chat_input += event.unicode

            if self.ai_thinking and time.time() >= self.ai_think_end_time and not self.game_over:
                self.ai_make_move()

            self.screen.fill((200, 200, 200))
            self.draw_board()

            if self.game_over:
                over_surf = self.font.render("Oyun bitti! Sonuç: " + self.board.result(), True, (200, 20, 20))
                self.screen.blit(over_surf, (self.BOARD_MARGIN, self.BOARD_MARGIN + self.BOARD_PIXEL + 30))

            pygame.display.flip()

        # Oyun kapanırken chat ve hamle dosyalarını sil
        self.chat_manager.delete_history_file()
        self.move_manager.delete_history_file()
        pygame.quit()
