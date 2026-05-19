from __future__ import annotations

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtCore import Qt
from PySide6.QtSvg import QSvgRenderer


def main() -> int:
    app = QGuiApplication(sys.argv)

    source = BASE_DIR / "assets" / "app_icon.svg"
    target = BASE_DIR / "assets" / "app_icon.ico"

    if not source.exists():
        print(f"No existe el SVG fuente: {source}")
        return 1

    renderer = QSvgRenderer(str(source))
    if not renderer.isValid():
        print("No se pudo cargar el SVG para generar el icono.")
        return 1

    image = QImage(256, 256, QImage.Format_ARGB32)
    image.fill(Qt.transparent)

    painter = QPainter(image)
    renderer.render(painter)
    painter.end()

    if not image.save(str(target)):
        print("No se pudo guardar el archivo .ico")
        return 1

    print(f"Icono generado correctamente en: {target}")
    app.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
