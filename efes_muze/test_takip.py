"""Çalıştır: python3 -m unittest test_takip -v  (geçici DB kullanır)"""
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

_d = tempfile.mkdtemp()
os.environ["EFES_MUZE_DB"] = os.path.join(_d, "takip.db")
import muze
from eklentiler import takip
from eklentiler.takip import TakipHatasi


class Takip(unittest.TestCase):
    def setUp(self):
        if os.path.exists(muze.DB):
            os.remove(muze.DB)
        self.con = muze.baglan()
        self.con.execute("INSERT INTO eserler(envanter_no,ad) VALUES('E1','Vazo')")
        self.con.execute("INSERT INTO eserler(envanter_no,ad) VALUES('E2','Heykel')")
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def durum(self, no="E1"):
        return self.con.execute("SELECT durum FROM eserler WHERE envanter_no=?", (no,)).fetchone()[0]

    def test_restorasyon_dongusu(self):
        takip.restorasyon_baslat(self.con, "E1", "Atölye A", "Ayşe", "2026-12-01", kullanici="t",
                                 baslangic="2026-11-01")
        self.con.commit()
        self.assertEqual(self.durum(), "restorasyonda")
        takip.restorasyon_bitir(self.con, "E1", "temizlendi", kullanici="t", bitis="2026-11-20")
        self.con.commit()
        self.assertEqual(self.durum(), "depoda")
        r = self.con.execute("SELECT * FROM restorasyonlar").fetchone()
        self.assertEqual((r["bitis"], r["sonuc_notu"]), ("2026-11-20", "temizlendi"))
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM hareketler").fetchone()[0], 2)

    def test_cift_kayit_ve_gecersiz_tarih(self):
        takip.restorasyon_baslat(self.con, "E1", "A", "S", "2026-12-01", baslangic="2026-11-01")
        with self.assertRaises(TakipHatasi):
            takip.odunc_ver(self.con, "E1", "Kurum", "2026-12-01", cikis="2026-11-02")
        with self.assertRaises(TakipHatasi):
            takip.restorasyon_baslat(self.con, "E2", "A", "S", "2026-10-01", baslangic="2026-11-01")
        with self.assertRaises(TakipHatasi):
            takip.restorasyon_baslat(self.con, "E2", "A", "S", "yarın")

    def test_odunc_iade(self):
        takip.odunc_ver(self.con, "E1", "Ankara Müzesi", "2027-01-01", sigorta_degeri=1000,
                        kondisyon_notu="iyi", cikis="2026-11-01")
        self.assertEqual(self.durum(), "odunc")
        takip.odunc_iade(self.con, "E1", "hasarsız", donus="2026-12-30")
        self.assertEqual(self.durum(), "depoda")
        o = self.con.execute("SELECT * FROM oduncler").fetchone()
        self.assertEqual(o["gercek_donus"], "2026-12-30")
        self.assertEqual(o["kondisyon_notu"], "iyi | iade: hasarsız")
        with self.assertRaises(TakipHatasi):
            takip.odunc_iade(self.con, "E1")

    def test_yurt_disi_kurallari(self):
        with self.assertRaises(TakipHatasi):  # izin yok
            takip.odunc_ver(self.con, "E1", "Louvre", "2027-01-01", sigorta_degeri=5, yurt_disi=True,
                            cikis="2026-11-01")
        with self.assertRaises(TakipHatasi):  # sigorta yok
            takip.odunc_ver(self.con, "E1", "Louvre", "2027-01-01", izin_no="K-1", yurt_disi=True,
                            cikis="2026-11-01")
        with self.assertRaises(TakipHatasi):  # tek ülke > 1 yıl
            takip.odunc_ver(self.con, "E1", "Louvre", "2027-12-01", sigorta_degeri=5, izin_no="K-1",
                            yurt_disi=True, ulke_sayisi=1, cikis="2026-11-01")
        self.assertEqual(self.durum(), "depoda")  # reddedilen işlem eseri değiştirmez
        takip.odunc_ver(self.con, "E1", "Louvre", "2028-10-01", sigorta_degeri=5, izin_no="K-1",
                        yurt_disi=True, ulke_sayisi=2, cikis="2026-11-01")
        self.assertEqual(self.durum(), "odunc")

    def test_geciken_listesi(self):
        takip.restorasyon_baslat(self.con, "E1", "A", "S", "2026-11-10", baslangic="2026-11-01")
        takip.odunc_ver(self.con, "E2", "Kurum", "2026-11-20", cikis="2026-11-01")
        l = takip.gecikenler(self.con, "2026-11-25")
        self.assertEqual([(x[0], x[1], x[5]) for x in l], [("restorasyon", "E1", 15), ("odunc", "E2", 5)])
        self.assertEqual(takip.gecikenler(self.con, "2026-11-05"), [])

    def test_kayitlar_degistirilemez(self):
        takip.restorasyon_baslat(self.con, "E1", "A", "S", "2026-12-01", baslangic="2026-11-01")
        with self.assertRaises(sqlite3.DatabaseError):
            self.con.execute("DELETE FROM restorasyonlar")
        takip.restorasyon_bitir(self.con, "E1", bitis="2026-11-02")
        with self.assertRaises(sqlite3.DatabaseError):
            self.con.execute("UPDATE restorasyonlar SET atolye='X'")

    def test_cli_dogrudan_gecis_engellenir(self):
        self.con.close()
        def c(*arg):
            return subprocess.run([sys.executable, "muze.py", *arg], capture_output=True, text=True,
                                  env=dict(os.environ, EFES_MUZE_DB=muze.DB),
                                  cwd=os.path.dirname(os.path.abspath(__file__)))
        self.assertNotEqual(c("eser-durum", "E1", "restorasyonda").returncode, 0)
        r = c("restorasyon-baslat", "E1", "--atolye", "A", "--sorumlu", "S", "--bitis", "2020-01-01",
              "--baslangic", "2019-12-01", "--kullanici", "t")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotEqual(c("eser-durum", "E1", "depoda").returncode, 0)  # açık kayıt varken
        self.assertIn("gecikti", c("geciken-listesi").stdout)
        self.assertEqual(c("restorasyon-bitir", "E1", "--kullanici", "t").returncode, 0)
        self.assertEqual(c("eser-durum", "E1", "sergide").returncode != 0, True)  # sergi gerekir
        self.con = muze.baglan()


if __name__ == "__main__":
    unittest.main()
