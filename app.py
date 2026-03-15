import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from openai import OpenAI

# -------------------------
# OPENAI CLIENT
# -------------------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(page_title="AI Lending Intelligence Platform", layout="wide")

st.title("AI Lending Intelligence Platform")
st.caption("Borrower Risk • Cross-Sell Analytics • Portfolio Simulation")

# -------------------------
# NBFC CONFIG
# -------------------------

NBFC_CONFIG = {
"Bajaj Finance": {"commission":0.28,"attach_boost":0.05},
"Tata Capital": {"commission":0.25,"attach_boost":0.00},
"Mahindra Finance": {"commission":0.30,"attach_boost":0.03},
"Cholamandalam Finance": {"commission":0.27,"attach_boost":0.02},
"Poonawalla Fincorp": {"commission":0.24,"attach_boost":-0.02},
"HDFC Credila": {"commission":0.22,"attach_boost":0.04}
}

# -------------------------
# INPUT PANEL
# -------------------------

st.sidebar.header("Borrower Inputs")

nbfc = st.sidebar.selectbox("NBFC Partner",list(NBFC_CONFIG.keys()))

age = st.sidebar.slider("Age",21,60)

occupation = st.sidebar.selectbox(
"Occupation",
["Salaried","Self Employed","Gig Worker"]
)

loan_type = st.sidebar.selectbox(
"Loan Type",
["Personal Loan","Consumer Durable Loan","Home Loan","Business Loan"]
)

loan_amount = st.sidebar.number_input(
"Loan Amount ₹",
50000,
5000000,
step=50000
)

tenure = st.sidebar.slider("Tenure",1,15)

city = st.sidebar.selectbox(
"City Tier",
["Tier 1","Tier 2","Tier 3"]
)

# -------------------------
# RISK MODEL
# -------------------------

def risk_score():

    score = 3

    if loan_amount > 1000000:
        score += 2

    if occupation in ["Self Employed","Gig Worker"]:
        score += 2

    if tenure > 7:
        score += 1

    if city == "Tier 3":
        score += 1

    if age < 25:
        score += 1

    return min(score,10)

# -------------------------
# ATTACH MODEL
# -------------------------

BASE_ATTACH = {
"Personal Loan":0.45,
"Consumer Durable Loan":0.30,
"Business Loan":0.50,
"Home Loan":0.70
}

# -------------------------
# CALCULATIONS
# -------------------------

risk = risk_score()

attach = min(BASE_ATTACH[loan_type] + NBFC_CONFIG[nbfc]["attach_boost"],0.9)

premium_rate = 0.02
premium = loan_amount * premium_rate

expected_premium = premium * attach

commission = NBFC_CONFIG[nbfc]["commission"]

nbfc_revenue = expected_premium * commission
insurer_revenue = expected_premium * (1 - commission)

# -------------------------
# DASHBOARD
# -------------------------

st.header("Borrower Risk Dashboard")

c1,c2,c3,c4 = st.columns(4)

c1.metric("Risk Score",f"{risk}/10")

c2.metric("Attach Probability",f"{attach*100:.1f}%")

c3.metric("Premium",f"₹{premium:,.0f}")

c4.metric("Expected Premium",f"₹{expected_premium:,.0f}")

# -------------------------
# REVENUE SPLIT
# -------------------------

st.header("Revenue Split")

df_rev = pd.DataFrame({
"Entity":["NBFC","Insurer"],
"Revenue":[nbfc_revenue,insurer_revenue]
})

fig = px.pie(df_rev,names="Entity",values="Revenue",title="Revenue Split")

st.plotly_chart(fig,use_container_width=True)

# -------------------------
# WHY THIS RECOMMENDATION
# -------------------------

st.header("Why this recommendation?")

reasons = []

if loan_amount > 1000000:
    reasons.append("Higher loan amount increases protection demand")

if occupation in ["Self Employed","Gig Worker"]:
    reasons.append("Income volatility increases borrower risk")

if tenure > 7:
    reasons.append("Longer tenure increases need for protection")

if city == "Tier 3":
    reasons.append("Higher credit uncertainty in smaller markets")

for r in reasons:
    st.write("•",r)

# -------------------------
# PORTFOLIO SIMULATION
# -------------------------

st.header("Portfolio Simulation")

loans = 1000

portfolio_premium = premium * attach * loans
portfolio_nbfc = portfolio_premium * commission
portfolio_insurer = portfolio_premium * (1-commission)

c1,c2,c3 = st.columns(3)

c1.metric("Policies Sold",int(loans*attach))

c2.metric("NBFC Portfolio Revenue",f"₹{portfolio_nbfc:,.0f}")

c3.metric("Insurer Portfolio Revenue",f"₹{portfolio_insurer:,.0f}")

# -------------------------
# PORTFOLIO CHART
# -------------------------

df_portfolio = pd.DataFrame({
"Entity":["NBFC","Insurer"],
"Revenue":[portfolio_nbfc,portfolio_insurer]
})

fig2 = px.bar(df_portfolio,x="Entity",y="Revenue",title="Portfolio Revenue")

st.plotly_chart(fig2,use_container_width=True)

# -------------------------
# CSV UPLOAD
# -------------------------

st.header("Batch Borrower Scoring")

uploaded_file = st.file_uploader("Upload borrower CSV")

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.write("Preview",df.head())

    st.write("Total Borrowers:",len(df))

# -------------------------
# AI STRATEGY INSIGHTS
# -------------------------

if st.button("Generate AI Strategy Insights"):

    prompt=f"""
Explain lending cross-sell strategy.

NBFC: {nbfc}
Borrower age: {age}
Occupation: {occupation}
Loan type: {loan_type}
Loan amount: {loan_amount}
Tenure: {tenure}
City tier: {city}

Risk score: {risk}
Attach probability: {attach}

Explain:
1 risk drivers
2 cross sell opportunity
3 product strategy
4 RM sales pitch
"""

    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role":"user","content":prompt}]
    )

    st.header("AI Strategy Insights")

    st.write(response.choices[0].message.content)