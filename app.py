import streamlit as st
import pandas as pd

# ==========================================
# 1. APP CONFIG & KEYFRAME HUD STYLING
# ==========================================
st.set_page_config(page_title="AthleteIQ - S&C Engine", layout="wide", page_icon="⚡")

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
    .hud-value { font-size: 22px; font-weight: 700; color: #00F2FE; }
    .hud-label { font-size: 11px; color: #A0AEC0; text-transform: uppercase; letter-spacing: 1px; }
    .badge-status { background-color: #3182CE; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MASTER EXERCISE & MOVEMENT DATABASE
# ==========================================
EXERCISE_DATABASE = {
    "Lower Body Quad Dynamic": {
        "Regression": "Spanish Squat Hold (Isometric)",
        "Standard": "Barbell Back Squat",
        "Progression": "Single-Leg Pistol Squat / Jump Squat",
        "Primary_Equipment": "Barbell",
        "Fallback_Equipment": "Dumbbells",
        "Fallback_Exercise": "Goblet Squat",
        "Hypertrophy_Tempo": "4-1-1-0",
        "Power_Tempo": "X-0-X-0",
        "Joint_Flag": "Knee"
    },
    "Posterior Chain Hinge": {
        "Regression": "Single-Leg Glute Bridge",
        "Standard": "Nordic Hamstring Curl / Romanian Deadlift",
        "Progression": "Trap Bar Deadlift",
        "Primary_Equipment": "Barbell",
        "Fallback_Equipment": "Resistance Bands",
        "Fallback_Exercise": "Banded Good Mornings",
        "Hypertrophy_Tempo": "3-1-1-0",
        "Power_Tempo": "2-0-X-0",
        "Joint_Flag": "Hamstring / Groin"
    },
    "Horizontal Push": {
        "Regression": "Incline Push-Up",
        "Standard": "Barbell Bench Press",
        "Progression": "Explosive Plyo Push-Up",
        "Primary_Equipment": "Barbell",
        "Fallback_Equipment": "Dumbbells",
        "Fallback_Exercise": "Dumbbell Floor Press",
        "Hypertrophy_Tempo": "3-1-1-0",
        "Power_Tempo": "X-0-X-0",
        "Joint_Flag": "Shoulder / Wrist"
    },
    "Vertical Push": {
        "Regression": "Half-Kneeling Bottoms-Up KB Press",
        "Standard": "Overhead Barbell Press",
        "Progression": "Push Press / Jerk",
        "Primary_Equipment": "Barbell",
        "Fallback_Equipment": "Kettlebell",
        "Fallback_Exercise": "Single-Arm KB Press",
        "Hypertrophy_Tempo": "3-0-1-0",
        "Power_Tempo": "X-0-X-0",
        "Joint_Flag": "Shoulder / Wrist"
    },
    "Horizontal Pull": {
        "Regression": "Inverted Ring Row",
        "Standard": "Barbell Bent-Over Row",
        "Progression": "Single-Arm Cable Lawnmover Row",
        "Primary_Equipment": "Barbell",
        "Fallback_Equipment": "Rings",
        "Fallback_Exercise": "Bodyweight Ring Row",
        "Hypertrophy_Tempo": "2-1-2-0",
        "Power_Tempo": "1-0-X-0",
        "Joint_Flag": "Lower Back"
    },
    "Vertical Pull": {
        "Regression": "Band-Assisted Pull-Up",
        "Standard": "Strict Bodyweight Pull-Up",
        "Progression": "Weighted Pull-Up / Muscle-Up",
        "Primary_Equipment": "Pull-Up Bar",
        "Fallback_Equipment": "Resistance Bands",
        "Fallback_Exercise": "Banded Lat Pulldown",
        "Hypertrophy_Tempo": "3-0-1-1",
        "Power_Tempo": "X-0-1-0",
        "Joint_Flag": "Shoulder / Wrist"
    },
    "Rotational & Core": {
        "Regression": "Pallof Press Hold",
        "Standard": "Diagonal Cable Chops",
        "Progression": "Rotational Med-Ball Scoop Throw",
        "Primary_Equipment": "Cables",
        "Fallback_Equipment": "Medicine Ball",
        "Fallback_Exercise": "Med-Ball Wall Slam",
        "Hypertrophy_Tempo": "2-1-2-0",
        "Power_Tempo": "X-0-X-0",
        "Joint_Flag": "Lower Back"
    }
}

SPORT_WARMUPS = {
    "Racket Sports / Golf": [
        "Wrist & Forearm Dynamic Rotations",
        "Thoracic Spine Openers (Transverse Plane)",
        "Lateral Multi-Directional Shuttles"
    ],
    "Soccer": [
        "Dynamic Hamstring Sweeps & Adductor Mobilization",
        "Ankle Mobility & Single-Leg Balance Hops",
        "Multi-Directional Change of Direction (COD) Shuttles"
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
# 3. SIDEBAR HUD CONTROLS
# ==========================================
st.sidebar.title("⚡ AthleteIQ Engine Controls")

st.sidebar.markdown("### 🏃 Athlete Profile")
sport = st.sidebar.selectbox("Select Sport Demands", ["Soccer", "Basketball", "Racket Sports / Golf", "General Fitness"])
season = st.sidebar.radio("Seasonal Phase", ["Off-Season", "In-Season"])
days_to_game = st.sidebar.slider("Days Until Match", 1, 7, 3) if season == "In-Season" else 0

st.sidebar.markdown("### 🩹 Active Pain / Injuries")
active_pain = st.sidebar.multiselect("Flag Pain Areas", ["Knee", "Hamstring / Groin", "Shoulder / Wrist", "Lower Back"])

st.sidebar.markdown("### 🏋️ Facility & Equipment")
available_eq = st.sidebar.multiselect(
    "Available Gear", 
    ["Barbell", "Dumbbells", "Kettlebell", "Cables", "Rings", "Medicine Ball", "Pull-Up Bar", "Resistance Bands"],
    default=["Barbell", "Dumbbells", "Cables", "Pull-Up Bar"]
)

# ==========================================
# 4. PERIODIZATION & DECISION LOGIC
# ==========================================
def get_periodization(season_phase, game_days):
    if season_phase == "In-Season":
        if game_days <= 1:
            return {"sets": 2, "reps": "2-3", "intent": "Neural Primer / Recovery", "vol": "-60%", "tempo_type": "Power_Tempo"}
        elif game_days <= 3:
            return {"sets": 3, "reps": "3-4", "intent": "Power & Rate of Force", "vol": "-40%", "tempo_type": "Power_Tempo"}
        else:
            return {"sets": 3, "reps": "4-6", "intent": "Strength Maintenance", "vol": "-20%", "tempo_type": "Hypertrophy_Tempo"}
    else:
        return {"sets": 4, "reps": "8-12", "intent": "Structural Hypertrophy & Base", "vol": "100% (Baseline)", "tempo_type": "Hypertrophy_Tempo"}

period_params = get_periodization(season, days_to_game)

# ==========================================
# 5. TOP HUD METRICS (FULL KEYFRAME)
# ==========================================
st.title("🎯 AthleteIQ Dashboard")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""
        <div class="hud-card">
            <div class="hud-label">Sport Focus</div>
            <div class="hud-value">{sport.split('/')[0]}</div>
            <span class="badge-status">{season}</span>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="hud-card">
            <div class="hud-label">Training Intent</div>
            <div class="hud-value" style="font-size:16px; padding-top:4px;">{period_params['intent']}</div>
            <div class="hud-label">Match -{days_to_game}D</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="hud-card">
            <div class="hud-label">Volume Target</div>
            <div class="hud-value">{period_params['vol']}</div>
            <div class="hud-label">{period_params['sets']} Sets / Movement</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="hud-card">
            <div class="hud-label">Gear Match</div>
            <div class="hud-value">{len(available_eq)}/8</div>
            <div class="hud-label">Available Types</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
        <div class="hud-card">
            <div class="hud-label">Pain Flags</div>
            <div class="hud-value" style="color: {'#E53E3E' if active_pain else '#38A169'};">
                {'⚠️ ' + str(len(active_pain)) if active_pain else '🟢 0'}
            </div>
            <div class="hud-label">Active Regressions</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 6. TAB ARCHITECTURE (FULL UNIFIED ENGINE)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🏋️ Dynamic Workout Plan", 
    "🩹 Rehab & OPT Progression Matrix", 
    "📊 Athletic Assessment Engine",
    "📚 Complete Exercise & Equipment Library"
])

# TAB 1: DYNAMIC WORKOUT PLAN
with tab1:
    st.subheader(f"Session Program: {sport} ({season})")
    
    st.markdown("#### Phase 1: Sport-Specific Movement Prep")
    for i, step in enumerate(SPORT_WARMUPS.get(sport, SPORT_WARMUPS["General Fitness"]), 1):
        st.write(f"• **Step {i}**: {step}")
        
    st.markdown("---")
    st.markdown("#### Phase 2: Main Strength & Power Prescription")
    
    table_rows = []
    for pattern, info in EXERCISE_DATABASE.items():
        # Check pain flag
        has_flag = info["Joint_Flag"] in active_pain
        
        # Exercise Selection & Fallback Logic
        if has_flag:
            selected_exercise = info["Regression"]
            status_note = "⚠️ Regressed (Pain/Rehab)"
            prescribed_tempo = "3-2-3-0 (Control)"
        else:
            # Check primary equipment
            if info["Primary_Equipment"] in available_eq:
                selected_exercise = info["Standard"] if season == "Off-Season" else info["Progression"]
                status_note = "✅ Standard Target"
            elif info["Fallback_Equipment"] in available_eq:
                selected_exercise = info["Fallback_Exercise"]
                status_note = f"🔄 Equipment Swap ({info['Fallback_Equipment']})"
            else:
                selected_exercise = "Bodyweight Tempo Adaptation"
                status_note = "⚠️ Bodyweight Fallback"
            
            prescribed_tempo = info[period_params["tempo_type"]]

        table_rows.append({
            "Movement Pattern": pattern,
            "Prescribed Exercise": selected_exercise,
            "Target Sets": period_params["sets"],
            "Target Reps": period_params["reps"],
            "OPEX Tempo (E-P-C-P)": prescribed_tempo,
            "Equipment Needed": info["Primary_Equipment"],
            "Engine Decision": status_note
        })
        
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

# TAB 2: REHAB & OPT MATRIX
with tab2:
    st.subheader("NASM OPT Progression & Clinical Scaling Matrix")
    st.markdown("Systematic scaling pathways based on pain signals and performance milestones:")
    
    opt_rows = []
    for pattern, info in EXERCISE_DATABASE.items():
        opt_rows.append({
            "Pattern": pattern,
            "Phase 1: Regress (Isometric/Rehab)": info["Regression"],
            "Phase 2: Standard (Base Strength)": info["Standard"],
            "Phase 3: Progress (Explosive/Power)": info["Progression"],
            "Target Joint": info["Joint_Flag"]
        })
    st.table(pd.DataFrame(opt_rows))

# TAB 3: ATHLETIC ASSESSMENT
with tab3:
    st.subheader("Diagnostic Scorecard & Percentile Benchmarks")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        vj = st.number_input("Vertical Jump (Inches)", 10.0, 50.0, 24.0)
    with col_b:
        vo2 = st.number_input("VO2 Max (mL/kg/min)", 20.0, 90.0, 48.0)
    with col_c:
        asym = st.number_input("Asymmetry Index (%)", 0.0, 30.0, 4.5)
        
    st.markdown("#### Diagnostic Evaluation")
    if vj >= 28.0:
        st.success("✅ Explosive Power: High Athletic Output (≥80th Percentile)")
    else:
        st.info("ℹ️ Explosive Power: Baseline Capacity (Focus on Rate of Force Development)")
        
    if asym > 10.0:
        st.warning("⚠️ Movement Asymmetry Discrepancy (>10%). Prioritizing Unilateral Correctives.")
    else:
        st.success("✅ Symmetry Within Normal Range (<10%).")

# TAB 4: COMPLETE EXERCISE & GEAR LIBRARY
with tab4:
    st.subheader("Exercise System Database")
    st.markdown("Complete breakdown of movement patterns, primary equipment, fallback pathways, and tempo profiles:")
    
    full_lib = []
    for pattern, info in EXERCISE_DATABASE.items():
        full_lib.append({
            "Pattern": pattern,
            "Standard Movement": info["Standard"],
            "Primary Equipment": info["Primary_Equipment"],
            "Fallback Equipment": info["Fallback_Equipment"],
            "Fallback Exercise": info["Fallback_Exercise"],
            "Hypertrophy Tempo": info["Hypertrophy_Tempo"],
            "Power Tempo": info["Power_Tempo"]
        })
    st.dataframe(pd.DataFrame(full_lib), use_container_width=True)
