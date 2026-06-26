import mysql.connector
import os

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
    problem = input("Enter the problem name of the problem to be deleted: ")
    cursor.execute("DELETE FROM PROBLEMS WHERE problem_name = %s",(problem))
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

def updateStatus():
    record = input("Enter the problem name of the problem to be updated: ")
    newsts = input("Enter new status for the problem: ")
    cursor.execute("UPDATE PROBLEMS SET STATUS=%s WHERE problem_name=%s",(newsts,record))
    conn.commit()

def randomProblem():
    cursor.execute("SELECT * FROM PROBLEMS ORDER BY RAND() LIMIT 1")
    print("Problem name: ",cursor.fetchone()[1])
    print("Topic: ",cursor.fetchone()[2])
    print("Difficulty: ",cursor.fetchone()[3])
    print("File path: ",cursor.fetchone()[4])

def tableStats():
    print("=== DATABASE STATISTICS ===")
    cursor.execute("SELECT COUNT(*) AS Total_Problems FROM PROBLEMS")
    print("Total problems:",cursor.fetchone()[0])
    print("")
    print("By Difficulty: ")
    cursor.execute("SELECT difficulty, COUNT(*) AS Count FROM PROBLEMS GROUP BY difficulty")
    for difficulty, count in cursor.fetchall():
        print(difficulty,":",count)
    print("")
    print("By Status: ")
    cursor.execute("SELECT status, COUNT(*) AS Count FROM PROBLEMS GROUP BY status")
    for status, count in cursor.fetchall():
        print(status,":",count)

def openProblem():
    topic = input("Please enter the name of problem whose file is to be opened: ")
    cursor.execute("SELECT file_path FROM problems where problem_name=%s",(topic))
    path = cursor.fetchone()[0]
    os.startfile(path)
    
def addRevision():
    pname = input("Add name of the problem which you revised: ")
    cursor.execute("UPDATE PROBLEMS SET TIMES_REVISED = TIMES_REVISED + 1,LAST_REVISED = CURDATE() WHERE PROBLEM_NAME = %s",(pname))
    conn.commit()
    print("Revision of",pname,"has been updated in your problems table.")


print("1. Add a record to your problems table.")
print("2. Edit an existing record in your problems table.")
print("3. Print an existing record in your problems table.")
print("4. View the code to an existing problem in your problems table.")
print("5. Delete a record from your problems table.")
print("6. Statistics of your problems database.")
print("7. Update status of a record in your problemss table.")
print("8. Select a random problems from your problems table.")
print("9. Statistics of your problems table.")
print("10. Open file of a problem from your problems table.")
print("11. Add revision to a problem in your problems table.")
choice = int(input("Enter your choice(1,2,3,4,5,6,7,8,9 or 10) according to the operation you want to perform: "))

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
elif choice==7:
    updateStatus()
elif choice==8:
    randomProblem()
elif choice==9:
    tableStats()  
elif choice==10:
    openProblem() 
elif choice==11:
    addRevision() 
else:
    print("Invalid choice!")

cursor.close()
conn.close()