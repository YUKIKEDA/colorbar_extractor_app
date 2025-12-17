"""
全パターンのコンター図を一括生成するスクリプト

使用方法:
    python generate_all_contours.py --library all --colormaps all --output ./output
    python generate_all_contours.py --library matplotlib --colormaps viridis,plasma,jet
    python generate_all_contours.py --library plotly --positions right,top --types cae_inner
    python generate_all_contours.py --random-offset --max-offset 1.5  # ランダムオフセット有効
"""

import argparse
import itertools
from pathlib import Path
from typing import List
import time

from contour_utils import (
    COLORMAPS,
    COLORBAR_POSITIONS,
    COLORBAR_ORIENTATIONS,
    CONTOUR_TYPES,
    SHAPE_PRESETS,
    get_representative_colormaps,
    get_output_dir
)


def generate_matplotlib_contours(
    colormaps: List[str],
    positions: List[str],
    orientations: List[str],
    contour_types: List[str],
    shapes: List[str],
    output_dir: Path,
    random_offset: bool = False,
    max_offset: float = 1.0
) -> int:
    """Matplotlibでコンター図を生成"""
    from contour_base_mpl import create_matplotlib_contour
    
    count = 0
    total = len(colormaps) * len(positions) * len(orientations) * len(contour_types) * len(shapes)
    
    for cmap, pos, orient, ctype, shape_name in itertools.product(
        colormaps, positions, orientations, contour_types, shapes
    ):
        count += 1
        print(f"[Matplotlib {count}/{total}] {cmap} | {pos} | {orient} | {ctype} | {shape_name}")
        
        shape_params = SHAPE_PRESETS.get(shape_name, {})
        
        try:
            create_matplotlib_contour(
                colormap=cmap,
                colorbar_position=pos,
                colorbar_orientation=orient,
                contour_type=ctype,
                shape=shape_name,
                output_dir=output_dir / 'matplotlib',
                save=True,
                show=False,
                random_offset=random_offset,
                max_offset=max_offset,
                **{k: v for k, v in shape_params.items() if k != 'shape'}
            )
        except Exception as e:
            print(f"  Error: {e}")
    
    return count


def generate_plotly_contours(
    colormaps: List[str],
    positions: List[str],
    orientations: List[str],
    contour_types: List[str],
    shapes: List[str],
    output_dir: Path,
    random_offset: bool = False,
    max_offset: float = 1.0
) -> int:
    """Plotlyでコンター図を生成"""
    from contour_base_plotly import create_plotly_contour
    
    count = 0
    total = len(colormaps) * len(positions) * len(orientations) * len(contour_types) * len(shapes)
    
    for cmap, pos, orient, ctype, shape_name in itertools.product(
        colormaps, positions, orientations, contour_types, shapes
    ):
        count += 1
        print(f"[Plotly {count}/{total}] {cmap} | {pos} | {orient} | {ctype} | {shape_name}")
        
        shape_params = SHAPE_PRESETS.get(shape_name, {})
        
        try:
            create_plotly_contour(
                colormap=cmap,
                colorbar_position=pos,
                colorbar_orientation=orient,
                contour_type=ctype,
                shape=shape_name,
                output_dir=output_dir / 'plotly',
                save=True,
                show=False,
                random_offset=random_offset,
                max_offset=max_offset,
                **{k: v for k, v in shape_params.items() if k != 'shape'}
            )
        except Exception as e:
            print(f"  Error: {e}")
    
    return count


def generate_bokeh_contours(
    colormaps: List[str],
    positions: List[str],
    orientations: List[str],
    contour_types: List[str],
    shapes: List[str],
    output_dir: Path,
    random_offset: bool = False,
    max_offset: float = 1.0
) -> int:
    """Bokehでコンター図を生成"""
    from contour_base_bokeh import create_bokeh_contour
    
    count = 0
    total = len(colormaps) * len(positions) * len(orientations) * len(contour_types) * len(shapes)
    
    for cmap, pos, orient, ctype, shape_name in itertools.product(
        colormaps, positions, orientations, contour_types, shapes
    ):
        count += 1
        print(f"[Bokeh {count}/{total}] {cmap} | {pos} | {orient} | {ctype} | {shape_name}")
        
        shape_params = SHAPE_PRESETS.get(shape_name, {})
        
        try:
            create_bokeh_contour(
                colormap=cmap,
                colorbar_position=pos,
                colorbar_orientation=orient,
                contour_type=ctype,
                shape=shape_name,
                output_dir=output_dir / 'bokeh',
                save_file=True,
                show=False,
                random_offset=random_offset,
                max_offset=max_offset,
                **{k: v for k, v in shape_params.items() if k != 'shape'}
            )
        except Exception as e:
            print(f"  Error: {e}")
    
    return count


def main():
    parser = argparse.ArgumentParser(description='コンター図を一括生成')
    
    parser.add_argument(
        '--library', '-l',
        type=str,
        default='all',
        help='ライブラリ (matplotlib, plotly, bokeh, all)'
    )
    parser.add_argument(
        '--colormaps', '-c',
        type=str,
        default='representative',
        help='カラーマップ (all, representative, またはカンマ区切りのリスト)'
    )
    parser.add_argument(
        '--positions', '-p',
        type=str,
        default='all',
        help='カラーバー位置 (all, またはカンマ区切りのリスト: top,bottom,left,right)'
    )
    parser.add_argument(
        '--orientations', '-o',
        type=str,
        default='all',
        help='カラーバー向き (all, またはカンマ区切りのリスト: horizontal,vertical)'
    )
    parser.add_argument(
        '--types', '-t',
        type=str,
        default='all',
        help='コンタータイプ (all, またはカンマ区切りのリスト: cae_inner,cae_outer,standard)'
    )
    parser.add_argument(
        '--shapes', '-s',
        type=str,
        default='circle',
        help='形状 (all, またはカンマ区切りのリスト: circle,rectangle,ring,bracket,gear)'
    )
    parser.add_argument(
        '--output', '-O',
        type=str,
        default=None,
        help='出力ディレクトリ'
    )
    parser.add_argument(
        '--random-offset', '-r',
        action='store_true',
        help='マスク位置をランダムにずらす（CAEタイプのみ有効）'
    )
    parser.add_argument(
        '--max-offset', '-m',
        type=float,
        default=1.0,
        help='ランダムオフセットの最大量（デフォルト: 1.0）'
    )
    
    args = parser.parse_args()
    
    # ライブラリの解析
    if args.library == 'all':
        libraries = ['matplotlib', 'plotly', 'bokeh']
    else:
        libraries = [lib.strip() for lib in args.library.split(',')]
    
    # カラーマップの解析
    if args.colormaps == 'all':
        colormaps = COLORMAPS
    elif args.colormaps == 'representative':
        colormaps = get_representative_colormaps(10)
    else:
        colormaps = [c.strip() for c in args.colormaps.split(',')]
    
    # 位置の解析
    if args.positions == 'all':
        positions = COLORBAR_POSITIONS
    else:
        positions = [p.strip() for p in args.positions.split(',')]
    
    # 向きの解析
    if args.orientations == 'all':
        orientations = COLORBAR_ORIENTATIONS
    else:
        orientations = [o.strip() for o in args.orientations.split(',')]
    
    # タイプの解析
    if args.types == 'all':
        contour_types = CONTOUR_TYPES
    else:
        contour_types = [t.strip() for t in args.types.split(',')]
    
    # 形状の解析
    if args.shapes == 'all':
        shapes = list(SHAPE_PRESETS.keys())
    else:
        shapes = [s.strip() for s in args.shapes.split(',')]
    
    # 出力ディレクトリ
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = get_output_dir()
    
    # サブディレクトリ作成
    for lib in libraries:
        (output_dir / lib).mkdir(parents=True, exist_ok=True)
    
    # 生成数の計算
    per_lib = len(colormaps) * len(positions) * len(orientations) * len(contour_types) * len(shapes)
    total = per_lib * len(libraries)
    
    print("\n=== コンター図一括生成 ===")
    print(f"ライブラリ: {libraries}")
    print(f"カラーマップ: {len(colormaps)} 種類")
    print(f"位置: {positions}")
    print(f"向き: {orientations}")
    print(f"タイプ: {contour_types}")
    print(f"形状: {shapes}")
    print(f"ランダムオフセット: {args.random_offset} (最大: {args.max_offset})")
    print(f"合計生成数: {total}")
    print(f"出力先: {output_dir}")
    print("=" * 40 + "\n")
    
    start_time = time.time()
    total_count = 0
    
    # 各ライブラリで生成
    if 'matplotlib' in libraries:
        count = generate_matplotlib_contours(
            colormaps, positions, orientations, contour_types, shapes, output_dir,
            random_offset=args.random_offset, max_offset=args.max_offset
        )
        total_count += count
        print(f"\nMatplotlib: {count} ファイル生成完了\n")
    
    if 'plotly' in libraries:
        count = generate_plotly_contours(
            colormaps, positions, orientations, contour_types, shapes, output_dir,
            random_offset=args.random_offset, max_offset=args.max_offset
        )
        total_count += count
        print(f"\nPlotly: {count} ファイル生成完了\n")
    
    if 'bokeh' in libraries:
        count = generate_bokeh_contours(
            colormaps, positions, orientations, contour_types, shapes, output_dir,
            random_offset=args.random_offset, max_offset=args.max_offset
        )
        total_count += count
        print(f"\nBokeh: {count} ファイル生成完了\n")
    
    elapsed = time.time() - start_time
    print("\n=== 完了 ===")
    print(f"合計: {total_count} ファイル")
    print(f"所要時間: {elapsed:.1f} 秒")
    print(f"出力先: {output_dir}")


if __name__ == '__main__':
    main()

