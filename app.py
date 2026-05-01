import streamlit as st
from database import init_db
from pages import (
    get_role, get_user, logout,
    home, register, patient_login, doctor_login,
    patient_dashboard, my_records, book_appt, my_appointments,
    doctor_dashboard, view_patient_records, add_new_record, manage_appointments
)

st.set_page_config(page_title="MediCare HMS", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* sidebar dark gradient background */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f2027 0%, #1a3a4a 60%, #203a43 100%);
    }
    [data-testid="stSidebar"] * { color: #e0f0ff !important; }

    .sidebar-brand {
        text-align: center;
        padding: 1.5rem 1rem 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 1.5rem;
    }
    .sidebar-brand h1 {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin: 0 !important;
    }
    .sidebar-brand p {
        font-size: 0.75rem !important;
        color: #7ecfff !important;
        margin: 0.25rem 0 0 !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    /* dark banner at the top of each page */
    .page-header {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        border-radius: 12px;
        padding: 1.8rem 2rem;
        margin-bottom: 2rem;
        color: white;
    }
    .page-header h2 { margin: 0 0 0.3rem 0; font-size: 1.8rem; font-weight: 700; }
    .page-header p  { margin: 0; opacity: 0.75; font-size: 0.95rem; }

    /* stat boxes on dashboards */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        border-left: 4px solid #2c5364;
        margin-bottom: 1rem;
    }
    .stat-card .label { font-size: 0.78rem; color: #888; text-transform: uppercase; letter-spacing: 0.07em; font-weight: 600; margin-bottom: 0.3rem; }
    .stat-card .value { font-size: 2rem; font-weight: 800; color: #1a3a4a; }
    .stat-card .sub   { font-size: 0.82rem; color: #aaa; margin-top: 0.2rem; }

    .section-card {
        background: white;
        border-radius: 12px;
        padding: 1.6rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        margin-bottom: 1.5rem;
    }
    .section-card h4 {
        margin: 0 0 1rem 0;
        color: #1a3a4a;
        font-size: 1.05rem;
        font-weight: 700;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid #e8f4fd;
    }

    /* individual record cards */
    .record-pill {
        background: #f0f8ff;
        border: 1px solid #cce4f7;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .record-pill .rp-date    { font-size: 0.78rem; color: #2c7bb6; font-weight: 600; margin-bottom: 0.4rem; }
    .record-pill .rp-disease { font-weight: 700; color: #1a3a4a; font-size: 1rem; }
    .record-pill .rp-med     { color: #555; font-size: 0.88rem; margin-top: 0.2rem; }
    .record-pill .rp-doctor  { font-size: 0.78rem; color: #888; margin-top: 0.3rem; }

    /* appointment cards */
    .appt-card {
        background: #fff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    }

    /* status color badges for appointments */
    .badge-pending   { display:inline-block; background:#fff8e1; color:#f57c00; border-radius:20px; padding:0.15rem 0.7rem; font-size:0.78rem; font-weight:700; }
    .badge-confirmed { display:inline-block; background:#e8f5e9; color:#2e7d32; border-radius:20px; padding:0.15rem 0.7rem; font-size:0.78rem; font-weight:700; }
    .badge-declined  { display:inline-block; background:#ffebee; color:#c62828; border-radius:20px; padding:0.15rem 0.7rem; font-size:0.78rem; font-weight:700; }

    /* form and button styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div { border-radius: 8px !important; }
    .stButton > button { border-radius: 8px !important; font-weight: 600 !important; padding: 0.5rem 1.4rem !important; }
    div[data-testid="stForm"] {
        background: #f8fbff;
        border: 1px solid #ddeeff;
        border-radius: 12px;
        padding: 1.4rem;
    }

    /* sidebar navigation items */
    [data-testid="stSidebar"] .stRadio > div { gap: 0.4rem; }
    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 0.5rem 0.9rem !important;
        transition: background 0.2s;
        text-transform: none !important;
        letter-spacing: 0 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover { background: rgba(255,255,255,0.12); }
</style>
""", unsafe_allow_html=True)



def sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <h1>MediCare</h1>
            <p>Hospital Management System</p>
        </div>
        """, unsafe_allow_html=True)

        role = get_role()

        if role == "patient":
            u = get_user()
            st.markdown(f"""
            <div style="padding:0.8rem 1rem; background:rgba(255,255,255,0.08); border-radius:10px; margin-bottom:1.2rem;">
                <div style="font-size:0.75rem; opacity:0.6; text-transform:uppercase; letter-spacing:0.07em;">Signed in as</div>
                <div style="font-weight:700; font-size:1rem;">{u['name']}</div>
                <div style="font-size:0.78rem; opacity:0.65;">{u['email']}</div>
            </div>
            """, unsafe_allow_html=True)
            page = st.radio("nav", ["My Dashboard", "My Records", "Book Appointment", "My Appointments"], label_visibility="collapsed")
            st.markdown("---")
            if st.button("Log Out", use_container_width=True):
                logout()
            return page

        elif role == "doctor":
            u = get_user()
            st.markdown(f"""
            <div style="padding:0.8rem 1rem; background:rgba(255,255,255,0.08); border-radius:10px; margin-bottom:1.2rem;">
                <div style="font-size:0.75rem; opacity:0.6; text-transform:uppercase; letter-spacing:0.07em;">Signed in as</div>
                <div style="font-weight:700; font-size:1rem;">{u['name']}</div>
                <div style="font-size:0.78rem; opacity:0.65;">{u['specialization']}</div>
            </div>
            """, unsafe_allow_html=True)
            page = st.radio("nav", ["Doctor Dashboard", "Patient Records", "Add Record", "Appointments"], label_visibility="collapsed")
            st.markdown("---")
            if st.button("Log Out", use_container_width=True):
                logout()
            return page

        else:
            page = st.radio("nav", ["Home", "Patient Login", "Register", "Doctor Login"], label_visibility="collapsed")
            return page



def main():
    init_db()        # create tables on first run
    page = sidebar() # draw the sidebar and get selected page
    role = get_role() # check who is logged in

    if role is None:
        if "Home" in page:          home()
        elif "Patient Login" in page: patient_login()
        elif "Register" in page:    register()
        elif "Doctor Login" in page: doctor_login()

    # patient is logged in  show patient pages
    elif role == "patient":
        if page == "My Dashboard":       patient_dashboard()
        elif page == "My Records":       my_records()
        elif page == "Book Appointment": book_appt()
        elif page == "My Appointments":  my_appointments()

    # doctor is logged in show doctor pages
    elif role == "doctor":
        if page == "Doctor Dashboard":  doctor_dashboard()
        elif page == "Patient Records": view_patient_records()
        elif page == "Add Record":      add_new_record()
        elif page == "Appointments":    manage_appointments()


if __name__ == "__main__":
    main()