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

## Durum geçişleri ve denetim izi

İzinli geçişler: `depoda` -> sergide/restorasyonda/odunc; `sergide` -> başka sergi/depoda/restorasyonda/odunc;
`restorasyonda` ve `odunc` -> yalnızca `depoda` (iade). `sergide` durumuna yalnızca `yerlestir` ile (sergi belirterek)
geçilir; `odunc` veya `restorasyonda` eser sergiye yerleştirilemez.
Her geçiş `hareketler` tablosuna (tarih, eski/yeni durum ve sergi, kullanıcı, açıklama) aynı işlemde yazılır; tablo
ekleme-yalnızdır (UPDATE/DELETE tetikleyiciyle engelli). `eser-durum` ve `yerlestir` için `--kullanici` ve `--aciklama`
verilebilir; kullanıcı verilmezse `EFES_KULLANICI` ortam değişkeni, o da yoksa işletim sistemi kullanıcısı kullanılır.
Sınır: ekleme-yalnız koruma tetikleyiciyle sağlanır, DB dosyasına doğrudan erişimi (dosya silme/yeniden yazma) engellemez; dosya izinleri ve yedekleme ayrıca yönetilmelidir.
Geçersiz (eski sürümden kalma) bir durumdaki eser yalnızca `eser-durum NO depoda` ile kurtarılır. Eşzamanlı değişiklikte komut hata verir, tekrar denenir.
Not (KVKK 6698): `kullanici` personel kimliğidir; saklama süresi/erişim kurum politikasına göre belirlenmelidir.

DB doğrulaması: mevcut tabloya CHECK eklenemediğinden `eklentiler/dogrulama.py` tetikleyicilerle geçersiz durum,
sergisiz `sergide`, geçersiz bilet türü/adet/tutar yazımlarını reddeder (mevcut veriye dokunmaz, eski DB'ler açılışta
otomatik yükseltilir). Yeni özellikler `eklentiler/` altında modül olarak eklenir (`sema`, `komutlar` kancaları).

Veritabanı yolu `EFES_MUZE_DB` ortam değişkeniyle değiştirilebilir (varsayılan: `efes_muze.db`).
Test: `python3 -m unittest test_gecis -v`

## Restorasyon ve ödünç takibi

```
python3 muze.py restorasyon-baslat EF-001 --atolye "İzmir Bölge Lab." --sorumlu "A. Yılmaz" --bitis 2026-12-31
python3 muze.py restorasyon-bitir EF-001 --not "temizlik tamamlandı"
python3 muze.py odunc-ver EF-001 "Ankara Müzesi" --donus 2027-03-01 --sigorta 50000 --izin-no "2026/15"
python3 muze.py odunc-ver EF-002 "Louvre" --donus 2027-06-01 --sigorta 900000 --izin-no "K-123" --yurt-disi --ulke-sayisi 1
python3 muze.py odunc-iade EF-001 --kondisyon "hasarsız"
python3 muze.py geciken-listesi
```
- `restorasyonda` ve `odunc` durumlarına artık yalnızca bu komutlarla geçilir (`eser-durum` reddeder); her işlem
  tarihli kayıt tutar ve `hareketler` denetim izine yazılır. Açık kaydı olan eser `eser-durum` ile depoya alınamaz.
- Kayıtlar silinemez; kapanmış kayıt değiştirilemez. Geriye dönük girişte `--baslangic` / `--cikis` kullanılır.
- `geciken-listesi`: planlanan bitiş/dönüş tarihi geçmiş açık kayıtlar.
- Mevzuat (kontrol 2026-11-07, web aramasıyla; resmî metinle teyit edilmeli): yurt dışı gönderim 2863 s. Kanun md. 32
  kapsamındadır; program izin/karar numarası ve sigorta değeri ister, süreyi sınırlar (tek ülke 1 yıl, birden çok
  ülke 2 yıl). Yönetmelik 2020'de değişmiştir, güncel metin doğrulanmalıdır. Yurt içi ödünç ve restorasyon izin/usul
  kuralları (Müzeler İç Hizmetler Yönetmeliği vb.) doğrulanamadığı için program bunlarda yalnızca kayıt tutar;
  `--izin-no` serbest metindir. Sorumlu/kullanıcı personel adıdır (KVKK 6698), ziyaretçi verisi tutulmaz.
- Test: `python3 -m unittest test_gecis test_takip -v`

## Bilet tarifesi ve iade

```
python3 muze.py tarife-ayarla yetiskin 700 --baslangic 2026-07-01 --kaynak "KTB tarife duyurusu"
python3 muze.py tarife-listele
python3 muze.py bilet-iade yetiskin 1 --neden "yanlış tür seçildi" [--satis-tarihi 2026-11-01]
python3 muze.py rapor        # iade ve net tutarı da gösterir
```
- Fiyat artık `tarifeler` tablosundan, satış gününde geçerli son kayıttan okunur. Her kayıt tarihli, kaynaklı (yönerge/duyuru) ve
  değiştirilemez; tarife değişince yeni tarihle yeni kayıt eklenir. Tarife kaydı yoksa eski sabit fiyatlar (200 / 50 TL, doğrulanmamış varsayılan) kullanılır.
- `bilet-iade`: gerekçe zorunludur; iade edilebilir adet, o günün satışlarından hesaplanır (fazlası reddedilir). Gün içinde tarife
  değiştiyse iade tutarı o günün ortalama birim fiyatıdır. İade kayıtları silinemez/değiştirilemez; satış kaydı da değiştirilmez.
- Mevzuat (kontrol 2026-11-07, web aramasıyla; resmî metinle teyit edilmeli): giriş ücretleri Bakanlığın giriş usul ve esasları
  yönergesine ekli listededir (2252 s. Döner Sermaye Kanunu çerçevesi); kaynaklar güncel fiyatlarda çelişkilidir, tarife resmî duyurudan
  girilmelidir. Ücretsiz giriş kategorileri (ör. 18 yaş ve altı, 65 yaş ve üstü T.C. vatandaşları) yönergeye göredir; güncel yaş/belge
  şartları teyit edilmelidir. Bilet iadesinin usulüne dair hüküm doğrulanamadı: program yalnızca gerekçeli kayıt tutar; tahsilat/iade
  işlemi kurumun Döner Sermaye ve muhasebe usullerine göre ayrıca yapılır. Yalnızca personel adı tutulur (KVKK 6698).
- Test: `python3 -m unittest test_gecis test_takip test_tarife test_sayim -v`

## Günlük sayım ve envanter mutabakatı

```
python3 muze.py sayim-baslat --yer "Salon A" --sorumlu "A. Yılmaz" --komisyon "A. Yılmaz, B. Kaya, C. Demir"   # veya --sergi AD / --tumu
python3 muze.py sayim-isaretle 1 EF-001 EF-002 [--yer "Salon A"]     # sayımda bulunan eserler (birden çok numara)
python3 muze.py sayim-rapor 1                                        # açıkken taslak tutanak
python3 muze.py sayim-kapat 1                                        # kapatır ve mutabakat tutanağını yazar
python3 muze.py sayim-listele
```
- Başlangıçta kapsamdaki eserlerin anlık görüntüsü alınır. Beklenen: `depoda`/`sergide` eserler. `odunc`/`restorasyonda` eserler
  "dışarıda kayıtlı" sayılır, eksik yazılmaz.
- Tutanak: **eksik** (kayıtta var, bulunamadı), **fazla/beklenmeyen** (kapsam dışı veya kayıtlı durumu bulunmaya uymayan),
  **konum farkı** (`--yer` kayıtlıdan farklıysa), dışarıda kayıtlı. Kapanan sayım ve satırları değiştirilemez/silinemez.
- Program eser kaydını düşmez ve durumunu değiştirmez; yalnızca fark tutanağı üretir.
- Mevzuat (kontrol 2026-11-07, web aramasıyla ve yalnızca ikincil kaynaklarla; resmî metinle teyit edilmeli): Taşınır Mal
  Yönetmeliği uygulamasında yıl sonu sayımı harcama yetkilisinin görevlendirdiği sayım komisyonunca yapılır; eksik için tutanak ve
  kayıttan düşme teklifi, fazla için sayım fazlası fişi ve değer tespiti gerekir; müzeler Müze Yönetim Hesabı Cetveli düzenler.
  Bu işlemler kurumun taşınır usullerine göre ayrıca yürütülür. Müzeler İç Hizmetler Yönetmeliği'nin sayım hükümleri ve sayım
  sıklığı doğrulanamadı, program bunları varsaymaz. Komisyon üyeleri personel adıdır (KVKK 6698).
- Test: `python3 -m unittest test_gecis test_takip test_tarife test_sayim -v`

## Masaüstü saati

`python3 saat.py` — dijital saat (SS:DD), Efes hava durumu (Open-Meteo, 15 dk'da bir yenilenir) ve aylık takvim.
Gerekli: `python3-tk` (Linux). Kapatmak için Esc.

### Masaüstü kısayolu

`efes_muze/kisayol/` klasöründen:
- **Windows:** `Efes-Saat.bat` dosyasına sağ tık → Gönder → Masaüstü (kısayol oluştur). Python (tkinter dahil) kurulu olmalı.
- **macOS:** `Efes-Saat.command` dosyasını Dock'a veya masaüstüne sürükleyin (ilk kez `chmod +x` gerekebilir).
- **Linux:** `bash kisayol/linux-kisayol-kur.sh` masaüstüne ve uygulama menüsüne "Efes Saat" ekler.
