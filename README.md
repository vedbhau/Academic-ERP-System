# 🎓 ERP System – Flask-Based Educational Management

## 📌 Project Overview
This project is a comprehensive ERP (Enterprise Resource Planning) system designed for educational institutions. Built using the Flask web framework, it facilitates efficient management of students, teachers, courses, attendance, marks, fees, and timetables. The system supports multiple user roles including Admin, Teacher, and Student, each with tailored functionalities to streamline academic and administrative processes.

## ✨ Features

- 🔐 **Role-Based Authentication**: Secure login system for Admin, Teacher, and Student roles
- 👨‍🎓 **Student Module**: Registration, profile updates, academic record viewing (marks, attendance, fees)
- 👩‍🏫 **Teacher Module**: Subject assignments, attendance marking, and marks entry
- 📝 **Attendance Management**: Track student attendance subject-wise
- 🧮 **Marks Management**: Add and view internal/exam assessments
- 💳 **Fee Management**: Fee submission, fee status tracking, and receipt generation
- 📅 **Timetable Module**: Organized timetable for both students and teachers
- 📊 **Admin Dashboard**: Centralized control panel for managing users and data
- 📁 **PDF Receipt Generation (optional)**: Generate downloadable fee receipts using PDF tools
- 🌐 **Responsive UI**: Clean and user-friendly interface using Bootstrap
- 🗃️ **Database Integration**: Fully integrated with MySQL (or SQLite alternative)


## Technologies Used
- Python 3.x
- Flask Web Framework
- HTML5, CSS3, JavaScript (for frontend templates)
- SQLite / SQL (for database management)
- Jinja2 templating engine
- Bootstrap (assumed for styling based on templates)
- Other Python libraries as per requirements 

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd d:/Erp_system_flask project
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # On Windows
   source venv/bin/activate  # On Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Run the provided SQL scripts (`database.sql`, `add_courses.sql`, `add_subjects.sql`, etc.) to initialize the database schema and seed data.

5. Run the Flask application:
   ```bash
   python app.py
   ```

6. Access the application in your browser at:
   ```
   http://localhost:5000
   ```

## Project Structure

```
d:/Erp_system_flask project/
│
├── app.py                  # Main Flask application
├── admin.py                # Admin related routes and logic
├── teacher.py              # Teacher related routes and logic
├── user.py                 # User (student) related routes and logic
├── db_config.py            # Database configuration
├── database.sql            # SQL script for initial database setup
├── add_courses.sql         # SQL script to add courses
├── add_subjects.sql        # SQL script to add subjects
├── static/                 # Static assets (images, CSS, JS)
├── templates/              # HTML templates organized by user roles
│   ├── admin/
│   ├── teacher/
│   └── user/
├── README.md               # Project documentation
└── LICENSE                 # License information
```

## Usage

- Admin users can manage students, teachers, fees, and generate reports.
- Teachers can manage attendance, marks, and view their assigned subjects.
- Students can view their attendance, marks, fees, and timetable.
- Login and signup pages are provided for authentication.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with clear messages.
4. Push your branch and create a pull request.

Please ensure your code follows the existing style and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [MIT LICENSE](LICENSE) file for details.

---
## 📬 Contact
For any questions or support, please contact 
email - work.vedm@gmail.com
