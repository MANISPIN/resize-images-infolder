import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import os
import glob

class ImageResizer:
    def __init__(self, root):
        self.root = root
        self.root.title("画像リサイズツール")
        self.root.geometry("500x400")
        
        # 変数の初期化
        self.width_var = tk.StringVar(value="1024")
        self.height_var = tk.StringVar(value="1024")
        self.folder_path = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # フォルダ選択セクション
        folder_frame = ttk.LabelFrame(main_frame, text="フォルダ選択", padding="10")
        folder_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(folder_frame, text="画像フォルダ:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).grid(row=0, column=1, padx=(5, 5))
        ttk.Button(folder_frame, text="参照", command=self.select_folder).grid(row=0, column=2)
        
        # 解像度設定セクション
        size_frame = ttk.LabelFrame(main_frame, text="出力解像度設定", padding="10")
        size_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(size_frame, text="幅 (ピクセル):").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(size_frame, textvariable=self.width_var, width=10).grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(size_frame, text="高さ (ピクセル):").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(size_frame, textvariable=self.height_var, width=10).grid(row=0, column=3, padx=(5, 0))
        
        # アスペクト比保持チェックボックス
        self.keep_aspect_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(size_frame, text="アスペクト比を保持", variable=self.keep_aspect_var).grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
        
        # 処理ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="画像をリサイズ", command=self.resize_images, style="Accent.TButton").grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="クリア", command=self.clear_all).grid(row=0, column=1)
        
        # 進捗バー
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # ログ表示エリア
        log_frame = ttk.LabelFrame(main_frame, text="処理ログ", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=10, width=60)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # グリッドの重み設定
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 初期フォルダを現在のディレクトリに設定
        self.folder_path.set(os.getcwd())
    
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.log_message(f"フォルダを選択しました: {folder}")
    
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def get_image_files(self, folder_path):
        """フォルダ内の画像ファイルを取得"""
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff', '*.webp']
        image_files = []
        
        for ext in image_extensions:
            pattern = os.path.join(folder_path, ext)
            image_files.extend(glob.glob(pattern))
            # 大文字の拡張子も検索
            pattern = os.path.join(folder_path, ext.upper())
            image_files.extend(glob.glob(pattern))
        
        return sorted(image_files)
    
    def resize_images(self):
        """画像のリサイズ処理を実行"""
        try:
            folder = self.folder_path.get()
            if not folder or not os.path.exists(folder):
                messagebox.showerror("エラー", "有効なフォルダを選択してください。")
                return
            
            # 解像度の取得と検証
            try:
                target_width = int(self.width_var.get())
                target_height = int(self.height_var.get())
                #self.log_message(f"target_width: {target_width}, target_height: {target_height}")
                if target_width <= 0 or target_height <= 0:
                    raise ValueError("解像度は正の整数である必要があります。")
            except ValueError as e:
                messagebox.showerror("エラー", f"解像度の入力が無効です: {e}")
                return
            
            # 画像ファイルの取得
            image_files = self.get_image_files(folder)
            if not image_files:
                messagebox.showwarning("警告", "指定されたフォルダに画像ファイルが見つかりません。")
                return
            
            self.log_message(f"処理開始: {len(image_files)}個の画像ファイルを発見")
            
            # 進捗バーの設定
            self.progress_var.set(0)
            progress_step = 100.0 / len(image_files)
            
            processed_count = 0
            error_count = 0
            
            for i, image_path in enumerate(image_files):
                try:
                    # ファイル名の処理
                    filename = os.path.basename(image_path)
                    name, ext = os.path.splitext(filename)
                    new_filename = f"{name}_red{ext}"
                    output_path = os.path.join(folder, new_filename)
                    
                    # 画像の読み込みとリサイズ
                    with Image.open(image_path) as img:
                        # アスペクト比を保持する場合の処理
                        if self.keep_aspect_var.get():
                            img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                            resized_img = img
                        else:
                            resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                        
                        # 画像の保存
                        resized_img.save(output_path, quality=95, optimize=True)
                    
                    processed_count += 1
                    self.log_message(f"処理完了: {filename} → {new_filename}")
                    
                except Exception as e:
                    error_count += 1
                    self.log_message(f"エラー: {filename} - {str(e)}")
                
                # 進捗バーの更新
                self.progress_var.set((i + 1) * progress_step)
                self.root.update()
            
            # 処理完了メッセージ
            if error_count == 0:
                messagebox.showinfo("完了", f"すべての画像の処理が完了しました。\n処理済み: {processed_count}個")
            else:
                messagebox.showwarning("完了", f"処理が完了しました。\n処理済み: {processed_count}個\nエラー: {error_count}個")
            
            self.log_message("処理が完了しました。")
            
        except Exception as e:
            messagebox.showerror("エラー", f"予期しないエラーが発生しました: {str(e)}")
            self.log_message(f"エラー: {str(e)}")
    
    def clear_all(self):
        """ログをクリア"""
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)

def main():
    root = tk.Tk()
    app = ImageResizer(root)
    root.mainloop()

if __name__ == "__main__":
    main() 