"""
This is where your existing simulation (e.g. dso_lab.py's BENCH_HTML,
rendered via st.components.v1.html) plugs in. Search for "PLUG IN YOUR
SIMULATION HERE" below.
"""
import streamlit as st
import streamlit.components.v1 as components
import api_client as api
from dso_lab import render_bench

st.set_page_config(page_title="Simulation - ENGiTwin", page_icon="🔬", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please log in first (go to the main app page).")
    st.stop()

attempt_id = st.session_state.get("active_attempt_id")
experiment = st.session_state.get("active_experiment")

if not attempt_id:
    st.info("No active experiment. Go to **Labs** and click Start on an experiment.")
    st.stop()

left, right = st.columns([3, 2])

# ------------------------------------------------------------------
# LEFT: the simulation bench itself
# ------------------------------------------------------------------
with left:
    st.title(f"🔬 {experiment['title']}")
    st.caption(experiment["description"])

    # ================================================================
    # SIMULATION BENCH
    #
    # dso_lab.py owns the big HTML/JS string (BENCH_HTML) that drives the
    # virtual oscilloscope + function generator bench. render_bench() just
    # drops it into the page via streamlit.components.v1.html.
    #
    # Which bench (if any) loads is driven by experiment["simulation_config"]
    # ["bench"] - set by app/seed.py for the built-in DSO experiment, and by
    # the "Simulator" dropdown on the Labs page for any new ones. Add new
    # bench types here as more simulators get built.
    #
    # NOTE: to feed live readings back to the backend for autosave/scoring,
    # have the bench's JS call:
    #
    #   window.parent.postMessage({type: "engitwin_sim_update", data: {...}}, "*")
    #
    # and add a small Streamlit component / st_javascript listener to
    # forward that payload into api.update_attempt(attempt_id, data).
    # ================================================================
    bench = (experiment.get("simulation_config") or {}).get("bench", "")

    if bench == "dso":
        render_bench()
    else:
        st.info(
            "🚧 There's no interactive simulator wired up for this experiment yet "
            "— take your readings from the real/physical setup (or however your "
            "instructor directed) and record them below.",
        )

    st.divider()
    st.subheader("Submit your results")
    st.caption("Enter the measurements your simulation produced, then complete the attempt.")

    with st.form("complete_form"):
        # Simple generic measurement entry - customize per experiment type
        num_fields = st.number_input("Number of measurements to record", min_value=1, max_value=10, value=2)
        measurements = {}
        cols = st.columns(2)
        for i in range(int(num_fields)):
            with cols[i % 2]:
                key = st.text_input(f"Measurement {i+1} name", key=f"mk_{i}")
                val = st.text_input(f"Measurement {i+1} value", key=f"mv_{i}")
                if key:
                    measurements[key] = val

        submitted = st.form_submit_button("✅ Complete Attempt", use_container_width=True)
        if submitted:
            try:
                result = api.complete_attempt(attempt_id, measurements)
                r = result["result"]
                st.success(f"Score: {r['score']} / {r['max_score']}")
                st.info(r["ai_feedback"])
                st.session_state.active_attempt_id = None
                st.session_state.active_experiment = None
            except api.APIError as e:
                st.error(str(e))

# ------------------------------------------------------------------
# RIGHT: AI lab assistant chat
# ------------------------------------------------------------------
with right:
    st.subheader("🤖 AI Lab Assistant")

    if "ai_chat_loaded" not in st.session_state or st.session_state.get("ai_chat_attempt") != attempt_id:
        try:
            st.session_state.ai_history = api.ai_history(attempt_id)
        except api.APIError:
            st.session_state.ai_history = []
        st.session_state.ai_chat_loaded = True
        st.session_state.ai_chat_attempt = attempt_id

    chat_box = st.container(height=450, border=True)
    with chat_box:
        for msg in st.session_state.ai_history:
            role = "assistant" if msg["role"] == "assistant" else "user"
            with st.chat_message(role):
                st.write(msg["content"])

    if not st.session_state.ai_history:
        if st.button("Start conversation with AI assistant", use_container_width=True):
            try:
                reply = api.ai_ask(attempt_id)
                st.session_state.ai_history.append(reply)
                st.rerun()
            except api.APIError as e:
                st.error(str(e))
    else:
        user_msg = st.chat_input("Answer the assistant's question...")
        if user_msg:
            st.session_state.ai_history.append({"role": "student", "content": user_msg, "created_at": ""})
            try:
                reply = api.ai_ask(attempt_id, user_msg)
                st.session_state.ai_history.append(reply)
                st.rerun()
            except api.APIError as e:
                st.error(str(e))
