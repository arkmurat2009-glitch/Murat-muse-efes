"""Eser hareketleri: ekleme-yalnız denetim izi tablosu ve `eser-gecmis` komutu.

Not (KVKK 6698): `kullanici` alanı personel adı/kullanıcı kodudur. Ziyaretçi verisi tutulmaz.
Kurumun saklama süresi ve erişim politikası ayrıca belirlenmelidir.
"""
import getpass
import os
import sys
from datetime import datetime

SEMA = """
CREATE TABLE IF NOT EXISTS hareketler(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  eser_id INTEGER NOT NULL REFERENCES eserler(id),
  tarih TEXT NOT NULL,
  eski_durum TEXT,
  yeni_durum TEXT NOT NULL,
  eski_sergi_id INTEGER,
  yeni_sergi_id INTEGER,
  kullanici TEXT NOT NULL,
  aciklama TEXT
);
CREATE INDEX IF NOT EXISTS hareketler_eser ON hareketler(eser_id, id);
CREATE TRIGGER IF NOT EXISTS hareketler_guncelleme_yasak BEFORE UPDATE ON hareketler
BEGIN SELECT RAISE(ABORT, 'hareketler kayıtları değiştirilemez'); END;
CREATE TRIGGER IF NOT EXISTS hareketler_silme_yasak BEFORE DELETE ON hareketler
BEGIN SELECT RAISE(ABORT, 'hareketler kayıtları silinemez'); END;
"""


def sema(con):
    con.executescript(SEMA)


def kullanici_adi(a=None):
    k = getattr(a, "kullanici", None) or os.environ.get("EFES_KULLANICI")
    if not k:
        try:
            k = getpass.getuser()
        except Exception:
            k = os.environ.get("USER") or "bilinmiyor"
    return k


def kaydet(con, eser, yeni_durum, yeni_sergi_id, kullanici, aciklama=None):
    """`eser` güncellemeden ÖNCE okunmuş satırdır; çağıran aynı işlemde (transaction) olmalı."""
    con.execute(
        "INSERT INTO hareketler(eser_id,tarih,eski_durum,yeni_durum,eski_sergi_id,yeni_sergi_id,kullanici,aciklama)"
        " VALUES(?,?,?,?,?,?,?,?)",
        (eser["id"], datetime.now().isoformat(timespec="seconds"), eser["durum"], yeni_durum,
         eser["sergi_id"], yeni_sergi_id, kullanici, aciklama))


def eser_gecmis(a):
    from muze import baglan
    con = baglan()
    try:
        e = con.execute("SELECT id, ad FROM eserler WHERE envanter_no=?", (a.no,)).fetchone()
        if not e:
            sys.exit("Eser bulunamadı.")
        print(f"== {a.no} {e['ad']} geçmişi ==")
        satirlar = con.execute(
            "SELECT h.*, so.ad AS eski_sergi, sy.ad AS yeni_sergi FROM hareketler h "
            "LEFT JOIN sergiler so ON so.id=h.eski_sergi_id LEFT JOIN sergiler sy ON sy.id=h.yeni_sergi_id "
            "WHERE h.eser_id=? ORDER BY h.id", (e["id"],)).fetchall()
        if not satirlar:
            print("Hareket kaydı yok.")
        for r in satirlar:
            yer = f" [{r['eski_sergi'] or '-'} -> {r['yeni_sergi'] or '-'}]" if r["eski_sergi_id"] or r["yeni_sergi_id"] else ""
            print(f"{r['tarih']}  {r['eski_durum'] or '-'} -> {r['yeni_durum']}{yer}  "
                  f"({r['kullanici']}){'  ' + r['aciklama'] if r['aciklama'] else ''}")
    finally:
        con.close()


def komutlar(sp):
    x = sp.add_parser("eser-gecmis", help="eserin hareket geçmişi")
    x.add_argument("no")
    x.set_defaults(f=eser_gecmis)
