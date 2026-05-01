# 🏥 MediCare – Hospital Management System

## Overview
MediCare is a simple Hospital Management System (HMS) built using Python, Streamlit, and SQLite. It digitizes hospital processes by managing patient data, doctor information, and medical records in an organized and accessible way.

The system supports two types of users:
- Patients
- Doctors

---

##  Features

###  Patient
- Register and login
- View personal profile
- Access medical records
- Book a appointment

###  Doctor
- Secure login
- View all patients
- Add diagnosis and prescriptions
- Can schedule appointment

###  Dashboard
- Displays total patients, doctors, and records
- Easy-to-use interface

---

##  Tech Stack
- **Python**
- **Streamlit** (Frontend UI)
- **SQLite** (Database)
- **Pandas** (Data display)

---

##  System Design
The system follows a simple architecture:
- **Frontend:** Streamlit interface (forms, dashboards)
- **Backend Logic:** Python functions
- **Database:** SQLite with 3 tables:
  - Patients
  - Doctors
  - Records

Relationships:
- One patient → multiple records  
- One doctor → multiple records  

---

##  Programming Concepts Used
- **Encapsulation:** Database access through functions  
- **Abstraction:** Simplified user interaction  
- **Modular Design:** Code divided into multiple functions  

---

##  Limitations
- No password authentication (low security)
- Doctors are hardcoded (not dynamic)
- No appointment or billing system

---

## Future Improvements
- Add authentication system
- Doctor registration feature
- Appointment scheduling
- Billing system
- Admin dashboard
- Deploy the system online

---

## ▶ How to Run

1. Clone the repository:
```bash
git clone https://github.com/yujin-adhikarii/hospital-management-system.git