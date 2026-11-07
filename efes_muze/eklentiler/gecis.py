"""Eser durum geçiş kuralları. Geçişler tek işlemde uygulanır ve hareketler tablosuna yazılır."""
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
    # Eski sürümlerden kalan geçersiz durum (ör. 'kayip') yalnızca 'depoda' ile kurtarılır.
    if eski not in GECISLER:
        if yeni == "depoda":
            return
        raise GecisHatasi(f"'{eski}' tanımsız bir durum; önce 'depoda' durumuna alın.")
    if yeni not in GECISLER[eski]:
        izinli = ", ".join(sorted(GECISLER.get(eski, ()))) or "yok"
        raise GecisHatasi(f"'{eski}' durumundan '{yeni}' durumuna geçilemez. İzinli: {izinli}.")


def degistir(con, no, yeni, sergi_id=None, kullanici=None, aciklama=None):
    """Durumu değiştirir. Hata durumunda GecisHatasi; çağıran işlemi geri alır."""
    if not con.in_transaction:
        con.execute("BEGIN IMMEDIATE")  # okuma-yazma arası eşzamanlı değişikliği engelle
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
    # Koşullu güncelleme: satır okunduktan sonra değiştiyse hareket zinciri bozulmaz.
    n = con.execute("UPDATE eserler SET durum=?, sergi_id=? WHERE id=? AND durum=? AND sergi_id IS ?",
                    (yeni, sergi_id, e["id"], e["durum"], e["sergi_id"])).rowcount
    if n != 1:
        raise GecisHatasi("Eser aynı anda başka biri tarafından değiştirildi; tekrar deneyin.")
    hareketler.kaydet(con, e, yeni, sergi_id, kullanici or hareketler.kullanici_adi(), aciklama)


def sema(con):
    pass
