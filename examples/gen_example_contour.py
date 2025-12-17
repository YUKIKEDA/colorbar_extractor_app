"""
コンター図サンプル生成スクリプト

様々なタイプのコンター図を生成するためのメインエントリポイント。
Matplotlib, Plotly, Bokehの3つのライブラリに対応し、
カラーマップ、カラーバーの位置・向き、CAEスタイルなど
多様なパターンのコンター図を生成できます。

使用方法:
---------
1. 単一のサンプルを生成:
   python gen_example_contour.py --demo

2. 代表的なパターンを一括生成:
   python gen_example_contour.py --generate representative

3. 全パターンを生成:
   python gen_example_contour.py --generate all

4. 特定の条件で生成:
   python gen_example_contour.py \\
       --library matplotlib \\
       --colormap viridis \\
       --position right \\
       --orientation vertical \\
       --type cae_inner \\
       --shape circle

5. カスタム一括生成:
   python generate_all_contours.py --help

ファイル構成:
------------
- contour_utils.py      : 共通ユーティリティ（データ生成、マスク処理など）
- contour_base_mpl.py   : Matplotlib用ベースモジュール
- contour_base_plotly.py: Plotly用ベースモジュール
- contour_base_bokeh.py : Bokeh用ベースモジュール
- generate_all_contours.py: 一括生成スクリプト
- matplotlib/           : Matplotlibサンプルファイル
- plotly/              : Plotlyサンプルファイル
- bokeh/               : Bokehサンプルファイル

対応カラーマップ:
----------------
viridis, plasma, inferno, magma, cividis, Greys, Purples, Blues, Greens,
Oranges, Reds, YlOrBr, YlOrRd, OrRd, PuRd, RdPu, BuPu, GnBu, PuBu, YlGnBu,
PuBuGn, BuGn, YlGn, binary, gist_yarg, gist_gray, gray, bone, pink, spring,
summer, autumn, winter, cool, Wistia, hot, afmhot, gist_heat, copper, PiYG,
PRGn, BrBG, PuOr, RdGy, RdBu, RdYlBu, RdYlGn, Spectral, coolwarm, bwr,
seismic, berlin, managua, vanimo, twilight, twilight_shifted, hsv, Pastel1,
Pastel2, Paired, Accent, Dark2, Set1, Set2, Set3, tab10, tab20, tab20b,
tab20c, flag, prism, ocean, gist_earth, terrain, gist_stern, gnuplot,
gnuplot2, CMRmap, cubehelix, brg, gist_rainbow, rainbow, jet, turbo,
nipy_spectral, gist_ncar

コンタータイプ:
--------------
- standard  : 標準のコンター図（マスクなし）
- cae_inner : CAEスタイル - 形状内部のみにコンター表示
- cae_outer : CAEスタイル - 形状外部にコンター表示（形状部分は白抜き）

形状プリセット:
--------------
- circle    : 円形
- rectangle : 長方形
- ring      : リング（ドーナツ形）
- bracket   : L字型ブラケット
- gear      : 歯車形状
"""

import argparse
import sys
from pathlib import Path

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from contour_utils import (
    COLORMAPS,
    COLORBAR_POSITIONS,
    COLORBAR_ORIENTATIONS,
    CONTOUR_TYPES,
    SHAPE_PRESETS,
)


def run_demo():
    """デモ用のサンプルコンター図を生成して表示"""
    print("=== コンター図デモ ===\n")
    
    # Matplotlib
    print("1. Matplotlib - viridis, CAE内部（円形）")
    from contour_base_mpl import create_matplotlib_contour
    create_matplotlib_contour(
        colormap='viridis',
        colorbar_position='right',
        colorbar_orientation='vertical',
        contour_type='cae_inner',
        shape='circle',
        show=True,
        save=False
    )
    
    # Plotly
    print("\n2. Plotly - plasma, CAE外部（リング）")
    from contour_base_plotly import create_plotly_contour
    create_plotly_contour(
        colormap='plasma',
        colorbar_position='right',
        colorbar_orientation='vertical',
        contour_type='cae_outer',
        shape='ring',
        show=True,
        save=False
    )
    
    # Bokeh
    print("\n3. Bokeh - inferno, 標準")
    from contour_base_bokeh import create_bokeh_contour
    create_bokeh_contour(
        colormap='inferno',
        colorbar_position='right',
        colorbar_orientation='vertical',
        contour_type='standard',
        show=True,
        save_file=False
    )
    
    print("\nデモ完了！")


def generate_single(
    library: str,
    colormap: str,
    position: str,
    orientation: str,
    contour_type: str,
    shape: str,
    show: bool = True,
    save: bool = True
):
    """単一のコンター図を生成"""
    shape_params = SHAPE_PRESETS.get(shape, {})
    shape_kwargs = {k: v for k, v in shape_params.items() if k != 'shape'}
    
    if library == 'matplotlib':
        from contour_base_mpl import create_matplotlib_contour
        create_matplotlib_contour(
            colormap=colormap,
            colorbar_position=position,
            colorbar_orientation=orientation,
            contour_type=contour_type,
            shape=shape,
            show=show,
            save=save,
            **shape_kwargs
        )
    elif library == 'plotly':
        from contour_base_plotly import create_plotly_contour
        create_plotly_contour(
            colormap=colormap,
            colorbar_position=position,
            colorbar_orientation=orientation,
            contour_type=contour_type,
            shape=shape,
            show=show,
            save=save,
            **shape_kwargs
        )
    elif library == 'bokeh':
        from contour_base_bokeh import create_bokeh_contour
        create_bokeh_contour(
            colormap=colormap,
            colorbar_position=position,
            colorbar_orientation=orientation,
            contour_type=contour_type,
            shape=shape,
            show=show,
            save_file=save,
            **shape_kwargs
        )
    else:
        print(f"Unknown library: {library}")
        return
    
    print(f"\n生成完了: {library} | {colormap} | {position} | {orientation} | {contour_type} | {shape}")


def generate_batch(mode: str):
    """バッチ生成を実行"""
    import subprocess
    
    script_path = Path(__file__).parent / 'generate_all_contours.py'
    
    if mode == 'representative':
        cmd = [sys.executable, str(script_path), '--colormaps', 'representative', '--shapes', 'circle,ring']
    elif mode == 'all':
        cmd = [sys.executable, str(script_path), '--colormaps', 'all', '--shapes', 'all']
    else:
        print(f"Unknown mode: {mode}")
        return
    
    print(f"実行コマンド: {' '.join(cmd)}\n")
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(
        description='コンター図サンプル生成スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python gen_example_contour.py --demo
  python gen_example_contour.py --generate representative
  python gen_example_contour.py -l matplotlib -c jet -p top -o horizontal -t standard
        """
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='デモモード: 各ライブラリのサンプルを1つずつ表示'
    )
    parser.add_argument(
        '--generate', '-g',
        type=str,
        choices=['representative', 'all'],
        help='一括生成モード (representative: 代表的なパターン, all: 全パターン)'
    )
    parser.add_argument(
        '--library', '-l',
        type=str,
        choices=['matplotlib', 'plotly', 'bokeh'],
        default='matplotlib',
        help='使用するライブラリ'
    )
    parser.add_argument(
        '--colormap', '-c',
        type=str,
        default='viridis',
        help='カラーマップ名'
    )
    parser.add_argument(
        '--position', '-p',
        type=str,
        choices=COLORBAR_POSITIONS,
        default='right',
        help='カラーバーの位置'
    )
    parser.add_argument(
        '--orientation', '-o',
        type=str,
        choices=COLORBAR_ORIENTATIONS,
        default='vertical',
        help='カラーバーの向き'
    )
    parser.add_argument(
        '--type', '-t',
        type=str,
        choices=CONTOUR_TYPES,
        default='cae_inner',
        help='コンタータイプ'
    )
    parser.add_argument(
        '--shape', '-s',
        type=str,
        choices=list(SHAPE_PRESETS.keys()),
        default='circle',
        help='形状タイプ'
    )
    parser.add_argument(
        '--no-show',
        action='store_true',
        help='表示しない'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='保存しない'
    )
    parser.add_argument(
        '--list-colormaps',
        action='store_true',
        help='利用可能なカラーマップを一覧表示'
    )
    
    args = parser.parse_args()
    
    # カラーマップ一覧表示
    if args.list_colormaps:
        print("利用可能なカラーマップ:")
        print("-" * 40)
        for i, cmap in enumerate(COLORMAPS, 1):
            print(f"  {i:2d}. {cmap}")
        print(f"\n合計: {len(COLORMAPS)} 種類")
        return
    
    # デモモード
    if args.demo:
        run_demo()
        return
    
    # 一括生成モード
    if args.generate:
        generate_batch(args.generate)
        return
    
    # 単一生成モード
    generate_single(
        library=args.library,
        colormap=args.colormap,
        position=args.position,
        orientation=args.orientation,
        contour_type=args.type,
        shape=args.shape,
        show=not args.no_show,
        save=not args.no_save
    )


if __name__ == '__main__':
    main()

