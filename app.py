import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Bank Loan Decision System", layout="wide")

# -------------------------------------------------
# STYLE
# -------------------------------------------------

st.markdown("""
<style>
.title{
font-size:40px;
font-weight:bold;
text-align:center;
color:#1d4ed8;
}

.block{
background-color:#f8fafc;
padding:20px;
border-radius:10px;
margin-bottom:20px;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">🏦 Autonomous Bank Loan Decision System</p>', unsafe_allow_html=True)

st.write("This system simulates **real banking loan evaluation using an agentic workflow**.")

# -------------------------------------------------
# APPLICATION INTAKE AGENT
# -------------------------------------------------

st.header("Loan Application Form")

col1, col2 = st.columns(2)

with col1:

    name = st.text_input("Applicant Name")
    age = st.slider("Age",18,65)
    income = st.number_input("Monthly Income (₹)",0)
    employment = st.selectbox(
        "Employment Type",
        ["Salaried","Self Employed","Business","Student"]
    )

with col2:

    credit_score = st.slider("Credit Score",300,900)
    loan_amount = st.number_input("Loan Amount Requested (₹)",0)
    tenure = st.slider("Loan Tenure (Years)",1,30)
    existing_emi = st.number_input("Existing Monthly EMI (₹)",0)

# -------------------------------------------------
# BANK CALCULATIONS
# -------------------------------------------------

def calculate_emi(P,r,n):

    r = r/(12*100)
    n = n*12

    if P == 0:
        return 0

    emi = P*r*(1+r)**n/((1+r)**n-1)

    return emi

def debt_to_income(total_emi,income):

    if income == 0:
        return 0

    return (total_emi/income)*100

def loan_to_income(loan_amount,income):

    if income == 0:
        return 0

    return loan_amount/(income*12)

# -------------------------------------------------
# ELIGIBILITY AGENT
# -------------------------------------------------

def eligibility_agent(age,income,credit_score):

    if age < 21:
        return False,"Applicant below eligible age"

    if income < 20000:
        return False,"Income below bank minimum threshold"

    if credit_score < 600:
        return False,"Credit score below bank requirement"

    return True,"Applicant passes basic eligibility"

# -------------------------------------------------
# RISK AGENT
# -------------------------------------------------

def risk_agent(credit_score,dti,lti):

    score = 0

    if credit_score > 750:
        score += 40
    elif credit_score > 650:
        score += 25
    else:
        score += 10

    if dti < 30:
        score += 30
    elif dti < 45:
        score += 20
    else:
        score += 10

    if lti < 5:
        score += 30
    else:
        score += 10

    if score > 75:
        return "Low Risk",score
    elif score > 50:
        return "Medium Risk",score
    else:
        return "High Risk",score

# -------------------------------------------------
# DECISION AGENT
# -------------------------------------------------

def decision_agent(risk):

    if risk == "Low Risk":
        return "Loan Approved"

    elif risk == "Medium Risk":
        return "Conditional Approval"

    else:
        return "Loan Rejected"

# -------------------------------------------------
# EXPLANATION AGENT
# -------------------------------------------------

def explanation_agent(risk):

    if risk == "Low Risk":
        return "Applicant shows strong financial profile and repayment capability."

    if risk == "Medium Risk":
        return "Applicant has moderate financial risk. Bank may request guarantor."

    if risk == "High Risk":
        return "High financial risk due to credit profile or debt burden."

# -------------------------------------------------
# RUN WORKFLOW
# -------------------------------------------------

if st.button("Run Loan Evaluation Workflow"):

    interest_rate = 9

    emi = calculate_emi(loan_amount,interest_rate,tenure)

    total_emi = emi + existing_emi

    dti = debt_to_income(total_emi,income)

    lti = loan_to_income(loan_amount,income)

    eligible,message = eligibility_agent(age,income,credit_score)

    if not eligible:

        st.error("❌ Loan Rejected")
        st.write(message)

    else:

        risk,score = risk_agent(credit_score,dti,lti)

        decision = decision_agent(risk)

        explanation = explanation_agent(risk)

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

        st.header("Loan Evaluation Dashboard")

        c1,c2,c3,c4 = st.columns(4)

        c1.metric("Calculated EMI",f"₹{round(emi)}")
        c2.metric("Debt To Income Ratio",f"{round(dti)}%")
        c3.metric("Risk Score",score)
        c4.metric("Risk Category",risk)

# -------------------------------------------------
# FINAL DECISION
# -------------------------------------------------

        st.subheader("Final Bank Decision")

        if decision == "Loan Approved":

            st.success("✅ LOAN APPROVED")

        elif decision == "Conditional Approval":

            st.warning("⚠ CONDITIONAL APPROVAL")

        else:

            st.error("❌ LOAN REJECTED")

        st.write(explanation)

# -------------------------------------------------
# ANALYTICS
# -------------------------------------------------

        st.subheader("Risk Factor Analysis")

        df = pd.DataFrame({
            "Factors":[
                "Credit Score Strength",
                "Debt Burden",
                "Loan Exposure"
            ],
            "Score":[
                credit_score/9,
                100-dti,
                max(100-lti*10,10)
            ]
        })

        st.bar_chart(df.set_index("Factors"))

# -------------------------------------------------
# AGENT WORKFLOW
# -------------------------------------------------

        st.subheader("Agent Workflow")

        st.info("""
Application Intake Agent  
⬇  
Eligibility Check Agent  
⬇  
Risk Assessment Agent  
⬇  
Decision Agent  
⬇  
Explanation Agent  
""")

# -------------------------------------------------
# REPORT
# -------------------------------------------------

        st.subheader("Loan Evaluation Report")

        st.write("Applicant:",name)
        st.write("Income:",income)
        st.write("Credit Score:",credit_score)
        st.write("Loan Amount:",loan_amount)
        st.write("Loan Tenure:",tenure,"years")
        st.write("Calculated EMI:",round(emi))
        st.write("Debt-To-Income:",round(dti),"%")
        st.write("Loan-To-Income:",round(lti,2))
        st.write("Risk Category:",risk)
        st.write("Final Decision:",decision)
