"""
Assignments page - covers the Teacher -> Student edge of the diagram
(Institution -> Teacher / Student -> Assignments) that the backend already
supports (/assignments, /assignments/mine, /users) but had no frontend for.

Teachers see a form to assign an experiment to one of their students.
Students (and everyone else, harmlessly) see a list of what's been
assigned to them, with a button to jump straight into the simulation.
"""
import datetime as dt

import streamlit as st
import api_client as api

st.set_page_config(page_title="Assignments - ENGiTwin", page_icon="📝", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please log in first (go to the main app page).")
    st.stop()

user = st.session_state.user
st.title("📝 Assignments")

# ---------------------------------------------------------------------
# Teacher view: assign an experiment to a student
# ---------------------------------------------------------------------
if user["role"] == "teacher":
    st.subheader("Assign a lab to a student")

    try:
        labs = api.list_labs()
    except api.APIError as e:
        st.error(str(e))
        labs = []

    try:
        students = [u for u in api.list_users() if u["role"] == "student"]
    except api.APIError as e:
        st.error(str(e))
        students = []

    if not labs:
        st.info("No labs exist yet - create one on the **Labs** page first.")
    elif not students:
        st.info("No students found yet. Students need to sign up (and join your "
                 "institution, if you're using one) before you can assign work to them.")
    else:
        with st.form("assign_form"):
            lab_choice = st.selectbox("Lab", labs, format_func=lambda l: l["title"])

            try:
                experiments = api.list_experiments(lab_choice["id"]) if lab_choice else []
            except api.APIError as e:
                st.error(str(e))
                experiments = []

            if not experiments:
                st.caption("This lab has no experiments yet.")
                exp_choice = None
            else:
                exp_choice = st.selectbox("Experiment", experiments, format_func=lambda x: x["title"])

            student_choice = st.selectbox("Student", students, format_func=lambda s: f"{s['name']} ({s['email']})")
            due = st.date_input("Due date", value=None)

            submitted = st.form_submit_button("Assign", use_container_width=True)
            if submitted:
                if not exp_choice:
                    st.error("Pick an experiment with at least one existing entry.")
                else:
                    try:
                        due_dt = dt.datetime.combine(due, dt.time()) if due else None
                        api.create_assignment(exp_choice["id"], student_choice["id"], due_dt)
                        st.success(f"Assigned '{exp_choice['title']}' to {student_choice['name']}.")
                    except api.APIError as e:
                        st.error(str(e))

    st.divider()

# ---------------------------------------------------------------------
# Everyone: "my assignments" (populated for students; empty otherwise)
# ---------------------------------------------------------------------
st.subheader("My assignments")

try:
    assignments = api.my_assignments()
except api.APIError as e:
    st.error(str(e))
    assignments = []

if not assignments:
    st.info("Nothing assigned to you yet.")
else:
    for a in assignments:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                due_str = a["due_date"][:10] if a.get("due_date") else "no due date"
                st.markdown(f"**Experiment #{a['experiment_id']}** &nbsp;·&nbsp; due {due_str}")
                st.caption(f"Assigned by teacher #{a['teacher_id']}")
            with col2:
                if st.button("Start ▶", key=f"assign_start_{a['id']}", use_container_width=True):
                    try:
                        exp = api.get_experiment(a["experiment_id"])
                        attempt = api.start_attempt(exp["id"])
                        st.session_state.active_attempt_id = attempt["id"]
                        st.session_state.active_experiment = exp
                        st.switch_page("pages/2_Simulation.py")
                    except api.APIError as e:
                        st.error(str(e))
