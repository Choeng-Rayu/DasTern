# app.py
import streamlit as st
import torch
from healthcare_lnp import HealthcarePredictor, MedicalDataProcessor
import pandas as pd

st.set_page_config(
    page_title="Healthcare LNP AI Assistant",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .prediction-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .risk-high { color: #d32f2f; font-weight: bold; }
    .risk-medium { color: #f57c00; font-weight: bold; }
    .risk-low { color: #388e3c; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    """Load the healthcare model"""
    try:
        predictor = HealthcarePredictor('healthcare_lnp_model.pth')
        return predictor
    except:
        st.warning("Model not found. Please train the model first using healthcare_lnp.py")
        return None

def main():
    st.title("🏥 Healthcare LNP AI Assistant")
    st.markdown("### Language Neural Processing for Medical Diagnosis and Treatment")
    
    # Sidebar
    with st.sidebar:
        st.header("Model Information")
        st.info("This AI model assists in disease prediction, medication suggestion, and risk assessment based on patient medical records.")
        
        st.header("Settings")
        confidence_threshold = st.slider("Confidence Threshold", 0.5, 1.0, 0.7)
        
        st.header("Common Disease Categories")
        for code, name in MedicalDataProcessor.DISEASE_CATEGORIES.items():
            st.text(f"{code}: {name}")
    
    # Load model
    predictor = load_model()
    
    if predictor is None:
        st.error("Please train the model first by running healthcare_lnp.py")
        return
    
    # Main interface
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Patient Assessment", 
        "📊 Data Analysis", 
        "💊 Medication Guide",
        "📈 Model Training"
    ])
    
    with tab1:
        st.header("Patient Medical Record Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Enter Patient Information")
            
            # Patient demographics
            age = st.number_input("Age", min_value=0, max_value=120, value=45)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            
            # Symptoms
            symptoms = st.multiselect(
                "Symptoms",
                ["Fever", "Cough", "Chest Pain", "Shortness of Breath", 
                 "Headache", "Fatigue", "Nausea", "Dizziness", 
                 "Joint Pain", "Rash", "Abdominal Pain", "Vomiting"],
                default=["Fever", "Cough"]
            )
            
            # Medical history
            history = st.text_area("Medical History", 
                                 "Hypertension for 5 years, Type 2 Diabetes")
            
            # Vital signs
            with st.expander("Vital Signs"):
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    bp_sys = st.number_input("Systolic BP", 80, 200, 120)
                    hr = st.number_input("Heart Rate", 40, 180, 75)
                with col_v2:
                    bp_dia = st.number_input("Diastolic BP", 50, 130, 80)
                    temp = st.number_input("Temperature (°C)", 35.0, 42.0, 36.6)
            
            # Current medications
            medications = st.text_area("Current Medications", "Metformin 500mg, Lisinopril 10mg")
        
        with col2:
            st.subheader("Clinical Notes")
            clinical_notes = st.text_area(
                "Enter detailed clinical notes:",
                height=300,
                value=f"""{age} year old {gender.lower()} presenting with {', '.join(symptoms)}.
Medical History: {history}
Current Medications: {medications}
Vital Signs: BP {bp_sys}/{bp_dia}, HR {hr}, Temp {temp}°C.
Physical Examination: {st.text_input("Physical Exam Findings", "Unremarkable")}
Laboratory Findings: {st.text_input("Lab Results", "Pending")}"""
            )
        
        # Analyze button
        if st.button("🔍 Analyze Medical Record", type="primary", use_container_width=True):
            with st.spinner("Analyzing medical record..."):
                result = predictor.predict(clinical_notes)
                
                # Display results
                st.success("Analysis Complete!")
                
                col_r1, col_r2, col_r3 = st.columns(3)
                
                with col_r1:
                    st.metric(
                        "Predicted Condition",
                        result['disease_prediction'],
                        f"Confidence: {result['disease_confidence']:.2%}"
                    )
                
                with col_r2:
                    risk_color = "risk-high" if result['risk_score'] > 0.7 else "risk-medium" if result['risk_score'] > 0.3 else "risk-low"
                    st.metric(
                        "Risk Assessment",
                        f"{result['risk_score']:.2%}",
                        result['severity_assessment']
                    )
                
                with col_r3:
                    st.metric(
                        "Severity",
                        result['severity_assessment'],
                        "Level"
                    )
                
                # Detailed results
                with st.expander("📋 Detailed Analysis", expanded=True):
                    st.subheader("Suggested Treatment Plan")
                    
                    # Medications
                    st.markdown("**💊 Recommended Medications:**")
                    for med in result['suggested_medications'][:5]:
                        st.markdown(f"- {med}")
                    
                    # Symptoms identified
                    st.markdown("**🔍 Identified Symptoms:**")
                    for symptom in result['symptoms_identified'][:5]:
                        st.markdown(f"- {symptom}")
                    
                    # Recommendations
                    st.markdown("**📋 Clinical Recommendations:**")
                    recommendations = [
                        "Follow up in 7 days",
                        "Monitor vital signs regularly",
                        "Consider additional lab tests",
                        "Patient education on medication adherence"
                    ]
                    for rec in recommendations:
                        st.markdown(f"- {rec}")
    
    with tab2:
        st.header("Medical Data Analysis")
        
        # Generate sample data
        if st.button("Generate Sample Medical Data"):
            with st.spinner("Generating data..."):
                df = MedicalDataProcessor.create_sample_data(500)
                st.dataframe(df.head(10))
                
                # Show statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Records", len(df))
                with col2:
                    st.metric("Disease Categories", df['disease_category'].nunique())
                with col3:
                    st.metric("Avg Age", f"{df['age'].mean():.1f}")
                
                # Disease distribution
                st.subheader("Disease Category Distribution")
                disease_dist = df['disease_category'].value_counts().sort_index()
                st.bar_chart(disease_dist)
    
    with tab3:
        st.header("Medication Information Guide")
        
        # Search medications
        search_term = st.text_input("Search Medications", placeholder="Enter medication name...")
        
        # Display medication information
        medication_data = {
            "Medication": MedicalDataProcessor.COMMON_MEDICATIONS,
            "Category": ["Antiplatelet", "Antidiabetic", "ACE Inhibitor", "Statin", 
                        "Thyroid", "Calcium Blocker", "Beta Blocker", "Bronchodilator",
                        "PPI", "ARB", "Statin", "Diuretic", "Antibiotic", "Steroid",
                        "Anticonvulsant", "Antidepressant", "Anticoagulant", "Insulin",
                        "Diuretic", "NSAID"],
            "Common Uses": [
                "Prevents blood clots, pain relief",
                "Type 2 diabetes management",
                "Hypertension, heart failure",
                "Lowers cholesterol",
                "Thyroid hormone replacement",
                "Hypertension, angina",
                "Hypertension, heart conditions",
                "Asthma, COPD",
                "GERD, ulcer treatment",
                "Hypertension",
                "Lowers cholesterol",
                "Hypertension, edema",
                "Bacterial infections",
                "Inflammation, autoimmune",
                "Neuropathic pain, seizures",
                "Depression, anxiety",
                "Blood thinner",
                "Diabetes management",
                "Edema, hypertension",
                "Pain, inflammation"
            ]
        }
        
        df_meds = pd.DataFrame(medication_data)
        
        if search_term:
            df_meds = df_meds[df_meds['Medication'].str.contains(search_term, case=False)]
        
        st.dataframe(df_meds, use_container_width=True)
    
    with tab4:
        st.header("Model Training Interface")
        
        st.info("To train the model with your own data, modify and run healthcare_lnp.py")
        
        st.code("""
# To train with custom data:
# 1. Prepare your medical data in CSV format with columns:
#    - text: Medical record text
#    - disease_category: Numerical disease code
#    - other relevant features

# 2. Modify the create_sample_data() function to load your data

# 3. Run the training:
#    python healthcare_lnp.py
        """, language="python")
        
        # Upload training data
        uploaded_file = st.file_uploader("Upload Medical Data (CSV)", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write(f"Uploaded {len(df)} records")
            st.dataframe(df.head())
            
            if st.button("Start Training with Uploaded Data"):
                st.warning("Training functionality requires running the healthcare_lnp.py script directly.")
                st.info("Please run: python healthcare_lnp.py --data_path your_data.csv")

if __name__ == "__main__":
    main()