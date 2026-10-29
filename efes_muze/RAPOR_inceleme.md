# Efes Müzesi Yönetim Programı - İnceleme Raporu

Kapsam: `efes_muze/muze.py` (160 satır), `efes_muze/saat.py` (146 satır), `efes_muze/README.md`. Kod değiştirilmemiştir.
Not: Bu rapor hukuki tavsiye değildir. Mevzuat maddeleri bu incelemede güncel kaynaktan doğrulanmamıştır (internet/skill kullanılmadı); "doğrulanmalı" ifadeleri bu nedenledir.

## Kritik

1. **Eser durum geçişi kontrolsüz, denetim izi yok** - `muze.py:70-75`. `eser-durum` herhangi bir durumdan herhangi birine geçişe izin verir (ör. restorasyondan doğrudan `sergide`; `odunc` eser için iade kaydı yok). `sergide` durumu `sergi_id` olmadan atanabilir (veri tutarsızlığı). İki UPDATE aynı işlemde ama tutarlılık kuralı yok. Kim/ne zaman/neden değiştirdi kaydı tutulmuyor.
2. **Durum alanında DB düzeyinde kısıt yok** - `muze.py:19`. `durum` için CHECK yok; doğrulama yalnızca argparse'ta (`muze.py:138,142`). Başka bir araçla/SQL ile geçersiz değer girilebilir. `biletler.tur/adet/tutar` için de CHECK yok (`muze.py:27-33`).
3. **Yerleştirmede durum kuralı eksik** - `muze.py:92`. Yalnızca `restorasyonda` engelleniyor; `odunc` (kurum dışında) eser sergiye yerleştirilebilir.
4. **Bilet geliri kaydı mali mevzuata uygun değil (doğrulanmalı)** - `muze.py:103-112`. Makbuz/bilet seri numarası, iptal/iade, kasiyer, saat, ödeme yöntemi, gün sonu mutabakatı yok. Kayıtlar silinebilir/değiştirilebilir (DB dosyası düz SQLite). 5018 sayılı Kanun ve ilgili tahsilat/makbuz düzenlemeleri ile müze giriş ücreti tebliğleri açısından doğrulanmalı. Tutar `REAL` (float) tutuluyor (`muze.py:32`); para için kuruş cinsinden INTEGER/Decimal önerilir.
5. **Fiyatlar kod içine gömülü** - `muze.py:9`. Resmî ücret tarifesi değiştiğinde kod değişmeli; tarih geçerlilikli tarife tablosu yok. Tarifedeki tutarların (200/50 TL) güncel resmî tarifeyle uyumu doğrulanmalı. `cocuk` ve `muze_kart` ücretsiz satırları da gelir tablosuna karışıyor; ücretsiz giriş gerekçesi (yaş/belge) kaydedilmiyor.
6. **2863 / envanter-belgeleme yetersizliği (doğrulanmalı)** - `muze.py:11-20`. Eser kaydı yalnızca no, ad, dönem, malzeme, yer içeriyor. Müze envanter/belgeleme uygulamalarının genelde istediği alanlar yok: ölçü, edinme yolu/tarihi (satın alma, bağış, kazı), buluntu yeri/kazı bilgisi, fotoğraf/belge, durum/koruma raporu, sigorta değeri, zimmet/sorumlu. Resmî envanter ve düşüm/ödünç/restorasyon çıkış-giriş kayıtları için mevzuat gereksinimleri doğrulanmalı. Eser silme/düşüm komutu da yok (iyi), ama veri kaybı yedeği de yok (bkz. 8).
7. **Erişim kontrolü ve yetkilendirme yok** - tüm komutlar `muze.py:155`. Herkes çalıştırabilir; kullanıcı kimliği yok, dolayısıyla sorumlu kişi izlenemez. DB dosyası `efes_muze.db` göreli yoldadır (`muze.py:8`), çalışma dizinine göre farklı DB oluşur (sessizce boş yeni veritabanı açılır).

## Önemli

8. **Yedekleme/bütünlük** - SQLite dosyası için yedek, WAL/dışa aktarma yok; dosya kaybı = envanter kaybı.
9. **Bağlantılar kapatılmıyor** - `muze.py:37-42, 65, 84, 117, 135`: `with baglan() as con` yalnızca commit/rollback yapar, bağlantıyı kapatmaz. `eser_listele`, `sergi_listele`, `rapor` bağlantıyı hiç yönetmiyor. Kısa ömürlü CLI'de sorun az; ama sürekli çalışan kullanımda sızıntı olur. Her komutta `CREATE TABLE IF NOT EXISTS` çalıştırılıyor; şema sürümleme/migrasyon yok.
10. **Girdi doğrulama** - boş/çok uzun `no`/`ad` kabul edilir (`muze.py:45-52`); envanter no formatı (örn. `EF-001`) doğrulanmıyor. `--tarih` biçimi doğrulanmıyor (`muze.py:117`), geçersiz tarih sessizce 0 sonuç döner. `adet` için üst sınır yok (`muze.py:106`). `LIKE` içindeki `%`/`_` kaçışsız (`muze.py:60`).
11. **Hata yönetimi** - `eser_durum` bulunamayan esere ikinci UPDATE'i yine çalıştırır, `muze.py:73-74` (zararsız ama gereksiz). `sqlite3.OperationalError` (kilitli/yazılamaz DB) yakalanmıyor; kullanıcıya ham traceback gider. `eser_ekle`'de `IntegrityError` tüm kısıt ihlallerini "numara kayıtlı" diye raporlar (`muze.py:52`).
12. **`bulundugu_yer` ile `sergi_id` yinelenir** - `muze.py:16,20`: iki ayrı konum bilgisi; `yerlestir` `bulundugu_yer` alanını güncellemez, tutarsızlık oluşur. Konum geçmişi yok.
13. **Test yok** - hiç test dosyası bulunmuyor. Durum geçişi, yerleştirme kuralı, bilet tutarı ve rapor toplamları için birim testi gerekli.
14. **Tarih/saat** - `date.today()` yerel saat kullanır (`muze.py:111, 117`); gün sonu/zaman dilimi tutarsızlığı olabilir. Satış saati kaydedilmiyor.
15. **KVKK (6698) - `saat.py` içindeki beyan** - `saat.py:3-5` docstring "kişisel veri toplanmaz/saklanmaz (KVKK kapsamında veri yok)" diyor. Hava durumu isteği (`saat.py:45`) dış servise (Open-Meteo) giderken kullanıcının IP adresi sunucuya ulaşır; IP adresinin kişisel veri sayılıp sayılmayacağı ve yurt dışı aktarım değerlendirmesi hukuk birimince doğrulanmalı. Kesin "veri yok" ifadesi yumuşatılmalı. Ayrıca Open-Meteo ücretsiz API'sinin kurumsal/ticari olmayan kullanım şartlarına uygunluğu doğrulanmalı (CC BY 4.0 atıf kaynak gösteriliyor, iyi).
16. **KVKK - ileride bilet/ziyaretçi verisi** - Şu an bilet kaydı kişisel veri içermiyor (iyi). İsim/TC/e-posta (müze kart, grup rezervasyonu) eklenirse aydınlatma, saklama süresi, silme ve erişim kayıtları gerekir.
17. **Ödünç (`odunc`) süreci** - ödünç veren/alan kurum, tarih aralığı, sigorta, durum raporu, iade tarihi tutulmuyor (`muze.py:138-142`). Müzelerde ödünç/geçici çıkış için ilgili yönetmelik hükümleri doğrulanmalı.

## İyileştirme

18. **README ile uyumsuzluk** - `README.md:3` "bağımlılıksız" diyor; `saat.py` için `python3-tk` gerekli (README:19'da belirtilmiş, çelişki küçük). `bilet` türleri README'de var ama `cocuk` fiyat bilgisi (0 TL) kullanıcıya açık değil. Satış sonrası makbuz/numara yazdırılmıyor.
19. **Eksik komutlar** - eser düzenleme/silme(düşüm), sergi silme/düzenleme, bilet iptali, rapor dışa aktarma (CSV), tarih aralıklı rapor, eser detay görünümü.
20. **Kullanılabilirlik** - çıktılar sabit genişlikli sütunlarda (`muze.py:66-67`) uzun adlarda kayar; sonuç yoksa boş çıktı veriliyor ("kayıt bulunamadı" mesajı yok). `yerlestir` hata mesajı "bulunamadı veya restorasyonda" iki nedeni birleştiriyor (`muze.py:94`).
21. **`saat.py` küçük noktalar** - `HAVA_KODLARI` (`saat.py:30-38`) 56,57,66,67,77,85,86 gibi WMO kodlarını içermiyor, "Bilinmiyor" gösterir. Emoji simgeler bazı Linux yazı tiplerinde görünmeyebilir. `except Exception` (`saat.py:135`) hatayı gizler; günlük/log yok. `-topmost` (`saat.py:56`) her zaman üstte kalır, bazı ortamlarda rahatsız edici olabilir. İş parçacığı-ana döngü paylaşımı (`_hava_sonuc`) pratikte güvenli (tek atama) ancak kilitsiz.
22. **Dil/kodlama** - dosya açma/yazma kodlaması belirtilmemiş; Türkçe karakterli çıktı için terminal kodlaması UTF-8 olmalı (`PYTHONIOENCODING`).

## Mevzuat özet tablosu (hepsi doğrulanmalı)

| Alan | Gözlem |
|---|---|
| 2863 Kültür ve Tabiat Varlıklarını Koruma Kanunu | Envanter/belgeleme alanları ve hareket kayıtları eksik (madde 6, 17) |
| 6698 KVKK | Mevcut hâlde kişisel veri yok; `saat.py` beyanı fazla kesin (madde 15) |
| 5018 Kamu Mali Yönetimi | Gelir kaydı/makbuz/mutabakat yok (madde 4, 5) |
| Müze iç hizmet yönetmeliği ve ücret düzenlemeleri | Tarife kodda sabit; iç hizmet kuralları (ödünç, zimmet, giriş-çıkış) modellenmemiş (madde 5, 17) |

## Öncelikli öneri sırası
1. Durum geçişi kuralları + `durum_gecmisi` tablosu + CHECK kısıtları (1-3).
2. Bilet: makbuz no, iptal/iade, INTEGER kuruş, tarife tablosu (4-5).
3. Envanter alanlarının mevzuata göre genişletilmesi (6).
4. Test, bağlantı yönetimi, yedekleme (8-9, 13).
5. KVKK beyanının hukuk birimince gözden geçirilmesi (15).
