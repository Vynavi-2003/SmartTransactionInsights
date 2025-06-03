import pandas as pd
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_insights(df, use_llm=False, spend_alert_threshold=1000):
    insights = []

    required_cols = {'category', 'amount', 'month', 'year', 'date', 'description'}
    if not required_cols.issubset(df.columns):
        return ["Required columns missing for generating insights."]

    # ----- 1. Category-wise monthly trend -----
    for category in df['category'].dropna().unique():
        subset = df[df['category'] == category]
        monthly_totals = subset.groupby(['year', 'month'])['amount'].sum().sort_index()

        if len(monthly_totals) >= 2:
            last, prev = monthly_totals.iloc[-1], monthly_totals.iloc[-2]
            diff = last - prev
            pct_change = (diff / prev) * 100 if prev != 0 else 0
            trend = "increased" if pct_change > 0 else "decreased"
            base_insight = f"Your spending on {category.lower()} {trend} by {abs(pct_change):.1f}% this month compared to last."

            if use_llm:
                try:
                    prompt = f"Rewrite this financial insight more conversationally: '{base_insight}'"
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                    )
                    message = response["choices"][0]["message"]["content"].strip()
                    insights.append(message)
                except Exception as e:
                    insights.append(f"GPT error: {e}")
            else:
                insights.append(base_insight)

    # ----- 2. Highest spend category -----
    total_by_category = df.groupby('category')['amount'].sum()
    if not total_by_category.empty:
        top_category = total_by_category.idxmax()
        top_amount = total_by_category.max()
        insights.append(f"📌 You spent the most on {top_category.lower()}: ₹{top_amount:.2f} in total.")

    # ----- 3. Average monthly spend -----
    monthly_total = df.groupby(['year', 'month'])['amount'].sum()
    if not monthly_total.empty:
        avg_spend = monthly_total.mean()
        insights.append(f"📊 Your average monthly spending is ₹{avg_spend:.2f}.")

    # ----- 4. High spend alerts -----
    high_spends = df[df['amount'] > spend_alert_threshold]
    for _, row in high_spends.iterrows():
        insights.append(
            f"🚨 High spend alert: ₹{row['amount']} on {row['category']} ({row['description']}) on {row['date'].date()}"
        )

    if not insights:
        insights.append("No insights could be generated. Try uploading more transactions.")

    return insights
