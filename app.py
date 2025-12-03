import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# Page setup
st.set_page_config(
    page_title="Shifting Narratives prototype",
    page_icon="🌍",
    layout="centered"
)

# Load data
data_path = Path("data/events.csv")
if data_path.exists():
    df = pd.read_csv(data_path)
else:
    df = pd.DataFrame({
        "event_name": [
            "Climate Summit", "Climate Summit",
            "AI Regulation", "AI Regulation",
            "World Cup Final", "World Cup Final"
        ],
        "stakeholder": [
            "Government", "Media",
            "Government", "Media",
            "Public", "Media"
        ],
        "text_summary": [
            "Focuses on cooperation and policy agreements.",
            "Highlights protests and controversies.",
            "Emphasizes innovation and competitiveness.",
            "Warns about risks and ethical concerns.",
            "Celebrates unity and friendly rivalry.",
            "Debates referee decisions and drama."
        ],
        "sentiment": [0.6, -0.3, 0.4, -0.2, 0.5, -0.1],
        "keywords": [
            "policy, agreement, targets",
            "protest, criticism, deal",
            "innovation, regulation, growth",
            "risk, ethics, control",
            "celebration, unity, rivalry",
            "referee, drama, debate"
        ],
        "date": [
            "2023-11-15", "2023-11-15",
            "2024-02-10", "2024-02-10",
            "2022-12-18", "2022-12-18"
        ]
    })

# Sidebar controls
st.sidebar.header("Controls")
event = st.sidebar.selectbox("Select an event", df["event_name"].unique())
stakeholder = st.sidebar.radio("Select stakeholder", ["Government", "Media", "Public"])
mood_adjust = st.sidebar.slider("Adjust sentiment intensity", -0.5, 0.5, 0.0, 0.05)

# Filter and process data
event_df = df[df["event_name"] == event].copy()

if stakeholder in event_df["stakeholder"].unique():
    row = event_df[event_df["stakeholder"] == stakeholder].iloc[0]
else:
    row = event_df.iloc[0]
    stakeholder = row["stakeholder"]

# Apply mood adjustment
event_df["sentiment"] = event_df["sentiment"] + mood_adjust
row_sentiment = float(row["sentiment"]) + mood_adjust

# Header
st.title("Shifting Narratives")
st.subheader(f"{stakeholder} perspective on {event}")

# Summary and sentiment
sent_color = (
    "MediumSeaGreen" if row_sentiment > 0.2
    else ("SlateGray" if -0.2 <= row_sentiment <= 0.2
          else "Crimson")
)
sent_label = (
    "Positive" if row_sentiment > 0.2
    else ("Neutral" if -0.2 <= row_sentiment <= 0.2
          else "Negative")
)

st.markdown(
    f"<div style='padding:12px;border-radius:10px;background:#f5f5f5;'>"
    f"<b>Summary:</b> {row['text_summary']}</div>",
    unsafe_allow_html=True
)
st.markdown(
    f"<div style='margin-top:8px;color:{sent_color};'>"
    f"<b>Sentiment:</b> {row_sentiment:.2f} ({sent_label})</div>",
    unsafe_allow_html=True
)
st.write(f"**Keywords:** {row['keywords']}")

# Timeline visualization
timeline = (
    alt.Chart(df)
    .mark_circle(size=120)
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("event_name:N", title="Event"),
        color=alt.Color("stakeholder:N", legend=None),
        tooltip=["event_name", "stakeholder", "sentiment"]
    )
    .properties(title="Event Timeline", height=150)
)
st.altair_chart(timeline, use_container_width=True)

# Sentiment comparison bar chart for current event
bar_chart = (
    alt.Chart(event_df)
    .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
    .encode(
        x=alt.X("stakeholder:N", title="Stakeholder"),
        y=alt.Y(
            "sentiment:Q",
            title="Sentiment Score",
            scale=alt.Scale(domain=[-0.6, 0.6])
        ),
        color=alt.Color("stakeholder:N"),
        tooltip=["stakeholder", "sentiment"]
    )
    .properties(width=500, height=260, title="Sentiment Comparison (Bar)")
)
st.altair_chart(bar_chart, use_container_width=True)

# 🥧 Pie chart: sentiment intensity per stakeholder (current event)
# Create non-negative intensity and sentiment category
pie_df = event_df.copy()
pie_df["sentiment_intensity"] = pie_df["sentiment"].abs()
pie_df["sentiment_category"] = pie_df["sentiment"].apply(
    lambda s: "Positive" if s > 0.05 else ("Negative" if s < -0.05 else "Neutral")
)

pie_chart = (
    alt.Chart(pie_df)
    .mark_arc(innerRadius=40)  # donut style
    .encode(
        theta=alt.Theta("sentiment_intensity:Q", title="Sentiment Intensity"),
        color=alt.Color("stakeholder:N", title="Stakeholder"),
        tooltip=["stakeholder", "sentiment", "sentiment_category"]
    )
    .properties(
        width=350,
        height=350,
        title=f"Sentiment Intensity by Stakeholder for '{event}' (Pie)"
    )
)

st.altair_chart(pie_chart, use_container_width=False)

# Interaction fun
col1, col2 = st.columns(2)
with col1:
    if st.button("Celebrate understanding 🎉"):
        st.balloons()

st.caption("Interactive visualization of narrative differences across stakeholders.")
