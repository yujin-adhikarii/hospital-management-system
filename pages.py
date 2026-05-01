import streamlit as st
import pandas as pd
from datetime import date

from database import (
    hash_pw, all_doctors, all_patients,
    register_patient, find_patient, find_doctor,
    add_record, remove_record, patient_records,
    book_appointment, patient_appointments,
    doctor_appointments, update_appt_status,
    get_counts
)



def get_role():
    return st.session_state.get("role")

def get_user():
    return st.session_state.get("user")

def logout():
    for key in ["role", "user", "page"]:
        st.session_state.pop(key, None)
    st.rerun()


def home():
    st.markdown("""
    <div class="page-header">
        <h2>Welcome to MediCare HMS</h2>
        <p>A hospital management system for patients and doctors.</p>
    </div>
    """, unsafe_allow_html=True)

    counts = get_counts()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="label">Registered Patients</div><div class="value">{counts["patients"]}</div><div class="sub">Active accounts</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="label">Medical Doctors</div><div class="value">{counts["doctors"]}</div><div class="sub">On staff</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="label">Medical Records</div><div class="value">{counts["records"]}</div><div class="sub">Total entries</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="section-card">
            <h4>For Patients</h4>
            <ul style="color:#444; line-height:2;">
                <li>Create your patient account</li>
                <li>Log in with email and password</li>
                <li>View your own medical records</li>
                <li>Book appointments with doctors</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="section-card">
            <h4>For Doctors</h4>
            <ul style="color:#444; line-height:2;">
                <li>Log in with hospital email</li>
                <li>View all registered patients</li>
                <li>Add or delete health records</li>
                <li>Confirm or decline appointments</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("Doctor Credentials"):
        docs = all_doctors()
        if not docs.empty:
            st.dataframe(docs[["name", "specialization"]], use_container_width=True, hide_index=True)
       


def register():
    st.markdown("""
    <div class="page-header">
        <h2>Patient Registration</h2>
        <p>Create your MediCare account to get started.</p>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.form("reg_form", clear_on_submit=True):
            st.markdown("#### Create an Account")
            name   = st.text_input("Full Name", placeholder="Sita Kc")
            email  = st.text_input("Email", placeholder="sita@example.com")
            age    = st.number_input("Age", min_value=1, max_value=120, value=20)
            pw     = st.text_input("Password", type="password", placeholder="At least 6 characters")
            pw2    = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
            submit = st.form_submit_button("Register", use_container_width=True)

            if submit:
                if not name.strip() or not email.strip() or not pw.strip():
                    st.error("All fields are required.")
                elif "@" not in email or "." not in email:
                    st.error("Enter a valid email address.")
                elif len(pw) < 6:
                    st.error("Password must be at least 6 characters.")
                elif pw != pw2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_patient(name, email, int(age), pw)
                    if ok:
                        st.success(msg + " You can now log in.")
                    else:
                        st.error(msg)


def patient_login():
    st.markdown("""
    <div class="page-header">
        <h2>Patient Login</h2>
        <p>Sign in to access your records and appointments.</p>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.form("pat_login"):
            st.markdown("#### Sign In")
            email  = st.text_input("Email", placeholder="alric@example.com")
            pw     = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", use_container_width=True)

            if submit:
                if not email.strip() or not pw.strip():
                    st.error("Please fill in all fields.")
                else:
                    p = find_patient(email)
                    if p and p["password"] == hash_pw(pw):
                        st.session_state["role"] = "patient"
                        st.session_state["user"] = p
                        st.success("Welcome back, " + p["name"] + "!")
                        st.rerun()
                    else:
                        st.error("Wrong email or password.")


def doctor_login():
    st.markdown("""
    <div class="page-header">
        <h2>Doctor Login</h2>
        <p>Secure access for medical staff.</p>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.form("doc_login"):
            st.markdown("#### Doctor Sign In")
            email  = st.text_input("Hospital Email", placeholder="doctor@hospital.com")
            pw     = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", use_container_width=True)

            if submit:
                if not email.strip() or not pw.strip():
                    st.error("Please fill in all fields.")
                else:
                    d = find_doctor(email)
                    if d and d["password"] == hash_pw(pw):
                        st.session_state["role"] = "doctor"
                        st.session_state["user"] = d
                        st.success("Welcome, " + d["name"] + "!")
                        st.rerun()
                    else:
                        st.error("Wrong email or password.")




def patient_dashboard():
    u = get_user()
    st.markdown(f"""
    <div class="page-header">
        <h2>Hello, {u['name']}</h2>
        <p>Here is your health overview.</p>
    </div>
    """, unsafe_allow_html=True)

    recs          = patient_records(u["id"])
    appts         = patient_appointments(u["id"])
    pending_count = len([a for a in appts if a["status"] == "pending"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="label">Patient ID</div><div class="value">#{u["id"]:04d}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="label">Age</div><div class="value">{u["age"]}</div><div class="sub">years</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="label">Medical Records</div><div class="value">{len(recs)}</div><div class="sub">Total visits</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card"><div class="label">Pending Appointments</div><div class="value">{pending_count}</div><div class="sub">Awaiting reply</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    if recs:
        st.markdown("#### Recent Records")
        for r in recs[:3]:
            st.markdown(f"""
            <div class="record-pill">
                <div class="rp-date">{r['date']}</div>
                <div class="rp-disease">{r['disease']}</div>
                <div class="rp-med">Medicine: {r['medicine']}</div>
                <div class="rp-doctor">{r['doctor_name']} - {r['specialization']}</div>
            </div>""", unsafe_allow_html=True)
        if len(recs) > 3:
            st.caption("Showing 3 of " + str(len(recs)) + ". Go to My Records to see all.")
    else:
        st.info("No records yet. Your doctor will add them after a visit.")


def my_records():
    u = get_user()
    st.markdown(f"""
    <div class="page-header">
        <h2>My Medical Records</h2>
        <p>All records for {u['name']}.</p>
    </div>
    """, unsafe_allow_html=True)

    recs = patient_records(u["id"])

    if not recs:
        st.info("No records found yet.")
        return

    # show as a table first
    df = pd.DataFrame(recs)
    df.rename(columns={
        "id": "Record No", "disease": "Diagnosis", "medicine": "Prescription",
        "date": "Date", "doctor_name": "Doctor", "specialization": "Specialty"
    }, inplace=True)
    df = df[["Record No", "Date", "Diagnosis", "Prescription", "Doctor", "Specialty"]]
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### Detailed View")

    # expandable detail for each record
    for r in recs:
        with st.expander(r['date'] + "  -  " + r['disease']):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Diagnosis**")
                st.write(r["disease"])
                st.markdown("**Prescription**")
                st.write(r["medicine"])
            with col2:
                st.markdown("**Doctor**")
                st.write(r["doctor_name"])
                st.markdown("**Specialization**")
                st.write(r["specialization"])


def book_appt():
    u = get_user()
    st.markdown("""
    <div class="page-header">
        <h2>Book an Appointment</h2>
        <p>Send a request to one of our doctors.</p>
    </div>
    """, unsafe_allow_html=True)

    docs = all_doctors()
    if docs.empty:
        st.warning("No doctors available right now.")
        return

    options = {row['name'] + " (" + row['specialization'] + ")": row["id"] for _, row in docs.iterrows()}

    with st.form("appt_form"):
        st.markdown("#### Appointment Details")
        selected  = st.selectbox("Choose a Doctor", list(options.keys()))
        doc_id    = options[selected]
        appt_date = st.date_input("Preferred Date", min_value=date.today())
        reason    = st.text_area("Reason for Visit", placeholder="e.g. Chest pain, routine checkup...", height=100)
        submit    = st.form_submit_button("Send Request", use_container_width=True)

        if submit:
            if not reason.strip():
                st.error("Please describe your reason for visiting.")
            else:
                ok, msg = book_appointment(u["id"], int(doc_id), str(appt_date), reason)
                if ok:
                    st.success(msg + " The doctor will respond soon.")
                else:
                    st.error(msg)


def my_appointments():
    u = get_user()
    st.markdown("""
    <div class="page-header">
        <h2>My Appointments</h2>
        <p>Check the status of your appointment requests.</p>
    </div>
    """, unsafe_allow_html=True)

    appts = patient_appointments(u["id"])

    if not appts:
        st.info("No appointments yet. Go to Book Appointment to send a request.")
        return

    p_count = sum(1 for a in appts if a["status"] == "pending")
    c_count = sum(1 for a in appts if a["status"] == "confirmed")
    d_count = sum(1 for a in appts if a["status"] == "declined")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="label">Pending</div><div class="value">{p_count}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="label">Confirmed</div><div class="value">{c_count}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="label">Declined</div><div class="value">{d_count}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    f = st.radio("Show", ["All", "Pending", "Confirmed", "Declined"], horizontal=True, label_visibility="collapsed")
    filtered = appts if f == "All" else [a for a in appts if a["status"] == f.lower()]

    for a in filtered:
        st.markdown(f"""
        <div class="appt-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                <b style="color:#1a3a4a;">{a['requested_date']}</b>
                <span class="badge-{a['status']}">{a['status'].capitalize()}</span>
            </div>
            <div style="color:#333; font-size:0.93rem;">Dr. {a['doctor_name']} - {a['specialization']}</div>
            <div style="color:#555; font-size:0.88rem; margin-top:0.3rem;">Reason: {a['reason']}</div>
            <div style="color:#aaa; font-size:0.78rem; margin-top:0.4rem;">Requested on {a['created_date']}</div>
        </div>
        """, unsafe_allow_html=True)



def doctor_dashboard():
    u = get_user()
    st.markdown(f"""
    <div class="page-header">
        <h2>Doctor Dashboard</h2>
        <p>{u['name']} - {u['specialization']}</p>
    </div>
    """, unsafe_allow_html=True)

    counts = get_counts()
    pats   = all_patients()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="label">Total Patients</div><div class="value">{counts["patients"]}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="label">Total Records</div><div class="value">{counts["records"]}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="label">Medical Staff</div><div class="value">{counts["doctors"]}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card"><div class="label">Pending Appointments</div><div class="value">{counts["pending"]}</div><div class="sub">Need action</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### All Patients")

    if pats.empty:
        st.info("No patients registered yet.")
    else:
        df = pats.copy()
        df.columns = ["ID", "Name", "Email", "Age"]
        st.dataframe(df, use_container_width=True, hide_index=True)


def view_patient_records():
    st.markdown("""
    <div class="page-header">
        <h2>Patient Records</h2>
        <p>Select a patient to see their full history.</p>
    </div>
    """, unsafe_allow_html=True)

    pats = all_patients()
    if pats.empty:
        st.info("No patients yet.")
        return

    # dropdown to select a patient
    options = {row['name'] + " (ID #" + str(row['id']) + ")": row["id"] for _, row in pats.iterrows()}
    selected = st.selectbox("Select Patient", list(options.keys()))
    pid = options[selected]

    # show patient info strip
    pat = pats[pats["id"] == pid].iloc[0]
    st.markdown(f"""
    <div style="background:#f0f8ff; border:1px solid #cce4f7; border-radius:10px; padding:0.9rem 1.2rem; margin:0.8rem 0 1.5rem;">
        <b>{pat['name']}</b> &nbsp;|&nbsp; Age: {pat['age']} &nbsp;|&nbsp; Email: {pat['email']}
    </div>
    """, unsafe_allow_html=True)

    recs = patient_records(int(pid))

    if not recs:
        st.info("No records for this patient yet.")
        return

    st.markdown("#### Records (" + str(len(recs)) + ") - Click Delete to remove a wrong entry")
    for r in recs:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div class="record-pill" style="margin-bottom:0.4rem;">
                <div class="rp-date">{r['date']} - {r['doctor_name']} ({r['specialization']})</div>
                <div class="rp-disease">{r['disease']}</div>
                <div class="rp-med">Medicine: {r['medicine']}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)
            if st.button("Delete", key="del_" + str(r['id'])):
                ok, _ = remove_record(r["id"])
                if ok:
                    st.success("Record removed.")
                    st.rerun()


def add_new_record():
    u = get_user()
    st.markdown("""
    <div class="page-header">
        <h2>Add Medical Record</h2>
        <p>Add a diagnosis and prescription for a patient.</p>
    </div>
    """, unsafe_allow_html=True)

    pats = all_patients()
    if pats.empty:
        st.warning("No patients registered yet.")
        return

    options = {row['name'] + " (ID #" + str(row['id']) + ")": row["id"] for _, row in pats.iterrows()}

    with st.form("add_rec_form"):
        st.markdown("#### Record Details")
        selected = st.selectbox("Select Patient", list(options.keys()))
        pid      = options[selected]
        disease  = st.text_area("Diagnosis", placeholder="e.g. Acute bronchitis with mild fever", height=100)
        medicine = st.text_area("Prescription", placeholder="e.g. Amoxicillin 500mg twice daily for 7 days", height=100)
        st.caption("This record will be saved under " + u['name'] + " on " + str(date.today()) + ".")
        submit = st.form_submit_button("Save Record", use_container_width=True)

        if submit:
            if not disease.strip() or not medicine.strip():
                st.error("Both fields are required.")
            else:
                ok, msg = add_record(int(pid), u["id"], disease, medicine)
                if ok:
                    st.success(msg)
                    pname = next(k for k, v in options.items() if v == pid)
                    st.markdown(f"""
                    <div class="record-pill" style="margin-top:1rem;">
                        <div class="rp-date">{date.today()} - just added</div>
                        <div class="rp-disease">{disease}</div>
                        <div class="rp-med">Medicine: {medicine}</div>
                        <div class="rp-doctor">Patient: {pname.split('(')[0].strip()}</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.error(msg)


def manage_appointments():
    u = get_user()
    st.markdown("""
    <div class="page-header">
        <h2>Appointments</h2>
        <p>Review and respond to patient requests.</p>
    </div>
    """, unsafe_allow_html=True)

    appts = doctor_appointments(u["id"])

    if not appts:
        st.info("No appointment requests yet.")
        return

    pending   = [a for a in appts if a["status"] == "pending"]
    confirmed = [a for a in appts if a["status"] == "confirmed"]
    declined  = [a for a in appts if a["status"] == "declined"]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="label">Pending</div><div class="value">{len(pending)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="label">Confirmed</div><div class="value">{len(confirmed)}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="label">Declined</div><div class="value">{len(declined)}</div></div>', unsafe_allow_html=True)

    # pending ones need a response from the doctor
    if pending:
        st.markdown("---")
        st.markdown("#### Pending - Needs Your Response")
        for a in pending:
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"""
                <div class="appt-card">
                    <div style="display:flex; justify-content:space-between;">
                        <b style="color:#1a3a4a;">{a['requested_date']}</b>
                        <span class="badge-pending">Pending</span>
                    </div>
                    <div style="color:#333; font-size:0.93rem; margin-top:0.3rem;">
                        {a['patient_name']} - Age {a['patient_age']} - {a['patient_email']}
                    </div>
                    <div style="color:#555; font-size:0.88rem; margin-top:0.3rem;">Reason: {a['reason']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
                if st.button("Confirm", key="c_" + str(a['id'])):
                    update_appt_status(a["id"], "confirmed")
                    st.success("Confirmed.")
                    st.rerun()
            with col3:
                st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
                if st.button("Decline", key="d_" + str(a['id'])):
                    update_appt_status(a["id"], "declined")
                    st.warning("Declined.")
                    st.rerun()

    if confirmed or declined:
        st.markdown("---")
        st.markdown("#### Past Appointments")
        for a in confirmed + declined:
            st.markdown(f"""
            <div class="appt-card">
                <div style="display:flex; justify-content:space-between;">
                    <b style="color:#1a3a4a;">{a['requested_date']}</b>
                    <span class="badge-{a['status']}">{a['status'].capitalize()}</span>
                </div>
                <div style="color:#333; font-size:0.93rem; margin-top:0.3rem;">
                    {a['patient_name']} - Age {a['patient_age']}
                </div>
                <div style="color:#555; font-size:0.88rem; margin-top:0.3rem;">Reason: {a['reason']}</div>
            </div>
            """, unsafe_allow_html=True)