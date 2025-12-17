"""
Bokeh コンター図サンプル
- カラーマップ: viridis
- カラーバー位置: 右
- カラーバー向き: 垂直
- タイプ: CAE内部（形状内部にコンター表示）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from contour_base_bokeh import create_bokeh_contour

if __name__ == '__main__':
    create_bokeh_contour(
        colormap='viridis',
        colorbar_position='right',
        colorbar_orientation='vertical',
        contour_type='cae_inner',
        shape='circle',
        radius=2.0,
        data_pattern='stress',
        save_file=True,
        show=True
    )

