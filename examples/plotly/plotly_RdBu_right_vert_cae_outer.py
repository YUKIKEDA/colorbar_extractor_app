"""
Plotly コンター図サンプル
- カラーマップ: RdBu
- カラーバー位置: 右
- カラーバー向き: 垂直
- タイプ: CAE外部（形状部分が白抜き）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from contour_base_plotly import create_plotly_contour

if __name__ == '__main__':
    create_plotly_contour(
        colormap='RdBu',
        colorbar_position='right',
        colorbar_orientation='vertical',
        contour_type='cae_outer',
        shape='gear',
        n_teeth=10,
        data_pattern='stress',
        save=True,
        show=True
    )

