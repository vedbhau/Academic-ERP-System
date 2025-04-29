from app import app
from flask import render_template, request, redirect, url_for, flash, jsonify
import admin as admin
import user as user
import teacher as teacher
import mysql.connector

# Database connection
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ved@7236",
    database="college_erp"
)

# Admin routes
import admin
app.add_url_rule("/adminLogin", view_func=admin.adminLogin, methods=["GET", "POST"])
app.add_url_rule("/adminDashboard", view_func=admin.adminDashboard)
app.add_url_rule("/addStudent", view_func=admin.addStudent, methods=["GET", "POST"])
app.add_url_rule("/deleteStudent/<sid>", view_func=admin.deleteStudent)
app.add_url_rule("/editStudent/<sid>", view_func=admin.editStudent, methods=["GET", "POST"])
app.add_url_rule("/adminLogout", view_func=admin.adminLogout)
app.add_url_rule("/manageTeacherSubjects", view_func=admin.manageTeacherSubjects, methods=["GET"])
app.add_url_rule("/adminAddSubject/<int:tid>", view_func=admin.adminAddSubject, methods=["POST"])
app.add_url_rule("/adminRemoveSubject/<int:tid>/<int:subid>", view_func=admin.adminRemoveSubject, methods=["POST"])

# Admin Fee Management Routes
app.add_url_rule("/admin/manage_fees", view_func=admin.manageFees, methods=["GET"])
app.add_url_rule("/admin/add_fee", view_func=admin.addFee, methods=["GET", "POST"])
app.add_url_rule("/admin/edit_fee/<int:feeid>", view_func=admin.editFee, methods=["GET", "POST"])
app.add_url_rule("/admin/update_fee_status/<int:feeid>", view_func=admin.updateFeeStatus, methods=["POST"])
app.add_url_rule("/admin/delete_fee/<int:feeid>", view_func=admin.deleteFee, methods=["GET"])
# Add this with other admin routes
app.add_url_rule("/admin/fee-report", view_func=admin.feeReport, methods=["GET"], endpoint="feeReport")

# ... existing routes ...


# User routes
app.add_url_rule("/Signup", view_func=user.studentSignup, methods=["GET", "POST"])
app.add_url_rule("/studentLogin", view_func=user.studentLogin, methods=["GET", "POST"])
app.add_url_rule("/studentDashboard", view_func=user.studentDashboard)
app.add_url_rule("/studentLogout", view_func=user.studentLogout)
app.add_url_rule("/editStudent", view_func=user.editStudentProfile, methods=["GET", "POST"])
app.add_url_rule("/viewMarks", view_func=user.viewMarks)
app.add_url_rule("/student/viewAttendance", view_func=user.viewAttendance)
app.add_url_rule("/viewFees", view_func=user.viewFees, methods=["GET"])



# Teacher routes
app.add_url_rule("/Signup", view_func=teacher.teacherSignup, methods=["GET", "POST"])
app.add_url_rule("/teacherLogin", view_func=teacher.teacherLogin, methods=["GET", "POST"])
app.add_url_rule("/teacherDashboard", view_func=teacher.teacherDashboard)
app.add_url_rule("/teacherLogout", view_func=teacher.teacherLogout)
app.add_url_rule("/addMarks", view_func=teacher.addMarks, methods=["GET", "POST"])
app.add_url_rule("/teacher/viewMarks", view_func=teacher.teacherViewMarks, methods=["GET"], endpoint="teacherViewMarks")
app.add_url_rule("/manageSubjects", view_func=teacher.manageSubjects, methods=["GET"])
app.add_url_rule("/addSubject/<int:subid>", view_func=teacher.addSubject, methods=["POST"])
app.add_url_rule("/removeSubject/<int:subid>", view_func=teacher.removeSubject, methods=["POST"])





# Signup route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        user_type = request.form.get("user_type")
        if user_type == "student":
            # Handle student signup
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            contact = request.form.get("contact")
            course = request.form.get("course")
            photo = request.files.get("photo")
            
            # Save student data to database
            cursor = con.cursor()
            try:
                # First, check if the course exists
                cursor.execute("SELECT cid FROM courses WHERE course_name = %s", (course,))
                course_result = cursor.fetchone()
                
                if not course_result:
                    flash(f"Course '{course}' does not exist. Please select a valid course.", "error")
                    return redirect(url_for("signup"))
                
                course_id = course_result[0]
                
                # Insert student data
                sql = "INSERT INTO student (name, email, password, contact, course) VALUES (%s, %s, %s, %s, %s)"
                val = (name, email, password, contact, course_id)
                cursor.execute(sql, val)
                con.commit()
                
                # Handle photo upload if provided
                if photo:
                    sid = cursor.lastrowid
                    filename = f"student_{sid}.jpg"
                    photo.save(f"static/uploads/{filename}")
                    cursor.execute("UPDATE student SET profile_picture = %s WHERE sid = %s", (filename, sid))
                    con.commit()
                
                flash("Student signup successful!", "success")
                return redirect(url_for("studentLogin"))
            except Exception as e:
                con.rollback()
                flash(f"Error during signup: {str(e)}", "error")
                return redirect(url_for("signup"))
            
        elif user_type == "teacher":
            # Handle teacher signup
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            branch = request.form.get("branch")
            photo = request.files.get("photo")
            
            # Save teacher data to database
            cursor = con.cursor()
            try:
                sql = "INSERT INTO teacher (name, email, password, branch) VALUES (%s, %s, %s, %s)"
                val = (name, email, password, branch)
                cursor.execute(sql, val)
                con.commit()
                
                # Handle photo upload if provided
                if photo:
                    tid = cursor.lastrowid
                    filename = f"teacher_{tid}.jpg"
                    photo.save(f"static/uploads/{filename}")
                    cursor.execute("UPDATE teacher SET profile_picture = %s WHERE tid = %s", (filename, tid))
                    con.commit()
                
                flash("Teacher signup successful!", "success")
                return redirect(url_for("teacherLogin"))
            except Exception as e:
                con.rollback()
                flash(f"Error during signup: {str(e)}", "error")
                return redirect(url_for("signup"))
            
        elif user_type == "admin":
            # Handle admin signup
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            
            # Save admin data to database
            cursor = con.cursor()
            try:
                sql = "INSERT INTO admin (username, password) VALUES (%s, %s)"
                val = (email, password)  # Using email as username
                cursor.execute(sql, val)
                con.commit()
                
                flash("Admin signup successful!", "success")
                return redirect(url_for("adminLogin"))
            except Exception as e:
                con.rollback()
                flash(f"Error during signup: {str(e)}", "error")
                return redirect(url_for("signup"))
            
        else:
            flash("Invalid user type selected", "error")
            return redirect(url_for("signup"))

@app.route("/")
def homepage():
    return render_template('home.html')

app.add_url_rule("/addAttendance", view_func=teacher.addAttendance, methods=["GET", "POST"])
# Removed conflicting routes for viewAttendance
# Re-adding with distinct routes

app.add_url_rule("/teacher/viewAttendance", view_func=teacher.viewAttendance, endpoint="teacherViewAttendance")
app.add_url_rule("/student/viewAttendance", view_func=user.viewAttendance, endpoint="studentViewAttendance")

app.add_url_rule("/uploadProfileImage", view_func=user.uploadProfileImage, methods=["POST"])

@app.route("/get_subjects/<int:course_id>")
def get_subjects(course_id):
    cursor = con.cursor(dictionary=True)
    try:
        # Get subjects for the course
        cursor.execute("""
            SELECT s.subid, s.subject_name, s.semester, c.course_name
            FROM subjects s
            JOIN courses c ON s.course_id = c.cid
            WHERE s.course_id = %s
            ORDER BY s.semester, s.subject_name
        """, (course_id,))
        subjects = cursor.fetchall()
        print(f"Found {len(subjects)} subjects for course_id {course_id}")
        print(f"Subjects: {subjects}")
        return jsonify(subjects)
    except Exception as e:
        print(f"Error fetching subjects: {str(e)}")
        return jsonify([])
    finally:
        cursor.close()
