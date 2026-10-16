#!/usr/bin/env python3
"""Efes Müzesi masaüstü saati: dijital saat (SS:DD), hava durumu ve aylık takvim.

Hava durumu Open-Meteo'dan (anahtarsız, ücretsiz) alınır; yalnızca müzenin sabit
koordinatları gönderilir, kişisel veri toplanmaz/saklanmaz (KVKK kapsamında veri yok).
Veri kaynağı: Open-Meteo.com (CC BY 4.0).
"""
import calendar
import json
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

ARKA, KART, YAZI, SOLUK, VURGU, HAFTA_SONU = "#0f172a", "#1e293b", "#f8fafc", "#94a3b8", "#38bdf8", "#f87171"


def hava_al():
    """Güncel hava durumunu sözlük olarak döndürür; hata olursa istisna fırlatır."""
    with urllib.request.urlopen(HAVA_URL, timeout=10) as r:
        return json.load(r)["current"]


class Saat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Efes Müzesi Saat")
        self.configure(bg=ARKA)
        self.geometry("380x520")
        self.minsize(340, 480)
        self.attributes("-topmost", True)  # masaüstünde üstte kalsın; Esc ile kapanır
        self.bind("<Escape>", lambda _e: self.destroy())
        self._nokta = True
        self._takvim_ay = None
        self._hava_sonuc = None  # arka plan iş parçacığı yazar, ana döngü okur (Tk iş parçacığı güvenli değil)

        self.lbl_saat = tk.Label(self, font=("DejaVu Sans Mono", 64, "bold"), fg=YAZI, bg=ARKA)
        self.lbl_saat.pack(pady=(24, 0))
        self.lbl_tarih = tk.Label(self, font=("DejaVu Sans", 13), fg=SOLUK, bg=ARKA)
        self.lbl_tarih.pack()

        hava = tk.Frame(self, bg=KART)
        hava.pack(fill="x", padx=20, pady=18, ipady=8)
        self.lbl_simge = tk.Label(hava, font=("DejaVu Sans", 34), fg=VURGU, bg=KART)
        self.lbl_simge.pack(side="left", padx=(16, 8))
        yan = tk.Frame(hava, bg=KART)
        yan.pack(side="left", fill="x", expand=True)
        self.lbl_derece = tk.Label(yan, text="--°C", font=("DejaVu Sans", 22, "bold"),
                                   fg=YAZI, bg=KART, anchor="w")
        self.lbl_derece.pack(fill="x")
        self.lbl_durum = tk.Label(yan, text="Hava durumu alınıyor…", font=("DejaVu Sans", 10),
                                  fg=SOLUK, bg=KART, anchor="w", justify="left")
        self.lbl_durum.pack(fill="x")

        self.takvim = tk.Frame(self, bg=KART)
        self.takvim.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self._saati_guncelle()
        self._havayi_guncelle()

    def _saati_guncelle(self):
        simdi = datetime.now()
        ayrac = ":" if self._nokta else " "
        self._nokta = not self._nokta
        self.lbl_saat.config(text=f"{simdi:%H}{ayrac}{simdi:%M}")
        self.lbl_tarih.config(
            text=f"{simdi.day} {AYLAR[simdi.month - 1]} {simdi.year}, {GUNLER[simdi.weekday()]}")
        anahtar = (simdi.year, simdi.month, simdi.day)
        if anahtar != self._takvim_ay:  # yalnızca gün değişince yeniden çiz
            self._takvim_ay = anahtar
            self._takvimi_ciz(simdi)
        if self._hava_sonuc:
            self._havayi_goster(*self._hava_sonuc)
            self._hava_sonuc = None
        self.after(500, self._saati_guncelle)

    def _takvimi_ciz(self, simdi):
        for w in self.takvim.winfo_children():
            w.destroy()
        tk.Label(self.takvim, text=f"{AYLAR[simdi.month - 1]} {simdi.year}",
                 font=("DejaVu Sans", 13, "bold"), fg=YAZI, bg=KART).grid(
            row=0, column=0, columnspan=7, pady=(10, 6))
        for i, g in enumerate(GUN_KISA):
            tk.Label(self.takvim, text=g, font=("DejaVu Sans", 10, "bold"),
                     fg=HAFTA_SONU if i >= 5 else SOLUK, bg=KART).grid(row=1, column=i, sticky="nsew")
        for r, hafta in enumerate(calendar.Calendar(firstweekday=0).monthdayscalendar(
                simdi.year, simdi.month), start=2):
            for c, gun in enumerate(hafta):
                if gun == 0:
                    continue
                # bugün vurgulu, hafta sonları kırmızı
                bugun = gun == simdi.day
                tk.Label(self.takvim, text=str(gun), font=("DejaVu Sans", 11, "bold" if bugun else "normal"),
                         fg=ARKA if bugun else (HAFTA_SONU if c >= 5 else YAZI),
                         bg=VURGU if bugun else KART, width=3).grid(row=r, column=c, padx=1, pady=2)
        for c in range(7):
            self.takvim.columnconfigure(c, weight=1)

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
        self.lbl_simge.config(text=simge)
        self.lbl_derece.config(text=derece)
        self.lbl_durum.config(text=ayrinti)


if __name__ == "__main__":
    Saat().mainloop()
