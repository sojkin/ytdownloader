# YT Downloader

## Opis projektu
YT Downloader to narzędzie do pobierania filmów z YouTube.

## Instalacja

### Wymagania
- Python 3.7+
- pip
- git

### Krok po kroku
1. Sklonuj repozytorium
```bash
git clone https://github.com/sojkin/ytdownloader.git
cd ytdownloader
```

2. Utwórz środowisko wirtualne
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Zainstaluj zależności
```bash
pip install -r requirements.txt
```

## Uruchomienie

### Tryb konsolowy
```bash
python src/main.py
```

### Tryb graficzny
```bash
python src/gui.py
```

## Funkcje
- Pobieranie filmów z YouTube
- Wybór jakości wideo
- Zapis w wybranej lokalizacji

## Rozwiązywanie problemów
- Upewnij się, że masz najnowszą wersję
- Sprawdź połączenie internetowe
- Zaktualizuj zależności: `pip install -r requirements.txt`

## Licencja
MIT License