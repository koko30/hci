import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# -------------------------------------------------
# Page Setup: Defines title, icon, and screen layout
# -------------------------------------------------
st.set_page_config(
    page_title="Shifting Narratives",
    page_icon="🌍",
    layout="centered"
)

# -------------------------------------------------
# Data Loading: Reads event data from CSV or uses a fallback sample
# -------------------------------------------------
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

df["date"] = pd.to_datetime(df["date"])

# -------------------------------------------------
# Sentiment Label Function: Converts numeric values into categories
# -------------------------------------------------
def label_sentiment(s: float) -> str:
    if s > 0.05:
        return "Positive"
    elif s < -0.05:
        return "Negative"
    else:
        return "Neutral"

df["sentiment_category"] = df["sentiment"].apply(label_sentiment)

# Color mapping for sentiment categories
sentiment_color_scale = alt.Scale(
    domain=["Positive", "Neutral", "Negative"],
    range=["#2ca02c", "#7f7f7f", "#d62728"]
)

# -------------------------------------------------
# Sidebar Controls: User selections for event, perspective, and sentiment adjustment
# -------------------------------------------------
st.sidebar.header("Controls")

event = st.sidebar.selectbox(
    "Select an event",
    options=df["event_name"].unique()
)

stakeholder_choice = st.sidebar.radio(
    "Select stakeholder",
    options=["Government", "Media", "Public"]
)

mood_adjust = st.sidebar.slider(
    "Adjust sentiment intensity",
    min_value=-0.5,
    max_value=0.5,
    value=0.0,
    step=0.05
)

# -------------------------------------------------
# Filtering: Extracts data for the selected event and applies adjustments
# -------------------------------------------------
event_df = df[df["event_name"] == event].copy()
event_df["sentiment"] = event_df["sentiment"] + mood_adjust
event_df["sentiment_category"] = event_df["sentiment"].apply(label_sentiment)

# Determine which narrative to display as the main summary
if stakeholder_choice in event_df["stakeholder"].unique():
    row = event_df[event_df["stakeholder"] == stakeholder_choice].iloc[0]
    effective_stakeholder = stakeholder_choice
else:
    row = event_df.iloc[0]
    effective_stakeholder = row["stakeholder"]

row_sentiment = float(row["sentiment"])
row_category = label_sentiment(row_sentiment)

# -------------------------------------------------
# Header Section
# -------------------------------------------------
st.title("Shifting Narratives")
st.subheader(f"{effective_stakeholder} Perspective On “{event}”")

# -------------------------------------------------
# Color legend for sentiment interpretation
# -------------------------------------------------
st.markdown(
    """
### Color Meaning

- 🟢 Green = Positive  
- ⚪ Grey = Neutral  
- 🔴 Red = Negative  
"""
)

# -------------------------------------------------
# Summary Display: Shows narrative text and sentiment value
# -------------------------------------------------
if row_category == "Positive":
    sent_color = "#2ca02c"
elif row_category == "Negative":
    sent_color = "#d62728"
else:
    sent_color = "#7f7f7f"

st.markdown(
    f"""
<div style='padding:12px;border-radius:10px;background:#f5f5f5;'>
  <b>Summary ({effective_stakeholder}):</b> {row['text_summary']}
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div style='margin-top:8px;color:{sent_color};font-weight:bold;'>
  Sentiment: {row_sentiment:.2f} ({row_category})
</div>
""",
    unsafe_allow_html=True,
)

st.write(f"**Keywords:** {row['keywords']}")

# -------------------------------------------------
# Timeline Chart: Displays when each narrative was recorded
# -------------------------------------------------
st.markdown("### Event Timeline")

timeline = (
    alt.Chart(df)
    .mark_circle(size=120)
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("event_name:N", title="Event"),
        color="stakeholder:N",
        tooltip=["event_name", "stakeholder", "sentiment"]
    )
    .properties(height=160)
)

st.altair_chart(timeline, use_container_width=True)

# -------------------------------------------------
# Bar Chart: Shows sentiment values above or below zero
# -------------------------------------------------
st.markdown("### Sentiment Comparison")

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
        color=alt.Color(
            "sentiment_category:N",
            title="Sentiment",
            scale=sentiment_color_scale
        ),
        tooltip=["stakeholder", "sentiment", "sentiment_category"]
    )
    .properties(width=500, height=260)
)

st.altair_chart(bar_chart, use_container_width=True)

# -------------------------------------------------
# Pie Chart: Represents the strength of emotional tone
# -------------------------------------------------
st.markdown("### Emotional Intensity")

pie_df = event_df.copy()
pie_df["sentiment_intensity"] = pie_df["sentiment"].abs()

pie_chart = (
    alt.Chart(pie_df)
    .mark_arc(innerRadius=40)
    .encode(
        theta=alt.Theta("sentiment_intensity:Q", title="Intensity"),
        color=alt.Color(
            "sentiment_category:N",
            title="Sentiment",
            scale=sentiment_color_scale
        ),
        tooltip=["stakeholder", "sentiment", "sentiment_category"]
    )
    .properties(width=350, height=350)
)

st.altair_chart(pie_chart, use_container_width=False)

# -------------------------------------------------
# Simple Interaction Element
# -------------------------------------------------
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("Done Exploring 🎉"):
        st.balloons()
