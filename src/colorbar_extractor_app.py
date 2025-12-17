import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

class AdvancedColorbarExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("カラーバー抽出ツール (微調整モード付き)")
        self.root.geometry("1200x800")

        # --- データ管理変数 ---
        self.original_cv_image = None  # 元画像
        self.roi_cv_image = None       # ユーザーが矩形選択したエリア(ROI)
        self.base_rect = None          # 自動検出された基準矩形 (x, y, w, h)
        
        # マージン（削り込み）変数 (Tkinter IntVar)
        # 正の値=削る, 負の値=広げる
        self.margin_top = tk.IntVar(value=0)
        self.margin_bottom = tk.IntVar(value=0)
        self.margin_left = tk.IntVar(value=0)
        self.margin_right = tk.IntVar(value=0)
        
        # 拡大率
        self.zoom_level = tk.DoubleVar(value=1.0)

        # UI構築
        self._setup_ui()

    def _setup_ui(self):
        # メインコンテナ: 左右に分割
        paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5, bg="#ddd")
        paned_window.pack(fill=tk.BOTH, expand=True)

        # --- 左側: メイン画像表示エリア ---
        left_frame = tk.Frame(paned_window, bg="#e0e0e0")
        paned_window.add(left_frame, minsize=600)

        # コントロールバー (左上)
        btn_frame = tk.Frame(left_frame, bg="#e0e0e0", pady=5)
        btn_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Button(btn_frame, text="画像を開く", command=self.load_image, bg="#fff").pack(side=tk.LEFT, padx=10)
        tk.Label(btn_frame, text="ドラッグしてカラーバー周辺を囲んでください", bg="#e0e0e0").pack(side=tk.LEFT, padx=10)

        # Canvas
        self.main_canvas = tk.Canvas(left_frame, bg="#ccc", cursor="cross")
        self.main_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvasイベント
        self.main_canvas.bind("<ButtonPress-1>", self.on_main_press)
        self.main_canvas.bind("<B1-Motion>", self.on_main_drag)
        self.main_canvas.bind("<ButtonRelease-1>", self.on_main_release)

        # --- 右側: プレビュー＆微調整エリア ---
        right_frame = tk.Frame(paned_window, bg="#f9f9f9", width=400)
        paned_window.add(right_frame, minsize=300)
        right_frame.pack_propagate(False)

        # 1. プレビュー表示エリア (スクロール可能Canvas)
        lbl_preview_title = tk.Label(right_frame, text="抽出プレビュー (ピクセル確認)", font=("Bold", 10), bg="#f9f9f9")
        lbl_preview_title.pack(pady=(10, 0))

        self.preview_canvas = tk.Canvas(right_frame, bg="#aaa", height=400)
        self.preview_canvas.pack(fill=tk.BOTH, padx=10, pady=5)
        
        # プレビュー操作用のマウスイベント（ドラッグで移動）
        self.preview_canvas.bind("<ButtonPress-1>", self.on_preview_press)
        self.preview_canvas.bind("<B1-Motion>", self.on_preview_drag)

        # 2. ズームスライダー
        zoom_frame = tk.Frame(right_frame, bg="#f9f9f9")
        zoom_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(zoom_frame, text="Zoom:", bg="#f9f9f9").pack(side=tk.LEFT)
        self.scale_zoom = tk.Scale(zoom_frame, from_=1.0, to=10.0, resolution=0.5, orient=tk.HORIZONTAL, 
                                   variable=self.zoom_level, command=self.update_preview, bg="#f9f9f9", length=200)
        self.scale_zoom.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 3. マージン微調整パネル
        adj_frame = tk.LabelFrame(right_frame, text="境界線調整 (px)", bg="#f9f9f9", padx=10, pady=10)
        adj_frame.pack(fill=tk.X, padx=10, pady=10)

        # 十字キーのような配置にする
        #      [Top]
        # [Left]   [Right]
        #     [Bottom]
        
        def create_spin(parent, var, r, c):
            # コマンドを遅延実行させてレスポンスを良くする
            s = tk.Spinbox(parent, from_=-50, to=50, textvariable=var, width=5, command=lambda: self.update_preview(None))
            s.grid(row=r, column=c, padx=5, pady=5)
            # キーボード入力時にも更新
            s.bind("<Return>", lambda e: self.update_preview(None))
            s.bind("<FocusOut>", lambda e: self.update_preview(None))
            return s

        tk.Label(adj_frame, text="上", bg="#f9f9f9").grid(row=0, column=1)
        create_spin(adj_frame, self.margin_top, 1, 1)

        tk.Label(adj_frame, text="左", bg="#f9f9f9").grid(row=2, column=0)
        create_spin(adj_frame, self.margin_left, 2, 0)

        tk.Label(adj_frame, text="右", bg="#f9f9f9").grid(row=2, column=2)
        create_spin(adj_frame, self.margin_right, 2, 2)

        tk.Label(adj_frame, text="下", bg="#f9f9f9").grid(row=3, column=1)
        create_spin(adj_frame, self.margin_bottom, 4, 1)

        # 説明
        tk.Label(adj_frame, text="※正の値=削る / 負の値=広げる", font=("Arial", 8), fg="#666", bg="#f9f9f9").grid(row=5, column=0, columnspan=3, pady=5)

        # 4. 保存ボタン
        btn_save = tk.Button(right_frame, text="現在の状態で保存", command=self.save_image, bg="#4CAF50", fg="white", font=("Bold", 12), pady=10)
        btn_save.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)

        # 変数初期化
        self.rect_start_x = None
        self.rect_start_y = None
        self.rect_id = None
        self.scale_factor = 1.0
        self.img_offset_x = 0
        self.img_offset_y = 0
        self.preview_drag_start = None

    # --- 画像読み込み処理 ---
    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not path: 
            return

        img = cv2.imread(path)
        if img is None: 
            return

        self.original_cv_image = img
        self.display_main_image()

    def display_main_image(self):
        if self.original_cv_image is None: 
            return
        
        # 画面サイズに合わせてリサイズ表示
        h, w = self.original_cv_image.shape[:2]
        cw = self.main_canvas.winfo_width()
        ch = self.main_canvas.winfo_height()
        if cw < 50: 
            cw = 600
        if ch < 50: 
            ch = 600

        scale = min(cw/w, ch/h, 1.0)
        self.scale_factor = scale
        
        new_w, new_h = int(w*scale), int(h*scale)
        rgb = cv2.cvtColor(self.original_cv_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb).resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_main_img = ImageTk.PhotoImage(pil_img)

        self.main_canvas.delete("all")
        self.img_offset_x = (cw - new_w)//2
        self.img_offset_y = (ch - new_h)//2
        
        self.main_canvas.create_image(self.img_offset_x, self.img_offset_y, image=self.tk_main_img, anchor=tk.NW)

    # --- ドラッグ選択処理 ---
    def on_main_press(self, event):
        self.rect_start_x = event.x
        self.rect_start_y = event.y
        if self.rect_id:
            self.main_canvas.delete(self.rect_id)
            self.rect_id = None

    def on_main_drag(self, event):
        if not self.rect_start_x: 
            return
        if self.rect_id: 
            self.main_canvas.delete(self.rect_id)
        self.rect_id = self.main_canvas.create_rectangle(
            self.rect_start_x, self.rect_start_y, event.x, event.y, outline="red", width=2, dash=(4,4)
        )

    def on_main_release(self, event):
        if not self.rect_start_x:
            return
        
        # 座標計算
        x1, y1 = min(self.rect_start_x, event.x), min(self.rect_start_y, event.y)
        x2, y2 = max(self.rect_start_x, event.x), max(self.rect_start_y, event.y)

        # キャンバス座標 -> 画像座標
        ix1 = int((x1 - self.img_offset_x) / self.scale_factor)
        iy1 = int((y1 - self.img_offset_y) / self.scale_factor)
        ix2 = int((x2 - self.img_offset_x) / self.scale_factor)
        iy2 = int((y2 - self.img_offset_y) / self.scale_factor)

        # クリップ
        h, w = self.original_cv_image.shape[:2]
        ix1, iy1 = max(0, ix1), max(0, iy1)
        ix2, iy2 = min(w, ix2), min(h, iy2)

        if ix2 - ix1 < 5 or iy2 - iy1 < 5: 
            return

        # ROI保存
        self.roi_cv_image = self.original_cv_image[iy1:iy2, ix1:ix2].copy()
        
        # 自動検出実行
        self.run_auto_detection()

        self.rect_start_x = None

    # --- 自動検出ロジック ---
    def run_auto_detection(self):
        if self.roi_cv_image is None: 
            return

        # アルゴリズム: 彩度で検出して結合
        hsv = cv2.cvtColor(self.roi_cv_image, cv2.COLOR_BGR2HSV)
        s = hsv[:, :, 1]
        _, binary = cv2.threshold(s, 20, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5,3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        roi_h, roi_w = self.roi_cv_image.shape[:2]
        
        if contours:
            # 有効な矩形をすべて集めて包含矩形を作る
            rects = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 50]
            if rects:
                min_x = min([r[0] for r in rects])
                min_y = min([r[1] for r in rects])
                max_x = max([r[0]+r[2] for r in rects])
                max_y = max([r[1]+r[3] for r in rects])
                
                self.base_rect = (min_x, min_y, max_x - min_x, max_y - min_y)
            else:
                self.base_rect = (0, 0, roi_w, roi_h) # 見つからなければ全体
        else:
            self.base_rect = (0, 0, roi_w, roi_h)

        # マージン値をリセット (初期値は0)
        # ※もし枠線が残りやすいなら、初期値を1か2にしても良い
        self.margin_top.set(0)
        self.margin_bottom.set(0)
        self.margin_left.set(0)
        self.margin_right.set(0)

        self.update_preview()

    # --- プレビュー更新 (リアルタイム) ---
    def update_preview(self, _=None):
        if self.roi_cv_image is None or self.base_rect is None: 
            return

        bx, by, bw, bh = self.base_rect
        
        # ユーザー設定マージンを適用
        mt = self.margin_top.get()
        mb = self.margin_bottom.get()
        ml = self.margin_left.get()
        mr = self.margin_right.get()

        # 最終的な切り出し座標 (ROI座標系)
        # ROI範囲外に出ないようにクリップする
        roi_h, roi_w = self.roi_cv_image.shape[:2]

        x1 = max(0, bx + ml)
        y1 = max(0, by + mt)
        x2 = min(roi_w, bx + bw - mr)
        y2 = min(roi_h, by + bh - mb)

        # 矛盾チェック（幅・高さが0以下にならないように）
        if x2 <= x1: 
            x2 = x1 + 1
        if y2 <= y1: 
            y2 = y1 + 1

        # 切り出し
        self.preview_cv_img = self.roi_cv_image[y1:y2, x1:x2]

        # 拡大表示
        zoom = self.zoom_level.get()
        ph, pw = self.preview_cv_img.shape[:2]
        new_pw, new_ph = int(pw * zoom), int(ph * zoom)

        # NEAREST法でリサイズ（ドットをくっきりさせるため）
        rgb = cv2.cvtColor(self.preview_cv_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb).resize((new_pw, new_ph), Image.Resampling.NEAREST)
        self.tk_preview_img = ImageTk.PhotoImage(pil_img)

        # Canvas更新
        self.preview_canvas.delete("all")
        # 中央に配置
        self.preview_canvas.config(scrollregion=(0, 0, new_pw, new_ph))
        self.preview_canvas.create_image(new_pw//2, new_ph//2, image=self.tk_preview_img, anchor=tk.CENTER)

    # --- プレビューのドラッグ移動 (パン) ---
    def on_preview_press(self, event):
        self.preview_canvas.scan_mark(event.x, event.y)

    def on_preview_drag(self, event):
        self.preview_canvas.scan_dragto(event.x, event.y, gain=1)

    # --- 保存 ---
    def save_image(self):
        if not hasattr(self, 'preview_cv_img') or self.preview_cv_img is None:
            return
        
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPG", "*.jpg")])
        if path:
            cv2.imwrite(path, self.preview_cv_img)
            messagebox.showinfo("保存完了", f"保存しました:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedColorbarExtractor(root)
    root.mainloop()