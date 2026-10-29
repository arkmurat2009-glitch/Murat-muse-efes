"""Çalıştır: python3 -m unittest test_gecis -v  (geçici DB kullanır, gerçek DB'ye dokunmaz)"""
import os
import sqlite3
import tempfile
import unittest

_d = tempfile.mkdtemp()
os.environ["EFES_MUZE_DB"] = os.path.join(_d, "test.db")
import muze
from eklentiler import gecis


class Gecis(unittest.TestCase):
    def setUp(self):
        if os.path.exists(muze.DB):
            os.remove(muze.DB)
        self.con = muze.baglan()
        self.con.execute("INSERT INTO eserler(envanter_no,ad) VALUES('E1','x')")
        self.con.execute("INSERT INTO sergiler(ad) VALUES('S')")
        self.sid = self.con.execute("SELECT id FROM sergiler").fetchone()[0]

    def tearDown(self):
        self.con.close()

    def durum(self):
        return self.con.execute("SELECT durum, sergi_id FROM eserler").fetchone()

    def test_odunc_sergiye_yerlesemez(self):
        gecis.degistir(self.con, "E1", "odunc", kullanici="t")
        with self.assertRaises(gecis.GecisHatasi):
            gecis.degistir(self.con, "E1", "sergide", self.sid, "t")
        self.assertEqual(self.durum()[0], "odunc")

    def test_sergide_sergisiz_olmaz(self):
        with self.assertRaises(gecis.GecisHatasi):
            gecis.degistir(self.con, "E1", "sergide", None, "t")

    def test_restorasyon_sadece_depoya(self):
        gecis.degistir(self.con, "E1", "restorasyonda", kullanici="t")
        with self.assertRaises(gecis.GecisHatasi):
            gecis.degistir(self.con, "E1", "odunc", kullanici="t")

    def test_hareket_kaydi_ve_sergi_temizlenir(self):
        gecis.degistir(self.con, "E1", "sergide", self.sid, "ali", "açılış")
        gecis.degistir(self.con, "E1", "depoda", kullanici="ali")
        self.assertEqual(tuple(self.durum()), ("depoda", None))
        n = self.con.execute("SELECT COUNT(*) FROM hareketler").fetchone()[0]
        self.assertEqual(n, 2)

    def test_db_kisitlari(self):
        gecis.degistir(self.con, "E1", "odunc", kullanici="t")
        for q in ("UPDATE eserler SET durum='bozuk'", "DELETE FROM hareketler",
                  "INSERT INTO biletler(tarih,tur,adet,tutar) VALUES('2026-01-01','vip',1,1)"):
            with self.assertRaises(sqlite3.DatabaseError):
                self.con.execute(q)


if __name__ == "__main__":
    unittest.main()
