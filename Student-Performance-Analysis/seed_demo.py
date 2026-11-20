"""Insert fictional demo records so the dashboard has data for practice.

Run once with: python seed_demo.py
These names and marks are made-up sample data, not real student records.
"""

import random

from app import SUBJECT_COLUMNS, get_connection, student_from_payload

DEMO_STUDENTS = [
    ("Aarav Sharma", "DEMO001", "CSBS", 5),
    ("Ananya Rao", "DEMO002", "AIML", 5),
    ("Rohan Kumar", "DEMO003", "CSE", 5),
    ("Diya Shetty", "DEMO004", "AIDS", 5),
    ("Kiran Nair", "DEMO005", "ECE", 5),
    ("Meera Pai", "DEMO006", "CSBS", 6),
    ("Rahul Das", "DEMO007", "AIML", 6),
    ("Ishita Rao", "DEMO008", "CSE", 6),
    ("Vikram Hegde", "DEMO009", "AIDS", 4),
    ("Nisha Bhat", "DEMO010", "ECE", 4),
    ("Aditya Shetty", "DEMO011", "CSBS", 4),
    ("Sana Khan", "DEMO012", "AIML", 7),
    ("Arjun Menon", "DEMO013", "CSE", 7),
    ("Tara Rao", "DEMO014", "AIDS", 7),
    ("Dev Patil", "DEMO015", "ECE", 3),
]


def main() -> None:
    rng = random.Random(2026)
    with get_connection() as connection:
        existing = connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if existing:
            print(f"Database already contains {existing} student record(s). No demo data was added.")
            print("To reset the demo, stop Flask and delete instance/student_performance.db, then run this script again.")
            return

        for name, usn, department, semester in DEMO_STUDENTS:
            marks = [rng.randint(42, 98) for _ in SUBJECT_COLUMNS]
            if usn in {"DEMO007", "DEMO009", "DEMO015"}:
                marks[2] = rng.randint(18, 33)  # Include a few illustrative fail results.
            payload = {
                "name": name,
                "usn": usn,
                "department": department,
                "semester": semester,
                "academic_year": "2026-27",
                "attendance": round(rng.uniform(68, 99), 1),
                **dict(zip(SUBJECT_COLUMNS, marks)),
            }
            student = student_from_payload(payload)
            columns = [
                "name", "usn", "department", "semester", "academic_year", "attendance",
                *SUBJECT_COLUMNS, "average", "result", "grade",
            ]
            placeholders = ", ".join("?" for _ in columns)
            connection.execute(
                f"INSERT INTO students ({', '.join(columns)}) VALUES ({placeholders})",
                [student[column] for column in columns],
            )

    print(f"Added {len(DEMO_STUDENTS)} fictional demo students.")
    print("Start the website with: python app.py")


if __name__ == "__main__":
    main()
