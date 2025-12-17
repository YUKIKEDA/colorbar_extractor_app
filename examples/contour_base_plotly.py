"""
Plotly用コンター図生成ベースモジュール
"""

import plotly.graph_objects as go
import numpy as np
from pathlib import Path
from typing import Optional, Literal

from contour_utils import (
    generate_contour_data,
    create_shape_mask,
    apply_mask_to_data,
    get_output_dir,
    generate_filename
)


# Plotlyで使用可能なカラースケールのマッピング
# MatplotlibとPlotlyのカラーマップ名の対応
PLOTLY_COLORSCALE_MAP = {
    'viridis': 'Viridis',
    'plasma': 'Plasma',
    'inferno': 'Inferno',
    'magma': 'Magma',
    'cividis': 'Cividis',
    'Greys': 'Greys',
    'Greens': 'Greens',
    'Blues': 'Blues',
    'Oranges': 'Oranges',
    'Reds': 'Reds',
    'YlOrBr': 'YlOrBr',
    'YlOrRd': 'YlOrRd',
    'OrRd': 'OrRd',
    'PuRd': 'PuRd',
    'RdPu': 'RdPu',
    'BuPu': 'BuPu',
    'GnBu': 'GnBu',
    'PuBu': 'PuBu',
    'YlGnBu': 'YlGnBu',
    'PuBuGn': 'PuBuGn',
    'BuGn': 'BuGn',
    'YlGn': 'YlGn',
    'hot': 'Hot',
    'RdBu': 'RdBu',
    'RdYlBu': 'RdYlBu',
    'RdYlGn': 'RdYlGn',
    'Spectral': 'Spectral',
    'coolwarm': 'RdBu',  # Plotlyにはcoolwarmがないので近いものを使用
    'jet': 'Jet',
    'rainbow': 'Rainbow',
    'hsv': 'HSV',
    'gray': 'Greys',
    'bone': 'gray',
    'pink': 'Picnic',
    'copper': 'Copper',  # 非公式だが動く場合がある
    'terrain': 'Earth',
    'ocean': 'deep',
    'bwr': 'RdBu',
    'seismic': 'RdBu',
    'PiYG': 'PiYG',
    'PRGn': 'PRGn',
    'BrBG': 'BrBG',
    'PuOr': 'PuOr',
    'RdGy': 'RdGy',
}


def get_plotly_colorscale(colormap: str) -> str:
    """MatplotlibのカラーマップをPlotlyのカラースケールに変換"""
    return PLOTLY_COLORSCALE_MAP.get(colormap, 'Viridis')


def create_plotly_contour(
    colormap: str = 'viridis',
    colorbar_position: Literal['top', 'bottom', 'left', 'right'] = 'right',
    colorbar_orientation: Literal['horizontal', 'vertical'] = 'vertical',
    contour_type: Literal['cae_inner', 'cae_outer', 'standard'] = 'standard',
    shape: str = 'circle',
    data_pattern: str = 'stress',
    width: int = 800,
    height: int = 700,
    n_contours: int = 20,
    save: bool = True,
    output_dir: Optional[Path] = None,
    show: bool = False,
    **shape_kwargs
) -> go.Figure:
    """
    Plotlyでコンター図を生成
    
    Args:
        colormap: カラーマップ名（Matplotlib互換名）
        colorbar_position: カラーバーの位置
        colorbar_orientation: カラーバーの向き
        contour_type: コンタータイプ
        shape: 形状タイプ
        data_pattern: データパターン
        width: 図の幅
        height: 図の高さ
        n_contours: コンターレベル数
        save: ファイルに保存するかどうか
        output_dir: 出力ディレクトリ
        show: 表示するかどうか
        **shape_kwargs: 形状固有のパラメータ
    
    Returns:
        Plotly Figure
    """
    # データ生成
    X, Y, Z = generate_contour_data(nx=150, ny=150, pattern=data_pattern)
    
    # マスク処理
    if contour_type != 'standard':
        mask = create_shape_mask(X, Y, shape=shape, **shape_kwargs)
        Z = apply_mask_to_data(Z, mask, contour_type)
    
    # Plotlyのカラースケールに変換
    plotly_colorscale = get_plotly_colorscale(colormap)
    
    # カラーバーの設定
    colorbar_config = {
        'title': 'Value',
        'titleside': 'right' if colorbar_orientation == 'vertical' else 'top',
        'thickness': 20,
        'len': 0.8,
    }
    
    # 位置に応じた設定
    if colorbar_position == 'top':
        colorbar_config.update({
            'orientation': 'h',
            'y': 1.02,
            'yanchor': 'bottom',
            'x': 0.5,
            'xanchor': 'center',
        })
    elif colorbar_position == 'bottom':
        colorbar_config.update({
            'orientation': 'h',
            'y': -0.15,
            'yanchor': 'top',
            'x': 0.5,
            'xanchor': 'center',
        })
    elif colorbar_position == 'left':
        colorbar_config.update({
            'orientation': 'v',
            'x': -0.15,
            'xanchor': 'right',
            'y': 0.5,
            'yanchor': 'middle',
        })
    else:  # right
        colorbar_config.update({
            'orientation': 'v',
            'x': 1.02,
            'xanchor': 'left',
            'y': 0.5,
            'yanchor': 'middle',
        })
    
    # コンター図の作成
    fig = go.Figure()
    
    # 塗りつぶしコンター
    fig.add_trace(go.Contour(
        x=X[0, :],
        y=Y[:, 0],
        z=Z,
        colorscale=plotly_colorscale,
        contours=dict(
            coloring='heatmap',
            showlabels=False,
            start=np.nanmin(Z),
            end=np.nanmax(Z),
            size=(np.nanmax(Z) - np.nanmin(Z)) / n_contours
        ),
        colorbar=colorbar_config,
        line=dict(width=0.5, color='rgba(0,0,0,0.3)'),
        ncontours=n_contours,
    ))
    
    # レイアウト設定
    fig.update_layout(
        title=dict(
            text=f'Plotly Contour | Colormap: {colormap} | Type: {contour_type}',
            x=0.5,
            xanchor='center',
            font=dict(size=14)
        ),
        width=width,
        height=height,
        xaxis=dict(
            title='X',
            scaleanchor='y',
            scaleratio=1,
        ),
        yaxis=dict(
            title='Y',
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=80, r=100, t=80, b=80)
    )
    
    # 保存
    if save:
        if output_dir is None:
            output_dir = get_output_dir()
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
        
        filename = generate_filename(
            'plotly', colormap, colorbar_position,
            colorbar_orientation, contour_type
        )
        filepath = output_dir / filename
        
        # 静的画像として保存
        try:
            fig.write_image(str(filepath), scale=2)
            print(f"Saved: {filepath}")
        except Exception:
            # kaleido がインストールされていない場合はHTMLで保存
            html_path = filepath.with_suffix('.html')
            fig.write_html(str(html_path))
            print(f"Saved as HTML (kaleido not available): {html_path}")
    
    if show:
        fig.show()
    
    return fig


if __name__ == '__main__':
    # テスト実行
    create_plotly_contour(
        colormap='viridis',
        colorbar_position='right',
        colorbar_orientation='vertical',
        contour_type='cae_inner',
        shape='circle',
        show=True
    )

