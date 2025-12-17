"""
Bokeh用コンター図生成ベースモジュール

PNG出力には以下の依存関係が必要です：
- selenium
- webdriver-manager (推奨) または chromedriver-binary

インストール方法:
    pip install selenium webdriver-manager

webdriver-managerを使用すると、Chromeのバージョンに合った
chromedriverを自動的にダウンロードして使用します。
"""

import numpy as np
from pathlib import Path
from typing import Optional, Literal

from bokeh.plotting import figure, save, show as bokeh_show
from bokeh.models import ColorBar, LinearColorMapper, BasicTicker
from bokeh.io import export_png, output_file
from bokeh.palettes import (
    Viridis256, Plasma256, Inferno256, Magma256, Cividis256,
    Greys256, Blues256, Greens256, Oranges256, Reds256, Purples256,
    RdBu11, RdYlBu11, RdYlGn11, Spectral11, PiYG11, PRGn11, BrBG11, PuOr11, RdGy11,
    Turbo256
)

from contour_utils import (
    generate_contour_data,
    create_shape_mask,
    apply_mask_to_data,
    get_output_dir,
    generate_filename,
    generate_random_offset
)


def _setup_chrome_driver():
    """ChromeドライバーをセットアップしてWebDriverを返す"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception:
        return None


# グローバルなWebDriverインスタンス（再利用のため）
_webdriver = None


def _get_webdriver():
    """WebDriverを取得（シングルトン）"""
    global _webdriver
    if _webdriver is None:
        _webdriver = _setup_chrome_driver()
    return _webdriver


# Bokehで使用可能なパレットのマッピング
def get_bokeh_palette(colormap: str, n_colors: int = 256):
    """MatplotlibのカラーマップをBokehのパレットに変換"""
    palette_map = {
        'viridis': Viridis256,
        'plasma': Plasma256,
        'inferno': Inferno256,
        'magma': Magma256,
        'cividis': Cividis256,
        'Greys': Greys256,
        'Blues': Blues256,
        'Greens': Greens256,
        'Oranges': Oranges256,
        'Reds': Reds256,
        'Purples': Purples256,
        'turbo': Turbo256,
        # Divergingパレット（サイズ固定）
        'RdBu': RdBu11,
        'RdYlBu': RdYlBu11,
        'RdYlGn': RdYlGn11,
        'Spectral': Spectral11,
        'PiYG': PiYG11,
        'PRGn': PRGn11,
        'BrBG': BrBG11,
        'PuOr': PuOr11,
        'RdGy': RdGy11,
    }
    
    palette = palette_map.get(colormap, Viridis256)
    
    # パレットのサイズを調整（必要に応じて）
    if isinstance(palette, tuple):
        palette = list(palette)
    
    return palette


def create_bokeh_contour(
    colormap: str = 'viridis',
    colorbar_position: Literal['top', 'bottom', 'left', 'right'] = 'right',
    colorbar_orientation: Literal['horizontal', 'vertical'] = 'vertical',
    contour_type: Literal['cae_inner', 'cae_outer', 'standard'] = 'standard',
    shape: str = 'circle',
    data_pattern: str = 'stress',
    width: int = 800,
    height: int = 700,
    n_levels: int = 20,
    save_file: bool = True,
    output_dir: Optional[Path] = None,
    show: bool = False,
    random_offset: bool = False,
    max_offset: float = 1.0,
    offset_x: Optional[float] = None,
    offset_y: Optional[float] = None,
    random_seed: Optional[int] = None,
    **shape_kwargs
):
    """
    Bokehでコンター図を生成
    
    Bokehは真のコンター図をサポートしていないため、
    ヒートマップ（image）として表示します。
    
    Args:
        colormap: カラーマップ名
        colorbar_position: カラーバーの位置
        colorbar_orientation: カラーバーの向き
        contour_type: コンタータイプ
        shape: 形状タイプ
        data_pattern: データパターン
        width: 図の幅
        height: 図の高さ
        n_levels: カラーレベル数（ヒートマップでは直接使用しない）
        save_file: ファイルに保存するかどうか
        output_dir: 出力ディレクトリ
        show: 表示するかどうか
        random_offset: マスク位置をランダムにずらすかどうか
        max_offset: ランダムオフセットの最大量
        offset_x: X方向の固定オフセット（random_offset=Falseの場合に使用）
        offset_y: Y方向の固定オフセット（random_offset=Falseの場合に使用）
        random_seed: ランダムシード（再現性のため）
        **shape_kwargs: 形状固有のパラメータ
    
    Returns:
        Bokeh figure
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
    
    # データ範囲
    x_min, x_max = X.min(), X.max()
    y_min, y_max = Y.min(), Y.max()
    z_min, z_max = np.nanmin(Z), np.nanmax(Z)
    
    # パレット取得
    palette = get_bokeh_palette(colormap)
    
    # カラーマッパー
    color_mapper = LinearColorMapper(
        palette=palette,
        low=z_min,
        high=z_max,
        nan_color='white'  # NaNは白で表示
    )
    
    # 図の作成
    title = f'Bokeh Contour | Colormap: {colormap} | Type: {contour_type}'
    p = figure(
        width=width,
        height=height,
        title=title,
        x_axis_label='X',
        y_axis_label='Y',
        x_range=(x_min, x_max),
        y_range=(y_min, y_max),
        match_aspect=True,
        background_fill_color='white'
    )
    
    # ヒートマップとしてデータを描画
    p.image(
        image=[Z],
        x=x_min,
        y=y_min,
        dw=x_max - x_min,
        dh=y_max - y_min,
        color_mapper=color_mapper
    )
    
    # カラーバーの設定
    color_bar = ColorBar(
        color_mapper=color_mapper,
        ticker=BasicTicker(),
        label_standoff=12,
        border_line_color=None,
        title='Value'
    )
    
    # カラーバーの向きと位置
    if colorbar_orientation == 'horizontal':
        color_bar.orientation = 'horizontal'
        color_bar.width = 300
        color_bar.height = 20
    else:
        color_bar.orientation = 'vertical'
        color_bar.width = 20
        color_bar.height = 300
    
    # 位置に応じてカラーバーを追加
    if colorbar_position == 'right':
        p.add_layout(color_bar, 'right')
    elif colorbar_position == 'left':
        p.add_layout(color_bar, 'left')
    elif colorbar_position == 'top':
        color_bar.orientation = 'horizontal'
        color_bar.width = 300
        color_bar.height = 20
        p.add_layout(color_bar, 'above')
    elif colorbar_position == 'bottom':
        color_bar.orientation = 'horizontal'
        color_bar.width = 300
        color_bar.height = 20
        p.add_layout(color_bar, 'below')
    
    # 保存
    if save_file:
        if output_dir is None:
            output_dir = get_output_dir()
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
        
        filename = generate_filename(
            'bokeh', colormap, colorbar_position,
            colorbar_orientation, contour_type
        )
        filepath = output_dir / filename
        
        # PNG保存を試みる（seleniumとwebdriverが必要）
        # 公式ドキュメント: https://docs.bokeh.org/en/latest/docs/user_guide/output/export.html
        png_saved = False
        
        # webdriver-managerを使用してPNG出力を試みる
        try:
            driver = _get_webdriver()
            if driver is not None:
                export_png(p, filename=str(filepath), webdriver=driver)
                print(f"Saved: {filepath}")
                png_saved = True
        except Exception:
            pass
        
        # webdriver-managerが失敗した場合、通常のexport_pngを試みる
        if not png_saved:
            try:
                export_png(p, filename=str(filepath))
                print(f"Saved: {filepath}")
                png_saved = True
            except Exception as e:
                # HTMLで保存（PNG出力に必要なドライバーがない場合）
                html_path = filepath.with_suffix('.html')
                output_file(str(html_path))
                save(p)
                print(f"Saved as HTML (PNG export failed: {e})")
                print("PNG出力には selenium と webdriver-manager が必要です:")
                print("  pip install selenium webdriver-manager")
    
    if show:
        bokeh_show(p)
    
    return p


if __name__ == '__main__':
    # テスト実行
    create_bokeh_contour(
        colormap='viridis',
        colorbar_position='right',
        colorbar_orientation='vertical',
        contour_type='cae_inner',
        shape='circle',
        show=True
    )
