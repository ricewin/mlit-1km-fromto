# MapLibre Migration Investigation

## 概要 (Overview)

FoliumからMapLibreへの移行可能性の調査結果をまとめました。

## 調査結果 (Investigation Results)

### ✅ 移行可能 (Migration is Feasible)

現在のデュアルマップ機能を維持したまま、FoliumからMapLibreに置き換えることができます。

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
import maplibre

# カスタムHTMLを生成してmaplibre-gl-compareライブラリを使用
# maplibre-gl-compareでデュアルマップを実装

html_output = create_dual_map_html(
    gdf_1, gdf_2,
    value_1, value_2,
    colormap_1, colormap_2,
    map_center, zoom_start
)
```

## 機能比較 (Feature Comparison)

| 機能 | Folium | MapLibre | 状態 |
|------|--------|----------|------|
| デュアルマップ | ✅ DualMap plugin | ✅ maplibre-gl-compare | 実装済み |
| GeoJSONレイヤー | ✅ folium.GeoJson | ✅ addSource/addLayer | 実装済み |
| カラーマップ | ✅ branca | ✅ branca | 実装済み |
| ツールチップ | ✅ tooltip | ✅ Popup on hover | 実装済み |
| フルスクリーン | ✅ Fullscreen plugin | ✅ FullscreenControl | 実装済み |
| ナビゲーション | ✅ 自動 | ✅ NavigationControl | 実装済み |
| スケール | ✅ control_scale | ✅ ScaleControl | 実装済み |
| ミニマップ | ✅ MiniMap plugin | ⚠️ 未実装 | 必要に応じて実装可能 |
| カスタムタイル | ✅ tiles param | ✅ raster source | 実装済み |

## 主な変更点 (Key Changes)

### 1. デュアルマップの実装方法

**Folium:**
- `folium.plugins.DualMap`を使用
- 左右のマップが自動的に同期

**MapLibre:**
- カスタムHTMLで`maplibre-gl-compare`ライブラリを使用
- JavaScriptで左右のマップを作成し、Compareクラスで同期

### 2. レンダリング方法

**Folium:**
```python
m = folium.plugins.DualMap(...)
m_html = m.get_root().render()
html(m_html, height=600)
```

**MapLibre:**
```python
html_output = create_dual_map_html(...)
html(html_output, height=600)
```

### 3. スタイリング

**Folium:**
- `style_function`でスタイルを定義
- Pythonでカラーを計算

**MapLibre:**
- GeoJSONのpropertiesにカラー情報を追加
- MapLibreの`['get', 'color']`式で参照

## 利点 (Advantages)

### MapLibreの利点

1. **パフォーマンス**: WebGL使用で大規模データでも高速
2. **軽量**: Foliumより小さいファイルサイズ
3. **モダン**: 最新のマッピング技術を使用
4. **オープンソース**: MapLibre GLは完全なオープンソース
5. **カスタマイズ性**: より柔軟なスタイリングが可能

### Foliumの利点

1. **簡単**: Pythonだけで完結
2. **豊富なプラグイン**: 多くの既存プラグイン
3. **安定性**: 長い開発履歴

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

現在のデュアルマップ機能を完全に維持したまま、FoliumからMapLibreに置き換えることができます。主な機能はすべて実装済みで、パフォーマンスとモダンな技術スタックの利点があります。

ただし、ミニマップ機能は現在未実装です。必要に応じて追加実装が可能です。

## 次のステップ (Next Steps)

1. ✅ MapLibre実装の作成 - 完了
2. ✅ 基本機能のテスト - 完了
3. ⬜ 実データでのテスト
4. ⬜ パフォーマンステスト
5. ⬜ ユーザーフィードバックの収集
6. ⬜ 移行の決定

## 参考資料 (References)

- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js-docs/api/)
- [maplibre-gl-compare](https://github.com/maplibre/maplibre-gl-compare)
- [Folium Documentation](https://python-visualization.github.io/folium/)
- [maplibre Python Package](https://pypi.org/project/maplibre/)
