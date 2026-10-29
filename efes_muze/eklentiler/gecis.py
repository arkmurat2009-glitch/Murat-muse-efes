"""Eser durum geçiş kuralları. Geçişler tek işlemde uygulanır ve hareketler tablosuna yazılır."""
import sqlite3
import sys

from . import hareketler

# Her durumdan izin verilen hedefler. 'sergide' yalnızca `yerlestir` ile (sergi gerekli) alınır.
GECISLER = {
    "depoda": {"sergide", "restorasyonda", "odunc"},
    "sergide": {"sergide", "depoda", "restorasyonda", "odunc"},
    "restorasyonda": {"depoda"},
    "odunc": {"depoda"},
}


class GecisHatasi(Exception):
    pass


def kontrol(eski, yeni):
    if yeni not in GECISLER.get(eski, ()):
        izinli = ", ".join(sorted(GECISLER.get(eski, ()))) or "yok"
        raise GecisHatasi(f"'{eski}' durumundan '{yeni}' durumuna geçilemez. İzinli: {izinli}.")


def degistir(con, no, yeni, sergi_id=None, kullanici=None, aciklama=None):
    """Durumu değiştirir. Hata durumunda GecisHatasi; çağıran işlemi geri alır."""
    e = con.execute("SELECT * FROM eserler WHERE envanter_no=?", (no,)).fetchone()
    if not e:
        raise GecisHatasi("Eser bulunamadı.")
    if yeni == "sergide":
        if sergi_id is None:
            raise GecisHatasi("'sergide' durumu için sergi gerekir; 'yerlestir' komutunu kullanın.")
    else:
        sergi_id = None
    if e["durum"] == yeni and sergi_id == e["sergi_id"]:
        raise GecisHatasi(f"Eser zaten '{yeni}' durumunda.")
    kontrol(e["durum"], yeni)
    hareketler.kaydet(con, e, yeni, sergi_id, kullanici or hareketler.kullanici_adi(), aciklama)
    con.execute("UPDATE eserler SET durum=?, sergi_id=? WHERE id=?", (yeni, sergi_id, e["id"]))


def sema(con):
    pass
