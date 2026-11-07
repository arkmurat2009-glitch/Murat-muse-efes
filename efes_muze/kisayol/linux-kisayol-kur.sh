#!/bin/bash
# Linux: masaüstüne ve uygulama menüsüne "Efes Saat" kısayolu ekler.
# Gerekli: python3-tk (sudo apt install python3-tk)
set -e
KOK="$(cd "$(dirname "$0")/.." && pwd)"
MASAUSTU="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
mkdir -p "$MASAUSTU" "$HOME/.local/share/applications"
DOSYA="$MASAUSTU/efes-saat.desktop"
cat > "$DOSYA" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Efes Saat
Comment=Dijital saat, hava durumu ve takvim
Exec=python3 "$KOK/saat.py"
Path=$KOK
Icon=$KOK/arka_plan.png
Terminal=false
Categories=Utility;Clock;
DESKTOP
chmod +x "$DOSYA"
cp "$DOSYA" "$HOME/.local/share/applications/efes-saat.desktop"
command -v gio >/dev/null && gio set "$DOSYA" metadata::trusted true 2>/dev/null || true
echo "Kısayol eklendi: $DOSYA"
