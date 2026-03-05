import streamlit as st
import json
import time
from dotenv import load_dotenv
import os

# LLM
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

# -----------------------------
# Initialize LLM
# -----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=OPENAI_API_KEY
)

st.set_page_config(page_title="AI Grant Proposal Generator", layout="wide")

# =========================================================
# AGENTS
# =========================================================

def guideline_extraction_agent(text):

    prompt = f"""
    Extract grant constraints from the following funding call.

    Return JSON with:
    max_budget
    mandatory_sections
    evaluation_weights

    Funding Call:
    {text}
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        return json.loads(response.content)
    except:
        return {
            "max_budget": 5000000,
            "mandatory_sections": ["Objectives","Methodology","Impact"],
            "evaluation_weights":{
                "Innovation":30,
                "Feasibility":25,
                "Impact":25,
                "Team":20
            }
        }


def proposal_drafting_agent(project_info):

    prompt = f"""
    Write a structured research grant proposal.

    Project Title: {project_info['title']}
    Problem: {project_info['problem']}
    Methodology: {project_info['methodology']}
    Impact: {project_info['impact']}

    Sections:
    Abstract
    Objectives
    Methodology
    Impact

    Return JSON.
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        return json.loads(response.content)
    except:
        return {"Draft": response.content}


def budget_agent(duration):

    budget = {
        "Equipment": 1500000,
        "Personnel": 2000000,
        "Travel": 500000,
        "Contingency": 500000
    }

    timeline = []
    for i in range(1, duration+1):
        timeline.append(f"Month {i}: Development Phase")

    return budget, timeline


def evaluation_agent(proposal):

    proposal_text = json.dumps(proposal)

    prompt = f"""
    Evaluate this grant proposal.

    Score each category out of 25.

    Categories:
    Innovation
    Feasibility
    Impact
    Clarity

    Return JSON:

    {{
    "total_score": number,
    "weaknesses":[]
    }}

    Proposal:
    {proposal_text}
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        return json.loads(response.content)
    except:
        return {"total_score":70,"weaknesses":["Needs clearer methodology"]}


def refinement_agent(proposal, weaknesses):

    proposal_text = json.dumps(proposal)

    prompt = f"""
    Improve the proposal based on these weaknesses:

    Weaknesses:
    {weaknesses}

    Proposal:
    {proposal_text}

    Return improved proposal JSON.
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        return json.loads(response.content)
    except:
        return proposal


# =========================================================
# UI
# =========================================================

st.title("🎓 AI Research Grant Proposal Generator & Evaluator")
st.write("Agentic System: Generate → Evaluate → Improve")

# Sidebar
st.sidebar.header("⚙ Settings")
iterations = st.sidebar.slider("Max Iterations",1,5,3)
target_score = st.sidebar.slider("Target Score",60,100,85)

# Upload guidelines
st.header("📂 Upload Funding Guidelines")

uploaded_file = st.file_uploader("Upload PDF or Text",type=["txt"])

guideline_text = ""

if uploaded_file:
    guideline_text = uploaded_file.read().decode("utf-8")
    st.success("Guidelines uploaded")

# Project inputs
st.header("🧪 Project Details")

title = st.text_input("Project Title")
problem = st.text_area("Problem Statement")
methodology = st.text_area("Proposed Methodology")
impact = st.text_area("Expected Impact")

duration = st.number_input(
    "Project Duration (Months)",
    min_value=1,
    max_value=36,
    value=12
)

# Run system
if st.button("🚀 Run Autonomous Proposal System"):

    if not title or not problem:
        st.warning("Please fill project details")
        st.stop()

    project_info = {
        "title":title,
        "problem":problem,
        "methodology":methodology,
        "impact":impact
    }

    # --------------------------------
    # Step 1 Guideline Agent
    # --------------------------------

    with st.spinner("Extracting grant constraints..."):
        constraints = guideline_extraction_agent(guideline_text)

    # --------------------------------
    # Step 2 Draft Proposal
    # --------------------------------

    with st.spinner("Generating proposal draft..."):
        proposal = proposal_drafting_agent(project_info)

    # --------------------------------
    # Step 3 Budget Agent
    # --------------------------------

    budget,timeline = budget_agent(duration)

    history=[]

    # --------------------------------
    # Iterative Loop
    # --------------------------------

    for i in range(iterations):

        with st.spinner(f"Evaluating proposal (Iteration {i+1})..."):

            result = evaluation_agent(proposal)

        score = result["total_score"]
        weaknesses = result["weaknesses"]

        history.append({
            "iteration":i+1,
            "score":score,
            "weaknesses":weaknesses
        })

        if score >= target_score:
            break

        with st.spinner("Refining proposal..."):
            proposal = refinement_agent(proposal,weaknesses)

    st.success("Process completed")

    # =====================================================
    # DISPLAY RESULTS
    # =====================================================

    col1,col2 = st.columns(2)

    with col1:

        st.subheader("📄 Final Proposal")

        for k,v in proposal.items():
            st.markdown(f"### {k}")
            st.write(v)

    with col2:

        st.subheader("💰 Budget")

        total=0
        for k,v in budget.items():
            st.write(f"{k}: ₹{v}")
            total+=v

        st.write(f"**Total Budget: ₹{total}**")

        st.subheader("📅 Timeline")

        for t in timeline[:6]:
            st.write(t)

        if len(timeline)>6:
            st.write("...")

    st.subheader("📊 Evaluation History")

    for h in history:
        st.write(f"Iteration {h['iteration']} — Score: {h['score']}")
        st.write("Weaknesses:")
        for w in h["weaknesses"]:
            st.write("-",w)