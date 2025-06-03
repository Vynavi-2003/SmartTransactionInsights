# File: app/streamlit_app.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from src.preprocessing import load_and_clean_data
from src.insights import generate_insights

st.set_page_config(page_title="Smart Transaction Insights", layout="centered")
st.title("📊 Smart Transaction Insights")

st.markdown(
    "Upload your transaction CSV to generate personalized financial insights."
)

# Upload CSV
file = st.file_uploader("Upload your transaction CSV", type=["csv"])

if file:
    df = load_and_clean_data(file)
    st.subheader("📄 Raw Transactions")
    st.dataframe(df)

    st.sidebar.header("⚙️ Settings")

    # Spend threshold setting
    threshold = st.sidebar.slider(
        "High Spend Alert Threshold (₹)", min_value=100, max_value=10000, value=1000, step=100
    )

    # LLM toggle
    use_llm = st.sidebar.checkbox("Use LLM for rephrasing insights (GPT)", value=False)

    # Limit number of insights
    max_insights = st.sidebar.number_input(
        "How many insights to show?", min_value=1, max_value=50, value=10, step=1
    )

    # Generate insights
    insights = generate_insights(df, use_llm=use_llm, spend_alert_threshold=threshold)

    # Show top N
    st.subheader("🔍 Insights")
    for i, ins in enumerate(insights[:max_insights], 1):
        st.markdown(f"**{i}.** {ins}")
