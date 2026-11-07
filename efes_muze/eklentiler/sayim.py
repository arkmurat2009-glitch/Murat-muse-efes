"""Envanter sayımı ve mutabakat: beklenen listesi (anlık görüntü), işaretleme, eksik/fazla/konum farkı tutanağı.

Program eser kaydını DÜŞMEZ ve durumunu DEĞİŞTİRMEZ; yalnızca fark tutanağı üretir. Eksik eser için kayıttan
düşme, fazla için sayım fazlası/değer tespiti süreçleri kurumun taşınır usullerine göre ayrıca yürütülür.

Mevzuat notu (kontrol tarihi 2026-11-07, web aramasıyla ve YALNIZCA ikincil kaynaklarla; resmî metinle teyit edilmeli):
- Taşınır Mal Yönetmeliği uygulamasında yıl sonu sayımı, harcama yetkilisinin görevlendirdiği sayım komisyonunca
  yapılır; sayım ve döküm cetveli düzenlenir. Eksik için tutanak ve kayıttan düşme teklif/onay tutanağı; fazla için
  sayım fazlası fişi ve değer tespiti gerekir. Müze birimleri Müze Yönetim Hesabı Cetveli düzenler.
- Müzeler İç Hizmetler Yönetmeliği'nin sayım hükümleri DOĞRULANAMADI; madde numarası ve sayım sıklığı varsayılmadı.
Kullanıcı ve komisyon alanları personel adıdır (KVKK 6698); ziyaretçi verisi tutulmaz.
"""
import sys
from datetime import datetime

from . import hareketler

FIZIKSEL = ("depoda", "sergide")  # fiziken müzede bulunması beklenen durumlar

SEMA = """
CREATE TABLE IF NOT EXISTS sayimlar(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  baslangic TEXT NOT NULL,
  kapsam_tur TEXT NOT NULL CHECK(kapsam_tur IN ('tumu','yer','sergi')),
  kapsam_deger TEXT,
  sorumlu TEXT NOT NULL,
  komisyon TEXT,
  durum TEXT NOT NULL DEFAULT 'acik' CHECK(durum IN ('acik','kapali')),
  kapanis TEXT
);
CREATE TABLE IF NOT EXISTS sayim_satirlari(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sayim_id INTEGER NOT NULL REFERENCES sayimlar(id),
  eser_id INTEGER NOT NULL REFERENCES eserler(id),
  beklenen INTEGER NOT NULL,
  beklenen_yer TEXT,
  beklenen_durum TEXT NOT NULL,
  bulundu INTEGER,
  bulunan_yer TEXT,
  isaretleme TEXT,
  isaretleyen TEXT,
  aciklama TEXT,
  UNIQUE(sayim_id, eser_id)
);
CREATE INDEX IF NOT EXISTS sayim_satirlari_sayim ON sayim_satirlari(sayim_id);
CREATE TRIGGER IF NOT EXISTS sayimlar_silme_yasak BEFORE DELETE ON sayimlar
BEGIN SELECT RAISE(ABORT, 'sayım kayıtları silinemez'); END;
CREATE TRIGGER IF NOT EXISTS sayimlar_kapali_degismez BEFORE UPDATE ON sayimlar
WHEN OLD.durum='kapali'
BEGIN SELECT RAISE(ABORT, 'kapanmış sayım değiştirilemez'); END;
CREATE TRIGGER IF NOT EXISTS sayim_satir_silme_yasak BEFORE DELETE ON sayim_satirlari
BEGIN SELECT RAISE(ABORT, 'sayım satırları silinemez'); END;
CREATE TRIGGER IF NOT EXISTS sayim_satir_kapali_guncelleme BEFORE UPDATE ON sayim_satirlari
WHEN (SELECT durum FROM sayimlar WHERE id=OLD.sayim_id)='kapali'
BEGIN SELECT RAISE(ABORT, 'kapanmış sayım değiştirilemez'); END;
CREATE TRIGGER IF NOT EXISTS sayim_satir_kapali_ekleme BEFORE INSERT ON sayim_satirlari
WHEN (SELECT durum FROM sayimlar WHERE id=NEW.sayim_id)='kapali'
BEGIN SELECT RAISE(ABORT, 'kapanmış sayıma satır eklenemez'); END;
"""


class SayimHatasi(Exception):
    pass


def sema(con):
    con.executescript(SEMA)


def _simdi():
    return datetime.now().isoformat(timespec="seconds")


def _sayim(con, sid, acik=False):
    s = con.execute("SELECT * FROM sayimlar WHERE id=?", (sid,)).fetchone()
    if not s:
        raise SayimHatasi("Sayım bulunamadı.")
    if acik and s["durum"] != "acik":
        raise SayimHatasi("Sayım kapanmış; değiştirilemez.")
    return s


def baslat(con, sorumlu, tumu=False, yer=None, sergi=None, komisyon=None):
    """Kapsamdaki eserlerin anlık görüntüsünü alır; sayım id'sini döndürür."""
    if not (sorumlu or "").strip():
        raise SayimHatasi("Sorumlu zorunludur.")
    if sum(bool(x) for x in (tumu, yer, sergi)) != 1:
        raise SayimHatasi("Kapsam olarak tam olarak biri verilmeli: --tumu, --yer veya --sergi.")
    if not con.in_transaction:
        con.execute("BEGIN IMMEDIATE")
    if tumu:
        tur, deger, sql, p = "tumu", None, "SELECT * FROM eserler", ()
    elif yer:
        tur, deger = "yer", yer
        sql, p = "SELECT * FROM eserler WHERE bulundugu_yer=? COLLATE NOCASE", (yer,)
    else:
        s = con.execute("SELECT id FROM sergiler WHERE ad=?", (sergi,)).fetchone()
        if not s:
            raise SayimHatasi("Sergi bulunamadı.")
        tur, deger, sql, p = "sergi", sergi, "SELECT * FROM eserler WHERE sergi_id=?", (s["id"],)
    eserler = con.execute(sql, p).fetchall()
    if not eserler:
        raise SayimHatasi("Kapsamda eser yok.")
    sid = con.execute("INSERT INTO sayimlar(baslangic,kapsam_tur,kapsam_deger,sorumlu,komisyon) VALUES(?,?,?,?,?)",
                      (_simdi(), tur, deger, sorumlu, komisyon)).lastrowid
    for e in eserler:
        con.execute("INSERT INTO sayim_satirlari(sayim_id,eser_id,beklenen,beklenen_yer,beklenen_durum) "
                    "VALUES(?,?,?,?,?)", (sid, e["id"], int(e["durum"] in FIZIKSEL), e["bulundugu_yer"], e["durum"]))
    return sid


def isaretle(con, sid, no, kullanici, yer=None, aciklama=None):
    """Eseri 'bulundu' işaretler. Kapsam dışı (beklenmeyen) ama kayıtlı eser fazla olarak eklenir."""
    _sayim(con, sid, acik=True)
    e = con.execute("SELECT * FROM eserler WHERE envanter_no=?", (no,)).fetchone()
    if not e:
        raise SayimHatasi(f"{no}: envanter kaydı yok (kayıtsız eser tutanağa ayrıca yazılmalı).")
    r = con.execute("SELECT * FROM sayim_satirlari WHERE sayim_id=? AND eser_id=?", (sid, e["id"])).fetchone()
    if r and r["bulundu"]:
        raise SayimHatasi(f"{no}: zaten işaretlendi.")
    if r:
        con.execute("UPDATE sayim_satirlari SET bulundu=1, bulunan_yer=?, isaretleme=?, isaretleyen=?, aciklama=? "
                    "WHERE id=?", (yer, _simdi(), kullanici, aciklama, r["id"]))
    else:
        con.execute("INSERT INTO sayim_satirlari(sayim_id,eser_id,beklenen,beklenen_yer,beklenen_durum,bulundu,"
                    "bulunan_yer,isaretleme,isaretleyen,aciklama) VALUES(?,?,0,?,?,1,?,?,?,?)",
                    (sid, e["id"], e["bulundugu_yer"], e["durum"], yer, _simdi(), kullanici, aciklama))


def rapor(con, sid):
    """Mutabakat sonucu: sözlük (bulunan, eksik, fazla, konum_farki, disarida, sayilar)."""
    s = _sayim(con, sid)
    satirlar = con.execute(
        "SELECT l.*, e.envanter_no, e.ad FROM sayim_satirlari l JOIN eserler e ON e.id=l.eser_id "
        "WHERE l.sayim_id=? ORDER BY e.envanter_no", (sid,)).fetchall()
    bulunan = [r for r in satirlar if r["beklenen"] and r["bulundu"]]
    eksik = [r for r in satirlar if r["beklenen"] and not r["bulundu"]]
    fazla = [r for r in satirlar if not r["beklenen"] and r["bulundu"]]
    disarida = [r for r in satirlar if not r["beklenen"] and not r["bulundu"]]
    konum = [r for r in satirlar if r["bulundu"] and r["bulunan_yer"] and
             (r["beklenen_yer"] or "").strip().casefold() != r["bulunan_yer"].strip().casefold()]
    beklenen = len(bulunan) + len(eksik)
    return {"sayim": s, "bulunan": bulunan, "eksik": eksik, "fazla": fazla, "konum_farki": konum,
            "disarida": disarida, "beklenen": beklenen}


def kapat(con, sid):
    s = _sayim(con, sid, acik=True)
    con.execute("UPDATE sayimlar SET durum='kapali', kapanis=? WHERE id=?", (_simdi(), s["id"]))


def tutanak(con, sid):
    r = rapor(con, sid)
    s = r["sayim"]
    kapsam = {"tumu": "tüm envanter", "yer": f"yer: {s['kapsam_deger']}",
              "sergi": f"sergi: {s['kapsam_deger']}"}[s["kapsam_tur"]]
    satirlar = [f"== Sayım #{s['id']} mutabakat tutanağı ({'KAPALI' if s['durum'] == 'kapali' else 'AÇIK, taslak'}) ==",
                f"Başlangıç: {s['baslangic']}   Kapanış: {s['kapanis'] or '-'}",
                f"Kapsam: {kapsam}   Sorumlu: {s['sorumlu']}   Komisyon: {s['komisyon'] or '-'}",
                f"Beklenen: {r['beklenen']}  Bulunan: {len(r['bulunan'])}  Eksik: {len(r['eksik'])}  "
                f"Fazla: {len(r['fazla'])}  Konum farkı: {len(r['konum_farki'])}  "
                f"Dışarıda kayıtlı (sayım dışı): {len(r['disarida'])}"]

    def bolum(baslik, liste, fmt):
        if liste:
            satirlar.append(f"-- {baslik} --")
            satirlar.extend(fmt(x) for x in liste)

    bolum("EKSİK (kayıtta var, sayımda bulunamadı)", r["eksik"],
          lambda x: f"{x['envanter_no']:<10} {x['ad']:<28} kayıtlı yer: {x['beklenen_yer'] or '-'} ({x['beklenen_durum']})")
    bolum("FAZLA / BEKLENMEYEN (kapsam dışı veya kayıtlı durumu fiziki bulunmaya uymuyor)", r["fazla"],
          lambda x: f"{x['envanter_no']:<10} {x['ad']:<28} kayıtlı: {x['beklenen_durum']}, yer: {x['beklenen_yer'] or '-'}")
    bolum("KONUM FARKI", r["konum_farki"],
          lambda x: f"{x['envanter_no']:<10} {x['ad']:<28} kayıtlı: {x['beklenen_yer'] or '-'} -> bulunan: {x['bulunan_yer']}")
    bolum("DIŞARIDA KAYITLI (ödünç/restorasyon; sayım dışı)", r["disarida"],
          lambda x: f"{x['envanter_no']:<10} {x['ad']:<28} durum: {x['beklenen_durum']}")
    satirlar.append("Not: Eksik/fazla işlemleri (kayıttan düşme teklifi, sayım fazlası fişi, değer tespiti, Bakanlığa "
                    "bildirim) kurumun taşınır usullerine göre ayrıca yürütülür; program kayıtları kendiliğinden değiştirmez.")
    return "\n".join(satirlar)


# ---- komut satırı ----

def _cli(fn):
    def sar(a):
        from muze import baglan
        with baglan() as con:
            try:
                fn(con, a)
            except SayimHatasi as h:
                sys.exit(f"Hata: {h}")
    return sar


def _baslat(con, a):
    sid = baslat(con, a.sorumlu, a.tumu, a.yer, a.sergi, a.komisyon)
    n = con.execute("SELECT SUM(beklenen), COUNT(*) FROM sayim_satirlari WHERE sayim_id=?", (sid,)).fetchone()
    print(f"Sayım #{sid} başlatıldı. Beklenen: {n[0]} eser (kapsam toplam {n[1]}; "
          f"{n[1] - n[0]} eser dışarıda kayıtlı).")


def _isaretle(con, a):
    k = hareketler.kullanici_adi(a)
    hatalar = []
    for no in a.no:
        try:
            isaretle(con, a.sayim, no, k, a.yer, a.aciklama)
        except SayimHatasi as h:
            hatalar.append(str(h))
    for h in hatalar:
        print(f"Uyarı: {h}", file=sys.stderr)
    p = con.execute("SELECT SUM(beklenen), SUM(beklenen AND bulundu) FROM sayim_satirlari WHERE sayim_id=?",
                    (a.sayim,)).fetchone()
    print(f"İşaretlendi: {len(a.no) - len(hatalar)}. İlerleme: {p[1] or 0}/{p[0] or 0} beklenen eser bulundu.")
    if hatalar and len(hatalar) == len(a.no):
        sys.exit(1)


def _kapat(con, a):
    kapat(con, a.sayim)
    print(tutanak(con, a.sayim))


def _rapor(con, a):
    _sayim(con, a.sayim)
    print(tutanak(con, a.sayim))


def _listele(con, a):
    for s in con.execute("SELECT * FROM sayimlar ORDER BY id"):
        print(f"#{s['id']:<4} {s['baslangic']}  {s['kapsam_tur']:<6} {s['kapsam_deger'] or '-':<18} "
              f"{s['durum']:<6} sorumlu: {s['sorumlu']}")


def komutlar(sp):
    x = sp.add_parser("sayim-baslat", help="sayım başlat (kapsamın anlık görüntüsünü alır)")
    g = x.add_mutually_exclusive_group(required=True)
    g.add_argument("--tumu", action="store_true"); g.add_argument("--yer", help="bulundugu_yer ile eşleşir")
    g.add_argument("--sergi", help="sergi adı")
    x.add_argument("--sorumlu", required=True); x.add_argument("--komisyon", help="komisyon üyeleri (serbest metin)")
    x.set_defaults(f=_cli(_baslat))
    x = sp.add_parser("sayim-isaretle", help="sayımda bulunan eserleri işaretle (birden çok envanter no verilebilir)")
    x.add_argument("sayim", type=int); x.add_argument("no", nargs="+")
    x.add_argument("--yer", help="fiilen bulunduğu yer (kayıtlıdan farklıysa konum farkı yazılır)")
    x.add_argument("--aciklama"); x.add_argument("--kullanici"); x.set_defaults(f=_cli(_isaretle))
    x = sp.add_parser("sayim-kapat", help="sayımı kapat, mutabakat tutanağını yaz")
    x.add_argument("sayim", type=int); x.set_defaults(f=_cli(_kapat))
    x = sp.add_parser("sayim-rapor", help="mutabakat tutanağı (açık sayımda taslak)")
    x.add_argument("sayim", type=int); x.set_defaults(f=_cli(_rapor))
    x = sp.add_parser("sayim-listele", help="sayımlar"); x.set_defaults(f=_cli(_listele))
