import streamlit as st
import pandas as pd
import numpy as np
import json
import os
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

# Custom CSS strictly tailored to match the original app screenshot aesthetics
st.markdown("""
<style>
    /* Dark background core */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Original Header Styling */
    .title-header {
        text-align: center;
        padding-top: 10px;
        padding-bottom: 20px;
    }
    .title-header h1 {
        color: #38bdf8;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin-bottom: 0px;
    }
    .title-header p {
        color: #a855f7;
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 5px;
    }

    /* Exact Original Gradient Banner Badges */
    .gradient-banner {
        background: linear-gradient(90deg, #7c3aed 0%, #ec4899 100%);
        color: white;
        padding: 14px 20px;
        border-radius: 12px;
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
    }

    /* Photo 4 Fix: Metric text full visibility without changing original metric layout */
    div[data-testid="stMetricValue"] > div {
        font-size: 1.5rem !important;
        white-space: normal !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
    }
    div[data-testid="stMetricLabel"] > label {
        font-size: 0.9rem !important;
        color: #94a3b8 !important;
        white-space: normal !important;
    }

    /* Input labels and norms visual formatting */
    .norm-text {
        color: #6e7681;
        font-size: 0.85rem;
        margin-top: -12px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. PERSISTENT ATHLETE PROFILE DATABASE & CRUD SYSTEM
# ==============================================================================
DB_FILE = "athletes_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

if "db" not in st.session_state:
    st.session_state.db = load_db()

# Default starter parameters
DEFAULT_METRICS = {
    "age": 22,
    "gender": "Female",
    "sport": "Combat Athlete",
    "weight_kg": 75.0,
    "height_cm": 175.0,
    "injuries": "Minor Patellar Tendinopathy (Right Knee)",
    "rom_ankle": 35.0,
    "rom_hip_flexion": 120.0,
    "rom_hip_extension": 15.0,
    "rom_tspine": 45.0,
    "medball_chest_pass": 6.80,
    "medball_overhead_throw": 8.50,
    "medball_forehand_throw": 7.20,  # Photo 2 Restored
    "medball_backhand_throw": 6.90,   # Photo 2 Restored
    "cmj_cm": 42.00,
    "horiz_jump_both": 215.00,
    "horiz_jump_left": 105.00,
    "horiz_jump_right": 104.00,
    "vert_jump_left": 20.00,
    "vert_jump_right": 30.00,
    "sprint_5m": 2.50,
    "sprint_10m": 2.00,
    "agility_7x7": 14.20,
    "tdrill_agility": 10.20,
    "sprint_1000m": 235.00,
    "rm_back_squat": 110.0,
    "rm_bench_press": 75.0
}

# Initialize initial sample profile if DB is completely empty
if not st.session_state.db:
    st.session_state.db["Alex Morgan"] = {
        "history": [
            {"date": "2026-01-10", "metrics": DEFAULT_METRICS.copy()},
            {"date": "2026-02-10", "metrics": DEFAULT_METRICS.copy()}
        ]
    }
    save_db(st.session_state.db)

# ==============================================================================
# 3. HEADER & SIDEBAR PROFILE MANAGEMENT (LOAD/EDIT/DELETE)
# ==============================================================================
st.markdown("""
<div class="title-header">
    <h1>⚡ ATHLETE-IQ PERFORMANCE ENGINE</h1>
    <p>Developed by: Coach Ahmed Youssef 👑</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("👤 Athlete Profiles")

athlete_list = list(st.session_state.db.keys())

# Profile Selector
selected_athlete = st.sidebar.selectbox("Select Active Athlete Profile", athlete_list)

# Profile Management Options
st.sidebar.markdown("---")
st.sidebar.subheader("Manage Profiles")

new_athlete_name = st.sidebar.text_input("New Athlete Name")
if st.sidebar.button("➕ Save / Create Profile"):
    if new_athlete_name.strip():
        if new_athlete_name not in st.session_state.db:
            st.session_state.db[new_athlete_name] = {
                "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "metrics": DEFAULT_METRICS.copy()}]
            }
            save_db(st.session_state.db)
            st.sidebar.success(f"Profile '{new_athlete_name}' created!")
            st.rerun()

if st.sidebar.button("🗑️ Remove Selected Profile"):
    if len(athlete_list) > 1:
        del st.session_state.db[selected_athlete]
        save_db(st.session_state.db)
        st.sidebar.success(f"Profile '{selected_athlete}' deleted.")
        st.rerun()
    else:
        st.sidebar.warning("At least one profile must remain in the database.")

# Load active athlete's latest metrics
athlete_data = st.session_state.db[selected_athlete]
active_metrics = athlete_data["history"][-1]["metrics"]

# ==============================================================================
# 4. ASSESSMENT INPUT FORM (PHOTOS 1, 2, 3 FIXES INTEGRATED)
# ==============================================================================
st.subheader("📋 Athlete Assessment Input & Diagnostic Data")

with st.expander("⚙️ Edit Assessment Metrics & Parameters", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 1. Demographics & General Metrics")
        sport_type = st.selectbox("Sport Discipline", ["Combat Athlete", "Racquet Sports", "Field Sports", "Track & Field"], 
                                  index=["Combat Athlete", "Racquet Sports", "Field Sports", "Track & Field"].index(active_metrics.get("sport", "Combat Athlete")))
        age = st.number_input("Age", value=int(active_metrics.get("age", 22)))
        gender = st.selectbox("Gender", ["Female", "Male"], index=0 if active_metrics.get("gender") == "Female" else 1)
        weight_kg = st.number_input("Weight (kg)", value=float(active_metrics.get("weight_kg", 75.0)))
        height_cm = st.number_input("Height (cm)", value=float(active_metrics.get("height_cm", 175.0)))
        injuries = st.text_input("Active Injuries / Notes", value=active_metrics.get("injuries", ""))

        # Photo 3 Fix: Removed broken asset path alt-text, cleaned up section heading
        st.markdown("### 3. Joint Maximum Range of Motion (ROM) Goniometry Matrix")
        
        rom_ankle = st.number_input("Ankle Dorsiflexion (°)", value=float(active_metrics.get("rom_ankle", 35.0)))
        st.markdown('<div class="norm-text">Norm: ≥30°</div>', unsafe_allow_html=True)
        
        rom_hip_flexion = st.number_input("Hip Flexion (°)", value=float(active_metrics.get("rom_hip_flexion", 120.0)))
        st.markdown('<div class="norm-text">Norm: ≥120°</div>', unsafe_allow_html=True)
        
        rom_hip_extension = st.number_input("Hip Extension (°)", value=float(active_metrics.get("rom_hip_extension", 15.0)))
        st.markdown('<div class="norm-text">Norm: ≥15°</div>', unsafe_allow_html=True)
        
        rom_tspine = st.number_input("T-Spine Rotation (°)", value=float(active_metrics.get("rom_tspine", 45.0)))
        st.markdown('<div class="norm-text">Norm: ≥45°</div>', unsafe_allow_html=True)

        st.markdown("### 4.1. Power Metrics")
        medball_chest = st.number_input("Chest Pass Med-Ball (m)", value=float(active_metrics.get("medball_chest_pass", 6.80)))
        medball_overhead = st.number_input("Overhead Throw Med-Ball (m)", value=float(active_metrics.get("medball_overhead_throw", 8.50)))
        
        # Photo 2 Fix: Restored Forehand & Backhand throws
        medball_forehand = st.number_input("Forehand Throw Med-Ball (m)", value=float(active_metrics.get("medball_forehand_throw", 7.20)))
        medball_backhand = st.number_input("Backhand Throw Med-Ball (m)", value=float(active_metrics.get("medball_backhand_throw", 6.90)))

    with col2:
        # Photo 1 Fix: All inputs active and clearly readable for combat and all athletes
        st.markdown("### 4.2. Speed & Agility Metrics")
        sprint_5m = st.number_input("5m First-Step Sprint (sec)", value=float(active_metrics.get("sprint_5m", 2.50)))
        sprint_10m = st.number_input("10m Sprint (sec)", value=float(active_metrics.get("sprint_10m", 2.00)))
        agility_7x7 = st.number_input("7 x 7 Agility Drill (sec)", value=float(active_metrics.get("agility_7x7", 14.20)))
        tdrill = st.number_input("T-Drill Agility (sec)", value=float(active_metrics.get("tdrill_agility", 10.20)))
        sprint_1000m = st.number_input("1000m Sprint (sec)", value=float(active_metrics.get("sprint_1000m", 235.00)))

        st.markdown("### 4.3. Jump & 1RM Max Matrix")
        cmj = st.number_input("Countermovement Jump (CMJ) (cm)", value=float(active_metrics.get("cmj_cm", 42.0)))
        horiz_both = st.number_input("Horizontal Jump Both Legs (cm)", value=float(active_metrics.get("horiz_jump_both", 215.0)))
        horiz_left = st.number_input("Horizontal Jump Left (cm)", value=float(active_metrics.get("horiz_jump_left", 105.0)))
        horiz_right = st.number_input("Horizontal Jump Right (cm)", value=float(active_metrics.get("horiz_jump_right", 104.0)))
        vert_left = st.number_input("Vertical Jump Single Leg Left (cm)", value=float(active_metrics.get("vert_jump_left", 20.0)))
        vert_right = st.number_input("Vertical Jump Single Leg Right (cm)", value=float(active_metrics.get("vert_jump_right", 30.0)))
        
        rm_squat = st.number_input("1RM Max Back Squat (kg)", value=float(active_metrics.get("rm_back_squat", 110.0)))
        rm_bench = st.number_input("1RM Bench Press (kg)", value=float(active_metrics.get("rm_bench_press", 75.0)))

    # Save Reassessment Entry Button
    if st.button("💾 Save Reassessment Data for Active Athlete"):
        new_entry = {
            "age": age, "gender": gender, "sport": sport_type, "weight_kg": weight_kg, "height_cm": height_cm,
            "injuries": injuries, "rom_ankle": rom_ankle, "rom_hip_flexion": rom_hip_flexion,
            "rom_hip_extension": rom_hip_extension, "rom_tspine": rom_tspine,
            "medball_chest_pass": medball_chest, "medball_overhead_throw": medball_overhead,
            "medball_forehand_throw": medball_forehand, "medball_backhand_throw": medball_backhand,
            "cmj_cm": cmj, "horiz_jump_both": horiz_both, "horiz_jump_left": horiz_left,
            "horiz_jump_right": horiz_right, "vert_jump_left": vert_left, "vert_jump_right": vert_right,
            "sprint_5m": sprint_5m, "sprint_10m": sprint_10m, "agility_7x7": agility_7x7,
            "tdrill_agility": tdrill, "sprint_1000m": sprint_1000m, "rm_back_squat": rm_squat, "rm_bench_press": rm_bench
        }
        
        st.session_state.db[selected_athlete]["history"].append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "metrics": new_entry
        })
        save_db(st.session_state.db)
        st.success(f"Reassessment saved for {selected_athlete}!")
        st.rerun()

# ==============================================================================
# 5. DYNAMIC CALCULATIONS & METRICS DISPLAY (PHOTO 4 FIX)
# ==============================================================================
# Real-time plan update engine logic based directly on inputs
mas_speed = round(1000.0 / sprint_1000m, 2) if sprint_1000m > 0 else 4.26
horiz_asym = round(abs(horiz_left - horiz_right) / max(horiz_left, horiz_right) * 100, 1) if max(horiz_left, horiz_right) > 0 else 0.0
vert_asym = round(abs(vert_left - vert_right) / max(vert_left, vert_right) * 100, 1) if max(vert_left, vert_right) > 0 else 0.0

# Force-Velocity Profile Dynamics
if cmj > 50 and rm_squat < 100:
    fv_profile = "Velocity-Deficit Force Profile"
elif cmj < 35 and rm_squat > 130:
    fv_profile = "Force-Deficit Speed-Strength Profile"
else:
    fv_profile = "Balanced Force-Velocity Profile"

# Gradient Title Banner (Original Keyframe Match)
st.markdown("""
<div class="gradient-banner">
    🚀 Dynamic Multi-Month Periodization Engine
</div>
""", unsafe_allow_html=True)

# Metrics Cards Display (Photo 4 text truncation fixed)
m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)

with m_col1:
    st.metric(label="Force-Velocity Profile", value=fv_profile)

with m_col2:
    st.metric(label="Max Aerobic Speed", value=f"{mas_speed} m/s")

with m_col3:
    st.metric(label="Horiz Asymmetry", value=f"{horiz_asym}%")

with m_col4:
    st.metric(label="Vert Asymmetry", value=f"{vert_asym}%")

with m_col5:
    st.metric(label="Volume Schema", value="2 Sets / Ex")

# ==============================================================================
# 6. NON-REPETITIVE MULTI-MONTH PERIODIZATION PLAN (PHOTOS 5, 6, 7 FIX)
# ==============================================================================
# Exercises dynamically rotate across months while targeting identical muscle groups & movement patterns
PERIODIZATION_PLAN = {
    "Month 1": {
        "title": "📌 Month 1: Accumulation Phase (Work Capacity & Base Build)",
        "loading": f"70% 1RM (Sq: {round(rm_squat*0.7, 1)}kg, Bench: {round(rm_bench*0.7, 1)}kg) (4 x 8 Reps)",
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
        "loading": f"88% 1RM (Sq: {round(rm_squat*0.88, 1)}kg, Bench: {round(rm_bench*0.88, 1)}kg) (4 x 3 Reps)",
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
        "loading": f"85% 1RM (Sq: {round(rm_squat*0.85, 1)}kg, Bench: {round(rm_bench*0.85, 1)}kg) (3 x 2 Fast)",
        "exercises": [
            "Dynamic Multi-Planar Bound & Ankle Stiffness Warmup",
            "Plyometric Box Jumps",
            "Single-Leg Cable Isometric Knee Extension",
            "Speed Dumbbell Bench Press",
            f"High-Velocity Sprint Shuttles @ {round(mas_speed*22, 1)}m Target"
        ]
    }
}

tab_m1, tab_m2, tab_m3 = st.tabs(["📅 MONTH 1", "📅 MONTH 2", "📅 MONTH 3"])

for tab, m_key in zip([tab_m1, tab_m2, tab_m3], ["Month 1", "Month 2", "Month 3"]):
    with tab:
        p_data = PERIODIZATION_PLAN[m_key]
        st.markdown(f"### {p_data['title']}")
        
        # Sub-tabs for weeks (Original Layout)
        w1, w2, w3, w4 = st.tabs(["Week 1", "Week 2", "Week 3", "Week 4"])
        
        for week_tab in [w1, w2, w3, w4]:
            with week_tab:
                st.write(f"**Phase Focus:** {m_key} Target Prescribed Loading | **Loading:** {p_data['loading']}")
                
                # Render Clean Native Table matching original keyframe screenshots (with index column 0,1,2,3...)
                df_plan = pd.DataFrame({"Exercise": p_data["exercises"]})
                st.table(df_plan)

# ==============================================================================
# 7. SAVED ASSESSMENT RECORDS & PROGRESSION GRAPH (PHOTO 8 FIX)
# ==============================================================================
st.markdown("""
<div class="gradient-banner">
    📈 Saved Assessment Records & Multi-Month Tracking
</div>
""", unsafe_allow_html=True)

# Build history dataframe for active athlete
history_list = []
for idx, entry in enumerate(athlete_data["history"]):
    m = entry["metrics"]
    history_list.append({
        "index": idx,
        "athlete_name": selected_athlete,
        "date": entry.get("date", f"Session {idx+1}"),
        "age": m.get("age"),
        "gender": m.get("gender"),
        "weight_kg": m.get("weight_kg"),
        "height_cm": m.get("height_cm"),
        "1RM Back Squat (kg)": m.get("rm_back_squat"),
        "1RM Bench Press (kg)": m.get("rm_bench_press"),
        "CMJ (cm)": m.get("cmj_cm"),
        "10m Sprint (s)": m.get("sprint_10m")
    })

df_history = pd.DataFrame(history_list)

# Render native Streamlit table with index matching Screenshot 1
st.dataframe(df_history.set_index("index"), use_container_width=True)

# Photo 8 Fix: Reassessment Progression Chart
if len(df_history) > 1:
    st.markdown("### 📊 Reassessment Progression Trajectory")
    chart_metric = st.selectbox("Select Trajectory Metric", ["1RM Back Squat (kg)", "1RM Bench Press (kg)", "CMJ (cm)", "10m Sprint (s)"])
    
    fig = px.line(
        df_history, 
        x="date", 
        y=chart_metric, 
        markers=True, 
        title=f"{selected_athlete} - {chart_metric} Progression Over Time"
    )
    
    fig.update_traces(line_color="#ec4899", line_width=3, marker=dict(size=10, color="#38bdf8"))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#161b22",
        font=dict(color="#c9d1d9")
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("ℹ️ Save a second reassessment entry above to view the progression chart visualizer.")
