"""
Matplotlib コンター図サンプル
- カラーマップ: hot
- カラーバー位置: 右
- カラーバー向き: 垂直
- タイプ: CAE外部（形状部分が白抜き）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from contour_base_mpl import create_matplotlib_contour

if __name__ == '__main__':
    create_matplotlib_contour(
        colormap='hot',
        colorbar_position='right',
        colorbar_orientation='vertical',
        contour_type='cae_outer',
        shape='gear',
        n_teeth=10,
        data_pattern='stress',
        save=True,
        show=True
    )

