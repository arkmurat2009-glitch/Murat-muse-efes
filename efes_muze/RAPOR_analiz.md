# Analiz Raporu: Eser durum geçişi + hareket denetim izi (commit edilmemiş değişiklikler)

Kapsam: `muze.py` (diff), `README.md` (diff), yeni `eklentiler/` (`__init__`, `dogrulama`, `gecis`, `hareketler`), `test_gecis.py`. Kod değiştirilmemiştir. Tüm testler/komutlar geçici DB ile (`EFES_MUZE_DB`) çalıştırıldı; depodaki `efes_muze.db`'ye dokunulmadı. Hukuki tavsiye değildir.

## Özet (1 dakikalık)

Değişiklik, RAPOR_inceleme.md Kritik 1-3 maddelerini (kontrolsüz geçiş, DB kısıtı yok, odunc eserin sergiye yerleşmesi) ve FIKIRLER.md fikir 1'i (hareket geçmişi, `--kullanici`, `eser-gecmis`) karşılıyor. 5 birim testi geçti; CLI uçtan uca doğru çalıştı (geçerli/geçersiz geçişler, hareket kaydı, "zaten o durumda", bulunamadı, geri alma). Eski şemalı DB açılışta sorunsuz yükseltildi, mevcut veri bozulmadı. Kritik bulgu yok. Önemli bulgular: (1) eski veride geçersiz durum (ör. `kayip`) olan eser hiçbir komutla kurtarılamaz; (2) geçiş okuma+yazma tek işlemde değil (nadir yarış); (3) test kapsamı dar (CLI, eski DB yükseltme, atomiklik, `kullanici` öncelik sırası yok). Öneri: **birleştir, küçük düzeltmelerle** (aşağıda).

## Bulgular

### Kritik
Yok.

### Önemli
1. **Eski veride tutarsız durum kurtarılamıyor** - `eklentiler/gecis.py` `GECISLER`. Denendi: eski DB'de `durum='kayip'` olan eser için `eser-durum L4 depoda` -> "'kayip' durumundan 'depoda' durumuna geçilemez. İzinli: yok." Tetikleyiciler yalnızca yeni yazmaları denetlediğinden eski bozuk satırlar kalır ve komutla düzeltilemez (yalnızca doğrudan SQL ile). Öneri: bilinmeyen eski durum için `depoda`'ya (gerekçeli) düzeltme geçişi izin ver veya README'ye bu durumun elle düzeltileceğini yaz. Aynı biçimde `sergide`+`sergi_id NULL` ve `odunc`+`sergi_id dolu` eski satırlar denendi: `depoda`'ya geçişle düzeliyor (iyi), `L3` için hareket kaydında eski sergi görünüyor (iyi).
2. **Okuma ve yazma aynı işlemde değil (TOCTOU)** - `gecis.degistir`: `SELECT` işlem dışında, `INSERT hareketler` ile işlem başlıyor; eşzamanlı iki kullanıcı aynı eski durumdan geçiş yaptırırsa her ikisi de başarılı olup hareket zinciri (`eski_durum`) tutarsız olabilir. Tetikleyici bunu yakalamaz (durum yine geçerli). Çok kullanıcılı/paylaşımlı dosya kullanımında önemli; tek kullanıcılı CLI'de düşük olasılık. Öneri: `BEGIN IMMEDIATE` ile başlatmak veya `UPDATE ... WHERE durum=?` + `rowcount` kontrolü.
3. **Test kapsamı yetersiz** - `test_gecis.py` yalnızca `gecis.degistir`'i doğrudan çağırıyor. Eksik: CLI akışı (`eser-durum`, `yerlestir`, `eser-gecmis`; ör. `eser-gecmis` içindeki `from muze import baglan` betik `__main__` iken modülü ikinci kez yükler, şu an çalışıyor ama kırılgan), eski DB yükseltme, kullanıcı öncelik sırası (`--kullanici` > `EFES_KULLANICI` > OS), hareket + güncelleme atomikliği/rollback, sergiden sergiye geçiş, "zaten o durumda" hatası, `sergide`->`sergide` farklı sergi. Test, import sırasına bağlı bir `os.environ` hilesi kullanıyor (modül yüklenmeden önce ayarlanmalı); başka test modülü `muze`'yi önce içe aktarırsa gerçek DB'ye yazabilir.
4. **Geçmiş kaydı için KVKK/saklama notu yalnızca belgede** - `hareketler.kullanici` OS kullanıcı adı (ör. `root`) olabilir; kişisel veri (personel) sayılabilir. README notu doğru yönde; saklama süresi, erişim ve aydınlatma kurum politikasında tanımlanmalı. Paylaşımlı hesapla (`root`) kullanımda denetim izi anlamsızlaşır; sonuç çıktıda `(root)` görüldü. Öneri: kullanıcı verilmezse ve OS kullanıcısı genel hesapsa uyarı ver veya `--kullanici` zorunlu yap.
5. **Ekleme-yalnız garantisi DB dosyası düzeyinde değil** - tetikleyiciler `DROP TRIGGER` veya dosyayı doğrudan düzenleyerek aşılabilir; 2863/5018 açısından "değiştirilemez kayıt" iddiası yalnızca yazılım kontrolüdür. README'de bu sınır belirtilmeli; dosya yedeği/imza ayrıca düşünülmeli (RAPOR_inceleme madde 8 hâlâ açık).

### Küçük
6. `hareketler.kullanici_adi(a=None)` parametresi `gecis.degistir`'de hiç `a` ile çağrılmıyor; `kullanici or kullanici_adi()` kullanılıyor, `a` yolu ölü. `gecis.sema` boş ve `import sqlite3, sys` kullanılmıyor (`gecis.py`).
7. `eklentiler/__init__.py` docstring'i `parametreler(p)` kancasından söz ediyor ama uygulanmamış.
8. `with baglan() as con` yalnızca commit/rollback yapar, bağlantıyı kapatmaz (RAPOR_inceleme madde 9 açık; yeni kod `eser_gecmis`'te doğru kapatıyor, tutarsızlık).
9. `eser-durum EF-001 sergide` mesajı yönlendirici (iyi), ama `argparse` seçeneğinde `sergide` hâlâ listeleniyor; yardım metni bu yüzden yanıltıcı.
10. `sergide`->`sergide` (başka sergi) için `eser-durum` değil `yerlestir` gerekir; README bunu söylüyor, `GECISLER`'deki `sergide` kendine izni bunu destekler. Açıklama yeterli.
11. Hareket tarihi yerel saat, saat dilimi yok (`datetime.now().isoformat`). Gün sonu karşılaştırmasında tutarsızlık olabilir (RAPOR_inceleme madde 14).
12. Restorasyon/ödünç hâlâ yalnızca etiket (karşı kurum, süre, izin yok) - FIKIRLER fikir 2 kapsam dışı; mevzuat açısından ödünç/geçici çıkış belgelenmesi (2863) hâlâ eksik. Bu değişiklik yeni risk doğurmuyor, mevcut eksiği değiştirmiyor.

## Doğrulama sonuçları (geçici DB)

| Kontrol | Sonuç |
|---|---|
| `python3 -m unittest test_gecis -v` | 5/5 geçti |
| Eski şema DB'yi yeni kodla açma | Sorunsuz; tablolar/tetikleyiciler eklendi, veri korundu |
| depoda->sergide (`eser-durum`) | Reddedildi, `yerlestir` yönlendirmesi |
| `yerlestir` -> odunc -> depoda | Çalıştı; her biri `eser-gecmis`'te, sergi alanı doğru |
| Aynı duruma tekrar | "zaten 'depoda' durumunda" |
| Bilinmeyen eser | "Eser bulunamadı." (`Hata:` mesajıyla çıkış kodu 1) |
| Bilet adet 0 / -1 | Reddedildi |
| `rapor` | Eski ve yeni verilerle çalıştı |
| Depo çalışma ağacı | Yalnızca zaten bilinen değişiklikler; `efes_muze.db` oluşmadı |

## Eski verilerle uyum
Şema yalnızca ekleme (yeni tablo, indeks, tetikleyici); eski tablolar değişmedi, geriye dönük yükseltme otomatik. Eski satırlara dokunulmaz (Önemli 1 hariç). Eski sürümle açılan aynı DB çalışmaya devam eder (yeni tabloyu yok sayar), ancak eski sürüm geçişleri hareket kaydı bırakmaz ve tetikleyiciler eski sürümün geçersiz yazımlarını reddedebilir (ör. `odunc` eseri `yerlestir` ile sergiye almak artık hata verir).

## İstenenleri karşılama
- RAPOR_inceleme Kritik 1, 2, 3: karşılandı (DB kısıtı bilet için de eklendi). Kritik 7 (kullanıcı kimliği): kısmen (kimlik kendi beyanı, doğrulama yok). Madde 13 (test yok): kısmen.
- FIKIRLER fikir 1: karşılandı. Fikir 2 (restorasyon/ödünç kaydı): bilinçli olarak yok.
- Mevzuat: 2863 (envanter/hareket izi) için olumlu adım, doğrulanmalı; KVKK 6698: personel kimliği tutuluyor, saklama politikası şart (Önemli 4); 5018: hesap verebilirlik için olumlu; bilet/makbuz boşlukları değişmedi.

## Varsayımlar
- Mevzuat madde numaraları ve gereksinimleri güncel kaynaktan doğrulanmadı (internet kullanılmadı).
- Tek kullanıcılı, yerel SQLite CLI kullanımı varsayıldı; eşzamanlılık bulguları buna göre ağırlıklandırıldı.
- Eski DB senaryosu, `HEAD` sürümünün `muze.py` dosyasıyla oluşturulan geçici DB'ye elle eski/tutarsız satırlar eklenerek denendi.
- `.claude/` altındaki ajan tanımları kapsam dışı bırakıldı (kod değil).

## Karar önerisi: **Düzelt (küçük) ve birleştir**
Mimari doğru, geriye dönük uyumlu, kritik hata yok. Birleştirmeden önce: (a) bozuk eski durumdan kurtarma yolu veya belge notu (Önemli 1), (b) `UPDATE ... WHERE durum=?` ile yarışa dayanıklılık (Önemli 2), (c) birkaç ek test: CLI, eski DB yükseltme, rollback (Önemli 3), (d) README'ye "denetim izi dosya düzeyinde korumasızdır" notu (Önemli 5). Geri alma gerekmez; bu düzeltmeler ayrı küçük commit olabilir.
