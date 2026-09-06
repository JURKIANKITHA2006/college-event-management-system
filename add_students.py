import sqlite3

DATABASE = "events.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

start_number = 231211101001

for i in range(1000):
    registration_no = str(start_number + i)
    name = f"Student {i + 1}"
    email = f"{registration_no}@college.edu"
    department = "CSE AI"

    cursor.execute(
        """
        INSERT OR IGNORE INTO students
        (registration_no, name, email, department)
        VALUES (?, ?, ?, ?)
        """,
        (registration_no, name, email, department)
    )

conn.commit()

total = cursor.execute(
    "SELECT COUNT(*) FROM students"
).fetchone()[0]

conn.close()

print(f"Total students in database: {total}")