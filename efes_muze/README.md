# Efes Müzesi Yönetim Programı

Bağımlılıksız (yalnızca Python 3 standart kütüphanesi) komut satırı programı. Veriler `efes_muze.db` (SQLite) dosyasında tutulur.

```
python3 muze.py eser-ekle EF-001 "Artemis Heykeli" --donem "Roma" --malzeme "Mermer"
python3 muze.py sergi-ekle "Artemis Salonu" --salon A1
python3 muze.py yerlestir EF-001 "Artemis Salonu"
python3 muze.py eser-durum EF-001 restorasyonda
python3 muze.py eser-listele --ara Roma
python3 muze.py bilet yetiskin 2
python3 muze.py rapor
```
Bilet türleri: yetiskin (200 TL), ogrenci (50 TL), cocuk, muze_kart (ücretsiz).
