import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# --- Page setup ---
st.set_page_config(page_title="Shifting Narratives", page_icon="🌍", layout="centered")

# --- Load data ---
data_path = Path("data/events.csv")
if data_path.exists():
    df = pd.read_csv(data_path)
else:
    # If no CSV file found, use example data
    df = pd.DataFrame({
        "event_name": ["Climate Summit","Climate Summit","AI Regulation","AI Regulation","World Cup Final","World Cup Final"],
        "stakeholder": ["Government","Media","Government","Media","Public","Media"],
        "text_summary": [
            "Focuses on cooperation and policy agreements.",
            "Highlights protests and controversies.",
            "Emphasizes innovation and safety.",
            "Raises questions about motives and privacy.",
            "Celebrates unity and friendly rivalry.",
            "Debates referee decisions and drama."
        ],
        "sentiment": [0.6,-0.3,0.4,-0.2,0.5,-0.1],
        "keywords": [
            "policy, agreement, targets",
            "protest, criticism, deal",
            "innovation, safety, law",
            "ethics, control, privacy",
            "celebration, unity, rivalry",
            "referee, drama, debate"
        ],
        "date": ["2023-11-15","2023-11-15","2024-02-10","2024-02-10","2022-12-18","2022-12-18"]
    })

# --- Sidebar controls ---
st.sidebar.markdown("## ⚙️ Controls")
event = st.sidebar.selectbox("Select an event", df["event_name"].unique())
stakeholder = st.sidebar.radio("Select stakeholder", ["Government","Media","Public"])
boost = st.sidebar.slider("🎚️ Adjust mood intensity", -0.5, 0.5, 0.0, 0.05)

# --- Filter data for chosen event ---
event_df = df[df["event_name"] == event].copy()
if stakeholder in event_df["stakeholder"].unique():
    row = event_df[event_df["stakeholder"] == stakeholder].iloc[0]
else:
    row = event_df.iloc[0]
    stakeholder = row["stakeholder"]

event_df["sentiment"] = event_df["sentiment"] + boost
row_sent = float(row["sentiment"]) + boost

# --- Header ---
st.markdown("## 🌍 Shifting Narratives — Interactive Demo")
st.markdown(f"**👤 {stakeholder}** on **_{event}_**")

# --- Narrative box ---
sent_note = "✅ Positive vibe" if row_sent > 0.2 else ("😐 Neutral-ish" if -0.2 <= row_sent <= 0.2 else "⚠️ Negative vibe")
sent_color = "MediumSeaGreen" if row_sent > 0.2 else ("SlateGray" if -0.2 <= row_sent <= 0.2 else "Crimson")

st.markdown(
    f"<div style='padding:12px;border-radius:12px;background:#f0f0f0;'>"
    f"<b>Summary:</b> {row['text_summary']}</div>",
    unsafe_allow_html=True
)
st.markdown(
    f"<div style='margin-top:6px;color:{sent_color};'>"
    f"<b>Sentiment:</b> {row_sent:.2f} — {sent_note}</div>",
    unsafe_allow_html=True
)
st.write(f"**🔑 Keywords:** {row['keywords']}")

# --- Timeline chart (shows all events) ---
timeline = alt.Chart(df).mark_circle(size=120).encode(
    x=alt.X("date:T", title="Date"),
    y=alt.Y("event_name:N", title="Event"),
    color=alt.Color("stakeholder:N", legend=None),
    tooltip=["event_name", "stakeholder", "sentiment"]
).properties(
    title="📅 Event Timeline",
    height=150
)
st.altair_chart(timeline, use_container_width=True)

# --- Sentiment bar chart ---
base = alt.Chart(event_df).encode(
    x=alt.X("stakeholder:N", title="Stakeholder"),
    y=alt.Y("sentiment:Q", title="Sentiment Score", scale=alt.Scale(domain=[-0.6, 0.6])),
    tooltip=["stakeholder","sentiment"]
)

chart = base.mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
    color=alt.Color("stakeholder:N", scale=alt.Scale(scheme="tableau20"))
).properties(
    width=500, height=260, title="Sentiment Comparison (with mood slider)"
)

st.altair_chart(chart, use_container_width=True)

# --- Fun buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🎉 Celebrate understanding"):
        st.balloons()
with col2:
    if st.button("❄️ Snow (just for fun)"):
        st.snow()

st.caption("Tip: tweak the slider to see how the chart responds. Add your own events in data/events.csv.")
