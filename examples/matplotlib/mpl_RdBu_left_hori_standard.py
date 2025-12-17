"""
Matplotlib コンター図サンプル
- カラーマップ: RdBu (赤-青 ダイバージング)
- カラーバー位置: 左
- カラーバー向き: 水平（※左側でも水平にすると上に配置される）
- タイプ: 標準（マスクなし）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from contour_base_mpl import create_matplotlib_contour

if __name__ == '__main__':
    create_matplotlib_contour(
        colormap='RdBu',
        colorbar_position='left',
        colorbar_orientation='vertical',  # 左配置では垂直が適切
        contour_type='standard',
        data_pattern='waves',
        save=True,
        show=True
    )

