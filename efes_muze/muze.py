#!/usr/bin/env python3
"""Efes Müzesi Yönetim Programı: eser envanteri, ziyaretçi/bilet ve sergi yönetimi."""
import argparse
import sqlite3
import sys
from datetime import date

DB = "efes_muze.db"
BILET_FIYAT = {"yetiskin": 200.0, "ogrenci": 50.0, "cocuk": 0.0, "muze_kart": 0.0}

SEMA = """
CREATE TABLE IF NOT EXISTS eserler(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  envanter_no TEXT UNIQUE NOT NULL,
  ad TEXT NOT NULL,
  donem TEXT,
  malzeme TEXT,
  bulundugu_yer TEXT,
  durum TEXT NOT NULL DEFAULT 'depoda',
  sergi_id INTEGER REFERENCES sergiler(id)
);
CREATE TABLE IF NOT EXISTS sergiler(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ad TEXT UNIQUE NOT NULL,
  salon TEXT
);
CREATE TABLE IF NOT EXISTS biletler(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tarih TEXT NOT NULL,
  tur TEXT NOT NULL,
  adet INTEGER NOT NULL,
  tutar REAL NOT NULL
);
"""


def baglan():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(SEMA)
    return con


def eser_ekle(a):
    with baglan() as con:
        try:
            con.execute(
                "INSERT INTO eserler(envanter_no,ad,donem,malzeme,bulundugu_yer) VALUES(?,?,?,?,?)",
                (a.no, a.ad, a.donem, a.malzeme, a.yer))
        except sqlite3.IntegrityError:
            sys.exit(f"Hata: {a.no} envanter numarası zaten kayıtlı.")
    print("Eser eklendi.")


def eser_listele(a):
    sql = "SELECT e.*, s.ad AS sergi FROM eserler e LEFT JOIN sergiler s ON s.id=e.sergi_id WHERE 1=1"
    p = []
    if a.ara:
        sql += " AND (e.ad LIKE ? OR e.donem LIKE ? OR e.malzeme LIKE ?)"
        p += [f"%{a.ara}%"] * 3
    if a.durum:
        sql += " AND e.durum=?"
        p.append(a.durum)
    for r in baglan().execute(sql + " ORDER BY e.envanter_no", p):
        print(f"{r['envanter_no']:<10} {r['ad']:<30} {r['donem'] or '-':<14} "
              f"{r['durum']:<10} {r['sergi'] or '-'}")


def eser_durum(a):
    with baglan() as con:
        n = con.execute("UPDATE eserler SET durum=? WHERE envanter_no=?", (a.durum, a.no)).rowcount
        if a.durum != "sergide":
            con.execute("UPDATE eserler SET sergi_id=NULL WHERE envanter_no=?", (a.no,))
    print("Güncellendi." if n else "Eser bulunamadı.")


def sergi_ekle(a):
    with baglan() as con:
        try:
            con.execute("INSERT INTO sergiler(ad,salon) VALUES(?,?)", (a.ad, a.salon))
        except sqlite3.IntegrityError:
            sys.exit("Hata: bu sergi zaten var.")
    print("Sergi eklendi.")


def sergiye_yerlestir(a):
    with baglan() as con:
        s = con.execute("SELECT id FROM sergiler WHERE ad=?", (a.sergi,)).fetchone()
        if not s:
            sys.exit("Sergi bulunamadı.")
        n = con.execute("UPDATE eserler SET sergi_id=?, durum='sergide' WHERE envanter_no=? AND durum!='restorasyonda'",
                        (s["id"], a.no)).rowcount
    print("Eser sergiye yerleştirildi." if n else "Eser bulunamadı veya restorasyonda.")


def sergi_listele(a):
    for r in baglan().execute(
            "SELECT s.ad, s.salon, COUNT(e.id) n FROM sergiler s LEFT JOIN eserler e ON e.sergi_id=s.id GROUP BY s.id"):
        print(f"{r['ad']:<30} salon: {r['salon'] or '-':<10} eser: {r['n']}")


def bilet_sat(a):
    if a.tur not in BILET_FIYAT:
        sys.exit(f"Geçersiz tür. Seçenekler: {', '.join(BILET_FIYAT)}")
    if a.adet < 1:
        sys.exit("Adet en az 1 olmalı.")
    tutar = BILET_FIYAT[a.tur] * a.adet
    with baglan() as con:
        con.execute("INSERT INTO biletler(tarih,tur,adet,tutar) VALUES(?,?,?,?)",
                    (date.today().isoformat(), a.tur, a.adet, tutar))
    print(f"{a.adet} x {a.tur} bileti satıldı. Tutar: {tutar:.2f} TL")


def rapor(a):
    con = baglan()
    t = a.tarih or date.today().isoformat()
    print(f"== {t} günlük rapor ==")
    for r in con.execute("SELECT tur, SUM(adet) n, SUM(tutar) t FROM biletler WHERE tarih=? GROUP BY tur", (t,)):
        print(f"{r['tur']:<10} {r['n']:>5} kişi  {r['t']:>9.2f} TL")
    r = con.execute("SELECT COALESCE(SUM(adet),0) n, COALESCE(SUM(tutar),0) t FROM biletler WHERE tarih=?", (t,)).fetchone()
    print(f"TOPLAM     {r['n']:>5} kişi  {r['t']:>9.2f} TL")
    print("-- Eser durumları --")
    for r in con.execute("SELECT durum, COUNT(*) n FROM eserler GROUP BY durum"):
        print(f"{r['durum']:<14} {r['n']}")


def main():
    p = argparse.ArgumentParser(description="Efes Müzesi Yönetim Programı")
    sp = p.add_subparsers(dest="komut", required=True)

    x = sp.add_parser("eser-ekle", help="yeni eser kaydı")
    x.add_argument("no"); x.add_argument("ad")
    x.add_argument("--donem"); x.add_argument("--malzeme"); x.add_argument("--yer")
    x.set_defaults(f=eser_ekle)

    x = sp.add_parser("eser-listele", help="eserleri listele/ara")
    x.add_argument("--ara"); x.add_argument("--durum", choices=["depoda", "sergide", "restorasyonda", "odunc"])
    x.set_defaults(f=eser_listele)

    x = sp.add_parser("eser-durum", help="eser durumunu değiştir")
    x.add_argument("no"); x.add_argument("durum", choices=["depoda", "sergide", "restorasyonda", "odunc"])
    x.set_defaults(f=eser_durum)

    x = sp.add_parser("sergi-ekle"); x.add_argument("ad"); x.add_argument("--salon"); x.set_defaults(f=sergi_ekle)
    x = sp.add_parser("sergi-listele"); x.set_defaults(f=sergi_listele)
    x = sp.add_parser("yerlestir", help="eseri sergiye yerleştir")
    x.add_argument("no"); x.add_argument("sergi"); x.set_defaults(f=sergiye_yerlestir)

    x = sp.add_parser("bilet", help="bilet sat")
    x.add_argument("tur"); x.add_argument("adet", type=int); x.set_defaults(f=bilet_sat)

    x = sp.add_parser("rapor", help="günlük rapor"); x.add_argument("--tarih"); x.set_defaults(f=rapor)

    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
