# Student Performance Analysis and Management System

## 1. Project Overview

The Student Performance Analysis and Management System is a web-based application developed using Python and Flask. It helps manage student information, record examination marks, calculate academic performance, and analyze student results through an interactive dashboard.

The system uses SQLite to store student records and provides visual reports to understand academic performance.

## 2. Objectives

- Maintain student details digitally.
- Store student names, USNs, departments, and academic details.
- Enter and manage marks for six subjects.
- Calculate total marks and average automatically.
- Calculate grades and pass/fail status.
- Track student attendance.
- Analyze student performance using charts and graphs.
- Export student records as CSV files.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| SQLite | Database management |
| Pandas | Data analysis |
| HTML | Webpage structure |
| CSS | Website styling |
| JavaScript | Interactive functionality |
| Chart.js | Data visualization |
| VS Code | Development environment |
| Git & GitHub | Version control |

## 4. Main Features

- **Dashboard:** Displays total students, average performance, pass percentage, and other statistics.
- **Student Management:** Add, edit, delete, and view student details.
- **Marks Management:** Enter marks for six subjects.
- **Automatic Calculation:** Calculates total marks, average, and grades.
- **Performance Analysis:** Displays subject-wise and overall performance.
- **Attendance Tracking:** Records and monitors student attendance.
- **Charts and Analytics:** Visualizes grades, results, departments, and subject performance.
- **Search and Filters:** Find students using search and filtering options.
- **CSV Export:** Download student records for further analysis.

## 5. Project Structure

```text
Student-Performance-Analysis/
│
├── app.py
├── seed_demo.py
├── requirements.txt
├── README.md
├── .gitignore
├── setup_windows.bat
├── run_windows.bat
│
├── instance/
│   └── .gitkeep
│
├── templates/
│   └── index.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    └── js/
        └── script.js
```

## 6. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/advithanand07-crypyo/Student-Performance-Analysis.git
```

### Step 2: Open the Project Folder

```bash
cd Student-Performance-Analysis
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 5: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 6: Run the Application

```bash
python app.py
```

### Step 7: Open in Browser

Visit:

```text
http://127.0.0.1:5000
```

## 7. Database

The project uses SQLite for storing student information.

The database is automatically created when the application runs.

Database location:

```text
instance/student_performance.db
```

## 8. Demo Data (Optional)

To insert fictional sample student records, run:

```bash
python seed_demo.py
```

## 9. Future Enhancements

- Student login and authentication.
- Faculty and administrator dashboards.
- PDF report generation.
- Advanced academic reports.
- Semester-wise performance comparison.
- Improved data visualization.

## 10. Learning Outcomes

- Understanding Python web development.
- Working with Flask applications.
- Database operations using SQLite.
- Performing data analysis using Pandas.
- Creating interactive dashboards.
- Using Git and GitHub for project management.

## 11. Author

**Developed by Advith Anand.**

## 12. License

This project is intended for educational and learning purposes.
