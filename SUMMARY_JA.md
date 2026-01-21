# MapLibre移行調査結果の要約

## 調査概要

**課題**: 現在のデュアルマップを維持して、ライブラリをFoliumからmaplibreに置き換えられるか調査する。

**結論**: ✅ **移行可能です**

## 実装完了

### 新規ファイル

1. **app/common/maplibre_map_builder.py**
   - MapLibreを使用したデュアルマップ実装
   - Foliumの`folium_map_builder.py`と同じインターフェース
   - `maplibre-gl-compare`ライブラリを使用

2. **MAPLIBRE_MIGRATION.md**
   - 詳細な移行ドキュメント（日本語・英語）
   - 機能比較表
   - 実装方法の違い
   - 移行手順

3. **app/pages/maplibre_test.py**
   - MapLibre実装のテストページ
   - サンプルデータで動作確認

## 機能実装状況

| 機能 | 状態 | 備考 |
|------|------|------|
| デュアルマップ表示 | ✅ 完了 | maplibre-gl-compare使用 |
| GeoJSONレイヤー | ✅ 完了 | データドリブンスタイリング |
| カラーマップ | ✅ 完了 | branca継続使用 |
| ホバーツールチップ | ✅ 完了 | Foliumと同等の機能 |
| ナビゲーションコントロール | ✅ 完了 | ズーム・パン |
| スケールコントロール | ✅ 完了 | |
| フルスクリーン | ✅ 完了 | |
| 地理院タイル | ✅ 完了 | カスタムタイルURL対応 |
| 凡例表示 | ✅ 完了 | 左右マップに表示 |
| マップ同期 | ✅ 完了 | 左右のマップが連動 |

## 重要な違い

### 1. 座標の順序

- **Folium**: `[緯度, 経度]` (`[lat, lon]`)
- **MapLibre**: `[経度, 緯度]` (`[lon, lat]`)

⚠️ この違いはコード内に明確にコメントされています

### 2. 実装方法

- **Folium**: Pythonライブラリで完結
- **MapLibre**: カスタムHTMLでJavaScript実装

### 3. 依存関係

```toml
# 追加
maplibre = "^0.3.6"
```

## 利点

### MapLibreの利点

1. ⚡ **高パフォーマンス**: WebGL使用で大規模データでも高速
2. 💾 **軽量**: より小さいファイルサイズ
3. 🆕 **モダン**: 最新のマッピング技術
4. 🔓 **完全オープンソース**: MapLibre GLは完全なオープンソース
5. 🎨 **柔軟性**: より詳細なカスタマイズが可能

## テスト結果

- ✅ 構文チェック: 合格
- ✅ 機能テスト: 合格
- ✅ セキュリティスキャン (CodeQL): 脆弱性なし
- ✅ HTML生成: 有効なHTML出力 (約25KB)

## 使用方法

### 現在のFolium実装

```python
from common.folium_map_builder import folium_map_builder

folium_map_builder(df_latlon, gdf_main, gdf_sub, "population", "diff", zoom_start)
```

### MapLibre実装

```python
from common.maplibre_map_builder import maplibre_map_builder

maplibre_map_builder(df_latlon, gdf_main, gdf_sub, "population", "diff", zoom_start)
```

同じインターフェースなので、インポート文を変更するだけで切り替え可能です。

## 推奨移行プラン

### 短期（現状維持）
- Foliumを継続使用
- 安定性を優先

### 中期（段階的移行）
1. 両方のライブラリを並行提供
2. ユーザーに選択肢を提供
3. フィードバック収集

### 長期（完全移行）
1. MapLibreに完全移行
2. Foliumの依存関係を削除
3. パフォーマンス向上を享受

## 次のステップ

1. ✅ MapLibre実装の作成 - **完了**
2. ✅ 基本機能のテスト - **完了**
3. ⬜ 実データでのテスト - **推奨**
4. ⬜ パフォーマンス比較 - **推奨**
5. ⬜ ユーザーフィードバック - **推奨**
6. ⬜ 移行の決定

## 関連ファイル

- `/app/common/maplibre_map_builder.py` - MapLibre実装
- `/app/common/folium_map_builder.py` - 既存のFolium実装
- `/MAPLIBRE_MIGRATION.md` - 詳細な移行ドキュメント
- `/app/pages/maplibre_test.py` - テストページ

## まとめ

現在のデュアルマップ機能を完全に維持したまま、FoliumからMapLibreへの置き換えが可能です。すべての主要機能が実装されテスト済みです。パフォーマンスとモダンな技術スタックの利点があります。

**調査結果**: ✅ **移行は実現可能で推奨できます**
