import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import requests
import re
import time
import threading
import pyperclip
import os

# --- JS код для копирования ---
JS_CODE = """var imageUrls = [];

var observer = new MutationObserver(function(mutations) {
  mutations.forEach(function(mutation) {
    if (mutation.addedNodes) {
      for (var i = 0; i < mutation.addedNodes.length; i++) {
        var node = mutation.addedNodes[i];
        if (node.tagName === 'IMG') {
          var src = node.src;
          if (src && !imageUrls.includes(src)) {
            imageUrls.push(src);
            console.log('Новое изображение найдено:', src);
          }
        }
      }
    }
  });
});

observer.observe(document.body, { childList: true, subtree: true });

var initialImages = document.getElementsByTagName('img');
for (var i = 0; i < initialImages.length; i++) {
  var src = initialImages[i].src;
  if (src && !imageUrls.includes(src)) {
    imageUrls.push(src);
  }
}
console.log('Начальный список изображений:', imageUrls);
"""

# --- Основное окно ---
root = tk.Tk()
root.title("Загрузчик изображений")
root.geometry("720x600")
root.resizable(False, False)
root.configure(bg="#2b2b2b")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", padding=6, relief="flat", background="#4CAF50", foreground="white")
style.configure("TProgressbar", thickness=18)

# --- Функции ---
def paste_from_clipboard(target_box):
    text = pyperclip.paste()
    target_box.insert(tk.END, text + "\n")

def copy_js_code():
    pyperclip.copy(JS_CODE)
    messagebox.showinfo("Скопировано", "Код для наблюдения за изображениями скопирован в буфер обмена!")

def choose_folder(var):
    folder = filedialog.askdirectory()
    if folder:
        var.set(folder)

def add_download_block():
    block = tk.Frame(container, bg="#3c3c3c", bd=1, relief="ridge", padx=5, pady=5)
    block.pack(fill="x", pady=6, padx=8)

    text_box = scrolledtext.ScrolledText(block, height=5, width=70, wrap=tk.WORD, bg="#1e1e1e", fg="white")
    text_box.pack(padx=4, pady=4)
    
    btns = tk.Frame(block, bg="#3c3c3c")
    btns.pack(pady=3)
    
    ttk.Button(btns, text="📋 Вставить из буфера", command=lambda: paste_from_clipboard(text_box)).pack(side=tk.LEFT, padx=5)
    
    folder_var = tk.StringVar()
    entry = tk.Entry(btns, textvariable=folder_var, width=40, bg="#2b2b2b", fg="white", relief="flat")
    entry.pack(side=tk.LEFT, padx=5)
    ttk.Button(btns, text="📂 Папка", command=lambda: choose_folder(folder_var)).pack(side=tk.LEFT, padx=5)

    download_blocks.append((text_box, folder_var))

def download_all():
    delay = delay_var.get()
    total_urls = 0
    all_urls = []
    for text_box, _ in download_blocks:
        urls = re.findall(r'"(https?://.*?)"', text_box.get("1.0", tk.END))
        all_urls.extend(urls)
    if not all_urls:
        messagebox.showerror("Ошибка", "Не найдено ни одной ссылки для загрузки.")
        return

    progress["maximum"] = len(all_urls)
    progress["value"] = 0
    status_text.config(state="normal")
    status_text.delete("1.0", tk.END)
    status_text.insert(tk.END, f"🔄 Начало загрузки ({len(all_urls)} файлов)...\n")
    status_text.config(state="disabled")

    def worker():
        counter = 0
        for block_index, (text_box, folder_var) in enumerate(download_blocks, start=1):
            urls = re.findall(r'"(https?://.*?)"', text_box.get("1.0", tk.END))
            folder = folder_var.get()
            if not urls or not folder:
                continue
            os.makedirs(folder, exist_ok=True)
            for i, url in enumerate(urls):
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        ext = os.path.splitext(url.split("?")[0])[1] or ".jpg"
                        filename = os.path.join(folder, f"image_{i+1}{ext}")
                        with open(filename, "wb") as f:
                            f.write(response.content)
                        log = f"[Список {block_index}] ✅ image_{i+1}{ext}\n"
                    else:
                        log = f"[Список {block_index}] ⚠️ Код {response.status_code}: {url}\n"
                except Exception as e:
                    log = f"[Список {block_index}] ❌ Ошибка: {e}\n"

                counter += 1
                progress["value"] = counter
                status_text.config(state="normal")
                status_text.insert(tk.END, log)
                status_text.config(state="disabled")
                status_text.see(tk.END)
                time.sleep(delay)
        messagebox.showinfo("Готово", f"Все загрузки завершены ({counter} файлов)!")

    threading.Thread(target=worker, daemon=True).start()

# --- Верхняя панель ---
top_frame = tk.Frame(root, bg="#2b2b2b")
top_frame.pack(pady=10)
ttk.Button(top_frame, text="📜 Скопировать JS для сбора ссылок", command=copy_js_code).pack()

# --- Контейнер для списков ---
container = tk.Frame(root, bg="#2b2b2b")
container.pack(fill="both", expand=True)

download_blocks = []
add_download_block()  # первый список

ttk.Button(root, text="➕ Добавить ещё список", command=add_download_block).pack(pady=5)

# --- Настройки и запуск ---
bottom_frame = tk.Frame(root, bg="#2b2b2b")
bottom_frame.pack(pady=10)
tk.Label(bottom_frame, text="Задержка (сек):", fg="white", bg="#2b2b2b").pack(side=tk.LEFT, padx=5)
delay_var = tk.DoubleVar(value=1.0)
tk.Entry(bottom_frame, textvariable=delay_var, width=6, justify="center", bg="#1e1e1e", fg="white", relief="flat").pack(side=tk.LEFT, padx=5)
ttk.Button(bottom_frame, text="⬇️ Скачать всё", command=download_all).pack(side=tk.LEFT, padx=10)

# --- Прогресс и статус ---
progress = ttk.Progressbar(root, orient="horizontal", length=680, mode="determinate")
progress.pack(pady=5)

status_text = scrolledtext.ScrolledText(root, height=8, width=85, wrap=tk.WORD, bg="#1e1e1e", fg="white")
status_text.pack(padx=10, pady=5)

root.mainloop()
