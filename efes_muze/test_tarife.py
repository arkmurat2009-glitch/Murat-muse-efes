"""Çalıştır: python3 -m unittest test_tarife -v  (geçici DB kullanır)"""
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

_d = tempfile.mkdtemp()
os.environ["EFES_MUZE_DB"] = os.path.join(_d, "tarife.db")
import muze
from eklentiler import tarife
from eklentiler.tarife import TarifeHatasi


class Tarife(unittest.TestCase):
    def setUp(self):
        if os.path.exists(muze.DB):
            os.remove(muze.DB)
        self.con = muze.baglan()

    def tearDown(self):
        self.con.close()

    def sat(self, tur, adet, tutar, gun="2026-11-01"):
        self.con.execute("INSERT INTO biletler(tarih,tur,adet,tutar) VALUES(?,?,?,?)", (gun, tur, adet, tutar))

    def test_tarihli_fiyat_ve_varsayilan(self):
        self.assertEqual(tarife.fiyat(self.con, "yetiskin", "2026-11-01", 200.0), 200.0)  # kayıt yok: varsayılan
        tarife.tarife_ayarla(self.con, "yetiskin", 300, "2026-01-01", "Yönerge A", "t")
        tarife.tarife_ayarla(self.con, "yetiskin", 700, "2026-07-01", "Duyuru B", "t")
        self.assertEqual(tarife.fiyat(self.con, "yetiskin", "2026-03-01"), 300)
        self.assertEqual(tarife.fiyat(self.con, "yetiskin", "2026-07-01"), 700)
        self.assertIsNone(tarife.fiyat(self.con, "yetiskin", "2025-12-31"))  # henüz geçerli tarife yok

    def test_tarife_dogrulama_ve_degismezlik(self):
        with self.assertRaises(TarifeHatasi):
            tarife.tarife_ayarla(self.con, "vip", 1, "2026-01-01", "k", "t")
        with self.assertRaises(TarifeHatasi):
            tarife.tarife_ayarla(self.con, "yetiskin", -1, "2026-01-01", "k", "t")
        with self.assertRaises(TarifeHatasi):
            tarife.tarife_ayarla(self.con, "yetiskin", 1, "2026-01-01", "  ", "t")
        with self.assertRaises(TarifeHatasi):
            tarife.tarife_ayarla(self.con, "yetiskin", 1, "dün", "k", "t")
        tarife.tarife_ayarla(self.con, "yetiskin", 1, "2026-01-01", "k", "t")
        for q in ("UPDATE tarifeler SET fiyat=2", "DELETE FROM tarifeler"):
            with self.assertRaises(sqlite3.DatabaseError):
                self.con.execute(q)

    def test_iade_tutar_ve_sinir(self):
        self.sat("yetiskin", 4, 800)
        self.con.commit()
        t = tarife.iade(self.con, "yetiskin", 1, "yanlış tür", "t", "2026-11-01", "2026-11-01")
        self.assertEqual(t, 200.0)
        tarife.iade(self.con, "yetiskin", 3, "grup iptali", "t", "2026-11-01", "2026-11-02")
        with self.assertRaises(TarifeHatasi):  # 4 satıldı, 4 iade edildi
            tarife.iade(self.con, "yetiskin", 1, "fazla", "t", "2026-11-01", "2026-11-02")
        self.assertEqual(tarife.iade_ozeti(self.con, "2026-11-02"), (3, 600.0))

    def test_iade_gecersiz_girdiler(self):
        self.sat("ogrenci", 2, 100)
        self.con.commit()
        for args in (("vip", 1, "n"), ("ogrenci", 0, "n"), ("ogrenci", 1, " "), ("yetiskin", 1, "n")):
            with self.assertRaises(TarifeHatasi):
                tarife.iade(self.con, *args, "t", "2026-11-01")
        with self.assertRaises(TarifeHatasi):  # iade tarihi satıştan önce
            tarife.iade(self.con, "ogrenci", 1, "n", "t", "2026-11-01", "2026-10-31")
        tarife.iade(self.con, "ogrenci", 1, "n", "t", "2026-11-01", "2026-11-01")
        for q in ("DELETE FROM bilet_iadeleri", "UPDATE bilet_iadeleri SET adet=1"):
            with self.assertRaises(sqlite3.DatabaseError):
                self.con.execute(q)

    def test_cli_bilet_fiyati_tarifeden_ve_rapor(self):
        self.con.close()
        def c(*arg):
            return subprocess.run([sys.executable, "muze.py", *arg], capture_output=True, text=True,
                                  env=dict(os.environ, EFES_MUZE_DB=muze.DB, EFES_KULLANICI="t"),
                                  cwd=os.path.dirname(os.path.abspath(__file__)))
        self.assertEqual(c("tarife-ayarla", "yetiskin", "350", "--baslangic", "2020-01-01",
                           "--kaynak", "Test yönergesi").returncode, 0)
        self.assertIn("Tutar: 700.00", c("bilet", "yetiskin", "2").stdout)
        self.assertEqual(c("bilet-iade", "yetiskin", "1", "--neden", "hatalı satış").returncode, 0)
        self.assertNotEqual(c("bilet-iade", "yetiskin", "5", "--neden", "x").returncode, 0)
        r = c("rapor").stdout
        self.assertIn("İADE", r)
        self.assertRegex(r, r"NET\s+1 kişi\s+350\.00 TL")
        self.assertIn("Test yönergesi", c("tarife-listele").stdout)
        self.con = muze.baglan()


if __name__ == "__main__":
    unittest.main()
