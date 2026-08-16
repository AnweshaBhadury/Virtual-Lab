import streamlit as st
import api_client as api

st.set_page_config(page_title="Labs - ENGiTwin", page_icon="📚", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please log in first (go to the main app page).")
    st.stop()

user = st.session_state.user

st.markdown(
    """
    <style>
    .lab-title { font-size: 17px; font-weight: 800; color: #f0f3f7; }
    .lab-cat { font-size: 11px; font-weight: 700; color: #4f8ef7; letter-spacing: 0.5px; }
    .lab-desc { font-size: 13px; color: #9aa5b3; margin-top: 4px; }
    .exp-row {
        background: #10151c; border: 1px solid #232b36; border-radius: 10px;
        padding: 10px 14px; margin-top: 8px;
    }
    .sim-badge {
        display:inline-block; font-size: 10px; font-weight: 800; padding: 2px 7px;
        border-radius: 5px; margin-left: 6px; vertical-align: middle;
    }
    .sim-badge.live { background: #1f9d55; color: #fff; }
    .sim-badge.soon { background: #3a3f2a; color: #cfd3a0; border: 1px solid #6b7050; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Known bench types the frontend actually knows how to render. Everything
# else falls back to a manual measurement-entry flow (still fully
# gradeable) with a "coming soon" note in the simulation view. Key must
# match what app/seed.py and the backend use: simulation_config["bench"].
BENCH_TYPES = {
    "": "None (manual entry only)",
    "dso": "Digital Storage Oscilloscope + Function Generator",
}

# Teachers / institution admins / independent users can create labs
can_create = user["role"] in ("teacher", "institution_admin", "independent_user")

selected_category = st.session_state.get("selected_category")

# ---------------------------------------------------------------------
# Header / breadcrumb
# ---------------------------------------------------------------------
if selected_category:
    if st.button("← All subjects", key="back_to_subjects"):
        st.session_state.selected_category = None
        st.rerun()
    st.title(f"📚 {selected_category}")
else:
    st.title("📚 All Labs")
    st.caption("Tip: pick a subject from the home page for a focused view, or browse everything below.")

# ---------------------------------------------------------------------
# Create a new lab (optionally pre-filled with the selected subject)
# ---------------------------------------------------------------------
if can_create:
    with st.expander("➕ Create a new lab"):
        with st.form("create_lab_form"):
            title = st.text_input("Lab title")
            description = st.text_area("Description")
            category = st.text_input("Category / subject", value=selected_category or "general")
            submitted = st.form_submit_button("Create lab")
            if submitted and title:
                try:
                    api.create_lab(title, description, category)
                    st.success("Lab created.")
                    st.rerun()
                except api.APIError as e:
                    st.error(str(e))

try:
    labs = api.list_labs()
except api.APIError as e:
    st.error(str(e))
    st.stop()

if selected_category:
    labs = [l for l in labs if l["category"] == selected_category]

if not labs:
    st.info("No labs here yet." + (" Create one above to get started." if can_create else ""))
    st.stop()

# ---------------------------------------------------------------------
# Lab list
# ---------------------------------------------------------------------
for lab in labs:
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="lab-title">{lab['title']}</div>
            <div class="lab-cat">{lab['category'].upper()}</div>
            <div class="lab-desc">{lab['description'] or ''}</div>
            """,
            unsafe_allow_html=True,
        )

        try:
            experiments = api.list_experiments(lab["id"])
        except api.APIError as e:
            st.error(str(e))
            experiments = []

        if can_create:
            with st.expander("➕ Add experiment to this lab"):
                with st.form(f"create_exp_{lab['id']}"):
                    e_title = st.text_input("Experiment title", key=f"et_{lab['id']}")
                    e_desc = st.text_area("Experiment description", key=f"ed_{lab['id']}")
                    e_max = st.number_input("Max score", value=100.0, key=f"em_{lab['id']}")
                    bench = st.selectbox(
                        "Simulator",
                        list(BENCH_TYPES.keys()),
                        format_func=lambda k: BENCH_TYPES[k],
                        key=f"bench_{lab['id']}",
                        help="Picks which interactive bench opens on the Simulation page. "
                             "Leave as 'None' if students should just take real/manual readings.",
                    )
                    submitted = st.form_submit_button("Create experiment")
                    if submitted and e_title:
                        try:
                            config = {"bench": bench} if bench else {}
                            api.create_experiment(lab["id"], e_title, e_desc, config, e_max)
                            st.success("Experiment created.")
                            st.rerun()
                        except api.APIError as e2:
                            st.error(str(e2))

        if not experiments:
            st.caption("No experiments in this lab yet.")
            continue

        for exp in experiments:
            bench = (exp.get("simulation_config") or {}).get("bench", "")
            badge = (
                '<span class="sim-badge live">LIVE SIMULATOR</span>'
                if bench in ("dso",)
                else '<span class="sim-badge soon">MANUAL / COMING SOON</span>'
            )
            st.markdown(
                f"""
                <div class="exp-row">
                    <b>{exp['title']}</b> {badge} &nbsp;·&nbsp; max score {exp['max_score']}
                    <div style="font-size:12px;color:#9aa5b3;margin-top:2px;">{exp['description'] or ''}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            _, col2 = st.columns([4, 1])
            with col2:
                if st.button("Start ▶", key=f"start_{exp['id']}", use_container_width=True):
                    try:
                        attempt = api.start_attempt(exp["id"])
                        st.session_state.active_attempt_id = attempt["id"]
                        st.session_state.active_experiment = exp
                        st.switch_page("pages/2_Simulation.py")
                    except api.APIError as e3:
                        st.error(str(e3))
