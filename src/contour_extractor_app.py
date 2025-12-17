"""
コンター領域抽出ツール

コンター図から指定した領域のみを抽出し、外側を白塗りにするアプリケーション。
矩形選択とフリーハンド選択に対応。
領域パラメータの保存・読み込み・バッチ処理に対応。
"""

import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from PIL import Image, ImageTk
import cv2
import numpy as np


class ContourExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("コンター領域抽出ツール")
        self.root.geometry("1400x900")

        # --- データ管理変数 ---
        self.original_cv_image = None  # 元画像
        self.result_cv_image = None    # 結果画像
        self.mask = None               # マスク画像
        
        # 選択ツール
        self.tool_mode = tk.StringVar(value="rectangle")  # "rectangle" or "freehand"
        
        # フリーハンド用のポイントリスト
        self.freehand_points = []
        self.freehand_line_ids = []
        
        # 矩形選択用
        self.rect_start_x = None
        self.rect_start_y = None
        self.rect_id = None
        
        # 表示用
        self.scale_factor = 1.0
        self.img_offset_x = 0
        self.img_offset_y = 0
        
        # 背景色（白）
        self.bg_color = (255, 255, 255)
        
        # 複数領域を保持
        self.regions = []  # [(type, points), ...]
        
        # UI構築
        self._setup_ui()

    def _setup_ui(self):
        # メインコンテナ
        main_container = tk.Frame(self.root, bg="#e0e0e0")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # --- 上部: ツールバー ---
        toolbar = tk.Frame(main_container, bg="#d0d0d0", pady=8)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # 画像を開くボタン
        tk.Button(toolbar, text="📁 画像を開く", command=self.load_image, 
                  bg="#fff", padx=10).pack(side=tk.LEFT, padx=10)
        
        # セパレータ
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # ツール選択
        tk.Label(toolbar, text="選択ツール:", bg="#d0d0d0").pack(side=tk.LEFT, padx=5)
        
        self.btn_rect = tk.Radiobutton(
            toolbar, text="◻ 矩形", variable=self.tool_mode, value="rectangle",
            bg="#d0d0d0", indicatoron=0, padx=15, pady=5,
            selectcolor="#4CAF50", command=self.on_tool_change
        )
        self.btn_rect.pack(side=tk.LEFT, padx=2)
        
        self.btn_freehand = tk.Radiobutton(
            toolbar, text="✏ フリーハンド", variable=self.tool_mode, value="freehand",
            bg="#d0d0d0", indicatoron=0, padx=15, pady=5,
            selectcolor="#4CAF50", command=self.on_tool_change
        )
        self.btn_freehand.pack(side=tk.LEFT, padx=2)
        
        # セパレータ
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 領域操作ボタン
        tk.Button(toolbar, text="➕ 領域を追加", command=self.add_region,
                  bg="#2196F3", fg="white", padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="🗑 最後の領域を削除", command=self.remove_last_region,
                  bg="#ff9800", fg="white", padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="🔄 全てクリア", command=self.clear_all_regions,
                  bg="#f44336", fg="white", padx=10).pack(side=tk.LEFT, padx=5)
        
        # セパレータ
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 適用・保存ボタン
        tk.Button(toolbar, text="✓ マスク適用", command=self.apply_mask,
                  bg="#4CAF50", fg="white", padx=15, font=("Bold", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="💾 保存", command=self.save_image,
                  bg="#9C27B0", fg="white", padx=15, font=("Bold", 10)).pack(side=tk.LEFT, padx=5)
        
        # セパレータ
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # パラメータ操作ボタン
        tk.Button(toolbar, text="📤 領域を保存", command=self.export_regions,
                  bg="#607D8B", fg="white", padx=10).pack(side=tk.LEFT, padx=3)
        tk.Button(toolbar, text="📥 領域を読込", command=self.import_regions,
                  bg="#607D8B", fg="white", padx=10).pack(side=tk.LEFT, padx=3)
        tk.Button(toolbar, text="⚡ バッチ処理", command=self.batch_process,
                  bg="#795548", fg="white", padx=10).pack(side=tk.LEFT, padx=3)
        
        # --- 中央: 左右分割 ---
        paned_window = tk.PanedWindow(main_container, orient=tk.HORIZONTAL, sashwidth=5, bg="#ccc")
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # --- 左側: 元画像＆選択エリア ---
        left_frame = tk.Frame(paned_window, bg="#e0e0e0")
        paned_window.add(left_frame, minsize=600)
        
        tk.Label(left_frame, text="元画像 (領域を選択してください)", 
                 font=("Bold", 10), bg="#e0e0e0").pack(pady=5)
        
        # Canvas
        self.main_canvas = tk.Canvas(left_frame, bg="#888", cursor="cross")
        self.main_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvasイベント
        self.main_canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.main_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.main_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.main_canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        
        # ヒントラベル
        self.hint_label = tk.Label(left_frame, text="", bg="#e0e0e0", fg="#666")
        self.hint_label.pack(pady=2)
        self.update_hint()
        
        # --- 右側: プレビューエリア ---
        right_frame = tk.Frame(paned_window, bg="#f0f0f0")
        paned_window.add(right_frame, minsize=400)
        
        tk.Label(right_frame, text="プレビュー (マスク適用後)", 
                 font=("Bold", 10), bg="#f0f0f0").pack(pady=5)
        
        self.preview_canvas = tk.Canvas(right_frame, bg="#888")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # --- 下部: ステータスバー ---
        status_bar = tk.Frame(main_container, bg="#d0d0d0", height=25)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(status_bar, text="画像を開いてください", 
                                     bg="#d0d0d0", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.region_count_label = tk.Label(status_bar, text="領域数: 0", 
                                           bg="#d0d0d0", anchor=tk.E)
        self.region_count_label.pack(side=tk.RIGHT, padx=10)

    def update_hint(self):
        """ヒントラベルを更新"""
        if self.tool_mode.get() == "rectangle":
            hint = "💡 ドラッグで矩形を描画 → 「領域を追加」で確定"
        else:
            hint = "💡 クリックで点を追加 → ダブルクリックまたは「領域を追加」で確定"
        self.hint_label.config(text=hint)

    def on_tool_change(self):
        """ツール変更時の処理"""
        self.clear_current_selection()
        self.update_hint()

    def clear_current_selection(self):
        """現在の選択をクリア"""
        # 矩形選択をクリア
        if self.rect_id:
            self.main_canvas.delete(self.rect_id)
            self.rect_id = None
        self.rect_start_x = None
        self.rect_start_y = None
        
        # フリーハンド選択をクリア
        for line_id in self.freehand_line_ids:
            self.main_canvas.delete(line_id)
        self.freehand_line_ids = []
        self.freehand_points = []

    # --- 画像読み込み ---
    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")]
        )
        if not path:
            return
        
        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("エラー", "画像の読み込みに失敗しました")
            return
        
        self.original_cv_image = img
        self.result_cv_image = None
        self.regions = []
        self.clear_current_selection()
        
        self.display_main_image()
        self.clear_preview()
        self.update_status(f"読み込み: {path}")
        self.update_region_count()

    def display_main_image(self):
        """メイン画像を表示"""
        if self.original_cv_image is None:
            return
        
        self.main_canvas.update()
        h, w = self.original_cv_image.shape[:2]
        cw = self.main_canvas.winfo_width()
        ch = self.main_canvas.winfo_height()
        if cw < 50:
            cw = 600
        if ch < 50:
            ch = 600
        
        scale = min(cw / w, ch / h, 1.0)
        self.scale_factor = scale
        
        new_w, new_h = int(w * scale), int(h * scale)
        rgb = cv2.cvtColor(self.original_cv_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb).resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_main_img = ImageTk.PhotoImage(pil_img)
        
        self.main_canvas.delete("all")
        self.img_offset_x = (cw - new_w) // 2
        self.img_offset_y = (ch - new_h) // 2
        
        self.main_canvas.create_image(
            self.img_offset_x, self.img_offset_y, 
            image=self.tk_main_img, anchor=tk.NW, tags="main_image"
        )
        
        # 既存の領域を再描画
        self.redraw_regions()

    def redraw_regions(self):
        """登録済みの領域を再描画"""
        self.main_canvas.delete("region")
        
        for i, (region_type, points) in enumerate(self.regions):
            color = self._get_region_color(i)
            
            if region_type == "rectangle" and len(points) == 2:
                # 矩形
                x1, y1 = self._image_to_canvas(*points[0])
                x2, y2 = self._image_to_canvas(*points[1])
                self.main_canvas.create_rectangle(
                    x1, y1, x2, y2, 
                    outline=color, width=2, tags="region"
                )
            elif region_type == "freehand" and len(points) >= 3:
                # フリーハンド（ポリゴン）
                canvas_points = [self._image_to_canvas(px, py) for px, py in points]
                flat_points = [coord for point in canvas_points for coord in point]
                self.main_canvas.create_polygon(
                    flat_points, 
                    outline=color, fill="", width=2, tags="region"
                )

    def _get_region_color(self, index):
        """領域のカラーを取得"""
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FF00FF", "#00FFFF", "#FFFF00"]
        return colors[index % len(colors)]

    def _canvas_to_image(self, cx, cy):
        """キャンバス座標を画像座標に変換"""
        ix = int((cx - self.img_offset_x) / self.scale_factor)
        iy = int((cy - self.img_offset_y) / self.scale_factor)
        return ix, iy

    def _image_to_canvas(self, ix, iy):
        """画像座標をキャンバス座標に変換"""
        cx = int(ix * self.scale_factor + self.img_offset_x)
        cy = int(iy * self.scale_factor + self.img_offset_y)
        return cx, cy

    # --- キャンバスイベント ---
    def on_canvas_press(self, event):
        if self.original_cv_image is None:
            return
        
        if self.tool_mode.get() == "rectangle":
            self._start_rectangle(event)
        else:
            self._add_freehand_point(event)

    def on_canvas_drag(self, event):
        if self.original_cv_image is None:
            return
        
        if self.tool_mode.get() == "rectangle":
            self._drag_rectangle(event)

    def on_canvas_release(self, event):
        if self.original_cv_image is None:
            return
        
        if self.tool_mode.get() == "rectangle":
            self._end_rectangle(event)

    def on_canvas_double_click(self, event):
        """ダブルクリックでフリーハンド選択を確定"""
        if self.tool_mode.get() == "freehand" and len(self.freehand_points) >= 3:
            self.add_region()

    # --- 矩形選択 ---
    def _start_rectangle(self, event):
        self.rect_start_x = event.x
        self.rect_start_y = event.y
        if self.rect_id:
            self.main_canvas.delete(self.rect_id)
            self.rect_id = None

    def _drag_rectangle(self, event):
        if self.rect_start_x is None:
            return
        if self.rect_id:
            self.main_canvas.delete(self.rect_id)
        self.rect_id = self.main_canvas.create_rectangle(
            self.rect_start_x, self.rect_start_y, event.x, event.y,
            outline="#FF0000", width=2, dash=(4, 4)
        )

    def _end_rectangle(self, event):
        # 矩形描画は維持（add_regionで確定するまで）
        pass

    # --- フリーハンド選択 ---
    def _add_freehand_point(self, event):
        self.freehand_points.append((event.x, event.y))
        
        # 点を描画
        r = 4
        self.main_canvas.create_oval(
            event.x - r, event.y - r, event.x + r, event.y + r,
            fill="#FF0000", outline="#FF0000", tags="freehand_temp"
        )
        
        # 線を描画
        if len(self.freehand_points) >= 2:
            x1, y1 = self.freehand_points[-2]
            x2, y2 = self.freehand_points[-1]
            line_id = self.main_canvas.create_line(
                x1, y1, x2, y2, fill="#FF0000", width=2, tags="freehand_temp"
            )
            self.freehand_line_ids.append(line_id)

    # --- 領域操作 ---
    def add_region(self):
        """現在の選択を領域として追加"""
        if self.original_cv_image is None:
            return
        
        h, w = self.original_cv_image.shape[:2]
        
        if self.tool_mode.get() == "rectangle":
            if self.rect_start_x is None or self.rect_id is None:
                messagebox.showwarning("警告", "矩形が選択されていません")
                return
            
            # 矩形の座標を取得
            coords = self.main_canvas.coords(self.rect_id)
            if len(coords) != 4:
                return
            
            x1, y1, x2, y2 = coords
            ix1, iy1 = self._canvas_to_image(x1, y1)
            ix2, iy2 = self._canvas_to_image(x2, y2)
            
            # クリップ
            ix1, iy1 = max(0, min(ix1, w)), max(0, min(iy1, h))
            ix2, iy2 = max(0, min(ix2, w)), max(0, min(iy2, h))
            
            if abs(ix2 - ix1) < 5 or abs(iy2 - iy1) < 5:
                messagebox.showwarning("警告", "領域が小さすぎます")
                return
            
            # 正規化
            if ix1 > ix2:
                ix1, ix2 = ix2, ix1
            if iy1 > iy2:
                iy1, iy2 = iy2, iy1
            
            self.regions.append(("rectangle", [(ix1, iy1), (ix2, iy2)]))
            
        else:  # freehand
            if len(self.freehand_points) < 3:
                messagebox.showwarning("警告", "3点以上を選択してください")
                return
            
            # キャンバス座標を画像座標に変換
            image_points = []
            for cx, cy in self.freehand_points:
                ix, iy = self._canvas_to_image(cx, cy)
                ix, iy = max(0, min(ix, w)), max(0, min(iy, h))
                image_points.append((ix, iy))
            
            self.regions.append(("freehand", image_points))
        
        # 現在の選択をクリアして再描画
        self.clear_current_selection()
        self.main_canvas.delete("freehand_temp")
        self.display_main_image()
        self.update_region_count()
        self.update_status(f"領域を追加しました（合計: {len(self.regions)}）")

    def remove_last_region(self):
        """最後の領域を削除"""
        if self.regions:
            self.regions.pop()
            self.display_main_image()
            self.update_region_count()
            self.update_status("最後の領域を削除しました")

    def clear_all_regions(self):
        """全ての領域をクリア"""
        self.regions = []
        self.clear_current_selection()
        self.main_canvas.delete("freehand_temp")
        self.display_main_image()
        self.clear_preview()
        self.update_region_count()
        self.update_status("全ての領域をクリアしました")

    # --- マスク処理 ---
    def apply_mask(self):
        """マスクを適用して結果を生成"""
        if self.original_cv_image is None:
            messagebox.showwarning("警告", "画像が読み込まれていません")
            return
        
        if not self.regions:
            messagebox.showwarning("警告", "領域が選択されていません")
            return
        
        h, w = self.original_cv_image.shape[:2]
        
        # マスク画像を作成（黒で初期化）
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # 各領域をマスクに追加
        for region_type, points in self.regions:
            if region_type == "rectangle":
                (x1, y1), (x2, y2) = points
                cv2.rectangle(mask, (int(x1), int(y1)), (int(x2), int(y2)), 255, -1)
            elif region_type == "freehand":
                pts = np.array(points, dtype=np.int32)
                cv2.fillPoly(mask, [pts], 255)
        
        # 結果画像を作成
        result = self.original_cv_image.copy()
        
        # マスク外を白で塗りつぶし
        result[mask == 0] = self.bg_color
        
        self.result_cv_image = result
        self.mask = mask
        
        self.display_preview()
        self.update_status("マスクを適用しました")

    def display_preview(self):
        """プレビュー表示"""
        if self.result_cv_image is None:
            return
        
        self.preview_canvas.update()
        h, w = self.result_cv_image.shape[:2]
        cw = self.preview_canvas.winfo_width()
        ch = self.preview_canvas.winfo_height()
        if cw < 50:
            cw = 400
        if ch < 50:
            ch = 400
        
        scale = min(cw / w, ch / h, 1.0)
        new_w, new_h = int(w * scale), int(h * scale)
        
        rgb = cv2.cvtColor(self.result_cv_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb).resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_preview_img = ImageTk.PhotoImage(pil_img)
        
        self.preview_canvas.delete("all")
        offset_x = (cw - new_w) // 2
        offset_y = (ch - new_h) // 2
        self.preview_canvas.create_image(
            offset_x, offset_y, 
            image=self.tk_preview_img, anchor=tk.NW
        )

    def clear_preview(self):
        """プレビューをクリア"""
        self.preview_canvas.delete("all")
        self.result_cv_image = None

    # --- 保存 ---
    def save_image(self):
        """結果画像を保存"""
        if self.result_cv_image is None:
            messagebox.showwarning("警告", "先にマスクを適用してください")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("BMP", "*.bmp")]
        )
        if path:
            cv2.imwrite(path, self.result_cv_image)
            messagebox.showinfo("保存完了", f"保存しました:\n{path}")
            self.update_status(f"保存完了: {path}")

    # --- ステータス更新 ---
    def update_status(self, message):
        self.status_label.config(text=message)

    def update_region_count(self):
        self.region_count_label.config(text=f"領域数: {len(self.regions)}")

    # --- 領域パラメータのエクスポート/インポート ---
    def export_regions(self):
        """領域パラメータをJSONファイルにエクスポート"""
        if not self.regions:
            messagebox.showwarning("警告", "エクスポートする領域がありません")
            return
        
        # 画像サイズ情報を取得
        image_size = None
        if self.original_cv_image is not None:
            h, w = self.original_cv_image.shape[:2]
            image_size = {"width": w, "height": h}
        
        # エクスポートデータを作成
        export_data = {
            "version": "1.0",
            "description": "コンター領域抽出パラメータ",
            "image_size": image_size,
            "regions": []
        }
        
        for region_type, points in self.regions:
            region_data = {
                "type": region_type,
                "points": [{"x": int(p[0]), "y": int(p[1])} for p in points]
            }
            export_data["regions"].append(region_data)
        
        # ファイル保存ダイアログ
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="領域パラメータを保存"
        )
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            self.update_status(f"領域パラメータを保存: {path}")
            messagebox.showinfo("保存完了", f"領域パラメータを保存しました:\n{path}")

    def import_regions(self):
        """JSONファイルから領域パラメータをインポート"""
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")],
            title="領域パラメータを読み込み"
        )
        if not path:
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # データの検証
            if "regions" not in import_data:
                raise ValueError("無効なパラメータファイルです")
            
            # 領域をインポート
            imported_regions = []
            for region_data in import_data["regions"]:
                region_type = region_data["type"]
                points = [(p["x"], p["y"]) for p in region_data["points"]]
                imported_regions.append((region_type, points))
            
            # 既存の領域に追加するか確認
            if self.regions:
                result = messagebox.askyesnocancel(
                    "確認",
                    "既存の領域があります。\n\n"
                    "「はい」: 既存の領域を置き換え\n"
                    "「いいえ」: 既存の領域に追加\n"
                    "「キャンセル」: 中止"
                )
                if result is None:
                    return
                elif result:  # はい
                    self.regions = imported_regions
                else:  # いいえ
                    self.regions.extend(imported_regions)
            else:
                self.regions = imported_regions
            
            self.display_main_image()
            self.update_region_count()
            self.update_status(f"領域パラメータを読み込み: {len(imported_regions)}個")
            
            # 画像サイズの警告
            if self.original_cv_image is not None and "image_size" in import_data:
                orig_size = import_data["image_size"]
                if orig_size:
                    h, w = self.original_cv_image.shape[:2]
                    if orig_size["width"] != w or orig_size["height"] != h:
                        messagebox.showwarning(
                            "警告",
                            f"元の画像サイズ ({orig_size['width']}x{orig_size['height']}) と\n"
                            f"現在の画像サイズ ({w}x{h}) が異なります。\n"
                            "領域の位置がずれる可能性があります。"
                        )
            
        except Exception as e:
            messagebox.showerror("エラー", f"読み込みに失敗しました:\n{e}")

    def batch_process(self):
        """バッチ処理: 複数画像に同じ領域パラメータを適用"""
        # バッチ処理ダイアログを表示
        BatchProcessDialog(self.root, self)

    def apply_mask_to_image(self, cv_image):
        """指定された画像にマスクを適用（バッチ処理用）"""
        if not self.regions:
            return cv_image
        
        h, w = cv_image.shape[:2]
        
        # マスク画像を作成
        mask = np.zeros((h, w), dtype=np.uint8)
        
        for region_type, points in self.regions:
            if region_type == "rectangle":
                (x1, y1), (x2, y2) = points
                # 画像サイズにクリップ
                x1, y1 = max(0, min(int(x1), w)), max(0, min(int(y1), h))
                x2, y2 = max(0, min(int(x2), w)), max(0, min(int(y2), h))
                cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
            elif region_type == "freehand":
                # 画像サイズにクリップ
                clipped_points = []
                for px, py in points:
                    px = max(0, min(int(px), w - 1))
                    py = max(0, min(int(py), h - 1))
                    clipped_points.append((px, py))
                pts = np.array(clipped_points, dtype=np.int32)
                cv2.fillPoly(mask, [pts], 255)
        
        # 結果画像を作成
        result = cv_image.copy()
        result[mask == 0] = self.bg_color
        
        return result


class BatchProcessDialog:
    """バッチ処理ダイアログ"""
    
    def __init__(self, parent, app):
        self.app = app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("バッチ処理")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.input_files = []
        self.output_dir = tk.StringVar()
        self.suffix = tk.StringVar(value="_extracted")
        self.use_regions_file = tk.BooleanVar(value=False)
        self.regions_file = tk.StringVar()
        
        self._setup_ui()
    
    def _setup_ui(self):
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 説明
        tk.Label(main_frame, text="複数の画像に同じ領域パラメータを適用します",
                 font=("Bold", 11)).pack(anchor=tk.W, pady=(0, 15))
        
        # === 領域パラメータ選択 ===
        param_frame = tk.LabelFrame(main_frame, text="領域パラメータ", padx=10, pady=10)
        param_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(param_frame, text="現在の領域を使用", 
                       variable=self.use_regions_file, value=False,
                       command=self._toggle_regions_file).pack(anchor=tk.W)
        
        file_row = tk.Frame(param_frame)
        file_row.pack(fill=tk.X, pady=5)
        tk.Radiobutton(file_row, text="JSONファイルを使用:", 
                       variable=self.use_regions_file, value=True,
                       command=self._toggle_regions_file).pack(side=tk.LEFT)
        self.regions_entry = tk.Entry(file_row, textvariable=self.regions_file, width=35, state=tk.DISABLED)
        self.regions_entry.pack(side=tk.LEFT, padx=5)
        self.regions_browse_btn = tk.Button(file_row, text="参照...", 
                                            command=self._browse_regions, state=tk.DISABLED)
        self.regions_browse_btn.pack(side=tk.LEFT)
        
        # 現在の領域数を表示
        region_count = len(self.app.regions)
        self.region_info_label = tk.Label(param_frame, 
                                          text=f"（現在 {region_count} 個の領域が設定されています）",
                                          fg="#666")
        self.region_info_label.pack(anchor=tk.W)
        
        # === 入力ファイル選択 ===
        input_frame = tk.LabelFrame(main_frame, text="入力画像", padx=10, pady=10)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        btn_row = tk.Frame(input_frame)
        btn_row.pack(fill=tk.X)
        tk.Button(btn_row, text="ファイルを追加", command=self._add_files).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_row, text="フォルダを追加", command=self._add_folder).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_row, text="クリア", command=self._clear_files).pack(side=tk.LEFT, padx=2)
        
        # ファイルリスト
        list_frame = tk.Frame(input_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=8)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        self.file_count_label = tk.Label(input_frame, text="0 ファイル選択中")
        self.file_count_label.pack(anchor=tk.W)
        
        # === 出力設定 ===
        output_frame = tk.LabelFrame(main_frame, text="出力設定", padx=10, pady=10)
        output_frame.pack(fill=tk.X, pady=5)
        
        dir_row = tk.Frame(output_frame)
        dir_row.pack(fill=tk.X, pady=2)
        tk.Label(dir_row, text="出力先:").pack(side=tk.LEFT)
        tk.Entry(dir_row, textvariable=self.output_dir, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(dir_row, text="参照...", command=self._browse_output).pack(side=tk.LEFT)
        
        suffix_row = tk.Frame(output_frame)
        suffix_row.pack(fill=tk.X, pady=2)
        tk.Label(suffix_row, text="ファイル名サフィックス:").pack(side=tk.LEFT)
        tk.Entry(suffix_row, textvariable=self.suffix, width=20).pack(side=tk.LEFT, padx=5)
        tk.Label(suffix_row, text="（例: image.png → image_extracted.png）", fg="#666").pack(side=tk.LEFT)
        
        # === ボタン ===
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=15)
        
        tk.Button(btn_frame, text="キャンセル", command=self.dialog.destroy,
                  width=12).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="実行", command=self._execute,
                  bg="#4CAF50", fg="white", width=12).pack(side=tk.RIGHT, padx=5)
    
    def _toggle_regions_file(self):
        """JSONファイル選択の有効/無効を切り替え"""
        if self.use_regions_file.get():
            self.regions_entry.config(state=tk.NORMAL)
            self.regions_browse_btn.config(state=tk.NORMAL)
        else:
            self.regions_entry.config(state=tk.DISABLED)
            self.regions_browse_btn.config(state=tk.DISABLED)
    
    def _browse_regions(self):
        """領域パラメータファイルを選択"""
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")],
            title="領域パラメータファイルを選択"
        )
        if path:
            self.regions_file.set(path)
    
    def _add_files(self):
        """画像ファイルを追加"""
        paths = filedialog.askopenfilenames(
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")]
        )
        for path in paths:
            if path not in self.input_files:
                self.input_files.append(path)
                self.file_listbox.insert(tk.END, Path(path).name)
        self._update_file_count()
    
    def _add_folder(self):
        """フォルダ内の画像を追加"""
        folder = filedialog.askdirectory(title="画像フォルダを選択")
        if folder:
            extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff']
            for file in Path(folder).iterdir():
                if file.suffix.lower() in extensions:
                    path = str(file)
                    if path not in self.input_files:
                        self.input_files.append(path)
                        self.file_listbox.insert(tk.END, file.name)
            self._update_file_count()
    
    def _clear_files(self):
        """ファイルリストをクリア"""
        self.input_files = []
        self.file_listbox.delete(0, tk.END)
        self._update_file_count()
    
    def _update_file_count(self):
        """ファイル数を更新"""
        self.file_count_label.config(text=f"{len(self.input_files)} ファイル選択中")
    
    def _browse_output(self):
        """出力先フォルダを選択"""
        folder = filedialog.askdirectory(title="出力先フォルダを選択")
        if folder:
            self.output_dir.set(folder)
    
    def _execute(self):
        """バッチ処理を実行"""
        # 検証
        if not self.input_files:
            messagebox.showwarning("警告", "処理する画像を選択してください")
            return
        
        if not self.output_dir.get():
            messagebox.showwarning("警告", "出力先フォルダを指定してください")
            return
        
        # 領域パラメータを取得
        if self.use_regions_file.get():
            if not self.regions_file.get():
                messagebox.showwarning("警告", "領域パラメータファイルを選択してください")
                return
            try:
                with open(self.regions_file.get(), 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                regions = []
                for region_data in import_data["regions"]:
                    region_type = region_data["type"]
                    points = [(p["x"], p["y"]) for p in region_data["points"]]
                    regions.append((region_type, points))
            except Exception as e:
                messagebox.showerror("エラー", f"パラメータファイルの読み込みに失敗:\n{e}")
                return
        else:
            regions = self.app.regions
        
        if not regions:
            messagebox.showwarning("警告", "領域パラメータがありません")
            return
        
        # 出力フォルダを作成
        output_path = Path(self.output_dir.get())
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 一時的に領域を保存
        original_regions = self.app.regions
        self.app.regions = regions
        
        # 処理実行
        success_count = 0
        error_count = 0
        
        for input_path in self.input_files:
            try:
                # 画像を読み込み
                img = cv2.imread(input_path)
                if img is None:
                    error_count += 1
                    continue
                
                # マスクを適用
                result = self.app.apply_mask_to_image(img)
                
                # 出力ファイル名を生成
                input_file = Path(input_path)
                output_name = f"{input_file.stem}{self.suffix.get()}{input_file.suffix}"
                output_file = output_path / output_name
                
                # 保存
                cv2.imwrite(str(output_file), result)
                success_count += 1
                
            except Exception as e:
                print(f"Error processing {input_path}: {e}")
                error_count += 1
        
        # 領域を復元
        self.app.regions = original_regions
        
        # 結果を表示
        messagebox.showinfo(
            "完了",
            f"バッチ処理が完了しました\n\n"
            f"成功: {success_count} ファイル\n"
            f"エラー: {error_count} ファイル\n\n"
            f"出力先: {output_path}"
        )
        
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ContourExtractor(root)
    root.mainloop()

