import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from pathlib import Path

class FileRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Renamer")
        self.root.geometry("900x700")
        
        self.files = []
        self.file_numbers = {}  # Словарь для хранения номеров файлов
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Source directory selection
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(dir_frame, text="Папка с файлами:").grid(row=0, column=0, sticky=tk.W)
        self.dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.dir_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(dir_frame, text="Обзор", command=self.browse_directory).grid(row=0, column=2)
        
        # New name pattern
        name_frame = ttk.Frame(main_frame)
        name_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(name_frame, text="Новый шаблон названия:").grid(row=0, column=0, sticky=tk.W)
        
        # Frame for name entry and paste button
        name_entry_frame = ttk.Frame(name_frame)
        name_entry_frame.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.name_pattern_var = tk.StringVar(value="file")
        self.name_entry = ttk.Entry(name_entry_frame, textvariable=self.name_pattern_var, width=30)
        self.name_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Paste button
        ttk.Button(name_entry_frame, text="Вставить", command=self.paste_from_clipboard, width=8).grid(row=0, column=1, padx=5)
        
        ttk.Label(name_frame, text="Расширение:").grid(row=0, column=2, padx=(20, 0))
        
        self.ext_var = tk.StringVar(value="cbr")
        ext_combo = ttk.Combobox(name_frame, textvariable=self.ext_var, values=["cbr", "cbz", "zip", "rar"], width=10)
        ext_combo.grid(row=0, column=3, padx=5)
        
        # Files listbox with scrollbar
        list_frame = ttk.LabelFrame(main_frame, text="Файлы для переименования", padding="5")
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create treeview for files with numbers
        columns = ("number", "filename")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="extended")
        
        self.tree.heading("number", text="№")
        self.tree.heading("filename", text="Имя файла")
        
        self.tree.column("number", width=60, anchor="center")
        self.tree.column("filename", width=600, anchor="w")
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind double click for editing numbers
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Return>", self.on_double_click)
        self.tree.bind("<Up>", self.move_up)
        self.tree.bind("<Down>", self.move_down)
        self.tree.bind("<Control-Up>", self.move_to_top)
        self.tree.bind("<Control-Down>", self.move_to_bottom)
        
        # Move buttons
        move_frame = ttk.Frame(list_frame)
        move_frame.grid(row=0, column=2, padx=10, sticky=(tk.N, tk.S))
        
        ttk.Button(move_frame, text="↑ Вверх", command=self.move_up).grid(row=0, column=0, pady=2, sticky=tk.EW)
        ttk.Button(move_frame, text="↓ Вниз", command=self.move_down).grid(row=1, column=0, pady=2, sticky=tk.EW)
        ttk.Button(move_frame, text="В начало", command=self.move_to_top).grid(row=2, column=0, pady=2, sticky=tk.EW)
        ttk.Button(move_frame, text="В конец", command=self.move_to_bottom).grid(row=3, column=0, pady=2, sticky=tk.EW)
        ttk.Button(move_frame, text="Удалить", command=self.remove_file).grid(row=4, column=0, pady=10, sticky=tk.EW)
        
        # Number assignment frame
        number_frame = ttk.Frame(main_frame)
        number_frame.grid(row=3, column=0, columnspan=3, pady=5)
        
        ttk.Label(number_frame, text="Назначить номера:").grid(row=0, column=0, sticky=tk.W)
        self.start_number_var = tk.StringVar(value="1")
        ttk.Entry(number_frame, textvariable=self.start_number_var, width=5).grid(row=0, column=1, padx=5)
        ttk.Button(number_frame, text="Применить к выделенным", command=self.assign_numbers).grid(row=0, column=2, padx=5)
        ttk.Button(number_frame, text="Авто-нумерация", command=self.auto_number).grid(row=0, column=3, padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Загрузить файлы", command=self.load_files).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Предпросмотр", command=self.preview_rename).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Переименовать", command=self.rename_files).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Очистить", command=self.clear_files).grid(row=0, column=3, padx=5)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="Предпросмотр переименования", padding="5")
        preview_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.preview_text = tk.Text(preview_frame, height=8, wrap=tk.NONE)
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(5, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        name_entry_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
    def paste_from_clipboard(self):
        """Вставляет текст из буфера обмена в поле названия"""
        try:
            # Получаем текст из буфера обмена
            clipboard_text = self.root.clipboard_get()
            if clipboard_text:
                # Очищаем поле и вставляем текст
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, clipboard_text.strip())
        except tk.TclError:
            # Если в буфере нет текста
            messagebox.showinfo("Информация", "Буфер обмена пуст или содержит не текстовые данные")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось вставить из буфера: {str(e)}")
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)
            self.load_files()
    
    def load_files(self):
        directory = self.dir_var.get()
        if not directory or not os.path.exists(directory):
            messagebox.showerror("Ошибка", "Выберите корректную папку")
            return
        
        self.files = []
        self.file_numbers = {}
        self.tree.delete(*self.tree.get_children())
        
        # Get all files in directory
        file_list = []
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                file_list.append((file, file_path))
        
        # Sort files naturally
        file_list.sort(key=lambda x: self.natural_sort_key(x[0]))
        
        for i, (file, file_path) in enumerate(file_list, 1):
            self.files.append(file_path)
            self.file_numbers[file_path] = i
            self.tree.insert("", "end", values=(i, file))
    
    def natural_sort_key(self, s):
        import re
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', s)]
    
    def on_double_click(self, event):
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            column = self.tree.identify_column(event.x)
            if column == "#1":  # Number column
                self.edit_number(item)
    
    def edit_number(self, item):
        # Create edit window
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Изменить номер")
        edit_win.geometry("200x100")
        edit_win.transient(self.root)
        edit_win.grab_set()
        
        current_values = self.tree.item(item, "values")
        current_number = current_values[0]
        
        ttk.Label(edit_win, text="Новый номер:").pack(pady=5)
        number_var = tk.StringVar(value=current_number)
        entry = ttk.Entry(edit_win, textvariable=number_var, width=10)
        entry.pack(pady=5)
        entry.select_range(0, tk.END)
        entry.focus()
        
        def save_number():
            try:
                new_number = int(number_var.get())
                file_path = self.files[self.tree.index(item)]
                self.file_numbers[file_path] = new_number
                self.update_tree_display()
                edit_win.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число")
        
        ttk.Button(edit_win, text="Сохранить", command=save_number).pack(pady=5)
        entry.bind("<Return>", lambda e: save_number())
    
    def move_up(self, event=None):
        selected = self.tree.selection()
        if selected:
            indices = [self.tree.index(item) for item in selected]
            indices.sort()
            
            # Move each selected item up if possible
            for index in indices:
                if index > 0 and index - 1 not in indices:
                    self.files[index], self.files[index-1] = self.files[index-1], self.files[index]
            
            self.update_tree_display()
            # Reselect moved items
            for i, item in enumerate(selected):
                new_index = indices[i] - 1 if indices[i] > 0 else 0
                self.tree.selection_add(self.tree.get_children()[new_index])
    
    def move_down(self, event=None):
        selected = self.tree.selection()
        if selected:
            indices = [self.tree.index(item) for item in selected]
            indices.sort(reverse=True)
            
            # Move each selected item down if possible
            for index in indices:
                if index < len(self.files) - 1 and index + 1 not in indices:
                    self.files[index], self.files[index+1] = self.files[index+1], self.files[index]
            
            self.update_tree_display()
            # Reselect moved items
            for i, item in enumerate(selected):
                new_index = indices[i] + 1 if indices[i] < len(self.files) - 1 else indices[i]
                self.tree.selection_add(self.tree.get_children()[new_index])
    
    def move_to_top(self, event=None):
        selected = self.tree.selection()
        if selected:
            indices = [self.tree.index(item) for item in selected]
            indices.sort()
            
            # Move selected items to top
            moved_files = []
            for index in indices:
                moved_files.append(self.files[index])
            
            # Remove selected files and insert at beginning
            for index in sorted(indices, reverse=True):
                del self.files[index]
            
            self.files = moved_files + self.files
            
            self.update_tree_display()
            # Reselect moved items
            for i in range(len(selected)):
                self.tree.selection_add(self.tree.get_children()[i])
    
    def move_to_bottom(self, event=None):
        selected = self.tree.selection()
        if selected:
            indices = [self.tree.index(item) for item in selected]
            indices.sort(reverse=True)
            
            # Move selected items to bottom
            moved_files = []
            for index in indices:
                moved_files.append(self.files[index])
            
            # Remove selected files and append to end
            for index in sorted(indices, reverse=True):
                del self.files[index]
            
            self.files = self.files + moved_files
            
            self.update_tree_display()
            # Reselect moved items
            for i in range(len(self.files) - len(selected), len(self.files)):
                self.tree.selection_add(self.tree.get_children()[i])
    
    def assign_numbers(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите файлы для назначения номеров")
            return
        
        try:
            start_number = int(self.start_number_var.get())
            indices = [self.tree.index(item) for item in selected]
            
            for i, index in enumerate(indices):
                file_path = self.files[index]
                self.file_numbers[file_path] = start_number + i
            
            self.update_tree_display()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное начальное число")
    
    def auto_number(self):
        # Reset all numbers to sequential order
        for i, file_path in enumerate(self.files, 1):
            self.file_numbers[file_path] = i
        self.update_tree_display()
    
    def remove_file(self):
        selected = self.tree.selection()
        if selected:
            indices = [self.tree.index(item) for item in selected]
            indices.sort(reverse=True)  # Remove from end to avoid index issues
            
            for index in indices:
                file_path = self.files[index]
                del self.files[index]
                if file_path in self.file_numbers:
                    del self.file_numbers[file_path]
            
            self.update_tree_display()
    
    def update_tree_display(self):
        self.tree.delete(*self.tree.get_children())
        for file_path in self.files:
            filename = os.path.basename(file_path)
            number = self.file_numbers.get(file_path, 0)
            self.tree.insert("", "end", values=(number, filename))
    
    def preview_rename(self):
        if not self.files:
            messagebox.showwarning("Предупреждение", "Нет файлов для переименования")
            return
        
        self.preview_text.delete(1.0, tk.END)
        
        name_pattern = self.name_pattern_var.get().strip()
        new_extension = self.ext_var.get().strip()
        
        if not name_pattern:
            name_pattern = "file"
        
        # Sort files by their assigned numbers
        sorted_files = sorted(self.files, key=lambda x: self.file_numbers.get(x, 0))
        
        for file_path in sorted_files:
            old_name = os.path.basename(file_path)
            number = self.file_numbers.get(file_path, 0)
            # Создаем новое имя с назначенным номером
            new_name = f"{name_pattern}_{number:02d}.{new_extension}"
            self.preview_text.insert(tk.END, f"{old_name} → {new_name}\n")
    
    def rename_files(self):
        if not self.files:
            messagebox.showwarning("Предупреждение", "Нет файлов для переименования")
            return
        
        name_pattern = self.name_pattern_var.get().strip()
        new_extension = self.ext_var.get().strip()
        
        if not name_pattern:
            name_pattern = "file"
        
        try:
            # Sort files by their assigned numbers for renaming
            sorted_files = sorted(self.files, key=lambda x: self.file_numbers.get(x, 0))
            
            for file_path in sorted_files:
                if not os.path.exists(file_path):
                    continue
                
                old_name = os.path.basename(file_path)
                directory = os.path.dirname(file_path)
                number = self.file_numbers.get(file_path, 0)
                
                # Создаем новое имя
                new_name = f"{name_pattern}_{number:02d}.{new_extension}"
                new_path = os.path.join(directory, new_name)
                
                # Переименовываем файл
                os.rename(file_path, new_path)
            
            messagebox.showinfo("Успех", "Файлы успешно переименованы!")
            self.load_files()  # Reload to show new names
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при переименовании: {str(e)}")
    
    def clear_files(self):
        self.files = []
        self.file_numbers = {}
        self.tree.delete(*self.tree.get_children())
        self.preview_text.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamerApp(root)
    root.mainloop()