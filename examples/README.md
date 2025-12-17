# コンター図サンプル生成スクリプト

様々なタイプのコンター図を生成するためのスクリプト集です。
Matplotlib、Plotly、Bokehの3つのライブラリに対応し、多様なパターンのコンター図画像を生成できます。

## セットアップ

```bash
# 必要なパッケージのインストール
pip install -r requirements.txt
```

## ファイル構成

```
examples/
├── contour_utils.py           # 共通ユーティリティ（データ生成、マスク処理など）
├── contour_base_mpl.py        # Matplotlib用ベースモジュール
├── contour_base_plotly.py     # Plotly用ベースモジュール
├── contour_base_bokeh.py      # Bokeh用ベースモジュール
├── gen_example_contour.py     # メインエントリポイント
├── generate_all_contours.py   # 全パターン一括生成スクリプト
├── matplotlib/                # Matplotlibサンプルファイル
├── plotly/                    # Plotlyサンプルファイル
└── bokeh/                     # Bokehサンプルファイル
```

## 使用方法

### 1. デモモード

各ライブラリのサンプルを1つずつ表示します：

```bash
python gen_example_contour.py --demo
```

### 2. 単一のコンター図を生成

特定の条件でコンター図を1つ生成します：

```bash
python gen_example_contour.py \
    --library matplotlib \
    --colormap viridis \
    --position right \
    --orientation vertical \
    --type cae_inner \
    --shape circle
```

**短縮オプション版：**

```bash
python gen_example_contour.py -l matplotlib -c jet -p top -o horizontal -t standard -s circle
```

### 3. 代表的なパターンを一括生成

代表的なカラーマップ（10種類）と形状（circle, ring）の組み合わせを生成：

```bash
python gen_example_contour.py --generate representative
```

### 4. 全パターンを一括生成

全てのカラーマップ・位置・向き・タイプ・形状の組み合わせを生成：

```bash
python gen_example_contour.py --generate all
```

### 5. カスタム一括生成

`generate_all_contours.py` を使用して、より細かい条件指定が可能です：

```bash
# Matplotlibで特定のカラーマップのみ生成
python generate_all_contours.py --library matplotlib --colormaps viridis,plasma,jet

# 全ライブラリで右側カラーバーのみ生成
python generate_all_contours.py --library all --positions right

# CAE内部タイプのみ生成
python generate_all_contours.py --types cae_inner --shapes circle,ring

# 出力先を指定
python generate_all_contours.py --output ./my_output
```

### 6. 個別サンプルファイルを実行

各パターンのサンプルファイルを直接実行できます：

```bash
# Matplotlib
python matplotlib/mpl_viridis_right_vert_cae_inner.py

# Plotly
python plotly/plotly_plasma_left_vert_cae_outer.py

# Bokeh
python bokeh/bokeh_inferno_top_hori_standard.py
```

### 7. 利用可能なカラーマップを一覧表示

```bash
python gen_example_contour.py --list-colormaps
```

## オプション一覧

### gen_example_contour.py

| オプション | 短縮形 | 説明 | デフォルト |
|-----------|-------|------|-----------|
| `--demo` | - | デモモード | - |
| `--generate` | `-g` | 一括生成モード (representative/all) | - |
| `--library` | `-l` | ライブラリ (matplotlib/plotly/bokeh) | matplotlib |
| `--colormap` | `-c` | カラーマップ名 | viridis |
| `--position` | `-p` | カラーバー位置 (top/bottom/left/right) | right |
| `--orientation` | `-o` | カラーバー向き (horizontal/vertical) | vertical |
| `--type` | `-t` | コンタータイプ | cae_inner |
| `--shape` | `-s` | 形状タイプ | circle |
| `--no-show` | - | 画面に表示しない | False |
| `--no-save` | - | ファイルに保存しない | False |
| `--list-colormaps` | - | カラーマップ一覧表示 | - |

### generate_all_contours.py

| オプション | 短縮形 | 説明 | デフォルト |
|-----------|-------|------|-----------|
| `--library` | `-l` | ライブラリ (all/matplotlib/plotly/bokeh) | all |
| `--colormaps` | `-c` | カラーマップ (all/representative/カンマ区切り) | representative |
| `--positions` | `-p` | カラーバー位置 (all/カンマ区切り) | all |
| `--orientations` | `-o` | カラーバー向き (all/カンマ区切り) | all |
| `--types` | `-t` | コンタータイプ (all/カンマ区切り) | all |
| `--shapes` | `-s` | 形状タイプ (all/カンマ区切り) | circle |
| `--output` | `-O` | 出力ディレクトリ | ./output |

## 対応パターン

### ライブラリ

| ライブラリ | 説明 |
|-----------|------|
| **Matplotlib** | 最も一般的なPythonグラフライブラリ。高品質なPNG出力 |
| **Plotly** | インタラクティブなグラフライブラリ。PNG/HTML出力 |
| **Bokeh** | Webベースのインタラクティブ可視化。PNG/HTML出力 |

### カラーマップ（83種類）

**Perceptually Uniform Sequential:**
- viridis, plasma, inferno, magma, cividis

**Sequential (single hue):**
- Greys, Purples, Blues, Greens, Oranges, Reds

**Sequential (multi-hue):**
- YlOrBr, YlOrRd, OrRd, PuRd, RdPu, BuPu, GnBu, PuBu, YlGnBu, PuBuGn, BuGn, YlGn

**Diverging:**
- PiYG, PRGn, BrBG, PuOr, RdGy, RdBu, RdYlBu, RdYlGn, Spectral, coolwarm, bwr, seismic

**Miscellaneous:**
- jet, turbo, rainbow, terrain, ocean, hot, cool など

### カラーバー位置

| 位置 | 説明 |
|-----|------|
| `top` | 上部 |
| `bottom` | 下部 |
| `left` | 左側 |
| `right` | 右側 |

### カラーバー向き

| 向き | 説明 |
|-----|------|
| `horizontal` | 水平 |
| `vertical` | 垂直 |

### コンタータイプ

| タイプ | 説明 |
|-------|------|
| `standard` | 通常のコンター図（マスクなし） |
| `cae_inner` | CAEスタイル - 形状**内部**のみにコンター表示 |
| `cae_outer` | CAEスタイル - 形状**外部**にコンター表示（形状部分は白抜き） |

### 形状プリセット

| 形状 | 説明 |
|-----|------|
| `circle` | 円形 |
| `rectangle` | 長方形 |
| `ring` | リング（ドーナツ形） |
| `bracket` | L字型ブラケット |
| `gear` | 歯車形状 |

## ファイル名の命名規則

生成されるファイル名は以下の形式です：

```
{lib}_{colormap}_{position}_{orientation}_{type}.png
```

**例：**
- `mpl_viridis_right_vert_cae_inner.png`
- `plotly_plasma_left_hori_cae_outer.png`
- `bokeh_jet_top_hori_standard.png`

**略称：**
| 項目 | 略称 |
|-----|------|
| matplotlib | mpl |
| horizontal | hori |
| vertical | vert |

## 出力先

デフォルトでは `examples/output/` ディレクトリに保存されます。
`--output` オプションで変更可能です。

## 注意事項

- **Plotly**: PNG出力には `kaleido` パッケージが必要です。未インストールの場合はHTML形式で保存されます。
- **Bokeh**: PNG出力には `selenium` と Chromeドライバーが必要です。未インストールの場合はHTML形式で保存されます。
- 全パターン生成（約83カラーマップ × 4位置 × 2向き × 3タイプ × 5形状 × 3ライブラリ）は非常に多くのファイルを生成します。代表的なパターンから始めることをお勧めします。

## ライセンス

このプロジェクトのライセンスに従います。

