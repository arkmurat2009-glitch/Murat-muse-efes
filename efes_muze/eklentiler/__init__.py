"""Eklenti kaydı. Her eklenti modülü şunları sağlayabilir:
  sema(con)       -> geriye dönük uyumlu (IF NOT EXISTS) şema/tetikleyici kurulumu
  komutlar(sp)    -> argparse alt komutlarını ekler
  parametreler(p) -> mevcut alt komutlara ek bağımsız değişken ekler (ad -> parser sözlüğü verilir)
"""
from . import dogrulama, gecis, hareketler

# Sıra önemli: hareketler tablosu, geçiş kuralları kullanılmadan önce kurulmalı.
EKLENTILER = [hareketler, dogrulama, gecis]


def sema_uygula(con):
    for m in EKLENTILER:
        if hasattr(m, "sema"):
            m.sema(con)


def komutlari_ekle(sp):
    for m in EKLENTILER:
        if hasattr(m, "komutlar"):
            m.komutlar(sp)
