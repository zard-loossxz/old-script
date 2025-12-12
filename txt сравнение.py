import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import difflib

class TextComparator:
    def __init__(self, root):
        self.root = root
        self.root.title("Сравнение текстовых файлов")
        self.root.geometry("1200x700")
        
        # Переменные для хранения путей к файлам
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        
        # Настройка стиля
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
    def setup_styles(self):
        """Настройка стилей для виджетов"""
        style = ttk.Style()
        style.theme_use('clam')
        
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Фрейм для кнопок выбора файлов
        file_frame = ttk.Frame(self.root, padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Кнопка выбора первого файла
        ttk.Button(file_frame, text="Выбрать файл 1", 
                  command=self.select_file1).grid(row=0, column=0, padx=5, pady=5)
        self.file1_label = ttk.Label(file_frame, text="Файл не выбран", 
                                    relief="sunken", padding=5, width=50)
        self.file1_label.grid(row=0, column=1, padx=5, pady=5)
        
        # Кнопка выбора второго файла
        ttk.Button(file_frame, text="Выбрать файл 2", 
                  command=self.select_file2).grid(row=1, column=0, padx=5, pady=5)
        self.file2_label = ttk.Label(file_frame, text="Файл не выбран", 
                                    relief="sunken", padding=5, width=50)
        self.file2_label.grid(row=1, column=1, padx=5, pady=5)
        
        # Кнопка сравнения
        ttk.Button(file_frame, text="Сравнить файлы", 
                  command=self.compare_files, style="Accent.TButton").grid(row=0, column=2, rowspan=2, padx=20)
        
        # Фрейм для текстовых областей
        text_frame = ttk.Frame(self.root, padding="10")
        text_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        # Настройка весов строк и столбцов
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_columnconfigure(1, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        # Текстовая область для первого файла
        ttk.Label(text_frame, text="Файл 1:").grid(row=0, column=0, sticky=tk.W)
        self.text1 = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                               width=50, height=25,
                                               font=("Courier", 10))
        self.text1.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        # Текстовая область для второго файла
        ttk.Label(text_frame, text="Файл 2:").grid(row=0, column=1, sticky=tk.W)
        self.text2 = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                               width=50, height=25,
                                               font=("Courier", 10))
        self.text2.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        # Область для отображения различий
        diff_frame = ttk.Frame(self.root, padding="10")
        diff_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        ttk.Label(diff_frame, text="Различия:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        diff_frame.grid_rowconfigure(1, weight=1)
        diff_frame.grid_columnconfigure(0, weight=1)
        
        self.diff_text = scrolledtext.ScrolledText(diff_frame, wrap=tk.WORD,
                                                   height=10,
                                                   font=("Courier", 10))
        self.diff_text.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        # Добавляем теги для подсветки
        self.text1.tag_config("added", background="#ccffcc")
        self.text1.tag_config("removed", background="#ffcccc")
        self.text2.tag_config("added", background="#ccffcc")
        self.text2.tag_config("removed", background="#ffcccc")
        self.diff_text.tag_config("diff_added", foreground="green")
        self.diff_text.tag_config("diff_removed", foreground="red")
        self.diff_text.tag_config("diff_info", foreground="blue")
        
        # Статус бар
        self.status_bar = ttk.Label(self.root, text="Готов к работе", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    def select_file1(self):
        """Выбор первого файла"""
        filename = filedialog.askopenfilename(
            title="Выберите первый файл",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filename:
            self.file1_path.set(filename)
            self.file1_label.config(text=filename)
            self.load_file_to_text(filename, self.text1)
    
    def select_file2(self):
        """Выбор второго файла"""
        filename = filedialog.askopenfilename(
            title="Выберите второй файл",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filename:
            self.file2_path.set(filename)
            self.file2_label.config(text=filename)
            self.load_file_to_text(filename, self.text2)
    
    def load_file_to_text(self, filename, text_widget):
        """Загрузка содержимого файла в текстовое поле"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, content)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def compare_files(self):
        """Сравнение двух файлов"""
        if not self.file1_path.get() or not self.file2_path.get():
            messagebox.showwarning("Внимание", "Выберите оба файла для сравнения")
            return
        
        try:
            # Чтение файлов
            with open(self.file1_path.get(), 'r', encoding='utf-8') as f1:
                lines1 = f1.readlines()
            with open(self.file2_path.get(), 'r', encoding='utf-8') as f2:
                lines2 = f2.readlines()
            
            # Очистка текстовых полей
            self.text1.delete(1.0, tk.END)
            self.text2.delete(1.0, tk.END)
            self.diff_text.delete(1.0, tk.END)
            
            # Отображение содержимого файлов
            self.text1.insert(1.0, ''.join(lines1))
            self.text2.insert(1.0, ''.join(lines2))
            
            # Сравнение с помощью difflib
            differ = difflib.Differ()
            diff = list(differ.compare(lines1, lines2))
            
            # Отображение различий
            line_num = 1
            for line in diff:
                if line.startswith('+ '):
                    self.diff_text.insert(tk.END, f"{line_num:4}: ", "diff_info")
                    self.diff_text.insert(tk.END, line[2:], "diff_added")
                    line_num += 1
                elif line.startswith('- '):
                    self.diff_text.insert(tk.END, f"{line_num:4}: ", "diff_info")
                    self.diff_text.insert(tk.END, line[2:], "diff_removed")
                    line_num += 1
                elif line.startswith('  '):
                    line_num += 1
                elif line.startswith('? '):
                    continue
            
            # Подсветка различий в исходных файлах
            self.highlight_differences(lines1, lines2)
            
            # Обновление статуса
            diff_count = sum(1 for line in diff if line.startswith('+ ') or line.startswith('- '))
            self.status_bar.config(text=f"Сравнение завершено. Найдено различий: {diff_count}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сравнении файлов:\n{str(e)}")
            self.status_bar.config(text="Ошибка при сравнении файлов")
    
    def highlight_differences(self, lines1, lines2):
        """Подсветка различий в текстовых полях"""
        # Создаем последовательности для сравнения
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        
        # Очищаем предыдущую подсветку
        for tag in ["added", "removed"]:
            self.text1.tag_remove(tag, 1.0, tk.END)
            self.text2.tag_remove(tag, 1.0, tk.END)
        
        # Подсветка для первого файла (удаленные строки)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                start_pos = self.get_position(self.text1, i1, 0)
                end_pos = self.get_position(self.text1, i2, 0)
                self.text1.tag_add("removed", start_pos, end_pos)
        
        # Подсветка для второго файла (добавленные строки)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                start_pos = self.get_position(self.text2, j1, 0)
                end_pos = self.get_position(self.text2, j2, 0)
                self.text2.tag_add("added", start_pos, end_pos)
    
    def get_position(self, text_widget, line, column):
        """Получение позиции в текстовом виджете"""
        return f"{line + 1}.{column}"

def main():
    root = tk.Tk()
    app = TextComparator(root)
    root.mainloop()

if __name__ == "__main__":
    main()