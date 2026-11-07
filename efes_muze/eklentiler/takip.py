"""Restorasyon ve ödünç takibi: tarihli, sorumlu/kurum bilgili kayıtlar, geciken listesi.

Eserin durumu `gecis.degistir` ile (hareketler tablosuna yazarak) aynı işlemde değiştirilir.

Mevzuat notu (kontrol tarihi 2026-11-07, web aramasıyla; resmî metinle teyit edilmeli):
- Yurt dışına geçici sergi: 2863 s. Kanun md. 32 ve "Korunması Gerekli Taşınır Kültür ve Tabiat
  Varlıklarının Yurt Dışına Çıkarılması ve Yurda Sokulması Hakkında Yönetmelik". İzin Cumhurbaşkanı
  kararıyla verilir; sigorta ve teminat gerekir; süre tek ülke için 1 yılı, birden çok ülke için 2 yılı
  geçemez. Yönetmelik 2020'de değiştirilmiştir; güncel metin doğrulanmalıdır.
- Yurt içi ödünç ve restorasyon izin/usul kuralları (Müzeler İç Hizmetler Yönetmeliği vb.) DOĞRULANAMADI.
  Bu yüzden program yalnızca kayıt tutar; izin numarası serbest metindir ve zorunlu tutulmaz.
Kullanıcı alanı personel adıdır (KVKK 6698); ziyaretçi verisi tutulmaz.
"""
import sys
from datetime import date, datetime

from . import gecis, hareketler

# Yurt dışı süre sınırları (gün): tek ülke 1 yıl, birden çok ülke 2 yıl (2863 md. 32 yönetmeliği; teyit edilecek).
YURT_DISI_SINIR = {1: 365, 2: 730}

SEMA = """
CREATE TABLE IF NOT EXISTS restorasyonlar(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  eser_id INTEGER NOT NULL REFERENCES eserler(id),
  baslangic TEXT NOT NULL,
  planlanan_bitis TEXT NOT NULL,
  atolye TEXT NOT NULL,
  sorumlu TEXT NOT NULL,
  izin_no TEXT,
  kondisyon_notu TEXT,
  bitis TEXT,
  sonuc_notu TEXT
);
CREATE INDEX IF NOT EXISTS restorasyonlar_eser ON restorasyonlar(eser_id, id);
CREATE TABLE IF NOT EXISTS oduncler(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  eser_id INTEGER NOT NULL REFERENCES eserler(id),
  kurum TEXT NOT NULL,
  cikis TEXT NOT NULL,
  planlanan_donus TEXT NOT NULL,
  gercek_donus TEXT,
  sigorta_degeri REAL,
  izin_no TEXT,
  yurt_disi INTEGER NOT NULL DEFAULT 0,
  ulke_sayisi INTEGER,
  kondisyon_notu TEXT
);
CREATE INDEX IF NOT EXISTS oduncler_eser ON oduncler(eser_id, id);
CREATE TRIGGER IF NOT EXISTS restorasyonlar_silme_yasak BEFORE DELETE ON restorasyonlar
BEGIN SELECT RAISE(ABORT, 'restorasyon kayıtları silinemez'); END;
CREATE TRIGGER IF NOT EXISTS restorasyonlar_kapali_degismez BEFORE UPDATE ON restorasyonlar
WHEN OLD.bitis IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'kapanmış restorasyon kaydı değiştirilemez'); END;
CREATE TRIGGER IF NOT EXISTS oduncler_silme_yasak BEFORE DELETE ON oduncler
BEGIN SELECT RAISE(ABORT, 'ödünç kayıtları silinemez'); END;
CREATE TRIGGER IF NOT EXISTS oduncler_kapali_degismez BEFORE UPDATE ON oduncler
WHEN OLD.gercek_donus IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'kapanmış ödünç kaydı değiştirilemez'); END;
"""


class TakipHatasi(Exception):
    pass


def sema(con):
    con.executescript(SEMA)


def tarih(s, alan):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date().isoformat()
    except (TypeError, ValueError):
        raise TakipHatasi(f"{alan}: tarih YYYY-AA-GG biçiminde olmalı.")


def acik_kayit(con, eser_id):
    """Eserin açık (kapanmamış) restorasyon veya ödünç kaydı varsa ('restorasyon'|'odunc', satır)."""
    r = con.execute("SELECT * FROM restorasyonlar WHERE eser_id=? AND bitis IS NULL", (eser_id,)).fetchone()
    if r:
        return "restorasyon", r
    o = con.execute("SELECT * FROM oduncler WHERE eser_id=? AND gercek_donus IS NULL", (eser_id,)).fetchone()
    return ("odunc", o) if o else (None, None)


def _eser(con, no):
    e = con.execute("SELECT * FROM eserler WHERE envanter_no=?", (no,)).fetchone()
    if not e:
        raise TakipHatasi("Eser bulunamadı.")
    return e


def _baslat(con):
    if not con.in_transaction:
        con.execute("BEGIN IMMEDIATE")


def restorasyon_baslat(con, no, atolye, sorumlu, planlanan_bitis, izin_no=None, kondisyon_notu=None,
                       kullanici=None, baslangic=None):
    _baslat(con)
    bas = tarih(baslangic or date.today().isoformat(), "baslangic")
    bit = tarih(planlanan_bitis, "planlanan_bitis")
    if bit < bas:
        raise TakipHatasi("Planlanan bitiş, başlangıçtan önce olamaz.")
    if not atolye.strip() or not sorumlu.strip():
        raise TakipHatasi("Atölye ve sorumlu zorunludur.")
    e = _eser(con, no)
    if acik_kayit(con, e["id"])[0]:
        raise TakipHatasi("Eserin açık bir restorasyon/ödünç kaydı var.")
    try:
        gecis.degistir(con, no, "restorasyonda", kullanici=kullanici,
                       aciklama=f"restorasyon: {atolye} (sorumlu: {sorumlu})")
    except gecis.GecisHatasi as h:
        raise TakipHatasi(str(h))
    con.execute("INSERT INTO restorasyonlar(eser_id,baslangic,planlanan_bitis,atolye,sorumlu,izin_no,kondisyon_notu)"
                " VALUES(?,?,?,?,?,?,?)", (e["id"], bas, bit, atolye, sorumlu, izin_no, kondisyon_notu))


def restorasyon_bitir(con, no, sonuc_notu=None, kullanici=None, bitis=None):
    _baslat(con)
    e = _eser(con, no)
    tur, r = acik_kayit(con, e["id"])
    if tur != "restorasyon":
        raise TakipHatasi("Eserin açık restorasyon kaydı yok.")
    bit = tarih(bitis or date.today().isoformat(), "bitis")
    if bit < r["baslangic"]:
        raise TakipHatasi("Bitiş tarihi başlangıçtan önce olamaz.")
    try:
        gecis.degistir(con, no, "depoda", kullanici=kullanici, aciklama="restorasyon tamamlandı")
    except gecis.GecisHatasi as h:
        raise TakipHatasi(str(h))
    con.execute("UPDATE restorasyonlar SET bitis=?, sonuc_notu=? WHERE id=?", (bit, sonuc_notu, r["id"]))


def odunc_ver(con, no, kurum, planlanan_donus, sigorta_degeri=None, izin_no=None, yurt_disi=False,
              ulke_sayisi=None, kondisyon_notu=None, kullanici=None, cikis=None):
    _baslat(con)
    cik = tarih(cikis or date.today().isoformat(), "cikis")
    don = tarih(planlanan_donus, "planlanan_donus")
    if don < cik:
        raise TakipHatasi("Planlanan dönüş, çıkıştan önce olamaz.")
    if not kurum.strip():
        raise TakipHatasi("Kurum zorunludur.")
    if sigorta_degeri is not None and sigorta_degeri < 0:
        raise TakipHatasi("Sigorta değeri negatif olamaz.")
    if yurt_disi:
        # 2863 md. 32: izin (Cumhurbaşkanı kararı), sigorta/teminat ve süre sınırı (teyit edilecek).
        if not izin_no:
            raise TakipHatasi("Yurt dışı gönderim için izin/karar numarası (--izin-no) gerekir (2863 md. 32).")
        if not sigorta_degeri:
            raise TakipHatasi("Yurt dışı gönderim için sigorta değeri (--sigorta) gerekir.")
        ulke_sayisi = ulke_sayisi or 1
        sinir = YURT_DISI_SINIR[1 if ulke_sayisi == 1 else 2]
        gun = (date.fromisoformat(don) - date.fromisoformat(cik)).days
        if gun > sinir:
            raise TakipHatasi(f"Yurt dışı süre sınırı aşılıyor: {gun} gün > {sinir} gün "
                              f"({'tek ülke 1 yıl' if sinir == 365 else 'birden çok ülke 2 yıl'}; teyit edilecek).")
    else:
        ulke_sayisi = None
    e = _eser(con, no)
    if acik_kayit(con, e["id"])[0]:
        raise TakipHatasi("Eserin açık bir restorasyon/ödünç kaydı var.")
    try:
        gecis.degistir(con, no, "odunc", kullanici=kullanici,
                       aciklama=f"ödünç: {kurum}{' (yurt dışı)' if yurt_disi else ''}")
    except gecis.GecisHatasi as h:
        raise TakipHatasi(str(h))
    con.execute("INSERT INTO oduncler(eser_id,kurum,cikis,planlanan_donus,sigorta_degeri,izin_no,yurt_disi,"
                "ulke_sayisi,kondisyon_notu) VALUES(?,?,?,?,?,?,?,?,?)",
                (e["id"], kurum, cik, don, sigorta_degeri, izin_no, int(bool(yurt_disi)), ulke_sayisi,
                 kondisyon_notu))


def odunc_iade(con, no, kondisyon_notu=None, kullanici=None, donus=None):
    _baslat(con)
    e = _eser(con, no)
    tur, o = acik_kayit(con, e["id"])
    if tur != "odunc":
        raise TakipHatasi("Eserin açık ödünç kaydı yok.")
    don = tarih(donus or date.today().isoformat(), "donus")
    if don < o["cikis"]:
        raise TakipHatasi("Dönüş tarihi çıkıştan önce olamaz.")
    try:
        gecis.degistir(con, no, "depoda", kullanici=kullanici, aciklama="ödünç iade alındı")
    except gecis.GecisHatasi as h:
        raise TakipHatasi(str(h))
    # Dönüş kondisyon notu, çıkıştaki notun üzerine yazılmaz; ekleme yapılır.
    not_ = o["kondisyon_notu"]
    if kondisyon_notu:
        not_ = f"{not_ + ' | ' if not_ else ''}iade: {kondisyon_notu}"
    con.execute("UPDATE oduncler SET gercek_donus=?, kondisyon_notu=? WHERE id=?", (don, not_, o["id"]))


def gecikenler(con, bugun=None):
    """Planlanan tarihi geçmiş açık kayıtlar: [(tur, envanter_no, ad, kurum/atölye, plan, gecikme_gun)]."""
    b = tarih(bugun or date.today().isoformat(), "tarih")
    sonuc = []
    for r in con.execute("SELECT e.envanter_no, e.ad, r.atolye, r.planlanan_bitis p FROM restorasyonlar r "
                         "JOIN eserler e ON e.id=r.eser_id WHERE r.bitis IS NULL AND r.planlanan_bitis<? "
                         "ORDER BY r.planlanan_bitis", (b,)):
        sonuc.append(("restorasyon", r["envanter_no"], r["ad"], r["atolye"], r["p"], _gun(b, r["p"])))
    for r in con.execute("SELECT e.envanter_no, e.ad, o.kurum, o.planlanan_donus p FROM oduncler o "
                         "JOIN eserler e ON e.id=o.eser_id WHERE o.gercek_donus IS NULL AND o.planlanan_donus<? "
                         "ORDER BY o.planlanan_donus", (b,)):
        sonuc.append(("odunc", r["envanter_no"], r["ad"], r["kurum"], r["p"], _gun(b, r["p"])))
    return sonuc


def _gun(b, p):
    return (date.fromisoformat(b) - date.fromisoformat(p)).days


# ---- komut satırı ----

def _calistir(fn, *args, **kw):
    from muze import baglan
    with baglan() as con:
        try:
            fn(con, *args, **kw)
        except TakipHatasi as h:
            sys.exit(f"Hata: {h}")


def _k(a):
    return getattr(a, "kullanici", None) or hareketler.kullanici_adi(a)


def komutlar(sp):
    x = sp.add_parser("restorasyon-baslat", help="eseri restorasyona gönder (tarihli kayıt)")
    x.add_argument("no"); x.add_argument("--atolye", required=True); x.add_argument("--sorumlu", required=True)
    x.add_argument("--bitis", required=True, help="planlanan bitiş YYYY-AA-GG")
    x.add_argument("--izin-no"); x.add_argument("--kondisyon"); x.add_argument("--kullanici")
    x.add_argument("--baslangic", help="varsayılan: bugün (geriye dönük kayıt için YYYY-AA-GG)")
    x.set_defaults(f=lambda a: (_calistir(restorasyon_baslat, a.no, a.atolye, a.sorumlu, a.bitis, a.izin_no,
                                          a.kondisyon, _k(a), a.baslangic), print("Restorasyon başlatıldı.")))

    x = sp.add_parser("restorasyon-bitir", help="restorasyonu tamamla, eser depoya döner")
    x.add_argument("no"); x.add_argument("--not", dest="sonuc"); x.add_argument("--kullanici")
    x.set_defaults(f=lambda a: (_calistir(restorasyon_bitir, a.no, a.sonuc, _k(a)), print("Restorasyon bitti.")))

    x = sp.add_parser("odunc-ver", help="eseri ödünç ver (tarihli kayıt)")
    x.add_argument("no"); x.add_argument("kurum")
    x.add_argument("--donus", required=True, help="planlanan dönüş YYYY-AA-GG")
    x.add_argument("--sigorta", type=float, help="sigorta değeri (TL)"); x.add_argument("--izin-no")
    x.add_argument("--yurt-disi", action="store_true"); x.add_argument("--ulke-sayisi", type=int)
    x.add_argument("--kondisyon"); x.add_argument("--kullanici")
    x.add_argument("--cikis", help="varsayılan: bugün (geriye dönük kayıt için YYYY-AA-GG)")
    x.set_defaults(f=lambda a: (_calistir(odunc_ver, a.no, a.kurum, a.donus, a.sigorta, a.izin_no, a.yurt_disi,
                                          a.ulke_sayisi, a.kondisyon, _k(a), a.cikis), print("Ödünç kaydedildi.")))

    x = sp.add_parser("odunc-iade", help="ödünç eseri iade al")
    x.add_argument("no"); x.add_argument("--kondisyon"); x.add_argument("--kullanici")
    x.set_defaults(f=lambda a: (_calistir(odunc_iade, a.no, a.kondisyon, _k(a)), print("İade alındı.")))

    x = sp.add_parser("geciken-listesi", help="planlanan tarihi geçen restorasyon/ödünç kayıtları")
    x.add_argument("--tarih")
    x.set_defaults(f=_geciken_yaz)


def _geciken_yaz(a):
    from muze import baglan
    con = baglan()
    try:
        liste = gecikenler(con, a.tarih)
    except TakipHatasi as h:
        sys.exit(f"Hata: {h}")
    finally:
        con.close()
    if not liste:
        print("Geciken kayıt yok.")
    for tur, no, ad, yer, plan, gun in liste:
        print(f"{tur:<12} {no:<10} {ad:<28} {yer:<20} plan: {plan}  {gun} gün gecikti")
