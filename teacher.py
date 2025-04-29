from flask import render_template, request, redirect, url_for, session, flash
from db_config import con

def teacherLogin():
    if request.method == "GET":
        return render_template("teacher/teacherLogin.html")
    else:
        email = request.form["email"]
        password = request.form["password"]
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teacher WHERE email=%s AND password=%s", (email, password))
        teacher = cursor.fetchone()
        if teacher:
            session["teacher"] = teacher["tid"]
            session["teacher_name"] = teacher["name"]
            session["teacher_email"] = teacher["email"]
            return redirect(url_for("teacherDashboard"))
        else:
            flash("Invalid credentials")
            return redirect(url_for("teacherLogin"))
        
# Teacher Signup Function
def teacherSignup():
    if request.method == "GET":
        return render_template("templates/Signup.html")
    else:
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        branch = request.form["branch"]
        
        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("Signup"))

        # Check if the email already exists
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teacher WHERE email=%s", (email,))
        existing_teacher = cursor.fetchone()
        if existing_teacher:
            flash("Email already registered.")
            return redirect(url_for("Signup"))

        # Insert new teacher into the database
        cursor.execute(
            "INSERT INTO teacher (name, email, password, branch) VALUES (%s, %s, %s, %s)",
            (name, email, password, branch)
        )
        con.commit()

        flash("Teacher account created successfully. Please log in.")
        return redirect(url_for("teacherLogin"))


def teacherLogout():
    session.pop("teacher", None)
    return redirect(url_for("teacherLogin"))

def teacherDashboard():
    if "teacher" not in session:
        return redirect(url_for("teacherLogin"))

    tid = session["teacher"]
    cursor = con.cursor(dictionary=True)
    # Fetch distinct courses assigned to the teacher by joining teacher_subjects, subjects, and courses
    cursor.execute("""
        SELECT DISTINCT c.cid, c.course_name AS name, c.branch
        FROM courses c
        JOIN subjects s ON c.cid = s.course_id
        JOIN teacher_subjects ts ON s.subid = ts.subid
        WHERE ts.tid = %s
    """, (tid,))
    courses = cursor.fetchall()
    
    # Get teacher details
    cursor.execute("SELECT * FROM teacher WHERE tid=%s", (tid,))
    teacher = cursor.fetchone()
    
    return render_template("teacher/teacherDashboard.html", courses=courses, teacher=teacher)

def addAttendance():
    if "teacher" not in session:
        return redirect(url_for("teacherLogin"))

    if request.method == "GET":
        cursor = con.cursor(dictionary=True)
        tid = session["teacher"]
        
        # Get courses assigned to the teacher by joining teacher_subjects, subjects, and courses
        cursor.execute("""
            SELECT DISTINCT c.cid, c.course_name AS name, c.branch
            FROM courses c
            JOIN subjects s ON c.cid = s.course_id
            JOIN teacher_subjects ts ON s.subid = ts.subid
            WHERE ts.tid = %s
        """, (tid,))
        courses = cursor.fetchall()
        
        # Get students
        cursor.execute("SELECT * FROM student")
        students = cursor.fetchall()
        
        return render_template("teacher/addAttendance.html", courses=courses, students=students)
    else:
        try:
            selected_date = request.form["date"]
            status = request.form["status"]
            student_id = request.form["student"]
            course_id = request.form["course"]
            subid = request.form["subject"]
            tid = session["teacher"]

            cursor = con.cursor()
            sql = "INSERT INTO attendance (sid, tid, cid, subid, date, status) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (student_id, tid, course_id, subid, selected_date, status)
            cursor.execute(sql, val)
            con.commit()
            flash("Attendance recorded successfully.", "success")
            return redirect(url_for("teacherDashboard"))
        except Exception as e:
            flash(f"Error recording attendance: {str(e)}", "error")
            return redirect(url_for("addAttendance"))

def viewAttendance():
    if "teacher" not in session:
        return redirect(url_for("teacherLogin"))

    cursor = con.cursor(dictionary=True)
    tid = session["teacher"]
    
    cursor.execute("SELECT * FROM courses WHERE tid=%s", (tid,))
    courses = cursor.fetchall()

    course_id = request.args.get('course')
    date = request.args.get('date')
    
    sql = """
        SELECT a.date, c.course_name as course_name, s.name as student_name, a.status
        FROM attendance a
        JOIN student s ON a.sid = s.sid
        JOIN courses c ON a.cid = c.cid
        WHERE a.tid = %s
    """
    params = [tid]

    if course_id:
        sql += " AND a.cid = %s"
        params.append(course_id)

    if date:
        sql += " AND DATE(a.date) = %s"
        params.append(date)

    sql += " ORDER BY a.date DESC"

    cursor.execute(sql, tuple(params))
    records = cursor.fetchall()
    return render_template("teacher/viewAttendance.html", records=records, courses=courses)

def addMarks():
    if "teacher" not in session:
        return redirect(url_for("teacherLogin"))
    
    teacher_id = session["teacher"]
    cursor = con.cursor(dictionary=True)
    
    try:
        # Get courses for the teacher by joining teacher_subjects, subjects, and courses
        cursor.execute("""
            SELECT DISTINCT c.cid, c.course_name, c.branch
            FROM courses c
            JOIN subjects s ON c.cid = s.course_id
            JOIN teacher_subjects ts ON s.subid = ts.subid
            WHERE ts.tid = %s
        """, (teacher_id,))
        courses = cursor.fetchall()
        print(f"Found {len(courses)} courses for teacher_id {teacher_id}")
        print(f"Courses: {courses}")
        
        # Get all students
        cursor.execute("SELECT * FROM student")
        students = cursor.fetchall()
        print(f"Found {len(students)} students")
        
        if request.method == "POST":
            course_id = request.form["course"]
            subject_id = request.form["subject"]
            student_id = request.form["student"]
            assessment_type = request.form["assessment_type"]
            marks = request.form["marks"]
            
            print(f"Debug: course_id={course_id}, subject_id={subject_id}, student_id={student_id}, teacher_id={teacher_id}, assessment_type={assessment_type}, marks={marks}")
            
            # Insert marks into database
            cursor.execute("""
                INSERT INTO marks (sid, cid, subid, tid, assessment_type, marks)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (student_id, course_id, subject_id, teacher_id, assessment_type, marks))
            con.commit()
            
            flash("Marks added successfully!", "success")
            return redirect(url_for("teacherDashboard"))
        
        return render_template("teacher/addMarks.html", courses=courses, students=students)
    except Exception as e:
        print(f"Error in addMarks: {str(e)}")
        flash("An error occurred while processing your request.", "error")
        return redirect(url_for("teacherDashboard"))
    finally:
        cursor.close()

# NEW FUNCTION: View Marks
def teacherViewMarks():
    if "teacher" not in session:
        return redirect(url_for("teacherLogin"))
    
    tid = session["teacher"]
    cursor = con.cursor(dictionary=True)

    # Fetch distinct courses assigned to the teacher by joining teacher_subjects, subjects, and courses
    cursor.execute("""
        SELECT DISTINCT c.cid, c.course_name AS name, c.branch
        FROM courses c
        JOIN subjects s ON c.cid = s.course_id
        JOIN teacher_subjects ts ON s.subid = ts.subid
        WHERE ts.tid = %s
    """, (tid,))
    courses = cursor.fetchall()

    course_id = request.args.get("course")
    assessment_type = request.args.get("assessment_type")

    sql = """
        SELECT c.course_name as course_name, s.name as student_name,
               m.assessment_type, m.marks, m.created_at as date_added
        FROM marks m
        JOIN student s ON m.sid = s.sid
        JOIN courses c ON m.cid = c.cid
        WHERE m.tid = %s
    """
    params = [tid]

    if course_id:
        sql += " AND m.cid = %s"
        params.append(course_id)

    if assessment_type:
        sql += " AND m.assessment_type = %s"
        params.append(assessment_type)

    sql += " ORDER BY m.marks DESC"

    cursor.execute(sql, tuple(params))
    records = cursor.fetchall()
    
    return render_template("teacher/viewMarks.html", records=records, courses=courses)

def manageSubjects():
    if "teacher" not in session:
        return redirect(url_for("teacherLogin"))

    cursor = con.cursor(dictionary=True)
    tid = session["teacher"]

    # Get teacher's current subjects
    cursor.execute("""
        SELECT s.subid, s.subject_name, s.semester, c.course_name
        FROM subjects s
        JOIN teacher_subjects ts ON s.subid = ts.subid
        JOIN courses c ON s.course_id = c.cid
        WHERE ts.tid = %s
    """, (tid,))
    teacher_subjects = cursor.fetchall()

    # Get available subjects (subjects not assigned to the teacher)
    cursor.execute("""
        SELECT s.subid, s.subject_name, s.semester, c.course_name
        FROM subjects s
        JOIN courses c ON s.course_id = c.cid
        WHERE s.subid NOT IN (
            SELECT subid FROM teacher_subjects WHERE tid = %s
        )
    """, (tid,))
    available_subjects = cursor.fetchall()

    return render_template("teacher/manageSubjects.html", 
                         teacher_subjects=teacher_subjects,
                         available_subjects=available_subjects)

def addSubject(subid):
    if "teacher" not in session:
        return redirect(url_for("teacherLogin"))

    cursor = con.cursor()
    tid = session["teacher"]

    try:
        # Check if the subject is already assigned to the teacher
        cursor.execute("SELECT * FROM teacher_subjects WHERE tid = %s AND subid = %s", (tid, subid))
        if cursor.fetchone():
            flash("This subject is already assigned to you", "error")
            return redirect(url_for("manageSubjects"))

        # Assign the subject to the teacher
        cursor.execute("INSERT INTO teacher_subjects (tid, subid) VALUES (%s, %s)", (tid, subid))
        con.commit()
        flash("Subject added successfully", "success")
    except Exception as e:
        flash(f"Error adding subject: {str(e)}", "error")

    return redirect(url_for("manageSubjects"))

def removeSubject(subid):
    if "teacher" not in session:
        return redirect(url_for("teacherLogin"))

    cursor = con.cursor()
    tid = session["teacher"]

    try:
        cursor.execute("DELETE FROM teacher_subjects WHERE tid = %s AND subid = %s", (tid, subid))
        con.commit()
        flash("Subject removed successfully", "success")
    except Exception as e:
        flash(f"Error removing subject: {str(e)}", "error")

    return redirect(url_for("manageSubjects"))

