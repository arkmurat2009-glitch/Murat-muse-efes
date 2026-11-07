---
name: ui-ux-pro-max
description: Profesyonel UI/UX tasarım ve arayüz geliştirme rehberi. Arayüz, sayfa, bileşen, form, tasarım sistemi veya kullanılabilirlik/erişilebilirlik incelemesi istendiğinde kullan. Türkiye mevzuatına (KVKK, 5378, 6502, 6563 ve dijital erişilebilirlik genelgesi) uyumu kontrol eder.
---

# UI/UX Pro Max

Arayüz tasarlarken, kodlarken veya incelerken bu rehberi uygula. Önce hedef kullanıcıyı, ana görevi ve platformu (web/mobil/masaüstü/kiosk) netleştir; belirsizse varsayımı açıkça belirt.

## 1. Çalışma akışı

1. **Bağlam:** Kullanıcı kim, ne yapmaya çalışıyor, hangi cihaz/ağ koşulunda? Mevcut kodun stilini ve bileşenlerini önce oku, ona uy.
2. **Bilgi mimarisi:** Ekranları ve akışları listele; ana görevi en az adımda tamamlat.
3. **Tasarım belirteçleri (tokens):** Renk, tipografi, boşluk, gölge, yarıçapı tek yerde tanımla; sabit değerleri koda dağıtma.
4. **Uygulama:** Boş, yükleniyor, hata, başarılı ve kısmi veri durumlarını her bileşen için tasarla.
5. **Doğrulama:** Aşağıdaki kontrol listesi + mevzuat bölümü. Mümkünse tarayıcıda 360 px, 768 px, 1280 px genişliklerde ve açık/koyu temada dene.

## 2. Görsel hiyerarşi ve düzen

- Sayfada tek bir birincil eylem olsun; ikincil eylemler görsel olarak geri planda kalsın.
- 4/8 px tabanlı boşluk ölçeği kullan; yakın öğeler birbirine yakın, ilgisizler uzak (yakınlık ilkesi).
- Satır uzunluğu 45–75 karakter; gövde metni en az 16 px, satır yüksekliği 1.4–1.6.
- En fazla 2 yazı tipi ailesi, 4–5 boyut kademesi. Başlık hiyerarşisi (h1→h2→h3) anlamsal olarak doğru olsun.
- Mobil öncelikli tasarla; yatay kaydırma olmasın, kenar boşluğu en az 16 px.
- Türkçe karakterleri (ı, İ, ğ, ş, ç, ö, ü) tam destekleyen yazı tipi seç; `text-transform: uppercase` kullanırken `lang="tr"` ayarla ki "i → İ" doğru dönüşsün.

## 3. Renk ve tema

- Renkleri anlamsal adlarla tanımla (`--color-bg`, `--color-text`, `--color-primary`, `--color-danger`).
- Açık ve koyu tema için ayrı değerler tanımla; `prefers-color-scheme` ve `prefers-reduced-motion` tercihlerine saygı göster.
- Anlamı yalnızca renkle iletme; ikon, metin veya desen ekle (renk körlüğü).
- Kontrast: normal metin ≥ 4.5:1, büyük metin (≥ 24 px veya ≥ 18.66 px kalın) ve arayüz bileşenleri ≥ 3:1.

## 4. Etkileşim ve geri bildirim

- Dokunma hedefi en az 44×44 px (en az 24×24 px WCAG 2.2 alt sınırı), hedefler arası boşluk yeterli.
- Her etkileşimli öğenin görünür `:focus-visible` durumu olsun; `outline: none` ile odağı yok etme.
- Tüm işlevler klavyeyle yapılabilsin; odak sırası görsel sırayla uyumlu, modallarda odak kapanana kadar içeride tutulsun ve kapanınca tetikleyiciye dönsün.
- 100 ms altı anında, 1 s üstü işlemler için ilerleme göstergesi / iskelet ekran kullan.
- Geri alınamayan eylemlerde onay iste, mümkünse "geri al" sun.
- Animasyon 150–300 ms, anlamlı olsun; `prefers-reduced-motion` altında kapat. Saniyede 3'ten fazla yanıp sönen içerik kullanma.

## 5. Formlar

- Her alanın görünür `<label>`'ı olsun; yer tutucu (placeholder) etiket yerine geçmez.
- Doğru `type`, `inputmode`, `autocomplete` kullan (örn. `tel`, `email`, `one-time-code`).
- Hatayı alanın yanında, ne olduğunu ve nasıl düzeltileceğini söyleyerek göster (`aria-describedby`, `aria-invalid`); hata özeti odağa alınsın.
- Gereksiz alan isteme (veri minimizasyonu, bkz. KVKK). Zorunlu/isteğe bağlı alanı açıkça belirt.
- Gönderimde çift tıklamayı engelle, girilen veriyi hata sonrası koru.
- Telefon, TC kimlik no, IBAN gibi alanlarda biçim ve doğrulama yardımı ver; TC kimlik no gibi veriyi yalnızca gerçekten gerekiyorsa iste.

## 6. Erişilebilirlik (WCAG 2.1 AA, hedef 2.2 AA)

- Anlamsal HTML önce (`button`, `nav`, `main`, `label`, `table`); ARIA yalnızca anlamsal öğe yetmediğinde.
- Tüm anlamlı görsellerde `alt`; süs görsellerde `alt=""`.
- Sayfada `lang="tr"` (farklı dildeki parçada `lang` özniteliği), anlamlı `<title>`, "içeriğe atla" bağlantısı.
- Metin %200 büyütüldüğünde ve 320 px genişlikte içerik kaybolmasın (reflow); sabit piksel yükseklikli kapsayıcılardan kaçın.
- Video/ses için altyazı ve metin alternatifi; otomatik oynayan sesi kapat.
- Durum mesajları `role="status"`/`aria-live` ile duyurulsun.
- Araç önerisi: axe, Lighthouse; ayrıca klavye ile ve ekran okuyucuyla (NVDA/VoiceOver) elle dene.

## 7. Performans ve dayanıklılık

- Görselleri doğru boyutta ve modern biçimde (WebP/AVIF) sun; `loading="lazy"`, `width`/`height` belirt (CLS).
- Hedef: LCP < 2.5 s, INP < 200 ms, CLS < 0.1.
- Yazı tipini yerel ya da kendi alan adından sun (bkz. KVKK: üçüncü taraf istekleri veri aktarımı sayılabilir); `font-display: swap`.
- Çevrimdışı/yavaş ağ ve hata durumlarında anlaşılır mesaj göster.

## 8. İçerik ve mikro metin

- Türkçe, sade ve eyleme yönelik yaz: "Kaydet", "Siparişi tamamla"; belirsiz "Tamam" / "Gönder" kaçın.
- Hata mesajı suçlamasın: "Geçersiz giriş" yerine "E-posta adresi @ işareti içermeli".
- Tarih, saat, para birimi ve sayıyı Türkiye biçiminde göster (`gg.aa.yyyy`, `1.234,56 ₺`); `Intl` API'sini `tr-TR` ile kullan.
- Boş durumlarda sonraki adımı öner.

## 9. Türkiye mevzuatı uyum kontrolü

Aşağıdakiler genel tasarım kontrol listesidir; hukuki görüş değildir. Her madde için durum etiketi vardır: **[Doğrulandı]** birden çok ikincil kaynakta teyit edildi, **[Kısmen]** özü teyit edildi ayrıntısı edilmedi, **[Doğrulanamadı]** resmî metne bakılmadan kesin kabul edilmemeli. Doğrulama 2026-10-25'te yapıldı; resmî siteler (mevzuat.gov.tr, kvkk.gov.tr, Resmî Gazete) erişilemediği için resmî metin okunmadı. Kapsamı belli projelerde güncel resmî metni ve hukuk müşavirini esas al.

**Kişisel veriler: 6698 sayılı KVKK ve ilgili düzenlemeler**
- Aydınlatma metni, veri toplanan her noktada (form, kayıt, çerez) erişilebilir ve anlaşılır olsun.
- Açık rıza: ayrı, ön seçimsiz, hizmetin şartı olarak dayatılmayan, geri çekilmesi kolay onay. "Siteyi kullanarak kabul etmiş sayılırsınız" ve genel "kabul ediyorum" ifadeleri açık rıza sayılmaz. [Kısmen: KVKK çerez rehberi özetlerine dayanır]
- Veri minimizasyonu: yalnızca amaç için gerekli alanları iste.
- Çerezler: Kurum'un Çerez Uygulamaları Hakkında Rehberi 2022'de yayımlandı, Temmuz 2025'te iyi/kötü uygulama örnekleriyle güncellendi. Analitik, reklam ve kişiselleştirme çerezleri için açık rıza gerekir, onaydan önce çalışmasın; oturum, sepet, güvenlik gibi kesinlikle gerekli çerezler kapsam dışıdır. "Kabul et", "Reddet" ve "Ayarlar" seçeneklerini ilk katmanda aynı renk, boyut ve düzeyde sun; reddi alt menüye gömme, soluk gösterme, ön işaretli kategori kullanma. [Kısmen: ikincil kaynaklar rehberin reddi kabul kadar kolay kıldığını aktarıyor; rehberin 2025 metnindeki tam ifade ve satıcı bloglarında anılan Kurul karar numaraları resmî siteden doğrulanamadı]
- Yurt dışı aktarım (yabancı CDN, analitik, harita, yazı tipi, sohbet botu): KVKK m.9, 7499 sayılı Kanun m.34 ile değişti (RG 12.03.2024, 32487; yürürlük 01.06.2024). Aktarım yönetmeliği RG 10.07.2024, 32598. Kurum'un Yurt Dışına Aktarım Rehberi 02.01.2025'te yayımlandı. Eski açık rızaya dayalı aktarımlar için geçiş 01.09.2024'te bitti. [Doğrulandı] Yeterlilik kararı listesinin güncel durumunu Kurum'dan kontrol et.
- İlgili kişi başvurusu: KVKK m.11 hakları sayar (öğrenme, düzeltme, silme, itiraz, zarar giderim vb.); m.13 başvurunun yazılı veya Kurul'un belirlediği yöntemlerle (Veri Sorumlusuna Başvuru Usul ve Esasları Hakkında Tebliğ; KEP dahil) veri sorumlusuna yapılmasını ve cevabın en geç 30 gün içinde verilmesini öngörür. Kolay bulunur bir başvuru kanalı ve form sağla. [Doğrulandı: ikincil kaynaklar]
- Özel nitelikli veriyi gereksizse toplama.

**Dijital erişilebilirlik**
- 5378 sayılı Engelliler Hakkında Kanun m.7: bilgilendirme hizmetleri ile bilgi ve iletişim teknolojilerinin engelliler için erişilebilir olması ilkesini koyar. [Doğrulandı] Bu madde web siteleri için ayrıntılı teknik standart veya yaptırım içermez.
- Web sitesi ve mobil uygulama erişilebilirliği için Cumhurbaşkanlığı'nın **2025/10 sayılı Genelgesi** (Haziran 2025) bildirilmektedir; kamu kurumları, belediyeler, üniversiteler ve bazı özel sektör kuruluşları (banka, e-ticaret vb.) anılmakta, süreler olarak kamu için bir yıl, e-ticaret için iki yıl aktarılmaktadır. Genelge doğrudan yaptırım öngörmemekte, denetim ve kamu kaynağı kullanımında ölçüt olabilmektedir. [Kısmen: yalnızca hukuk bürosu ve haber özetleri; kapsam, süre ve standart sürümü (WCAG 2.1 mi 2.2 mi) kaynaklarda çelişiyor, resmî metinden teyit et]
- Karar verilmemişse WCAG 2.2 AA'yı hedefle; 2.1 AA'yı da karşılar.

**Tüketici ve e-ticaret: 6502 sayılı Kanun, Mesafeli Sözleşmeler Yönetmeliği, 6563 sayılı Kanun**
- Mesafeli sözleşmelerde ön bilgilendirme ve 14 günlük gerekçesiz cayma hakkı: 6502 m.48 ve Mesafeli Sözleşmeler Yönetmeliği. [Doğrulandı] İstisnalar yönetmelikte sayılıdır, ürününe göre kontrol et.
- Yönetmelik m.8/1: satıcı/sağlayıcı (2022 değişikliğiyle aracı hizmet sağlayıcı da, RG 23.08.2022) siparişi onaylamadan hemen önce siparişin ödeme yükümlülüğü doğurduğunu açık ve anlaşılır biçimde bildirmelidir; aksi hâlde tüketici siparişle bağlı olmaz. [Doğrulandı] Düğme metni için resmî bir kalıp **bulunmadı**; "Siparişi onayla ve öde" gibi ifade ticari rehberlerin önerisidir. Bilgilendirmenin fiyat (vergiler dahil), teslimat bedeli, ödeme ve cayma koşullarını ödeme öncesinde ayrıca ve belirgin göstermesi gerekir. Yönetmelik geçici m.1'deki 01.01.2025 tarihleri RG 10.08.2024 (32628) ile 01.01.2026'ya ertelendi; RG 24.05.2025 (32909) değişikliği 01.01.2026'da yürürlüğe girdi ve m.5/1 (g) ile (k) bentlerini (iade taşıyıcısı bilgisi, tüketici uyuşmazlık yolları) yeniden yazdı. Platformda kurulan sözleşmelerde iade taşıyıcısı bilgisi eksik veya tüketici bölgesinde şubesi yoksa masraf aracı hizmet sağlayıcıya aittir. Telefon, akıllı saat ve bilgisayarın cayma istisnasından çıkarıldığı bildirildi; ön bilgilendirme formunu güncel haliyle kullan. [Kısmen: bu ayrıntılar haber ve hukuk sitesi özetlerine dayanır, resmî metinle teyit et]
- Önceden işaretli ek ürün/hizmet ve gizli ücret ("karanlık desenler") kullanma. Türk hukukunda karanlık desen ayrı bir kurum olarak düzenlenmemiştir; değerlendirme 6502 sayılı Kanun, Reklam ve Haksız Ticari Uygulamalar Yönetmeliği (2026'da değiştirildiği bildirildi), Reklam Kurulu yetkisi, mesafeli sözleşme ön bilgilendirmesi ve KVKK aydınlatma/açık rıza kuralları üzerinden yapılır. Ayrı bir "karanlık desen yasağı" maddesi yoktur. [Kısmen]
- Satıcı kimliği: Elektronik Ticaret Aracı Hizmet Sağlayıcı ve Elektronik Ticaret Hizmet Sağlayıcılar Hakkında Yönetmelik (6563 sayılı Kanuna dayanır; 29.12.2022 RG 32058 ile değişti) uyarınca tacir hizmet sağlayıcı kendi ortamında ticaret unvanı, MERSİS numarası, merkez adresi ve tebligata elverişli KEP adresini bulundurur; esnaf için vergi kimlik numarası istenir; pazar yerinde satış yapan satıcı için de unvan/işletme adı/marka, KEP ve MERSİS (tacir) veya vergi no (esnaf) gösterilir. Tam alan listesini güncel yönetmelikten kontrol et. [Kısmen]
- Ticari elektronik ileti (e-posta, SMS, arama) için önceden onay gerekir; onay İYS üzerinden veya yazılı/elektronik alınır ve alıcı gerekçesiz ret hakkına sahiptir; ret, bildirimin yapıldığı kanalın onayını geçersiz kılar. 6563 m.6 önceden onayı, m.7 iletinin içeriğinin alınan onaya uygun olmasını ve hizmet sağlayıcıyı tanıtan, erişilebilir iletişim bilgisini düzenler; esnaf ve tacirlere ileti için önceden onay şartı aranmaz. Onaysız veya onaya aykırı ileti için m.12 idari para cezası 2026'da 2.859–14.309 TL'dir (RG 25.12.2025, 33118; her yıl güncellenir). Ret hakkının kanundaki madde numarası **doğrulanamadı**; atıf için Ticari İletişim Yönetmeliği ve İYS tebliğini esas al. [Doğrulandı]

**Dil**
- Tüketiciye yönelik bilgilendirmeyi Türkçe sun. [Doğrulanamadı: dayanak madde bu turda bulunamadı]

**Üçüncü taraf bileşenler:** Kullanıcı verisi gönderen bileşenleri aydınlatma metnine ve yurt dışı aktarım değerlendirmesine ekle.

## 10. Teslim öncesi kontrol listesi

- [ ] Tek birincil eylem, net hiyerarşi, tutarlı boşluk ve tipografi
- [ ] Tüm durumlar: boş / yükleniyor / hata / başarı
- [ ] Kontrast, odak halkası, klavye erişimi, `lang="tr"`
- [ ] 320–1280 px duyarlı, yatay kaydırma yok, %200 yakınlaştırmada kullanılabilir
- [ ] Açık/koyu tema ve `prefers-reduced-motion`
- [ ] Formlarda etiket, hata mesajı, `autocomplete`
- [ ] Aydınlatma metni, çerez onayı, ticari ileti onayı, cayma/ön bilgilendirme (kapsam dahilindeyse)
- [ ] Üçüncü taraf istekleri ve yurt dışı aktarımları gözden geçirildi
- [ ] Yapılan varsayımlar ve açık mevzuat riskleri kullanıcıya raporlandı

## 11. Çıktı biçimi

Tasarım/inceleme sonunda şunları kısaca ver: (1) ne yapıldı, (2) bulunan sorunlar önem sırasıyla, (3) mevzuat açısından dikkat edilecekler ve hukuki doğrulama gerektiren noktalar, (4) sonraki adımlar.
