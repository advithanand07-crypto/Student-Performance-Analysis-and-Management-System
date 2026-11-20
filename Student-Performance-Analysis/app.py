"""Student Performance Analysis and Analytics Dashboard.

A beginner-friendly Flask + SQLite + Pandas project.
"""

from __future__ import annotations

import math
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import pandas as pd
from flask import Flask, jsonify, make_response, render_template, request


BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE = INSTANCE_DIR / "student_performance.db"

# Edit these labels to match the six subjects in your semester.
SUBJECTS = [
    "Subject 1",
    "Subject 2",
    "Subject 3",
    "Subject 4",
    "Subject 5",
    "Subject 6",
]
SUBJECT_COLUMNS = [f"subject_{i}" for i in range(1, 7)]
PASS_MARK = 35.0  # Example rule: a student must score at least 35 in every subject.

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection and always close it after the operation."""
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    """Create the student table when the application is first started."""
    subject_fields = ",\n".join(
        f"{column} REAL NOT NULL DEFAULT 0 CHECK ({column} >= 0 AND {column} <= 100)"
        for column in SUBJECT_COLUMNS
    )
    with get_connection() as connection:
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                usn TEXT NOT NULL COLLATE NOCASE UNIQUE,
                department TEXT NOT NULL DEFAULT 'General',
                semester INTEGER NOT NULL DEFAULT 1 CHECK (semester BETWEEN 1 AND 8),
                academic_year TEXT NOT NULL DEFAULT '2026-27',
                attendance REAL NOT NULL DEFAULT 0 CHECK (attendance >= 0 AND attendance <= 100),
                {subject_fields},
                average REAL NOT NULL DEFAULT 0,
                result TEXT NOT NULL DEFAULT 'Pass',
                grade TEXT NOT NULL DEFAULT 'E',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_students_department ON students(department)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_students_semester ON students(semester)"
        )


def grade_for_average(average: float) -> str:
    """Return a simple illustrative grade based on the average score."""
    if average >= 90:
        return "A+"
    if average >= 80:
        return "A"
    if average >= 70:
        return "B"
    if average >= 60:
        return "C"
    if average >= 50:
        return "D"
    if average >= PASS_MARK:
        return "E"
    return "F"


def filtered_rows(department: str = "", semester: str = "") -> list[dict[str, Any]]:
    """Read students from SQLite and apply optional dashboard filters."""
    sql = "SELECT * FROM students WHERE 1 = 1"
    values: list[Any] = []
    if department:
        sql += " AND department = ?"
        values.append(department)
    if semester:
        sql += " AND semester = ?"
        values.append(int(semester))
    sql += " ORDER BY average DESC, name COLLATE NOCASE ASC"
    with get_connection() as connection:
        rows = connection.execute(sql, values).fetchall()
    return [dict(row) for row in rows]


def student_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize form/API data before saving it."""
    name = str(payload.get("name", "")).strip()
    usn = str(payload.get("usn", "")).strip().upper()
    department = str(payload.get("department", "General")).strip() or "General"
    academic_year = str(payload.get("academic_year", "2026-27")).strip() or "2026-27"

    if not name:
        raise ValueError("Please enter the student's name.")
    if not usn:
        raise ValueError("Please enter the student's USN.")
    if len(name) > 80 or len(usn) > 30 or len(department) > 60:
        raise ValueError("Name, USN, or department is too long.")

    try:
        semester = int(payload.get("semester", 1))
        attendance = float(payload.get("attendance", 0))
        marks = [float(payload.get(column, 0)) for column in SUBJECT_COLUMNS]
    except (TypeError, ValueError):
        raise ValueError("Semester, attendance and all six marks must be valid numbers.")

    if not 1 <= semester <= 8:
        raise ValueError("Semester must be between 1 and 8.")
    if not math.isfinite(attendance) or not 0 <= attendance <= 100:
        raise ValueError("Attendance must be between 0 and 100.")
    if any(not math.isfinite(mark) or mark < 0 or mark > 100 for mark in marks):
        raise ValueError("Each subject mark must be between 0 and 100.")

    average = round(sum(marks) / len(marks), 2)
    result = "Pass" if all(mark >= PASS_MARK for mark in marks) else "Fail"
    return {
        "name": name,
        "usn": usn,
        "department": department,
        "semester": semester,
        "academic_year": academic_year,
        "attendance": round(attendance, 2),
        **dict(zip(SUBJECT_COLUMNS, marks)),
        "average": average,
        "result": result,
        "grade": grade_for_average(average),
    }


def dashboard_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Use Pandas to calculate dashboard KPIs and chart data."""
    if not rows:
        return {
            "total_students": 0,
            "average_score": 0,
            "pass_rate": 0,
            "average_attendance": 0,
            "top_student": "—",
            "top_average": 0,
            "subject_labels": SUBJECTS,
            "subject_averages": [0] * len(SUBJECTS),
            "grade_labels": ["A+", "A", "B", "C", "D", "E", "F"],
            "grade_values": [0] * 7,
            "result_labels": ["Pass", "Fail"],
            "result_values": [0, 0],
            "department_labels": [],
            "department_averages": [],
            "semester_labels": [],
            "semester_averages": [],
        }

    frame = pd.DataFrame(rows)
    total = int(len(frame))
    passed = int((frame["result"] == "Pass").sum())
    subject_averages = [round(float(frame[column].mean()), 2) for column in SUBJECT_COLUMNS]

    department_frame = (
        frame.groupby("department", dropna=False)["average"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
    )
    semester_frame = (
        frame.groupby("semester")["average"].mean().round(2).sort_index()
    )
    grade_order = ["A+", "A", "B", "C", "D", "E", "F"]
    grade_counts = frame["grade"].value_counts()

    top_row = frame.sort_values(["average", "name"], ascending=[False, True]).iloc[0]
    return {
        "total_students": total,
        "average_score": round(float(frame["average"].mean()), 2),
        "pass_rate": round((passed / total) * 100, 2),
        "average_attendance": round(float(frame["attendance"].mean()), 2),
        "top_student": str(top_row["name"]),
        "top_average": round(float(top_row["average"]), 2),
        "subject_labels": SUBJECTS,
        "subject_averages": subject_averages,
        "grade_labels": grade_order,
        "grade_values": [int(grade_counts.get(grade, 0)) for grade in grade_order],
        "result_labels": ["Pass", "Fail"],
        "result_values": [passed, total - passed],
        "department_labels": [str(value) for value in department_frame.index.tolist()],
        "department_averages": [float(value) for value in department_frame.tolist()],
        "semester_labels": [f"Sem {int(value)}" for value in semester_frame.index.tolist()],
        "semester_averages": [float(value) for value in semester_frame.tolist()],
    }


@app.route("/")
def index():
    return render_template(
        "index.html",
        subjects=SUBJECTS,
        subject_columns=SUBJECT_COLUMNS,
        pass_mark=PASS_MARK,
    )


@app.get("/api/dashboard")
def api_dashboard():
    department = request.args.get("department", "").strip()
    semester = request.args.get("semester", "").strip()
    try:
        rows = filtered_rows(department, semester)
    except ValueError:
        return jsonify({"error": "Invalid semester filter."}), 400
    return jsonify(dashboard_summary(rows))


@app.get("/api/students")
def api_students():
    department = request.args.get("department", "").strip()
    semester = request.args.get("semester", "").strip()
    search = request.args.get("search", "").strip().lower()
    try:
        rows = filtered_rows(department, semester)
    except ValueError:
        return jsonify({"error": "Invalid semester filter."}), 400

    if search:
        rows = [
            row for row in rows
            if search in row["name"].lower()
            or search in row["usn"].lower()
            or search in row["department"].lower()
        ]
    return jsonify([
        {
            **row,
            "subjects": [row[column] for column in SUBJECT_COLUMNS],
        }
        for row in rows
    ])


@app.get("/api/filters")
def api_filters():
    with get_connection() as connection:
        departments = [
            row[0] for row in connection.execute(
                "SELECT DISTINCT department FROM students ORDER BY department COLLATE NOCASE"
            ).fetchall()
        ]
        semesters = [
            row[0] for row in connection.execute(
                "SELECT DISTINCT semester FROM students ORDER BY semester"
            ).fetchall()
        ]
    return jsonify({"departments": departments, "semesters": semesters})


@app.post("/api/students")
def api_add_student():
    payload = request.get_json(silent=True) or {}
    try:
        student = student_from_payload(payload)
        columns = [
            "name", "usn", "department", "semester", "academic_year", "attendance",
            *SUBJECT_COLUMNS, "average", "result", "grade",
        ]
        placeholders = ", ".join("?" for _ in columns)
        values = [student[column] for column in columns]
        with get_connection() as connection:
            cursor = connection.execute(
                f"INSERT INTO students ({', '.join(columns)}) VALUES ({placeholders})",
                values,
            )
            student_id = cursor.lastrowid
        return jsonify({"message": "Student added successfully.", "id": student_id}), 201
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except sqlite3.IntegrityError:
        return jsonify({"error": "This USN already exists. Enter a unique USN."}), 409


@app.put("/api/students/<int:student_id>")
def api_update_student(student_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        student = student_from_payload(payload)
        columns = [
            "name", "usn", "department", "semester", "academic_year", "attendance",
            *SUBJECT_COLUMNS, "average", "result", "grade",
        ]
        assignments = ", ".join(f"{column} = ?" for column in columns)
        values = [student[column] for column in columns]
        with get_connection() as connection:
            cursor = connection.execute(
                f"UPDATE students SET {assignments}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                [*values, student_id],
            )
            if cursor.rowcount == 0:
                return jsonify({"error": "Student record not found."}), 404
        return jsonify({"message": "Student updated successfully."})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except sqlite3.IntegrityError:
        return jsonify({"error": "This USN is already used by another student."}), 409


@app.delete("/api/students/<int:student_id>")
def api_delete_student(student_id: int):
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM students WHERE id = ?", (student_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Student record not found."}), 404
    return jsonify({"message": "Student deleted successfully."})


@app.get("/export/csv")
def export_csv():
    rows = filtered_rows(
        request.args.get("department", "").strip(),
        request.args.get("semester", "").strip(),
    )
    columns = [
        "id", "name", "usn", "department", "semester", "academic_year", "attendance",
        *SUBJECT_COLUMNS, "average", "grade", "result",
    ]
    frame = pd.DataFrame(rows, columns=columns)
    frame = frame.rename(columns={
        "id": "ID", "name": "Name", "usn": "USN", "department": "Department",
        "semester": "Semester", "academic_year": "Academic Year", "attendance": "Attendance",
        "average": "Average", "grade": "Grade", "result": "Result",
        **dict(zip(SUBJECT_COLUMNS, SUBJECTS)),
    })
    csv_data = frame.to_csv(index=False)
    response = make_response("\ufeff" + csv_data)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = "attachment; filename=student_performance.csv"
    return response


init_db()

if __name__ == "__main__":
    app.run(debug=True)
