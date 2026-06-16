from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import mysql.connector


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "ProblemDB",
}


class CodingProblemsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Coding Problems Database")
        self.root.geometry("1000x650")
        self.root.minsize(900, 560)

        self.selected_id = None
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

        self.setup_style()
        self.build_ui()
        self.load_records()

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f6f8fb")
        style.configure("Header.TLabel", background="#f6f8fb", foreground="#18202f", font=("Segoe UI", 20, "bold"))
        style.configure("Subtle.TLabel", background="#f6f8fb", foreground="#637083", font=("Segoe UI", 10))
        style.configure("TLabel", background="#f6f8fb", foreground="#263244", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 7))
        style.configure("Primary.TButton", background="#1f6feb", foreground="white")
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def build_ui(self):
        main = ttk.Frame(self.root, padding=18)
        main.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(main)
        header.pack(fill=tk.X, pady=(0, 14))

        ttk.Label(header, text="Coding Problems Database", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(
            header,
            text="Save solved DSA problems, search them later, and open the stored code file.",
            style="Subtle.TLabel",
        ).pack(anchor=tk.W, pady=(4, 0))

        content = ttk.Frame(main)
        content.pack(fill=tk.BOTH, expand=True)

        form = ttk.Frame(content, padding=(0, 0, 16, 0))
        form.pack(side=tk.LEFT, fill=tk.Y)

        table_area = ttk.Frame(content)
        table_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.problem_name = tk.StringVar()
        self.topic = tk.StringVar()
        self.difficulty = tk.StringVar(value="Easy")
        self.file_path = tk.StringVar()
        self.search_text = tk.StringVar()
        self.filter_field = tk.StringVar(value="All")

        self.add_labeled_entry(form, "Problem Name", self.problem_name)
        self.add_labeled_entry(form, "Topic", self.topic)

        ttk.Label(form, text="Difficulty").pack(anchor=tk.W, pady=(12, 4))
        difficulty_box = ttk.Combobox(
            form,
            textvariable=self.difficulty,
            values=("Easy", "Medium", "Hard"),
            state="readonly",
            width=30,
        )
        difficulty_box.pack(fill=tk.X)

        ttk.Label(form, text="Code File Path").pack(anchor=tk.W, pady=(12, 4))
        path_row = ttk.Frame(form)
        path_row.pack(fill=tk.X)
        ttk.Entry(path_row, textvariable=self.file_path, width=28).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_row, text="Browse", command=self.choose_file).pack(side=tk.LEFT, padx=(8, 0))

        button_grid = ttk.Frame(form)
        button_grid.pack(fill=tk.X, pady=(18, 0))

        ttk.Button(button_grid, text="Add", style="Primary.TButton", command=self.add_record).grid(
            row=0, column=0, sticky="ew", padx=(0, 6), pady=5
        )
        ttk.Button(button_grid, text="Update", command=self.update_record).grid(
            row=0, column=1, sticky="ew", padx=(6, 0), pady=5
        )
        ttk.Button(button_grid, text="Delete", command=self.delete_record).grid(
            row=1, column=0, sticky="ew", padx=(0, 6), pady=5
        )
        ttk.Button(button_grid, text="Clear", command=self.clear_form).grid(
            row=1, column=1, sticky="ew", padx=(6, 0), pady=5
        )

        button_grid.columnconfigure(0, weight=1)
        button_grid.columnconfigure(1, weight=1)

        ttk.Button(form, text="View Code", command=self.view_code).pack(fill=tk.X, pady=(14, 0))

        search_row = ttk.Frame(table_area)
        search_row.pack(fill=tk.X, pady=(0, 10))

        ttk.Entry(search_row, textvariable=self.search_text).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Combobox(
            search_row,
            textvariable=self.filter_field,
            values=("All", "Problem Name", "Topic", "Difficulty"),
            state="readonly",
            width=16,
        ).pack(side=tk.LEFT, padx=8)
        ttk.Button(search_row, text="Search", command=self.search_records).pack(side=tk.LEFT)
        ttk.Button(search_row, text="Refresh", command=self.load_records).pack(side=tk.LEFT, padx=(8, 0))

        columns = ("ID", "Problem Name", "Topic", "Difficulty", "File Path")
        self.tree = ttk.Treeview(table_area, columns=columns, show="headings")

        widths = {
            "ID": 60,
            "Problem Name": 190,
            "Topic": 140,
            "Difficulty": 100,
            "File Path": 330,
        }

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=widths[column], anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.fill_form_from_selection)

        scrollbar = ttk.Scrollbar(table_area, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

    def add_labeled_entry(self, parent, label, variable):
        ttk.Label(parent, text=label).pack(anchor=tk.W, pady=(12, 4))
        ttk.Entry(parent, textvariable=variable, width=34).pack(fill=tk.X)

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="Choose Code File",
            filetypes=(("Code/Text Files", "*.py *.txt *.java *.cpp *.c *.js"), ("All Files", "*.*")),
        )
        if path:
            self.file_path.set(path)

    def add_record(self):
        if not self.validate_form():
            return

        self.cursor.execute(
            """
            INSERT INTO PROBLEMS (problem_name, topic, difficulty, file_path)
            VALUES (%s, %s, %s, %s)
            """,
            (
                self.problem_name.get().strip(),
                self.topic.get().strip(),
                self.difficulty.get().strip(),
                self.file_path.get().strip(),
            ),
        )
        self.conn.commit()
        messagebox.showinfo("Saved", "Problem added successfully.")
        self.clear_form()
        self.load_records()

    def update_record(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a record to update.")
            return
        if not self.validate_form():
            return

        self.cursor.execute(
            """
            UPDATE PROBLEMS
            SET problem_name = %s, topic = %s, difficulty = %s, file_path = %s
            WHERE ID = %s
            """,
            (
                self.problem_name.get().strip(),
                self.topic.get().strip(),
                self.difficulty.get().strip(),
                self.file_path.get().strip(),
                self.selected_id,
            ),
        )
        self.conn.commit()
        messagebox.showinfo("Updated", "Problem updated successfully.")
        self.clear_form()
        self.load_records()

    def delete_record(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a record to delete.")
            return

        confirm = messagebox.askyesno("Delete Record", "Do you want to delete this problem?")
        if not confirm:
            return

        self.cursor.execute("DELETE FROM PROBLEMS WHERE ID = %s", (self.selected_id,))
        self.conn.commit()
        messagebox.showinfo("Deleted", "Problem deleted successfully.")
        self.clear_form()
        self.load_records()

    def view_code(self):
        path = self.file_path.get().strip()
        if not path:
            messagebox.showwarning("Missing File", "Select a record or choose a code file first.")
            return

        code_path = Path(path)
        if not code_path.exists():
            messagebox.showerror("File Not Found", "The saved file path does not exist.")
            return

        code_window = tk.Toplevel(self.root)
        code_window.title(code_path.name)
        code_window.geometry("850x560")

        text = tk.Text(code_window, wrap=tk.NONE, font=("Consolas", 11), padx=12, pady=12)
        text.pack(fill=tk.BOTH, expand=True)

        horizontal = ttk.Scrollbar(code_window, orient=tk.HORIZONTAL, command=text.xview)
        horizontal.pack(fill=tk.X)

        text.configure(xscrollcommand=horizontal.set)
        text.insert("1.0", code_path.read_text(encoding="utf-8"))
        text.configure(state=tk.DISABLED)

    def load_records(self):
        self.search_text.set("")
        self.cursor.execute("SELECT ID, problem_name, topic, difficulty, file_path FROM PROBLEMS ORDER BY ID")
        self.show_rows(self.cursor.fetchall())

    def search_records(self):
        keyword = self.search_text.get().strip()
        field = self.filter_field.get()

        if not keyword:
            self.load_records()
            return

        like_value = f"%{keyword}%"
        if field == "Problem Name":
            query = "SELECT ID, problem_name, topic, difficulty, file_path FROM PROBLEMS WHERE problem_name LIKE %s"
            params = (like_value,)
        elif field == "Topic":
            query = "SELECT ID, problem_name, topic, difficulty, file_path FROM PROBLEMS WHERE topic LIKE %s"
            params = (like_value,)
        elif field == "Difficulty":
            query = "SELECT ID, problem_name, topic, difficulty, file_path FROM PROBLEMS WHERE difficulty LIKE %s"
            params = (like_value,)
        else:
            query = """
                SELECT ID, problem_name, topic, difficulty, file_path
                FROM PROBLEMS
                WHERE problem_name LIKE %s OR topic LIKE %s OR difficulty LIKE %s
            """
            params = (like_value, like_value, like_value)

        self.cursor.execute(query, params)
        self.show_rows(self.cursor.fetchall())

    def show_rows(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def fill_form_from_selection(self, _event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.selected_id = values[0]
        self.problem_name.set(values[1])
        self.topic.set(values[2])
        self.difficulty.set(values[3])
        self.file_path.set(values[4])

    def validate_form(self):
        if not self.problem_name.get().strip():
            messagebox.showwarning("Missing Value", "Problem name is required.")
            return False
        if not self.topic.get().strip():
            messagebox.showwarning("Missing Value", "Topic is required.")
            return False
        if not self.difficulty.get().strip():
            messagebox.showwarning("Missing Value", "Difficulty is required.")
            return False
        if not self.file_path.get().strip():
            messagebox.showwarning("Missing Value", "File path is required.")
            return False
        return True

    def clear_form(self):
        self.selected_id = None
        self.problem_name.set("")
        self.topic.set("")
        self.difficulty.set("Easy")
        self.file_path.set("")
        self.tree.selection_remove(self.tree.selection())

    def close_app(self):
        self.cursor.close()
        self.conn.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    try:
        CodingProblemsApp(root)
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", f"Could not connect to MySQL:\n\n{error}")
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()
