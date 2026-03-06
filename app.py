import streamlit as st
from transformers import pipeline

st.set_page_config(page_title="AI Loan Approval System", layout="centered")

st.title("🏦 AI Loan Approval System")
st.write("Enter your details to check if your loan will be approved.")

# -------------------------
# LOAD LLM
# -------------------------

llm = pipeline(
    "text2text-generation",
    model="google/flan-t5-small"
)

# -------------------------
# AGENT 1 - APPLICATION AGENT
# -------------------------

def application_agent(data):
    return data


# -------------------------
# AGENT 2 - ELIGIBILITY AGENT
# -------------------------

def eligibility_agent(age, income, credit_score):

    if age < 21:
        return False

    if income < 25000:
        return False

    if credit_score < 650:
        return False

    return True


# -------------------------
# AGENT 3 - RISK AGENT
# -------------------------

def risk_agent(income, existing_emi):

    if existing_emi > income * 0.5:
        return "High"

    elif existing_emi > income * 0.3:
        return "Medium"

    return "Low"


# -------------------------
# AGENT 4 - DECISION AGENT
# -------------------------

def decision_agent(eligible, risk, loan_amount, income):

    if not eligible:
        return "Rejected"

    if risk == "High":
        return "Rejected"

    if loan_amount > income * 60:
        return "Rejected"

    return "Approved"


# -------------------------
# AGENT 5 - LLM EXPLANATION AGENT
# -------------------------

def explanation_agent(decision):

    prompt = f"""
Explain briefly why a bank would {decision} a loan application.
"""

    result = llm(prompt, max_length=50)

    return result[0]["generated_text"]


# -------------------------
# USER INPUT
# -------------------------

name = st.text_input("Full Name")

age = st.slider("Age", 18, 65)

income = st.number_input("Monthly Income (₹)", 0)

credit_score = st.slider("Credit Score", 300, 900)

loan_amount = st.number_input("Loan Amount Requested (₹)", 0)

existing_emi = st.number_input("Existing Monthly EMI (₹)", 0)


# -------------------------
# BUTTON
# -------------------------

if st.button("Check Loan Approval"):

    data = {
        "name": name,
        "age": age,
        "income": income,
        "credit": credit_score
    }

    application = application_agent(data)

    eligible = eligibility_agent(age, income, credit_score)

    risk = risk_agent(income, existing_emi)

    decision = decision_agent(eligible, risk, loan_amount, income)

    explanation = explanation_agent(decision)

    st.header("Loan Decision")

    if decision == "Approved":
        st.success("✅ Loan Approved")
    else:
        st.error("❌ Loan Rejected")

    st.write("Explanation:", explanation)
