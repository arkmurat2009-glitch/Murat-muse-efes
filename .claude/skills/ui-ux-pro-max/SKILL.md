---
name: ui-ux-pro-max
description: Profesyonel UI/UX tasarım ve arayüz geliştirme rehberi. Arayüz, sayfa, bileşen, form, tasarım sistemi veya kullanılabilirlik/erişilebilirlik incelemesi istendiğinde kullan. Türkiye mevzuatına (KVKK, 5378, 6502, 6563) uyumu kontrol eder.
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

Aşağıdakiler genel tasarım kontrol listesidir; hukuki görüş değildir. Kapsamı belli olan projelerde güncel metni ve yetkili hukuk müşavirini esas al, mevzuatın değişmiş olabileceğini unutma.

**Kişisel veriler: 6698 sayılı KVKK ve ilgili yönetmelikler**
- Aydınlatma metni, veri toplanan her noktada (form, kayıt, çerez) erişilebilir ve anlaşılır olsun.
- Açık rıza: ayrı, işaretlenmemiş (ön seçimsiz) onay kutusu; hizmetin şartı olarak dayatılmasın, geri çekilmesi kolay olsun.
- Veri minimizasyonu: yalnızca amaç için gerekli alanları iste.
- Çerezler: zorunlu olmayan çerezler için kullanıcı tercihine göre (reddet/kabul et eşit görünürlükte) onay al; Kişisel Verileri Koruma Kurumu'nun çerez rehberi ve ilgili kurul kararlarına bak. Analitik/reklam betikleri onaydan önce çalışmasın.
- Yurt dışına aktarım (örn. yabancı CDN, analitik, harita, yazı tipi servisleri) için KVKK m.9 şartlarını kontrol et.
- İlgili kişi başvurusu (m.11) için kolay bulunur bir kanal sağla.
- Özel nitelikli veri (sağlık, biyometri vb.) arayüzde ayrıca korunsun ve gereksizse toplanmasın.

**Erişilebilirlik: 5378 sayılı Engelliler Hakkında Kanun ve ilgili düzenlemeler**
- Kamu kurumları ve kanunda sayılan sunucular için dijital erişilebilirlik yükümlülüğü vardır; ölçüt olarak WCAG 2.1 AA (Avrupa'daki EN 301 549 ile uyumlu) alınmalıdır. Ücretsiz/özel projelerde de iyi uygulama olarak hedefle.

**Tüketici ve e-ticaret: 6502 sayılı Kanun, Mesafeli Sözleşmeler Yönetmeliği, 6563 sayılı Kanun**
- Satın alma akışında ön bilgilendirme (fiyat vergiler dahil, teslimat, cayma hakkı) sipariş öncesi görünsün.
- Ödeme düğmesi açık ödeme yükümlülüğünü belirtsin (örn. "Siparişi onayla ve öde").
- Önceden işaretli ek ürün/hizmet ve gizli ücret ("karanlık desenler") kullanma; sahte aciliyet/stok baskısı yapma.
- Cayma hakkı ve iletişim bilgileri kolay bulunur olsun; satıcı/hizmet sağlayıcı kimliği ve MERSİS/vergi bilgileri görünsün.
- Ticari elektronik ileti (e-posta, SMS, arama) için önceden onay gerekir (İYS); onay kutusu ön seçimsiz ve ayrı olsun, her iletide ret yolu bulunsun.

**Dil**
- Tüketiciye yönelik bilgilendirme ve sözleşme metinleri Türkçe sunulmalıdır; çok dilli arayüzde Türkçe sürümü eksik bırakma.

**Yapay zekâ/üçüncü taraf bileşenleri:** Kullanıcı verisi gönderen bileşenleri (sohbet botu, analitik, harita) KVKK ve aydınlatma metnine ekle.

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
