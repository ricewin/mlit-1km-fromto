# MapLibre Migration Investigation

## 概要 (Overview)

FoliumからMapLibreへの移行可能性の調査結果をまとめました。

## 調査結果 (Investigation Results)

### ✅ 移行可能 (Migration is Feasible)

FoliumからMapLibreに置き換えることができます。現在の実装では2つの独立したマップをStreamlitのカラムで並べて表示します。

## 実装比較 (Implementation Comparison)

### Folium実装

```python
# folium_map_builder.py
import folium
import folium.plugins

m = folium.plugins.DualMap(
    location=map_center,
    tiles=map_tile,
    attr=attr,
    zoom_start=zoom_start,
    ...
)

folium.GeoJson(data=row["geometry"], ...).add_to(m.m1)
folium.plugins.Fullscreen().add_to(m)
MiniMap(toggle_display=True, minimized=True).add_to(m.m2)

m_html = m.get_root().render()
```

### MapLibre実装

```python
# maplibre_map_builder.py
from maplibre import Map, MapOptions, Layer, LayerType
from maplibre.sources import GeoJSONSource
from maplibre.streamlit import st_maplibre
import streamlit as st

# 2つの独立したマップを作成
map1 = create_single_map(gdf_1, value_1, colormap_1, map_center, zoom_start)
map2 = create_single_map(gdf_2, value_2, colormap_2, map_center, zoom_start)

# Streamlitのカラムで並べて表示
col1, col2 = st.columns(2)
with col1:
    st_maplibre(map1, height=500)
with col2:
    st_maplibre(map2, height=500)
```

## 機能比較 (Feature Comparison)

| 機能                 | Folium               | MapLibre              | 状態                 |
| -------------------- | -------------------- | --------------------- | -------------------- |
| サイドバイサイド表示 | ✅ DualMap plugin    | ✅ st.columns(2)      | 実装済み             |
| GeoJSONレイヤー      | ✅ folium.GeoJson    | ✅ addSource/addLayer | 実装済み             |
| カラーマップ         | ✅ branca            | ✅ branca             | 実装済み             |
| ツールチップ         | ✅ tooltip           | ✅ add_tooltip()      | 実装済み             |
| ナビゲーション       | ✅ 自動              | ✅ NavigationControl  | 実装済み             |
| スケール             | ✅ control_scale     | ✅ ScaleControl       | 実装済み             |
| カスタムタイル       | ✅ tiles param       | ✅ raster source      | 実装済み             |
| マップ同期           | ✅ 自動同期          | ❌ 未実装             | 独立したマップ       |
| フルスクリーン       | ✅ Fullscreen plugin | ❌ 未実装             | 必要に応じて実装可能 |
| ミニマップ           | ✅ MiniMap plugin    | ❌ 未実装             | 必要に応じて実装可能 |
| 凡例表示             | ✅ colormap.add_to() | ⚠️ キャプションのみ   | st.subheaderで表示   |

## 主な変更点 (Key Changes)

### 1. デュアルマップの実装方法

**Folium:**

- `folium.plugins.DualMap`を使用
- 左右のマップが自動的に同期

**MapLibre:**

- 2つの独立した`Map`インスタンスを作成
- `st.columns(2)`で左右に並べて表示
- マップ同期は未実装（独立して操作可能）

### 2. 座標の順序 (Coordinate Order)

**重要な違い:**

- **Folium**: `[lat, lon]` 順序を使用 (location パラメータ)
- **MapLibre**: `[lon, lat]` 順序を使用 (center パラメータ)

この違いはコード内で明確にコメントされています。

### 3. レンダリング方法

**Folium:**

```python
m = folium.plugins.DualMap(...)
m_html = m.get_root().render()
html(m_html, height=600)
```

**MapLibre:**

```python
map1 = create_single_map(...)
map2 = create_single_map(...)

col1, col2 = st.columns(2)
with col1:
    st_maplibre(map1, height=500)
with col2:
    st_maplibre(map2, height=500)
```

### 4. スタイリング

**Folium:**

- `style_function`でスタイルを定義
- Pythonでカラーを計算

**MapLibre:**

- GeoJSONのpropertiesにカラー情報を追加
- MapLibreの`['get', 'color']`式で参照
- maplibre Python APIを使用してPythonのみで実装

**注意**: 現在の実装ではカラーマップのキャプションがハードコードされています（"滞在人口"と"増減率"）。より汎用的な実装にするには、これらをパラメータとして渡すことを検討してください。

## 利点 (Advantages)

### MapLibreの利点

1. **パフォーマンス**: WebGL使用で大規模データでも高速
2. **軽量**: Foliumより小さいファイルサイズ
3. **モダン**: 最新のマッピング技術を使用
4. **オープンソース**: MapLibre GLは完全なオープンソース
5. **カスタマイズ性**: より柔軟なスタイリングが可能
6. **シンプル**: Python APIのみで実装、カスタムHTMLやJavaScriptは不要

### Foliumの利点

1. **簡単**: Pythonだけで完結
2. **豊富なプラグイン**: 多くの既存プラグイン
3. **安定性**: 長い開発履歴
4. **自動同期**: DualMapで自動的にマップが同期

## 移行手順 (Migration Steps)

### 1. 依存関係の追加

```toml
# pyproject.toml
[tool.poetry.dependencies]
maplibre = "^0.3.6"
```

```txt
# requirements.txt
maplibre >= 0.3.6
```

### 2. コードの変更

```python
# Before (Folium)
from common.folium_map_builder import folium_map_builder

folium_map_builder(df_latlon, gdf_main, gdf_sub, "population", "diff", zoom_start)

# After (MapLibre)
from common.maplibre_map_builder import maplibre_map_builder

maplibre_map_builder(df_latlon, gdf_main, gdf_sub, "population", "diff", zoom_start)
```

### 3. テスト

新しい`maplibre_test.py`ページでテストできます。

## 推奨事項 (Recommendations)

### 短期（現在のまま）

- Foliumを継続使用
- 安定性を優先

### 中期（段階的移行）

1. 両方のライブラリを並行して提供
2. ユーザーに選択肢を提供
3. フィードバックを収集

### 長期（完全移行）

1. MapLibreに完全移行
2. Foliumの依存関係を削除
3. パフォーマンス向上を享受

## テスト方法 (How to Test)

### 1. Streamlitアプリを起動

```bash
streamlit run app/main.py
```

### 2. MapLibreテストページにアクセス

アプリのサイドバーから "maplibre_test" ページを選択

### 3. 既存ページとの比較

- Comparison ページ (Folium使用)
- maplibre_test ページ (MapLibre使用)

を比較して、機能が同等であることを確認

## 実装ファイル (Implementation Files)

- `app/common/folium_map_builder.py` - 既存のFolium実装
- `app/common/maplibre_map_builder.py` - 新しいMapLibre実装
- `app/pages/maplibre_test.py` - MapLibreのテストページ

## 結論 (Conclusion)

✅ **MapLibreへの移行は可能です**

FoliumからMapLibreに置き換えることができます。現在の実装では2つの独立したマップを並べて表示する形式です。主な機能は実装済みですが、マップ同期機能は未実装です。パフォーマンスとモダンな技術スタックの利点があります。

## 次のステップ (Next Steps)

1. ✅ MapLibre実装の作成 - 完了
2. ✅ 基本機能のテスト - 完了
3. ⬜ 実データでのテスト
4. ⬜ パフォーマンステスト
5. ⬜ ユーザーフィードバックの収集
6. ⬜ 必要に応じてマップ同期機能の追加
7. ⬜ 移行の決定

## 参考資料 (References)

- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js-docs/api/)
- [maplibre Python Package](https://pypi.org/project/maplibre/)
- [Folium Documentation](https://python-visualization.github.io/folium/)
