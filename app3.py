import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------
# PAGE CONFIG
# -----------------------------------------

st.set_page_config(
    page_title="Bank Retention Intelligence Dashboard",
    layout="wide"
)

st.title("🏦 Customer Engagement & Product Utilization Analytics")
st.markdown(
"""
This dashboard evaluates customer engagement, product utilization,
and financial commitment to identify retention drivers and churn risks.
"""
)

# -----------------------------------------
# LOAD DATA
# -----------------------------------------

df = pd.read_csv("European_Bank.csv")

# -----------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------

st.sidebar.header("Dashboard Controls")

engagement_filter = st.sidebar.selectbox(
    "Customer Engagement",
    ["All", "Active", "Inactive"]
)

product_slider = st.sidebar.slider(
    "Product Count",
    int(df["NumOfProducts"].min()),
    int(df["NumOfProducts"].max()),
    (1,4)
)

balance_threshold = st.sidebar.slider(
    "Balance Threshold",
    int(df["Balance"].min()),
    int(df["Balance"].max()),
    int(df["Balance"].quantile(0.75))
)

salary_threshold = st.sidebar.slider(
    "Salary Threshold",
    int(df["EstimatedSalary"].min()),
    int(df["EstimatedSalary"].max()),
    int(df["EstimatedSalary"].quantile(0.75))
)

# -----------------------------------------
# APPLY FILTERS
# -----------------------------------------

filtered_df = df.copy()

if engagement_filter == "Active":
    filtered_df = filtered_df[filtered_df["IsActiveMember"] == 1]

elif engagement_filter == "Inactive":
    filtered_df = filtered_df[filtered_df["IsActiveMember"] == 0]

filtered_df = filtered_df[
    filtered_df["NumOfProducts"].between(product_slider[0], product_slider[1])
]

# -----------------------------------------
# KPI METRICS
# -----------------------------------------

total_customers = filtered_df.shape[0]
churn_rate = filtered_df["Exited"].mean() * 100
avg_balance = filtered_df["Balance"].mean()
avg_products = filtered_df["NumOfProducts"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Customers", total_customers)
col2.metric("Churn Rate", f"{churn_rate:.2f}%")
col3.metric("Average Balance", f"${avg_balance:,.0f}")
col4.metric("Avg Products", f"{avg_products:.2f}")

st.divider()

# -----------------------------------------
# MODULE 1 : ENGAGEMENT VS CHURN
# -----------------------------------------

st.header("📊 Engagement vs Churn Overview")

engagement_churn = filtered_df.groupby("IsActiveMember")["Exited"].mean().reset_index()

fig1 = px.bar(
    engagement_churn,
    x="IsActiveMember",
    y="Exited",
    color="IsActiveMember",
    labels={"IsActiveMember":"Active Member", "Exited":"Churn Rate"},
    title="Churn Rate by Engagement Level"
)

fig1.update_yaxes(tickformat=".0%")

st.plotly_chart(fig1, use_container_width=True)

st.divider()

# -----------------------------------------
# MODULE 2 : PRODUCT UTILIZATION
# -----------------------------------------

st.header("📦 Product Utilization Impact Analysis")

product_churn = filtered_df.groupby("NumOfProducts")["Exited"].mean().reset_index()

fig2 = px.bar(
    product_churn,
    x="NumOfProducts",
    y="Exited",
    color="NumOfProducts",
    title="Churn Rate by Number of Products"
)

fig2.update_xaxes(
    tickmode="linear",
    dtick=1
)

fig2.update_yaxes(tickformat=".0%")

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# -----------------------------------------
# MODULE 3 : HIGH VALUE DISENGAGED DETECTOR
# -----------------------------------------

st.header("⚠ High-Value Disengaged Customer Detector")

high_value = filtered_df[
    (filtered_df["Balance"] > balance_threshold) &
    (filtered_df["EstimatedSalary"] > salary_threshold) &
    (filtered_df["IsActiveMember"] == 0)
]

st.metric("High Value Disengaged Customers", high_value.shape[0])

st.dataframe(high_value.head(10))

st.divider()

# -----------------------------------------
# MODULE 4 : RELATIONSHIP STRENGTH
# -----------------------------------------

st.header("💪 Retention Strength Scoring Panel")

filtered_df["RelationshipScore"] = (
    filtered_df["IsActiveMember"]*2 +
    filtered_df["NumOfProducts"] +
    filtered_df["HasCrCard"]
)

relationship = filtered_df.groupby("RelationshipScore")["Exited"].mean().reset_index()

fig3 = px.line(
    relationship,
    x="RelationshipScore",
    y="Exited",
    markers=True,
    title="Churn Rate by Relationship Strength"
)

fig3.update_xaxes(
    tickmode="linear",
    dtick=1
)

fig3.update_yaxes(tickformat=".0%")

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# -----------------------------------------
# DATA PREVIEW
# -----------------------------------------

st.subheader("Filtered Dataset Preview")

st.dataframe(filtered_df.head(20))