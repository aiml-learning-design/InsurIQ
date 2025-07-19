# main.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, Dict
from pydantic import BaseModel
from enum import Enum
import logging
import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

# Configuration
class Config:
    """Central configuration for InsurIQ system"""
    API_KEYS = {
        "FEMA": os.getenv("FEMA_API_KEY", ""),
        "ATTOM": os.getenv("ATTOM_API_KEY", ""),
        "HAZARDHUB": os.getenv("HAZARDHUB_TOKEN", ""),
        "SNOWFLAKE": os.getenv("SNOWFLAKE_PASSWORD", "")
    }

    RISK_WEIGHTS = {
        "fire": 0.25,
        "flood": 0.30,
        "windstorm": 0.20,
        "earthquake": 0.10,
        "construction": 0.10,
        "claims": 0.05
    }


    SNOWFLAKE_CONFIG = {
        # "user": os.getenv("SNOWFLAKE_USER", ""),
        # "password": API_KEYS["SNOWFLAKE"],
        # "account": os.getenv("SNOWFLAKE_ACCOUNT", ""),
        # "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", ""),
        # "database": os.getenv("SNOWFLAKE_DATABASE", ""),
        # "schema": os.getenv("SNOWFLAKE_SCHEMA", "")
        "user": "",
        "password": "",
        "account": "",
        "warehouse": "",
        "database": "",
        "schema": ""
    }

    RISK_WEIGHTS = {
        "fire": 0.25,
        "flood": 0.30,
        "windstorm": 0.20,
        "earthquake": 0.10,
        "construction": 0.10,
        "claims": 0.05
    }

    @classmethod
    def validate(cls):
        pass
        # missing = [k for k, v in cls.API_KEYS.items() if not v]
        # if missing:
        #     logger.warning(f"Missing API keys for: {', '.join(missing)}")

Config.validate()

# Data Models
class RiskType(str, Enum):
    FIRE = "fire"
    FLOOD = "flood"
    WINDSTORM = "windstorm"
    EARTHQUAKE = "earthquake"
    CONSTRUCTION = "construction"
    CLAIMS = "claims"

class RiskAssessmentResult(BaseModel):
    score: float  # Risk score between 0-5
    confidence: float  # Confidence score between 0-1
    factors: Dict[str, float]  # Contributing factors to the score
    raw_data: Dict  # Raw API response data

class AgentState(TypedDict):
    inputs: dict  # Raw input data
    extracted_data: dict  # Processed structured data
    risk_scores: dict  # Individual risk scores
    natcat_score: float  # Final composite score
    decision: dict  # Underwriting decision
    report: str  # Final report

# Risk API Client
class RiskAPIs:
    """Central class for all external risk assessment API integrations"""
    def __init__(self, snowflake_config: Dict):
        pass
       # self.sf_conn = None  # Initialize as None
        # Only attempt connection if config has values
        # if all(snowflake_config.values()):
        #     try:
        #         self.sf_conn = snowflake.connector.connect(**snowflake_config)
        #     except Exception as e:
        #         logger.warning(f"Snowflake connection failed: {e}")
        #
        # self.api_config = {
        #     "hazardhub": {"url": "https://api.hazardhub.com/v1/risks"},
        #     "fema": {"url": "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/28/query"},
        #     "attom": {"url": "https://api.attomdata.com/propertyapi/v1.0.0/property/detail"},
        #     "usgs": {"url": "https://earthquake.usgs.gov/ws/designmaps/asce7-16.json"},
        #     "overpass": {"url": "https://overpass-api.de/api/interpreter"}
        # }


    def get_flood_risk(self, lat: float, lon: float, has_basement: bool) -> Optional[RiskAssessmentResult]:
        try:
            # TODO: Implement actual FEMA API call
            # Example implementation (commented out):
            """
            response = requests.get(
                self.api_config["fema"]["url"],
                params={
                    "geometry": f"{lon},{lat}",
                    "geometryType": "esriGeometryPoint",
                    "inSR": "4326",
                    "f": "json"
                },
                headers={"X-API-KEY": Config.API_KEYS["FEMA"]}
            )
            data = response.json()
            zone = data["features"][0]["attributes"]["FLD_ZONE"] if data["features"] else "X"
            zone_score = {"VE":5, "AE":4, "A":3, "X":1, "D":2}.get(zone, 1)
            """

            # Current mock implementation
            zone_score = 3.0
            basement_penalty = 1.5 if has_basement else 1.0
            return RiskAssessmentResult(
                score=min(zone_score * basement_penalty, 5),
                confidence=0.85,
                factors={
                    "flood_zone": "AE",  # Mock value
                    "basement_penalty": basement_penalty
                },
                raw_data={}  # Would contain actual API response
            )
        except Exception as e:
            logger.error(f"Flood risk assessment failed: {e}")
            return None

    def get_fire_risk(self, lat: float, lon: float, construction_type: str) -> Optional[RiskAssessmentResult]:
        try:
            # TODO: Implement actual HazardHub/Google Maps API calls for:
            # - Fire station proximity
            # - Wildfire risk data

            # Current mock implementation
            distance = 2.5
            wildfire_score = 3.2
            construction_factor = self._get_construction_factor(construction_type)
            composite_score = (distance * 0.4 + wildfire_score * 0.4) * construction_factor

            return RiskAssessmentResult(
                score=min(composite_score, 5),
                confidence=0.9,
                factors={
                    "fire_station_distance_km": distance,
                    "wildfire_score": wildfire_score,
                    "construction_factor": construction_factor
                },
                raw_data={"stations": [], "wildfire": {}}  # Would contain actual API responses
            )
        except Exception as e:
            logger.error(f"Fire risk assessment failed: {e}")
            return None

    def get_windstorm_risk(self, lat: float, lon: float) -> Optional[RiskAssessmentResult]:
        try:
            # TODO: Implement actual HazardHub API call for windstorm data
            # Would fetch hurricane, tornado, and hail risk scores

            # Current mock implementation
            return RiskAssessmentResult(
                score=3.0,
                confidence=0.8,
                factors={
                    "hurricane": 2.5,
                    "tornado": 3.0,
                    "hail": 1.5
                },
                raw_data={}  # Would contain actual API response
            )
        except Exception as e:
            logger.error(f"Windstorm risk assessment failed: {e}")
            return None

    def get_earthquake_risk(self, lat: float, lon: float) -> Optional[RiskAssessmentResult]:
        try:
            # TODO: Implement actual USGS API call for seismic data
            # Would fetch PGA (Peak Ground Acceleration) values

            # Current mock implementation
            return RiskAssessmentResult(
                score=1.5,
                confidence=0.75,
                factors={"pga": 0.3},  # Mock PGA value
                raw_data={}  # Would contain actual API response
            )
        except Exception as e:
            logger.error(f"Earthquake risk assessment failed: {e}")
            return None

    def get_construction_risk(self, address: str) -> Optional[RiskAssessmentResult]:
        try:
            # TODO: Implement actual ATTOM API call for property details
            # Would fetch roof condition, year built, etc.

            # Current mock implementation
            return RiskAssessmentResult(
                score=2.0,
                confidence=0.7,
                factors={
                    "roof_condition": "Fair",  # Mock value
                    "year_built": 1990  # Mock value
                },
                raw_data={}  # Would contain actual API response
            )
        except Exception as e:
            logger.error(f"Construction risk assessment failed: {e}")
            return None

    def get_claims_risk(self, lat: float, lon: float) -> Optional[RiskAssessmentResult]:
        try:
            # TODO: Implement actual Snowflake query for historical claims data
            # Example implementation (commented out):
            """
            cur = self.sf_conn.cursor()
            cur.execute(f'''
                SELECT COUNT(*) as claim_count
                FROM claims_history 
                WHERE ST_DISTANCE(
                    ST_MAKEPOINT({lon}, {lat}),
                    ST_MAKEPOINT(longitude, latitude)
                ) <= 5000  # 5km radius
                AND claim_date > DATEADD(year, -5, CURRENT_DATE())
            ''')
            claim_count = cur.fetchone()[0]
            """

            # Current mock implementation
            claim_count = 2  # Mock value
            return RiskAssessmentResult(
                score=min(claim_count, 5),  # Cap score at 5
                confidence=0.9,
                factors={"nearby_claims": claim_count},
                raw_data={"claim_count": claim_count}  # Would contain actual query results
            )
        except Exception as e:
            logger.error(f"Claims risk assessment failed: {e}")
            return None

    def _get_construction_factor(self, construction_type: str) -> float:
        # This is a fixed mapping, no API call needed
        return {
            "wood": 1.2, "concrete": 0.8, "steel": 0.7,
            "masonry": 1.0, "unknown": 1.1
        }.get(construction_type.lower(), 1.0)

# RAG System Setup
# def setup_rag():
#     """Mock RAG setup for demo purposes"""
#     try:
#         from langchain_core.documents import Document
#         from langchain_community.embeddings.fake import FakeEmbeddings
#
#         # Create mock document
#         docs = [Document(page_content="Standard underwriting guidelines apply.")]
#
#         # Use fake embeddings to avoid external dependencies
#         embeddings = FakeEmbeddings(size=384)
#
#         # Create vector store
#         from langchain_community.vectorstores import FAISS
#         vectorstore = FAISS.from_documents(docs, embeddings)
#         return vectorstore.as_retriever()
#     except Exception as e:
#         logger.error(f"RAG setup failed: {e}")
#         # Fallback to simple mock retriever
#         from langchain_core.retrievers import BaseRetriever
#         from langchain_core.documents import Document
#         class MockRetriever(BaseRetriever):
#             def _get_relevant_documents(self, query):
#                 return [Document(page_content="Mock guideline response")]
#         return MockRetriever()

def setup_rag():
    from langchain_core.documents import Document
    from langchain_core.retrievers import BaseRetriever

    class MockRetriever(BaseRetriever):
        def _get_relevant_documents(self, query):
            return [Document(
                page_content="Standard underwriting guidelines:\n" +
                             "1. Properties in flood zones require additional inspection\n" +
                             "2. Wood construction gets 20% higher risk factor\n" +
                             "3. Buildings older than 30 years need structural review"
            )]

    return MockRetriever()


guidelines_retriever = setup_rag()

def get_relevant_guidelines(query):
    docs = guidelines_retriever.get_relevant_documents(query)
    return "\n\n".join(doc.page_content for doc in docs)

# Workflow Definition

workflow = StateGraph(AgentState)

# Instantiate RiskAPIs once and reuse
risk_client = RiskAPIs(Config.SNOWFLAKE_CONFIG)

#@workflow.add_node
def input_processing(state: AgentState) -> AgentState:
    inputs = state["inputs"]
    extracted = {
        "address": inputs["address"],
        "construction_type": inputs["construction_type"],
        "year_built": inputs["year_built"],
        "floors": inputs["floors"],
        "has_basement": True,
        "lat": 34.0522,  # Mock coordinates (Los Angeles)
        "lon": -118.2437
    }
    return {"extracted_data": extracted}
#workflow.add_node("input_processing", input_processing)

#@workflow.add_node
def geocoding(state: AgentState) -> AgentState:
    return {"extracted_data": {**state["extracted_data"], "lat": 34.0522, "lon": -118.2437}}
#workflow.add_node("geocoding", geocoding)


#@workflow.add_node
def fire_risk_assessment(state: AgentState) -> AgentState:
    data = state["extracted_data"]
    result = risk_client.get_fire_risk(data["lat"], data["lon"], data["construction_type"])
    return {"risk_scores": {"fire": result.score if result else 0}}
#workflow.add_node("fire_risk_assessment", fire_risk_assessment)

#@workflow.add_node
def flood_risk_assessment(state: AgentState) -> AgentState:
    data = state["extracted_data"]
    result = risk_client.get_flood_risk(data["lat"], data["lon"], data.get("has_basement", False))
    return {"risk_scores": {"flood": result.score if result else 0}}
#workflow.add_node("flood_risk_assessment", flood_risk_assessment)

#@workflow.add_node
def windstorm_risk_assessment(state: AgentState) -> AgentState:
    data = state["extracted_data"]
    result = risk_client.get_windstorm_risk(data["lat"], data["lon"])
    return {"risk_scores": {"windstorm": result.score if result else 0}}
#workflow.add_node("windstorm_risk_assessment", windstorm_risk_assessment)

#@workflow.add_node
def natcat_aggregation(state: AgentState) -> AgentState:
    weights = Config.RISK_WEIGHTS
    score = sum(state["risk_scores"].get(k, 0)*v for k,v in weights.items()) * 20  # Scale 0-100
    return {"natcat_score": score}
#workflow.add_node("natcat_aggregation", natcat_aggregation)

#@workflow.add_node
def decision_engine(state: AgentState) -> AgentState:
    decision = "STP" if state["natcat_score"] < 50 else "Referred"
    return {"decision": {"status": decision, "reason": "Based on composite risk score"}}
#workflow.add_node("decision_engine", decision_engine)

#@workflow.add_node
def report_generation(state: AgentState) -> AgentState:
    guidelines = get_relevant_guidelines("Property underwriting guidelines")
   # workflow.add_node("report_generation", report_generation)
    report = f"""
NATCAT Score: {state['natcat_score']:.1f}/100
Risk Breakdown:
- Fire: {state['risk_scores'].get('fire', 0):.1f}/5
- Flood: {state['risk_scores'].get('flood', 0):.1f}/5
- Windstorm: {state['risk_scores'].get('windstorm', 0):.1f}/5

Underwriting Decision: {state['decision']['status']}
Reason: {state['decision']['reason']}

Guidelines Reference:
{guidelines}
"""
    return {"report": report}

# Workflow Definition
# 3. Build the Graph
# ------------------------------

#workflow = StateGraph(AgentState)




workflow.add_node("input_processing", input_processing)
workflow.add_node("geocoding", geocoding)
workflow.add_node("fire_risk_assessment", fire_risk_assessment)
workflow.add_node("flood_risk_assessment", flood_risk_assessment)
workflow.add_node("windstorm_risk_assessment", windstorm_risk_assessment)
workflow.add_node("natcat_aggregation", natcat_aggregation)
workflow.add_node("decision_engine", decision_engine)
workflow.add_node("report_generation", report_generation)


# ------------------------------
# 4. Define Edges
# ------------------------------

workflow.set_entry_point("input_processing")

# workflow.add_edge("input_processing", "geocoding")
# workflow.add_edge("geocoding", "risk_assessment")
# workflow.add_edge("risk_assessment", "weather_fetch")
# workflow.add_edge("weather_fetch", "fetch_property_details")
# workflow.add_edge("fetch_property_details", "fetch_snowflake_data")
# workflow.add_edge("fetch_snowflake_data", "report_generation")
# workflow.add_edge("report_generation", END)

workflow.add_edge("input_processing", "geocoding")
workflow.add_edge("geocoding", "fire_risk_assessment")
workflow.add_edge("fire_risk_assessment", "windstorm_risk_assessment")
workflow.add_edge("windstorm_risk_assessment", "flood_risk_assessment")
workflow.add_edge("flood_risk_assessment", "natcat_aggregation")
workflow.add_edge("natcat_aggregation", "decision_engine")
workflow.add_edge("decision_engine", "report_generation")
workflow.add_edge("report_generation", END)
#workflow.set_finish_point("report_generation")
app = workflow.compile()

# Streamlit UI
def main():
    st.title("InsurIQ - AI-Powered Underwriting")

    with st.form("underwriting_form"):
        st.subheader("Property Information")
        col1, col2 = st.columns(2)
        with col1:
            property_id = st.text_input("Property ID", "PROP-123")
            property_type = st.selectbox("Property Type", ["Residential", "Commercial", "Industrial"])
            address = st.text_area("Address", "123 Main St, Los Angeles, CA")
        with col2:
            construction_type = st.selectbox("Construction Type", ["Wood", "Concrete", "Steel"])
            year_built = st.number_input("Year Built", min_value=1800, max_value=2025, value=1990)
            floors = st.number_input("Number of Floors", min_value=1, max_value=100, value=2)

        submitted = st.form_submit_button("Submit for Underwriting")

    if submitted:
        inputs = {
            "property_id": property_id,
            "property_type": property_type,
            "address": address,
            "construction_type": construction_type,
            "year_built": year_built,
            "floors": floors
        }

        with st.spinner("Processing underwriting request..."):
            result = app.invoke({"inputs": inputs})

            st.success("Underwriting Complete!")

            st.subheader("Risk Assessment")
            risk_df = pd.DataFrame.from_dict(result["risk_scores"], orient="index", columns=["Score"])
            st.bar_chart(risk_df)

            st.metric("NATCAT Score", f"{result['natcat_score']:.1f}/100",
                      delta_color="inverse" if result['natcat_score'] > 50 else "normal")

            st.subheader("Underwriting Decision")
            if result["decision"]["status"] == "STP":
                st.success("✅ Straight Through Processing (STP) Eligible")
            else:
                st.warning("⚠️ Requires Manual Underwriting Review")

            with st.expander("View Detailed Report"):
                st.write(result["report"])

if __name__ == "__main__":
    main()