# Colorbar & Contour Extractor App

コンター図からカラーバーやコンター領域を抽出するGUIツール群です。

## 概要

CAE解析結果やグラフ画像から、カラーバー部分やコンター領域のみを切り出して保存できます。機械学習用のデータセット作成などに活用できます。

## アプリケーション一覧

### 1. カラーバー抽出ツール (`colorbar_extractor_app.py`)

コンター図からカラーバー部分のみを自動検出・抽出します。

**機能:**
- 画像読み込み（PNG, JPG, JPEG, BMP）
- ドラッグ操作でカラーバー周辺を選択
- 彩度ベースの自動検出アルゴリズム
- ピクセル単位の微調整（上下左右のマージン）
- 1x〜10xのズームプレビュー
- PNG/JPG形式で保存

### 2. コンター領域抽出ツール (`contour_extractor_app.py`)

コンター図から指定した領域のみを抽出し、外側を白塗りにします。

**機能:**
- 画像読み込み（PNG, JPG, JPEG, BMP, TIF）
- **矩形選択**: ドラッグで矩形領域を選択
- **フリーハンド選択**: クリックで自由な形状を描画
- 複数領域の追加・削除
- マスク適用でリアルタイムプレビュー
- PNG/JPG/BMP形式で保存

**用途:**
- CAE内部コンター（cae_inner）: フリーハンドで複雑な形状を選択
- CAE外部コンター（cae_outer）: 矩形選択で簡単に領域指定
- 標準コンター: 矩形選択でコンター部分のみを抽出

## インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd colorbar_extractor_app

# 依存パッケージをインストール
pip install -r requirements.txt
```

## 使用方法

### カラーバー抽出ツール

```bash
python src/colorbar_extractor_app.py
```

**操作手順:**
1. 「画像を開く」ボタンで画像を読み込む
2. ドラッグ操作でカラーバー周辺を矩形選択
3. 自動検出された結果が右側パネルにプレビュー表示
4. 必要に応じて境界線調整でマージンを微調整
   - 正の値: 削る（内側に縮小）
   - 負の値: 広げる（外側に拡大）
5. 「現在の状態で保存」ボタンで保存

### コンター領域抽出ツール

```bash
python src/contour_extractor_app.py
```

**操作手順:**
1. 「画像を開く」ボタンで画像を読み込む
2. ツールを選択（矩形 / フリーハンド）
3. 領域を選択
   - **矩形**: ドラッグで矩形を描画
   - **フリーハンド**: クリックで点を追加（ダブルクリックで確定）
4. 「領域を追加」ボタンで領域を確定
5. 必要に応じて複数領域を追加
6. 「マスク適用」ボタンでプレビューを確認
7. 「保存」ボタンで結果を保存

## ファイル構成

```
colorbar_extractor_app/
├── README.md                      # このファイル
├── requirements.txt               # 依存パッケージ
├── src/
│   ├── colorbar_extractor_app.py  # カラーバー抽出ツール
│   └── contour_extractor_app.py   # コンター領域抽出ツール
└── examples/                      # サンプルコンター図生成スクリプト
    ├── README.md                  # examples用の詳細ドキュメント
    ├── gen_example_contour.py
    ├── generate_all_contours.py
    ├── contour_base_mpl.py        # Matplotlib用
    ├── contour_base_plotly.py     # Plotly用
    ├── contour_base_bokeh.py      # Bokeh用
    ├── contour_utils.py           # 共通ユーティリティ
    ├── matplotlib/                # Matplotlibサンプル
    ├── plotly/                    # Plotlyサンプル
    ├── bokeh/                     # Bokehサンプル
    └── output/                    # 生成された画像の出力先
```

## サンプルコンター図の生成

`examples/` ディレクトリには、テスト用のコンター図を生成するスクリプトが含まれています。

### デモ実行

```bash
cd examples
python gen_example_contour.py --demo
```

### 一括生成

```bash
# 代表的なパターンを生成
python gen_example_contour.py --generate representative

# カスタム生成
python generate_all_contours.py --library matplotlib --colormaps viridis,jet --random-offset
```

詳細は `examples/README.md` を参照してください。

## 対応するコンター図タイプ

| 項目 | オプション |
|------|-----------|
| ライブラリ | Matplotlib, Plotly, Bokeh |
| カラーマップ | 83種類（viridis, jet, coolwarm など） |
| カラーバー位置 | 上、下、左、右 |
| カラーバー向き | 水平、垂直 |
| CAEスタイル | 形状内部、形状外部（白抜き）、標準 |

## 依存パッケージ

- Python 3.8+
- tkinter
- Pillow
- OpenCV (opencv-python)
- NumPy
- Matplotlib
- Plotly
- Bokeh
- Selenium + webdriver-manager（Bokeh PNG出力用）
- Kaleido（Plotly PNG出力用）

## ライセンス

MIT License

## 作者

[Your Name]

