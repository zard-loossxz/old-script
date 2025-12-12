import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import random
import string
from pathlib import Path
import math

class FileRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer - Rename All & Distribute")
        self.root.geometry("600x450")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Заголовок
        title_label = tk.Label(self.root, text="Переименование всех файлов и распределение по папкам", 
                              font=("Arial", 12, "bold"))
        title_label.pack(pady=10)
        
        # Выбор папки
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(folder_frame, text="Выберите корневую папку:").pack(anchor="w")
        
        self.folder_path = tk.StringVar()
        path_entry = tk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(folder_frame, text="Обзор", command=self.browse_folder)
        browse_btn.pack(side="right")
        
        # Настройки переименования файлов
        rename_frame = tk.LabelFrame(self.root, text="Настройки переименования файлов")
        rename_frame.pack(pady=10, padx=20, fill="x")
        
        # Длина имени файла
        tk.Label(rename_frame, text="Длина имени файла:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.file_name_length = tk.IntVar(value=8)
        file_length_spin = tk.Spinbox(rename_frame, from_=4, to=20, width=5,
                                     textvariable=self.file_name_length)
        file_length_spin.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Префикс для файлов
        tk.Label(rename_frame, text="Префикс файлов:").grid(row=0, column=2, sticky="w", padx=10, pady=5)
        self.file_prefix = tk.StringVar()
        file_prefix_entry = tk.Entry(rename_frame, textvariable=self.file_prefix, width=15)
        file_prefix_entry.grid(row=0, column=3, padx=(10, 0), pady=5)
        
        # Сохранять расширения
        self.keep_extensions = tk.BooleanVar(value=True)
        ext_check = tk.Checkbutton(rename_frame, text="Сохранять расширения файлов",
                                  variable=self.keep_extensions)
        ext_check.grid(row=1, column=0, columnspan=4, sticky="w", padx=10, pady=5)
        
        # Настройки распределения по папкам
        dist_frame = tk.LabelFrame(self.root, text="Настройки распределения по папкам")
        dist_frame.pack(pady=10, padx=20, fill="x")
        
        # Включить распределение
        self.enable_distribution = tk.BooleanVar(value=True)
        dist_check = tk.Checkbutton(dist_frame, text="Включить распределение файлов по подпапкам",
                                   variable=self.enable_distribution, command=self.toggle_distribution)
        dist_check.grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=5)
        
        # Настройки распределения (появляются только когда включено)
        self.dist_settings_frame = tk.Frame(dist_frame)
        self.dist_settings_frame.grid(row=1, column=0, columnspan=4, sticky="w", padx=20, pady=5)
        
        # Порог для создания подпапок
        tk.Label(self.dist_settings_frame, text="Создавать подпапки если файлов больше:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=2)
        self.files_threshold = tk.IntVar(value=100)
        threshold_spin = tk.Spinbox(self.dist_settings_frame, from_=10, to=1000, width=5,
                                   textvariable=self.files_threshold)
        threshold_spin.grid(row=0, column=1, padx=(0, 20), pady=2)
        
        # Оставлять в основной папке
        tk.Label(self.dist_settings_frame, text="Оставлять в основной папке:").grid(row=0, column=2, sticky="w", padx=(0, 10), pady=2)
        self.keep_in_main = tk.IntVar(value=100)
        keep_spin = tk.Spinbox(self.dist_settings_frame, from_=10, to=500, width=5,
                              textvariable=self.keep_in_main)
        keep_spin.grid(row=0, column=3, pady=2)
        
        # Настройки имен папок
        tk.Label(self.dist_settings_frame, text="Длина имени папки:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=2)
        self.folder_name_length = tk.IntVar(value=8)
        folder_length_spin = tk.Spinbox(self.dist_settings_frame, from_=4, to=15, width=5,
                                       textvariable=self.folder_name_length)
        folder_length_spin.grid(row=1, column=1, padx=(0, 20), pady=2)
        
        tk.Label(self.dist_settings_frame, text="Префикс папок:").grid(row=1, column=2, sticky="w", padx=(0, 10), pady=2)
        self.folder_prefix = tk.StringVar(value="sub")
        folder_prefix_entry = tk.Entry(self.dist_settings_frame, textvariable=self.folder_prefix, width=15)
        folder_prefix_entry.grid(row=1, column=3, pady=2)
        
        # Информация
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5, padx=20, fill="x")
        
        self.stats_label = tk.Label(info_frame, text="Статистика: выберите папку и нажмите 'Сканировать'", 
                                   font=("Arial", 9))
        self.stats_label.pack(anchor="w")
        
        # Прогресс бар
        self.progress = ttk.Progressbar(self.root, mode='determinate')
        self.progress.pack(pady=10, padx=20, fill="x")
        
        # Кнопки
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.scan_btn = tk.Button(button_frame, text="Сканировать файлы", 
                                 command=self.scan_files, state="disabled",
                                 bg="#2196F3", fg="white", font=("Arial", 10))
        self.scan_btn.pack(side="left", padx=5)
        
        self.process_btn = tk.Button(button_frame, text="Переименовать и распределить", 
                                   command=self.process_all, state="disabled",
                                   bg="#4CAF50", fg="white", font=("Arial", 10))
        self.process_btn.pack(side="left", padx=5)
        
        # Статус
        self.status_label = tk.Label(self.root, text="Выберите папку для начала")
        self.status_label.pack()
        
        # Данные
        self.all_files = []
        self.folder_stats = {}
        
        self.toggle_distribution()
        
    def toggle_distribution(self):
        """Показывает/скрывает настройки распределения"""
        if self.enable_distribution.get():
            self.dist_settings_frame.grid()
        else:
            self.dist_settings_frame.grid_remove()
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.scan_btn.config(state="normal")
            self.status_label.config(text=f"Выбрана папка: {folder}")
            self.all_files = []
            self.folder_stats = {}
            self.update_stats()
            
    def scan_files(self):
        """Сканирует все файлы рекурсивно"""
        folder_path = self.folder_path.get()
        
        if not folder_path or not os.path.exists(folder_path):
            messagebox.showerror("Ошибка", "Пожалуйста, выберите существующую папку")
            return
            
        try:
            self.all_files = []
            self.folder_stats = {}
            total_folders = 0
            
            self.status_label.config(text="Сканирование...")
            self.progress['mode'] = 'indeterminate'
            self.progress.start()
            
            # Рекурсивно обходим все папки и собираем файлы
            for root_dir, dirs, files in os.walk(folder_path):
                total_folders += 1
                file_count = len(files)
                
                # Собираем все файлы
                for filename in files:
                    file_path = Path(root_dir) / filename
                    self.all_files.append(file_path)
                
                # Для распределения: запоминаем папки с большим количеством файлов
                if self.enable_distribution.get() and file_count >= self.files_threshold.get():
                    self.folder_stats[root_dir] = {
                        'file_count': file_count,
                        'files': [Path(root_dir) / f for f in files]
                    }
                
                if total_folders % 10 == 0:
                    self.status_label.config(text=f"Сканировано папок: {total_folders}, файлов: {len(self.all_files)}")
                    self.root.update_idletasks()
            
            self.progress.stop()
            self.progress['mode'] = 'determinate'
            self.progress['value'] = 0
            
            self.status_label.config(text=f"Сканирование завершено: {len(self.all_files)} файлов в {total_folders} папках")
            
            if self.all_files:
                self.process_btn.config(state="normal")
            else:
                messagebox.showinfo("Информация", "В выбранной папке нет файлов")
                self.process_btn.config(state="disabled")
                
            self.update_stats()
                
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Ошибка", f"Ошибка при сканировании: {str(e)}")
    
    def update_stats(self):
        """Обновляет статистику в интерфейсе"""
        if not self.all_files:
            self.stats_label.config(text="Статистика: выберите папку и нажмите 'Сканировать'")
            return
            
        stats_text = f"Всего файлов: {len(self.all_files)}\n"
        
        if self.enable_distribution.get() and self.folder_stats:
            stats_text += f"Папок для распределения: {len(self.folder_stats)} (файлов > {self.files_threshold.get()})"
        elif self.enable_distribution.get():
            stats_text += f"Папок для распределения: 0 (файлов > {self.files_threshold.get()} не найдено)"
        else:
            stats_text += "Распределение отключено - все файлы останутся в исходных папках"
            
        self.stats_label.config(text=stats_text)
    
    def generate_unique_filename(self, existing_names, extension=""):
        """Генерирует уникальное имя файла"""
        chars = string.ascii_letters + string.digits
        
        while True:
            random_name = ''.join(random.choice(chars) for _ in range(self.file_name_length.get()))
            
            # Добавляем префикс если указан
            prefix = self.file_prefix.get().strip()
            if prefix:
                random_name = f"{prefix}_{random_name}"
            
            if extension and self.keep_extensions.get():
                full_name = f"{random_name}{extension}"
            else:
                full_name = random_name
                
            if full_name not in existing_names:
                return full_name
    
    def generate_folder_name(self, parent_folder):
        """Генерирует уникальное имя для подпапки"""
        chars = string.ascii_letters + string.digits
        parent_path = Path(parent_folder)
        
        while True:
            random_name = ''.join(random.choice(chars) for _ in range(self.folder_name_length.get()))
            
            prefix = self.folder_prefix.get().strip()
            if prefix:
                folder_name = f"{prefix}_{random_name}"
            else:
                folder_name = random_name
                
            # Проверяем что папка с таким именем не существует
            potential_path = parent_path / folder_name
            if not potential_path.exists():
                return folder_name
    
    def process_all(self):
        """Основная функция обработки - переименовывает ВСЕ файлы и распределяет при необходимости"""
        if not self.all_files:
            return
            
        try:
            # Подтверждение
            confirm_msg = f"Будет переименовано ВСЕХ {len(self.all_files)} файлов во всех папках.\n\n"
            
            if self.enable_distribution.get() and self.folder_stats:
                confirm_msg += f"Дополнительно в {len(self.folder_stats)} папках с {self.files_threshold.get()}+ файлами:\n"
                confirm_msg += f"- Будет оставлено по {self.keep_in_main.get()} файлов\n"
                confirm_msg += f"- Остальные файлы перемещены в подпапки\n\n"
            
            confirm_msg += "ВСЕ файлы получат случайные уникальные имена.\n\nПродолжить?"
            
            if not messagebox.askyesno("Подтверждение", confirm_msg):
                return
            
            # Генерируем уникальные имена для ВСЕХ файлов
            self.status_label.config(text="Генерация уникальных имен для всех файлов...")
            self.progress['maximum'] = len(self.all_files) + (len(self.folder_stats) * 10 if self.enable_distribution.get() else 0)
            self.progress['value'] = 0
            
            existing_names = set()
            rename_plan = []
            
            # Планируем переименование для всех файлов
            for file_path in self.all_files:
                extension = file_path.suffix if self.keep_extensions.get() else ""
                new_name = self.generate_unique_filename(existing_names, extension)
                existing_names.add(new_name)
                
                # Определяем куда перемещать файл
                if self.enable_distribution.get() and str(file_path.parent) in self.folder_stats:
                    # Этот файл в папке которая будет распределяться - решение о перемещении примем позже
                    rename_plan.append((file_path, new_name, None))
                else:
                    # Файл остается в своей папке
                    new_path = file_path.parent / new_name
                    rename_plan.append((file_path, new_name, new_path))
                
                self.progress['value'] += 1
                if self.progress['value'] % 100 == 0:
                    self.status_label.config(text=f"Подготовка: {self.progress['value']}/{len(self.all_files)}")
                    self.root.update_idletasks()
            
            # Обрабатываем распределение для папок с большим количеством файлов
            if self.enable_distribution.get():
                self.process_distribution(rename_plan)
            
            # Выполняем переименование
            self.status_label.config(text="Переименование файлов...")
            success_count = 0
            failed_files = []
            
            for i, (old_path, new_name, new_path) in enumerate(rename_plan):
                if new_path is None:
                    continue  # Уже обработано в распределении
                    
                try:
                    if old_path.exists():
                        old_path.rename(new_path)
                        success_count += 1
                    else:
                        failed_files.append(f"Файл не найден: {old_path}")
                except Exception as e:
                    failed_files.append(f"{old_path} - {str(e)}")
                
                if (i + 1) % 50 == 0:
                    self.status_label.config(text=f"Переименовано: {i+1}/{len(rename_plan)}")
                    self.root.update_idletasks()
            
            # Результат
            result_msg = f"Переименовано файлов: {success_count}/{len(self.all_files)}"
            
            if failed_files:
                result_msg += f"\n\nОшибки ({len(failed_files)}):\n" + "\n".join(failed_files[:5])
                if len(failed_files) > 5:
                    result_msg += f"\n... и еще {len(failed_files) - 5} ошибок"
            
            messagebox.showinfo("Готово", result_msg)
            self.status_label.config(text=f"Готово! Переименовано {success_count} файлов")
            self.process_btn.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
    
    def process_distribution(self, rename_plan):
        """Обрабатывает распределение файлов по подпапкам"""
        self.status_label.config(text="Распределение файлов по подпапкам...")
        
        # Группируем файлы по папкам
        folder_files = {}
        for old_path, new_name, new_path in rename_plan:
            if new_path is None:  # Файлы которые нужно распределить
                folder_path = str(old_path.parent)
                if folder_path not in folder_files:
                    folder_files[folder_path] = []
                folder_files[folder_path].append((old_path, new_name))
        
        # Обрабатываем каждую папку
        for folder_path, files in folder_files.items():
            keep_count = self.keep_in_main.get()
            
            if len(files) <= keep_count:
                # Если файлов меньше лимита - оставляем все в основной папке
                for old_path, new_name in files:
                    new_path = Path(folder_path) / new_name
                    # Обновляем план переименования
                    for i, (op, nn, np) in enumerate(rename_plan):
                        if op == old_path and nn == new_name:
                            rename_plan[i] = (op, nn, new_path)
                            break
                continue
            
            # Перемешиваем файлы для случайного выбора
            random.shuffle(files)
            
            # Файлы которые остаются в основной папке
            files_to_keep = files[:keep_count]
            for old_path, new_name in files_to_keep:
                new_path = Path(folder_path) / new_name
                # Обновляем план переименования
                for i, (op, nn, np) in enumerate(rename_plan):
                    if op == old_path and nn == new_name:
                        rename_plan[i] = (op, nn, new_path)
                        break
            
            # Файлы которые перемещаем в подпапки
            files_to_move = files[keep_count:]
            
            # Создаем подпапки и распределяем файлы
            files_per_subfolder = 100
            file_groups = [files_to_move[i:i + files_per_subfolder] 
                          for i in range(0, len(files_to_move), files_per_subfolder)]
            
            for group in file_groups:
                # Создаем подпапку
                subfolder_name = self.generate_folder_name(folder_path)
                subfolder_path = Path(folder_path) / subfolder_name
                subfolder_path.mkdir()
                
                # Перемещаем файлы в подпапку
                for old_path, new_name in group:
                    new_path = subfolder_path / new_name
                    # Обновляем план переименования
                    for i, (op, nn, np) in enumerate(rename_plan):
                        if op == old_path and nn == new_name:
                            rename_plan[i] = (op, nn, new_path)
                            break
                
                self.progress['value'] += 1
                self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamer(root)
    root.mainloop()