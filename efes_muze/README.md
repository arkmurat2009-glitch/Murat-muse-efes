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
python3 muze.py kitap-ekle 9780306406157 "Efes Rehberi" 150 --yazar "A. Yazar" --stok 20
python3 muze.py kitap-sat 9780306406157 2
python3 muze.py kitap-stok 9780306406157 10
python3 muze.py kitap-listele --ara Efes
```
Kitap modülü: ISBN-13 doğrulanır, stok eksiye düşürülmez, satışlar günlük raporda görünür.
Mevzuat notu (kontrol tarihi 2026-10-28, kaynaklar web aramasıyla; resmî metinle teyit edilmeli):
- Yayın satış gelirleri 2252 sayılı Kültür Bakanlığı Döner Sermaye Kanunu ve Kültür ve Turizm Bakanlığı Döner Sermaye Yönetmeliği kapsamındadır (yönetmeliğin güncel metni doğrulanamadı); program yalnızca kayıt tutar, tahsilat/tahakkuk ve fiyat tarifesi Döner Sermaye usullerine göre yürütülmelidir.
- Basılı kitap teslimi KDV'den istisnadır (3065 s. K. md. 13/n, 7166 s. K.; 2026 geçerliliği doğrulanamadı). E-kitap ve poşetli yayınlar kapsam dışıdır.
- Müze kendi kitabını bastırıyorsa 6279 sayılı Kanun'a göre yasal depo (Millî Kütüphane vb.) yükümlülüğü doğabilir.

Bilet türleri: yetiskin (200 TL), ogrenci (50 TL), cocuk, muze_kart (ücretsiz).

## Masaüstü saati

`python3 saat.py` — dijital saat (SS:DD), Efes hava durumu (Open-Meteo, 15 dk'da bir yenilenir) ve aylık takvim.
Gerekli: `python3-tk` (Linux). Kapatmak için Esc.
