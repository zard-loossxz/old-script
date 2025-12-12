import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading

class FileListerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сборщик имен файлов")
        self.root.geometry("700x450")
        
        # Переменные
        self.folder_path = tk.StringVar()
        self.save_path = tk.StringVar()
        self.include_subfolders = tk.BooleanVar(value=True)
        self.progress = tk.DoubleVar()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка расширения сетки
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Выбор папки для сканирования
        ttk.Label(main_frame, text="Выберите папку для сканирования:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        scan_frame = ttk.Frame(main_frame)
        scan_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        scan_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(scan_frame, textvariable=self.folder_path).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(scan_frame, text="Обзор", command=self.browse_scan_folder).grid(row=0, column=1)
        
        # Выбор пути сохранения
        ttk.Label(main_frame, text="Куда сохранить список файлов:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        save_frame = ttk.Frame(main_frame)
        save_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        save_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(save_frame, textvariable=self.save_path).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(save_frame, text="Обзор", command=self.browse_save_location).grid(row=0, column=1)
        
        # Опции
        options_frame = ttk.LabelFrame(main_frame, text="Опции", padding="5")
        options_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Checkbutton(options_frame, text="Включая подпапки", 
                       variable=self.include_subfolders).grid(row=0, column=0, sticky=tk.W)
        
        # Кнопка запуска
        ttk.Button(main_frame, text="Собрать имена файлов", 
                  command=self.start_file_listing).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Прогресс-бар
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="Готов к работе")
        self.status_label.grid(row=7, column=0, columnspan=2, pady=5)
        
        # Текстовое поле для предпросмотра
        ttk.Label(main_frame, text="Предпросмотр (первые 20 файлов):").grid(row=8, column=0, sticky=tk.W, pady=(10, 0))
        
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.preview_text = tk.Text(text_frame, height=10, width=70)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Настройка расширения для основного фрейма
        main_frame.rowconfigure(9, weight=1)
    
    def browse_scan_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку для сканирования")
        if folder:
            self.folder_path.set(folder)
            # Предлагаем автоматическое имя для файла сохранения
            default_save = os.path.join(os.path.dirname(folder), "file_list.txt")
            self.save_path.set(default_save)
    
    def browse_save_location(self):
        file_path = filedialog.asksaveasfilename(
            title="Куда сохранить список файлов",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if file_path:
            self.save_path.set(file_path)
    
    def start_file_listing(self):
        folder = self.folder_path.get()
        save_path = self.save_path.get()
        
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Ошибка", "Пожалуйста, выберите существующую папку для сканирования")
            return
        
        if not save_path:
            messagebox.showerror("Ошибка", "Пожалуйста, укажите путь для сохранения файла")
            return
        
        # Создаем директорию для сохранения если ее нет
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать директорию для сохранения:\n{str(e)}")
                return
        
        # Запуск в отдельном потоке чтобы не блокировать GUI
        thread = threading.Thread(target=self.list_files)
        thread.daemon = True
        thread.start()
    
    def list_files(self):
        folder = self.folder_path.get()
        save_path = self.save_path.get()
        include_subfolders = self.include_subfolders.get()
        
        try:
            self.update_status("Поиск файлов...")
            self.progress.set(0)
            
            # Собираем все файлы
            all_files = []
            
            if include_subfolders:
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        full_path = os.path.join(root, file)
                        relative_path = os.path.relpath(full_path, folder)
                        all_files.append(relative_path)
            else:
                for item in os.listdir(folder):
                    full_path = os.path.join(folder, item)
                    if os.path.isfile(full_path):
                        all_files.append(item)
            
            self.progress.set(50)
            self.update_status(f"Найдено {len(all_files)} файлов. Сохранение...")
            
            # Сохраняем в файл
            with open(save_path, 'w', encoding='utf-8') as f:
                # Записываем заголовок с информацией
                f.write(f"Список файлов из папки: {folder}\n")
                f.write(f"Всего файлов: {len(all_files)}\n")
                f.write(f"Включая подпапки: {'Да' if include_subfolders else 'Нет'}\n")
                f.write("=" * 50 + "\n\n")
                
                # Записываем файлы
                for file_path in all_files:
                    f.write(file_path + '\n')
            
            self.progress.set(100)
            self.update_status(f"Готово! Сохранено в: {save_path}")
            
            # Показываем превью
            preview_text = f"Всего файлов: {len(all_files)}\n\n"
            preview_text += "\n".join(all_files[:20])
            if len(all_files) > 20:
                preview_text += f"\n\n... и еще {len(all_files) - 20} файлов"
            
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, preview_text)
            
            messagebox.showinfo("Готово", 
                              f"Список файлов сохранен в:\n{save_path}\n\n"
                              f"Найдено файлов: {len(all_files)}\n"
                              f"Папка сканирования: {folder}")
            
        except Exception as e:
            self.update_status("Ошибка!")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
    
    def update_status(self, message):
        # Обновляем статус в основном потоке
        self.root.after(0, lambda: self.status_label.config(text=message))

def main():
    root = tk.Tk()
    app = FileListerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()