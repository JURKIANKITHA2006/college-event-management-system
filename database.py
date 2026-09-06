import sqlite3

DATABASE = "events.db"


def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_no TEXT UNIQUE,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT
        )
    """)

    # Events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            venue TEXT NOT NULL,
            description TEXT,
capacity INTEGER DEFAULT 100,
registration_deadline TEXT,
registration_open INTEGER DEFAULT 1
    # Registrations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            event_id INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)

    # Event Ratings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            event_id INTEGER,
            rating INTEGER,
            feedback TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)

    # Event Memories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            file_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)

    # Participation Points table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participation_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            event_id INTEGER,
            points INTEGER DEFAULT 10,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)

    conn.commit()
    conn.close()

    print("Database created successfully!")


if __name__ == "__main__":
    create_database()