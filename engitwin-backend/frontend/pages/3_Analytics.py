import streamlit as st
import pandas as pd
import api_client as api

st.set_page_config(page_title="Analytics - ENGiTwin", page_icon="📊", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please log in first (go to the main app page).")
    st.stop()

st.title("📊 My Analytics")

try:
    data = api.my_analytics()
except api.APIError as e:
    st.error(str(e))
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total attempts", data["total_attempts"])
col2.metric("Completed", data["completed_attempts"])
col3.metric("Average score", data["average_score"])
col4.metric("Best score", data["best_score"])

st.divider()

if data["per_experiment"]:
    df = pd.DataFrame(data["per_experiment"])
    st.subheader("Scores by experiment")
    st.bar_chart(df.set_index("experiment_title")["score"])

    st.subheader("Attempt history")
    st.dataframe(
        df[["experiment_title", "score", "max_score", "completed_at"]],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No completed attempts yet - go finish a lab experiment!")
