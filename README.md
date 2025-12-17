# Colorbar Extractor App

コンター図からカラーバーを自動検出・抽出するGUIツールです。

## 概要

CAE解析結果やグラフ画像からカラーバー部分のみを切り出して保存できます。自動検出機能とピクセル単位の微調整機能を備えており、正確なカラーバー抽出が可能です。

## 機能

- **画像読み込み**: PNG, JPG, JPEG, BMP形式に対応
- **範囲選択**: ドラッグ操作でカラーバー周辺を大まかに選択
- **自動検出**: 彩度ベースのアルゴリズムでカラーバー領域を自動検出
- **微調整**: 上下左右のマージンをピクセル単位で調整可能
- **ズームプレビュー**: 1x〜10xのズーム機能で境界を確認
- **保存**: PNG/JPG形式で抽出結果を保存

## インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd colorbar_extractor_app

# 依存パッケージをインストール
pip install -r requirements.txt
```

## 使用方法

### アプリケーションの起動

```bash
python src/colorbar_extractor_app.py
```

### 操作手順

1. **「画像を開く」** ボタンをクリックして画像を読み込む
2. **ドラッグ操作** でカラーバー周辺を矩形選択
3. 自動検出された結果が右側パネルにプレビュー表示
4. 必要に応じて **境界線調整** でマージンを微調整
   - 正の値: 削る（内側に縮小）
   - 負の値: 広げる（外側に拡大）
5. **「現在の状態で保存」** ボタンで抽出結果を保存

## ファイル構成

```
colorbar_extractor_app/
├── README.md                 # このファイル
├── requirements.txt          # 依存パッケージ
├── src/
│   └── colorbar_extractor_app.py  # メインアプリケーション
└── examples/                 # サンプルコンター図生成スクリプト
    ├── README.md             # examples用の詳細ドキュメント
    ├── gen_example_contour.py
    ├── generate_all_contours.py
    ├── contour_base_mpl.py   # Matplotlib用
    ├── contour_base_plotly.py # Plotly用
    ├── contour_base_bokeh.py  # Bokeh用
    ├── contour_utils.py      # 共通ユーティリティ
    ├── matplotlib/           # Matplotlibサンプル
    ├── plotly/               # Plotlyサンプル
    ├── bokeh/                # Bokehサンプル
    └── output/               # 生成された画像の出力先
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

