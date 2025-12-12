import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import requests
import re
import time
import threading
import os
import pyperclip

class CompactDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Downloader")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        self.root.configure(bg="white")
        
        self.setup_styles()
        self.create_widgets()
        self.download_blocks = []
        self.add_download_block()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=6, background="#1976D2", foreground="white")
        style.configure("TProgressbar", thickness=15)

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="white")
        header_frame.pack(pady=10)
        
        tk.Label(header_frame, text="Universal Downloader", 
                font=("Arial", 14, "bold"), bg="white", fg="#333").pack()
        
        # Main container
        self.container = tk.Frame(self.root, bg="white")
        self.container.pack(fill="both", expand=True, padx=10)
        
        # Controls
        controls_frame = tk.Frame(self.root, bg="white")
        controls_frame.pack(pady=8)
        
        tk.Label(controls_frame, text="Задержка (сек):", bg="white", fg="#333").pack(side=tk.LEFT, padx=5)
        self.delay_var = tk.DoubleVar(value=1.0)
        tk.Entry(controls_frame, textvariable=self.delay_var, width=6, 
                bg="white", fg="black", relief="solid", bd=1).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="➕ Добавить список", 
                  command=self.add_download_block).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(controls_frame, text="⬇️ Скачать всё", 
                  command=self.download_all).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", 
                                       length=680, mode="determinate")
        self.progress.pack(pady=8)
        
        # Status log
        self.status_text = scrolledtext.ScrolledText(self.root, height=8, 
                                                   wrap=tk.WORD, bg="white", fg="black",
                                                   font=("Consolas", 9))
        self.status_text.pack(fill="both", expand=True, padx=10, pady=5)

    def choose_folder(self, var):
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)

    def paste_from_clipboard(self, text_box):
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content:
                text_box.insert(tk.END, clipboard_content)
                messagebox.showinfo("Успех", "Текст из буфера обмена вставлен!")
            else:
                messagebox.showwarning("Предупреждение", "Буфер обмена пуст")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось вставить из буфера: {str(e)}")

    def add_download_block(self):
        block = tk.Frame(self.container, bg="#F8F8F8", relief="solid", bd=1, padx=8, pady=8)
        block.pack(fill="x", pady=6)
        
        # URL input with paste button
        input_frame = tk.Frame(block, bg="#F8F8F8")
        input_frame.pack(fill="x", pady=4)
        
        text_box = scrolledtext.ScrolledText(input_frame, height=4, wrap=tk.WORD, 
                                           bg="white", fg="black", font=("Arial", 9))
        text_box.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Paste button next to text area
        paste_btn = ttk.Button(input_frame, text="📋 Вставить", 
                              command=lambda: self.paste_from_clipboard(text_box),
                              width=12)
        paste_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Folder selection
        folder_frame = tk.Frame(block, bg="#F8F8F8")
        folder_frame.pack(fill="x", pady=4)
        
        folder_var = tk.StringVar()
        folder_entry = tk.Entry(folder_frame, textvariable=folder_var, 
                               width=50, bg="white", fg="black", relief="solid", bd=1)
        folder_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(folder_frame, text="📁 Выбрать папку", 
                  command=lambda: self.choose_folder(folder_var)).pack(side=tk.LEFT, padx=5)
        
        self.download_blocks.append((text_box, folder_var))

    def detect_extension(self, url, response):
        content_type = response.headers.get("Content-Type", "").lower()
        
        type_map = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg", 
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "video/mp4": ".mp4",
            "video/webm": ".webm",
            "application/pdf": ".pdf"
        }
        
        for content, extension in type_map.items():
            if content in content_type:
                return extension
        
        # Fallback to URL extension
        ext = os.path.splitext(url.split("?")[0])[1]
        return ext if ext else ".bin"

    def download_all(self):
        delay = self.delay_var.get()
        all_urls = []
        
        for text_box, _ in self.download_blocks:
            content = text_box.get("1.0", tk.END)
            # Регулярное выражение корректно игнорирует окружающие кавычки
            urls = re.findall(r"https?://[^\s\"']+", content)
            all_urls.extend(urls)
        
        if not all_urls:
            messagebox.showerror("Ошибка", "Не найдено ссылок для загрузки.")
            return
        
        self.progress["maximum"] = len(all_urls)
        self.progress["value"] = 0
        
        self.status_text.config(state="normal")
        self.status_text.delete("1.0", tk.END)
        self.status_text.insert(tk.END, f"Начало загрузки {len(all_urls)} файлов...\n")
        self.status_text.config(state="disabled")
        
        def worker():
            counter = 0
            
            # 💡 КРИТИЧНОЕ ИЗМЕНЕНИЕ: Добавляем User-Agent для обхода ошибки 403
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            for block_idx, (text_box, folder_var) in enumerate(self.download_blocks, 1):
                content = text_box.get("1.0", tk.END)
                urls = re.findall(r"https?://[^\s\"']+", content)
                folder = folder_var.get()
                
                if not urls or not folder:
                    self.status_text.config(state="normal")
                    self.status_text.insert(tk.END, f"[{block_idx}] ⚠️ Пропущен: нет ссылок или не выбрана папка\n")
                    self.status_text.see(tk.END)
                    self.status_text.config(state="disabled")
                    continue
                
                os.makedirs(folder, exist_ok=True)
                
                for i, url in enumerate(urls):
                    try:
                        # Используем заголовки при запросе
                        response = requests.get(url, headers=headers, timeout=15, stream=True)
                        if response.status_code == 200:
                            ext = self.detect_extension(url, response)
                            # Имя файла на основе номера в списке и расширения
                            filename = f"file_{i+1}{ext}" 
                            filepath = os.path.join(folder, filename)
                            
                            with open(filepath, "wb") as f:
                                for chunk in response.iter_content(1024 * 32):
                                    f.write(chunk)
                            
                            log = f"[{block_idx}] ✅ {filename} (Скачано)\n"
                        else:
                            # Ошибки, такие как 403 Forbidden, 404 Not Found
                            log = f"[{block_idx}] ⚠️ Ошибка HTTP {response.status_code} для: {url[:60]}...\n"
                            
                    except Exception as e:
                        # Ошибки, такие как проблемы с сетью или таймаут
                        log = f"[{block_idx}] ❌ Ошибка сети/Таймаут: {str(e)[:50]}...\n"
                    
                    counter += 1
                    # Обновление прогресс-бара и лога в GUI
                    self.root.after(0, lambda c=counter, l=log: self.update_status(c, l)) 
                    
                    time.sleep(delay)
            
            self.root.after(0, lambda: messagebox.showinfo("Готово", f"Загружено файлов: {counter}"))
        
        threading.Thread(target=worker, daemon=True).start()

    def update_status(self, counter, log):
        # Метод для безопасного обновления GUI из потока worker
        self.progress["value"] = counter
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, log)
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = CompactDownloader(root)
    root.mainloop()