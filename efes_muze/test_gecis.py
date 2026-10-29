"""Çalıştır: python3 -m unittest test_gecis -v  (geçici DB kullanır, gerçek DB'ye dokunmaz)"""
import os
import sqlite3
import subprocess
import sys
import tempfile
from types import SimpleNamespace
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


    def test_bozuk_eski_durum_depoya_kurtarilir(self):
        self.con.execute("DROP TRIGGER eserler_durum_guncelle")
        self.con.execute("UPDATE eserler SET durum='kayip'")
        self.con.commit()
        muze.eklentiler.sema_uygula(self.con)
        with self.assertRaises(gecis.GecisHatasi):
            gecis.degistir(self.con, "E1", "odunc", kullanici="t")
        gecis.degistir(self.con, "E1", "depoda", kullanici="t")
        self.assertEqual(self.durum()[0], "depoda")

    def test_rollback_hareket_yazilmaz(self):
        self.con.commit()
        try:
            with self.con:
                gecis.degistir(self.con, "E1", "odunc", kullanici="t")
                raise RuntimeError
        except RuntimeError:
            pass
        self.assertEqual(self.durum()[0], "depoda")
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM hareketler").fetchone()[0], 0)

    def test_eszamanli_degisiklik_reddedilir(self):
        self.con.commit()
        diger = sqlite3.connect(muze.DB, timeout=0.1)
        diger.execute("BEGIN IMMEDIATE")  # yazma kilidi
        self.con.execute("PRAGMA busy_timeout=100")
        with self.assertRaises(sqlite3.OperationalError):
            gecis.degistir(self.con, "E1", "odunc", kullanici="t")
        diger.rollback(); diger.close()

    def test_kullanici_onceligi(self):
        from eklentiler import hareketler
        os.environ["EFES_KULLANICI"] = "env"
        try:
            self.assertEqual(hareketler.kullanici_adi(SimpleNamespace(kullanici="arg")), "arg")
            self.assertEqual(hareketler.kullanici_adi(SimpleNamespace(kullanici=None)), "env")
        finally:
            del os.environ["EFES_KULLANICI"]

    def test_eski_db_yukseltme_ve_cli(self):
        db = os.path.join(_d, "eski.db")
        con = sqlite3.connect(db)
        con.executescript(muze.SEMA)  # eklentisiz eski şema
        con.execute("INSERT INTO eserler(envanter_no,ad) VALUES('E9','eski')")
        con.commit(); con.close()
        env = dict(os.environ, EFES_MUZE_DB=db)
        def calistir(*arg):
            return subprocess.run([sys.executable, "muze.py", *arg], env=env, capture_output=True,
                                  text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        r = calistir("eser-durum", "E9", "odunc", "--kullanici", "ali")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = calistir("eser-durum", "E9", "sergide")
        self.assertNotEqual(r.returncode, 0)
        r = calistir("eser-gecmis", "E9")
        self.assertIn("depoda -> odunc", r.stdout)
        self.assertIn("(ali)", r.stdout)


if __name__ == "__main__":
    unittest.main()
