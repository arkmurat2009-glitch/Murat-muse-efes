"""Bilet tarifesi (tarihli fiyat tablosu) ve bilet iadesi.

Mevzuat notu (kontrol tarihi 2026-11-07, web aramasıyla; resmî metinle teyit edilmeli):
- Müze giriş ücretleri Kültür ve Turizm Bakanlığı'nın giriş usul ve esasları yönergesine ekli listede yer alır
  (2252 sayılı Döner Sermaye Kanunu çerçevesi). Fiyatlar sık değişir ve kaynaklar çelişkilidir; bu yüzden
  fiyat kodda sabit değil, `tarifeler` tablosundadır ve her kayıt için kaynak (yönerge/duyuru) yazılır.
- Ücretsiz giriş kategorileri (ör. 18 yaş ve altı, 65 yaş ve üstü T.C. vatandaşları) yönergeye göredir; güncel
  yaş sınırları ve belge şartları teyit edilmelidir.
- Bilet iadesinin usulüne dair bir hüküm DOĞRULANAMADI. Program yalnızca iadeyi gerekçesiyle kaydeder;
  tahsilat/iade işlemi kurumun Döner Sermaye ve muhasebe usullerine göre ayrıca yürütülmelidir.
Kullanıcı alanı personel adıdır (KVKK 6698); ziyaretçi verisi tutulmaz.
"""
import sys
from datetime import date, datetime

from . import hareketler

BILET_TURLERI = ("yetiskin", "ogrenci", "cocuk", "muze_kart")

SEMA = """
CREATE TABLE IF NOT EXISTS tarifeler(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tur TEXT NOT NULL,
  fiyat REAL NOT NULL CHECK(fiyat >= 0),
  gecerli_baslangic TEXT NOT NULL,
  kaynak TEXT NOT NULL,
  kullanici TEXT NOT NULL,
  kayit_zamani TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS tarifeler_tur ON tarifeler(tur, gecerli_baslangic, id);
CREATE TABLE IF NOT EXISTS bilet_iadeleri(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tarih TEXT NOT NULL,
  satis_tarihi TEXT NOT NULL,
  tur TEXT NOT NULL,
  adet INTEGER NOT NULL CHECK(adet >= 1),
  tutar REAL NOT NULL CHECK(tutar >= 0),
  neden TEXT NOT NULL,
  kullanici TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS bilet_iadeleri_satis ON bilet_iadeleri(satis_tarihi, tur);
CREATE TRIGGER IF NOT EXISTS tarifeler_degismez BEFORE UPDATE ON tarifeler
BEGIN SELECT RAISE(ABORT, 'tarife kayıtları değiştirilemez; yeni tarih ile yeni kayıt ekleyin'); END;
CREATE TRIGGER IF NOT EXISTS tarifeler_silme_yasak BEFORE DELETE ON tarifeler
BEGIN SELECT RAISE(ABORT, 'tarife kayıtları silinemez'); END;
CREATE TRIGGER IF NOT EXISTS tarifeler_tur_kontrol BEFORE INSERT ON tarifeler
WHEN NEW.tur NOT IN ('yetiskin','ogrenci','cocuk','muze_kart') OR TRIM(NEW.kaynak)=''
BEGIN SELECT RAISE(ABORT, 'tarifeler: geçersiz tür veya boş kaynak'); END;
CREATE TRIGGER IF NOT EXISTS bilet_iadeleri_degismez BEFORE UPDATE ON bilet_iadeleri
BEGIN SELECT RAISE(ABORT, 'iade kayıtları değiştirilemez'); END;
CREATE TRIGGER IF NOT EXISTS bilet_iadeleri_silme_yasak BEFORE DELETE ON bilet_iadeleri
BEGIN SELECT RAISE(ABORT, 'iade kayıtları silinemez'); END;
CREATE TRIGGER IF NOT EXISTS bilet_iadeleri_kontrol BEFORE INSERT ON bilet_iadeleri
WHEN NEW.tur NOT IN ('yetiskin','ogrenci','cocuk','muze_kart') OR TRIM(NEW.neden)=''
BEGIN SELECT RAISE(ABORT, 'bilet_iadeleri: geçersiz tür veya boş gerekçe'); END;
"""


class TarifeHatasi(Exception):
    pass


def sema(con):
    con.executescript(SEMA)


def _tarih(s, alan):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date().isoformat()
    except (TypeError, ValueError):
        raise TarifeHatasi(f"{alan}: tarih YYYY-AA-GG biçiminde olmalı.")


def fiyat(con, tur, gun=None, varsayilan=None):
    """Tür için `gun` tarihinde geçerli en son tarife fiyatı; kayıt yoksa `varsayilan` (eski sabit fiyat)."""
    g = _tarih(gun or date.today().isoformat(), "tarih")
    r = con.execute("SELECT fiyat FROM tarifeler WHERE tur=? AND gecerli_baslangic<=? "
                    "ORDER BY gecerli_baslangic DESC, id DESC LIMIT 1", (tur, g)).fetchone()
    return r["fiyat"] if r else varsayilan


def tarife_ayarla(con, tur, tutar, baslangic, kaynak, kullanici):
    if tur not in BILET_TURLERI:
        raise TarifeHatasi(f"Geçersiz tür. Seçenekler: {', '.join(BILET_TURLERI)}")
    if tutar < 0:
        raise TarifeHatasi("Fiyat negatif olamaz.")
    if not (kaynak or "").strip():
        raise TarifeHatasi("Kaynak (yönerge/duyuru/karar) zorunludur.")
    b = _tarih(baslangic, "baslangic")
    con.execute("INSERT INTO tarifeler(tur,fiyat,gecerli_baslangic,kaynak,kullanici,kayit_zamani) "
                "VALUES(?,?,?,?,?,?)",
                (tur, tutar, b, kaynak, kullanici, datetime.now().isoformat(timespec="seconds")))


def iade(con, tur, adet, neden, kullanici, satis_tarihi=None, tarih=None):
    """Belirli bir günün satışlarından iade; iade edilebilir adet ve tutar o günün satışlarından hesaplanır.
    Dönen değer: iade tutarı. Çağıran işlemi (transaction) yönetir."""
    if tur not in BILET_TURLERI:
        raise TarifeHatasi(f"Geçersiz tür. Seçenekler: {', '.join(BILET_TURLERI)}")
    if adet < 1:
        raise TarifeHatasi("Adet en az 1 olmalı.")
    if not (neden or "").strip():
        raise TarifeHatasi("İade gerekçesi (--neden) zorunludur.")
    if not con.in_transaction:
        con.execute("BEGIN IMMEDIATE")  # iade edilebilir adet kontrolü ile yazma arasında yarış olmasın
    sg = _tarih(satis_tarihi or date.today().isoformat(), "satis_tarihi")
    ig = _tarih(tarih or date.today().isoformat(), "tarih")
    if ig < sg:
        raise TarifeHatasi("İade tarihi satış tarihinden önce olamaz.")
    s = con.execute("SELECT COALESCE(SUM(adet),0) n, COALESCE(SUM(tutar),0) t FROM biletler "
                    "WHERE tarih=? AND tur=?", (sg, tur)).fetchone()
    onceki = con.execute("SELECT COALESCE(SUM(adet),0) FROM bilet_iadeleri WHERE satis_tarihi=? AND tur=?",
                         (sg, tur)).fetchone()[0]
    kalan = s["n"] - onceki
    if s["n"] == 0:
        raise TarifeHatasi(f"{sg} tarihinde '{tur}' satışı yok.")
    if adet > kalan:
        raise TarifeHatasi(f"İade edilebilir adet aşıldı (iade edilebilir: {kalan}).")
    # Gün içinde tarife değiştiyse ortalama birim fiyat kullanılır.
    tutar = round(s["t"] / s["n"] * adet, 2)
    con.execute("INSERT INTO bilet_iadeleri(tarih,satis_tarihi,tur,adet,tutar,neden,kullanici) VALUES(?,?,?,?,?,?,?)",
                (ig, sg, tur, adet, tutar, neden, kullanici))
    return tutar


def iade_ozeti(con, gun):
    """`gun` tarihinde yapılan iadelerin (adet, tutar) toplamı."""
    r = con.execute("SELECT COALESCE(SUM(adet),0) n, COALESCE(SUM(tutar),0) t FROM bilet_iadeleri WHERE tarih=?",
                    (gun,)).fetchone()
    return r["n"], r["t"]


# ---- komut satırı ----

def _tarife_ayarla_cli(a):
    from muze import baglan
    with baglan() as con:
        try:
            tarife_ayarla(con, a.tur, a.fiyat, a.baslangic or date.today().isoformat(), a.kaynak,
                          hareketler.kullanici_adi(a))
        except TarifeHatasi as h:
            sys.exit(f"Hata: {h}")
    print("Tarife kaydedildi.")


def _tarife_listele_cli(a):
    from muze import baglan
    con = baglan()
    try:
        for r in con.execute("SELECT * FROM tarifeler ORDER BY tur, gecerli_baslangic, id"):
            print(f"{r['tur']:<10} {r['fiyat']:>9.2f} TL  {r['gecerli_baslangic']}  ({r['kaynak']}; {r['kullanici']})")
    finally:
        con.close()


def _iade_cli(a):
    from muze import baglan
    with baglan() as con:
        try:
            t = iade(con, a.tur, a.adet, a.neden, hareketler.kullanici_adi(a), a.satis_tarihi)
        except TarifeHatasi as h:
            sys.exit(f"Hata: {h}")
    print(f"{a.adet} x {a.tur} bileti iade kaydedildi. İade tutarı: {t:.2f} TL")


def komutlar(sp):
    x = sp.add_parser("tarife-ayarla", help="tarihli bilet fiyatı ekle (kaynak zorunlu)")
    x.add_argument("tur"); x.add_argument("fiyat", type=float)
    x.add_argument("--baslangic", help="geçerlilik başlangıcı YYYY-AA-GG (varsayılan: bugün)")
    x.add_argument("--kaynak", required=True, help="dayanak: yönerge/duyuru/karar")
    x.add_argument("--kullanici"); x.set_defaults(f=_tarife_ayarla_cli)
    x = sp.add_parser("tarife-listele", help="tarife geçmişi"); x.set_defaults(f=_tarife_listele_cli)
    x = sp.add_parser("bilet-iade", help="satılan bilet iadesi (gerekçeli kayıt)")
    x.add_argument("tur"); x.add_argument("adet", type=int); x.add_argument("--neden", required=True)
    x.add_argument("--satis-tarihi", help="satışın yapıldığı gün YYYY-AA-GG (varsayılan: bugün)")
    x.add_argument("--kullanici"); x.set_defaults(f=_iade_cli)
