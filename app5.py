import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────

st.set_page_config(
    page_title="Bank Retention Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# PLOTLY CHART DEFAULTS
# ─────────────────────────────────────────

COLORS = {
    "blue":  "#2563EB",
    "red":   "#DC2626",
    "green": "#16A34A",
    "amber": "#D97706",
}

CHART_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="sans-serif", size=12),
    margin=dict(l=10, r=10, t=45, b=10),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="#E2E8F0"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

def apply_chart_style(fig):
    fig.update_layout(**CHART_LAYOUT)
    return fig

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────

@st.cache_data
def load_data():
    df = pd.read_csv("European_Bank.csv")
    df["AgeGroup"] = pd.cut(
        df["Age"],
        bins=[17, 30, 40, 50, 60, 100],
        labels=["18-30", "31-40", "41-50", "51-60", "60+"]
    )
    df["RelationshipScore"] = (
        df["IsActiveMember"] * 2 +
        df["NumOfProducts"] +
        df["HasCrCard"]
    )
    return df

df = load_data()

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────

st.sidebar.title("Dashboard Controls")
st.sidebar.markdown("---")

engagement_filter = st.sidebar.selectbox(
    "Customer Engagement",
    ["All Customers", "Active Only", "Inactive Only"]
)

geo_options = ["All"] + sorted(df["Geography"].unique().tolist())
geo_filter = st.sidebar.selectbox("Geography", geo_options)

gender_options = ["All"] + sorted(df["Gender"].unique().tolist())
gender_filter = st.sidebar.selectbox("Gender", gender_options)

st.sidebar.markdown("---")

product_slider = st.sidebar.slider(
    "Number of Products",
    int(df["NumOfProducts"].min()),
    int(df["NumOfProducts"].max()),
    (1, 4)
)

balance_threshold = st.sidebar.slider(
    " Balance Threshold ($)",
    int(df["Balance"].min()),
    int(df["Balance"].max()),
    int(df["Balance"].quantile(0.75)),
    step=1000,
    format="$%d"
)

salary_threshold = st.sidebar.slider(
    "Salary Threshold ($)",
    int(df["EstimatedSalary"].min()),
    int(df["EstimatedSalary"].max()),
    int(df["EstimatedSalary"].quantile(0.75)),
    step=1000,
    format="$%d"
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Dataset: European Bank  |  Total records: {len(df):,}")

# ─────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────

fdf = df.copy()

if engagement_filter == "Active Only":
    fdf = fdf[fdf["IsActiveMember"] == 1]
elif engagement_filter == "Inactive Only":
    fdf = fdf[fdf["IsActiveMember"] == 0]

if geo_filter != "All":
    fdf = fdf[fdf["Geography"] == geo_filter]

if gender_filter != "All":
    fdf = fdf[fdf["Gender"] == gender_filter]

fdf = fdf[fdf["NumOfProducts"].between(product_slider[0], product_slider[1])]

fdf["HighValueDisengaged"] = (
    (fdf["Balance"] > balance_threshold) &
    (fdf["EstimatedSalary"] > salary_threshold) &
    (fdf["IsActiveMember"] == 0)
)

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────

st.title("🏦 Bank Customer Retention Intelligence")
st.markdown(
    "Analyzing engagement, product utilization, and financial commitment "
    "to identify retention drivers and churn risks across the European Bank."
)
st.divider()

# ─────────────────────────────────────────
# KPI METRICS
# ─────────────────────────────────────────

total        = fdf.shape[0]
churn_rate   = fdf["Exited"].mean() * 100
active_rate  = fdf["IsActiveMember"].mean() * 100
avg_balance  = fdf["Balance"].mean()
avg_products = fdf["NumOfProducts"].mean()
hv_count     = int(fdf["HighValueDisengaged"].sum())

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Customers",  f"{total:,}")
k2.metric("Churn Rate",       f"{churn_rate:.1f}%")
k3.metric("Active Members",   f"{active_rate:.1f}%")
k4.metric("Avg Balance",      f"${avg_balance:,.0f}")
k5.metric("Avg Products",     f"{avg_products:.2f}")
k6.metric("At-Risk Premium",  f"{hv_count:,}")

st.divider()

# ─────────────────────────────────────────
# MODULE 1 · ENGAGEMENT VS CHURN
# ─────────────────────────────────────────

st.header("📊 Engagement vs Churn Overview")

st.info(
    "**Key Finding:** Inactive members churn at ~27% vs ~14% for active members — "
    "nearly 2x higher risk. Engagement status is the strongest binary predictor of churn in this dataset."
)

col1, col2 = st.columns(2)

with col1:
    eng = fdf.groupby("IsActiveMember")["Exited"].mean().reset_index()
    eng["Status"] = eng["IsActiveMember"].map({0: "Inactive", 1: "Active"})
    eng["Churn %"] = (eng["Exited"] * 100).round(1)

    fig1 = px.bar(
        eng,
        x="Status",
        y="Churn %",
        color="Status",
        color_discrete_map={"Active": COLORS["green"], "Inactive": COLORS["red"]},
        text=eng["Churn %"].map("{:.1f}%".format),
        title="Churn Rate: Active vs Inactive Members",
        labels={"Churn %": "Churn Rate (%)"}
    )
    fig1.update_traces(textposition="outside")
    fig1.update_yaxes(range=[0, 40], ticksuffix="%")
    fig1.update_layout(showlegend=False)
    apply_chart_style(fig1)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    geo_eng = fdf.groupby(["Geography", "IsActiveMember"])["Exited"].mean().reset_index()
    geo_eng["Status"]  = geo_eng["IsActiveMember"].map({0: "Inactive", 1: "Active"})
    geo_eng["Churn %"] = (geo_eng["Exited"] * 100).round(1)

    fig2 = px.bar(
        geo_eng,
        x="Geography",
        y="Churn %",
        color="Status",
        barmode="group",
        color_discrete_map={"Active": COLORS["blue"], "Inactive": COLORS["red"]},
        text=geo_eng["Churn %"].map("{:.1f}%".format),
        title="Churn Rate by Region & Engagement",
        labels={"Churn %": "Churn Rate (%)"}
    )
    fig2.update_traces(textposition="outside")
    fig2.update_yaxes(range=[0, 45], ticksuffix="%")
    apply_chart_style(fig2)
    st.plotly_chart(fig2, use_container_width=True)

age_eng = fdf.groupby(["AgeGroup", "IsActiveMember"])["Exited"].mean().reset_index()
age_eng["Status"] = age_eng["IsActiveMember"].map({0: "Inactive", 1: "Active"})

fig3 = px.line(
    age_eng,
    x="AgeGroup",
    y="Exited",
    color="Status",
    markers=True,
    color_discrete_map={"Active": COLORS["blue"], "Inactive": COLORS["red"]},
    title="Churn Rate by Age Group & Engagement Status",
    labels={"Exited": "Churn Rate", "AgeGroup": "Age Group"}
)
fig3.update_yaxes(tickformat=".0%")
apply_chart_style(fig3)
st.plotly_chart(fig3, use_container_width=True)

st.warning(
    "**Age Insight:** The 41–50 age group shows the sharpest churn spike — especially among inactive members. "
    "This cohort is the primary re-engagement target."
)

st.divider()

# ─────────────────────────────────────────
# MODULE 2 · PRODUCT UTILIZATION
# ─────────────────────────────────────────

st.header("📦 Product Utilization Impact Analysis")

st.info(
    "**Key Finding:** Customers with 2 products churn at only ~8% — the retention sweet spot. "
    "3–4 product holders churn at 83–100%, pointing to product-fit mismatch or over-selling."
)

col1, col2 = st.columns(2)

with col1:
    prod_churn = fdf.groupby("NumOfProducts").agg(
        ChurnRate=("Exited", "mean"),
        Count=("Exited", "count")
    ).reset_index()
    prod_churn["Churn %"]  = (prod_churn["ChurnRate"] * 100).round(1)
    prod_churn["Products"] = prod_churn["NumOfProducts"].astype(str)

    fig4 = px.bar(
        prod_churn,
        x="Products",
        y="Churn %",
        color="Churn %",
        color_continuous_scale=["#16A34A", "#D97706", "#DC2626"],
        text=prod_churn["Churn %"].map("{:.1f}%".format),
        title="Churn Rate by Number of Products",
        labels={"Churn %": "Churn Rate (%)", "Products": "No. of Products"}
    )
    fig4.update_traces(textposition="outside")
    fig4.update_yaxes(range=[0, 120], ticksuffix="%")
    fig4.update_coloraxes(showscale=False)
    apply_chart_style(fig4)
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    prod_dist = fdf.groupby(["NumOfProducts", "Exited"]).size().reset_index(name="Count")
    prod_dist["Status"]   = prod_dist["Exited"].map({0: "Retained", 1: "Churned"})
    prod_dist["Products"] = prod_dist["NumOfProducts"].astype(str)

    fig5 = px.bar(
        prod_dist,
        x="Products",
        y="Count",
        color="Status",
        barmode="stack",
        color_discrete_map={"Retained": COLORS["blue"], "Churned": COLORS["red"]},
        title="Customer Volume: Retained vs Churned by Product Count",
        labels={"Count": "Number of Customers", "Products": "No. of Products"}
    )
    apply_chart_style(fig5)
    st.plotly_chart(fig5, use_container_width=True)

geo_prod = fdf.groupby(["Geography", "NumOfProducts"])["Exited"].mean().reset_index()
geo_prod_pivot = geo_prod.pivot(index="Geography", columns="NumOfProducts", values="Exited")

fig6 = go.Figure(data=go.Heatmap(
    z=(geo_prod_pivot.values * 100).round(1),
    x=[f"{c} Product(s)" for c in geo_prod_pivot.columns],
    y=geo_prod_pivot.index.tolist(),
    colorscale=[[0, "#DCFCE7"], [0.5, "#FEF9C3"], [1.0, "#FEE2E2"]],
    text=np.round(geo_prod_pivot.values * 100, 1),
    texttemplate="%{text}%",
    textfont=dict(size=13),
    colorbar=dict(title="Churn %", ticksuffix="%")
))
fig6.update_layout(
    title="Churn Rate Heatmap: Geography x Product Count",
    **CHART_LAYOUT
)
st.plotly_chart(fig6, use_container_width=True)

st.error(
    "**Action Required:** Germany shows the highest churn rates across nearly all product tiers. "
    "A targeted retention campaign for German customers is strongly recommended."
)

st.divider()

# ─────────────────────────────────────────
# MODULE 3 · HIGH-VALUE DISENGAGED DETECTOR
# ─────────────────────────────────────────

st.header("⚠️ High-Value Disengaged Customer Detector")

st.info(
    f"**Risk Definition:** Customers with Balance > ${balance_threshold:,} AND "
    f"Salary > ${salary_threshold:,} AND Inactive.  \n"
    "This segment churns at ~30.5% vs ~18.9% for all others — a 61% relative uplift in churn probability."
)

hv_df  = fdf[fdf["HighValueDisengaged"]]
std_df = fdf[~fdf["HighValueDisengaged"]]

k1, k2, k3 = st.columns(3)
k1.metric(
    "High-Value Disengaged",
    f"{len(hv_df):,}",
    f"{len(hv_df)/max(len(fdf), 1)*100:.1f}% of filtered customers"
)
k2.metric(
    "Their Churn Rate",
    f"{hv_df['Exited'].mean()*100:.1f}%" if len(hv_df) > 0 else "N/A",
    "vs 18.9% baseline"
)
k3.metric(
    "Avg Balance (At-Risk)",
    f"${hv_df['Balance'].mean():,.0f}" if len(hv_df) > 0 else "N/A"
)

col1, col2 = st.columns(2)

with col1:
    seg_data = pd.DataFrame({
        "Segment":    ["High-Value Disengaged", "Standard Customers"],
        "Churn Rate": [
            hv_df["Exited"].mean() * 100 if len(hv_df) > 0 else 0,
            std_df["Exited"].mean() * 100 if len(std_df) > 0 else 0
        ]
    })

    fig7 = px.bar(
        seg_data,
        x="Segment",
        y="Churn Rate",
        color="Segment",
        color_discrete_map={
            "High-Value Disengaged": COLORS["red"],
            "Standard Customers":   COLORS["blue"]
        },
        text=seg_data["Churn Rate"].map("{:.1f}%".format),
        title="Churn Rate: At-Risk Segment vs Standard",
        labels={"Churn Rate": "Churn Rate (%)"}
    )
    fig7.update_traces(textposition="outside")
    fig7.update_yaxes(range=[0, 45], ticksuffix="%")
    fig7.update_layout(showlegend=False)
    apply_chart_style(fig7)
    st.plotly_chart(fig7, use_container_width=True)

with col2:
    if len(hv_df) > 0:
        geo_risk = hv_df.groupby("Geography").size().reset_index(name="Count")
        fig8 = px.pie(
            geo_risk,
            names="Geography",
            values="Count",
            title="High-Value Disengaged: Geographic Distribution",
            color_discrete_sequence=[COLORS["blue"], COLORS["amber"], COLORS["red"]]
        )
        fig8.update_traces(textinfo="label+percent")
        apply_chart_style(fig8)
        st.plotly_chart(fig8, use_container_width=True)
    else:
        st.info("No customers match current thresholds. Try lowering the sidebar sliders.")

st.subheader("Top At-Risk Premium Customers")
st.caption("Sorted by balance — inactive customers above both thresholds")

display_cols = ["CustomerId", "Geography", "Gender", "Age", "Tenure",
                "Balance", "NumOfProducts", "EstimatedSalary", "Exited"]
display_cols = [c for c in display_cols if c in fdf.columns]

if len(hv_df) > 0:
    risk_table = hv_df[display_cols].sort_values("Balance", ascending=False).head(15).copy()
    risk_table["Balance"]         = risk_table["Balance"].map("${:,.0f}".format)
    risk_table["EstimatedSalary"] = risk_table["EstimatedSalary"].map("${:,.0f}".format)
    risk_table["Exited"]          = risk_table["Exited"].map({0: "Retained", 1: "Churned"})
    st.dataframe(risk_table, use_container_width=True, hide_index=True)
else:
    st.info("No at-risk customers match the current filter criteria.")

st.divider()

# ─────────────────────────────────────────
# MODULE 4 · RETENTION STRENGTH SCORING
# ─────────────────────────────────────────

st.header("💪 Retention Strength Scoring Panel")

st.info(
    "**Scoring Formula:** `RelationshipScore = (IsActiveMember x 2) + NumOfProducts + HasCrCard`  \n"
    "Scores range 1–7. Scores 3–5 have the lowest churn (< 18%). "
    "Scores 6–7 spike due to inactive customers holding many products."
)

rel = fdf.groupby("RelationshipScore").agg(
    ChurnRate=("Exited", "mean"),
    Count=("Exited", "count")
).reset_index()
rel["Churn %"] = (rel["ChurnRate"] * 100).round(1)

col1, col2 = st.columns(2)

with col1:
    fig9 = px.line(
        rel,
        x="RelationshipScore",
        y="Churn %",
        markers=True,
        title="Churn Rate by Relationship Score",
        labels={"Churn %": "Churn Rate (%)", "RelationshipScore": "Relationship Score"}
    )
    fig9.update_traces(
        line=dict(color=COLORS["blue"], width=2.5),
        marker=dict(size=9, color=COLORS["blue"])
    )
    fig9.update_xaxes(tickmode="linear", dtick=1)
    fig9.update_yaxes(ticksuffix="%")
    apply_chart_style(fig9)
    st.plotly_chart(fig9, use_container_width=True)

with col2:
    score_dist = fdf.groupby(["RelationshipScore", "Exited"]).size().reset_index(name="Count")
    score_dist["Status"] = score_dist["Exited"].map({0: "Retained", 1: "Churned"})

    fig10 = px.bar(
        score_dist,
        x="RelationshipScore",
        y="Count",
        color="Status",
        barmode="stack",
        color_discrete_map={"Retained": COLORS["blue"], "Churned": COLORS["red"]},
        title="Customer Distribution by Relationship Score",
        labels={"Count": "Customers", "RelationshipScore": "Relationship Score"}
    )
    fig10.update_xaxes(tickmode="linear", dtick=1)
    apply_chart_style(fig10)
    st.plotly_chart(fig10, use_container_width=True)

st.subheader("Score Band Summary")

def score_band(s):
    if s <= 2:   return "🔴 High Risk"
    elif s <= 5: return "🟢 Safe Zone"
    else:        return "🟡 Watch List"

rel["Risk Band"]  = rel["RelationshipScore"].apply(score_band)
rel["Customers"]  = rel["Count"].map("{:,}".format)
rel["Churn Rate"] = rel["Churn %"].map("{:.1f}%".format)

summary = rel[["RelationshipScore", "Risk Band", "Churn Rate", "Customers"]].rename(
    columns={"RelationshipScore": "Score"}
)
st.dataframe(summary, use_container_width=True, hide_index=True)

st.warning(
    "**Retention Strategy:** Score 2–3 customers (high churn, large population) are the top candidates "
    "for re-engagement campaigns. Moving a customer from Score 2 to Score 4 reduces churn "
    "probability by approximately 15 percentage points."
)

st.divider()
st.caption(
    "Bank Customer Retention Intelligence "
)
