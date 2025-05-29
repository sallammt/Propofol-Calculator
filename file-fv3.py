import streamlit as st  
import numpy as np  
from scipy.integrate import odeint  
import pandas as pd  
import matplotlib.pyplot as plt  
  
st.set_page_config(page_title="Propofol Infusion Calculator", layout="centered")  
st.title("Propofol Infusion Calculator (Paedfusor Model)")  
  
st.markdown("""  
Enter the patient’s weight and desired bolus dose. The calculator will recommend an infusion rate to achieve a target effect-site concentration (Ce) of 1.2–1.4 mcg/mL, and show you the expected concentration curves and key time points.  
""")  
  
# User input  
weight = st.number_input("Patient weight (kg)", min_value=5.0, max_value=100.0, value=20.0, step=0.5)  
bolus_dose = st.number_input("Bolus dose (mg/kg)", min_value=0.5, max_value=3.0, value=2.0, step=0.1)  
  
def calculate_propofol_infusion_flexible(weight, bolus_dose):  
    target_ce_min = 1.2  
    target_ce_max = 1.4  
    V1 = 0.458 * weight  
    V2 = 0.308 * weight  
    V3 = 0.789 * weight  
    CL1 = 0.119 * weight  
    CL2 = 0.112 * weight  
    CL3 = 0.042 * weight  
    ke0 = 0.152  
    k10 = CL1 / V1  
    k12 = CL2 / V1  
    k21 = CL2 / V2  
    k13 = CL3 / V1  
    k31 = CL3 / V3  
    def pk_model(y, t, infusion_rate):  
        A1, A2, A3, Ae = y  
        infusion_mcg_per_min = infusion_rate * 1000  
        dA1dt = -(k10 + k12 + k13) * A1 + k21 * A2 + k31 * A3 + infusion_mcg_per_min  
        dA2dt = k12 * A1 - k21 * A2  
        dA3dt = k13 * A1 - k31 * A3  
        dAedt = ke0 * A1 - ke0 * Ae  
        return [dA1dt, dA2dt, dA3dt, dAedt]  
    bolus_mcg = bolus_dose * weight * 1000  
    initial_conditions = [bolus_mcg, 0, 0, 0]  
    time_points = np.linspace(0, 120, 1201)  
    infusion_rates_mgkg_h = np.arange(3, 15, 0.1)  
    best_rate = None  
    best_score = float('inf')  
    for rate_mgkg_h in infusion_rates_mgkg_h:  
        rate_mg_per_min = rate_mgkg_h * weight / 60  
        sol = odeint(pk_model, initial_conditions, time_points, args=(rate_mg_per_min,))  
        Ce = sol[:, 3] / (V1 * 1000)  
        Ce_steady = Ce[time_points > 10]  
        mean_Ce = np.mean(Ce_steady)  
        if target_ce_min <= mean_Ce <= target_ce_max:  
            score = abs(mean_Ce - (target_ce_min + target_ce_max) / 2)  
            if score < best_score:  
                best_score = score  
                best_rate = rate_mgkg_h  
    if best_rate is not None:  
        rate_mg_per_min = best_rate * weight / 60  
        sol = odeint(pk_model, initial_conditions, time_points, args=(rate_mg_per_min,))  
        C1 = sol[:, 0] / (V1 * 1000)  
        Ce = sol[:, 3] / (V1 * 1000)  
        exceed_indices = np.where(Ce > target_ce_max)[0]  
        if len(exceed_indices) > 0:  
            exceed_time = time_points[exceed_indices[0]]  
            warning = f"Ce will exceed {target_ce_max} mcg/mL at approximately {round(exceed_time, 1)} minutes."  
            reduction_warning = f"Consider reducing the infusion rate at {round(exceed_time, 1)} minutes to prevent overshooting the target."  
        else:  
            exceed_time = None  
            warning = f"Ce does not exceed the upper target ({target_ce_max} mcg/mL) in the first 2 hours."  
            reduction_warning = "No infusion rate reduction needed in the first 2 hours."  
        reach_indices = np.where(Ce >= target_ce_min)[0]  
        if len(reach_indices) > 0:  
            reach_time = time_points[reach_indices[0]]  
            reach_info = f"Ce reaches the lower target ({target_ce_min} mcg/mL) at {round(reach_time, 1)} minutes."  
        else:  
            reach_time = None  
            reach_info = "Ce does not reach the lower target in the first 2 hours."  
        Ce_steady = Ce[time_points > 10]  
        mean_Ce = np.mean(Ce_steady)  
        results = {  
            'weight': weight,  
            'bolus_dose_mgkg': bolus_dose,  
            'bolus_dose_mg': bolus_dose * weight,  
            'infusion_rate_mgkg_h': round(best_rate, 1),  
            'total_infusion_rate_mg_h': round(best_rate * weight, 1),  
            'infusion_rate_mg_min': round(best_rate * weight / 60, 2),  
            'expected_ce': round(mean_Ce, 2),  
            'target_range': f"{target_ce_min}-{target_ce_max}",  
            'exceed_time': exceed_time,  
            'reach_time': reach_time,  
            'warning': warning,  
            'reduction_warning': reduction_warning,  
            'reach_info': reach_info,  
            'C1_curve': C1,  
            'Ce_curve': Ce,  
            'time_points': time_points,  
            'success': True  
        }  
    else:  
        results = {  
            'weight': weight,  
            'bolus_dose_mgkg': bolus_dose,  
            'success': False,  
            'error': 'No suitable infusion rate found'  
        }  
    return results  
  
if st.button("Calculate"):  
    result = calculate_propofol_infusion_flexible(weight, bolus_dose)  
    if result['success']:  
        st.subheader("Summary")  
        st.write(f"**Weight:** {result['weight']} kg")  
        st.write(f"**Bolus dose:** {result['bolus_dose_mgkg']} mg/kg ({result['bolus_dose_mg']} mg)")  
        st.write(f"**Recommended infusion rate:** {result['infusion_rate_mgkg_h']} mg/kg/h ({result['total_infusion_rate_mg_h']} mg/h, {result['infusion_rate_mg_min']} mg/min)")  
        st.write(f"**Expected steady-state Ce:** {result['expected_ce']} mcg/mL (target: {result['target_range']} mcg/mL)")  
        st.write(result['reach_info'])  
        st.write(result['warning'])  
        st.write(result['reduction_warning'])  
  
        # Plot  
        fig, ax = plt.subplots(2, 1, figsize=(8, 8))  
        ax[0].plot(result['time_points'], result['C1_curve'], label='Plasma (C1)', color='blue')  
        ax[0].plot(result['time_points'], result['Ce_curve'], label='Effect-site (Ce)', color='red')  
        ax[0].axhline(1.2, color='green', linestyle='--', alpha=0.7, label='Lower target')  
        ax[0].axhline(1.4, color='orange', linestyle='--', alpha=0.7, label='Upper target')  
        if result['reach_time'] is not None:  
            ax[0].axvline(result['reach_time'], color='green', linestyle=':', alpha=0.5)  
        if result['exceed_time'] is not None:  
            ax[0].axvline(result['exceed_time'], color='orange', linestyle=':', alpha=0.5)  
        ax[0].set_xlabel('Time (minutes)')  
        ax[0].set_ylabel('Concentration (mcg/mL)')  
        ax[0].set_title('Propofol Concentrations vs Time')  
        ax[0].legend()  
        ax[0].grid(True, alpha=0.3)  
        ax[0].set_xlim(0, 60)  
  
        # Zoomed view  
        time_mask = result['time_points'] <= 20  
        ax[1].plot(result['time_points'][time_mask], result['C1_curve'][time_mask], label='Plasma (C1)', color='blue')  
        ax[1].plot(result['time_points'][time_mask], result['Ce_curve'][time_mask], label='Effect-site (Ce)', color='red')  
        ax[1].axhline(1.2, color='green', linestyle='--', alpha=0.7, label='Lower target')  
        ax[1].axhline(1.4, color='orange', linestyle='--', alpha=0.7, label='Upper target')  
        if result['reach_time'] is not None and result['reach_time'] <= 20:  
            ax[1].axvline(result['reach_time'], color='green', linestyle=':', alpha=0.5)  
        ax[1].set_xlabel('Time (minutes)')  
        ax[1].set_ylabel('Concentration (mcg/mL)')  
        ax[1].set_title('First 20 Minutes (Detailed View)')  
        ax[1].legend()  
        ax[1].grid(True, alpha=0.3)  
        ax[1].set_xlim(0, 20)  
        plt.tight_layout()  
        st.pyplot(fig)  
  
        # Table  
        key_times = [0.5, 1, 2, 3, 5, 10, 15, 20, 30, 45, 60, 90, 120]  
        key_indices = [np.abs(result['time_points'] - t).argmin() for t in key_times]  
        concentration_table = pd.DataFrame({  
            'Time (min)': key_times,  
            'Plasma C1 (mcg/mL)': [round(result['C1_curve'][i], 2) for i in key_indices],  
            'Effect-site Ce (mcg/mL)': [round(result['Ce_curve'][i], 2) for i in key_indices]  
        })  
        st.subheader("Key Time Points")  
        st.dataframe(concentration_table)  
    else:  
        st.error(result['error'])  