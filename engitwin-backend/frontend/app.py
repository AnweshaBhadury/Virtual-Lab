"""
ENGiTwin frontend - main entry point.

Run with:  streamlit run app.py
(from inside the frontend/ folder, with the backend already running on
 http://localhost:8000)

Handles:
- Login
- Signup, split into two paths:
    * Independent User - just an account, no institution.
    * Institution - either join an existing institution with a code
      (as teacher or student, capped by the institution's seat limit),
      or set up a brand new institution (becomes institution_admin,
      gets a shareable code + seat limit back).
- The landing page after login: a subject-category grid (Physics,
  Electrical, Computer Networks, DBMS, ...) that hands off to the Labs
  page filtered to whichever subject was clicked.
"""
import streamlit as st
import api_client as api

st.set_page_config(page_title="ENGiTwin", page_icon="🧪", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.user = None

CATEGORY_ICONS = {
    "Electrical": "⚡",
    "Physics": "🔭",
    "Computer Networks": "🌐",
    "DBMS": "🗄️",
    "Mechanical": "⚙️",
    "Digital": "🔢",
    "Chemistry": "🧪",
    "general": "🧭",
}


def category_icon(name: str) -> str:
    return CATEGORY_ICONS.get(name, "📁")


# ---------------------------------------------------------------------
# LOGIN / SIGNUP
# ---------------------------------------------------------------------
def show_login():
    st.title("🧪 ENGiTwin")
    st.caption("Virtual lab platform - log in or create an account to continue.")

    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in", use_container_width=True)
            if submitted:
                try:
                    data = api.login(email, password)
                    st.session_state.token = data["access_token"]
                    st.session_state.user = data["user"]
                    st.rerun()
                except api.APIError as e:
                    st.error(str(e))

    with tab_signup:
        account_type = st.radio(
            "Account type",
            ["Independent User", "Institution"],
            horizontal=True,
            help="Independent User: just you, no institution. "
                 "Institution: join your college/school (or set one up).",
        )

        if account_type == "Independent User":
            _signup_independent()
        else:
            _signup_institution()


def _signup_independent():
    with st.form("signup_independent_form"):
        name = st.text_input("Full name")
        email = st.text_input("Email", key="indie_email")
        password = st.text_input("Password", type="password", key="indie_password")
        submitted = st.form_submit_button("Create account", use_container_width=True)
        if submitted:
            try:
                data = api.signup(name, email, password, "independent_user")
                st.session_state.token = data["access_token"]
                st.session_state.user = data["user"]
                st.rerun()
            except api.APIError as e:
                st.error(str(e))


def _signup_institution():
    mode = st.radio(
        "I want to...",
        ["Join with an institution code", "Set up a new institution"],
        horizontal=True,
    )

    if mode == "Join with an institution code":
        with st.form("signup_join_form"):
            name = st.text_input("Full name")
            email = st.text_input("Email", key="join_email")
            password = st.text_input("Password", type="password", key="join_password")
            role = st.selectbox("I am a...", ["student", "teacher"])
            code = st.text_input(
                "Institution code",
                help="Given to you by your institution admin.",
            ).strip().upper()
            submitted = st.form_submit_button("Join institution", use_container_width=True)
            if submitted:
                if not code:
                    st.error("Enter the institution code you were given.")
                else:
                    try:
                        data = api.signup(name, email, password, role, code)
                        st.session_state.token = data["access_token"]
                        st.session_state.user = data["user"]
                        st.rerun()
                    except api.APIError as e:
                        st.error(str(e))

    else:  # Set up a new institution
        st.caption(
            "You'll become the **institution admin**. After creating it, you'll "
            "get a code to share with your teachers and students."
        )
        with st.form("signup_new_institution_form"):
            inst_name = st.text_input("Institution name")
            name = st.text_input("Your full name")
            email = st.text_input("Your email", key="new_inst_email")
            password = st.text_input("Your password", type="password", key="new_inst_password")
            max_students = st.number_input(
                "Student seats to allow",
                min_value=0, value=30, step=1,
                help="How many students can join with this code. 0 = unlimited.",
            )
            submitted = st.form_submit_button("Create institution & account", use_container_width=True)
            if submitted:
                if not inst_name:
                    st.error("Enter an institution name.")
                else:
                    try:
                        inst = api.create_institution(inst_name, int(max_students))
                        data = api.signup(name, email, password, "institution_admin", inst["code"])
                        st.session_state.token = data["access_token"]
                        st.session_state.user = data["user"]
                        st.session_state.just_created_institution = inst
                        st.rerun()
                    except api.APIError as e:
                        st.error(str(e))


# ---------------------------------------------------------------------
# LANDING PAGE
# ---------------------------------------------------------------------
def show_landing():
    user = st.session_state.user

    st.markdown(
        """
        <style>
        .cat-card {
            background: linear-gradient(160deg, #1e2530 0%, #161b22 100%);
            border: 1px solid #2d3540; border-radius: 14px;
            padding: 22px 18px 16px 18px; text-align: center;
            transition: border-color 0.15s ease, transform 0.15s ease;
        }
        .cat-card:hover { border-color: #4f8ef7; transform: translateY(-2px); }
        .cat-icon { font-size: 34px; margin-bottom: 6px; }
        .cat-title { font-size: 16px; font-weight: 700; color: #f0f3f7; margin-bottom: 2px; }
        .cat-sub { font-size: 12px; color: #8a94a3; }
        .hero-banner {
            background: linear-gradient(120deg, #16324f 0%, #0d1b2a 100%);
            border-radius: 16px; padding: 28px 30px; margin-bottom: 22px;
            border: 1px solid #23445e;
        }
        .hero-title { font-size: 26px; font-weight: 800; color: #f0f3f7; margin-bottom: 4px; }
        .hero-sub { font-size: 14px; color: #9fb3c8; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.write(f"**{user['name']}**")
        st.caption(f"{user['email']} · {user['role'].replace('_', ' ').title()}")
        st.page_link("pages/1_Labs.py", label="Labs", icon="📚")
        st.page_link("pages/3_Analytics.py", label="Analytics", icon="📊")
        st.page_link("pages/4_Assignments.py", label="Assignments", icon="📝")
        if st.button("Log out", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()

    inst_just_created = st.session_state.pop("just_created_institution", None)
    if inst_just_created:
        st.success(
            f"Institution **{inst_just_created['name']}** created! "
            f"Share this code with your teachers and students: "
            f"`{inst_just_created['code']}` "
            f"({'unlimited' if inst_just_created['max_students'] == 0 else inst_just_created['max_students']} student seats)"
        )

    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-title">Welcome back, {user['name']} 👋</div>
            <div class="hero-sub">Pick a subject below to browse its labs and start an experiment.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("🔬 Labs")

    try:
        labs = api.list_labs()
    except api.APIError as e:
        st.error(str(e))
        labs = []

    # group labs by subject category
    by_category = {}
    for lab in labs:
        by_category.setdefault(lab["category"], []).append(lab)

    if not by_category:
        st.info("No labs yet.")
        return

    categories = sorted(by_category.keys())
    cols = st.columns(4)
    for i, cat in enumerate(categories):
        cat_labs = by_category[cat]

        with cols[i % 4]:
            st.markdown(
                f"""
                <div class="cat-card">
                    <div class="cat-icon">{category_icon(cat)}</div>
                    <div class="cat-title">{cat}</div>
                    <div class="cat-sub">{len(cat_labs)} lab{'s' if len(cat_labs) != 1 else ''}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open →", key=f"open_cat_{cat}", use_container_width=True):
                st.session_state.selected_category = cat
                st.switch_page("pages/1_Labs.py")
            st.write("")  # small spacer between rows


if not st.session_state.token:
    show_login()
else:
    show_landing()
