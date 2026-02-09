from flask import Flask, render_template, request, redirect, session, jsonify
import psycopg2
import psycopg2.extras
import random
import sys
import os
from dotenv import load_dotenv

# Get the parent directory (project root) first
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables from parent directory
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Add parent directory to path to import utils
sys.path.insert(0, BASE_DIR)
from utils.auth import login_required

app = Flask(__name__, 
    template_folder=os.path.join(BASE_DIR, 'template'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

# Configuration
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.getenv('FLASK_ENV', 'production') == 'development'

# Database URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/timetable_db')

# Handle Heroku/Render's postgres:// URL format (change to postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# ---------------- DB CONNECTION ----------------
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn

# Check and fix database schema
def check_and_fix_database_schema():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Check timetable table columns
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'timetable'
        """)
        columns = cur.fetchall()
        column_names = [col['column_name'] for col in columns]
        
        # Add semester column if missing
        if 'semester' not in column_names:
            print("Adding semester column to timetable table...")
            cur.execute("""
                ALTER TABLE timetable ADD COLUMN semester VARCHAR(10) DEFAULT 'ODD' NOT NULL
            """)
            print("✓ Added semester column")
        
        # Add updated_at column if missing
        if 'updated_at' not in column_names:
            print("Adding updated_at column to timetable table...")
            cur.execute("""
                ALTER TABLE timetable ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            print("✓ Added updated_at column")
        
        # Check subjects table
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'subjects'
        """)
        columns = cur.fetchall()
        column_names = [col['column_name'] for col in columns]
        
        if 'semester' not in column_names:
            print("Adding semester column to subjects table...")
            cur.execute("""
                ALTER TABLE subjects ADD COLUMN semester VARCHAR(10) DEFAULT 'ODD' NOT NULL
            """)
            print("✓ Added semester column to subjects")
        
        conn.commit()
        cur.close()
        conn.close()
        print("Database schema check completed")
        
    except Exception as e:
        print(f"Database schema check failed: {e}")

# Run schema check on import
check_and_fix_database_schema()

def get_cursor(conn):
    """Get a cursor that returns rows as dictionaries"""
    return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# -------- DEPRECATED - Keep for backwards compatibility --------
def dict_cursor(conn):
    """Legacy function - use get_cursor instead"""
    return get_cursor(conn)

# ---------------- HELPERS ----------------
def get_request_data():
    """Get data from either JSON or form submission"""
    if request.is_json:
        return request.get_json()
    # For form data, use request.form directly which handles MultiDict properly
    return dict(request.form)

def json_response(success, message, **kwargs):
    """Return a JSON response"""
    resp = {"success": success, "message": message}
    resp.update(kwargs)
    return jsonify(resp)

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = get_request_data()
        username = data.get("username")
        password = data.get("password")

        conn = get_db_connection()
        cur = get_cursor(conn)

        cur.execute(
            "SELECT role FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            role = user["role"]
            session["role"] = role

            if request.is_json:
                redirect_url = "/admin" if role == "admin" else "/faculty" if role == "faculty" else "/student"
                return json_response(True, "Login successful", redirect=redirect_url)
            
            if role == "admin":
                return redirect("/admin")
            elif role == "faculty":
                return redirect("/faculty")
            else:
                return redirect("/student")
        
        msg = "Invalid credentials"
        if request.is_json:
            return json_response(False, msg)
        return msg

    return render_template("login.html")

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
@login_required(role="admin")
def admin_dashboard():
    conn = get_db_connection()
    cur = get_cursor(conn)

    cur.execute("SELECT * FROM subjects")
    subjects = cur.fetchall()

    cur.execute("SELECT * FROM staff")
    faculty = cur.fetchall()

    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("admin_dashboard.html", subjects=subjects, faculty=faculty, courses=courses)

# -------- VIEW ALL TIMETABLES (ADMIN) --------
@app.route("/admin/view_timetables")
@login_required(role="admin")
def admin_view_timetables():
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)

        # Get all generated timetables grouped by year, course, and semester
        cur.execute("""
            SELECT DISTINCT
                t.year,
                t.course_id,
                t.semester,
                c.name as course_name,
                COUNT(t.id) as total_slots
            FROM timetable t
            JOIN courses c ON t.course_id = c.id
            GROUP BY t.year, t.course_id, t.semester, c.name
            ORDER BY t.year, c.name, t.semester
        """)

        timetables = cur.fetchall()
        cur.close()
        conn.close()

    except Exception as e:
        # If database query fails, return mock data for testing
        print(f"Database query failed: {e}")
        timetables = [
            {
                'year': 'III',
                'course_id': 1,
                'semester': 'ODD',
                'course_name': 'Computer Science',
                'total_slots': 45
            },
            {
                'year': 'II',
                'course_id': 2,
                'semester': 'EVEN',
                'course_name': 'Information Technology',
                'total_slots': 38
            },
            {
                'year': 'IV',
                'course_id': 1,
                'semester': 'ODD',
                'course_name': 'Computer Science',
                'total_slots': 42
            }
        ]

    return render_template("admin_view_timetables.html", timetables=timetables)

# ---------------- ADD SUBJECT ----------------
@app.route("/add_subject", methods=["POST"])
@login_required(role="admin")
def add_subject():
    data = get_request_data()
    
    code = data.get("code", "").strip()
    name = data.get("name", "").strip()
    year = data.get("year", "").strip()
    course_id = data.get("course_id", "").strip()
    semester = data.get("semester", "").strip()
    weekly_hours = data.get("weekly_hours", "4").strip()

    # Validate required fields
    if not all([code, name, year, course_id, semester, weekly_hours]):
        msg = "All fields are required"
        if request.is_json:
            return json_response(False, msg)
        return redirect(f"/admin?error={msg}")

    try:
        conn = get_db_connection()
        cur = get_cursor(conn)

        # Convert course_id to int
        course_id = int(course_id)
        weekly_hours = int(weekly_hours)

        cur.execute("""
            INSERT INTO subjects (code, name, year, course_id, semester, weekly_hours)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (code, name, year, course_id, semester, weekly_hours))

        conn.commit()
        cur.close()
        conn.close()

        if request.is_json:
            return json_response(True, "Subject added successfully", redirect="/admin")
        # Redirect with success message
        return redirect("/admin?success=subject_added")
    except Exception as e:
        import traceback
        traceback.print_exc()
        if request.is_json:
            return json_response(False, str(e))
        return redirect(f"/admin?error=Error adding subject")

# ---------------- ADD FACULTY ----------------
@app.route("/add_faculty", methods=["POST"])
@login_required(role="admin")
def add_faculty():
    data = get_request_data()
    
    staff_code = data.get("staff_code", "").strip()
    name = data.get("name", "").strip()
    department = data.get("department", "").strip()
    max_hours = data.get("max_hours", 20)
    subjects = data.get("subjects", []) if request.is_json else request.form.getlist("subjects")

    # Validate required fields
    if not all([staff_code, name, department, max_hours]):
        msg = "All fields are required"
        if request.is_json:
            return json_response(False, msg)
        return redirect(f"/admin?error={msg}")
    
    if not subjects:
        msg = "At least one subject must be selected"
        if request.is_json:
            return json_response(False, msg)
        return redirect(f"/admin?error={msg}")

    try:
        conn = get_db_connection()
        cur = get_cursor(conn)

        # Convert types
        max_hours = int(max_hours)
        subjects = [int(s) for s in subjects]

        # Insert staff
        cur.execute("""
            INSERT INTO staff (staff_code, name, department, max_hours)
            VALUES (%s, %s, %s, %s)
        """, (staff_code, name, department, max_hours))

        staff_db_id = cur.lastrowid
        conn.commit()

        # Assign subjects
        for subject_id in subjects:
            try:
                cur.execute("""
                    INSERT INTO staff_subjects (staff_id, subject_id)
                    VALUES (%s, %s)
                """, (staff_db_id, subject_id))
            except Exception as subj_err:
                continue

        conn.commit()
        cur.close()
        conn.close()

        if request.is_json:
            return json_response(True, "Faculty added successfully", redirect="/admin")
        return redirect("/admin?success=faculty_added")
    except Exception as e:
        if request.is_json:
            return json_response(False, str(e))
        return redirect(f"/admin?error=Error adding faculty")

# ---------------- EDIT SUBJECT ----------------
@app.route("/edit_subject/<int:id>", methods=["GET", "POST"])
@login_required(role="admin")
def edit_subject(id):
    conn = get_db_connection()
    cur = get_cursor(conn)

    if request.method == "POST":
        data = get_request_data()
        name = data.get("name")
        weekly_hours = data.get("weekly_hours")

        try:
            cur.execute("""
                UPDATE subjects
                SET name=%s, weekly_hours=%s
                WHERE id=%s
            """, (name, weekly_hours, id))

            conn.commit()
            cur.close()
            conn.close()

            if request.is_json:
                return json_response(True, "Subject updated", redirect="/admin")
            return redirect("/admin")
        except Exception as e:
            if request.is_json:
                return json_response(False, str(e))
            return str(e), 400

    cur.execute("SELECT * FROM subjects WHERE id=%s", (id,))
    subject = cur.fetchone()

    cur.close()
    conn.close()
    return render_template("edit_subject.html", subject=subject)

# ---------------- DELETE SUBJECT ----------------
@app.route("/delete_subject/<int:id>", methods=["GET", "POST"])
@login_required(role="admin")
def delete_subject(id):
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)

        cur.execute("DELETE FROM staff_subjects WHERE subject_id=%s", (id,))
        cur.execute("DELETE FROM subjects WHERE id=%s", (id,))

        conn.commit()
        cur.close()
        conn.close()

        if request.is_json:
            return json_response(True, "Subject deleted")
        return redirect("/admin")
    except Exception as e:
        if request.is_json:
            return json_response(False, str(e))
        return str(e), 400

# ---------------- EDIT FACULTY ----------------
@app.route("/edit_faculty/<int:id>", methods=["GET", "POST"])
@login_required(role="admin")
def edit_faculty(id):
    conn = get_db_connection()
    cur = get_cursor(conn)

    if request.method == "POST":
        name = request.form.get("name")
        max_hours = request.form.get("max_hours")
        subjects = request.form.getlist("subjects")

        try:
            cur.execute("""
                UPDATE staff SET name=%s, max_hours=%s WHERE id=%s
            """, (name, max_hours, id))

            # Remove old subject assignments
            cur.execute("DELETE FROM staff_subjects WHERE staff_id=%s", (id,))
            
            # Add new subject assignments
            for subject_id in subjects:
                cur.execute("""
                    INSERT INTO staff_subjects (staff_id, subject_id)
                    VALUES (%s, %s)
                """, (id, subject_id))

            conn.commit()
            cur.close()
            conn.close()

            if request.is_json:
                return json_response(True, "Faculty updated", redirect="/admin")
            return redirect("/admin")
        except Exception as e:
            if request.is_json:
                return json_response(False, str(e))
            return str(e), 400

    cur.execute("SELECT * FROM staff WHERE id=%s", (id,))
    faculty = cur.fetchone()

    cur.execute("SELECT id, code, name FROM subjects")
    subjects = cur.fetchall()

    cur.execute("SELECT subject_id FROM staff_subjects WHERE staff_id=%s", (id,))
    assigned = [s["subject_id"] for s in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template(
        "edit_faculty.html",
        faculty=faculty,
        subjects=subjects,
        assigned=assigned
    )

# ---------------- DELETE FACULTY ----------------
@app.route("/delete_faculty/<int:id>", methods=["GET", "POST"])
@login_required(role="admin")
def delete_faculty(id):
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)

        # Delete timetable entries first
        cur.execute("DELETE FROM timetable WHERE staff_id=%s", (id,))
        # Then delete staff_subjects
        cur.execute("DELETE FROM staff_subjects WHERE staff_id=%s", (id,))
        # Finally delete staff
        cur.execute("DELETE FROM staff WHERE id=%s", (id,))

        conn.commit()
        cur.close()
        conn.close()

        if request.is_json:
            return json_response(True, "Faculty deleted")
        return redirect("/admin")
    except Exception as e:
        if request.is_json:
            return json_response(False, str(e))
        return str(e), 400

# ---------------- FACULTY WORKLOAD ----------------
@app.route('/view_workload')
@login_required(role="admin")
def view_workload():
    conn = get_db_connection()
    cur = get_cursor(conn)
    cur.execute("SELECT * FROM faculty_workload")
    data = cur.fetchall()
    cur.close()
    conn.close()

    if request.is_json:
        return json_response(True, "Workload data", workload=data)
    return render_template('faculty_workload.html', workload=data)

# ----------------STUDENT DASHBOARD ----------------
@app.route("/student")
@login_required(role="student")
def student_dashboard():
    return render_template("student_dashboard.html")

# -------- FACULTY DASHBOARD ----------------
@app.route("/faculty", methods=["GET", "POST"])
@login_required(role="faculty")
def faculty_dashboard():
    conn = get_db_connection()
    cur = get_cursor(conn)

    cur.execute("SELECT id, name FROM staff")
    staff_list = cur.fetchall()

    schedule = None

    if request.method == "POST":
        staff_id = request.form["staff_id"]
        cur.execute("""
            SELECT t.day, p.period_no, s.code, s.name, t.year, t.course_id
            FROM timetable t
            JOIN subjects s ON t.subject_id = s.id
            JOIN periods p ON t.period_id = p.id
            WHERE t.staff_id = %s
            ORDER BY t.day, p.period_no
        """, (staff_id,))
        schedule = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "faculty_dashboard.html",
        staff_list=staff_list,
        schedule=schedule
    )

# -------- VIEW SUBJECTS --------
@app.route("/view_subjects")
@login_required(role="admin")
def view_subjects():
    conn = get_db_connection()
    cur = get_cursor(conn)
    
    cur.execute("""
        SELECT s.id, s.code, s.name, s.year, c.name as course_name, s.weekly_hours, s.semester
        FROM subjects s
        JOIN courses c ON s.course_id = c.id
        ORDER BY s.year, s.code
    """)
    subjects = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Organize subjects by year
    subjects_by_year = {
        "I": [],
        "II": [],
        "III": [],
        "IV": []
    }
    
    for subject in subjects:
        year = subject["year"]
        if year in subjects_by_year:
            subjects_by_year[year].append(subject)
    
    return render_template("view_subjects.html", subjects_by_year=subjects_by_year)

# -------- VIEW FACULTY --------
@app.route("/view_faculty")
@login_required(role="admin")
def view_faculty():
    conn = get_db_connection()
    cur = get_cursor(conn)
    
    cur.execute("""
        SELECT s.id, s.staff_code, s.name, s.department, s.max_hours
        FROM staff s
        ORDER BY s.staff_code
    """)
    faculty = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template("view_faculty.html", faculty=faculty)

# -------- AI TIMETABLE GENERATION --------
@app.route("/generate", methods=["POST"])
@login_required(role="admin")
def generate_timetable():
    data = get_request_data()
    year = data.get("year")
    course_id = data.get("course_id")
    semester = data.get("semester")

    conn = get_db_connection()
    cur = get_cursor(conn)

    try:
        # Delete existing timetable
        cur.execute(
            "DELETE FROM timetable WHERE year=%s AND course_id=%s AND semester=%s",
            (year, course_id, semester)
        )

        # Get subjects for that year & course & semester
        cur.execute("""
            SELECT s.id, s.weekly_hours
            FROM subjects s
            WHERE s.year=%s AND s.course_id=%s AND s.semester=%s
        """, (year, course_id, semester))
        subjects = cur.fetchall()

        # Get staff assignments
        cur.execute("""
            SELECT ss.staff_id, ss.subject_id
            FROM staff_subjects ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE s.year=%s AND s.course_id=%s AND s.semester=%s
        """, (year, course_id, semester))
        assignments = cur.fetchall()

        # Check if there are assignments
        if not assignments:
            cur.close()
            conn.close()
            msg = "Error: No staff assigned to subjects for this year and course. Please assign faculty to subjects first."
            if request.is_json:
                return json_response(False, msg)
            return msg, 400

        # Get period IDs mapped to period numbers
        cur.execute("SELECT id, period_no FROM periods ORDER BY period_no")
        period_data = cur.fetchall()
        period_map = {int(p["period_no"]): p["id"] for p in period_data}

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        period_nos = sorted(period_map.keys())

        staff_busy = {}
        room_busy = {}
        
        # Load existing staff assignments from all timetables to avoid duplicates
        cur.execute("""
            SELECT staff_id, day, period_id
            FROM timetable
        """)
        for row in cur.fetchall():
            staff_id = row["staff_id"]
            day = row["day"]
            period_id = row["period_id"]
            # Find period_no from period_id
            period_no = None
            for pno, pid in period_map.items():
                if pid == period_id:
                    period_no = pno
                    break
            if period_no:
                staff_busy[(staff_id, day, period_no)] = True
        
        # Get available classrooms
        cur.execute("SELECT id FROM classrooms")
        rooms = [r["id"] for r in cur.fetchall()]
        if not rooms:
            rooms = [1]
        
        # Load existing room assignments from all timetables to avoid conflicts
        cur.execute("""
            SELECT classroom_id, day, period_id
            FROM timetable
        """)
        for row in cur.fetchall():
            classroom_id = row["classroom_id"]
            day = row["day"]
            period_id = row["period_id"]
            # Find period_no from period_id
            period_no = None
            for pno, pid in period_map.items():
                if pid == period_id:
                    period_no = pno
                    break
            if period_no:
                room_busy[(classroom_id, day, period_no)] = True
        
        # Load existing subject-per-day counts to enforce max 2 allocations per subject per day
        subject_day_count = {}
        cur.execute("""
            SELECT subject_id, day, COUNT(*) as cnt
            FROM timetable
            GROUP BY subject_id, day
        """)
        for row in cur.fetchall():
            sid = row["subject_id"]
            day = row["day"]
            subject_day_count[(sid, day)] = int(row["cnt"])

        random.shuffle(assignments)
        placed_count = 0

        # Create a dictionary mapping subject_id to weekly_hours from subjects already fetched
        subject_hours = {s["id"]: s["weekly_hours"] for s in subjects}

        # Track which (day, period_no) slots are busy for this year/course
        year_course_busy = {}

        # Track remaining slots needed for each assignment
        remaining_slots = {}
        for assignment in assignments:
            subject_id = assignment["subject_id"]
            remaining_slots[subject_id] = subject_hours.get(subject_id, 1)

        # Allocate slots in a round-robin fashion across assignments and days
        # This ensures different subjects are spread throughout the week AND all days are used
        max_iterations = sum(remaining_slots.values()) + 100  # Safety check to avoid infinite loops
        iteration = 0
        
        # Keep track of which day to start with for better distribution
        day_index = 0

        while any(v > 0 for v in remaining_slots.values()) and iteration < max_iterations:
            iteration += 1
            assignments_shuffled = [a for a in assignments if remaining_slots[a["subject_id"]] > 0]
            random.shuffle(assignments_shuffled)

            for assignment in assignments_shuffled:
                subject_id = assignment["subject_id"]
                staff_id = assignment["staff_id"]

                if remaining_slots[subject_id] <= 0:
                    continue

                # Try to allocate one slot for this subject
                # Rotate through days to ensure all days get used before repeating
                slot_allocated = False
                days_to_try = days[day_index:] + days[:day_index]  # Start from current day_index
                
                for day in days_to_try:
                    if slot_allocated:
                        break
                    # Enforce max 2 allocations per subject per day
                    if subject_day_count.get((subject_id, day), 0) >= 2:
                        continue
                    period_nos_shuffled = period_nos.copy()
                    random.shuffle(period_nos_shuffled)
                    for period_no in period_nos_shuffled:
                        if slot_allocated:
                            break
                        # Check year/course constraint - each year can only have one class per day/period
                        if (day, period_no) in year_course_busy:
                            continue
                        if (staff_id, day, period_no) in staff_busy:
                            continue

                        # Find an available room for this slot
                        room_found = None
                        rooms_shuffled = rooms.copy()
                        random.shuffle(rooms_shuffled)
                        for room in rooms_shuffled:
                            if (room, day, period_no) not in room_busy:
                                room_found = room
                                break

                        if room_found is None:
                            # No room available for this slot
                            continue

                        period_id = period_map[period_no]
                        cur.execute("""
                            INSERT INTO timetable
                            (day, period_id, subject_id, staff_id, classroom_id, year, course_id, semester)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (day, period_id, subject_id, staff_id, room_found, year, course_id, semester))

                        # Mark constraints as busy
                        year_course_busy[(day, period_no)] = True
                        staff_busy[(staff_id, day, period_no)] = True
                        room_busy[(room_found, day, period_no)] = True
                        # Update subject-day allocation count
                        subject_day_count[(subject_id, day)] = subject_day_count.get((subject_id, day), 0) + 1
                        remaining_slots[subject_id] -= 1
                        placed_count += 1
                        slot_allocated = True
                        
                        # Rotate day index for next allocation
                        day_index = (day_index + 1) % len(days)

        conn.commit()
        cur.close()
        conn.close()

        redirect_url = f"/view_timetable?year={year}&course_id={course_id}&semester={semester}&success=timetable_generated"
        if request.is_json:
            return json_response(True, f"Timetable generated! Placed {placed_count} assignments.", redirect=redirect_url)
        return redirect(redirect_url)

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        error_msg = f"Error generating timetable: {str(e)}"
        if request.is_json:
            return json_response(False, str(e))
        return error_msg, 500

# -------- FETCH TIMETABLE --------
def get_timetable_dict(year, course_id, semester=None):
    conn = get_db_connection()
    cur = get_cursor(conn)

    query = """
        SELECT
            t.day,
            p.period_no,
            s.code,
            s.name,
            st.name as staff_name
        FROM timetable t
        JOIN subjects s ON t.subject_id = s.id
        JOIN staff st ON t.staff_id = st.id
        JOIN periods p ON t.period_id = p.id
        WHERE t.year=%s AND t.course_id=%s
    """
    
    params = [year, course_id]
    
    if semester:
        query += " AND t.semester=%s"
        params.append(semester)
    
    query += " ORDER BY t.day, p.period_no"
    
    cur.execute(query, params)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    timetable = {
        "Monday": [""] * 7,
        "Tuesday": [""] * 7,
        "Wednesday": [""] * 7,
        "Thursday": [""] * 7,
        "Friday": [""] * 7
    }

    for row in rows:
        day = row["day"]
        period_no = row["period_no"]
        code = row["code"]
        name = row["name"]
        staff = row["staff_name"]
        timetable[day][period_no - 1] = (
            f"<b>{code}</b><br>"
            f"<small>{name}</small><br>"
            f"<small>{staff}</small>"
        )

    return timetable

# -------- VIEW TIMETABLE --------
@app.route("/view_timetable")
@login_required()
def view_timetable():
    year = request.args.get("year")
    course_id = request.args.get("course_id")
    semester = request.args.get("semester")

    timetable = get_timetable_dict(year, course_id, semester)
    
    # Fetch course name for display
    conn = get_db_connection()
    cur = get_cursor(conn)
    course = ""
    try:
        cur.execute("SELECT name FROM courses WHERE id=%s", (course_id,))
        row = cur.fetchone()
        if row:
            course = row.get("name", "")
    except Exception:
        course = ""
    cur.close()
    conn.close()

    return render_template(
        "timetable_view.html",
        timetable=timetable,
        year=year,
        course_id=course_id,
        semester=semester,
        course=course
    )

# -------- PRINT --------
@app.route("/print")
@login_required()
def print_timetable():
    year = request.args.get("year")
    course_id = request.args.get("course_id")
    semester = request.args.get("semester")

    timetable = get_timetable_dict(year, course_id, semester)
    # Fetch course name for display in print header
    conn = get_db_connection()
    cur = get_cursor(conn)
    course = ""
    try:
        cur.execute("SELECT name FROM courses WHERE id=%s", (course_id,))
        row = cur.fetchone()
        if row:
            course = row.get("name", "")
    except Exception:
        course = ""
    cur.close()
    conn.close()

    return render_template(
        "timetable_print.html",
        timetable=timetable,
        year=year,
        course_id=course_id,
        semester=semester,
        course=course
    )

# -------- API: GET PERIODS --------
@app.route("/api/periods")
def get_periods_api():
    conn = get_db_connection()
    cur = get_cursor(conn)
    cur.execute("SELECT period_no, start_time, end_time FROM periods ORDER BY period_no")
    periods = cur.fetchall()
    cur.close()
    conn.close()
    
    # Convert timedelta objects to strings
    periods_list = []
    for period in periods:
        periods_list.append({
            'period_no': period['period_no'],
            'start_time': str(period['start_time']),
            'end_time': str(period['end_time'])
        })
    
    return json_response(True, "Periods fetched", data=periods_list)

# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    # Only enable debug mode in development environment
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
