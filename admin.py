from flask import render_template, request, redirect, url_for, session, flash
from db_config import con

# ------------------ Admin Login --------------------
def adminLogin():
    if request.method == "GET":
        return render_template("admin/adminLogin.html")
    else:
        try:
            username = request.form["username"]
            password = request.form["password"]
            
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM admin WHERE username = %s AND password = %s"
            val = (username, password)
            cursor.execute(sql, val)
            admin = cursor.fetchone()
            
            if admin:
                session["admin"] = admin["username"]
                return redirect(url_for("adminDashboard"))
            else:
                flash("Invalid username or password")
                return redirect(url_for("adminLogin"))
        except Exception as e:
            print(f"Error during admin login: {str(e)}")
            flash("An error occurred during login")
            return redirect(url_for("adminLogin"))

# ------------------ Admin Logout --------------------
def adminLogout():
    session.pop("admin", None)
    return redirect(url_for("adminLogin"))

# ------------------ Admin Dashboard --------------------
# def adminDashboard():
#     if "admin" not in session:
#         return redirect(url_for("adminLogin"))
    
#     cursor = con.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM student")
#     students = cursor.fetchall()
    
#     return render_template("admin/adminDashboard.html", students=students)

def adminDashboard():
    if "admin" not in session:
        return redirect(url_for("adminLogin"))
    
    cursor = con.cursor(dictionary=True)
    sql = "SELECT * FROM admin WHERE username = %s"
    val = (session['admin'],)
    cursor.execute(sql, val)
    admin = cursor.fetchone()

    return render_template("admin/adminDashboard.html", admin=admin)
# ------------------ Add Student --------------------
def addStudent():
    if "admin" not in session:
        return redirect(url_for("adminLogin"))
    
    if request.method == "GET":
        return render_template("admin/addStudent.html")
    else:
        try:
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            contact = request.form.get("contact", "")
            course = request.form.get("course", "")

            cursor = con.cursor(dictionary=True)
            
            # Check if email already exists
            cursor.execute("SELECT * FROM student WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Email already registered")
                return redirect(url_for("addStudent"))

            # Insert new student
            sql = "INSERT INTO student (name, email, password, contact, course) VALUES (%s, %s, %s, %s, %s)"
            val = (name, email, password, contact, course)
            cursor.execute(sql, val)
            con.commit()

            flash("Student added successfully")
            return redirect(url_for("adminDashboard"))
        except Exception as e:
            print(f"Error adding student: {str(e)}")
            flash("An error occurred while adding student")
            return redirect(url_for("addStudent"))

# ------------------ Delete Student --------------------
def deleteStudent(sid):
    if "admin" not in session:
        return redirect(url_for("adminLogin"))
    
    try:
        cursor = con.cursor()
        sql = "DELETE FROM student WHERE sid = %s"
        val = (sid,)
        cursor.execute(sql, val)
        con.commit()
        flash("Student deleted successfully")
    except Exception as e:
        print(f"Error deleting student: {str(e)}")
        flash("An error occurred while deleting student")
    
    return redirect(url_for("adminDashboard"))

# ------------------ Edit Student --------------------
def editStudent(sid):
    if "admin" not in session:
        return redirect(url_for("adminLogin"))
    
    cursor = con.cursor(dictionary=True)
    
    if request.method == "GET":
        cursor.execute("SELECT * FROM student WHERE sid = %s", (sid,))
        student = cursor.fetchone()
        return render_template("admin/editStudent.html", student=student)
    else:
        try:
            name = request.form["name"]
            email = request.form["email"]
            contact = request.form["contact"]
            course = request.form["course"]
            
            # Check if email is being changed to an existing one
            cursor.execute("SELECT * FROM student WHERE email = %s AND sid != %s", (email, sid))
            if cursor.fetchone():
                flash("Email already registered")
                return redirect(url_for("editStudent", sid=sid))
            
            sql = "UPDATE student SET name = %s, email = %s, contact = %s, course = %s WHERE sid = %s"
            val = (name, email, contact, course, sid)
            cursor.execute(sql, val)
            con.commit()
            
            flash("Student updated successfully")
            return redirect(url_for("adminDashboard"))
        except Exception as e:
            print(f"Error updating student: {str(e)}")
            flash("An error occurred while updating student")
            return redirect(url_for("editStudent", sid=sid))

def manageTeacherSubjects():
    if "admin" not in session:
        return redirect(url_for("adminLogin"))

    cursor = con.cursor(dictionary=True)

    # Get all teachers
    cursor.execute("""
        SELECT t.tid, t.name, t.email, t.branch
        FROM teacher t
        ORDER BY t.name
    """)
    teachers = cursor.fetchall()

    # Get subjects for each teacher
    for teacher in teachers:
        cursor.execute("""
            SELECT s.* 
            FROM subjects s
            JOIN teacher_subjects ts ON s.subid = ts.subid
            WHERE ts.tid = %s
        """, (teacher['tid'],))
        teacher['subjects'] = cursor.fetchall()

    # Get all available subjects
    cursor.execute("SELECT * FROM subjects ORDER BY subject_name")
    all_subjects = cursor.fetchall()

    return render_template("admin/manageTeacherSubjects.html", 
                         teachers=teachers, 
                         all_subjects=all_subjects)
def adminAddSubject(tid):
    if "admin" not in session:
        return redirect(url_for("adminLogin"))

    cursor = con.cursor()
    subid = request.form.get("subject")

    try:
        # Check if the subject is already assigned to the teacher
        cursor.execute("SELECT * FROM teacher_subjects WHERE tid = %s AND subid = %s", (tid, subid))
        if cursor.fetchone():
            flash("This subject is already assigned to the teacher", "error")
            return redirect(url_for("manageTeacherSubjects"))

        # Assign the subject to the teacher
        cursor.execute("INSERT INTO teacher_subjects (tid, subid) VALUES (%s, %s)", (tid, subid))
        con.commit()
        flash("Subject assigned successfully", "success")
    except Exception as e:
        flash(f"Error assigning subject: {str(e)}", "error")

    return redirect(url_for("manageTeacherSubjects"))

def adminRemoveSubject(tid, subid):
    if "admin" not in session:
        return redirect(url_for("adminLogin"))

    cursor = con.cursor()

    try:
        cursor.execute("DELETE FROM teacher_subjects WHERE tid = %s AND subid = %s", (tid, subid))
        con.commit()
        flash("Subject removed successfully", "success")
    except Exception as e:
        flash(f"Error removing subject: {str(e)}", "error")

    return redirect(url_for("manageTeacherSubjects"))

# ------------------ Manage Fees --------------------
def manageFees():
    if "admin" not in session:
        return redirect(url_for("adminLogin"))

    cursor = con.cursor(dictionary=True)

    # Fetch all students with their fee details
    cursor.execute("""
        SELECT s.sid, s.name, f.feeid, f.amount, f.status, f.due_date
        FROM student s
        LEFT JOIN fees f ON s.sid = f.sid
        ORDER BY s.name
    """)
    fees = cursor.fetchall()

    return render_template("admin/manageFees.html", fees=fees)

# ------------------ Add Fee --------------------
def addFee():
    if "admin" not in session:
        return redirect(url_for("adminLogin"))
    
    cursor = con.cursor(dictionary=True)

    if request.method == "GET":
        # Fetch students list for dropdown
        cursor.execute("SELECT sid, name FROM student ORDER BY name")
        students = cursor.fetchall()
        return render_template("admin/addFee.html", students=students)
    else:
        try:
            sid = request.form["sid"]
            amount = request.form["amount"]
            due_date = request.form["due_date"]
            status = request.form["status"]  # Get the fee status (Paid or Pending)
            payment_date = request.form.get("payment_date")  # Payment date is optional

            # If the status is "Paid", ensure payment_date is provided
            if status == "Paid" and not payment_date:
                flash("Payment date is required for paid fees", "error")
                return redirect(url_for("addFee"))

            # Insert the fee record into the database
            cursor.execute("""
                INSERT INTO fees (sid, amount, due_date, status, payment_date) 
                VALUES (%s, %s, %s, %s, %s)
            """, (sid, amount, due_date, status, payment_date if payment_date else None))

            con.commit()

            flash("Fee record added successfully", "success")
            return redirect(url_for("manageFees"))
        except Exception as e:
            print(f"Error adding fee: {str(e)}")
            flash("An error occurred while adding fee", "error")
            return redirect(url_for("addFee"))


# ------------------ Update Fee Status --------------------
def updateFeeStatus(feeid):
    if "admin" not in session:
        return redirect(url_for("adminLogin"))

    try:
        new_status = request.form["status"]  # Paid or Pending
        cursor = con.cursor()
        cursor.execute("UPDATE fees SET status = %s WHERE feeid = %s", (new_status, feeid))
        con.commit()
        flash("Fee status updated successfully", "success")
    except Exception as e:
        print(f"Error updating fee status: {str(e)}")
        flash("An error occurred while updating fee status", "error")
    
    return redirect(url_for("manageFees"))

# ------------------ Delete Fee Record --------------------
def deleteFee(feeid):
    if "admin" not in session:
        return redirect(url_for("adminLogin"))

    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM fees WHERE feeid = %s", (feeid,))
        con.commit()
        flash("Fee record deleted successfully", "success")
    except Exception as e:
        print(f"Error deleting fee record: {str(e)}")
        flash("An error occurred while deleting fee record", "error")

    return redirect(url_for("manageFees"))

def adminDashboard():
    if "admin" not in session:
        return redirect(url_for("adminLogin"))
    
    cursor = con.cursor(dictionary=True)
    sql = "SELECT * FROM admin WHERE username = %s"
    val = (session['admin'],)
    cursor.execute(sql, val)
    admin = cursor.fetchone()

    return render_template("admin/adminDashboard.html", admin=admin)

def editFee(feeid):
    if "admin" not in session:
        return redirect(url_for("adminLogin"))
    
    cursor = con.cursor(dictionary=True)
    
    if request.method == "GET":
        # Fetch the fee record
        cursor.execute("""
            SELECT f.*, s.name 
            FROM fees f 
            JOIN student s ON f.sid = s.sid 
            WHERE f.feeid = %s
        """, (feeid,))
        fee = cursor.fetchone()
        return render_template("admin/editFee.html", fee=fee)
    
    elif request.method == "POST":
        try:
            amount = request.form["amount"]
            due_date = request.form["due_date"]
            fee_type = request.form["fee_type"]
            status = request.form["status"]
            
            sql = """
                UPDATE fees 
                SET amount = %s, due_date = %s, fee_type = %s, status = %s
                WHERE feeid = %s
            """
            val = (amount, due_date, fee_type, status, feeid)
            cursor.execute(sql, val)
            con.commit()
            
            flash("Fee record updated successfully", "success")
            return redirect(url_for("manageFees"))
            
        except Exception as e:
            print(f"Error updating fee: {str(e)}")
            flash("An error occurred while updating the fee record", "error")
            return redirect(url_for("editFee", feeid=feeid))

def feeReport():
    if "admin" not in session:
        return redirect(url_for("adminLogin"))
    
    cursor = con.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT s.sid, s.name, f.feeid, f.amount, f.status, f.due_date, f.payment_date
            FROM student s
            LEFT JOIN fees f ON s.sid = f.sid
            ORDER BY s.name
        """)
        fee_report = cursor.fetchall()
        return render_template("admin/feeReport.html", fee_report=fee_report)
    except Exception as e:
        print(f"Error fetching fee report: {str(e)}")
        flash("An error occurred while fetching the fee report", "error")
        return redirect(url_for("adminDashboard"))
