import os
import time
from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from db_config import con

UPLOAD_FOLDER = 'static/uploads/profile_pictures'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------ Student Signup --------------------
def studentSignup():
    if request.method == "GET":
        return render_template("templates/Signup.html")
    else:
        try:
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            contact = request.form.get("contact", "")
            course = request.form.get("course", "")
            
            # Handle profile picture upload
            profile_picture = None
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to filename to make it unique
                    filename = f"{int(time.time())}_{filename}"
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    profile_picture = f"uploads/profile_pictures/{filename}"

            cursor = con.cursor(dictionary=True)
            
            # Check if email already exists
            cursor.execute("SELECT * FROM student WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Email already registered")
                return redirect(url_for("Signup"))

            # Insert new student with profile picture
            sql = "INSERT INTO student (name, email, password, contact, course, profile_picture) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (name, email, password, contact, course, profile_picture)
            cursor.execute(sql, val)
            con.commit()

            flash("Registration successful! Please login.")
            return redirect(url_for("studentLogin"))
        except Exception as e:
            print(f"Error in student signup: {str(e)}")
            flash("An error occurred during registration")
            return redirect(url_for("studentSignup"))

# ------------------ Student Login --------------------
def studentLogin():
    if request.method == "GET":
        return render_template("user/studentLogin.html")
    else:
        try:
            email = request.form["email"]
            password = request.form["password"]
            
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM student WHERE email = %s AND password = %s"
            val = (email, password)
            cursor.execute(sql, val)
            student = cursor.fetchone()
            
            if student:
                session["student"] = student["email"]
                session["student_id"] = student["sid"]
                session["student_name"] = student["name"]
                return redirect(url_for("studentDashboard"))
            else:
                flash("Invalid email or password")
                return redirect(url_for("studentLogin"))
        except Exception as e:
            print(f"Error during login: {str(e)}")
            flash("An error occurred during login")
            return redirect(url_for("studentLogin"))

# ------------------ Student Dashboard --------------------
def studentDashboard():
    if "student" not in session:
        return redirect(url_for("studentLogin"))

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM student WHERE email = %s", (session["student"],))
    student = cursor.fetchone()
    
    return render_template("user/studentDashboard.html", student=student)

# ------------------ Student Logout --------------------
def studentLogout():
    session.pop("student", None)
    session.pop("student_id", None)
    session.pop("student_name", None)
    return redirect(url_for("studentLogin"))

def editStudentProfile():
    if "student" not in session:
        return redirect(url_for("studentLogin"))
    
    cursor = con.cursor(dictionary=True)
    email = session["student"]
    
    if request.method == "GET":
        cursor.execute("SELECT * FROM student WHERE email=%s", (email,))
        student = cursor.fetchone()
        return render_template("user/editStudent.html", student=student)
    
    else:
        try:
            name = request.form["name"]
            contact = request.form["contact"]
            course = request.form["course"]
            
            # Handle profile picture upload
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to filename to make it unique
                    filename = f"{int(time.time())}_{filename}"
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    profile_picture = f"uploads/profile_pictures/{filename}"
                    
                    # Update profile with new picture
                    sql = "UPDATE student SET name=%s, contact=%s, course=%s, profile_picture=%s WHERE email=%s"
                    val = (name, contact, course, profile_picture, email)
                else:
                    # Update profile without changing picture
                    sql = "UPDATE student SET name=%s, contact=%s, course=%s WHERE email=%s"
                    val = (name, contact, course, email)
            else:
                # Update profile without changing picture
                sql = "UPDATE student SET name=%s, contact=%s, course=%s WHERE email=%s"
                val = (name, contact, course, email)
                
            cursor.execute(sql, val)
            con.commit()
            flash("Profile updated successfully")
            return redirect(url_for("studentDashboard"))
            
        except Exception as e:
            print(f"Error updating profile: {str(e)}")
            flash("An error occurred while updating profile")
            return redirect(url_for("editStudentProfile"))


def uploadProfileImage():
    if "student" not in session:
        return redirect(url_for("studentLogin"))

    sid = session["student_id"]
    file = request.files.get("profile_image")

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        rel_path = f"uploads/{filename}"

        cursor = con.cursor()
        cursor.execute("UPDATE student SET profile_picture = %s WHERE sid = %s", (rel_path, sid))
        con.commit()

    return redirect(url_for("studentDashboard"))


def viewMarks():
    if "student" not in session:
        return redirect(url_for("studentLogin"))

    cursor = con.cursor(dictionary=True)
    email = session["student"]

    cursor.execute("SELECT sid FROM student WHERE email=%s", (email,))
    sid = cursor.fetchone()["sid"]

    cursor.execute("""
        SELECT sub.subject_name AS subject, m.marks, m.assessment_type, m.created_at
        FROM marks m
        JOIN subjects sub ON m.subid = sub.subid
        WHERE m.sid = %s
        ORDER BY m.created_at DESC
    """, (sid,))
    all_marks = cursor.fetchall()

    return render_template("user/viewMarks.html", marks=all_marks)


def viewAttendance():
    if "student" not in session:
        return redirect(url_for("studentLogin"))

    cursor = con.cursor(dictionary=True)
    email = session["student"]

    cursor.execute("SELECT sid FROM student WHERE email=%s", (email,))
    sid = cursor.fetchone()["sid"]

    # Fetch attendance grouped by subject with counts of present and total classes
    cursor.execute("""
        SELECT sub.subject_name AS subject,
               SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_count,
               COUNT(*) AS total_classes
        FROM attendance a
        JOIN subjects sub ON a.subid = sub.subid
        WHERE a.sid = %s
        GROUP BY a.subid
    """, (sid,))
    attendance_records = cursor.fetchall()

    return render_template("user/viewAttendance.html", attendance=attendance_records)
def viewFees():
    if "student" not in session:
        return redirect(url_for("studentLogin"))

    cursor = con.cursor(dictionary=True)
    email = session["student"]

    cursor.execute("SELECT sid FROM student WHERE email=%s", (email,))
    sid = cursor.fetchone()["sid"]

    cursor.execute("""
        SELECT amount, status, due_date, created_at
        FROM fees
        WHERE sid = %s
        ORDER BY due_date ASC
    """, (sid,))
    fees = cursor.fetchall()

    return render_template("user/viewFees.html", fees=fees)
