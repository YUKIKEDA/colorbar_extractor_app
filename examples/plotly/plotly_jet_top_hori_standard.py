"""
Plotly コンター図サンプル
- カラーマップ: jet
- カラーバー位置: 上
- カラーバー向き: 水平
- タイプ: 標準（マスクなし）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from contour_base_plotly import create_plotly_contour

if __name__ == '__main__':
    create_plotly_contour(
        colormap='jet',
        colorbar_position='top',
        colorbar_orientation='horizontal',
        contour_type='standard',
        data_pattern='peaks',
        save=True,
        show=True
    )

