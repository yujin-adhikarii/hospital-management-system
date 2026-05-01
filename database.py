import sqlite3
import hashlib
import pandas as pd
from datetime import date

DB = "hospital.db"


def connect():
    conn = sqlite3.connect(DB, check_same_thread=False) 
    conn.row_factory = sqlite3.Row #accessing column with name not index
    return conn



def hash_pw(pw):
    return hashlib.sha256(pw.strip().encode()).hexdigest()



def init_db():
    with connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS patients (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT    NOT NULL,
                email    TEXT    UNIQUE NOT NULL,
                age      INTEGER NOT NULL,
                password TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS doctors (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                name           TEXT    NOT NULL,
                email          TEXT    UNIQUE NOT NULL,
                specialization TEXT    NOT NULL,
                password       TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS records (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL REFERENCES patients(id),
                doctor_id  INTEGER NOT NULL REFERENCES doctors(id),
                disease    TEXT NOT NULL,
                medicine   TEXT NOT NULL,
                date       TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id     INTEGER NOT NULL REFERENCES patients(id),
                doctor_id      INTEGER NOT NULL REFERENCES doctors(id),
                requested_date TEXT NOT NULL,
                reason         TEXT NOT NULL,
                status         TEXT NOT NULL DEFAULT 'pending',
                created_date   TEXT NOT NULL
            );
        """)

        dp = hash_pw("doctor123")
        conn.executemany("""
            INSERT INTO doctors (name, email, specialization, password)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                name = excluded.name,
                specialization = excluded.specialization
        """, [
            ("Dr. Aaditya Sahi", "aaditya@hospital.com", "General Physician", dp),
            ("Dr. Khem Parsad",  "parsad@hospital.com",  "Cardiology",        dp),
            ("Dr. Priya Sharma", "priya@hospital.com",   "Neurology",         dp),
            ("Dr. Ram Acharaya", "ram@hospital.com",     "Surgeon",           dp),
        ])
        conn.commit()



def register_patient(name, email, age, password):
    try:
        with connect() as conn:
            conn.execute(
                "INSERT INTO patients (name, email, age, password) VALUES (?, ?, ?, ?)",
                (name.strip(), email.strip().lower(), age, hash_pw(password))
            )
            conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "This email is already registered."


def find_patient(email):
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM patients WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
    return dict(row) if row else None


def all_patients():
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, name, email, age FROM patients ORDER BY name"
        ).fetchall() #gets every single row and keep them in list
    if not rows:
        return pd.DataFrame(columns=["id", "name", "email", "age"])
    return pd.DataFrame([dict(r) for r in rows]) #organizing the data in tables



def find_doctor(email):
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM doctors WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
    return dict(row) if row else None


def all_doctors():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM doctors ORDER BY name").fetchall()
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(r) for r in rows])


def add_record(patient_id, doctor_id, disease, medicine):
    if not disease.strip() or not medicine.strip():
        return False, "Both fields are required."
    try:
        with connect() as conn:
            conn.execute(
                "INSERT INTO records (patient_id, doctor_id, disease, medicine, date) VALUES (?, ?, ?, ?, ?)",
                (patient_id, doctor_id, disease.strip(), medicine.strip(), str(date.today()))
            )
            conn.commit()
        return True, "Record saved!"
    except Exception as e:
        return False, str(e)


def remove_record(record_id):
    try:
        with connect() as conn:
            conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
            conn.commit()
        return True, "Deleted."
    except Exception as e:
        return False, str(e)


def patient_records(patient_id):
    with connect() as conn:
        rows = conn.execute("""
            SELECT r.id, r.disease, r.medicine, r.date,
                   d.name AS doctor_name, d.specialization
            FROM records r
            JOIN doctors d ON r.doctor_id = d.id
            WHERE r.patient_id = ?
            ORDER BY r.date DESC
        """, (patient_id,)).fetchall()
    return [dict(r) for r in rows]



def book_appointment(patient_id, doctor_id, req_date, reason):
    if not reason.strip():
        return False, "Please write a reason."
    try:
        with connect() as conn:
            conn.execute("""
                INSERT INTO appointments
                (patient_id, doctor_id, requested_date, reason, status, created_date)
                VALUES (?, ?, ?, ?, 'pending', ?)
            """, (patient_id, doctor_id, req_date, reason.strip(), str(date.today())))
            conn.commit()
        return True, "Appointment request sent!"
    except Exception as e:
        return False, str(e)


def patient_appointments(patient_id):
    with connect() as conn:
        rows = conn.execute("""
            SELECT a.id, a.requested_date, a.reason, a.status, a.created_date,
                   d.name AS doctor_name, d.specialization
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.patient_id = ?
            ORDER BY a.created_date DESC
        """, (patient_id,)).fetchall()
    return [dict(r) for r in rows]


def doctor_appointments(doctor_id):
    with connect() as conn:
        rows = conn.execute("""
            SELECT a.id, a.requested_date, a.reason, a.status, a.created_date,
                   p.name AS patient_name, p.email AS patient_email, p.age AS patient_age
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.doctor_id = ?
            ORDER BY a.status ASC, a.requested_date ASC
        """, (doctor_id,)).fetchall()
    return [dict(r) for r in rows]


def update_appt_status(appt_id, status):
    try:
        with connect() as conn:
            conn.execute(
                "UPDATE appointments SET status = ? WHERE id = ?", (status, appt_id)
            )
            conn.commit()
        return True
    except:
        return False



def get_counts():
    with connect() as conn:
        p = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        d = conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
        r = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        a = conn.execute("SELECT COUNT(*) FROM appointments WHERE status='pending'").fetchone()[0]
    return {"patients": p, "doctors": d, "records": r, "pending": a}