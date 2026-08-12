import streamlit as st
import pandas as pd
import numpy as np

# Set Streamlit Page Layout
st.set_page_config(page_title="AthleteIQ - Clinical S&C Engine", layout="wide")

# Custom CSS for Text Truncation Guards & UI Formatting
st.markdown("""
<style>
    .element-container, .stMetric, div[data-testid="stMetricValue"] {
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    .hud-card {
        background-color: #1e222a;
        border-left: 5px solid #00d26a;
        padding: 15px;
        margin-bottom: 12px;
        border-radius: 6px;
        color: #ffffff;
    }
    .hud-header { font-size: 1.1rem; font-weight: bold; color: #00d26a; }
    .hud-meta { font-size: 0.85rem; color: #a0aab8; }
</style>
""", unsafe_allow_html=True)

# Initialize Session State Database
if "athlete_profiles_db" not in st.session_state:
    st.session_state["athlete_profiles_db"] = {}

# Comprehensive Exercise Database mapped across vectors, tempos, equipment, and SSC types
EXERCISE_DATABASE = {
    "Lower Bilateral Push": [
        {"name": "Barbell Back Squat", "equip": ["Barbell"], "vector": "Sagittal", "ssc": "None", "opt_phase": "Strength"},
        {"name": "Goblet Squat (Heel Elevated)", "equip": ["Dumbbell", "Kettlebell"], "vector": "Sagittal", "ssc": "None", "opt_phase": "Stabilization"},
        {"name": "Spanish Squat (Isometric Hold)", "equip": ["Bands"], "vector": "Sagittal", "ssc": "None", "opt_phase": "Stabilization"}
    ],
    "Lower Unilateral Push": [
        {"name": "Bulgarian Split Squat", "equip": ["Dumbbell", "Barbell", "Bodyweight"], "vector": "Sagittal", "ssc": "None", "opt_phase": "Strength"},
        {"name": "Step-Up with Knee Drive", "equip": ["Dumbbell", "Bodyweight"], "vector": "Sagittal", "ssc": "None", "opt_phase": "Stabilization"}
    ],
    "Upper Pressing": [
        {"name": "Barbell Bench Press", "equip": ["Barbell"], "vector": "Horizontal", "ssc": "None", "opt_phase": "Strength"},
        {"name": "Landmine Angled Press", "equip": ["Barbell"], "vector": "Angled", "ssc": "None", "opt_phase": "Stabilization"},
        {"name": "Neutral Grip DB Overhead Press", "equip": ["Dumbbell"], "vector": "Vertical", "ssc": "None", "opt_phase": "Strength"}
    ],
    "Plyometrics": [
        {"name": "Depth Jumps", "equip": ["Bodyweight"], "vector": "Vertical", "ssc": "Fast", "opt_phase": "Power"},
        {"name": "Box Jumps (Non-Countermovement)", "equip": ["Bodyweight"], "vector": "Vertical", "ssc": "Slow", "opt_phase": "Power"},
        {"name": "Sub-Maximal Pogo Hops", "equip": ["Bodyweight"], "vector": "Vertical", "ssc": "Slow", "opt_phase": "Stabilization"}
    ],
    "Warm-up / Correctives": [
        {"name": "Animal Flow - Beast Reach to Crab Extension", "equip": ["Bodyweight"], "vector": "Multi-Planar", "ssc": "None", "opt_phase": "Stabilization"},
        {"name": "Band Face Pull with Thoracic Extension", "equip": ["Bands"], "vector": "Horizontal", "ssc": "None", "opt_phase": "Stabilization"},
        {"name": "Short-Foot Arch Activation & Ankle Mobilization", "equip": ["Bodyweight"], "vector": "Sagittal", "ssc": "None", "opt_phase": "Stabilization"}
    ]
}

class AthleteIQEngine:
    def __init__(self, profile):
        self.p = profile

    def evaluate_biomechanics(self):
        warnings = []
        regressions = {}
        
        # Ankle Dorsiflexion Gate
        if self.p.get("rom_ankle", 30) < 25:
            warnings.append("Ankle Dorsiflexion < 25° detected: Elevated heel / Goblet Squat enforced.")
            regressions["Lower Bilateral Push"] = "Goblet Squat (Heel Elevated)"
            
        # Shoulder Overhead Flexion Gate
        if self.p.get("rom_shoulder", 180) < 155:
            warnings.append("Shoulder Flexion < 155° detected: Vertical Barbell Overhead Press blocked.")
            regressions["Upper Pressing"] = "Landmine Angled Press"
            
        # Asymmetry / Single-Leg Jump Disparity Gate
        if self.p.get("jump_asymmetry", 0) > 10.0:
            warnings.append("Single-Leg Jump Asymmetry > 10%: Swapped primary squat to Unilateral Corrective.")
            regressions["Lower Bilateral Push"] = "Bulgarian Split Squat"
            
        # Knee / Injury Override Gate
        if "Knee" in self.p.get("injuries", []):
            warnings.append("Active Knee Trauma: Enforcing isometric Spanish Squat protocol.")
            regressions["Lower Bilateral Push"] = "Spanish Squat (Isometric Hold)"
            
        return warnings, regressions

    def generate_program(self):
        warnings, regressions = self.evaluate_biomechanics()
        program = []
        
        # 1. Warm-Up Block (Animal Flow + Corrective Activation)
        program.append({
            "block": "Warm-Up & RNT Correctives",
            "exercise": "Animal Flow - Beast Reach to Crab Extension",
            "sets": 2, "reps": "60 sec flow", "tempo": "2-2-2-0", "intensity": "Mobility/RNT"
        })
        if self.p.get("posture_rounded_shoulders", False):
            program.append({
                "block": "Warm-Up & RNT Correctives",
                "exercise": "Band Face Pull with Thoracic Extension",
                "sets": 2, "reps": "15", "tempo": "2-1-1-2", "intensity": "Activation"
            })

        # 2. Plyometric / Power Block (SSC Gating)
        squat_1rm = self.p.get("squat_1rm", 100)
        bw = self.p.get("bodyweight", 70)
        
        if (squat_1rm / max(bw, 1)) >= 1.5 and "Knee" not in self.p.get("injuries", []):
            plyo = "Depth Jumps"
            tempo = "0-0-1-0"
        else:
            plyo = "Box Jumps (Non-Countermovement)"
            tempo = "1-1-1-0"
            
        program.append({
            "block": "Neural Power & Plyometrics",
            "exercise": plyo,
            "sets": 3, "reps": "5", "tempo": tempo, "intensity": "Maximal Intent"
        })

        # 3. Main Strength Compound Block
        primary_squat = regressions.get("Lower Bilateral Push", "Barbell Back Squat")
        
        # In-Season Load Scaling
        if self.p.get("season_phase") == "In-Season" and self.p.get("club_hours", 0) >= 10:
            sets, reps, intensity = 3, 3, "75% 1RM (Low Volume Maintenance)"
        else:
            sets, reps, intensity = 4, 6, "82.5% 1RM (Hypertrophy / Max Strength)"

        program.append({
            "block": "Primary Strength Compound",
            "exercise": primary_squat,
            "sets": sets, "reps": str(reps), "tempo": "3-1-1-0", "intensity": intensity
        })

        # 4. Upper Body Pressing Vector
        upper_press = regressions.get("Upper Pressing", "Barbell Bench Press")
        program.append({
            "block": "Upper Body Strength Vector",
            "exercise": upper_press,
            "sets": 3, "reps": "8", "tempo": "2-1-1-0", "intensity": "75% 1RM"
        })

        # 5. ESD Finisher (Calculated from MAS / Cooper Test)
        mas_speed = self.p.get("mas_speed", 3.5) # m/s
        target_shuttle = round(mas_speed * 15, 1) # 15-sec shuttle distance
        program.append({
            "block": "Energy System Development (ESD)",
            "exercise": f"100% MAS Shuttle Sprints ({target_shuttle}m shuttles)",
            "sets": 2, "reps": "8 intervals (15s work / 15s rest)", "tempo": "Continuous", "intensity": f"MAS Target: {mas_speed} m/s"
        })

        return warnings, program

# STREAMLIT UI LAYOUT
st.title(" AthleteIQ - Clinical S&C & Biomechanics Engine")

st.sidebar.header("Athlete Profile & Diagnostics")
profile_name = st.sidebar.text_input("Profile Name", "Athlete Alpha")
season_phase = st.sidebar.selectbox("Season Phase", ["Off-Season", "In-Season"])
club_hours = st.sidebar.number_input("Weekly Club Training Hours", 0, 30, 12)
bodyweight = st.sidebar.number_input("Bodyweight (kg)", 40, 150, 75)
squat_1rm = st.sidebar.number_input("Squat 1RM (kg)", 0, 300, 120)

st.sidebar.subheader("Clinical Screening & ROM")
rom_ankle = st.sidebar.slider("Ankle Dorsiflexion (°)", 10, 45, 20)
rom_shoulder = st.sidebar.slider("Shoulder Overhead Flexion (°)", 120, 180, 150)
jump_asymmetry = st.sidebar.slider("Single-Leg Jump Disparity (%)", 0.0, 30.0, 12.5)
posture_rounded = st.sidebar.checkbox("Static Posture: Upper Crossed / Rounded Shoulders", True)
injuries = st.sidebar.multiselect("Active Injuries / Pain Flags", ["Knee", "Shoulder", "Lower Back", "Ankle"], default=["Knee"])

st.sidebar.subheader("Performance Test Targets")
mas_speed = st.sidebar.number_input("Maximal Aerobic Speed - MAS (m/s)", 2.0, 6.0, 3.8)

# Construct Profile Dictionary
athlete_profile = {
    "name": profile_name,
    "season_phase": season_phase,
    "club_hours": club_hours,
    "bodyweight": bodyweight,
    "squat_1rm": squat_1rm,
    "rom_ankle": rom_ankle,
    "rom_shoulder": rom_shoulder,
    "jump_asymmetry": jump_asymmetry,
    "posture_rounded_shoulders": posture_rounded,
    "injuries": injuries,
    "mas_speed": mas_speed
}

# Run Engine Logic
engine = AthleteIQEngine(athlete_profile)
warnings, generated_plan = engine.generate_program()

# DISPLAY GENERATED RESULTS
st.header(f"Prescribed Macrocycle Block for: {profile_name}")

if warnings:
    st.subheader(" Clinical & Biomechanical Alerts Driven by Diagnostic Inputs")
    for w in warnings:
        st.warning(w)

st.subheader(" Generated HUD Prescription Cards")
for item in generated_plan:
    st.markdown(f"""
    <div class="hud-card">
        <div class="hud-header">[{item['block']}] {item['exercise']}</div>
        <div class="hud-meta">
            <b>Sets/Reps:</b> {item['sets']} x {item['reps']} &nbsp;|&nbsp; 
            <b>OPEX Tempo:</b> <code style="color:#00d26a;">{item['tempo']}</code> &nbsp;|&nbsp; 
            <b>Target Intensity:</b> {item['intensity']}
        </div>
    </div>
    """, unsafe_allow_html=True)
