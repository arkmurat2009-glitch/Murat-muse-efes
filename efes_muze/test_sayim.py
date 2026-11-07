"""Çalıştır: python3 -m unittest test_sayim -v  (geçici DB kullanır)"""
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

_d = tempfile.mkdtemp()
os.environ["EFES_MUZE_DB"] = os.path.join(_d, "sayim.db")
import muze
from eklentiler import sayim
from eklentiler.sayim import SayimHatasi


class Sayim(unittest.TestCase):
    def setUp(self):
        if os.path.exists(muze.DB):
            os.remove(muze.DB)
        self.con = muze.baglan()
        for no, ad, yer, durum in (("E1", "Vazo", "Salon A", "depoda"), ("E2", "Heykel", "Salon A", "depoda"),
                                   ("E3", "Sikke", "Salon A", "odunc"), ("E4", "Mozaik", "Salon B", "depoda")):
            self.con.execute("INSERT INTO eserler(envanter_no,ad,bulundugu_yer,durum) VALUES(?,?,?,?)",
                             (no, ad, yer, durum))
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def test_kapsam_ve_anlik_goruntu(self):
        sid = sayim.baslat(self.con, "Ali", yer="salon a")  # büyük/küçük harf duyarsız
        r = sayim.rapor(self.con, sid)
        self.assertEqual((r["beklenen"], len(r["disarida"])), (2, 1))  # E3 ödünçte: sayım dışı
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM sayim_satirlari").fetchone()[0], 3)

    def test_mutabakat_eksik_fazla_konum(self):
        sid = sayim.baslat(self.con, "Ali", yer="Salon A", komisyon="A, B, C")
        sayim.isaretle(self.con, sid, "E1", "t")
        sayim.isaretle(self.con, sid, "E4", "t", yer="Salon A")  # Salon B kayıtlı, burada bulundu: fazla
        sayim.isaretle(self.con, sid, "E3", "t")  # ödünçte kayıtlı ama bulundu: fazla/uyumsuz
        r = sayim.rapor(self.con, sid)
        self.assertEqual([x["envanter_no"] for x in r["eksik"]], ["E2"])
        self.assertEqual(sorted(x["envanter_no"] for x in r["fazla"]), ["E3", "E4"])
        self.assertEqual([x["envanter_no"] for x in r["konum_farki"]], ["E4"])
        self.assertEqual(len(r["bulunan"]), 1)

    def test_konum_ayni_ise_fark_yok(self):
        sid = sayim.baslat(self.con, "Ali", yer="Salon A")
        sayim.isaretle(self.con, sid, "E1", "t", yer="SALON A")
        self.assertEqual(sayim.rapor(self.con, sid)["konum_farki"], [])

    def test_gecersiz_girdiler(self):
        for kw in ({}, {"tumu": True, "yer": "x"}, {"yer": "Yok"}, {"sergi": "Yok"}):
            with self.assertRaises(SayimHatasi):
                sayim.baslat(self.con, "Ali", **kw)
        with self.assertRaises(SayimHatasi):
            sayim.baslat(self.con, " ", tumu=True)
        sid = sayim.baslat(self.con, "Ali", tumu=True)
        with self.assertRaises(SayimHatasi):
            sayim.isaretle(self.con, sid, "YOK", "t")
        sayim.isaretle(self.con, sid, "E1", "t")
        with self.assertRaises(SayimHatasi):  # çift işaretleme
            sayim.isaretle(self.con, sid, "E1", "t")

    def test_kapali_sayim_degismez_ve_kayitlar_korunur(self):
        sid = sayim.baslat(self.con, "Ali", yer="Salon A")
        sayim.isaretle(self.con, sid, "E1", "t")
        sayim.kapat(self.con, sid)
        with self.assertRaises(SayimHatasi):
            sayim.isaretle(self.con, sid, "E2", "t")
        with self.assertRaises(SayimHatasi):
            sayim.kapat(self.con, sid)
        for q in ("UPDATE sayim_satirlari SET bulundu=1", "DELETE FROM sayim_satirlari", "DELETE FROM sayimlar",
                  "UPDATE sayimlar SET sorumlu='x'"):
            with self.assertRaises(sqlite3.DatabaseError):
                self.con.execute(q)
        # sayım eser kaydını değiştirmez
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM eserler WHERE durum='depoda'").fetchone()[0], 3)

    def test_sergi_kapsami(self):
        self.con.execute("INSERT INTO sergiler(ad) VALUES('Roma')")
        sid_ = self.con.execute("SELECT id FROM sergiler").fetchone()[0]
        self.con.execute("UPDATE eserler SET durum='sergide', sergi_id=? WHERE envanter_no='E1'", (sid_,))
        sid = sayim.baslat(self.con, "Ali", sergi="Roma")
        self.assertEqual(sayim.rapor(self.con, sid)["beklenen"], 1)

    def test_cli_akis(self):
        self.con.close()
        def c(*arg):
            return subprocess.run([sys.executable, "muze.py", *arg], capture_output=True, text=True,
                                  env=dict(os.environ, EFES_MUZE_DB=muze.DB, EFES_KULLANICI="t"),
                                  cwd=os.path.dirname(os.path.abspath(__file__)))
        r = c("sayim-baslat", "--yer", "Salon A", "--sorumlu", "Ali", "--komisyon", "A, B")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Beklenen: 2", r.stdout)
        self.assertEqual(c("sayim-isaretle", "1", "E1").returncode, 0)
        self.assertNotEqual(c("sayim-isaretle", "1", "YOK").returncode, 0)
        self.assertIn("EKSİK", c("sayim-rapor", "1").stdout)
        k = c("sayim-kapat", "1").stdout
        self.assertIn("KAPALI", k)
        self.assertIn("E2", k)
        self.assertNotEqual(c("sayim-isaretle", "1", "E2").returncode, 0)
        self.assertIn("kapali", c("sayim-listele").stdout)
        self.con = muze.baglan()


if __name__ == "__main__":
    unittest.main()
