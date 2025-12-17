"""
Bokeh コンター図サンプル
- カラーマップ: plasma
- カラーバー位置: 左
- カラーバー向き: 垂直
- タイプ: CAE外部（形状部分が白抜き）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from contour_base_bokeh import create_bokeh_contour

if __name__ == '__main__':
    create_bokeh_contour(
        colormap='plasma',
        colorbar_position='left',
        colorbar_orientation='vertical',
        contour_type='cae_outer',
        shape='ring',
        outer_radius=2.5,
        inner_radius=1.0,
        data_pattern='stress',
        save_file=True,
        show=True
    )

