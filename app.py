import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# ==============================================================================
# 1. PAGE CONFIG & EXACT ORIGINAL KEYFRAME STYLING
# ==============================================================================
st.set_page_config(
    page_title="ATHLETE-IQ PERFORMANCE ENGINE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Original dark theme keyframe and CSS styling
st.markdown("""
<style>
    .stApp {
        background-color: #0b0e14;
        color: #e2e8f0;
    }
    
    .main-header {
        text-align: center;
        padding: 10px 0 20px 0;
    }
    .main-header h1 {
        color: #38bdf8;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: 1px;
        margin-bottom: 2px;
    }
    .main-header p {
        color: #c084fc;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0;
    }

    .gradient-banner {
        background: linear-gradient(90deg, #7c3aed 0%, #ec4899 100%);
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 10px;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 20px 0 15px 0;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25);
    }

    /* Metric box text overflow fix without layout distortion */
    div[data-testid="stMetricValue"] > div {
        font-size: 1.4rem !important;
        white-space: normal !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
    }
    div[data-testid="stMetricLabel"] > label {
        font-size: 0.88rem !important;
        color: #94a3b8 !important;
        white-space: normal !important;
    }

    .sub-norm {
        color: #64748b;
        font-size: 0.82rem;
        margin-top: -10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. HEADER
# ==============================================================================
st.markdown("""
<div class="main-header">
    <h1>⚡ ATHLETE-IQ PERFORMANCE ENGINE</h1>
    <p>Developed by: Coach Ahmed Youssef 👑</p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. ASSESSMENT INPUTS & DIAGNOSTIC DATA
# ==============================================================================
st.markdown('<div class="gradient-banner">📋 Assessment Data & Physical Parameters</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1. General Info & Demographics")
    sport_type = st.selectbox("Sport Discipline", ["Combat Athlete", "Racquet Sports", "Field Sports", "Track & Field"])
    age = st.number_input("Age", value=22, step=1)
    gender = st.selectbox("Gender", ["Female", "Male"])
    weight_kg = st.number_input("Weight (kg)", value=75.0, step=0.5)
    height_cm = st.number_input("Height (cm)", value=175.0, step=0.5)
    injuries = st.text_input("Active Injuries / Notes", value="Minor Patellar Tendinopathy (Right Knee)")

    st.markdown("### 3. Joint Maximum Range of Motion (ROM) Goniometry")
    rom_ankle = st.number_input("Ankle Dorsiflexion (°)", value=35.0)
    st.markdown('<div class="sub-norm">Norm: ≥30°</div>', unsafe_allow_html=True)

    rom_hip_flexion = st.number_input("Hip Flexion (°)", value=120.0)
    st.markdown('<div class="sub-norm">Norm: ≥120°</div>', unsafe_allow_html=True)

    rom_hip_extension = st.number_input("Hip Extension (°)", value=15.0)
    st.markdown('<div class="sub-norm">Norm: ≥15°</div>', unsafe_allow_html=True)

    rom_tspine = st.number_input("T-Spine Rotation (°)", value=45.0)
    st.markdown('<div class="sub-norm">Norm: ≥45°</div>', unsafe_allow_html=True)

    st.markdown("### 4.1. Power & Throws")
    medball_chest = st.number_input("Chest Pass Med-Ball (m)", value=6.80)
    medball_overhead = st.number_input("Overhead Throw Med-Ball (m)", value=8.50)
    medball_forehand = st.number_input("Forehand Throw Med-Ball (m)", value=7.20)
    medball_backhand = st.number_input("Backhand Throw Med-Ball (m)", value=6.90)

with col2:
    st.markdown("### 4.2. Speed & Agility Metrics")
    sprint_5m = st.number_input("5m First-Step Sprint (sec)", value=2.50)
    sprint_10m = st.number_input("10m Sprint (sec)", value=2.00)
    agility_7x7 = st.number_input("7 x 7 Agility Drill (sec)", value=14.20)
    tdrill = st.number_input("T-Drill Agility (sec)", value=10.20)
    sprint_1000m = st.number_input("1000m Sprint (sec)", value=235.00)

    st.markdown("### 4.3. Jumps & Strength Matrix")
    cmj = st.number_input("Countermovement Jump (CMJ) (cm)", value=42.0)
    horiz_both = st.number_input("Horizontal Jump Both Legs (cm)", value=215.0)
    horiz_left = st.number_input("Horizontal Jump Left (cm)", value=105.0)
    horiz_right = st.number_input("Horizontal Jump Right (cm)", value=104.0)
    vert_left = st.number_input("Vertical Jump Single Leg Left (cm)", value=20.0)
    vert_right = st.number_input("Vertical Jump Single Leg Right (cm)", value=30.0)

    rm_squat = st.number_input("1RM Max Back Squat (kg)", value=110.0)
    rm_bench = st.number_input("1RM Bench Press (kg)", value=75.0)

# ==============================================================================
# 4. REAL-TIME CALCULATIONS & METRICS
# ==============================================================================
mas_speed = round(1000.0 / sprint_1000m, 2) if sprint_1000m > 0 else 4.26
horiz_asym = round(abs(horiz_left - horiz_right) / max(horiz_left, horiz_right) * 100, 1) if max(horiz_left, horiz_right) > 0 else 0.0
vert_asym = round(abs(vert_left - vert_right) / max(vert_left, vert_right) * 100, 1) if max(vert_left, vert_right) > 0 else 0.0

if cmj > 50 and rm_squat < 100:
    fv_profile = "Velocity-Deficit Force Profile"
elif cmj < 35 and rm_squat > 130:
    fv_profile = "Force-Deficit Speed-Strength Profile"
else:
    fv_profile = "Balanced Force-Velocity Profile"

st.markdown('<div class="gradient-banner">🚀 Dynamic Multi-Month Periodization Engine</div>', unsafe_allow_html=True)

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("Force-Velocity Profile", fv_profile)
with m2:
    st.metric("Max Aerobic Speed", f"{mas_speed} m/s")
with m3:
    st.metric("Horiz Asymmetry", f"{horiz_asym}%")
with m4:
    st.metric("Vert Asymmetry", f"{vert_asym}%")
with m5:
    st.metric("Volume Schema", "2 Sets / Ex")

# ==============================================================================
# 5. DISTINCT MULTI-MONTH PERIODIZATION PROGRAM
# ==============================================================================
plan_data = {
    "Month 1": {
        "title": "📌 Month 1: Accumulation Phase (Work Capacity & Base Build)",
        "load": f"70% 1RM (Sq: {round(rm_squat*0.7, 1)}kg, Bench: {round(rm_bench*0.7, 1)}kg) (4 x 8 Reps)",
        "exercises": [
            "Dynamic World's Greatest Stretch & Multi-Planar Hip Flow",
            "Medicine Ball Rotational Launch",
            "Spanish Squat Isometric Hold (Knee-Sparing)",
            "Neutral-Grip Dumbbell Press",
            f"15s Linear Shuttle Run @ {round(mas_speed*18, 1)}m Target / 15s Rest"
        ]
    },
    "Month 2": {
        "title": "📌 Month 2: Intensification Phase (Max Strength & Dynamic Force)",
        "load": f"88% 1RM (Sq: {round(rm_squat*0.88, 1)}kg, Bench: {round(rm_bench*0.88, 1)}kg) (4 x 3 Reps)",
        "exercises": [
            "90/90 T-Spine Mobility & Banded Ankle Mobilization",
            "Heavy Trap-Bar Jump Squat",
            "Bulgarian Split Squat Iso Hold with Deficit",
            "Incline Barbell Bench Press",
            f"Repeated Sprint Agility Shuttles @ {round(mas_speed*20, 1)}m Target"
        ]
    },
    "Month 3": {
        "title": "📌 Month 3: Realization Phase (Peak Power, Speed & Taper)",
        "load": f"85% 1RM (Sq: {round(rm_squat*0.85, 1)}kg, Bench: {round(rm_bench*0.85, 1)}kg) (3 x 2 Fast)",
        "exercises": [
            "Dynamic Multi-Planar Bound & Ankle Stiffness Warmup",
            "Plyometric Box Jumps",
            "Single-Leg Cable Isometric Knee Extension",
            "Speed Dumbbell Bench Press",
            f"High-Velocity Sprint Shuttles @ {round(mas_speed*22, 1)}m Target"
        ]
    }
}

t_m1, t_m2, t_m3 = st.tabs(["📅 MONTH 1", "📅 MONTH 2", "📅 MONTH 3"])

for tab, month_key in zip([t_m1, t_m2, t_m3], ["Month 1", "Month 2", "Month 3"]):
    with tab:
        p_info = plan_data[month_key]
        st.markdown(f"### {p_info['title']}")
        
        w1, w2, w3, w4 = st.tabs(["Week 1", "Week 2", "Week 3", "Week 4"])
        for week_tab in [w1, w2, w3, w4]:
            with week_tab:
                st.write(f"**Phase Focus:** {month_key} Target Prescribed Loading | **Loading:** {p_info['load']}")
                st.table(pd.DataFrame({"Exercise": p_info["exercises"]}))

# ==============================================================================
# 6. ASSESSMENT RECORDS & TRACKING TABLE
# ==============================================================================
st.markdown('<div class="gradient-banner">📈 Assessment Records & Multi-Month Tracking</div>', unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = [
        {
            "index": 0, "date": "2026-01-10", "age": 22, "gender": gender, "weight_kg": weight_kg,
            "height_cm": height_cm, "1RM Back Squat (kg)": rm_squat, "1RM Bench Press (kg)": rm_bench,
            "CMJ (cm)": cmj, "10m Sprint (s)": sprint_10m
        }
    ]

if st.button("💾 Save Reassessment Entry"):
    new_idx = len(st.session_state.history)
    st.session_state.history.append({
        "index": new_idx,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "age": age,
        "gender": gender,
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "1RM Back Squat (kg)": rm_squat,
        "1RM Bench Press (kg)": rm_bench,
        "CMJ (cm)": cmj,
        "10m Sprint (s)": sprint_10m
    })
    st.success("Reassessment entry logged successfully!")

df_hist = pd.DataFrame(st.session_state.history)
st.dataframe(df_hist.set_index("index"), use_container_width=True)

if len(df_hist) > 1:
    st.markdown("### 📊 Reassessment Progression Graph")
    metric_choice = st.selectbox("Select Trajectory Metric", ["1RM Back Squat (kg)", "1RM Bench Press (kg)", "CMJ (cm)", "10m Sprint (s)"])
    fig = px.line(df_hist, x="date", y=metric_choice, markers=True, title=f"Progression Trajectory: {metric_choice}")
    fig.update_traces(line_color="#ec4899", line_width=3, marker=dict(size=10, color="#38bdf8"))
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0b0e14", plot_bgcolor="#161b22")
    st.plotly_chart(fig, use_container_width=True)
