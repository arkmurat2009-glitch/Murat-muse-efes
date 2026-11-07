# Efes Müzesi ve Bağlı Birimleri Yönetim Planı (Taslak)

> **Revizyon notu (28.10.2026):** Bu dosya `claude/efes-muzesi-yonetim-plani-hw4v6w` dalındaki taslağın mevzuat kontrolüne göre düzeltilmiş kopyasıdır. Değişen yerler `[Düzeltme]` ile işaretlidir. Kontrol web aramasıyla yapılmış, resmî metinler (mevzuat.gov.tr) doğrudan teyit edilememiştir.

> **Hukuki not:** Bu planda yalnızca yürürlükteki gerçek mevzuata atıf yapılmıştır. Madde numaraları bilerek verilmemiştir. Uygulamaya geçmeden önce güncel metinler mevzuat.gov.tr üzerinden ve Müdürlüğün bağlı olduğu Kültür ve Turizm Bakanlığı Kültür Varlıkları ve Müzeler Genel Müdürlüğü talimatlarıyla teyit edilmelidir. Bu belge hukuki görüş değildir.

## 1. Kapsam ve mevcut durum

Depodaki `efes_muze/muze.py` programı şunları yapar:

| Alan | Mevcut işlev |
|---|---|
| Eser envanteri | Envanter no, ad, dönem, malzeme, yer ve durum (depoda / sergide / restorasyonda / ödünç) |
| Sergi yönetimi | Sergi ve salon tanımı, esere sergi atama |
| Bilet | Yetişkin 200 TL, öğrenci 50 TL, çocuk ve müze kart ücretsiz. Günlük rapor |

**Bağlı birimler** (ör. ören yeri, ev müzesi, depo ve restorasyon atölyesi, kütüphane) depoda tanımlı değildir. Plan bunları "birim" kavramıyla modellemeyi önerir (Bölüm 6). Gerçek birim listesi Müdürlükten alınmalıdır.

## 2. Dayanak mevzuat

| Konu | Mevzuat |
|---|---|
| Koruma, envanter, müze işleyişi, ödünç ve sergileme, izinsiz kazı ve kaçakçılık | 2863 sayılı Kültür ve Tabiat Varlıklarını Koruma Kanunu ve ilgili yönetmelikleri |
| Kültür varlığı kaçakçılığı, yurt dışına çıkarma ve izinsiz kazı suçları `[Düzeltme]` | 2863 sayılı Kanun (ceza hükümleri; md. 67 ve devamı, yurt dışına çıkarma md. 68, izinsiz kazı md. 74 ikincil kaynaklara göre, madde numaraları resmî metinden teyit edilecek). 5607 sayılı Kaçakçılıkla Mücadele Kanunu yalnızca yurt dışından getirme (ithalat) bağlamında devreye girer |
| Müzenin iç işleyişi, Eser Envanter Defteri, personel görevleri `[Düzeltme: eklendi]` | Müzeler İç Hizmetler Yönetmeliği (eski "Anıtlar ve Müzeler Genel Müdürlüğü" adını kullanır; güncel yürürlüğü teyit edilecek) |
| Özel güvenlik `[Düzeltme: eklendi]` | 5188 sayılı Özel Güvenlik Hizmetleri Hakkında Kanun |
| Salon/alan tahsisi `[Düzeltme: eklendi]` | Süreli Kullanım Yönergesi |
| Mali yönetim, bütçe, iç kontrol | 5018 sayılı Kamu Mali Yönetimi ve Kontrol Kanunu |
| Taşınır kayıt ve sayım | Taşınır Mal Yönetmeliği (müzeler genel cetvel yerine Müze Yönetim Hesabı Cetveli kullanır) |
| Satın alma, restorasyon ve hizmet ihaleleri | 4734 sayılı Kamu İhale Kanunu, 4735 sayılı Kamu İhale Sözleşmeleri Kanunu |
| Kişisel veri | 6698 sayılı KVKK |
| İş sağlığı ve güvenliği, afet ve yangın | 6331 sayılı İSG Kanunu, Binaların Yangından Korunması Hakkında Yönetmelik |
| Personel | 657 sayılı Devlet Memurları Kanunu, 4857 sayılı İş Kanunu (işçi kadroları) |
| Fotoğraf ve yayın hakları | 5846 sayılı Fikir ve Sanat Eserleri Kanunu |
| Bilgi edinme | 4982 sayılı Bilgi Edinme Hakkı Kanunu |
| Elektronik kayıt ve imza | 5070 sayılı Elektronik İmza Kanunu |
| Dünya Mirası | UNESCO 1972 Dünya Mirası Sözleşmesi (Efes, 2015'ten beri listede) ve Yönetim Planı yükümlülükleri |

## 3. Organizasyon ve sorumluluklar

- **Müze Müdürü:** Genel yönetim, Bakanlıkla yazışma, harcama yetkilisi (5018 kapsamında).
- **Envanter ve Kayıt Birimi:** Eser kayıtları, sayım, ödünç ve emanet takibi.
- **Koruma ve Restorasyon Birimi:** Durum raporları, müdahale kayıtları, Bakanlık ve Bölge Kurulu izinleri.
- **Sergi ve Eğitim Birimi:** Sergi planı, eğitim programları.
- **Ziyaretçi Hizmetleri ve Bilet:** Bilet satış, müze kart, ziyaretçi istatistiği.
- **İdari ve Mali İşler:** Muhasebe, taşınır, satın alma, personel.
- **Güvenlik ve İSG:** Kamera, alarm, yangın, tahliye, iş güvenliği uzmanı ve işyeri hekimi.
- **Bilgi İşlem ve KVKK Sorumlusu:** Sistem, yedekleme, veri güvenliği.

Her birim için görev tanımı, vekâlet ve imza yetkisi yazılı olarak belirlenir.

## 4. Yönetim alanları ve ilkeler

### 4.1 Envanter ve koleksiyon yönetimi
1. Her eser için benzersiz envanter numarası ve fotoğraf, ölçü, malzeme, dönem, buluntu yeri ve edinim şekli kaydı tutulur.
2. Ödünç, geçici sergi ve yurt dışı gönderimi Bakanlık izniyle yapılır. Sigorta, kondisyon raporu ve nakliye şartları belgelenir.
3. Yılda en az bir kez, yıl sonunda kurulan sayım komisyonlarınca fiziki sayım yapılır. Fark tutanağa bağlanır ve Bakanlığa bildirilir (Bakanlık genelgesi, 12.03.2020; güncelliği teyit edilecek). `[Düzeltme]`
5. Müzeye giren eser, Eser Envanter Defteri'ne en geç bir ay içinde kaydedilir (Müzeler İç Hizmetler Yönetmeliği; teyit edilecek). `[Düzeltme: eklendi]`
4. Her kayıt değişikliği tarih, kullanıcı ve gerekçeyle izlenir (denetim izi).

### 4.2 Koruma ve restorasyon
1. Müdahale öncesi belgeleme (fotoğraf, rapor) zorunludur.
2. Restorasyonda olan eser sergilenemez. Programda bu kural zaten uygulanır.
3. Dış firma ihaleleri 4734 uyarınca yürütülür.

### 4.3 Sergi ve eğitim
Sergi planı yıllık hazırlanır. Eser sergilenmeden önce durum kontrolü, ışık ve nem koşulları ve güvenlik değerlendirmesi yapılır. Yayın ve afişte fotoğraf haklarına uyulur.

### 4.4 Ziyaretçi ve gelir yönetimi
1. Giriş ücretleri Bakanlıkça belirlenen tarifeye göre uygulanır. Programdaki 200 / 50 TL fiyatları doğrulanamamıştır; kaynaklar çelişkilidir ve güncel tarife resmî duyurudan alınmalıdır. `[Uyarı]` Programdaki sabit fiyatlar (200 / 50 TL) tarife değişince güncellenmelidir.
2. Ücretsiz giriş kategorileri (çocuk, müze kart, mevzuatta sayılanlar) tarifeye uygun işlenir.
3. Gelirler Bakanlık usulüne göre ilgili hesaba yatırılır. Gün sonu raporu ile mutabakat yapılır.

### 4.5 Güvenlik, İSG ve afet
Özel güvenlik görevlisi çalıştırılıyorsa 5188 sayılı Kanun hükümlerine uyulur. `[Düzeltme: eklendi]` Yangın, deprem ve hırsızlık için risk analizi, tahliye ve eser kurtarma planı hazırlanır. Yılda en az bir tatbikat yapılır. Personel eğitimleri kayıt altına alınır.

### 4.6 Kişisel veri (KVKK)
Ziyaretçi verisi asgari tutulur. Şu an yalnızca tür ve adet tutulur, kimlik tutulmaz, ki bu uygundur. Kimlik veya iletişim bilgisi toplanacaksa aydınlatma metni, saklama süresi ve imha politikası gerekir. Kamera kayıtları için de aydınlatma yapılır.

### 4.7 Mali yönetim ve iç kontrol
Yıllık faaliyet ve bütçe programı hazırlanır. Taşınır kayıtları Taşınır Mal Yönetmeliğine uygun tutulur; yıl sonunda Taşınır Sayım ve Döküm Cetveli düzenlenir ve müze birimleri için Müze Yönetim Hesabı Cetveli hazırlanır. `[Düzeltme]` İç kontrol eylem planı yılda bir güncellenir.

## 5. Yıllık eylem takvimi

| Dönem | Faaliyet |
|---|---|
| Ocak | Yıllık çalışma programı, bütçe ve ihtiyaç listesi |
| Ocak–Şubat | Yıl sonu sayım farklarının tutanağa bağlanması ve Bakanlığa bildirimi `[Düzeltme: sayım yıl sonuna alındı]` |
| Nisan | Yangın ve afet tatbikatı, İSG eğitimi |
| Mayıs–Eylül | Sergi ve eğitim programları, yüksek sezon ziyaretçi planı |
| Ekim | Restorasyon ve bakım ihaleleri |
| Kasım | Yedek alma testi, KVKK ve bilgi güvenliği gözden geçirme |
| Aralık | Yıl sonu envanter ve taşınır sayımı, faaliyet raporu, performans değerlendirme, iç kontrol raporu `[Düzeltme]` |

## 6. Yazılım yol haritası (mevzuata uyum açıkları)

Mevcut `muze.py` kodundan çıkan eksikler:

| # | Açık | Gerekçe | Öncelik |
|---|---|---|---|
| 1 | Denetim izi yok (kim, ne zaman değiştirdi) | Envanter ve taşınır denetimi | Yüksek |
| 2 | Ödünç durumu için ödünç alan kurum, izin no ve tarih kaydı yok | 2863 kapsamında izin takibi | Yüksek |
| 3 | `eser-durum` herhangi bir geçişe izin veriyor (ör. restorasyondan doğrudan sergiye) | Koruma ilkeleri | Orta |
| 4 | Eser silme ve düzeltme akışı yok, fotoğraf, ölçü, edinim şekli alanları yok | Envanter bütünlüğü | Yüksek |
| 5 | Bilet fiyatları kodda sabit, ücretsiz giriş gerekçesi kaydı yok | Tarifeye uyum | Orta |
| 6 | Birim (bağlı müze, depo, atölye) kavramı yok | Bağlı birim yönetimi | Orta |
| 7 | Kullanıcı ve yetki yok | İmza yetkisi, KVKK güvenliği | Yüksek |
| 8 | Yedekleme ve veritabanı koruma yok (SQLite dosyası) | Veri güvenliği | Orta |
| 9 | Sergi yerleştirmede güvenlik ve çevre koşulu kontrolü yok | Koruma | Düşük |

Önerilen aşamalar:
1. **Faz 1 (1–2 ay):** Denetim izi, eser alanlarının genişletilmesi, ödünç kaydı.
2. **Faz 2 (3–4 ay):** Birim modeli, kullanıcı ve rol yönetimi, durum geçiş kuralları.
3. **Faz 3 (5–6 ay):** Tarife tablosu, gelir mutabakatı, yedekleme, raporlama.

## 7. Performans göstergeleri

- Sayım farkı oranı (hedef: sıfır açıklanamayan fark)
- Kayıtlı eser oranı (fotoğraflı ve tam kayıtlı)
- Restorasyon süresi ve bekleyen eser sayısı
- Yıllık ziyaretçi sayısı ve gelir
- Tatbikat ve eğitim tamamlanma oranı
- Denetim bulgularının kapatılma süresi

## 8. Riskler

| Risk | Önlem |
|---|---|
| Eser kaybı veya hırsızlık | Sayım, güvenlik sistemi, erişim yetkisi |
| Yangın, deprem | Tahliye planı, tatbikat, eser kurtarma sırası |
| Veri kaybı | Düzenli yedek, yetkisiz erişim kontrolü |
| Mevzuat değişikliği | Yıllık mevzuat gözden geçirme |
| Mali usulsüzlük | İç kontrol, gün sonu mutabakat, görevler ayrılığı |

## 9. Açık sorular (Müdürlükten alınacak)

1. Bağlı birimlerin resmî listesi nedir?
2. Giriş ücret tarifesi hangi duyuruya dayanıyor ve güncel mi?
3. Ödünç ve restorasyon süreçlerinde kullanılan resmî formlar nelerdir?
4. Bakanlığın zorunlu kıldığı bir envanter sistemi (ör. MBS) var mı, bu program onunla nasıl bütünleşecek?
5. Çocuk ücretsiz giriş yaş sınırı ve yabancı ziyaretçiler için Müze Kart koşulları nedir? `[Eklendi]`
6. Müzeler İç Hizmetler Yönetmeliği hâlen yürürlükte mi, yerine geçen metin var mı? `[Eklendi]`

## 10. Bu kontrolde doğrulanmayan atıflar `[Eklendi]`

6698, 6331, 5846, 4982, 5070, Binaların Yangından Korunması Hakkında Yönetmelik, 657/4857 ayrımı, 5018'e göre harcama yetkilisi, gelirlerin yatırılma usulü ve Bölge Kurulu izinleri bu kontrolde aranmamıştır; yayımlamadan önce ayrıca teyit edilmelidir. Bu belge hukuki görüş değildir.
