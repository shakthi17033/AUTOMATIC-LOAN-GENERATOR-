import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="AI Loan Evaluation System", layout="wide")

# -----------------------------
# STYLE
# -----------------------------

st.markdown("""
<style>

body{
background-color:#eef2ff;
}

.title{
font-size:42px;
font-weight:bold;
text-align:center;
color:#1f4cff;
}

.box{
background:white;
padding:20px;
border-radius:10px;
box-shadow:0px 0px 10px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">🏦 Autonomous Loan Evaluation System</p>', unsafe_allow_html=True)

# -----------------------------
# INPUT SECTION
# -----------------------------

st.subheader("Applicant Information")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Applicant Name")
    age = st.slider("Age",18,65)
    income = st.number_input("Monthly Income",0)

with col2:
    credit = st.slider("Credit Score",300,900)
    loan = st.number_input("Loan Amount Requested",0)
    existing_loans = st.slider("Existing Loans",0,5)

employment = st.selectbox(
"Employment Type",
["Salaried","Self Employed","Student","Business"]
)

# -----------------------------
# AGENTS
# -----------------------------

def eligibility_agent(income, credit):
    score = 0

    if income > 50000:
        score += 40
    elif income > 30000:
        score += 25
    else:
        score += 10

    if credit > 750:
        score += 40
    elif credit > 650:
        score += 25
    else:
        score += 10

    return score


def risk_agent(score, existing_loans):

    if existing_loans >= 3:
        score -= 20

    if score > 70:
        return "Low Risk"
    elif score > 40:
        return "Medium Risk"
    else:
        return "High Risk"


def decision_agent(risk):

    if risk == "Low Risk":
        return "Approved"
    elif risk == "Medium Risk":
        return "Conditional Approval"
    else:
        return "Rejected"


def explanation_agent(risk, decision):

    if risk == "Low Risk":
        return "Applicant has strong financial indicators and low credit risk."

    if risk == "Medium Risk":
        return "Applicant has moderate financial stability. Conditional approval recommended."

    if risk == "High Risk":
        return "Applicant financial risk is high. Loan should not be approved."


# -----------------------------
# BUTTON
# -----------------------------

if st.button("Evaluate Loan Application"):

    score = eligibility_agent(income, credit)
    risk = risk_agent(score, existing_loans)
    decision = decision_agent(risk)
    explanation = explanation_agent(risk, decision)

    st.subheader("Loan Evaluation Dashboard")

    c1, c2, c3 = st.columns(3)

    c1.metric("Eligibility Score", score)
    c2.metric("Risk Category", risk)
    c3.metric("Decision", decision)

# -----------------------------
# CHARTS
# -----------------------------

    st.subheader("Risk Analytics")

    data = pd.DataFrame({
        "Factors":[
        "Income Stability",
        "Credit Strength",
        "Loan Burden",
        "Financial Reliability"
        ],

        "Score":[
        min(income/1000,100),
        credit/9,
        max(100-existing_loans*20,20),
        score
        ]
    })

    st.bar_chart(data.set_index("Factors"))

# -----------------------------
# AGENT WORKFLOW
# -----------------------------

    st.subheader("Agent Workflow")

    st.info("""
Application Input

⬇

Eligibility Agent → Calculates financial eligibility

⬇

Risk Assessment Agent → Determines applicant risk

⬇

Loan Decision Agent → Approves or rejects loan

⬇

Explanation Agent → Generates reasoning
""")

# -----------------------------
# AI EXPLANATION
# -----------------------------

    st.subheader("AI Explanation")

    st.success(explanation)
