# Student Performance Analysis Dashboard

A beginner-friendly academic analytics website built with **Python, Flask, Pandas, SQLite, HTML, CSS, JavaScript and Chart.js**. The responsive interface combines a sidebar, KPI cards, filters, student records and analytical charts inspired by the supplied dashboard screenshots.

## Features

- Student create, read, update and delete (CRUD) operations.
- Student name, USN, department, semester, academic year and attendance.
- Six configurable subject-mark fields (0–100).
- Automatic individual average, grade and pass/fail calculation.
- Dashboard KPIs: total students, class average, pass percentage and average attendance.
- Subject-wise averages, grade distribution, pass/fail, department comparison and semester charts.
- Department and semester dashboard filters.
- Search by student name, USN or department.
- Export the currently filtered student list to CSV.
- SQLite database is created automatically in `instance/student_performance.db`.
- Optional fictional sample records for testing and screenshots.

## 1. Install the software

1. Install [Python 3](https://www.python.org/downloads/). During Windows installation, tick **Add Python to PATH**.
2. Install [Visual Studio Code](https://code.visualstudio.com/Download).
3. Install a browser such as Google Chrome or Microsoft Edge.

### Recommended VS Code extensions

- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **Python Debugger** (Microsoft)
- **Prettier - Code formatter** (optional)

HTML, CSS and JavaScript support is already built into VS Code. Extensions are helpful but are not required to run the project.

## 2. Open the project in VS Code

1. Extract the ZIP file.
2. In VS Code, choose **File → Open Folder**.
3. Select the extracted `Student-Performance-Analysis` folder.
4. Choose **Terminal → New Terminal**.

## 3. Create and activate a virtual environment

In the VS Code terminal (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, either use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Or keep using PowerShell without activating and call the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. Install the Python libraries

With the virtual environment activated:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

This installs Flask and Pandas. SQLite is included with Python. Chart.js is loaded by the webpage from its CDN, so it is not a Python package.

## 5. Run the website

```powershell
python app.py
```

Open this address in your browser:

**http://127.0.0.1:5000**

Keep the terminal open while using the website. Press `Ctrl + C` in the terminal to stop the Flask server.

The SQLite database is created automatically the first time the application starts.

## 6. Add optional demo data

To populate the dashboard with 15 fictional records for practice, stop the Flask server and run:

```powershell
python seed_demo.py
```

Then start the application again:

```powershell
python app.py
```

The sample students are fictional. The seed script will not add duplicate data if the database already contains records. To start fresh, stop Flask and delete `instance/student_performance.db`; the app will create a new empty database on the next start.

## 7. Change the six subject names

Open `app.py` and find the `SUBJECTS` list near the top:

```python
SUBJECTS = [
    "Subject 1",
    "Subject 2",
    "Subject 3",
    "Subject 4",
    "Subject 5",
    "Subject 6",
]
```

Replace the labels with the six subject names from your semester. Keep exactly six subject names. The database column names (`subject_1` through `subject_6`) do not need to change. Restart Flask after editing.

## 8. Change the pass mark

The example project uses `PASS_MARK = 35.0`. A student is marked **Pass** only when every subject mark is at least this value. Change this constant in `app.py` to match the grading rules approved by your college. Confirm the applicable VTU rules with your department before using it for official results.

The grade bands are also illustrative and are in the `grade_for_average()` function in `app.py`.

## Project folder structure

```text
Student-Performance-Analysis/
│
├── app.py
├── seed_demo.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── instance/
│   └── student_performance.db   # Created automatically
│
├── templates/
│   └── index.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

## How the technologies work together

1. **HTML** builds the dashboard layout and student form.
2. **CSS** styles the responsive dashboard and tables.
3. **JavaScript** submits forms, filters the table and draws charts with Chart.js.
4. **Flask** provides the website and JSON API endpoints.
5. **SQLite** stores student information on the local computer.
6. **Pandas** calculates class averages, subject averages, grade counts and department/semester analytics.

## Troubleshooting

### `python` is not recognized
Reinstall Python and tick **Add Python to PATH**, or try `py app.py`.

### `No module named flask` or `No module named pandas`
Activate `.venv` and run `python -m pip install -r requirements.txt` again. Make sure VS Code is using the `.venv` interpreter.

### PowerShell says scripts are disabled
Use the Command Prompt activation command shown above, or run `.venv\Scripts\python.exe app.py` and `.venv\Scripts\python.exe -m pip install -r requirements.txt` without activation.

### Charts do not appear
Chart.js is loaded from a CDN, so check your internet connection and refresh the page. The rest of the local Flask website can run without the Google Fonts connection.

### Port 5000 is already in use
Stop the other Flask process, or change `app.run(debug=True)` at the bottom of `app.py` to `app.run(debug=True, port=5001)` and open `http://127.0.0.1:5001`.

## Important project notes

- This is a local academic project starter, not a production student-information system.
- No login or role-based access control is included in this dashboard-and-analytics scope.
- Do not enter real student personal information into a public or shared deployment without appropriate security, authorization and privacy safeguards.
- The example pass rule and grade boundaries must be checked against your institution's official assessment policy.
