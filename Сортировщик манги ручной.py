import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
from pathlib import Path

class BatchFolderOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Пакетный организатор папок")
        self.root.geometry("1400x900")
        
        self.source_folder = ""
        self.dest_folder = ""
        self.folders_data = []  # Список словарей с данными о папках
        self.selected_folders = set()  # Множество выбранных папок
        self.image_cache = {}  # Кэш для миниатюр
        
        # Стиль
        self.root.configure(bg='#2b2b2b')
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Верхняя панель с выбором папок
        top_frame = tk.Frame(self.root, bg='#3c3f41', pady=10)
        top_frame.pack(fill='x', padx=10)
        
        # Кнопки выбора
        btn_style = {'font': ('Arial', 10), 'height': 1, 'padx': 15}
        
        tk.Button(top_frame, text="📁 Выбрать исходную папку", 
                 command=self.select_source, bg='#4CAF50', fg='white',
                 **btn_style).pack(side='left', padx=5)
        
        tk.Button(top_frame, text="📂 Выбрать папку назначения", 
                 command=self.select_destination, bg='#2196F3', fg='white',
                 **btn_style).pack(side='left', padx=5)
        
        tk.Button(top_frame, text="🔄 Обновить список", 
                 command=self.load_folders, bg='#9C27B0', fg='white',
                 **btn_style).pack(side='left', padx=5)
        
        # Метки путей
        path_frame = tk.Frame(self.root, bg='#2b2b2b')
        path_frame.pack(fill='x', padx=10, pady=5)
        
        self.source_label = tk.Label(path_frame, text="Исходная папка: не выбрана", 
                                    bg='#2b2b2b', fg='white', anchor='w', 
                                    font=('Arial', 9))
        self.source_label.pack(fill='x', pady=2)
        
        self.dest_label = tk.Label(path_frame, text="Папка назначения: не выбрана", 
                                  bg='#2b2b2b', fg='white', anchor='w', 
                                  font=('Arial', 9))
        self.dest_label.pack(fill='x', pady=2)
        
        # Панель управления
        control_frame = tk.Frame(self.root, bg='#3c3f41', pady=8)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(control_frame, text="✅ ВЫБРАТЬ ВСЕ", 
                 command=self.select_all, bg='#8BC34A', fg='white',
                 font=('Arial', 10, 'bold'), padx=20).pack(side='left', padx=2)
        
        tk.Button(control_frame, text="❌ СНЯТЬ ВСЕ", 
                 command=self.deselect_all, bg='#F44336', fg='white',
                 font=('Arial', 10, 'bold'), padx=20).pack(side='left', padx=2)
        
        # Счетчики
        self.counter_label = tk.Label(control_frame, 
                                     text="Папок: 0 | Выбрано: 0", 
                                     bg='#3c3f41', fg='white', 
                                     font=('Arial', 11, 'bold'))
        self.counter_label.pack(side='left', padx=30)
        
        # Основной фрейм с папками и превью
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Левая часть - список папок с прокруткой
        left_frame = tk.Frame(main_frame, bg='#3c3f41', relief='flat', bd=0)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        tk.Label(left_frame, text="СПИСОК ПАПОК (кликните для просмотра):", 
                font=('Arial', 11, 'bold'), bg='#3c3f41', fg='white').pack(pady=10, padx=10)
        
        # Canvas для прокрутки списка папок
        folder_canvas = tk.Canvas(left_frame, bg='#2b2b2b', highlightthickness=0)
        folder_scrollbar = tk.Scrollbar(left_frame, orient="vertical", 
                                       command=folder_canvas.yview)
        self.folder_container = tk.Frame(folder_canvas, bg='#2b2b2b')
        
        self.folder_container.bind(
            "<Configure>",
            lambda e: folder_canvas.configure(scrollregion=folder_canvas.bbox("all"))
        )
        
        folder_canvas.create_window((0, 0), window=self.folder_container, anchor="nw")
        folder_canvas.configure(yscrollcommand=folder_scrollbar.set)
        
        folder_canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
        folder_scrollbar.pack(side="right", fill="y", pady=5)
        
        # Правая часть - превью фотографий выбранной папки
        right_frame = tk.Frame(main_frame, bg='#3c3f41', relief='flat', bd=0)
        right_frame.pack(side='right', fill='both', expand=True)
        
        tk.Label(right_frame, text="ПРЕВЬЮ ФОТОГРАФИЙ:", 
                font=('Arial', 11, 'bold'), bg='#3c3f41', fg='white').pack(pady=10)
        
        # Фрейм для информации о текущей папке
        self.current_folder_info = tk.Label(right_frame, 
                                          text="Выберите папку для просмотра фотографий", 
                                          bg='#4c5052', fg='white',
                                          font=('Arial', 10, 'bold'),
                                          relief='raised', bd=1, pady=8)
        self.current_folder_info.pack(fill='x', padx=10, pady=(0, 10))
        
        # Сетка для фотографий (4x3)
        self.photos_grid = tk.Frame(right_frame, bg='#3c3f41')
        self.photos_grid.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Создаем 12 ячеек для фотографий
        self.photo_labels = []
        for row in range(3):  # 3 ряда
            row_frame = tk.Frame(self.photos_grid, bg='#3c3f41')
            row_frame.pack(fill='both', expand=True, pady=2)
            for col in range(4):  # 4 колонки
                cell = tk.Frame(row_frame, bg='#2b2b2b', relief='sunken', bd=1, 
                               width=180, height=180)
                cell.pack(side='left', fill='both', expand=True, padx=2)
                cell.pack_propagate(False)
                
                # Лейбл для изображения
                img_label = tk.Label(cell, bg='#2b2b2b')
                img_label.pack(fill='both', expand=True, padx=2, pady=2)
                
                # Лейбл для названия файла
                name_label = tk.Label(cell, text="", bg='#2b2b2b', fg='white',
                                     font=('Arial', 8), pady=2)
                name_label.pack(fill='x', side='bottom')
                
                self.photo_labels.append((img_label, name_label, cell))
        
        # Кнопка переноса внизу
        bottom_frame = tk.Frame(self.root, bg='#2b2b2b', pady=10)
        bottom_frame.pack(fill='x', padx=10)
        
        self.transfer_btn = tk.Button(bottom_frame, text="🚀 ПЕРЕМЕСТИТЬ ВЫБРАННЫЕ ПАПКИ", 
                                     command=self.transfer_folders, bg='#FF5722', fg='white',
                                     font=('Arial', 14, 'bold'), height=2, 
                                     state='disabled', cursor='hand2')
        self.transfer_btn.pack(fill='x')
        
        self.progress_label = tk.Label(bottom_frame, text="", 
                                      bg='#2b2b2b', fg='white', 
                                      font=('Arial', 10))
        self.progress_label.pack(pady=5)
        
        # Предупреждение о перемещении
        warning_label = tk.Label(bottom_frame, 
                                text="⚠ ВНИМАНИЕ: Папки будут ПЕРЕМЕЩЕНЫ (удалены из исходной папки)", 
                                bg='#2b2b2b', fg='#FF9800',
                                font=('Arial', 9, 'bold'))
        warning_label.pack(pady=5)
    
    def select_source(self):
        folder = filedialog.askdirectory(title="Выберите исходную папку")
        if folder:
            self.source_folder = folder
            short_path = self.shorten_path(folder, 70)
            self.source_label.config(text=f"📁 Исходная папка: {short_path}")
            self.load_folders()
    
    def select_destination(self):
        folder = filedialog.askdirectory(title="Выберите папку назначения")
        if folder:
            self.dest_folder = folder
            short_path = self.shorten_path(folder, 70)
            self.dest_label.config(text=f"📂 Папка назначения: {short_path}")
            self.check_transfer_button()
    
    def shorten_path(self, path, max_length):
        if len(path) <= max_length:
            return path
        return "..." + path[-(max_length-3):]
    
    def load_folders(self):
        if not self.source_folder:
            messagebox.showwarning("Ошибка", "Сначала выберите исходную папку!")
            return
            
        # Очищаем контейнеры
        for widget in self.folder_container.winfo_children():
            widget.destroy()
        
        # Очищаем превью
        self.clear_photo_previews()
        
        self.folders_data = []
        self.selected_folders.clear()
        self.image_cache.clear()
        
        # Показываем сообщение о загрузке
        self.current_folder_info.config(text="Загрузка папок...")
        self.progress_label.config(text="Сканирование папок...")
        self.root.update()
        
        # Собираем папки
        folder_items = []
        try:
            for item in os.listdir(self.source_folder):
                item_path = os.path.join(self.source_folder, item)
                if os.path.isdir(item_path):
                    folder_items.append(item_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать папку: {e}")
            return
        
        if not folder_items:
            messagebox.showinfo("Информация", "В выбранной папке нет вложенных папок")
            return
        
        # Сортируем по имени
        folder_items.sort()
        
        # Запускаем загрузку в отдельном потоке
        thread = threading.Thread(target=self.process_folders, args=(folder_items,))
        thread.start()
    
    def process_folders(self, folder_items):
        total = len(folder_items)
        
        for idx, folder_path in enumerate(folder_items):
            folder_name = os.path.basename(folder_path)
            short_name = folder_name[:12] + "..." if len(folder_name) > 12 else folder_name
            
            # Создаем информацию о папке
            folder_info = {
                'path': folder_path,
                'name': folder_name,
                'short_name': short_name,
                'image_count': 0,
                'total_files': 0,
                'preview_images': [],
                'all_images': [],  # Все изображения для превью
                'number': idx + 1  # Номер папки
            }
            
            # Собираем ВСЕ изображения в папке
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic']
            try:
                for root, dirs, filenames in os.walk(folder_path):
                    for filename in filenames:
                        file_ext = os.path.splitext(filename.lower())[1]
                        if file_ext in image_extensions:
                            folder_info['all_images'].append(os.path.join(root, filename))
                
                folder_info['image_count'] = len(folder_info['all_images'])
                
                # Берем до 12 изображений для превью
                folder_info['preview_images'] = folder_info['all_images'][:12]
                
                # Считаем общее количество файлов
                for root, dirs, filenames in os.walk(folder_path):
                    folder_info['total_files'] += len(filenames)
                    
            except Exception as e:
                folder_info['error'] = str(e)
            
            self.folders_data.append(folder_info)
            
            # Обновляем интерфейс каждые 10 папок
            if idx % 10 == 0 or idx == total - 1:
                self.root.after(0, self.update_folder_list)
                self.root.after(0, self.update_progress, idx+1, total)
        
        self.root.after(0, self.finalize_loading)
    
    def update_folder_list(self):
        # Очищаем контейнер
        for widget in self.folder_container.winfo_children():
            widget.destroy()
        
        # Создаем виджеты для всех папок
        for folder_info in self.folders_data:
            self.create_folder_widget(folder_info)
        
        self.update_counters()
    
    def create_folder_widget(self, folder_info):
        folder_frame = tk.Frame(self.folder_container, bg='#3c3f41', 
                               relief='flat', bd=0, padx=5, pady=2)
        folder_frame.pack(fill='x', pady=1)
        
        # Внутренний фрейм для выделения
        inner_frame = tk.Frame(folder_frame, bg='#4c5052' if folder_info['path'] in self.selected_folders else '#3c3f41',
                              relief='raised' if folder_info['path'] in self.selected_folders else 'flat',
                              bd=1, cursor='hand2')
        inner_frame.pack(fill='x', padx=2, pady=2)
        
        # Фрейм для содержимого
        content_frame = tk.Frame(inner_frame, bg=inner_frame['bg'])
        content_frame.pack(fill='x', padx=10, pady=8)
        
        # Номер папки (слева, в кружке)
        number_frame = tk.Frame(content_frame, bg='#555', relief='raised', bd=1)
        number_frame.pack(side='left', padx=(0, 10))
        
        number_label = tk.Label(number_frame, text=str(folder_info['number']), 
                               bg='#555', fg='white', 
                               font=('Arial', 10, 'bold'),
                               width=3, height=1, padx=5, pady=3)
        number_label.pack()
        
        # Информация о папке (справа от номера)
        info_frame = tk.Frame(content_frame, bg=inner_frame['bg'])
        info_frame.pack(side='left', fill='x', expand=True)
        
        # Название папки
        short_name = folder_info['short_name']
        info_text = f"📁 {short_name}"
        
        # Добавляем информацию о количестве фото
        if folder_info['image_count'] > 0:
            info_text += f"   📸 {folder_info['image_count']}"
        
        # Добавляем индикатор выбора
        if folder_info['path'] in self.selected_folders:
            info_text = "✅ " + info_text
            selection_indicator = "● "
        else:
            selection_indicator = "○ "
        
        name_label = tk.Label(info_frame, text=info_text, 
                             bg=inner_frame['bg'], fg='white',
                             font=('Arial', 10), 
                             anchor='w', justify='left')
        name_label.pack(fill='x')
        
        # Дополнительная информация маленьким шрифтом
        if folder_info['total_files'] > 0:
            extra_info = f"Файлов: {folder_info['total_files']} | Выбрано: {selection_indicator}"
            extra_label = tk.Label(info_frame, text=extra_info,
                                 bg=inner_frame['bg'], fg='#aaaaaa',
                                 font=('Arial', 8),
                                 anchor='w', justify='left')
            extra_label.pack(fill='x', pady=(2, 0))
        
        # Функции для обработки событий
        def on_click(event):
            # Если Ctrl нажат - добавляем/убираем из выделения
            if event.state & 0x0004:  # Ctrl нажат
                self.toggle_folder_selection(folder_info['path'])
            else:
                # Показываем превью этой папки
                self.display_folder_preview(folder_info)
        
        def on_double_click(event):
            # Двойной клик переключает выделение
            self.toggle_folder_selection(folder_info['path'])
        
        # Привязываем события ко всем элементам
        for widget in [inner_frame, content_frame, number_frame, number_label, 
                      info_frame, name_label]:
            widget.bind('<Button-1>', on_click)
            widget.bind('<Double-Button-1>', on_double_click)
            widget.config(cursor='hand2')
        
        # Также привязываем к дополнительному лейблу, если он есть
        if folder_info['total_files'] > 0:
            extra_label.bind('<Button-1>', on_click)
            extra_label.bind('<Double-Button-1>', on_double_click)
            extra_label.config(cursor='hand2')
    
    def toggle_folder_selection(self, folder_path):
        if folder_path in self.selected_folders:
            self.selected_folders.remove(folder_path)
        else:
            self.selected_folders.add(folder_path)
        
        # Обновляем список папок
        self.update_folder_list()
        self.check_transfer_button()
    
    def display_folder_preview(self, folder_info):
        # Обновляем информацию о текущей папке
        folder_number = folder_info['number']
        folder_name = folder_info['name'][:20] + "..." if len(folder_info['name']) > 20 else folder_info['name']
        info_text = f"#{folder_number:03d} 📁 {folder_name}"
        if folder_info['image_count'] > 0:
            info_text += f" | 📸 Фото: {folder_info['image_count']}"
        if folder_info['total_files'] > 0:
            info_text += f" | 📄 Файлов: {folder_info['total_files']}"
        
        self.current_folder_info.config(text=info_text)
        
        # Очищаем превью
        self.clear_photo_previews()
        
        # Показываем фотографии
        if folder_info['preview_images']:
            for i, img_path in enumerate(folder_info['preview_images'][:12]):  # Максимум 12 фото
                if i >= len(self.photo_labels):
                    break
                    
                try:
                    # Загружаем и масштабируем изображение
                    img = Image.open(img_path)
                    img.thumbnail((160, 160))
                    photo = ImageTk.PhotoImage(img)
                    
                    img_label, name_label, cell = self.photo_labels[i]
                    
                    # Устанавливаем изображение
                    img_label.config(image=photo)
                    img_label.image = photo  # Сохраняем ссылку
                    
                    # Устанавливаем название файла (первые 10 символов)
                    filename = os.path.basename(img_path)
                    short_name = filename[:10] + "..." if len(filename) > 10 else filename
                    name_label.config(text=f"{i+1}. {short_name}")
                    
                    # Подсветка выбранной папки
                    if folder_info['path'] in self.selected_folders:
                        cell.config(bg='#4c5052')
                        name_label.config(bg='#4c5052')
                    else:
                        cell.config(bg='#2b2b2b')
                        name_label.config(bg='#2b2b2b')
                        
                except Exception as e:
                    img_label, name_label, cell = self.photo_labels[i]
                    img_label.config(text=f"{i+1}. Ошибка\nзагрузки", 
                                   font=('Arial', 8), fg='#ff4444')
                    name_label.config(text="")
        else:
            # Если нет изображений
            self.current_folder_info.config(
                text=f"#{folder_info['number']:03d} 📁 {folder_info['short_name']} | Нет изображений"
            )
    
    def clear_photo_previews(self):
        """Очищает все превью фотографий"""
        for img_label, name_label, cell in self.photo_labels:
            img_label.config(image='', text="")
            name_label.config(text="")
            cell.config(bg='#2b2b2b')
    
    def update_counters(self):
        self.counter_label.config(text=f"Папок: {len(self.folders_data)} | Выбрано: {len(self.selected_folders)}")
    
    def update_progress(self, processed, total):
        self.progress_label.config(text=f"Обработано {processed} из {total} папок")
    
    def check_transfer_button(self):
        if self.selected_folders and self.dest_folder:
            self.transfer_btn.config(state='normal', bg='#FF5722')
        else:
            self.transfer_btn.config(state='disabled', bg='#666666')
    
    def select_all(self):
        for folder_info in self.folders_data:
            self.selected_folders.add(folder_info['path'])
        self.update_folder_list()
        self.check_transfer_button()
    
    def deselect_all(self):
        self.selected_folders.clear()
        self.update_folder_list()
        self.check_transfer_button()
    
    def finalize_loading(self):
        self.update_folder_list()
        self.progress_label.config(text=f"Загружено {len(self.folders_data)} папок")
        
        if self.folders_data:
            # Показываем первую папку
            self.display_folder_preview(self.folders_data[0])
    
    def transfer_folders(self):
        if not self.selected_folders:
            messagebox.showwarning("Нет папок", "Вы не выбрали ни одной папки!")
            return
            
        if not self.dest_folder:
            messagebox.showwarning("Нет папки назначения", "Выберите папку назначения!")
            return
        
        # Создаем список выбранных папок с номерами
        selected_with_numbers = []
        for folder_info in self.folders_data:
            if folder_info['path'] in self.selected_folders:
                selected_with_numbers.append(folder_info)
        
        # Сортируем по номеру
        selected_with_numbers.sort(key=lambda x: x['number'])
        
        # Создаем текст для подтверждения
        confirm_text = f"Вы уверены, что хотите ПЕРЕМЕСТИТЬ {len(selected_with_numbers)} папок?\n\n"
        confirm_text += f"Из: {self.source_folder}\n"
        confirm_text += f"В: {self.dest_folder}\n\n"
        confirm_text += "Выбранные папки:\n"
        
        # Добавляем первые 10 папок в список
        for folder_info in selected_with_numbers[:10]:
            confirm_text += f"  #{folder_info['number']:03d} - {folder_info['name'][:30]}"
            if len(folder_info['name']) > 30:
                confirm_text += "..."
            confirm_text += "\n"
        
        if len(selected_with_numbers) > 10:
            confirm_text += f"  ... и ещё {len(selected_with_numbers) - 10} папок\n"
        
        confirm_text += "\n⚠ Папки будут УДАЛЕНЫ из исходной папки!"
        
        # Предупреждение о перемещении
        confirm = messagebox.askyesno("ПОДТВЕРЖДЕНИЕ ПЕРЕМЕЩЕНИЯ", confirm_text)
        if not confirm:
            return
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self._transfer_folders_thread, args=(selected_with_numbers,))
        thread.start()
    
    def _transfer_folders_thread(self, selected_with_numbers):
        total = len(selected_with_numbers)
        processed = 0
        errors = []
        
        # Создаем папку назначения, если её нет
        if not os.path.exists(self.dest_folder):
            try:
                os.makedirs(self.dest_folder)
            except Exception as e:
                self.root.after(0, messagebox.showerror, "Ошибка", 
                              f"Не удалось создать папку назначения: {e}")
                return
        
        # Перемещаем каждую выбранную папку
        for folder_info in selected_with_numbers:
            try:
                folder_path = folder_info['path']
                folder_name = folder_info['name']
                folder_number = folder_info['number']
                
                dest_path = os.path.join(self.dest_folder, folder_name)
                
                # Если папка уже существует в месте назначения
                if os.path.exists(dest_path):
                    # Добавляем номер папки к названию
                    base_name = f"{folder_number:03d}_{folder_name}"
                    dest_path = os.path.join(self.dest_folder, base_name)
                    
                    # Если и такое имя существует, добавляем суффикс
                    counter = 1
                    original_dest_path = dest_path
                    while os.path.exists(dest_path):
                        dest_path = f"{original_dest_path}_{counter}"
                        counter += 1
                
                # ПЕРЕМЕЩАЕМ папку (не копируем!)
                print(f"Перемещаем #{folder_number} {folder_path} -> {dest_path}")
                shutil.move(folder_path, dest_path)
                processed += 1
                
                # Обновляем прогресс
                self.root.after(0, self._update_transfer_progress, 
                              processed, total, folder_number, folder_name[:15])
                
            except Exception as e:
                error_msg = f"#{folder_info['number']:03d} {folder_info['name']}: {str(e)}"
                errors.append(error_msg)
                print(f"Ошибка при перемещении {folder_path}: {e}")
        
        self.root.after(0, self._transfer_complete, processed, total, errors)
    
    def _update_transfer_progress(self, processed, total, folder_number, current_folder):
        self.progress_label.config(
            text=f"Перемещение... {processed}/{total} | Текущая: #{folder_number:03d} {current_folder}"
        )
    
    def _transfer_complete(self, processed, total, errors):
        message = f"Перемещение завершено!\nУспешно перемещено: {processed} из {total} папок"
        
        if errors:
            error_text = "\n".join(errors[:5])  # Показываем только первые 5 ошибок
            if len(errors) > 5:
                error_text += f"\n... и ещё {len(errors) - 5} ошибок"
            message += f"\n\nОшибки:\n{error_text}"
        
        self.root.after(0, messagebox.showinfo, "Готово!", message)
        self.progress_label.config(text=f"Перемещение завершено! Перемещено {processed}/{total} папок")
        
        # Обновляем список (убираем перемещенные папки)
        self.selected_folders.clear()
        self.load_folders()

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchFolderOrganizer(root)
    root.mainloop()