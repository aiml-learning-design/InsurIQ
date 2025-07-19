# InsurIQ
- InsurIQ: AI-Powered House Insurance Underwriting System
- A smart, location-aware underwriting tool combining natural hazard analysis and property data for insurance decisions.

# InsurIQ - AI-Powered House Insurance Underwriting System

## Table of Contents
1. [Objectives](#objectives)
2. [System Architecture](#system-architecture)
3. [Component Flow](#component-flow)
4. [Data Flow](#data-flow)
5. [Tech Stack](#tech-stack)
6. [Component Responsibilities](#component-responsibilities)
7. [Future Enhancements](#future-enhancements)
8. [Getting Started](#getting-started)
9. [License](#license)

## Objectives <a name="objectives"></a>
InsurIQ is designed to:
- Automate property insurance underwriting using AI agents
- Provide comprehensive natural catastrophe (NATCAT) risk assessment
- Reduce manual underwriting workload through STP (Straight Through Processing)
- Improve risk assessment accuracy with multi-factor analysis
- Generate explainable underwriting decisions with audit trails
- Integrate with existing insurance systems and data sources



## InsurIQ Architecture

```mermaid
graph TD
%% UI Layer
    A[Streamlit UI\n- Underwriter Dashboard\n- Risk Visualization\n- Report Generation]

%% API Layer
    B[API Gateway\n FastAPI \n- Authentication\n- Request Routing\n- Rate Limiting]

%% Orchestration
C[LangGraph Orchestration Engine\n- Workflow Management\n- Agent Coordination\n- Error Handling]

%% Agent Groups
D[Input Processing Agents\n- Data Extraction\n- Validation\n- Geocoding]
E[Risk Agents\n- Fire Risk\n- Flood Risk\n- Windstorm\n- Earthquake]
F[Decision Agents\n- NATCAT Scoring\n- STP Rules\n- Premium Calc]
G[Reporting Agents\n- PDF Generation\n- Visualization\n- Audit Logs]

%% Data Layer
H[Data Sources\n- Snowflake DB\n- Document Storage\n- CRM Integrations]
I[External APIs\n- FEMA Flood\n- USGS Seismic\n- NOAA Weather]
J[Rules Engine\n- Underwriting Rules\n- Compliance Checks\n- Rate Tables]
K[Visualization Tools\n- Plotly\n- Matplotlib\n- Tableau Connector]

%% Connections
A --> B
B --> C
C --> D
C --> E
C --> F
C --> G
D --> H
E --> I
F --> J
G --> K
```










## System Architecture <a name="system-architecture"></a>
```mermaid
graph TD
    A[Streamlit UI] --> B[FastAPI Gateway]
    B --> C[LangGraph Orchestrator]
    C --> D[Input Processing Agents]
    C --> E[Risk Assessment Agents]
    C --> F[Decision Engine Agents]
    D --> G[Data Sources]
    E --> H[External APIs]
    F --> I[Business Rules]
```

```graph LR
A[Structured Data] --> B[Fire Risk]
A --> C[Flood Risk]
A --> D[Windstorm Risk]
A --> E[Earthquake Risk]
A --> F[Construction Risk]
A --> G[Claims Analysis]
```

## data flow

```aiignore
UI → API → Orchestrator → Agents → Data Sources → Analysis → Decisions → Reports → UI
```

```aiignore
flowchart LR
    RawInput -->|Extract| StructuredData
    StructuredData -->|Enrich| RiskScores
    RiskScores -->|Analyze| UnderwritingDecision
    UnderwritingDecision -->|Generate| Reports
```

## Tech Stack <a name="tech-stack"></a>

| Category          | Technologies                          |
|-------------------|---------------------------------------|
| Core Framework    | Python 3.10, LangGraph, LangChain     |
| UI                | Streamlit                             |
| API Layer         | FastAPI                               |
| Data Processing   | Pandas, NumPy                         |
| Visualization     | Plotly, Matplotlib                    |
| Vector Database   | FAISS                                 |
| LLM Integration   | OpenAI GPT-4                          |
| External APIs     | FEMA, USGS, NOAA                      |
| Data Storage      | Snowflake                             |

## Component Responsibilities <a name="component-responsibilities"></a>

### Input Processing Agents

| Agent            | Responsibility                          |
|------------------|----------------------------------------|
| ReadInput        | Extract data from various sources      |
| AddressGeocoder  | Convert addresses to coordinates       |
| DataValidator    | Verify input completeness              |

### Risk Assessment Agents

| Agent            | Risk Factors Evaluated                 |
|------------------|----------------------------------------|
| FireRisk         | Fire station proximity, wildfire       |
| FloodRisk        | FEMA zones, basement presence          |
| WindstormRisk    | Hurricane, tornado, hail               |
| EarthquakeRisk   | Seismic activity, soil type            |
| ConstructionRisk | Building materials, year built         |

## Future Enhancements <a name="future-enhancements"></a>

### Immediate Priorities
- [ ] Integration with more property data providers
- [ ] Mobile-friendly underwriter dashboard
- [ ] Automated document processing for PDFs/images

### Long-Term Roadmap (12+ months)
- [ ] IoT device integration for real-time monitoring
- [ ] Climate change impact modeling
- [ ] Blockchain-based policy management


### Getting Started
```aiignore
git clone https://github.com/yourorg/insuriq.git
cd insuriq
pip install -r requirements.txt
streamlit run insur_iq_app.py
```