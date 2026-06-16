# Coding Problems Database

A menu-driven Python project that stores solved coding problems in a MySQL database and opens the saved code file whenever needed.

## About The Project

When solving DSA problems, it is easy to forget old solutions. This project works like a personal coding archive. It stores the problem name, topic, difficulty, and file path in MySQL. When the user wants to view a solution, Python fetches the file path from the database and reads the code from that file.

## Features

- Add a coding problem record
- Edit an existing record
- Print all records
- Print a specific record by ID
- Filter records by topic or difficulty
- View saved code using the file path stored in the database
- Uses MySQL for data storage
- Uses Python file handling to read solution files

## Tech Stack

- Python
- MySQL
- mysql-connector-python

## Folder Structure

```text
Coding Problems Database/
├── main.py
├── README.md
├── requirements.txt
├── database_schema.sql
└── .gitignore
```

## Database Setup

Create the database and table using the SQL file:

```sql
SOURCE database_schema.sql;
```

Or copy and run the SQL commands from `database_schema.sql` in MySQL Workbench or the MySQL command line.

## Install Requirements

```bash
pip install -r requirements.txt
```

## Run The Project

```bash
python main.py
```

## Table Fields

The `PROBLEMS` table stores:

- `ID`
- `problem_name`
- `topic`
- `difficulty`
- `file_path`

## Example Use Case

1. Solve a LeetCode problem.
2. Save the code in a `.txt` or `.py` file.
3. Add the problem details and file path in this project.
4. Later, search the problem and view the saved code directly from the menu.

## Future Improvements

- Add a loop so the menu keeps running until the user exits
- Add delete record option
- Add better error handling for wrong inputs
- Add search by problem name
- Add platform field, such as LeetCode or Codeforces
- Add problem link field
- Hide database password using environment variables
- Build a GUI version using Tkinter
