import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

class ColorbarExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("カラーバー抽出ツール")
        self.root.geometry("1000x700")

        # 変数初期化
        self.original_cv_image = None # OpenCV形式 (BGR)
        self.display_image = None     # 表示用 (PIL形式)
        self.scale_factor = 1.0
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.extracted_cv_image = None

        # --- UI レイアウト ---
        
        # 上部: コントロールパネル
        control_frame = tk.Frame(root, bg="#f0f0f0", pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        btn_load = tk.Button(control_frame, text="画像を開く", command=self.load_image, width=15, bg="#ddd")
        btn_load.pack(side=tk.LEFT, padx=20)

        self.lbl_instruction = tk.Label(control_frame, text="画像を読み込み、カラーバー部分をドラッグして囲んでください", bg="#f0f0f0", fg="#333")
        self.lbl_instruction.pack(side=tk.LEFT, padx=10)

        btn_save = tk.Button(control_frame, text="抽出画像を保存", command=self.save_image, width=15, bg="#4CAF50", fg="white")
        btn_save.pack(side=tk.RIGHT, padx=20)

        # 中央: 画像表示エリア (Canvas)
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#e0e0e0", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # イベントバインド
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # 右側: プレビューエリア
        preview_frame = tk.Frame(root, width=200, bg="#fff", relief=tk.RIDGE, borderwidth=2)
        preview_frame.pack(side=tk.RIGHT, fill=tk.Y)
        preview_frame.pack_propagate(False) # サイズ固定

        tk.Label(preview_frame, text="抽出結果", font=("Arial", 12, "bold"), bg="#fff").pack(pady=10)
        
        self.lbl_preview = tk.Label(preview_frame, bg="#fff", text="(未抽出)")
        self.lbl_preview.pack(pady=20, expand=True)

    def load_image(self):
        """画像ファイルを選択して読み込む"""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
        if not file_path:
            return

        # OpenCVで読み込み
        img = cv2.imread(file_path)
        if img is None:
            messagebox.showerror("エラー", "画像を読み込めませんでした。")
            return
        
        self.original_cv_image = img
        self.extracted_cv_image = None
        self.lbl_preview.config(image='', text="(未抽出)")

        # 表示用にリサイズしてCanvasに描画
        self.display_image_on_canvas()

    def display_image_on_canvas(self):
        """画像をウィンドウサイズに合わせて縮小して表示"""
        if self.original_cv_image is None:
            return

        h, w = self.original_cv_image.shape[:2]
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        # Canvas初期化前対策
        if canvas_w < 50: 
            canvas_w = 800
        if canvas_h < 50: 
            canvas_h = 600

        # アスペクト比を維持してリサイズ計算
        scale_w = canvas_w / w
        scale_h = canvas_h / h
        self.scale_factor = min(scale_w, scale_h, 1.0) # 拡大はしない

        new_w = int(w * self.scale_factor)
        new_h = int(h * self.scale_factor)

        # 表示用にRGB変換
        rgb_img = cv2.cvtColor(self.original_cv_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        self.display_image = ImageTk.PhotoImage(pil_img)
        
        self.canvas.delete("all")
        # 中央寄せで表示
        self.canvas.create_image(canvas_w//2, canvas_h//2, image=self.display_image, anchor=tk.CENTER)
        
        # 画像の左上の座標を記録（クリック座標の補正用）
        self.img_offset_x = (canvas_w - new_w) // 2
        self.img_offset_y = (canvas_h - new_h) // 2

    def on_button_press(self, event):
        """ドラッグ開始"""
        if self.original_cv_image is None: 
            return
        self.start_x = event.x
        self.start_y = event.y
        
        # 既存の矩形を削除
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None

    def on_mouse_drag(self, event):
        """ドラッグ中：矩形描画"""
        if self.start_x is None: 
            return
        
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline="red", width=2, dash=(4, 2)
        )

    def on_button_release(self, event):
        """ドラッグ終了：選択範囲を取得して処理実行"""
        if self.start_x is None: 
            return

        end_x, end_y = event.x, event.y

        # 座標の正規化（左上、右下にする）
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        # 小さすぎる選択は無視
        if (x2 - x1) < 5 or (y2 - y1) < 5:
            self.start_x = None
            return

        # Canvas座標から元の画像の座標へ変換
        orig_x1 = int((x1 - self.img_offset_x) / self.scale_factor)
        orig_y1 = int((y1 - self.img_offset_y) / self.scale_factor)
        orig_x2 = int((x2 - self.img_offset_x) / self.scale_factor)
        orig_y2 = int((y2 - self.img_offset_y) / self.scale_factor)

        # 画像範囲内にクリップ
        h, w = self.original_cv_image.shape[:2]
        orig_x1 = max(0, min(w, orig_x1))
        orig_y1 = max(0, min(h, orig_y1))
        orig_x2 = max(0, min(w, orig_x2))
        orig_y2 = max(0, min(h, orig_y2))

        # ROI（関心領域）の切り出し
        roi = self.original_cv_image[orig_y1:orig_y2, orig_x1:orig_x2]

        if roi.size == 0:
            return

        # --- ここで抽出アルゴリズムを実行 ---
        self.process_roi(roi)
        self.start_x = None

    def process_roi(self, roi):
        """
        選択範囲(roi)から、OpenCVを使って
        「カラーバーのみ（目盛り除去）」を抽出するロジック
        """
        
        # 1. 彩度(Saturation)を利用して「色付き部分」のみをマスク
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        s_channel = hsv[:, :, 1] # 彩度チャンネル
        
        # 彩度しきい値 (0-255)。グレーや白黒は彩度が低い。
        # 30〜50あたりが一般的ですが、薄い色も拾うなら低めに設定
        _, binary = cv2.threshold(s_channel, 30, 255, cv2.THRESH_BINARY)

        # 2. ノイズ除去（モルフォロジー演算）
        # 小さなゴミを除去し、バーの塊をつなげる
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

        # 3. 最大輪郭の検出
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        target_roi = roi # デフォルトは切り抜いただけのもの

        if contours:
            # 面積が最大のものをカラーバーとみなす
            max_cnt = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(max_cnt)

            # ゴミでないか確認（ある程度の大きさが必要）
            if w > 5 and h > 5:
                # 検出された領域で再クロップ
                # 少しパディングを除去するか（オプション）
                padding = 0 
                if w > padding*2 and h > padding*2:
                    target_roi = roi[y+padding:y+h-padding, x+padding:x+w-padding]
                else:
                    target_roi = roi[y:y+h, x:x+w]

        self.extracted_cv_image = target_roi
        self.show_preview(target_roi)

    def show_preview(self, cv_img):
        """右側のパネルに結果を表示"""
        # BGR -> RGB
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)

        # プレビュー枠に合わせてリサイズ（アスペクト比維持）
        preview_w = 180
        preview_h = 400 # 縦長を想定
        
        img_w, img_h = pil_img.size
        scale = min(preview_w / img_w, preview_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        
        # 拡大しすぎないように制限
        if scale > 1.5: 
            pil_img = pil_img.resize((int(img_w*1.5), int(img_h*1.5)), Image.Resampling.NEAREST)
        else:
            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        self.preview_image = ImageTk.PhotoImage(pil_img)
        self.lbl_preview.config(image=self.preview_image, text="")

    def save_image(self):
        """抽出結果を保存"""
        if self.extracted_cv_image is None:
            messagebox.showwarning("警告", "まだ抽出されていません。")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG file", "*.png"), ("JPEG file", "*.jpg")])
        if file_path:
            cv2.imwrite(file_path, self.extracted_cv_image)
            messagebox.showinfo("完了", f"保存しました:\n{file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorbarExtractorApp(root)
    
    # 起動時にリサイズイベントで画像配置を調整するために待機
    root.update()
    
    root.mainloop()