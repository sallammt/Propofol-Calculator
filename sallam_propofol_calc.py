import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Sallam Propofol Calc",
    page_icon="💉",
    layout="wide"
)

def calculate_bsa(weight_kg, height_cm):
    """Calculate Body Surface Area using Mosteller formula"""
    return np.sqrt((height_cm * weight_kg) / 3600)

def calculate_bolus_dose(age_months, bsa_m2):
    """Calculate bolus dose using the Sallam formula"""
    return 0.75 + 0.14 * age_months + 45.82 * bsa_m2

# Header
st.title("🩺 Sallam Propofol Calc")
st.markdown("**Pediatric Propofol Bolus Dose Calculator**")
st.markdown("---")

# Sidebar for patient input
st.sidebar.header("📋 Patient Information")
st.sidebar.markdown("Enter patient details below:")

age_months = st.sidebar.number_input(
    "Age (months)", 
    min_value=0.0, 
    max_value=240.0, 
    value=1.0,
    step=0.1,
    help="Patient age in months"
)

weight_kg = st.sidebar.number_input(
    "Weight (kg)", 
    min_value=0.1, 
    max_value=200.0, 
    value=4.0,
    step=0.1,
    help="Patient weight in kilograms"
)

height_cm = st.sidebar.number_input(
    "Height (cm)", 
    min_value=10.0, 
    max_value=250.0, 
    value=52.0,
    step=0.1,
    help="Patient height in centimeters"
)

# Calculate BSA and bolus dose
bsa = calculate_bsa(weight_kg, height_cm)
bolus_dose = calculate_bolus_dose(age_months, bsa)
dose_per_kg = bolus_dose / weight_kg

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 Calculation Results")
    
    # Results metrics
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.metric(
            label="Bolus Dose",
            value=f"{bolus_dose:.2f} mg",
            help="Total recommended bolus dose"
        )
    
    with col_b:
        st.metric(
            label="Dose per kg",
            value=f"{dose_per_kg:.2f} mg/kg",
            help="Dose normalized by patient weight"
        )
    
    with col_c:
        st.metric(
            label="Body Surface Area",
            value=f"{bsa:.3f} m²",
            help="Calculated using Mosteller formula"
        )
    
    # Detailed breakdown
    st.subheader("🔍 Calculation Breakdown")
    
    breakdown_data = {
        "Component": [
            "Base dose",
            "Age component", 
            "BSA component",
            "**Total bolus dose**",
            "**Dose per kg**"
        ],
        "Formula": [
            "Fixed component",
            f"0.14 × {age_months}",
            f"45.82 × {bsa:.3f}",
            "0.75 + Age + BSA components",
            "Total dose ÷ weight"
        ],
        "Value": [
            "0.75 mg",
            f"{0.14 * age_months:.2f} mg",
            f"{45.82 * bsa:.2f} mg",
            f"**{bolus_dose:.2f} mg**",
            f"**{dose_per_kg:.2f} mg/kg**"
        ]
    }
    
    breakdown_df = pd.DataFrame(breakdown_data)
    st.table(breakdown_df)

with col2:
    st.header("⚠️ Safety Assessment")
    
    # Safety warnings
    if dose_per_kg > 3.0:
        st.error(f"🚨 HIGH DOSE WARNING\n\n{dose_per_kg:.2f} mg/kg exceeds typical range (1-3 mg/kg)\n\nConsider reducing dose or reassessing patient factors.")
    elif dose_per_kg < 1.0:
        st.warning(f"⚠️ LOW DOSE WARNING\n\n{dose_per_kg:.2f} mg/kg is below typical range (1-3 mg/kg)\n\nConsider patient-specific factors.")
    else:
        st.success(f"✅ DOSE WITHIN RANGE\n\n{dose_per_kg:.2f} mg/kg is within the typical safe range (1-3 mg/kg)")
    
    # Clinical considerations
    st.subheader("🏥 Clinical Notes")
    st.markdown("""
    **Consider:**
    - Patient ASA status
    - Comorbidities
    - Concurrent medications
    - Prematurity (if applicable)
    
    **Monitor for:**
    - Respiratory depression
    - Hypotension
    - Allergic reactions
    
    **Equipment ready:**
    - Bag-mask ventilation
    - Intubation supplies
    - Reversal agents
    """)

# Formula information
st.markdown("---")
st.subheader("📖 Formula Information")

col_formula1, col_formula2 = st.columns(2)

with col_formula1:
    st.markdown("""
    **Bolus Dose Formula:**
    ```
    Dose (mg) = 0.75 + 0.14 × age (months) + 45.82 × BSA (m²)
    ```
    """)

with col_formula2:
    st.markdown("""
    **BSA Formula (Mosteller):**
    ```
    BSA (m²) = √[(height(cm) × weight(kg)) / 3600]
    ```
    """)

# Footer
st.markdown("---")
st.markdown("*Sallam Propofol Calc - Pediatric Propofol Dosing Calculator*")
st.markdown("*Always verify calculations and consider individual patient factors*")
