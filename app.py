import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==============================================================================
# 1. PAGE CONFIGURATION & STYLING (KEYFRAME PRESERVATION & FIXES)
# ==============================================================================
st.set_page_config(
    page_title="ATHLETE-IQ PERFORMANCE ENGINE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to maintain dark theme keyframe and fix text truncation (Photo 4 fix)
st.markdown("""
<style>
    /* Dark Theme Core Keyframe */
    .main {
        background-color: #0b0e14;
        color: #f0f2f6;
    }
    
    /* Header Gradient Card */
    .main-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #311b92 50%, #4a148c 100%);
        padding: 24px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid #4338ca;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    .main-header h1 {
        color: #38bdf8;
        font-weight: 800;
        margin: 0;
        font-size: 2.2rem;
        letter-spacing: 1px;
    }
    
    .main-header p {
        color: #e0e7ff;
        font-weight: 600;
        margin-top: 6px;
        margin-bottom: 0;
    }

    /* Section Headers */
    .section-banner {
        background: linear-gradient(90deg, #a855f7 0%, #ec4899 100%);
        padding: 12px 20px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 1.15rem;
        color: #ffffff;
        margin-top: 25px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
    }

    /* FIX FOR PHOTO 4: Prevents text truncation on cards/metrics */
    .custom-metric-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        min-height: 110px;
    }
    
    .custom-metric-label {
        font-size: 0.88rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }

    .custom-metric-value {
        font-size: 1.5rem;
        color: #f8fafc;
        font-weight: 700;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        line-height: 1.2;
    }

    /* Tab and Input Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px 8px 0px 0px;
        color: #94a3b8;
        padding: 10px 20px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. PERSISTENT DATA ARCHITECTURE & ATHLETE CRUD SYSTEM
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

# Default athlete initial values template
DEFAULT_METRICS = {
    "age": 22,
    "gender": "Female",
    "sport": "Combat Athlete",
    "weight_kg": 75.0,
    "height_cm": 175.0,
    "injuries": "Minor Patellar Tendinopathy (Right Knee)",
    # Joint ROM
    "rom_ankle": 35.0,
    "rom_hip_flexion": 120.0,
    "rom_hip_extension": 15.0,
    "rom_tspine": 45.0,
    # Power & Throws
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
    # Speed & Agility
    "sprint_5m": 2.50,
    "sprint_10m": 2.00,
    "agility_7x7": 14.20,
    "tdrill_agility": 10.20,
    "sprint_1000m": 235.00,
    # 1RM
    "rm_back_squat": 110.0,
    "rm_bench_press": 75.0,
    "rm_trap_bar": 140.0
}

# Ensure at least sample record exists if DB is completely empty
if not st.session_state.db:
    st.session_state.db["Alex Morgan"] = {
        "profile_info": {"name": "Alex Morgan", "created_at": "2026-01-10"},
        "history": [
            {
                "date": "2026-01-10",
                "metrics": DEFAULT_METRICS.copy()
            }
        ]
    }
    save_db(st.session_state.db)

# ==============================================================================
# 3. HEADER & ATHLETE PROFILE MANAGER (SIDEBAR CRUD)
# ==============================================================================
st.markdown("""
<div class="main-header">
    <h1>⚡ ATHLETE-IQ PERFORMANCE ENGINE</h1>
    <p>Developed by: Coach Ahmed Youssef 👑</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("👤 Athlete Profile Manager")

athlete_names = list(st.session_state.db.keys())
menu_option = st.sidebar.radio("Select Action", ["Load / Edit Profile", "Create New Athlete Profile", "Manage Profiles"])

selected_athlete = None

if menu_option == "Create New Athlete Profile":
    new_name = st.sidebar.text_input("New Athlete Name")
    if st.sidebar.button("➕ Add Profile"):
        if new_name and new_name not in st.session_state.db:
            st.session_state.db[new_name] = {
                "profile_info": {"name": new_name, "created_at": datetime.now().strftime("%Y-%m-%d")},
                "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "metrics": DEFAULT_METRICS.copy()}]
            }
            save_db(st.session_state.db)
            st.sidebar.success(f"Profile for '{new_name}' created!")
            st.rerun()
        elif new_name in st.session_state.db:
            st.sidebar.error("Athlete profile already exists!")

elif menu_option == "Manage Profiles":
    target_athlete = st.sidebar.selectbox("Select Profile to Delete", athlete_names)
    if st.sidebar.button("🗑️ Delete Selected Profile"):
        if len(athlete_names) > 1:
            del st.session_state.db[target_athlete]
            save_db(st.session_state.db)
            st.sidebar.success(f"Deleted profile for '{target_athlete}'.")
            st.rerun()
        else:
            st.sidebar.warning("Cannot delete the only remaining profile!")

# Active athlete selection
active_athlete = st.sidebar.selectbox("Active Athlete Profile", athlete_names)
athlete_data = st.session_state.db[active_athlete]
latest_metrics = athlete_data["history"][-1]["metrics"]

st.sidebar.markdown("---")
st.sidebar.info(f"Active Profile: **{active_athlete}**\n\nAssessments Saved: **{len(athlete_data['history'])}**")

# ==============================================================================
# 4. DATA INPUT FORM & LIVE METRIC BINDING
# ==============================================================================
st.markdown('<div class="section-banner">⚙️ Athlete Assessment Inputs</div>', unsafe_allow_html=True)

with st.expander("📝 Edit Assessment Metrics & Physical Parameters", expanded=True):
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("**General & Demographics**")
        sport_type = st.selectbox("Sport / Discipline", ["Combat Athlete", "Racquet Sports (Tennis/Squash)", "Field Sports (Soccer/Rugby)", "Track & Field"], 
                                  index=["Combat Athlete", "Racquet Sports (Tennis/Squash)", "Field Sports (Soccer/Rugby)", "Track & Field"].index(latest_metrics.get("sport", "Combat Athlete")))
        age = st.number_input("Age", value=int(latest_metrics.get("age", 22)))
        gender = st.selectbox("Gender", ["Female", "Male"], index=0 if latest_metrics.get("gender") == "Female" else 1)
        weight_kg = st.number_input("Weight (kg)", value=float(latest_metrics.get("weight_kg", 75.0)))
        height_cm = st.number_input("Height (cm)", value=float(latest_metrics.get("height_cm", 175.0)))
        injuries = st.text_input("Active Injuries / Contraindications", value=latest_metrics.get("injuries", ""))

    with col_b:
        # Photo 3 Fix: Custom Clean Visual Header replacing broken image asset
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span style="font-size: 1.4rem;">📐</span>
            <strong style="font-size: 1.05rem;">3. Joint Maximum Range of Motion (ROM) Goniometry</strong>
        </div>
        """, unsafe_allow_html=True)
        
        rom_ankle = st.number_input("Ankle Dorsiflexion (°)", value=float(latest_metrics.get("rom_ankle", 35.0)))
        rom_hip_flexion = st.number_input("Hip Flexion (°)", value=float(latest_metrics.get("rom_hip_flexion", 120.0)))
        rom_hip_extension = st.number_input("Hip Extension (°)", value=float(latest_metrics.get("rom_hip_extension", 15.0)))
        rom_tspine = st.number_input("T-Spine Rotation (°)", value=float(latest_metrics.get("rom_tspine", 45.0)))

        st.markdown("**4.1. Power & Throws Metrics**")
        medball_chest = st.number_input("Chest Pass Med-Ball (m)", value=float(latest_metrics.get("medball_chest_pass", 6.80)))
        medball_overhead = st.number_input("Overhead Throw Med-Ball (m)", value=float(latest_metrics.get("medball_overhead_throw", 8.50)))
        # Photo 2 Fix: Restored Forehand & Backhand throws
        medball_forehand = st.number_input("Forehand Throw Med-Ball (m)", value=float(latest_metrics.get("medball_forehand_throw", 7.20)))
        medball_backhand = st.number_input("Backhand Throw Med-Ball (m)", value=float(latest_metrics.get("medball_backhand_throw", 6.90)))

    with col_c:
        # Photo 1 Fix: Ensure combat and all player inputs remain active, clear, and fully accessible
        st.markdown("**4.2. Speed & Agility Metrics**")
        sprint_5m = st.number_input("5m First-Step Sprint (sec)", value=float(latest_metrics.get("sprint_5m", 2.50)))
        sprint_10m = st.number_input("10m Sprint (sec)", value=float(latest_metrics.get("sprint_10m", 2.00)))
        agility_7x7 = st.number_input("7 x 7 Agility Drill (sec)", value=float(latest_metrics.get("agility_7x7", 14.20)))
        tdrill = st.number_input("T-Drill Agility (sec)", value=float(latest_metrics.get("tdrill_agility", 10.20)))
        sprint_1000m = st.number_input("1000m Sprint (sec)", value=float(latest_metrics.get("sprint_1000m", 235.00)))

        st.markdown("**Jumps & 1RM Matrix**")
        cmj = st.number_input("Countermovement Jump (CMJ) (cm)", value=float(latest_metrics.get("cmj_cm", 42.0)))
        horiz_both = st.number_input("Horizontal Jump Both Legs (cm)", value=float(latest_metrics.get("horiz_jump_both", 215.0)))
        horiz_left = st.number_input("Horizontal Jump Left (cm)", value=float(latest_metrics.get("horiz_jump_left", 105.0)))
        horiz_right = st.number_input("Horizontal Jump Right (cm)", value=float(latest_metrics.get("horiz_jump_right", 104.0)))
        vert_left = st.number_input("Vertical Jump Single Leg Left (cm)", value=float(latest_metrics.get("vert_jump_left", 20.0)))
        vert_right = st.number_input("Vertical Jump Single Leg Right (cm)", value=float(latest_metrics.get("vert_jump_right", 30.0)))
        rm_squat = st.number_input("1RM Max Back Squat (kg)", value=float(latest_metrics.get("rm_back_squat", 110.0)))
        rm_bench = st.number_input("1RM Bench Press (kg)", value=float(latest_metrics.get("rm_bench_press", 75.0)))

    save_col1, save_col2 = st.columns([1, 4])
    with save_col1:
        if st.button("💾 Save Reassessment"):
            updated_metrics = {
                "age": age, "gender": gender, "sport": sport_type, "weight_kg": weight_kg, "height_cm": height_cm,
                "injuries": injuries, "rom_ankle": rom_ankle, "rom_hip_flexion": rom_hip_flexion,
                "rom_hip_extension": rom_hip_extension, "rom_tspine": rom_tspine,
                "medball_chest_pass": medball_chest, "medball_overhead_throw": medball_overhead,
                "medball_forehand_throw": medball_forehand, "medball_backhand_throw": medball_backhand,
                "cmj_cm": cmj, "horiz_jump_both": horiz_both, "horiz_jump_left": horiz_left,
                "horiz_jump_right": horiz_right, "vert_jump_left": vert_left, "vert_jump_right": vert_right,
                "sprint_5m": sprint_5m, "sprint_10m": sprint_10m, "agility_7x7": agility_7x7,
                "tdrill_agility": tdrill, "sprint_1000m": sprint_1000m, "rm_back_squat": rm_squat,
                "rm_bench_press": rm_bench, "rm_trap_bar": rm_squat * 1.2
            }
            
            # Save new assessment entry with current timestamp
            st.session_state.db[active_athlete]["history"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "metrics": updated_metrics
            })
            save_db(st.session_state.db)
            st.success(f"New assessment record saved for {active_athlete}!")
            st.rerun()

# ==============================================================================
# 5. DERIVED ANALYTICS & DYNAMIC PERIODIZATION ENGINE
# ==============================================================================
# Dynamic calculation based directly on form state
mas_speed = round(1000.0 / sprint_1000m, 2) if sprint_1000m > 0 else 4.26
horiz_asym = round(abs(horiz_left - horiz_right) / max(horiz_left, horiz_right) * 100, 1)
vert_asym = round(abs(vert_left - vert_right) / max(vert_left, vert_right) * 100, 1)

# Determine Force-Velocity Profile dynamics
if cmj > 50 and rm_squat < 100:
    fv_profile = "Velocity-Deficit Force Profile"
elif cmj < 35 and rm_squat > 130:
    fv_profile = "Force-Deficit Speed-Strength Profile"
else:
    fv_profile = "Balanced Force-Velocity Profile"

st.markdown('<div class="section-banner">🚀 Dynamic Multi-Month Periodization Engine</div>', unsafe_allow_html=True)

# Photo 4 Fix: Metric display wrapped in custom CSS boxes to completely eliminate text truncation
m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)

with m_col1:
    st.markdown(f"""
    <div class="custom-metric-box">
        <div class="custom-metric-label">Force-Velocity Profile</div>
        <div class="custom-metric-value">{fv_profile}</div>
    </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown(f"""
    <div class="custom-metric-box">
        <div class="custom-metric-label">Max Aerobic Speed</div>
        <div class="custom-metric-value">{mas_speed} m/s</div>
    </div>
    """, unsafe_allow_html=True)

with m_col3:
    st.markdown(f"""
    <div class="custom-metric-box">
        <div class="custom-metric-label">Horiz Asymmetry</div>
        <div class="custom-metric-value">{horiz_asym}%</div>
    </div>
    """, unsafe_allow_html=True)

with m_col4:
    st.markdown(f"""
    <div class="custom-metric-box">
        <div class="custom-metric-label">Vert Asymmetry</div>
        <div class="custom-metric-value">{vert_asym}%</div>
    </div>
    """, unsafe_allow_html=True)

with m_col5:
    st.markdown(f"""
    <div class="custom-metric-box">
        <div class="custom-metric-label">Volume Schema</div>
        <div class="custom-metric-value">2-4 Sets / Ex</div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 6. NON-REPETITIVE MULTI-MONTH EXERCISE VARIATION ENGINE (Photos 5, 6, 7 Fix)
# ==============================================================================
# Muscle Group / Movement Pattern Mapping with DISTINCT exercise variations across months
EXERCISE_MAPPING = {
    "Month 1": {
        "phase_name": "📌 Month 1: Accumulation Phase (Work Capacity & Base Build)",
        "load": f"70% 1RM (Sq: {round(rm_squat*0.7, 1)}kg, Bench: {round(rm_bench*0.7, 1)}kg) (4 x 8 Reps)",
        "exercises": [
            {"Exercise": "Dynamic World's Greatest Stretch & Multi-Planar Hip Flow", "Target": "Warmup / Mobility"},
            {"Exercise": "Medicine Ball Rotational Launch", "Target": "Rotational Power"},
            {"Exercise": "Spanish Squat Isometric Hold (Knee-Sparing)", "Target": "Quadriceps / Tendon Loading"},
            {"Exercise": "Neutral-Grip Dumbbell Press", "Target": "Upper Horizontal Push"},
            {"Exercise": f"15s Linear Shuttle Run @ {round(mas_speed*18, 1)}m Target / 15s Rest", "Target": "Conditioning (MAS)"}
        ]
    },
    "Month 2": {
        "phase_name": "📌 Month 2: Intensification Phase (Max Strength & Dynamic Force)",
        "load": f"88% 1RM (Sq: {round(rm_squat*0.88, 1)}kg, Bench: {round(rm_bench*0.88, 1)}kg) (4 x 3 Reps)",
        "exercises": [
            {"Exercise": "90/90 T-Spine Mobility & Banded Ankle Mobilization", "Target": "Warmup / Mobility"},
            {"Exercise": "Heavy Trap-Bar Jump Squat", "Target": "Lower Body Power"},
            {"Exercise": "Bulgarian Split Squat Iso Hold with Deficit", "Target": "Quadriceps / Unilateral Strength"},
            {"Exercise": "Incline Barbell Bench Press", "Target": "Upper Horizontal Push"},
            {"Exercise": f"Repeated Sprint Agility Shuttles @ {round(mas_speed*20, 1)}m Target", "Target": "Conditioning (MAS)"}
        ]
    },
    "Month 3": {
        "phase_name": "📌 Month 3: Realization Phase (Peak Power, Speed & Taper)",
        "load": f"85% 1RM (Sq: {round(rm_squat*0.85, 1)}kg, Bench: {round(rm_bench*0.85, 1)}kg) (3 x 2 Fast)",
        "exercises": [
            {"Exercise": "Dynamic Multi-Planar Bound & Ankle Stiffness Warmup", "Target": "Warmup / Mobility"},
            {"Exercise": "Plyometric Box Jumps (Depth Jump to Land)", "Target": "Reactive Power"},
            {"Exercise": "Single-Leg Cable Isometric Knee Extension", "Target": "Quadriceps / Tendon Stiffness"},
            {"Exercise": "Speed Dumbbell Bench Press (Explosive Concept)", "Target": "Upper Horizontal Push"},
            {"Exercise": f"High-Velocity Sprint Shuttles @ {round(mas_speed*22, 1)}m Target", "Target": "Conditioning (MAS)"}
        ]
    }
}

tab1, tab2, tab3 = st.tabs(["📅 MONTH 1", "📅 MONTH 2", "📅 MONTH 3"])

for tab, month_key in zip([tab1, tab2, tab3], ["Month 1", "Month 2", "Month 3"]):
    with tab:
        m_data = EXERCISE_MAPPING[month_key]
        st.subheader(m_data["phase_name"])
        
        # Sub-tabs for weeks
        w1, w2, w3, w4 = st.tabs(["Week 1", "Week 2", "Week 3", "Week 4"])
        for w_idx, week_tab in enumerate([w1, w2, w3, w4], 1):
            with week_tab:
                st.write(f"**Phase Focus:** {month_key} Load Progression | **Target Prescribed Loading:** {m_data['load']}")
                df_ex = pd.DataFrame(m_data["exercises"])
                st.table(df_ex)

# ==============================================================================
# 7. SAVED ASSESSMENT RECORDS & PROGRESSION GRAPH (Photo 8 Fix)
# ==============================================================================
st.markdown('<div class="section-banner">📈 Saved Assessment Records & Multi-Month Tracking</div>', unsafe_allow_html=True)

history_records = athlete_data["history"]
history_df_list = []

for idx, rec in enumerate(history_records):
    m = rec["metrics"]
    history_df_list.append({
        "Assessment #": idx + 1,
        "Date": rec.get("date", f"Record {idx+1}"),
        "Athlete Name": active_athlete,
        "Age": m.get("age"),
        "Gender": m.get("gender"),
        "Weight (kg)": m.get("weight_kg"),
        "Back Squat 1RM (kg)": m.get("rm_back_squat"),
        "Bench Press 1RM (kg)": m.get("rm_bench_press"),
        "CMJ (cm)": m.get("cmj_cm"),
        "10m Sprint (s)": m.get("sprint_10m"),
        "1000m Sprint (s)": m.get("sprint_1000m")
    })

hist_df = pd.DataFrame(history_df_list)

# Render Data Table
st.dataframe(hist_df, use_container_width=True)

# Photo 8 Fix: Progression Chart Visualizer
st.markdown("### 📊 Athlete Progression Trajectory Graph")

if len(hist_df) > 1:
    metric_to_plot = st.selectbox(
        "Select Metric to Track Progression",
        ["Back Squat 1RM (kg)", "Bench Press 1RM (kg)", "CMJ (cm)", "10m Sprint (s)", "1000m Sprint (s)"]
    )
    
    fig = px.line(
        hist_df,
        x="Date",
        y=metric_to_plot,
        text=metric_to_plot,
        markers=True,
        title=f"Progression Trajectory: {metric_to_plot} ({active_athlete})"
    )
    
    fig.update_traces(
        line_color='#ec4899',
        line_width=3,
        marker=dict(size=10, color='#38bdf8'),
        textposition="top center"
    )
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b0e14",
        plot_bgcolor="#161b22",
        font=dict(color="#f0f2f6"),
        xaxis=dict(showgrid=True, gridcolor="#30363d"),
        yaxis=dict(showgrid=True, gridcolor="#30363d")
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("ℹ️ Perform and click '💾 Save Reassessment' above to log multiple test entries and view progression graphs over time.")
