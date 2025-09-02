#!/usr/bin/env python3
"""
Punto de entrada principal para Webtoon Downloader.

Ejecuta la interfaz gráfica por defecto o la interfaz de línea de comandos.
"""
import sys

def main():
    """Punto de entrada principal."""
    # Si no hay argumentos, ejecutar la interfaz gráfica
    if len(sys.argv) == 1:
        from webtoon_downloader.gui import main as gui_main
        gui_main()
    else:
        # Ejecutar la interfaz de línea de comandos
        from webtoon_downloader.cmd.cli import run
        run()

if __name__ == "__main__":
    main()
