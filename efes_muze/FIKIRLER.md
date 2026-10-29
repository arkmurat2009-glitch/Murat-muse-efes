# Efes Müzesi Yönetim Programı: Fikirler

Kaynak: `efes_muze/muze.py` (eserler, sergiler, biletler tabloları; 9 alt komut), `saat.py`, `README.md`. `RAPOR_inceleme.md` / `RAPOR_analiz.md` depoda yok.

Mevcut durumun özeti: eserin yalnızca anlık durumu tutuluyor (geçmiş yok), "odunc" ve "restorasyonda" birer etiket (tarih, karşı kurum, sorumlu yok), bilet fiyatları kodda sabit, iade/iptal yok, kim ne yaptı kaydı yok. Bu eksikler aşağıdaki sıralamanın temelidir.

Mevzuat notları genel bilgidir; madde numaraları ve güncel eşikler uygulamadan önce hukuk/mevzuat birimince doğrulanmalıdır.

## İlk uygulanacak 2 fikir

1. **Eser hareket geçmişi ve denetim izi** (fikir 1): Durum değişikliklerini tarih, kullanıcı ve gerekçeyle ayrı bir tabloda tutar. Sergiye alma, depoya iade, restorasyona gönderme, ödünç verme izlenebilir olur. Çaba S, değer çok yüksek; diğer fikirlerin çoğu bu tabloya dayanır.
2. **Restorasyon ve ödünç takip kaydı** (fikir 2): "restorasyonda" ve "odunc" etiketlerini tarihli, sorumlu ve karşı kurumlu kayda çevirir; dönüş tarihi geçenleri raporlar. Çaba M, değer yüksek; koleksiyon güvenliği ve hesap verebilirlik için kritik.

## Fikir listesi (değer/çaba sırasıyla)

### 1. Eser hareket geçmişi ve denetim izi
- Fayda: Bir eserin nerede, ne zaman, kimin kararıyla bulunduğu geriye dönük görülür; kayıp/hasar şüphesinde ve sayım farklarında temel kanıt olur.
- Çaba: S
- Mevzuat: 2863 sayılı Kanun kapsamında koruma/envanter yükümlülüğü ve 5018 (kamu mali yönetimi, hesap verebilirlik) ile uyumlu; ayrıntılı madde doğrulanmalı.
- Taslak: Yeni tablo `hareketler(id, eser_id, tarih, eski_durum, yeni_durum, eski_sergi_id, yeni_sergi_id, kullanici, not)`. `eser_durum` ve `sergiye_yerlestir` içinde aynı işlemde (transaction) kayıt atılır. Yeni alt komut: `eser-gecmis EF-001`. Ayrıca `--kullanici` parametresi veya `USER` ortam değişkeni.

### 2. Restorasyon ve ödünç takibi
- Fayda: Hangi eserin kimde/hangi atölyede olduğu, ne zaman döneceği bellidir; geciken dönüşler uyarılır. Sigorta ve koşul raporu bilgisi eklenebilir.
- Çaba: M
- Mevzuat: Taşınır kültür varlıklarının ödünç/geçici çıkışı 2863 ve ilgili Bakanlık yönergelerine tabidir; izin süreçleri doğrulanmalı.
- Taslak: Tablolar `restorasyonlar(eser_id, baslangic, planlanan_bitis, atolye, sorumlu, bitis, not)` ve `oduncler(eser_id, kurum, cikis, planlanan_donus, gercek_donus, sigorta_degeri, izin_no)`. Alt komutlar: `restorasyon-baslat`, `restorasyon-bitir`, `odunc-ver`, `odunc-iade`, `geciken-listesi`. `eser-durum` bu komutlara yönlendirilir; "odunc" durumuna doğrudan geçiş engellenir.

### 3. Günlük sayım ve envanter mutabakatı
- Fayda: Salon/depo bazlı fiziksel sayım ile kayıtlı konumun karşılaştırılması; eksik/fazla eserin hızlı tespiti.
- Çaba: M
- Mevzuat: Taşınır envanter ve sayım usulleri (5018 ve Taşınır Mal Yönetmeliği) ile ilişkili; müzeye özgü kurallar doğrulanmalı.
- Taslak: Tablo `sayimlar(id, tarih, sorumlu)` ve `sayim_satirlari(sayim_id, eser_id, bulundu, not)`. Alt komut: `sayim-baslat SALON`, `sayim-isaretle EF-001`, `sayim-kapat` (kayıp listesini yazar). Eserler tablosuna `salon/raf` alanı eklenir (şu an serbest metin `bulundugu_yer`).

### 4. Bilet iade/iptal ve fiyat tablosu
- Fayda: Şu an satış geri alınamıyor ve fiyatlar kodda sabit. Fiyat tablosu geçerlilik tarihli olursa tarife değişikliği kod değişikliği gerektirmez; iade kaydı kasa raporunu doğru tutar.
- Çaba: S
- Mevzuat: Giriş ücretleri Kültür ve Turizm Bakanlığı tarifesine göre belirlenir; güncel tarife ve muafiyetler (çocuk, öğrenci, müzekart) doğrulanmalı. Gelir kaydı 5018 kapsamında.
- Taslak: Tablo `tarifeler(tur, fiyat, gecerli_baslangic)`; `biletler`e `iptal_id` veya negatif adet kaydı. Alt komutlar: `tarife-ayarla`, `bilet-iade`. `bilet_sat` fiyatı tablodan okur.

### 5. Ziyaretçi analitiği (haftalık/aylık/yıllık, tür ve gelir kırılımı)
- Fayda: Yoğun gün/dönem, tür dağılımı ve gelir eğilimi; personel planlaması ve etkinlik zamanlaması için veri.
- Çaba: S
- Mevzuat: Yalnızca toplu sayı tutulduğu için kişisel veri yok; kimlik/e-posta gibi alan eklenirse KVKK 6698 devreye girer.
- Taslak: Alt komut `rapor-donem --baslangic --bitis [--grupla gun|hafta|ay]`, `csv-disa-aktar`. Mevcut `biletler` tablosu yeterli; `tarih` üzerine indeks eklenir. İsteğe bağlı saat bilgisi (`saat` sütunu) ile yoğun saat analizi.

### 6. Erişilebilirlik ve ziyaret koşulları kaydı
- Fayda: Salon bazında engelli erişimi (rampa, asansör, dokunsal yüzey), yeterli olmayan alanların tespiti ve iyileştirme planı.
- Çaba: S
- Mevzuat: 5378 sayılı Engelliler Hakkında Kanun ve erişilebilirlik standartları; ilgili maddeler doğrulanmalı.
- Taslak: `sergiler` tablosuna `erisim_notu`, `erisilebilir (0/1)` sütunları; alt komut `sergi-erisim SERGI --erisilebilir evet --not "..."`; `rapor`ta erişilemeyen salonlar listelenir.

### 7. Güvenlik ve koşul (ortam) olay günlüğü
- Fayda: Hırsızlık girişimi, alarm, nem/sıcaklık sapması, hasar tespiti gibi olayların eser ve salonla ilişkilendirilmesi; önleyici bakım için eğilim.
- Çaba: M
- Mevzuat: Güvenlik kamerası/kayıt verisi eklenirse KVKK 6698 ve 6331 (iş sağlığı ve güvenliği) açısından doğrulanmalı. Olay kaydı kişisel veri içermemelidir.
- Taslak: Tablo `olaylar(id, tarih, tur, salon_id, eser_id, siddet, aciklama, kapatildi)`. Alt komutlar `olay-ekle`, `olay-listele --acik`. `saat.py` hava verisinden aşırı sıcak/nem uyarısı salon günlüğüne bağlanabilir (ileri aşama).

### 8. Sergi planlama: tarih aralığı, kapasite ve çakışma kontrolü
- Fayda: Sergilerin başlangıç/bitiş tarihi, salon kapasitesi; aynı eserin iki sergiye veya restorasyon dönemine çakışmasının engellenmesi.
- Çaba: M
- Mevzuat: Doğrudan bir hüküm yok; geçici sergi için ödünç izinleri fikir 2 ile birlikte doğrulanmalı.
- Taslak: `sergiler`e `baslangic, bitis, kapasite`; `sergiye_yerlestir` kapasite ve çakışma kontrolü yapar. Alt komutlar `sergi-takvim`, `sergi-kapat` (eserleri otomatik depoya alır ve geçmişe yazar).

### 9. Veri bütünlüğü ve yedekleme (eser alanları, doğrulama, günlük yedek)
- Fayda: Koleksiyon verisinin tek SQLite dosyasında olması risklidir. Durum değerleri şu an yalnızca komut satırında kısıtlı, veritabanında değil; `eser-durum` "sergide" değerini sergi olmadan atayabiliyor ve olmayan eser için sessizce "bulunamadı" diyor.
- Çaba: S
- Mevzuat: Kayıtların saklanması ve arşiv (resmi kayıt niteliği) için ilgili saklama süreleri doğrulanmalı.
- Taslak: `CHECK(durum IN (...))`, `CHECK(durum!='sergide' OR sergi_id IS NOT NULL)`; alt komutlar `yedek` (dosya kopyası + tarih damgası), `dogrula`. Şema değişikliği için basit bir `user_version` göçü.

### 10. Sürdürülebilirlik göstergeleri ve çok dilli bilgi etiketi çıktısı
- Fayda: (a) Enerji/su/atık gibi göstergelerin aylık takibi; (b) eser bilgi etiketlerinin TR/EN (ve diğer diller) metin çıktısı, uluslararası ziyaretçi için.
- Çaba: M
- Mevzuat: Etiket içeriğinde telif/görsel hakları için 5846 sayılı Fikir ve Sanat Eserleri Kanunu doğrulanmalı; enerji verimliliği hedefleri kamu kurumları için genelgelere bağlı olabilir (doğrulanmalı).
- Taslak: Tablolar `gostergeler(ay, tur, deger)` ve `eser_etiketleri(eser_id, dil, baslik, aciklama)`. Alt komutlar `gosterge-gir`, `gosterge-rapor`, `etiket-yaz EF-001 --dil en`, `etiket-cikar --salon A1`.

## Sıralama gerekçesi

Fikir 1 ve 2 en yüksek değer/çaba oranına sahiptir ve kayıt bütünlüğünü sağlar. 3 ve 8 bunların üzerine kurulur. 4, 5, 6, 9 küçük çabayla görünür kazanç sağlar. 7 ve 10 daha geniş kapsamlı olduğu için sona bırakılmıştır.

## Genel not

Kişisel veri (ziyaretçi, personel, kamera) tutulacaksa önce KVKK 6698 kapsamında veri envanteri, aydınlatma metni ve saklama süresi belirlenmelidir.
