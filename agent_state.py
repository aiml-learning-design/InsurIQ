from langgraph.graph import Graph
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import HumanMessage

# Define agent states
class AgentState(TypedDict):
    inputs: dict  # Raw input data
    extracted_data: dict  # Processed structured data
    risk_scores: dict  # Individual risk scores
    natcat_score: float  # Final composite score
    decision: dict  # Underwriting decision
    report: str  # Final report

# Create the workflow
workflow = Graph()

# Define nodes
@workflow.add_node
def input_processing(state: AgentState) -> AgentState:
    """Process raw inputs and extract structured data"""
    # Use LLM with RAG to extract fields from documents/emails
    extracted = {
        "address": "...",
        "construction_type": "...",
        "year_built": "...",
        # etc.
    }
    return {"extracted_data": extracted}

@workflow.add_node
def geocoding(state: AgentState) -> AgentState:
    """Convert address to geospatial coordinates"""
    # Use Snowflake function or Google Maps API
    return {"extracted_data": {**state["extracted_data"], "lat": ..., "lon": ...}}

@workflow.add_node
def fire_risk_assessment(state: AgentState) -> AgentState:
    """Calculate fire risk score"""
    # Call APIs and calculate score (0-5)
    return {"risk_scores": {"fire": 3.2}}

# Add all other risk agents similarly...

@workflow.add_node
def natcat_aggregation(state: AgentState) -> AgentState:
    """Calculate composite NATCAT score"""
    weights = {
        "flood": 0.3,
        "windstorm": 0.25,
        # etc.
    }
    score = sum(state["risk_scores"][k]*v for k,v in weights.items())
    return {"natcat_score": score}

@workflow.add_node
def decision_engine(state: AgentState) -> AgentState:
    """Make underwriting decision"""
    decision = "STP" if state["natcat_score"] < 50 else "Referred"
    return {"decision": {"status": decision, "reason": "..."}}

@workflow.add_node
def report_generation(state: AgentState) -> AgentState:
    """Generate final report with LLM"""
    # Use RAG to pull relevant guidelines
    report = f"""
    NATCAT Score: {state['natcat_score']}
    Risk Breakdown:
    - Fire: {state['risk_scores']['fire']}
    - Flood: {state['risk_scores']['flood']}
    ...
    Decision: {state['decision']['status']}
    """
    return {"report": report}

# Define edges
workflow.add_edge("input_processing", "geocoding")
workflow.add_edge("geocoding", "fire_risk_assessment")
# Add all other edges...

# Set entry and exit points
workflow.set_entry_point("input_processing")
workflow.set_exit_point("report_generation")

# Compile the workflow
app = workflow.compile()