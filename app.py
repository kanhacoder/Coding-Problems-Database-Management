import os
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
        self.root.geometry("1180x720")
        self.root.minsize(1040, 640)

        self.selected_id = None
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

        self.ensure_table_columns()
        self.setup_style()
        self.build_ui()
        self.load_records()
        self.load_stats()

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def ensure_table_columns(self):
        self.cursor.execute("SHOW COLUMNS FROM PROBLEMS")
        existing_columns = {column[0].lower() for column in self.cursor.fetchall()}

        if "status" not in existing_columns:
            self.cursor.execute("ALTER TABLE PROBLEMS ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'UNSOLVED'")

        if "times_revised" not in existing_columns:
            self.cursor.execute("ALTER TABLE PROBLEMS ADD COLUMN times_revised INT NOT NULL DEFAULT 0")

        if "last_revised" not in existing_columns:
            self.cursor.execute("ALTER TABLE PROBLEMS ADD COLUMN last_revised DATE NULL")

        self.conn.commit()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f6f8fb")
        style.configure("Header.TLabel", background="#f6f8fb", foreground="#18202f", font=("Segoe UI", 20, "bold"))
        style.configure("Subtle.TLabel", background="#f6f8fb", foreground="#637083", font=("Segoe UI", 10))
        style.configure("TLabel", background="#f6f8fb", foreground="#263244", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=(10, 7))
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
            text="Track solved problems, status, revisions, and saved code files.",
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
        self.status = tk.StringVar(value="UNSOLVED")
        self.file_path = tk.StringVar()
        self.search_text = tk.StringVar()
        self.filter_field = tk.StringVar(value="All")
        self.stats_text = tk.StringVar(value="Stats will appear here.")

        self.add_labeled_entry(form, "Problem Name", self.problem_name)
        self.add_labeled_entry(form, "Topic", self.topic)

        ttk.Label(form, text="Difficulty").pack(anchor=tk.W, pady=(12, 4))
        ttk.Combobox(
            form,
            textvariable=self.difficulty,
            values=("Easy", "Medium", "Hard"),
            state="readonly",
            width=30,
        ).pack(fill=tk.X)

        ttk.Label(form, text="Status").pack(anchor=tk.W, pady=(12, 4))
        ttk.Combobox(
            form,
            textvariable=self.status,
            values=("UNSOLVED", "SOLVING", "SOLVED", "REVISE"),
            state="readonly",
            width=30,
        ).pack(fill=tk.X)

        ttk.Label(form, text="Code File Path").pack(anchor=tk.W, pady=(12, 4))
        path_row = ttk.Frame(form)
        path_row.pack(fill=tk.X)
        ttk.Entry(path_row, textvariable=self.file_path, width=28).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_row, text="Browse", command=self.choose_file).pack(side=tk.LEFT, padx=(8, 0))

        button_grid = ttk.Frame(form)
        button_grid.pack(fill=tk.X, pady=(18, 0))

        buttons = [
            ("Add", self.add_record, "Primary.TButton"),
            ("Update", self.update_record, None),
            ("Delete", self.delete_record, None),
            ("Clear", self.clear_form, None),
            ("View Code", self.view_code, None),
            ("Open File", self.open_problem_file, None),
            ("Add Revision", self.add_revision, None),
            ("Random Problem", self.random_problem, None),
        ]

        for index, (text, command, style_name) in enumerate(buttons):
            row = index // 2
            column = index % 2
            ttk.Button(button_grid, text=text, command=command, style=style_name or "TButton").grid(
                row=row,
                column=column,
                sticky="ew",
                padx=(0, 6) if column == 0 else (6, 0),
                pady=5,
            )

        button_grid.columnconfigure(0, weight=1)
        button_grid.columnconfigure(1, weight=1)

        ttk.Label(form, text="Database Statistics").pack(anchor=tk.W, pady=(18, 4))
        ttk.Label(form, textvariable=self.stats_text, justify=tk.LEFT, style="Subtle.TLabel").pack(anchor=tk.W, fill=tk.X)
        ttk.Button(form, text="Refresh Stats", command=self.load_stats).pack(fill=tk.X, pady=(10, 0))

        search_row = ttk.Frame(table_area)
        search_row.pack(fill=tk.X, pady=(0, 10))

        ttk.Entry(search_row, textvariable=self.search_text).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Combobox(
            search_row,
            textvariable=self.filter_field,
            values=("All", "Problem Name", "Topic", "Difficulty", "Status"),
            state="readonly",
            width=16,
        ).pack(side=tk.LEFT, padx=8)
        ttk.Button(search_row, text="Search", command=self.search_records).pack(side=tk.LEFT)
        ttk.Button(search_row, text="Refresh", command=self.load_records).pack(side=tk.LEFT, padx=(8, 0))

        columns = ("ID", "Problem Name", "Topic", "Difficulty", "Status", "Revisions", "Last Revised", "File Path")
        self.tree = ttk.Treeview(table_area, columns=columns, show="headings")

        widths = {
            "ID": 52,
            "Problem Name": 170,
            "Topic": 115,
            "Difficulty": 85,
            "Status": 90,
            "Revisions": 80,
            "Last Revised": 105,
            "File Path": 300,
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
            INSERT INTO PROBLEMS (problem_name, topic, difficulty, file_path, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            self.form_values(),
        )
        self.conn.commit()
        messagebox.showinfo("Saved", "Problem added successfully.")
        self.after_database_change()

    def update_record(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a record to update.")
            return
        if not self.validate_form():
            return

        self.cursor.execute(
            """
            UPDATE PROBLEMS
            SET problem_name = %s, topic = %s, difficulty = %s, file_path = %s, status = %s
            WHERE ID = %s
            """,
            (*self.form_values(), self.selected_id),
        )
        self.conn.commit()
        messagebox.showinfo("Updated", "Problem updated successfully.")
        self.after_database_change()

    def delete_record(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a record to delete.")
            return

        confirm = messagebox.askyesno("Delete Record", "Do you want to delete this problem?")
        if not confirm:
            return

        self.cursor.execute("DELETE FROM PROBLEMS WHERE ID = %s", (self.selected_id,))
        self.resequence_ids()
        self.conn.commit()
        messagebox.showinfo("Deleted", "Problem deleted successfully.")
        self.after_database_change()

    def resequence_ids(self):
        self.cursor.execute("SET @new_id = 0")
        self.cursor.execute("UPDATE PROBLEMS SET ID = -ID ORDER BY ID")
        self.cursor.execute("UPDATE PROBLEMS SET ID = (@new_id := @new_id + 1) ORDER BY ID DESC")
        self.cursor.execute("SELECT COALESCE(MAX(ID), 0) + 1 FROM PROBLEMS")
        next_id = self.cursor.fetchone()[0]
        self.cursor.execute(f"ALTER TABLE PROBLEMS AUTO_INCREMENT = {next_id}")

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

    def open_problem_file(self):
        path = self.file_path.get().strip()
        if not path:
            messagebox.showwarning("Missing File", "Select a record first.")
            return

        if not Path(path).exists():
            messagebox.showerror("File Not Found", "The saved file path does not exist.")
            return

        os.startfile(path)

    def add_revision(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a record to revise.")
            return

        self.cursor.execute(
            """
            UPDATE PROBLEMS
            SET times_revised = times_revised + 1, last_revised = CURDATE()
            WHERE ID = %s
            """,
            (self.selected_id,),
        )
        self.conn.commit()
        messagebox.showinfo("Revision Added", "Revision count updated.")
        self.load_records()
        self.load_stats()

    def random_problem(self):
        self.cursor.execute(
            """
            SELECT ID, problem_name, topic, difficulty, status, times_revised, last_revised, file_path
            FROM PROBLEMS
            ORDER BY RAND()
            LIMIT 1
            """
        )
        row = self.cursor.fetchone()
        if row is None:
            messagebox.showinfo("No Records", "No problems are saved yet.")
            return

        self.show_problem_details("Random Problem", row)

    def load_records(self):
        self.search_text.set("")
        self.cursor.execute(
            """
            SELECT ID, problem_name, topic, difficulty, status, times_revised, last_revised, file_path
            FROM PROBLEMS
            ORDER BY ID
            """
        )
        self.show_rows(self.cursor.fetchall())
        self.load_stats()

    def search_records(self):
        keyword = self.search_text.get().strip()
        field = self.filter_field.get()

        if not keyword:
            self.load_records()
            return

        like_value = f"%{keyword}%"
        base_query = """
            SELECT ID, problem_name, topic, difficulty, status, times_revised, last_revised, file_path
            FROM PROBLEMS
        """

        if field == "Problem Name":
            query = base_query + " WHERE problem_name LIKE %s"
            params = (like_value,)
        elif field == "Topic":
            query = base_query + " WHERE topic LIKE %s"
            params = (like_value,)
        elif field == "Difficulty":
            query = base_query + " WHERE difficulty LIKE %s"
            params = (like_value,)
        elif field == "Status":
            query = base_query + " WHERE status LIKE %s"
            params = (like_value,)
        else:
            query = base_query + """
                WHERE problem_name LIKE %s
                   OR topic LIKE %s
                   OR difficulty LIKE %s
                   OR status LIKE %s
            """
            params = (like_value, like_value, like_value, like_value)

        self.cursor.execute(query, params)
        self.show_rows(self.cursor.fetchall())

    def load_stats(self):
        self.cursor.execute("SELECT COUNT(*) FROM PROBLEMS")
        total = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT difficulty, COUNT(*) FROM PROBLEMS GROUP BY difficulty")
        difficulty_counts = self.cursor.fetchall()

        self.cursor.execute("SELECT status, COUNT(*) FROM PROBLEMS GROUP BY status")
        status_counts = self.cursor.fetchall()

        lines = [f"Total Problems: {total}", "", "By Difficulty:"]
        if difficulty_counts:
            lines.extend(f"{difficulty}: {count}" for difficulty, count in difficulty_counts)
        else:
            lines.append("No records")

        lines.append("")
        lines.append("By Status:")
        if status_counts:
            lines.extend(f"{status}: {count}" for status, count in status_counts)
        else:
            lines.append("No records")

        self.stats_text.set("\n".join(lines))

    def show_rows(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            display_row = list(row)
            if display_row[6] is None:
                display_row[6] = ""
            self.tree.insert("", tk.END, values=display_row)

    def fill_form_from_selection(self, _event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.selected_id = values[0]
        self.problem_name.set(values[1])
        self.topic.set(values[2])
        self.difficulty.set(values[3])
        self.status.set(values[4])
        self.file_path.set(values[7])

    def show_problem_details(self, title, row):
        details = (
            f"Problem Name: {row[1]}\n"
            f"Topic: {row[2]}\n"
            f"Difficulty: {row[3]}\n"
            f"Status: {row[4]}\n"
            f"Times Revised: {row[5]}\n"
            f"Last Revised: {row[6] or 'Not revised yet'}\n"
            f"File Path: {row[7]}"
        )
        messagebox.showinfo(title, details)

    def form_values(self):
        return (
            self.problem_name.get().strip(),
            self.topic.get().strip(),
            self.difficulty.get().strip(),
            self.file_path.get().strip(),
            self.status.get().strip(),
        )

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
        if not self.status.get().strip():
            messagebox.showwarning("Missing Value", "Status is required.")
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
        self.status.set("UNSOLVED")
        self.file_path.set("")
        self.tree.selection_remove(self.tree.selection())

    def after_database_change(self):
        self.clear_form()
        self.load_records()
        self.load_stats()

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

