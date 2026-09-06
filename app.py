from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime


app = Flask(__name__)
app.secret_key = "college_event_secret"

DATABASE = "events.db"

UPLOAD_FOLDER = "static/uploads"

ALLOWED_EXTENSIONS = {
    "png", "jpg", "jpeg", "gif",
    "mp4", "webm", "mov"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS 
# =========================
# STUDENT DASHBOARD
# =========================
@app.route("/")
@app.route("/dashboard")
def dashboard():

    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()

    events = conn.execute(
        "SELECT * FROM events ORDER BY date"
    ).fetchall()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (session["student_id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "dashboard.html",
        events=events,
        student=student
    )

# =========================
# STUDENT EVENTS
# =========================
@app.route("/events")
def events():

    conn = get_db()

    events = conn.execute(
        """
        SELECT
            events.*,
            COUNT(registrations.id) AS registered_count
        FROM events
        LEFT JOIN registrations
        ON events.id = registrations.event_id
        GROUP BY events.id
        ORDER BY events.date
        """
    ).fetchall()

    conn.close()

    return render_template(
        "events.html",
        events=events
    )

  # =========================
# EVENT MEMORIES
# =========================
@app.route("/event-memories")
def event_memories():

    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()

    memories = conn.execute(
        """
        SELECT
            event_memories.title,
            event_memories.description,
            event_memories.file_name,
            event_memories.file_type,
            events.name AS event_name
        FROM event_memories
        INNER JOIN events
        ON event_memories.event_id = events.id
        ORDER BY event_memories.id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "event_memories.html",
        memories=memories
    )

# =========================
# STUDENT LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        registration_no = request.form.get("registration_no")

        conn = get_db()

        student = conn.execute(
            """
            SELECT *
            FROM students
            WHERE registration_no = ?
            """,
            (registration_no,)
        ).fetchone()

        conn.close()

        if student:
            session["student_id"] = student["id"]
            session["student_registration_no"] = student["registration_no"]
            session["student_email"] = student["email"]

            return redirect("/dashboard")

        return "Invalid Registration Number"

    return render_template("login.html")


# =========================
# STUDENT LOGOUT
# =========================

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =========================
# STUDENT PROFILE
# =========================
@app.route("/profile")
def profile():

    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (session["student_id"],)
    ).fetchone()

    registered_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM registrations
        WHERE student_id = ?
        """,
        (session["student_id"],)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "profile.html",
        student=student,
        registered_count=registered_count
    )


@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()

    if request.method == "POST":

        name = request.form.get("name")
        department = request.form.get("department")

        conn.execute(
            """
            UPDATE students
            SET name = ?, department = ?
            WHERE id = ?
            """,
            (name, department, session["student_id"])
        )

        conn.commit()
        conn.close()

        return redirect("/profile")

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (session["student_id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "edit_profile.html",
        student=student
    )
# =========================
# EVENT REGISTRATION
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        student_id = session.get("student_id")

        if not student_id:
            return redirect("/login")

        event_name = request.form.get("event_name")

        conn = get_db()

        event = conn.execute(
            "SELECT * FROM events WHERE name = ?",
            (event_name,)
        ).fetchone()

        if not event:
            conn.close()
            return "Event not found"

        if event["registration_open"] == 0:
            conn.close()
            return "Registration is closed for this event."

        if event["registration_deadline"]:

            try:
                deadline = datetime.strptime(
                    event["registration_deadline"],
                    "%Y-%m-%d"
                )

                today = datetime.now()

                if today.date() > deadline.date():

                    conn.execute(
                        """
                        UPDATE events
                        SET registration_open = 0
                        WHERE id = ?
                        """,
                        (event["id"],)
                    )

                    conn.commit()
                    conn.close()

                    return "Registration deadline has passed."

            except ValueError:
                pass

        existing = conn.execute(
            """
            SELECT *
            FROM registrations
            WHERE student_id = ?
            AND event_id = ?
            """,
            (student_id, event["id"])
        ).fetchone()

        if existing:
            conn.close()
            return "You have already registered for this event."

        conn.execute(
            """
            INSERT INTO registrations
            (student_id, event_id)
            VALUES (?, ?)
            """,
            (student_id, event["id"])
        )
        # Award 10 participation points
        conn.execute(
           """
            INSERT INTO participation_points
            (student_id, event_id, points)
             VALUES (?, ?, ?)
            """,
             (student_id, event["id"], 10)
)

        conn.commit()
        conn.close()

        # Registration successful
        return redirect("/success")

    event_name = request.args.get("event_name")

    if event_name:

        conn = get_db()

        event = conn.execute(
            "SELECT * FROM events WHERE name = ?",
            (event_name,)
        ).fetchone()

        conn.close()

        return render_template(
            "register.html",
            event=event
        )

    return render_template("register.html")


# =========================
# REGISTRATION SUCCESS
# =========================

@app.route("/success")
def success():

    if "student_id" not in session:
        return redirect("/login")

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Registration Successful</title>

        <style>
            body {
                margin: 0;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background: linear-gradient(135deg, #667eea, #764ba2);
                font-family: Arial, sans-serif;
            }

            .box {
                background: white;
                padding: 45px;
                border-radius: 18px;
                text-align: center;
                width: 90%;
                max-width: 500px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.25);
            }

            .success {
                font-size: 60px;
            }

            h1 {
                color: #333;
                margin-bottom: 15px;
            }

            p {
                color: #666;
                font-size: 17px;
                margin-bottom: 30px;
            }

            a {
                display: inline-block;
                padding: 13px 25px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
            }

            a:hover {
                background: #5568d9;
            }
        </style>
    </head>

    <body>

        <div class="box">

            <div class="success">✅</div>

            <h1>Registered Successfully!</h1>

            <p>
                You have successfully registered for the event.
            </p>

            <a href="/my-events">
                View My Events
            </a>

        </div>

    </body>
    </html>
    """


# =========================
# MY EVENTS
# =========================

@app.route("/my-events")
def my_events():

    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()

    events = conn.execute(
        """
        SELECT events.*
        FROM events
        INNER JOIN registrations
        ON events.id = registrations.event_id
        WHERE registrations.student_id = ?
        ORDER BY events.date
        """,
        (session["student_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "my_events.html",
        events=events
    )


# =========================
# CERTIFICATE
# =========================

@app.route("/certificate/<int:event_id>")
def certificate(event_id):

    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()

    student = conn.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    event = conn.execute(
        """
        SELECT events.*
        FROM events
        INNER JOIN registrations
        ON events.id = registrations.event_id
        WHERE events.id = ?
        AND registrations.student_id = ?
        """,
        (event_id, session["student_id"])
    ).fetchone()

    conn.close()

    if not event:
        return "You are not registered for this event."

    return render_template(
        "certificate.html",
        student=student,
        event=event
    )
    # =========================
# EVENT RATING & FEEDBACK
# =========================

@app.route("/rate-event/<int:event_id>", methods=["GET", "POST"])
def rate_event(event_id):

    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()

    # Check whether the student registered for this event
    registration = conn.execute(
        """
        SELECT *
        FROM registrations
        WHERE student_id = ?
        AND event_id = ?
        """,
        (session["student_id"], event_id)
    ).fetchone()

    if not registration:
        conn.close()
        return "You are not registered for this event."

    # Get event details
    event = conn.execute(
        "SELECT * FROM events WHERE id = ?",
        (event_id,)
    ).fetchone()

    # Get existing rating, if any
    rating = conn.execute(
        """
        SELECT *
        FROM event_ratings
        WHERE student_id = ?
        AND event_id = ?
        """,
        (session["student_id"], event_id)
    ).fetchone()

    # Save rating
    if request.method == "POST":

        rating_value = request.form.get("rating")
        feedback = request.form.get("feedback")

        try:
            rating_value = int(rating_value)
        except (TypeError, ValueError):
            conn.close()
            return "Please select a valid rating."

        if rating_value < 1 or rating_value > 5:
            conn.close()
            return "Rating must be between 1 and 5."

        if rating:
            conn.execute(
                """
                UPDATE event_ratings
                SET rating = ?, feedback = ?
                WHERE student_id = ?
                AND event_id = ?
                """,
                (
                    rating_value,
                    feedback,
                    session["student_id"],
                    event_id
                )
            )
        else:
            conn.execute(
                """
                INSERT INTO event_ratings
                (student_id, event_id, rating, feedback)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session["student_id"],
                    event_id,
                    rating_value,
                    feedback
                )
            )

        conn.commit()
        conn.close()

        return redirect("/my-events")

    conn.close()

    return render_template(
        "rate_event.html",
        event=event,
        rating=rating
    )

# =========================
# ADMIN LOGIN
# =========================

@app.route("/admin")
@app.route("/admin-login", methods=["GET", "POST"])
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = (
            request.form.get("username")
            or request.form.get("email")
        )

        password = request.form.get("password")

        if username == "admin" and password == "admin123":

            session["admin"] = True

            return redirect("/admin_dashboard")

        return "Invalid username or password"

    return render_template("admin_login.html")


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin_dashboard")
@app.route("/admin/dashboard")
def admin_dashboard():

    if not session.get("admin"):
        return redirect("/admin-login")

    conn = get_db()

    total_events = conn.execute(
        "SELECT COUNT(*) FROM events"
    ).fetchone()[0]

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_registrations = conn.execute(
        "SELECT COUNT(*) FROM registrations"
    ).fetchone()[0]

    events = conn.execute(
        """
        SELECT
            events.*,
            (
                SELECT COUNT(*)
                FROM registrations
                WHERE registrations.event_id = events.id
            ) AS registration_count
        FROM events
        ORDER BY date
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_events=total_events,
        total_students=total_students,
        total_registrations=total_registrations,
        events=events
    )


# =========================
# ADD EVENT
# =========================
@app.route("/add_event", methods=["GET", "POST"])
@app.route("/admin/add-event", methods=["GET", "POST"])
def add_event():

    if not session.get("admin"):
        return redirect("/admin-login")

    if request.method == "POST":

        name = (
            request.form.get("name")
            or request.form.get("event_name")
        )

        date = request.form.get("date")
        time = request.form.get("time")
        venue = request.form.get("venue")
        description = request.form.get("description")
        capacity = request.form.get("capacity")

        deadline = (
            request.form.get("registration_deadline")
            or request.form.get("deadline")
        )

        conn = get_db()

        conn.execute(
            """
            INSERT INTO events
            (
                name,
                date,
                time,
                venue,
                description,
                capacity,
                registration_deadline,
                registration_open
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                date,
                time,
                venue,
                description,
                capacity,
                deadline,
                1
            )
        )

        conn.commit()
        conn.close()

        return redirect("/admin_dashboard")

    return render_template("add_event.html")

# =========================
# ADMIN EVENTS
# =========================

@app.route("/admin_events")
@app.route("/admin/events")
def admin_events():

    if not session.get("admin"):
        return redirect("/admin-login")

    conn = get_db()

    events = conn.execute(
        """
        SELECT
            events.*,
            (
                SELECT COUNT(*)
                FROM registrations
                WHERE registrations.event_id = events.id
            ) AS registration_count
        FROM events
        ORDER BY date
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin_events.html",
        events=events
    )


# =========================
# ALL REGISTRATIONS
# =========================

@app.route("/registrations")
@app.route("/admin_registrations")
@app.route("/admin/registrations")
def registrations():

    if not session.get("admin"):
        return redirect("/admin-login")

    conn = get_db()

    registrations = conn.execute(
        """
        SELECT
            registrations.id,
            students.registration_no,
            students.name,
            students.email,
            students.department,
            events.name AS event_name,
            events.date,
            events.registration_deadline
        FROM registrations

        INNER JOIN students
        ON registrations.student_id = students.id

        INNER JOIN events
        ON registrations.event_id = events.id

        ORDER BY events.date
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin_registrations.html",
        registrations=registrations
    )


# =========================
# EVENT REGISTRATIONS
# =========================

@app.route("/admin/registrations/<int:event_id>")
def event_registrations(event_id):

    if not session.get("admin"):
        return redirect("/admin-login")

    conn = get_db()

    event = conn.execute(
        """
        SELECT *
        FROM events
        WHERE id = ?
        """,
        (event_id,)
    ).fetchone()

    if not event:
        conn.close()
        return "Event not found"

    students = conn.execute(
        """
        SELECT
            students.registration_no,
            students.name,
            students.email,
            students.department
        FROM registrations

        INNER JOIN students
        ON registrations.student_id = students.id

        WHERE registrations.event_id = ?

        ORDER BY students.registration_no
        """
        ,
        (event_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "admin_registrations.html",
        event=event,
        students=students,
        registrations=students
    )


# =========================
# EDIT EVENT
# =========================

@app.route("/admin/update-event/<int:event_id>", methods=["GET", "POST"])
def update_event(event_id):

    if not session.get("admin"):
        return redirect("/admin-login")

    conn = get_db()

    event = conn.execute(
        """
        SELECT *
        FROM events
        WHERE id = ?
        """,
        (event_id,)
    ).fetchone()

    if not event:
        conn.close()
        return "Event not found"

    if request.method == "POST":

        name = (
            request.form.get("name")
            or request.form.get("event_name")
        )

        date = request.form.get("date")
        time = request.form.get("time")
        venue = request.form.get("venue")
        description = request.form.get("description")
        capacity = request.form.get("capacity")

        deadline = (
            request.form.get("registration_deadline")
            or request.form.get("deadline")
        )

        registration_open = request.form.get(
            "registration_open"
        )

        if registration_open is None:
            registration_open = 1
        else:
            registration_open = int(registration_open)

        conn.execute(
            """
            UPDATE events
            SET
                name = ?,
                date = ?,
                time = ?,
                venue = ?,
                description = ?,
                capacity = ?,
                registration_deadline = ?,
                registration_open = ?
            WHERE id = ?
            """,
            (
                name,
                date,
                time,
                venue,
                description,
                capacity,
                deadline,
                registration_open,
                event_id
            )
        )

        conn.commit()
        conn.close()

        return redirect("/admin/events")

    conn.close()

    return render_template(
        "update_event.html",
        event=event
    )


# =========================
# DELETE EVENT
# =========================

@app.route("/admin/delete-event/<int:event_id>")
def delete_event(event_id):

    if not session.get("admin"):
        return redirect("/admin-login")

    conn = get_db()

    conn.execute(
        """
        DELETE FROM registrations
        WHERE event_id = ?
        """,
        (event_id,)
    )

    conn.execute(
        """
        DELETE FROM events
        WHERE id = ?
        """,
        (event_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin/events")
    # =========================
# ADD EVENT MEMORY
# =========================
@app.route("/admin/add-memory", methods=["POST"])
def add_memory():

    if "admin" not in session:
        return redirect("/admin/login")

    event_id = request.form.get("event_id")
    title = request.form.get("title")
    description = request.form.get("description")

    file = request.files.get("memory_file")

    if not file or file.filename == "":
        return redirect("/admin/memories")

    if not allowed_file(file.filename):
        return redirect("/admin/memories")

    filename = secure_filename(file.filename)

    file_extension = filename.rsplit(".", 1)[1].lower()

    if file_extension in {"png", "jpg", "jpeg", "gif"}:
        file_type = "image"
    else:
        file_type = "video"

    file.save(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )
    )

    conn = get_db()

    conn.execute(
        """
        INSERT INTO event_memories
        (event_id, title, description, file_name, file_type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            event_id,
            title,
            description,
            filename,
            file_type
        )
    )

    conn.commit()
    conn.close()

    return redirect("/admin/memories")

    # =========================
# ADMIN EVENT MEMORIES
# =========================

@app.route("/admin/memories")
def admin_memories():

    if not session.get("admin"):
        return redirect("/admin-login")

    conn = get_db()

    events = conn.execute(
        "SELECT * FROM events ORDER BY date"
    ).fetchall()

    memories = conn.execute(
        """
        SELECT
            event_memories.*,
            events.name AS event_name
        FROM event_memories
        LEFT JOIN events
        ON event_memories.event_id = events.id
        ORDER BY event_memories.id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin_memories.html",
        events=events,
        memories=memories
    )
    # =========================
# DELETE EVENT MEMORY
# =========================

@app.route("/admin/delete-memory/<int:memory_id>")
def delete_memory(memory_id):

    if not session.get("admin"):
        return redirect("/admin-login")

    conn = get_db()

    memory = conn.execute(
        "SELECT file_name FROM event_memories WHERE id = ?",
        (memory_id,)
    ).fetchone()

    if memory:
        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            memory["file_name"]
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        conn.execute(
            "DELETE FROM event_memories WHERE id = ?",
            (memory_id,)
        )

        conn.commit()

    conn.close()

    return redirect("/admin/memories")
    # =========================
# PARTICIPATION POINTS
# =========================

@app.route("/participation-points")
def participation_points():

    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()

    points = conn.execute(
        """
        SELECT
            participation_points.points,
            events.name AS event_name
        FROM participation_points
        INNER JOIN events
        ON participation_points.event_id = events.id
        WHERE participation_points.student_id = ?
        ORDER BY participation_points.id DESC
        """,
        (session["student_id"],)
    ).fetchall()

    total_points = conn.execute(
        """
        SELECT COALESCE(SUM(points), 0)
        FROM participation_points
        WHERE student_id = ?
        """,
        (session["student_id"],)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "participation_points.html",
        points=points,
        total_points=total_points
    )
    # =========================
# STUDENT LEADERBOARD
# =========================

@app.route("/leaderboard")
def leaderboard():

    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()

    leaderboard_data = conn.execute(
        """
        SELECT
            students.name,
            students.registration_no,
            COALESCE(SUM(participation_points.points), 0) AS total_points
        FROM students
        LEFT JOIN participation_points
        ON students.id = participation_points.student_id
        GROUP BY students.id
        ORDER BY total_points DESC
        LIMIT 20
        """
    ).fetchall()

    conn.close()

    return render_template(
        "leaderboard.html",
        leaderboard=leaderboard_data
    )
    # =========================
# ADVANCED ANALYTICS
# =========================
@app.route("/analytics")
def analytics():

    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_events = conn.execute(
        "SELECT COUNT(*) FROM events"
    ).fetchone()[0]

    total_registrations = conn.execute(
        "SELECT COUNT(*) FROM registrations"
    ).fetchone()[0]

    total_points = conn.execute(
        "SELECT COALESCE(SUM(points), 0) FROM participation_points"
    ).fetchone()[0]

    event_data = conn.execute(
        """
        SELECT events.name, COUNT(registrations.id) AS registrations
        FROM events
        LEFT JOIN registrations
        ON events.id = registrations.event_id
        GROUP BY events.id
        ORDER BY registrations DESC
        LIMIT 10
        """
    ).fetchall()

    conn.close()

    return render_template(
        "analytics.html",
        total_students=total_students,
        total_events=total_events,
        total_registrations=total_registrations,
        total_points=total_points,
        event_data=event_data
    )
# =========================
# DIGITAL BADGES
# =========================
# =========================
# DIGITAL BADGES
# =========================

@app.route("/badges")
def badges():

    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()

    total_points = conn.execute(
        """
        SELECT COALESCE(SUM(points), 0)
        FROM participation_points
        WHERE student_id = ?
        """,
        (session["student_id"],)
    ).fetchone()[0]

    conn.close()

    badges = []

    if total_points >= 10:
        badges.append({
            "name": "Bronze Participant",
            "icon": "🥉",
            "description": "Earned by participating in events."
        })

    if total_points >= 30:
        badges.append({
            "name": "Silver Participant",
            "icon": "🥈",
            "description": "Excellent participation in college events."
        })

    if total_points >= 50:
        badges.append({
            "name": "Gold Participant",
            "icon": "🥇",
            "description": "Outstanding event participation."
        })

    if total_points >= 100:
        badges.append({
            "name": "Platinum Participant",
            "icon": "💎",
            "description": "Exceptional commitment to college events."
        })

    return render_template(
        "badges.html",
        badges=badges,
        total_points=total_points
    )
    # =========================
# ADMIN LOGOUT
# =========================

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect("/admin-login")


# ========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)