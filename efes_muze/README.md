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
python3 muze.py eser-gecmis EF-001
```
Bilet türleri: yetiskin (200 TL), ogrenci (50 TL), cocuk, muze_kart (ücretsiz).

## Durum geçişleri ve denetim izi

İzinli geçişler: `depoda` -> sergide/restorasyonda/odunc; `sergide` -> başka sergi/depoda/restorasyonda/odunc;
`restorasyonda` ve `odunc` -> yalnızca `depoda` (iade). `sergide` durumuna yalnızca `yerlestir` ile (sergi belirterek)
geçilir; `odunc` veya `restorasyonda` eser sergiye yerleştirilemez.
Her geçiş `hareketler` tablosuna (tarih, eski/yeni durum ve sergi, kullanıcı, açıklama) aynı işlemde yazılır; tablo
ekleme-yalnızdır (UPDATE/DELETE tetikleyiciyle engelli). `eser-durum` ve `yerlestir` için `--kullanici` ve `--aciklama`
verilebilir; kullanıcı verilmezse `EFES_KULLANICI` ortam değişkeni, o da yoksa işletim sistemi kullanıcısı kullanılır.
Not (KVKK 6698): `kullanici` personel kimliğidir; saklama süresi/erişim kurum politikasına göre belirlenmelidir.

DB doğrulaması: mevcut tabloya CHECK eklenemediğinden `eklentiler/dogrulama.py` tetikleyicilerle geçersiz durum,
sergisiz `sergide`, geçersiz bilet türü/adet/tutar yazımlarını reddeder (mevcut veriye dokunmaz, eski DB'ler açılışta
otomatik yükseltilir). Yeni özellikler `eklentiler/` altında modül olarak eklenir (`sema`, `komutlar` kancaları).

Veritabanı yolu `EFES_MUZE_DB` ortam değişkeniyle değiştirilebilir (varsayılan: `efes_muze.db`).
Test: `python3 -m unittest test_gecis -v`

## Masaüstü saati

`python3 saat.py` — dijital saat (SS:DD), Efes hava durumu (Open-Meteo, 15 dk'da bir yenilenir) ve aylık takvim.
Gerekli: `python3-tk` (Linux). Kapatmak için Esc.
