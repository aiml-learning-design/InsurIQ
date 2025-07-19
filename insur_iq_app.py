import streamlit as st
from langgraph_app import app  # Our compiled workflow
import pandas as pd
import plotly.express as px

# App title
st.title("InsurIQ - AI-Powered Underwriting")

# Input form
with st.form("underwriting_form"):
    st.subheader("Property Information")

    col1, col2 = st.columns(2)
    with col1:
        property_id = st.text_input("Property ID")
        property_type = st.selectbox("Property Type", ["Residential", "Commercial", "Industrial"])
        address = st.text_area("Address")

    with col2:
        construction_type = st.selectbox("Construction Type", ["Wood", "Concrete", "Steel"])
        year_built = st.number_input("Year Built", min_value=1800, max_value=2025)
        floors = st.number_input("Number of Floors", min_value=1, max_value=100)

    # File upload for document processing
    uploaded_files = st.file_uploader("Upload supporting documents", accept_multiple_files=True)

    submitted = st.form_submit_button("Submit for Underwriting")

if submitted:
    # Prepare inputs
    inputs = {
        "property_id": property_id,
        "property_type": property_type,
        "address": address,
        "construction_type": construction_type,
        "year_built": year_built,
        "floors": floors,
        "documents": [doc.read() for doc in uploaded_files]
    }

    # Run the workflow
    with st.spinner("Processing underwriting request..."):
        result = app.invoke({"inputs": inputs})

        # Display results
        st.success("Underwriting Complete!")

        # Score visualization
        st.subheader("Risk Assessment")
        risk_df = pd.DataFrame.from_dict(result["risk_scores"], orient="index", columns=["Score"])
        fig = px.bar(risk_df, y="Score", title="Risk Scores Breakdown")
        st.plotly_chart(fig)

        # NATCAT score gauge
        st.metric("NATCAT Score", f"{result['natcat_score']}/100",
                  delta_color="inverse" if result['natcat_score'] > 50 else "normal")

        # Decision
        st.subheader("Underwriting Decision")
        decision = result["decision"]
        if decision["status"] == "STP":
            st.success("✅ Straight Through Processing (STP) Eligible")
        else:
            st.warning("⚠️ Requires Manual Underwriting Review")

        # Full report
        with st.expander("View Detailed Report"):
            st.write(result["report"])

        # Download option
        st.download_button("Download Report", result["report"], file_name=f"{property_id}_report.txt")