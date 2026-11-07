#!/usr/bin/env python3
"""Efes Müzesi masaüstü saati: dijital saat (SS:DD), hava durumu ve aylık takvim.

Hava durumu Open-Meteo'dan (anahtarsız, ücretsiz) alınır; yalnızca müzenin sabit
koordinatları gönderilir, kişisel veri toplanmaz/saklanmaz (KVKK kapsamında veri yok).
Veri kaynağı: Open-Meteo.com (CC BY 4.0).
"""
import calendar
import json
import os
import random
import threading
import tkinter as tk
import urllib.request
from datetime import datetime

ENLEM, BOYLAM = 37.9396, 27.3410  # Efes / Selçuk, İzmir
HAVA_URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={ENLEM}&longitude={BOYLAM}"
    "&current=temperature_2m,apparent_temperature,relative_humidity_2m,"
    "weather_code,wind_speed_10m&timezone=Europe%2FIstanbul"
)
HAVA_YENILE_MS = 15 * 60 * 1000

AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
         "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
GUN_KISA = ["Pt", "Sa", "Ça", "Pe", "Cu", "Ct", "Pz"]

# WMO hava durumu kodları -> (açıklama, simge)
HAVA_KODLARI = {
    0: ("Açık", "☀"), 1: ("Çoğunlukla açık", "🌤"), 2: ("Parçalı bulutlu", "⛅"),
    3: ("Kapalı", "☁"), 45: ("Sisli", "🌫"), 48: ("Kırağılı sis", "🌫"),
    51: ("Hafif çisenti", "🌦"), 53: ("Çisenti", "🌦"), 55: ("Yoğun çisenti", "🌧"),
    61: ("Hafif yağmur", "🌦"), 63: ("Yağmur", "🌧"), 65: ("Şiddetli yağmur", "🌧"),
    71: ("Hafif kar", "🌨"), 73: ("Kar", "🌨"), 75: ("Yoğun kar", "❄"),
    80: ("Sağanak", "🌦"), 81: ("Sağanak", "🌧"), 82: ("Şiddetli sağanak", "⛈"),
    95: ("Gök gürültülü fırtına", "⛈"), 96: ("Dolulu fırtına", "⛈"), 99: ("Dolulu fırtına", "⛈"),
}

ARKA, KART, YAZI, SOLUK, VURGU, HAFTA_SONU = "#0f172a", "#0b1220", "#f8fafc", "#cbd5e1", "#38bdf8", "#f87171"
GEN, YUK = 400, 700
ARKA_PLAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arka_plan.png")
TAKVIM_Y = 478  # takvim panelinin üst kenarı (büstün yüzü üstte açık kalsın diye altta)


def gokyuzu_ciz(c):
    """Alacakaranlık gökyüzü (üstten alta lacivert → turuncu) ve yıldızlar."""
    ust, alt = (0x1e, 0x1b, 0x4b), (0xf5, 0x9e, 0x0b)
    for y in range(YUK):
        t = (y / YUK) ** 1.6
        renk = "#%02x%02x%02x" % tuple(int(u + (a - u) * t) for u, a in zip(ust, alt))
        c.create_line(0, y, GEN, y, fill=renk)
    rnd = random.Random(7)
    for _ in range(45):
        x, y = rnd.randint(0, GEN), rnd.randint(0, 330)
        c.create_oval(x, y, x + 2, y + 2, fill="#fef9c3", outline="")


def hava_al():
    """Güncel hava durumunu sözlük olarak döndürür; hata olursa istisna fırlatır."""
    with urllib.request.urlopen(HAVA_URL, timeout=10) as r:
        return json.load(r)["current"]


class Saat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Efes Müzesi Saat")
        self.resizable(False, False)
        self.attributes("-topmost", True)  # masaüstünde üstte kalsın; Esc ile kapanır
        self.bind("<Escape>", lambda _e: self.destroy())
        self._nokta = True
        self._takvim_ay = None
        self._hava_sonuc = None  # arka plan iş parçacığı yazar, ana döngü okur (Tk iş parçacığı güvenli değil)

        c = self.c = tk.Canvas(self, width=GEN, height=YUK, highlightthickness=0, bg=ARKA)
        c.pack()
        try:  # Marcus Aurelius büstü fotoğrafı (400x700 PNG, önceden hazırlanmış)
            self._arka = tk.PhotoImage(file=ARKA_PLAN)
            c.create_image(0, 0, image=self._arka, anchor="nw")
        except tk.TclError:  # dosya yoksa gökyüzü zeminiyle devam et
            gokyuzu_ciz(c)

        # yarı saydam paneller (stipple): arkadaki kütüphane hafifçe görünür
        c.create_rectangle(20, 150, GEN - 20, 232, fill=KART, stipple="gray75", outline="")
        c.create_rectangle(20, TAKVIM_Y, GEN - 20, TAKVIM_Y + 216, fill=KART, stipple="gray75", outline="")

        self.t_saat = c.create_text(GEN // 2, 64, font=("DejaVu Sans Mono", 68, "bold"), fill=YAZI)
        self.t_tarih = c.create_text(GEN // 2, 128, font=("DejaVu Sans", 13), fill=SOLUK)
        self.t_simge = c.create_text(58, 191, font=("DejaVu Sans", 32), fill=VURGU, text="…")
        self.t_derece = c.create_text(100, 176, anchor="w", font=("DejaVu Sans", 22, "bold"),
                                      fill=YAZI, text="--°C")
        self.t_durum = c.create_text(100, 205, anchor="w", font=("DejaVu Sans", 9), fill=SOLUK,
                                     text="Hava durumu alınıyor…")
        self._saati_guncelle()
        self._havayi_guncelle()

    def _saati_guncelle(self):
        simdi = datetime.now()
        ayrac = ":" if self._nokta else " "
        self._nokta = not self._nokta
        self.c.itemconfig(self.t_saat, text=f"{simdi:%H}{ayrac}{simdi:%M}")
        self.c.itemconfig(self.t_tarih, text=(
            f"{simdi.day} {AYLAR[simdi.month - 1]} {simdi.year}, {GUNLER[simdi.weekday()]}"))
        anahtar = (simdi.year, simdi.month, simdi.day)
        if anahtar != self._takvim_ay:  # yalnızca gün değişince yeniden çiz
            self._takvim_ay = anahtar
            self._takvimi_ciz(simdi)
        if self._hava_sonuc:
            self._havayi_goster(*self._hava_sonuc)
            self._hava_sonuc = None
        self.after(500, self._saati_guncelle)

    def _takvimi_ciz(self, simdi):
        c = self.c
        c.delete("takvim")
        c.create_text(GEN // 2, TAKVIM_Y + 20, text=f"{AYLAR[simdi.month - 1]} {simdi.year}", tags="takvim",
                      font=("DejaVu Sans", 13, "bold"), fill=YAZI)
        adim, sol = 51, 20 + 51 // 2 - 3
        for i, g in enumerate(GUN_KISA):
            c.create_text(sol + i * adim, TAKVIM_Y + 44, text=g, tags="takvim", font=("DejaVu Sans", 10, "bold"),
                          fill=HAFTA_SONU if i >= 5 else SOLUK)
        for r, hafta in enumerate(calendar.Calendar(firstweekday=0).monthdayscalendar(
                simdi.year, simdi.month)):
            for k, gun in enumerate(hafta):
                if gun == 0:
                    continue
                x, y, bugun = sol + k * adim, TAKVIM_Y + 70 + r * 24, gun == simdi.day
                if bugun:  # bugün vurgulu, hafta sonları kırmızı
                    c.create_oval(x - 13, y - 11, x + 13, y + 11, fill=VURGU, outline="", tags="takvim")
                c.create_text(x, y, text=str(gun), tags="takvim",
                              font=("DejaVu Sans", 11, "bold" if bugun else "normal"),
                              fill=ARKA if bugun else (HAFTA_SONU if k >= 5 else YAZI))

    def _havayi_guncelle(self):
        threading.Thread(target=self._hava_getir, daemon=True).start()
        self.after(HAVA_YENILE_MS, self._havayi_guncelle)

    def _hava_getir(self):
        try:
            veri = hava_al()
            aciklama, simge = HAVA_KODLARI.get(veri["weather_code"], ("Bilinmiyor", "?"))
            derece = f"{veri['temperature_2m']:.0f}°C"
            ayrinti = (f"Efes · {aciklama}\nHissedilen {veri['apparent_temperature']:.0f}°C · "
                       f"Nem %{veri['relative_humidity_2m']:.0f} · Rüzgâr {veri['wind_speed_10m']:.0f} km/s")
        except Exception:  # ağ yok / servis hatası: arayüzü bozma, sonraki turda tekrar dene
            simge, derece, ayrinti = "⚠", "--°C", "Hava durumu alınamadı"
        self._hava_sonuc = (simge, derece, ayrinti)

    def _havayi_goster(self, simge, derece, ayrinti):
        self.c.itemconfig(self.t_simge, text=simge)
        self.c.itemconfig(self.t_derece, text=derece)
        self.c.itemconfig(self.t_durum, text=ayrinti)


if __name__ == "__main__":
    Saat().mainloop()
