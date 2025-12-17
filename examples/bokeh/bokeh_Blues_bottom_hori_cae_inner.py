"""
Bokeh コンター図サンプル
- カラーマップ: Blues
- カラーバー位置: 下
- カラーバー向き: 水平
- タイプ: CAE内部（形状内部にコンター表示）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from contour_base_bokeh import create_bokeh_contour

if __name__ == '__main__':
    create_bokeh_contour(
        colormap='Blues',
        colorbar_position='bottom',
        colorbar_orientation='horizontal',
        contour_type='cae_inner',
        shape='rectangle',
        width=4.0,
        height=3.0,
        data_pattern='stress',
        save_file=True,
        show=True
    )

