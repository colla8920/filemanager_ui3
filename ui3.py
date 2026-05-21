import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


import customtkinter as cctk


cctk.set_appearance_mode("System")
cctk.set_default_color_theme("blue")


class ModernFileManager(cctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Файловый менеджер")
        self.geometry("1000x650")
        self.minsize(800, 500)

        self.current_dir = os.path.abspath(os.getcwd())
        self.clipboard_path = None
        self.clipboard_action = None

        self.setup_ui()
        self.setup_hotkeys()
        self.load_directory(self.current_dir)

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)


        self.nav_frame = cctk.CTkFrame(self, corner_radius=0, height=60)
        self.nav_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=0, pady=0)
        self.nav_frame.grid_propagate(False)

        self.btn_up = cctk.CTkButton(self.nav_frame, text="▲ Вверх", width=90, command=self.go_up)
        self.btn_up.pack(side=tk.LEFT, padx=15, pady=15)

        self.path_entry = cctk.CTkEntry(self.nav_frame, font=("Segoe UI", 13))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=15)
        self.path_entry.bind('<Return>', lambda e: self.load_directory(self.path_entry.get()))

        self.btn_go = cctk.CTkButton(self.nav_frame, text="Перейти", width=90,
                                     command=lambda: self.load_directory(self.path_entry.get()))
        self.btn_go.pack(side=tk.LEFT, padx=15, pady=15)


        self.sidebar_frame = cctk.CTkFrame(self, corner_radius=0, width=180)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        label_shortcuts = cctk.CTkLabel(self.sidebar_frame, text="БЫСТРЫЙ ДОСТУП", font=("Segoe UI", 11, "bold"),
                                        text_color="gray")
        label_shortcuts.pack(anchor="w", padx=15, pady=(20, 10))

        user_home = os.path.expanduser("~")
        shortcuts = [
            ("Домашняя", user_home),
            ("Рабочий стол", os.path.join(user_home, "Desktop")),
            ("Документы", os.path.join(user_home, "Documents")),
            ("Загрузки", os.path.join(user_home, "Downloads"))
        ]

        for name, path in shortcuts:
            if os.path.exists(path):
                btn = cctk.CTkButton(self.sidebar_frame, text=name, fg_color="transparent",
                                     text_color=("black", "white"), anchor="w", hover_color=("gray85", "gray25"),
                                     command=lambda p=path: self.load_directory(p))
                btn.pack(fill=tk.X, padx=10, pady=2)


        style = ttk.Style()
        style.theme_use("clam")

        is_dark = cctk.get_appearance_mode() == "Dark"
        bg_color = "#2a2a2a" if is_dark else "#ffffff"
        fg_color = "#ffffff" if is_dark else "#000000"
        field_bg = "#2a2a2a" if is_dark else "#ffffff"
        head_bg = "#212121" if is_dark else "#e5e5e5"

        style.configure("Treeview", background=bg_color, foreground=fg_color,
                        fieldbackground=field_bg, rowheight=28, font=("Segoe UI", 11), borderwidth=0)
        style.configure("Treeview.Heading", background=head_bg, foreground=fg_color,
                        font=("Segoe UI", 11, "bold"), borderwidth=0)
        style.map("Treeview", background=[("selected", "#1f6aa5")])

        self.table_frame = tk.Frame(self, bg=bg_color)
        self.table_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        columns = ("name", "type", "size", "modified")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text=" Имя", anchor=tk.W)
        self.tree.heading("type", text=" Тип", anchor=tk.W)
        self.tree.heading("size", text=" Размер", anchor=tk.W)
        self.tree.heading("modified", text=" Дата изменения", anchor=tk.W)

        self.tree.column("name", width=350, anchor=tk.W)
        self.tree.column("type", width=100, anchor=tk.W)
        self.tree.column("size", width=100, anchor=tk.W)
        self.tree.column("modified", width=150, anchor=tk.W)

        scrollbar = cctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<Double-1>", self.on_double_click)

        self.bottom_frame = cctk.CTkFrame(self, corner_radius=0, height=80)
        self.bottom_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.bottom_frame.grid_propagate(False)

        cctk.CTkButton(self.bottom_frame, text="Новая папка", width=110, command=self.create_folder).pack(side=tk.LEFT,
                                                                                                          padx=10,
                                                                                                          pady=15)
        cctk.CTkButton(self.bottom_frame, text="Копировать", width=100, fg_color="#2b719e",
                       command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5, pady=15)
        cctk.CTkButton(self.bottom_frame, text="Вырезать", width=100, fg_color="#2b719e",
                       command=self.cut_to_clipboard).pack(side=tk.LEFT, padx=5, pady=15)
        cctk.CTkButton(self.bottom_frame, text="Вставить", width=100, fg_color="#2fa572", hover_color="#107c41",
                       command=self.paste_from_clipboard).pack(side=tk.LEFT, padx=5, pady=15)
        cctk.CTkButton(self.bottom_frame, text="Удалить", width=100, fg_color="#bd3939", hover_color="#8c2323",
                       command=self.delete_item).pack(side=tk.LEFT, padx=5, pady=15)

        cctk.CTkButton(self.bottom_frame, text="Обновить", width=90, fg_color="gray40", hover_color="gray30",
                       command=self.refresh).pack(side=tk.RIGHT, padx=15, pady=15)

        self.status_label = cctk.CTkLabel(self.bottom_frame, text="Буфер обмена пуст", font=("Segoe UI", 12),
                                          text_color="gray")
        self.status_label.pack(side=tk.RIGHT, padx=20)

    def setup_hotkeys(self):
        self.bind('<Control-c>', lambda e: self.copy_to_clipboard())
        self.bind('<Control-x>', lambda e: self.cut_to_clipboard())
        self.bind('<Control-v>', lambda e: self.paste_from_clipboard())
        self.bind('<Delete>', lambda e: self.delete_item())

    def load_directory(self, path):
        try:
            if not os.path.isdir(path):
                raise NotADirectoryError
            self.current_dir = os.path.abspath(path)
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, self.current_dir)

            for item in self.tree.get_children():
                self.tree.delete(item)

            items = os.listdir(self.current_dir)
            dirs, files = [], []

            for item in items:
                full_path = os.path.join(self.current_dir, item)
                if os.path.isdir(full_path):
                    dirs.append(item)
                else:
                    files.append(item)

            dirs.sort()
            files.sort()

            for d in dirs:
                full_path = os.path.join(self.current_dir, d)
                mtime = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d %H:%M')
                self.tree.insert("", tk.END, text=full_path, values=(" 📁 " + d, "Папка", "", mtime))

            for f in files:
                full_path = os.path.join(self.current_dir, f)
                size = self.format_size(os.path.getsize(full_path))
                mtime = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d %H:%M')
                self.tree.insert("", tk.END, text=full_path, values=(" 📄 " + f, "Файл", size, mtime))

        except PermissionError:
            messagebox.showerror("Ошибка доступа", "У вас нет прав для просмотра этой папки.")
            self.go_up()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку: {e}")

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0

    def go_up(self):
        parent = os.path.dirname(self.current_dir)
        if parent != self.current_dir:
            self.load_directory(parent)

    def on_double_click(self, event):
        selected_item = self.tree.focus()
        if not selected_item: return
        item_path = self.tree.item(selected_item, "text")
        if os.path.isdir(item_path):
            self.load_directory(item_path)
        else:
            os.startfile(item_path) if os.name == 'nt' else os.system(f'xdg-open "{item_path}"')

    def get_selected_path(self):
        selected_item = self.tree.focus()
        if not selected_item: return None
        return self.tree.item(selected_item, "text")

    def refresh(self):
        self.load_directory(self.current_dir)

    def create_folder(self):
        folder_name = simpledialog.askstring("Новая папка", "Введите имя новой папки:")
        if folder_name:
            new_path = os.path.join(self.current_dir, folder_name)
            try:
                os.makedirs(new_path)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать папку:\n{e}")

    def delete_item(self):
        path = self.get_selected_path()
        if not path: return
        if messagebox.askyesno("Подтверждение", f"Вы действительно хотите удалить:\n{os.path.basename(path)}?"):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить элемент:\n{e}")

    def copy_to_clipboard(self):
        path = self.get_selected_path()
        if path:
            self.clipboard_path = path
            self.clipboard_action = 'copy'
            self.status_label.configure(text=f"В буфере (Копия): {os.path.basename(path)}", text_color="#2b719e")

    def cut_to_clipboard(self):
        path = self.get_selected_path()
        if path:
            self.clipboard_path = path
            self.clipboard_action = 'cut'
            self.status_label.configure(text=f"В буфере (Вырезано): {os.path.basename(path)}", text_color="#bd3939")

    def paste_from_clipboard(self):
        if not self.clipboard_path or not os.path.exists(self.clipboard_path):
            messagebox.showwarning("Буфер обмена", "Буфер обмена пуст.")
            return

        item_name = os.path.basename(self.clipboard_path)
        dest_path = os.path.join(self.current_dir, item_name)

        if os.path.isdir(self.clipboard_path) and self.current_dir.startswith(self.clipboard_path):
            messagebox.showerror("Ошибка", "Нельзя поместить папку внутрь самой себя!")
            return

        if os.path.exists(dest_path):
            if self.clipboard_path == dest_path:
                if self.clipboard_action == 'cut':
                    return
                elif self.clipboard_action == 'copy':
                    base, ext = os.path.splitext(item_name)
                    dest_path = os.path.join(self.current_dir, f"{base}_копия{ext}")
            else:
                if not messagebox.askyesno("Конфликт", f"Элемент '{item_name}' уже существует. Заменить?"):
                    return
                if os.path.isdir(dest_path):
                    shutil.rmtree(dest_path)
                else:
                    os.remove(dest_path)

        try:
            if self.clipboard_action == 'copy':
                if os.path.isdir(self.clipboard_path):
                    shutil.copytree(self.clipboard_path, dest_path)
                else:
                    shutil.copy2(self.clipboard_path, dest_path)
            elif self.clipboard_action == 'cut':
                shutil.move(self.clipboard_path, dest_path)
                self.clipboard_path = None
                self.clipboard_action = None
                self.status_label.configure(text="Буфер обмена пуст", text_color="gray")

            self.refresh()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Сбой при операции:\n{e}")


if __name__ == "__main__":
    app = ModernFileManager()
    app.mainloop()