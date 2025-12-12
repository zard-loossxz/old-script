import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import subprocess
import sys
from pathlib import Path
import shutil

class MP4toMP3Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер MP4 в MP3")
        self.root.geometry("650x800")
        self.root.resizable(False, False)
        
        # Переменные
        self.input_files = []
        self.output_folder = ""
        self.is_converting = False
        self.current_file_index = 0
        self.total_files = 0
        self.ffmpeg_path = self.find_ffmpeg()
        
        self.setup_ui()
        
        # Проверка ffmpeg
        if not self.ffmpeg_path:
            self.ask_install_ffmpeg()
    
    def find_ffmpeg(self):
        """Поиск ffmpeg в системе"""
        # Проверяем в PATH
        if shutil.which("ffmpeg"):
            return "ffmpeg"
        
        # Проверяем в папке с программой
        program_dir = os.path.dirname(os.path.abspath(__file__))
        local_ffmpeg = os.path.join(program_dir, "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            return local_ffmpeg
        
        # Проверяем общие пути в Windows
        common_paths = [
            os.path.join(os.environ.get('PROGRAMFILES', ''), "ffmpeg", "bin", "ffmpeg.exe"),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), "ffmpeg", "bin", "ffmpeg.exe"),
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            os.path.expanduser("~\\ffmpeg\\bin\\ffmpeg.exe"),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def ask_install_ffmpeg(self):
        """Запрос на установку ffmpeg"""
        response = messagebox.askyesno(
            "FFmpeg не найден", 
            "Для работы конвертера требуется FFmpeg.\n\n"
            "Хотите скачать его автоматически?\n"
            "(Требуется интернет, ~50 МБ)\n\n"
            "Или установите вручную с сайта ffmpeg.org"
        )
        
        if response:
            self.download_ffmpeg()
        else:
            messagebox.showinfo(
                "Инструкция по установке",
                "1. Скачайте FFmpeg с официального сайта: ffmpeg.org\n"
                "2. Распакуйте архив\n"
                "3. Скопируйте файлы ffmpeg.exe, ffprobe.exe в папку с этой программой\n"
                "4. Перезапустите программу"
            )
    
    def download_ffmpeg(self):
        """Скачивание FFmpeg"""
        import urllib.request
        import zipfile
        
        download_window = tk.Toplevel(self.root)
        download_window.title("Скачивание FFmpeg")
        download_window.geometry("400x200")
        download_window.resizable(False, False)
        
        tk.Label(
            download_window,
            text="Скачивание FFmpeg...",
            font=("Arial", 12),
            pady=20
        ).pack()
        
        progress_label = tk.Label(download_window, text="Подготовка...")
        progress_label.pack()
        
        progress_bar = ttk.Progressbar(download_window, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill="x")
        progress_bar.start()
        
        status_label = tk.Label(download_window, text="")
        status_label.pack()
        
        download_window.update()
        
        try:
            # URL для скачивания FFmpeg для Windows
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            
            program_dir = os.path.dirname(os.path.abspath(__file__))
            zip_path = os.path.join(program_dir, "ffmpeg.zip")
            
            # Скачивание
            status_label.config(text="Скачивание...")
            download_window.update()
            
            urllib.request.urlretrieve(ffmpeg_url, zip_path)
            
            # Распаковка
            status_label.config(text="Распаковка...")
            download_window.update()
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Ищем ffmpeg.exe в архиве
                for file_info in zip_ref.infolist():
                    if file_info.filename.endswith('ffmpeg.exe'):
                        # Извлекаем в папку с программой
                        zip_ref.extract(file_info, program_dir)
                        # Переименовываем
                        extracted_path = os.path.join(program_dir, file_info.filename)
                        final_path = os.path.join(program_dir, "ffmpeg.exe")
                        if os.path.exists(extracted_path):
                            shutil.move(extracted_path, final_path)
            
            # Удаляем архив
            if os.path.exists(zip_path):
                os.remove(zip_path)
            
            progress_bar.stop()
            progress_bar.config(mode='determinate', value=100)
            status_label.config(text="Готово!")
            
            self.ffmpeg_path = final_path
            messagebox.showinfo("Успех", "FFmpeg успешно установлен!\nПерезапустите программу.")
            download_window.destroy()
            
        except Exception as e:
            progress_bar.stop()
            messagebox.showerror(
                "Ошибка скачивания",
                f"Не удалось скачать FFmpeg:\n{str(e)}\n\n"
                f"Скачайте вручную с ffmpeg.org"
            )
            download_window.destroy()
    
    def setup_ui(self):
        # Цвета
        BG_COLOR = "#f0f0f0"
        BTN_COLOR = "#4CAF50"
        BTN_HOVER = "#45a049"
        
        self.root.config(bg=BG_COLOR)
        
        # Заголовок
        title_frame = tk.Frame(self.root, bg=BG_COLOR)
        title_frame.pack(pady=20)
        
        tk.Label(
            title_frame,
            text="🎵 Конвертер MP4 в MP3",
            font=("Arial", 18, "bold"),
            bg=BG_COLOR,
            fg="#2c3e50"
        ).pack()
        
        # Фрейм для выбора файлов
        files_frame = tk.LabelFrame(
            self.root,
            text="Файлы для конвертации",
            font=("Arial", 11, "bold"),
            bg=BG_COLOR,
            padx=15,
            pady=10
        )
        files_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Кнопки выбора файлов
        buttons_frame = tk.Frame(files_frame, bg=BG_COLOR)
        buttons_frame.pack(pady=5, fill="x")
        
        # Стиль для кнопок
        button_style = {
            'font': ("Arial", 10),
            'relief': "flat",
            'padx': 20,
            'pady': 8,
            'cursor': "hand2"
        }
        
        self.select_files_btn = tk.Button(
            buttons_frame,
            text="📁 Выбрать файлы",
            command=self.select_files,
            bg="#2196F3",
            fg="white",
            **button_style
        )
        self.select_files_btn.pack(side="left", padx=(0, 10))
        
        self.select_folder_btn = tk.Button(
            buttons_frame,
            text="📂 Выбрать папку",
            command=self.select_folder,
            bg="#2196F3",
            fg="white",
            **button_style
        )
        self.select_folder_btn.pack(side="left")
        
        self.clear_files_btn = tk.Button(
            buttons_frame,
            text="🗑️ Очистить список",
            command=self.clear_files,
            bg="#f44336",
            fg="white",
            **button_style
        )
        self.clear_files_btn.pack(side="right")
        
        # Список файлов
        list_frame = tk.Frame(files_frame, bg=BG_COLOR)
        list_frame.pack(pady=10, fill="both", expand=True)
        
        # Заголовок списка
        header_frame = tk.Frame(list_frame, bg=BG_COLOR)
        header_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(
            header_frame,
            text="Выбранные файлы:",
            font=("Arial", 10, "bold"),
            bg=BG_COLOR
        ).pack(anchor="w")
        
        self.file_count_label = tk.Label(
            header_frame,
            text="Файлов: 0",
            font=("Arial", 9),
            fg="#7f8c8d",
            bg=BG_COLOR
        )
        self.file_count_label.pack(anchor="e", side="right")
        
        # Прокручиваемый список файлов
        list_container = tk.Frame(list_frame, bg=BG_COLOR)
        list_container.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_container, bg=BG_COLOR)
        scrollbar.pack(side="right", fill="y")
        
        self.files_listbox = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            selectmode=tk.EXTENDED,
            height=8,
            bg="white",
            relief="solid",
            bd=1
        )
        self.files_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=self.files_listbox.yview)
        
        # Настройки качества
        quality_frame = tk.LabelFrame(
            self.root,
            text="Настройки качества",
            font=("Arial", 11, "bold"),
            bg=BG_COLOR,
            padx=15,
            pady=10
        )
        quality_frame.pack(pady=10, padx=20, fill="x")
        
        # Битрейт
        tk.Label(
            quality_frame,
            text="Битрейт аудио:",
            font=("Arial", 10),
            bg=BG_COLOR
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.bitrate_var = tk.StringVar(value="192")
        bitrate_options = ["128", "192", "256", "320"]
        self.bitrate_menu = ttk.Combobox(
            quality_frame,
            textvariable=self.bitrate_var,
            values=bitrate_options,
            width=10,
            state="readonly"
        )
        self.bitrate_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(
            quality_frame,
            text="kbps",
            font=("Arial", 10),
            bg=BG_COLOR
        ).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        # Фрейм для выбора папки сохранения
        output_frame = tk.LabelFrame(
            self.root,
            text="Сохранение",
            font=("Arial", 11, "bold"),
            bg=BG_COLOR,
            padx=15,
            pady=10
        )
        output_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(
            output_frame,
            text="Папка для сохранения MP3:",
            font=("Arial", 10),
            bg=BG_COLOR
        ).pack(anchor="w")
        
        entry_frame = tk.Frame(output_frame, bg=BG_COLOR)
        entry_frame.pack(fill="x", pady=5)
        
        self.output_entry = tk.Entry(
            entry_frame,
            font=("Arial", 10),
            bg="white"
        )
        self.output_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 10))
        
        self.browse_output_btn = tk.Button(
            entry_frame,
            text="Обзор",
            command=self.browse_output_folder,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 10),
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.browse_output_btn.pack(side="right")
        
        # Прогресс бар
        progress_frame = tk.Frame(self.root, bg=BG_COLOR)
        progress_frame.pack(pady=15, padx=20, fill="x")
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Готов к конвертации",
            font=("Arial", 10),
            bg=BG_COLOR,
            fg="#7f8c8d"
        )
        self.progress_label.pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            length=610
        )
        self.progress_bar.pack(pady=5, fill="x")
        
        self.status_label = tk.Label(
            progress_frame,
            text="",
            font=("Arial", 9),
            bg=BG_COLOR,
            fg="#2c3e50"
        )
        self.status_label.pack(anchor="w")
        
        # Кнопка конвертации
        self.convert_btn = tk.Button(
            self.root,
            text="🚀 Начать конвертацию",
            command=self.start_conversion,
            bg=BTN_COLOR,
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            padx=30,
            pady=12,
            state="disabled",
            cursor="hand2"
        )
        self.convert_btn.pack(pady=20)
        
        # Привязка событий для hover эффекта
        self.convert_btn.bind("<Enter>", lambda e: self.convert_btn.config(bg=BTN_HOVER))
        self.convert_btn.bind("<Leave>", lambda e: self.convert_btn.config(bg=BTN_COLOR))
        
        # Установить папку сохранения по умолчанию
        default_output = os.path.join(os.path.expanduser("~"), "Music", "MP3_Converted")
        os.makedirs(default_output, exist_ok=True)
        self.output_entry.insert(0, default_output)
        self.output_folder = default_output
        
        # Статус FFmpeg
        self.ffmpeg_status_label = tk.Label(
            self.root,
            text=f"FFmpeg: {'Найден ✓' if self.ffmpeg_path else 'Не найден ✗'}",
            font=("Arial", 8),
            bg=BG_COLOR,
            fg="#7f8c8d"
        )
        self.ffmpeg_status_label.pack(side="bottom", pady=5)
    
    def select_files(self):
        """Выбор нескольких MP4 файлов"""
        files = filedialog.askopenfilenames(
            title="Выберите видео файлы",
            filetypes=[
                ("Видео файлы", "*.mp4 *.mkv *.avi *.mov *.flv *.wmv"),
                ("MP4 files", "*.mp4"),
                ("Все файлы", "*.*")
            ]
        )
        
        if files:
            for file in files:
                if file not in self.input_files:
                    self.input_files.append(file)
                    filename = os.path.basename(file)
                    self.files_listbox.insert(tk.END, f"🎬 {filename}")
            
            self.update_file_count()
            self.update_convert_button_state()
    
    def select_folder(self):
        """Выбор папки с видео файлами"""
        folder = filedialog.askdirectory(title="Выберите папку с видео файлами")
        
        if folder:
            video_extensions = ['*.mp4', '*.mkv', '*.avi', '*.mov', '*.flv', '*.wmv', '*.mpg', '*.mpeg']
            video_files = []
            
            for ext in video_extensions:
                video_files.extend(Path(folder).glob(ext))
                video_files.extend(Path(folder).glob(ext.upper()))
            
            if video_files:
                for file_path in video_files:
                    file_str = str(file_path)
                    if file_str not in self.input_files:
                        self.input_files.append(file_str)
                        self.files_listbox.insert(tk.END, f"🎬 {file_path.name}")
                
                self.update_file_count()
                self.update_convert_button_state()
            else:
                messagebox.showwarning("Файлы не найдены", "В выбранной папке не найдено видео файлов")
    
    def clear_files(self):
        """Очистить список файлов"""
        self.input_files = []
        self.files_listbox.delete(0, tk.END)
        self.update_file_count()
        self.update_convert_button_state()
    
    def update_file_count(self):
        """Обновить счетчик файлов"""
        count = len(self.input_files)
        self.file_count_label.config(text=f"Файлов: {count}")
        
        if count > 0:
            self.files_listbox.config(bg="#f8f9fa")
        else:
            self.files_listbox.config(bg="white")
    
    def update_convert_button_state(self):
        """Обновить состояние кнопки конвертации"""
        if self.input_files and self.output_folder and self.ffmpeg_path:
            self.convert_btn.config(state="normal", bg="#4CAF50")
        else:
            self.convert_btn.config(state="disabled", bg="#cccccc")
    
    def browse_output_folder(self):
        """Выбор папки для сохранения"""
        folder = filedialog.askdirectory(title="Выберите папку для сохранения MP3")
        if folder:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
            self.output_folder = folder
            self.update_convert_button_state()
    
    def start_conversion(self):
        """Начать конвертацию в отдельном потоке"""
        if not self.ffmpeg_path:
            messagebox.showerror("FFmpeg не найден", "Установите FFmpeg для работы программы")
            return
        
        if not self.input_files:
            messagebox.showwarning("Нет файлов", "Выберите файлы для конвертации")
            return
        
        if not self.output_folder:
            messagebox.showwarning("Нет папки", "Выберите папку для сохранения")
            return
        
        # Проверяем существование папки
        if not os.path.exists(self.output_folder):
            try:
                os.makedirs(self.output_folder, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать папку:\n{str(e)}")
                return
        
        # Блокировка интерфейса во время конвертации
        self.is_converting = True
        self.current_file_index = 0
        self.total_files = len(self.input_files)
        
        self.convert_btn.config(state="disabled", text="⏳ Конвертация...", bg="#FF9800")
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Подготовка к конвертации...", fg="#2c3e50")
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=self.convert_files, daemon=True)
        thread.start()
    
    def convert_files(self):
        """Конвертация всех выбранных файлов с помощью FFmpeg"""
        successful = 0
        failed = 0
        failed_files = []
        bitrate = self.bitrate_var.get() + "k"
        
        for i, input_file in enumerate(self.input_files, 1):
            if not self.is_converting:
                break
                
            self.current_file_index = i
            
            # Обновление прогресса в основном потоке
            self.root.after(0, self.update_progress, i, input_file)
            
            try:
                # Проверка существования файла
                if not os.path.exists(input_file):
                    raise FileNotFoundError(f"Файл не найден: {input_file}")
                
                # Создание имени выходного файла
                filename = os.path.basename(input_file)
                name_without_ext = os.path.splitext(filename)[0]
                
                # Удаляем недопустимые символы для имени файла
                import re
                name_without_ext = re.sub(r'[<>:"/\\|?*]', '_', name_without_ext)
                
                output_file = os.path.join(self.output_folder, f"{name_without_ext}.mp3")
                
                # Проверка, не существует ли уже файл
                if os.path.exists(output_file):
                    # Добавляем номер к имени файла
                    counter = 1
                    while os.path.exists(output_file):
                        output_file = os.path.join(self.output_folder, f"{name_without_ext}_{counter}.mp3")
                        counter += 1
                
                # Команда FFmpeg для конвертации
                # -i input_file - входной файл
                # -q:a 0 - максимальное качество
                # -b:a bitrate - битрейт
                # -vn - без видео
                # -y - перезаписать существующий файл
                
                cmd = [
                    self.ffmpeg_path,
                    '-i', input_file,
                    '-vn',  # Без видео
                    '-acodec', 'libmp3lame',
                    '-ab', bitrate,  # Битрейт
                    '-ar', '44100',  # Частота дискретизации
                    '-y',  # Перезаписать если файл существует
                    output_file
                ]
                
                # Запуск FFmpeg
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
                
                if result.returncode == 0 and os.path.exists(output_file):
                    successful += 1
                else:
                    raise Exception(f"FFmpeg ошибка: {result.stderr[:100]}")
                
            except Exception as e:
                failed += 1
                failed_files.append(os.path.basename(input_file))
                error_msg = f"Ошибка при конвертации {os.path.basename(input_file)}: {str(e)}"
                print(error_msg)  # Для отладки
        
        # Завершение конвертации
        self.root.after(0, self.conversion_complete, successful, failed, failed_files)
    
    def update_progress(self, current, filename):
        """Обновление прогресса"""
        progress_percent = (current / self.total_files) * 100
        self.progress_bar['value'] = progress_percent
        
        short_name = os.path.basename(filename)
        if len(short_name) > 40:
            short_name = short_name[:37] + "..."
        
        self.progress_label.config(text=f"Конвертация: {short_name}")
        self.status_label.config(text=f"Файл {current} из {self.total_files} ({progress_percent:.1f}%)")
        
        # Обновление интерфейса
        self.root.update_idletasks()
    
    def conversion_complete(self, successful, failed, failed_files):
        """Завершение конвертации"""
        self.is_converting = False
        
        self.convert_btn.config(state="normal", text="🚀 Начать конвертацию", bg="#4CAF50")
        self.progress_bar['value'] = 100
        
        # Подготовка сообщения о результате
        result_message = ""
        
        if successful > 0:
            result_message += f"✅ Успешно сконвертировано: {successful} файлов\n"
            result_message += f"📁 Папка сохранения: {self.output_folder}\n\n"
        
        if failed > 0:
            result_message += f"❌ Не удалось сконвертировать: {failed} файлов\n"
            if failed_files:
                result_message += "Файлы с ошибками:\n"
                for f in failed_files[:5]:  # Показываем только первые 5 файлов
                    result_message += f"  • {f}\n"
                if len(failed_files) > 5:
                    result_message += f"  ... и еще {len(failed_files) - 5} файлов\n"
        
        if successful == 0 and failed == 0:
            result_message = "Конвертация отменена или не выполнена."
            self.progress_label.config(text="Конвертация отменена", fg="#f44336")
            self.status_label.config(text="")
        elif successful > 0 and failed == 0:
            self.progress_label.config(text=f"✅ Конвертация завершена успешно!", fg="#4CAF50")
            self.status_label.config(text=f"Сконвертировано файлов: {successful}")
        elif successful > 0 and failed > 0:
            self.progress_label.config(text=f"⚠️ Конвертация завершена частично", fg="#FF9800")
            self.status_label.config(text=f"Успешно: {successful}, Неудачно: {failed}")
        else:
            self.progress_label.config(text="❌ Конвертация не удалась", fg="#f44336")
            self.status_label.config(text="Проверьте файлы и попробуйте снова")
        
        # Показать диалог с результатами
        if successful > 0 or failed > 0:
            messagebox.showinfo("Результат конвертации", result_message)
        
        # Открыть папку с результатами если есть успешные файлы
        if successful > 0 and messagebox.askyesno("Открыть папку", "Открыть папку с результатами?"):
            try:
                if sys.platform == "win32":
                    os.startfile(self.output_folder)
                elif sys.platform == "darwin":  # macOS
                    subprocess.run(["open", self.output_folder])
                else:  # Linux
                    subprocess.run(["xdg-open", self.output_folder])
            except:
                pass
    
    def on_closing(self):
        """Обработка закрытия окна"""
        if self.is_converting:
            if messagebox.askyesno("Конвертация идет", "Конвертация все еще выполняется. Прервать?"):
                self.is_converting = False
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = MP4toMP3Converter(root)
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Центрирование окна
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()