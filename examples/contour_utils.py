"""
共通ユーティリティモジュール
コンター図生成に使用するデータ生成、形状マスク、設定などを提供
"""

import numpy as np
from pathlib import Path
from typing import Tuple, Optional

# カラーマップのリスト
COLORMAPS = [
    # Perceptually Uniform Sequential
    'viridis', 'plasma', 'inferno', 'magma', 'cividis',
    # Sequential (single hue)
    'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
    # Sequential (multi-hue)
    'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
    'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
    # Sequential (misc)
    'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
    'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
    'hot', 'afmhot', 'gist_heat', 'copper',
    # Diverging
    'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
    'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
    'berlin', 'managua', 'vanimo',
    # Cyclic
    'twilight', 'twilight_shifted', 'hsv',
    # Qualitative
    'Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2',
    'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c',
    # Miscellaneous
    'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
    'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
    'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral', 'gist_ncar'
]

# カラーバーの位置
COLORBAR_POSITIONS = ['top', 'bottom', 'left', 'right']

# カラーバーの向き
COLORBAR_ORIENTATIONS = ['horizontal', 'vertical']

# コンタータイプ
CONTOUR_TYPES = ['cae_inner', 'cae_outer', 'standard']

# ライブラリ
LIBRARIES = ['matplotlib', 'plotly', 'bokeh']


def generate_contour_data(
    nx: int = 100,
    ny: int = 100,
    pattern: str = 'peaks'
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    コンター図用のサンプルデータを生成
    
    Args:
        nx: X方向のグリッド数
        ny: Y方向のグリッド数
        pattern: データパターン ('peaks', 'waves', 'gradient', 'stress')
    
    Returns:
        X, Y, Z のグリッドデータ
    """
    x = np.linspace(-3, 3, nx)
    y = np.linspace(-3, 3, ny)
    X, Y = np.meshgrid(x, y)
    
    if pattern == 'peaks':
        # MATLABのpeaks関数に類似したパターン
        Z = (3 * (1 - X)**2 * np.exp(-X**2 - (Y + 1)**2)
             - 10 * (X/5 - X**3 - Y**5) * np.exp(-X**2 - Y**2)
             - 1/3 * np.exp(-(X + 1)**2 - Y**2))
    elif pattern == 'waves':
        # 波紋パターン
        R = np.sqrt(X**2 + Y**2)
        Z = np.sin(R * 2) * np.exp(-R / 3)
    elif pattern == 'gradient':
        # シンプルなグラデーション
        Z = X + Y
    elif pattern == 'stress':
        # 応力分布に似たパターン（CAE向け）
        Z = np.sin(X) * np.cos(Y) + 0.5 * np.sin(2*X) * np.cos(2*Y)
    else:
        Z = X * np.exp(-X**2 - Y**2)
    
    return X, Y, Z


def generate_random_offset(
    max_offset: float = 1.0,
    seed: Optional[int] = None
) -> Tuple[float, float]:
    """
    ランダムなオフセット値を生成
    
    Args:
        max_offset: 最大オフセット量（上下左右それぞれこの範囲内）
        seed: 乱数シード（再現性のため）
    
    Returns:
        (offset_x, offset_y) のタプル
    """
    if seed is not None:
        np.random.seed(seed)
    
    offset_x = np.random.uniform(-max_offset, max_offset)
    offset_y = np.random.uniform(-max_offset, max_offset)
    
    return offset_x, offset_y


def create_shape_mask(
    X: np.ndarray,
    Y: np.ndarray,
    shape: str = 'circle',
    offset_x: float = 0.0,
    offset_y: float = 0.0,
    **kwargs
) -> np.ndarray:
    """
    形状マスクを作成（CAEコンター用）
    
    Args:
        X, Y: グリッドデータ
        shape: 形状タイプ ('circle', 'rectangle', 'ring', 'bracket', 'gear')
        offset_x: X方向のオフセット量（マスク位置をずらす）
        offset_y: Y方向のオフセット量（マスク位置をずらす）
        **kwargs: 形状固有のパラメータ
    
    Returns:
        マスク配列 (True = 形状内部)
    """
    # オフセットを適用したグリッド座標
    X_offset = X - offset_x
    Y_offset = Y - offset_y
    
    if shape == 'circle':
        radius = kwargs.get('radius', 2.0)
        center_x = kwargs.get('center_x', 0.0)
        center_y = kwargs.get('center_y', 0.0)
        mask = (X_offset - center_x)**2 + (Y_offset - center_y)**2 <= radius**2
        
    elif shape == 'rectangle':
        width = kwargs.get('width', 4.0)
        height = kwargs.get('height', 3.0)
        center_x = kwargs.get('center_x', 0.0)
        center_y = kwargs.get('center_y', 0.0)
        mask = (np.abs(X_offset - center_x) <= width/2) & (np.abs(Y_offset - center_y) <= height/2)
        
    elif shape == 'ring':
        outer_radius = kwargs.get('outer_radius', 2.5)
        inner_radius = kwargs.get('inner_radius', 1.0)
        R = np.sqrt(X_offset**2 + Y_offset**2)
        mask = (R >= inner_radius) & (R <= outer_radius)
        
    elif shape == 'bracket':
        # L字型ブラケット
        mask = ((np.abs(X_offset) <= 2.5) & (Y_offset >= -2.5) & (Y_offset <= -1.0)) | \
               ((X_offset >= -2.5) & (X_offset <= -1.0) & (np.abs(Y_offset) <= 2.5))
               
    elif shape == 'gear':
        # 歯車形状（簡易版）
        R = np.sqrt(X_offset**2 + Y_offset**2)
        theta = np.arctan2(Y_offset, X_offset)
        n_teeth = kwargs.get('n_teeth', 8)
        inner = 1.5
        tooth_depth = 0.5
        modulated_r = inner + tooth_depth * (1 + np.sin(n_teeth * theta)) / 2
        mask = (R <= modulated_r) & (R >= 0.5)
        
    else:
        # デフォルト: 全域
        mask = np.ones_like(X, dtype=bool)
    
    return mask


def apply_mask_to_data(
    Z: np.ndarray,
    mask: np.ndarray,
    contour_type: str = 'cae_inner'
) -> np.ndarray:
    """
    データにマスクを適用
    
    Args:
        Z: 元のデータ
        mask: マスク配列
        contour_type: 'cae_inner' (形状内部にコンター) or 'cae_outer' (形状外部にコンター)
    
    Returns:
        マスク適用後のデータ (NaNで白抜き部分を表現)
    """
    Z_masked = Z.copy().astype(float)
    
    if contour_type == 'cae_inner':
        # 形状内部のみにコンターを表示
        Z_masked[~mask] = np.nan
    elif contour_type == 'cae_outer':
        # 形状外部にコンターを表示（形状部分は白抜き）
        Z_masked[mask] = np.nan
    # 'standard' の場合はマスクを適用しない
    
    return Z_masked


def get_output_dir() -> Path:
    """出力ディレクトリを取得・作成"""
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    return output_dir


def generate_filename(
    library: str,
    colormap: str,
    position: str,
    orientation: str,
    contour_type: str,
    extension: str = 'png'
) -> str:
    """
    ファイル名を生成
    
    Args:
        library: ライブラリ名 (matplotlib -> mpl, plotly, bokeh)
        colormap: カラーマップ名
        position: カラーバーの位置
        orientation: カラーバーの向き (horizontal -> hori, vertical -> vert)
        contour_type: コンタータイプ
        extension: ファイル拡張子
    
    Returns:
        ファイル名
    """
    lib_short = {
        'matplotlib': 'mpl',
        'plotly': 'plotly',
        'bokeh': 'bokeh'
    }.get(library, library)
    
    orient_short = {
        'horizontal': 'hori',
        'vertical': 'vert'
    }.get(orientation, orientation)
    
    return f"{lib_short}_{colormap}_{position}_{orient_short}_{contour_type}.{extension}"


def get_representative_colormaps(n: int = 10) -> list:
    """
    代表的なカラーマップを取得
    
    Args:
        n: 取得するカラーマップ数
    
    Returns:
        カラーマップ名のリスト
    """
    # 各カテゴリから代表的なものを選択
    representative = [
        'viridis',      # Perceptually Uniform
        'plasma',       # Perceptually Uniform
        'jet',          # Classic (よく使われる)
        'hot',          # Sequential
        'coolwarm',     # Diverging
        'RdBu',         # Diverging
        'rainbow',      # Miscellaneous
        'Greys',        # Sequential single
        'terrain',      # Miscellaneous
        'hsv',          # Cyclic
    ]
    return representative[:n]


# 形状プリセット
SHAPE_PRESETS = {
    'circle': {'shape': 'circle', 'radius': 2.0},
    'rectangle': {'shape': 'rectangle', 'width': 4.0, 'height': 3.0},
    'ring': {'shape': 'ring', 'outer_radius': 2.5, 'inner_radius': 1.0},
    'bracket': {'shape': 'bracket'},
    'gear': {'shape': 'gear', 'n_teeth': 8}
}

