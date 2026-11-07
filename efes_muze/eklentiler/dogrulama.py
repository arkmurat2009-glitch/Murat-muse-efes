"""DB düzeyinde doğrulama. SQLite mevcut tabloya CHECK ekleyemediği için (ALTER yok, tablo yeniden
kurmak mevcut DB'yi riske atar) BEFORE INSERT/UPDATE tetikleyicileri kullanılır. Yalnızca yeni yazmaları
denetler; mevcut satırlara dokunmaz."""

DURUMLAR = ("depoda", "sergide", "restorasyonda", "odunc")
BILET_TURLERI = ("yetiskin", "ogrenci", "cocuk", "muze_kart")


def _liste(t):
    return ",".join(f"'{x}'" for x in t)


SEMA = f"""
CREATE TRIGGER IF NOT EXISTS eserler_durum_ekle BEFORE INSERT ON eserler
WHEN NEW.durum NOT IN ({_liste(DURUMLAR)}) OR TRIM(NEW.envanter_no)='' OR TRIM(NEW.ad)=''
BEGIN SELECT RAISE(ABORT, 'eserler: geçersiz durum veya boş envanter_no/ad'); END;
CREATE TRIGGER IF NOT EXISTS eserler_durum_guncelle BEFORE UPDATE OF durum, sergi_id ON eserler
WHEN NEW.durum NOT IN ({_liste(DURUMLAR)})
  OR (NEW.durum='sergide' AND NEW.sergi_id IS NULL)
  OR (NEW.durum IN ('odunc','restorasyonda') AND NEW.sergi_id IS NOT NULL)
BEGIN SELECT RAISE(ABORT, 'eserler: geçersiz durum/sergi birleşimi'); END;
CREATE TRIGGER IF NOT EXISTS biletler_ekle BEFORE INSERT ON biletler
WHEN NEW.tur NOT IN ({_liste(BILET_TURLERI)}) OR NEW.adet < 1 OR NEW.tutar < 0
BEGIN SELECT RAISE(ABORT, 'biletler: geçersiz tür/adet/tutar'); END;
"""


def sema(con):
    con.executescript(SEMA)
