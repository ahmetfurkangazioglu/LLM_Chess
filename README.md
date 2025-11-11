# LLM Chess

Satranç oyunu - Pygame ile yapılmış, Stockfish AI ve LLM (TinyLlama) ile sohbet özellikli.

## Özellikler

- 🎮 Pygame ile grafik arayüz
- ♟️ Stockfish motoru ile AI rakip
- 💬 TinyLlama LLM ile sohbet
- 📝 Hamle ve sohbet geçmişi kaydı
- 🎨 Modern ve temiz tasarım

## Gereksinimler

```bash
pip install pygame python-chess stockfish transformers torch accelerate
```

## Kurulum

1. Repository'yi klonlayın:
```bash
git clone git@github.com:ahmetfurkangazioglu/LLM_Chess.git
cd LLM_Chess
```

2. Stockfish motorunu indirin ve `stockfish.exe` dosyasını proje klasörüne koyun:
   - [Stockfish İndir](https://stockfishchess.org/download/)

3. Pieces klasöründe taş görsellerini bulundurun (pawn_white.png, rook_black.png vb.)

4. Oyunu başlatın:
```bash
python main.py
```

## LLM Test

Jupyter Notebook ile TinyLlama modelini test etmek için:

```bash
jupyter notebook llm_test.ipynb
```

## Proje Yapısı

```
LLM_Chess/
├── main.py              # Ana çalıştırılabilir dosya
├── chess_game.py        # Oyun sınıfı
├── chat_manager.py      # Sohbet yönetimi
├── move_manager.py      # Hamle kayıt yönetimi
├── llm_test.ipynb       # LLM test notebook'u
├── pieces/              # Taş görselleri
└── stockfish.exe        # Stockfish motoru
```

## Kullanım

- Sol tıklama ile taş seçin ve hamle yapın
- Chat alanına yazı yazıp Enter ile mesaj gönderin
- AI otomatik hamle yapar ve ilerleyen versiyonlarda sohbet edecek

## Lisans

MIT License
