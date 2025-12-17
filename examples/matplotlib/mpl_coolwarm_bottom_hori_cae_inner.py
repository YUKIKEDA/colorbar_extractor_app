"""
Matplotlib コンター図サンプル
- カラーマップ: coolwarm
- カラーバー位置: 下
- カラーバー向き: 水平
- タイプ: CAE内部（形状内部にコンター表示）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from contour_base_mpl import create_matplotlib_contour

if __name__ == '__main__':
    create_matplotlib_contour(
        colormap='coolwarm',
        colorbar_position='bottom',
        colorbar_orientation='horizontal',
        contour_type='cae_inner',
        shape='bracket',
        data_pattern='stress',
        save=True,
        show=True
    )

