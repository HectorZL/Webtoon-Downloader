<br />
<p align="center">
  <h2 align="center">Webtoon Downloader</h2>
  <p align="center">
    Un descargador premium rápido con GUI y CLI para capítulos de Webtoons. \u26a1\ud83d\udcda
    <br />
    <br />
    <a href="https://github.com/Zehina/Webtoon-Downloader/issues">Reportar Error</a>
    \u00b7
    <a href="https://github.com/Zehina/Webtoon-Downloader/issues">Solicitar Funci\u00f3n</a>
    \u00b7
    <a href="https://zehina.github.io/Webtoon-Downloader/">Ver Documentaci\u00f3n</a>
  </p>
</p>

[![Release](https://img.shields.io/github/v/release/Zehina/webtoon-downloader)](https://github.com/Zehina/Webtoon-Downloader/releases)
[![Build status](https://img.shields.io/github/actions/workflow/status/Zehina/webtoon-downloader/main.yml?branch=master)](https://github.com/Zehina/webtoon-downloader/actions/workflows/main.yml?query=branch%3Amaster)
[![Commit activity](https://img.shields.io/github/commit-activity/m/Zehina/webtoon-downloader)](https://img.shields.io/github/commit-activity/m/Zehina/webtoon-downloader)
[![License](https://img.shields.io/github/license/Zehina/webtoon-downloader)](https://img.shields.io/github/license/Zehina/webtoon-downloader)

<p align="center">
  <img src="src/gui.png" alt="Webtoon Downloader GUI" width="700">
</p>

## Idioma | Language
[\ud83c\uddec\ud83c\udde7 English](README.md) | **\ud83c\uddea\ud83c\uddf8 Espa\u00f1ol**

## Qu\u00e9 hace \ud83c\udf10

Webtoon Downloader descarga series p\u00fablicas de Webtoons y las guarda como:

- carpetas de im\u00e1genes
- archivos ZIP
- archivos CBZ
- PDFs

Tambi\u00e9n soporta exportaci\u00f3n de metadatos, selecci\u00f3n de calidad de imagen, estrategias de reintento, proxies y descargas as\u00edncronas con reporte de progreso.

Sitio soportado:

- [https://www.webtoons.com/](https://www.webtoons.com/)

## Uso \ud83d\ude80
Requiere Python `3.10+`.

### \u2728 GUI Premium
La forma m\u00e1s f\u00e1cil de usar Webtoon Downloader es a trav\u00e9s de la nueva interfaz gr\u00e1fica. Proporciona una manera amigable de configurar las descargas y seguir el progreso.

**Para ejecutar la GUI:**
1. Aseg\u00farate de tener instalados los requisitos:
   ```bash
   pip install -r requirements.txt  # O usa 'uv sync'
   ```
2. Lanza la aplicaci\u00f3n:
   ```bash
   python gui.py
   ```

### \ud83d\udcbb CLI R\u00e1pido
Para usuarios avanzados, la interfaz de l\u00ednea de comandos ofrece velocidad y automatizaci\u00f3n.

**Instalar CLI:**
```bash
uv tool install webtoon_downloader
# O
pipx install webtoon_downloader
```

**Descargar una serie:**
```bash
webtoon-downloader "https://www.webtoons.com/en/.../list?title_no=..."
```

Comandos \u00fatiles:
```bash
webtoon-downloader [url] --latest
webtoon-downloader [url] --start 10 --end 25
webtoon-downloader [url] --save-as cbz
webtoon-downloader [url] --out ./downloads --separate
webtoon-downloader [url] --export-metadata --export-format json
webtoon-downloader [url] --proxy http://127.0.0.1:7890 --concurrent-pages 5
webtoon-downloader [url] --debug
```

## Limitaciones Conocidas \u26a0\ufe0f

Algunos fallos est\u00e1n fuera del control del proyecto:

- L\u00edmites de tasa de Webtoons y respuestas lentas de CDN
- Cap\u00edtulos de Daily Pass o solo para la aplicaci\u00f3n
- Cambios en el marcado o API del sitio original

## Descargo de Responsabilidad \u26a0\ufe0f

Esta herramienta est\u00e1 destinada \u00fanicamente para uso personal y educativo. Eres responsable de c\u00f3mo la utilices, incluyendo el cumplimiento de los t\u00e9rminos de servicio de los sitios web involucrados.

## Licencia \ud83d\udcc4

Distribuido bajo la Licencia MIT. Consulta [LICENSE](LICENSE).
