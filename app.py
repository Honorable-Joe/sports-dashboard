import streamlit as st
import pandas as pd

# ==========================================
# APP CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="AthleteIQ - S&C Engine", layout="wide", page_icon="⚡")

# Custom CSS to maintain HUD Keyframe & Modern Dark Athletic Styling
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E6ED; }
    .hud-card {
        background: linear-gradient(135deg, #1E2640 0%, #111827 100%);
        border: 1px solid #2D3748;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .hud-value { font-size: 24px; font-weight: 700; color: #00F2FE; }
    .hud-label { font-size: 12px; color: #A0AEC0; text-transform: uppercase; letter-spacing: 1px; }
    .badge-inseason { background-color: #E53E3E; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
    .badge-offseason { background-color: #38A169; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# EXERCISE DATABASE & PROGRESSION MAPS
# ==========================================
EXERCISE_DATABASE = {
    "Squat Pattern": {
        "Regression": "Spanish Squat Hold (Isometric)",
        "Standard": "Barbell Back Squat",
        "Progression": "Single-Leg Pistol Squat",
        "Equipment": ["Barbell", "Rack"],
        "Tempo_Hypertrophy": "4-1-1-0",
        "Tempo_Power": "X-0-X-0"
    },
    "Posterior Chain": {
        "Regression": "Single-Leg Glute Bridge",
        "Standard": "Nordic Hamstring Curl",
        "Progression": "Barbell Trap Bar Deadlift",
        "Equipment": ["Barbell", "Turf"],
        "Tempo_Hypertrophy": "3-1-1-0",
        "Tempo_Power": "2-0-X-0"
    },
    "Rotational Core": {
        "Regression": "Pallof Press Hold",
        "Standard": "Diagonal Cable Chops",
        "Progression": "Rotational Med-Ball Scoop Throw",
        "Equipment": ["Cables", "Medicine Ball"],
        "Tempo_Hypertrophy": "2-1-2-0",
        "Tempo_Power": "X-0-X-0"
    },
    "Upper Push": {
        "Regression": "Incline Push-Up",
        "Standard": "Barbell Bench Press",
        "Progression": "Explosive Plyo Push-Up",
        "Equipment": ["Barbell", "Bench"],
        "Tempo_Hypertrophy": "3-1-1-0",
        "Tempo_Power": "X-0-X-0"
    },
    "Upper Pull": {
        "Regression": "Inverted Ring Row",
        "Standard": "Strict Bodyweight Pull-Up",
        "Progression": "Weighted Ring Dip / Muscle-Up",
        "Equipment": ["Pull-Up Bar", "Rings"],
        "Tempo_Hypertrophy": "3-0-1-1",
        "Tempo_Power": "X-0-1-0"
    }
}

SPORT_WARMUPS = {
    "Racket Sports / Golf": [
        "Wrist & Forearm Dynamic Rotations",
        "Thoracic Spine Openers (Transverse Plane)",
        "Lateral Multi-Directional Shuttles"
    ],
    "Soccer": [
        "Dynamic Hamstring Sweeps & Adductor Warm-Up",
        "Ankle Mobility & Single-Leg Balance Hops",
        "Multi-Directional Change of Direction (COD) 10m Shuttles"
    ],
    "Basketball": [
        "Ankle Mobility & Achilles Stiffness Hops",
        "Drop Landings (Landing Mechanics Prep)",
        "Reactive Vertical Jump Hops"
    ],
    "General Fitness": [
        "World's Greatest Stretch",
        "Band Pull-Aparts & Glute Bridges",
        "Bodyweight Squats & Arm Circles"
    ]
}

# ==========================================
# ATHLETE-IQ DECISION ENGINE
# ==========================================
class AthleteIQEngine:
    @staticmethod
    def calculate_periodization(season_phase, days_to_game):
        """Adjusts volume, intensity, and TUT based on seasonal demands and game proximity."""
        if season_phase == "In-Season":
            if days_to_game <= 1:
                return {"sets": 2, "reps": "2-3", "intent": "Neural Primer / Recovery", "vol_adj": "-60%", "tempo": "X-0-X-0"}
            elif days_to_game <= 3:
                return {"sets": 3, "reps": "3-4", "intent": "Power & Max Velocity", "vol_adj": "-40%", "tempo": "X-0-X-0"}
            else:
                return {"sets": 3, "reps": "4-6", "intent": "Strength Maintenance", "vol_adj": "-20%", "tempo": "2-1-1-0"}
        else:  # Off-Season
            return {"sets": 4, "reps": "8-12", "intent": "Structural Hypertrophy & Base", "vol_adj": "Baseline", "tempo": "4-1-1-0"}

    @staticmethod
    def resolve_exercise(movement, has_pain, sports_mode):
        """Resolves OPT progression/regression pathing based on pain flags."""
        data = EXERCISE_DATABASE[movement]
        if has_pain:
            return data["Regression"], "Pain Regressed (Isometric/Slow Tempo)"
        elif sports_mode in ["Basketball", "Soccer"] and movement in ["Squat Pattern", "Posterior Chain"]:
            return data["Progression"], "Sport-Specific Power Progression"
        else:
            return data["Standard"], "Standard Baseline Movement"

# ==========================================
# SIDEBAR CONTROL PANEL (HUD INPUTS)
# ==========================================
st.sidebar.title("⚡ AthleteIQ Controls")
st.sidebar.subheader("Profile & Seasonality")

sport = st.sidebar.selectbox("Select Sport", ["Soccer", "Basketball", "Racket Sports / Golf", "General Fitness"])
season = st.sidebar.radio("Season Phase", ["Off-Season", "In-Season"])
days_to_game = st.sidebar.slider("Days Until Match", min_value=1, max_value=7, value=3) if season == "In-Season" else 0

st.sidebar.subheader("Clinical & Constraints")
active_pain = st.sidebar.multiselect("Flag Active Pain / Injury Areas", ["Knee", "Hamstring / Groin", "Shoulder / Wrist", "Lower Back"])
eq_access = st.sidebar.multiselect("Available Equipment", ["Barbell", "Rack", "Medicine Ball", "Cables", "Rings", "Turf"], default=["Barbell", "Rack", "Turf"])

# Calculate Periodization Parameters
params = AthleteIQEngine.calculate_periodization(season, days_to_game)

# ==========================================
# HUD TOP METRICS DISPLAY (KEYFRAME UI)
# ==========================================
st.title("🎯 AthleteIQ Performance Dashboard")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
        <div class="hud-card">
            <div class="hud-label">Season Phase</div>
            <div class="hud-value">{season}</div>
            <span class="{'badge-inseason' if season == 'In-Season' else 'badge-offseason'}">{params['intent']}</span>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="hud-card">
            <div class="hud-label">Volume Adjustment</div>
            <div class="hud-value">{params['vol_adj']}</div>
            <div class="hud-label">Target Sets: {params['sets']}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="hud-card">
            <div class="hud-label">Prescribed Tempo (E-P-C-P)</div>
            <div class="hud-value">{params['tempo']}</div>
            <div class="hud-label">OPEX TUT Control</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="hud-card">
            <div class="hud-label">Active Pain Status</div>
            <div class="hud-value" style="color: {'#E53E3E' if active_pain else '#38A169'};">
                {'⚠️ Pain Flagged' if active_pain else '🟢 Clean'}
            </div>
            <div class="hud-label">{len(active_pain)} Flags Active</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# MAIN CONTENT TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏋️ Dynamic Workout Plan", "🩹 Rehab & Regressions", "📊 Assessment Engine"])

with tab1:
    st.subheader(f"Custom Session Plan for {sport}")
    
    # Warm-Up Block
    st.markdown("**Phase 1: Dynamic Warm-Up & Movement Prep**")
    warmups = SPORT_WARMUPS.get(sport, SPORT_WARMUPS["General Fitness"])
    for i, wu in enumerate(warmups, 1):
        st.write(f"• **Step {i}**: {wu}")
    
    st.markdown("---")
    st.markdown("**Phase 2: Main Strength & Conditioning Prescription**")
    
    # Generate Prescribed Exercises Dataframe
    workout_data = []
    for movement, details in EXERCISE_DATABASE.items():
        # Pain logic checks
        pain_flag = False
        if "Knee" in active_pain and movement == "Squat Pattern":
            pain_flag = True
        elif "Hamstring / Groin" in active_pain and movement == "Posterior Chain":
            pain_flag = True
        elif "Shoulder / Wrist" in active_pain and movement in ["Upper Push", "Upper Pull"]:
            pain_flag = True
            
        ex_name, status = AthleteIQEngine.resolve_exercise(movement, pain_flag, sport)
        
        workout_data.append({
            "Pattern": movement,
            "Prescribed Exercise": ex_name,
            "Target Sets": params["sets"],
            "Target Reps": params["reps"],
            "OPEX Tempo": params["tempo"],
            "Selection Logic": status
        })
    
    df_workout = pd.DataFrame(workout_data)
    st.dataframe(df_workout, use_container_width=True)

with tab2:
    st.subheader("Clinical Pathway & OPT Scaling Matrix")
    st.markdown("""
        When an athlete flags active joint pain or structural limitation, the engine scales exercises 
        down the **NASM OPT Continuum** to isometric holds or slow eccentric tempos.
    """)
    
    reg_data = []
    for pattern, info in EXERCISE_DATABASE.items():
        reg_data.append({
            "Movement Pattern": pattern,
            "Regressed (Pain / Deload)": info["Regression"],
            "Standard (Baseline)": info["Standard"],
            "Progressed (Power / Athletic)": info["Progression"],
            "Rehab Tempo Target": "3-2-3-0 (Isometric / Slow TUT)"
        })
    
    st.table(pd.DataFrame(reg_data))

with tab3:
    st.subheader("Normative Assessment & Diagnostic Scorecard")
    st.markdown("Enter baseline metrics to compare against athletic norms:")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        v_jump = st.number_input("Vertical Jump (Inches)", min_value=10.0, max_value=50.0, value=24.0)
    with col_b:
        vo2_max = st.number_input("Estimated VO2 Max (mL/kg/min)", min_value=20.0, max_value=90.0, value=48.0)
    with col_c:
        asym = st.number_input("Asymmetry Index (%)", min_value=0.0, max_value=30.0, value=4.5)
        
    st.markdown("**Diagnostic Feedback:**")
    if v_jump >= 28.0:
        st.success("✅ Power Profile: High Explosive Capacity (≥80th Percentile)")
    else:
        st.info("ℹ️ Power Profile: Base Capacity (Focus on RFD and Dynamic Plyometrics)")
        
    if asym > 10.0:
        st.warning("⚠️ High Movement Asymmetry Detected (>10%). Unilateral Correctives Recommended.")
    else:
        st.success("✅ Movement Asymmetry Within Normal Limits (<10%).")
