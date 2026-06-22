import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="ProblemDB"
)
cursor = conn.cursor()

def addRecord():
    pname = input("Please enter the name of the problem: ")
    topic = input("Please enter the topic on which the problem is based: ")
    diffi = input("Enter the difficulty of the problem(Easy, Medium, Hard): ")
    fpath = input("Enter the path of the file in which the code is stored: ")
    cursor.execute("""INSERT INTO problems(problem_name, topic, difficulty, file_path)VALUES (%s, %s, %s, %s)""",(pname,topic,diffi,fpath,))
    conn.commit()

def editRecord():
    record = input("Please enter the name of the problem which you want to update: ")
    field = input("Enter the name of the field which you want to update(problem name, topic, difficulty, file path): ")
    edit = input("Enter the updated value for the field: ")
    if field.lower()=="problem name":
        cursor.execute("UPDATE PROBLEMS SET problem_name = %s WHERE problem_name = %s",(edit,record,))
        conn.commit()
    elif field.lower()=="topic":
        cursor.execute("UPDATE PROBLEMS SET topic = %s WHERE problem_name = %s",(edit,record,))
        conn.commit()
    elif field.lower()=="difficulty":
        cursor.execute("UPDATE PROBLEMS SET difficulty = %s WHERE problem_name = %s",(edit,record,))
        conn.commit()
    elif field.lower()=="file path":
        cursor.execute("UPDATE PROBLEMS SET file_path = %s WHERE problem_name = %s",(edit,record,))
        conn.commit()
    else:
        print("Invalid field input!")
    

def printRecord():
    ch = int(input("Enter 1 to print all records, 2 to print a particular record or 3 to print records with a field in common: "))
    if ch == 1:
        cursor.execute("SELECT * FROM PROBLEMS")
        records = cursor.fetchall()
        for record in records:
            print(record)
    elif ch == 2:
        problem = int(input("Enter the serial number of the record you want to print: "))
        cursor.execute("SELECT * FROM PROBLEMS WHERE ID = %s",(problem,))
        record = cursor.fetchone()
        print(record)
    elif ch == 3:
        fieldc = input("Enter the field in common(topic or difficulty): ")
        value = input("Enter the value of the field: ")
        if fieldc.lower()=="topic":
            cursor.execute("SELECT * FROM PROBLEMS WHERE topic = %s",(value,))
            records = cursor.fetchall()
            for record in records:
                print(record)
        elif fieldc.lower()=="difficulty":
            cursor.execute("SELECT * FROM PROBLEMS WHERE difficulty = %s",(value,))
            records = cursor.fetchall()
            for record in records:
                print(record)
        else:
            print("Invalid field input!")
    else:
        print("Invalid Choice!")

def printCode():
    problem = input("Enter the name of the problem of which the code is to be printed: ")
    cursor.execute("SELECT file_path FROM PROBLEMS WHERE problem_name = %s",(problem,))
    result = cursor.fetchone()
    if result:
        path = result[0]
        try:
            with open(path, "r") as file:
                print(file.read())
        except FileNotFoundError:
            print("File not found")
    else:
        print("Problem not found in database")

def delRecord():
    problem = input("Enter the topic of the problem to be deleted: ")
    cursor.execute("DELETE FROM PROBLEMS WHERE TOPIC = %s",(problem))
    conn.commit()

def dbStats():
    cursor.execute("SELECT COUNT(*) FROM PROBLEMS")
    print("Total Problems:", cursor.fetchone()[0])
    cursor.execute("SELECT COUNT(*) FROM PROBLEMS WHERE DIFFICULTY='EASY'")
    print("Easy:", cursor.fetchone()[0])
    cursor.execute("SELECT COUNT(*) FROM PROBLEMS WHERE DIFFICULTY='MEDIUM'")
    print("Medium:", cursor.fetchone()[0])
    cursor.execute("SELECT COUNT(*) FROM PROBLEMS WHERE DIFFICULTY='HARD'")
    print("Hard:", cursor.fetchone()[0])

print("1. Add a record to your problem's table.")
print("2. Edit an existing record in your problem's table.")
print("3. Print an existing record in your problem's table.")
print("4. View the code to an existing problem in your problem's table.")
print("5. Delete a record from your problem's table.")
print("6. Statistics of your problems database.")
choice = int(input("Enter your choice(1,2,3,4,5 or 6) according to the operation you want to perform: "))

if choice==1:
    addRecord()
elif choice==2:
    editRecord()
elif choice==3:
    printRecord()
elif choice==4:
    printCode()
elif choice==5:
    delRecord()
elif choice==6:
    dbStats()
else:
    print("Invalid choice!")

cursor.close()
conn.close()