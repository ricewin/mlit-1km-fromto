# mlit-1km-fromto

Open data on human flow (1km mesh, by municipality unit origin)

---

ANNOUNCEMENT: This app uses open data content[^1].  
お知らせ：このアプリはオープンデータのコンテンツを利用しています。

---

[![Zenn](https://img.shields.io/badge/Zenn-pfirsich-turquoise?logo=zenn)](https://zenn.dev/pfirsich)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

## Playground

Made with Streamlit.

### Mapping Libraries

- Current: [Folium](https://python-visualization.github.io/folium/latest/)
- Alternative: [MapLibre](https://maplibre.org/) - See [MAPLIBRE_MIGRATION.md](docs/Investigation_maplibre/MAPLIBRE_MIGRATION.md) for migration investigation results

### Streamlit Tutorial

Getting started: [30 Days of Streamlit](https://30days.streamlit.app/)

### Reference

Apps: [Streamlit](https://www.bing.com/ck/a?!&&p=c725e9c25297ac2c98af541823ce2261704590b8068cf662ac365fded2cb52f6JmltdHM9MTczNTQzMDQwMA&ptn=3&ver=2&hsh=4&fclid=1da6b28f-5a2c-6d60-1353-a6ba5bb56c5e&psq=streamlit&u=a1aHR0cHM6Ly9zdHJlYW1saXQuaW8v&ntb=1)
Maps: [Folium](https://python-visualization.github.io/folium/latest/)
Tiles: [GSI](https://maps.gsi.go.jp/development/ichiran.html)

## Development

### Testing

This project uses pytest for testing. See [tests/README.md](tests/README.md) for detailed testing strategy and documentation.

**Run all tests:**

```bash
pytest
```

**Run with verbose output:**

```bash
pytest -v
```

**Run unit tests only:**

```bash
pytest tests/unit/
```

**Run with coverage:**

```bash
pytest --cov=app --cov-report=html
```

### Installing Dependencies

Using Poetry:

```bash
poetry install
```

Or using pip:

```bash
pip install -r requirements.txt
pip install pytest  # for development
```

[^1]: 出典：[「全国の人流オープンデータ」（国土交通省）](https://www.geospatial.jp/ckan/dataset/mlit-1km-fromto)
