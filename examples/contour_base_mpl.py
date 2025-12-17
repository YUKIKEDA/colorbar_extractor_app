"""
Matplotlib用コンター図生成ベースモジュール
"""

import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional, Tuple, Literal

from contour_utils import (
    generate_contour_data,
    create_shape_mask,
    apply_mask_to_data,
    get_output_dir,
    generate_filename,
    generate_random_offset
)


def create_matplotlib_contour(
    colormap: str = 'viridis',
    colorbar_position: Literal['top', 'bottom', 'left', 'right'] = 'right',
    colorbar_orientation: Literal['horizontal', 'vertical'] = 'vertical',
    contour_type: Literal['cae_inner', 'cae_outer', 'standard'] = 'standard',
    shape: str = 'circle',
    data_pattern: str = 'stress',
    figsize: Tuple[int, int] = (10, 8),
    n_levels: int = 20,
    save: bool = True,
    output_dir: Optional[Path] = None,
    show: bool = False,
    dpi: int = 150,
    random_offset: bool = False,
    max_offset: float = 1.0,
    offset_x: Optional[float] = None,
    offset_y: Optional[float] = None,
    random_seed: Optional[int] = None,
    **shape_kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Matplotlibでコンター図を生成
    
    Args:
        colormap: カラーマップ名
        colorbar_position: カラーバーの位置 ('top', 'bottom', 'left', 'right')
        colorbar_orientation: カラーバーの向き ('horizontal', 'vertical')
        contour_type: コンタータイプ ('cae_inner', 'cae_outer', 'standard')
        shape: 形状タイプ ('circle', 'rectangle', 'ring', 'bracket', 'gear')
        data_pattern: データパターン ('peaks', 'waves', 'gradient', 'stress')
        figsize: 図のサイズ
        n_levels: コンターレベル数
        save: ファイルに保存するかどうか
        output_dir: 出力ディレクトリ
        show: 表示するかどうか
        dpi: 解像度
        random_offset: マスク位置をランダムにずらすかどうか
        max_offset: ランダムオフセットの最大量
        offset_x: X方向の固定オフセット（random_offset=Falseの場合に使用）
        offset_y: Y方向の固定オフセット（random_offset=Falseの場合に使用）
        random_seed: ランダムシード（再現性のため）
        **shape_kwargs: 形状固有のパラメータ
    
    Returns:
        Figure, Axes
    """
    # データ生成
    X, Y, Z = generate_contour_data(nx=150, ny=150, pattern=data_pattern)
    
    # マスク処理
    if contour_type != 'standard':
        # オフセットの決定
        if random_offset:
            off_x, off_y = generate_random_offset(max_offset, random_seed)
        else:
            off_x = offset_x if offset_x is not None else 0.0
            off_y = offset_y if offset_y is not None else 0.0
        
        mask = create_shape_mask(X, Y, shape=shape, offset_x=off_x, offset_y=off_y, **shape_kwargs)
        Z = apply_mask_to_data(Z, mask, contour_type)
    
    # 図の作成
    fig, ax = plt.subplots(figsize=figsize)
    
    # 背景を白に設定
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')
    
    # コンター図を描画
    try:
        contourf = ax.contourf(X, Y, Z, levels=n_levels, cmap=colormap)
        ax.contour(X, Y, Z, levels=n_levels, colors='black', 
                            linewidths=0.3, alpha=0.5)
    except ValueError:
        # カラーマップが存在しない場合はviridisを使用
        print(f"Warning: Colormap '{colormap}' not found. Using 'viridis'.")
        contourf = ax.contourf(X, Y, Z, levels=n_levels, cmap='viridis')
        ax.contour(X, Y, Z, levels=n_levels, colors='black',
                            linewidths=0.3, alpha=0.5)
    
    # カラーバーの設定
    cbar_kwargs = {
        'orientation': colorbar_orientation,
        'shrink': 0.8,
        'aspect': 30 if colorbar_orientation == 'vertical' else 40,
        'pad': 0.08
    }
    
    # 位置に応じた調整
    if colorbar_position == 'top':
        cbar_kwargs['location'] = 'top'
        cbar_kwargs['orientation'] = 'horizontal'
    elif colorbar_position == 'bottom':
        cbar_kwargs['location'] = 'bottom'
        cbar_kwargs['orientation'] = 'horizontal'
    elif colorbar_position == 'left':
        cbar_kwargs['location'] = 'left'
        cbar_kwargs['orientation'] = 'vertical'
    elif colorbar_position == 'right':
        cbar_kwargs['location'] = 'right'
        cbar_kwargs['orientation'] = 'vertical'
    
    cbar = fig.colorbar(contourf, ax=ax, **cbar_kwargs)
    cbar.set_label('Value', fontsize=12)
    
    # 軸の設定
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.set_aspect('equal')
    
    # タイトル
    title_parts = [
        'Matplotlib Contour',
        f'Colormap: {colormap}',
        f'Type: {contour_type}'
    ]
    ax.set_title(' | '.join(title_parts), fontsize=10)
    
    plt.tight_layout()
    
    # 保存
    if save:
        if output_dir is None:
            output_dir = get_output_dir()
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
        
        filename = generate_filename(
            'matplotlib', colormap, colorbar_position,
            colorbar_orientation, contour_type
        )
        filepath = output_dir / filename
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"Saved: {filepath}")
    
    if show:
        plt.show()
    else:
        plt.close(fig)
    
    return fig, ax


def create_matplotlib_contour_filled(
    colormap: str = 'viridis',
    colorbar_position: Literal['top', 'bottom', 'left', 'right'] = 'right',
    colorbar_orientation: Literal['horizontal', 'vertical'] = 'vertical',
    contour_type: Literal['cae_inner', 'cae_outer', 'standard'] = 'standard',
    shape: str = 'circle',
    data_pattern: str = 'stress',
    figsize: Tuple[int, int] = (10, 8),
    n_levels: int = 20,
    save: bool = True,
    output_dir: Optional[Path] = None,
    show: bool = False,
    dpi: int = 150,
    show_contour_lines: bool = True,
    **shape_kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Matplotlibで塗りつぶしコンター図を生成（コンター線あり/なし選択可能）
    """
    return create_matplotlib_contour(
        colormap=colormap,
        colorbar_position=colorbar_position,
        colorbar_orientation=colorbar_orientation,
        contour_type=contour_type,
        shape=shape,
        data_pattern=data_pattern,
        figsize=figsize,
        n_levels=n_levels,
        save=save,
        output_dir=output_dir,
        show=show,
        dpi=dpi,
        **shape_kwargs
    )


if __name__ == '__main__':
    # テスト実行
    create_matplotlib_contour(
        colormap='viridis',
        colorbar_position='right',
        colorbar_orientation='vertical',
        contour_type='cae_inner',
        shape='circle',
        show=True
    )

