import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# -------------------------------------------------
# Page Setup
# -------------------------------------------------
st.set_page_config(
    page_title="Shifting Narratives",
    page_icon="🌍",
    layout="centered"
)

# -------------------------------------------------
# Data Loading
# -------------------------------------------------
data_path = Path("data/events.csv")

if data_path.exists():
    df = pd.read_csv(data_path)
else:
    df = pd.DataFrame({
        "event_name": [
            "Climate Summit", "Climate Summit", "Climate Summit",
            "AI Regulation", "AI Regulation", "AI Regulation",
            "World Cup Final", "World Cup Final", "World Cup Final"
        ],
        "stakeholder": [
            "Government", "Media", "Public",
            "Government", "Media", "Public",
            "Government", "Media", "Public"
        ],
        "text_summary": [
            "Government stresses cooperation and long-term climate agreements.",
            "Media emphasizes mixed reactions and different negotiation outcomes.",
            "Public expresses hope but also frustration about slow progress.",
            "Government highlights AI innovation and safety frameworks.",
            "Media reports on heated debates about regulation speed.",
            "Public discussions show uncertainty and cautious optimism.",
            "Government congratulates athletes and focuses on national pride.",
            "Media covers intense match moments and controversial decisions.",
            "Public reactions include excitement and a calm appreciation of the match."
        ],
        "sentiment": [
            0.45, 0.02, -0.18,
            0.32, -0.22, 0.00,
            0.52, -0.14, 0.03
        ],
        "keywords": [
            "agreement, targets, cooperation",
            "reactions, negotiation, outcomes",
            "hope, frustration, progress",
            "innovation, safety, framework",
            "risk, debate, speed",
            "uncertainty, optimism, discussion",
            "pride, celebration, unity",
            "drama, controversy, intensity",
            "reaction, appreciation, calm"
        ],
        "date": [
            "2023-11-15", "2023-11-15", "2023-11-15",
            "2024-02-10", "2024-02-10", "2024-02-10",
            "2022-12-18", "2022-12-18", "2022-12-18"
        ]
    })

df["date"] = pd.to_datetime(df["date"])

# -------------------------------------------------
# Sentiment Categorization
# -------------------------------------------------
def label_sentiment(s: float) -> str:
    if s > 0.05:
        return "Positive"
    elif s < -0.05:
        return "Negative"
    else:
        return "Neutral"

df["sentiment_category"] = df["sentiment"].apply(label_sentiment)

sentiment_color_scale = alt.Scale(
    domain=["Positive", "Neutral", "Negative"],
    range=["#2ca02c", "#7f7f7f", "#d62728"]
)

# -------------------------------------------------
# Sidebar Controls
# -------------------------------------------------
st.sidebar.header("Controls")

event = st.sidebar.selectbox(
    "Select Event",
    options=df["event_name"].unique()
)

stakeholder_choice = st.sidebar.radio(
    "Select Stakeholder",
    options=df["stakeholder"].unique()
)

mood_adjust = st.sidebar.slider(
    "Adjust Sentiment Intensity",
    min_value=-0.5,
    max_value=0.5,
    value=0.0,
    step=0.05
)

comparison_mode = st.sidebar.checkbox("Enable Comparison Mode")

# -------------------------------------------------
# Event Filtering
# -------------------------------------------------
event_df = df[df["event_name"] == event].copy()
event_df["sentiment"] = event_df["sentiment"] + mood_adjust
event_df["sentiment_category"] = event_df["sentiment"].apply(label_sentiment)

if stakeholder_choice in event_df["stakeholder"].unique():
    row = event_df[event_df["stakeholder"] == stakeholder_choice].iloc[0]
    effective_stakeholder = stakeholder_choice
else:
    row = event_df.iloc[0]
    effective_stakeholder = row["stakeholder"]

row_sentiment = float(row["sentiment"])
row_category = label_sentiment(row_sentiment)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("Shifting Narratives")
st.subheader(f"{effective_stakeholder} Perspective On “{event}”")

# -------------------------------------------------
# Summary (Bigger Text)
# -------------------------------------------------
if row_category == "Positive":
    sent_color = "#2ca02c"
elif row_category == "Negative":
    sent_color = "#d62728"
else:
    sent_color = "#7f7f7f"

st.markdown(
    f"""
<div style='padding:18px;border-radius:10px;background:#f5f5f5;font-size:22px;line-height:1.5;'>
  <b>Summary ({effective_stakeholder}):</b><br>{row['text_summary']}
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div style='margin-top:10px;color:{sent_color};font-weight:bold;font-size:20px;'>
  Sentiment: {row_sentiment:.2f} ({row_category})
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"<div style='font-size:18px;margin-top:10px;'><b>Keywords:</b> {row['keywords']}</div>",
    unsafe_allow_html=True
)

# -------------------------------------------------
# Color Legend (Moved BELOW Summary & ABOVE Charts)
# -------------------------------------------------
st.markdown(
    """
### Color Meaning  
🟢 <span style='font-size:18px;'>Green = Positive</span><br>
⚪ <span style='font-size:18px;'>Grey = Neutral</span><br>
🔴 <span style='font-size:18px;'>Red = Negative</span>
""",
    unsafe_allow_html=True
)

# -------------------------------------------------
# Timeline Chart
# -------------------------------------------------
st.markdown("### Event Timeline")

timeline = (
    alt.Chart(df)
    .mark_circle(size=140)
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("event_name:N", title="Event"),
        color="stakeholder:N",
        tooltip=["event_name", "stakeholder", "sentiment"]
    )
)

st.altair_chart(timeline, use_container_width=True)

# -------------------------------------------------
# Comparison Mode Charts
# -------------------------------------------------
if comparison_mode:

    st.markdown("### Sentiment Comparison")

    bar_chart = (
        alt.Chart(event_df)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("stakeholder:N", title="Stakeholder"),
            y=alt.Y("sentiment:Q", title="Score", scale=alt.Scale(domain=[-0.6, 0.6])),
            color=alt.Color("sentiment_category:N", title="Sentiment", scale=sentiment_color_scale),
            tooltip=["stakeholder", "sentiment", "sentiment_category"]
        )
        .properties(width=500, height=260)
    )
    st.altair_chart(bar_chart, use_container_width=True)

    st.markdown("### Emotional Intensity")

    pie_df = event_df.copy()
    pie_df["sentiment_intensity"] = pie_df["sentiment"].abs()

    pie_chart = (
        alt.Chart(pie_df)
        .mark_arc(innerRadius=40)
        .encode(
            theta="sentiment_intensity:Q",
            color=alt.Color("sentiment_category:N", title="Sentiment", scale=sentiment_color_scale),
            tooltip=["stakeholder", "sentiment", "sentiment_category"]
        )
        .properties(width=350, height=350)
    )
    st.altair_chart(pie_chart, use_container_width=False)

# -------------------------------------------------
# End Interaction
# -------------------------------------------------
st.markdown("---")
if st.button("Done Exploring 🎉"):
    st.balloons()
