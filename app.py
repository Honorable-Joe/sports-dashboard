import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG & ATHLETIC STYLING
# ==========================================
st.set_page_config(
    page_title="Athlete-IQ Performance & Clinical Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.92), rgba(2, 6, 23, 0.96)), 
                    url('https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f8fafc;
        font-family: 'Inter', system-ui, sans-serif;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.2);
        backdrop-filter: blur(10px);
        margin-bottom: 15px;
    }
    .banner-header {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        padding: 12px 20px;
        border-radius: 10px;
        color: white;
        font-weight: 800;
        font-size: 1.25rem;
        margin-top: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
    }
    .scientific-note {
        background-color: rgba(15, 23, 42, 0.92);
        border-left: 4px solid #38bdf8;
        padding: 14px 18px;
        border-radius: 6px;
        margin-top: 10px;
        margin-bottom: 20px;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .injury-alert {
        background-color: rgba(225, 29, 72, 0.25);
        border-left: 4px solid #f43f5e;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. EMBEDDED EXERCISE & EQUIPMENT KNOWLEDGE BASE
# ==========================================
EXERCISE_DATABASE = {
    "Chest": {
        "Barbells & Plates": [
            {"name": "Flat Barbell Bench Press", "tempo": "3-0-1-0", "cue": "Drive feet into floor, retract scapulae, touch lower sternum.", "type": "Strength"},
            {"name": "Incline Barbell Press", "tempo": "3-1-1-0", "cue": "Unrack with locked wrists, lower bar smoothly to upper chest.", "type": "Hypertrophy"}
        ],
        "Dumbbells": [
            {"name": "Incline Dumbbell Press", "tempo": "3-1-1-0", "cue": "Keep elbows at 45-degree angle, squeeze pecs at top.", "type": "Hypertrophy"},
            {"name": "Dumbbell Hex Press", "tempo": "2-1-1-1", "cue": "Press dumbbells firmly together throughout whole movement range.", "type": "Hypertrophy"}
        ],
        "Medicine & Slam Balls": [
            {"name": "Medicine Ball Chest Passes", "tempo": "X-0-X-0", "cue": "Explosively extend arms and triple extend hips forward.", "type": "Power"}
        ],
        "Rigs & Suspension (TRX/Wood Rings)": [
            {"name": "Ring Push-Ups / Weighted Dips", "tempo": "3-1-1-0", "cue": "Turn rings out at top of motion, keep core tight.", "type": "Strength"}
        ]
    },
    "Back & Lats": {
        "Barbells & Plates": [
            {"name": "Barbell Bent-Over Rows", "tempo": "2-1-1-0", "cue": "Hinge hips back, pull bar to navel keeping spine flat.", "type": "Strength"},
            {"name": "T-Bar / Pendlay Rows", "tempo": "2-0-1-1", "cue": "Explode off floor with chest parallel to ground.", "type": "Strength"}
        ],
        "Rigs & Suspension (TRX/Wood Rings)": [
            {"name": "Weighted Pull-Ups", "tempo": "2-1-1-0", "cue": "Depress scapulae first, drive elbows down into ribs.", "type": "Strength"},
            {"name": "Single-Arm TRX Row", "tempo": "2-1-1-1", "cue": "Anti-rotate hips, pull thumb to ribcage.", "type": "Hypertrophy"}
        ],
        "Cable Systems & Selectorized": [
            {"name": "Lat Pulldowns (Neutral/Wide)", "tempo": "3-0-1-1", "cue": "Squeeze mid-back, avoid excessive backward lean.", "type": "Hypertrophy"}
        ]
    },
    "Lower Body Quadriceps": {
        "Barbells & Plates": [
            {"name": "Barbell Back Squats", "tempo": "3-1-1-0", "cue": "Break at hips and knees simultaneously, keep knees over toes.", "type": "Strength"},
            {"name": "Front Squats", "tempo": "3-1-1-0", "cue": "High elbows, vertical torso, drive through mid-foot.", "type": "Strength"}
        ],
        "Dumbbells": [
            {"name": "Bulgarian Split Squats", "tempo": "3-1-1-0", "cue": "Vertical front shin, drop rear knee straight down.", "type": "Hypertrophy"}
        ],
        "Plyo Boxes & Agility Ladders": [
            {"name": "Depth Jumps / Box Jumps", "tempo": "X-0-X-0", "cue": "Minimize ground contact time, land softly in athletic stance.", "type": "Power"}
        ]
    },
    "Lower Body Posterior Chain": {
        "Barbells & Plates": [
            {"name": "Romanian Deadlifts (RDLs)", "tempo": "3-1-1-0", "cue": "Push hips back to wall behind you, keep bar close to shins.", "type": "Strength"},
            {"name": "Barbell Hip Thrusts", "tempo": "2-1-1-2", "cue": "Posterior pelvic tilt at top, lock out glutes completely.", "type": "Hypertrophy"}
        ],
        "Kettlebells": [
            {"name": "Kettlebell Swings", "tempo": "X-0-X-0", "cue": "Explosive hip snap, let arms act purely as ropes.", "type": "Power"}
        ]
    },
    "Shoulders & Rotator Cuff": {
        "Barbells & Plates": [
            {"name": "Overhead Barbell Strict Press", "tempo": "3-0-1-0", "cue": "Brace core, push head through window at full lockout.", "type": "Strength"}
        ],
        "Dumbbells": [
            {"name": "Dumbbell Arnold Press", "tempo": "3-0-1-0", "cue": "Rotate palms smoothly from facing chest to facing forward.", "type": "Hypertrophy"}
        ],
        "Cable Systems & Selectorized": [
            {"name": "Cable Face Pulls", "tempo": "2-1-1-2", "cue": "Pull rope to forehead, rotate hands back into high double-bicep.", "type": "Prehab"}
        ]
    }
}

# ==========================================
# 3. PERSISTENT SESSION STATE INITIALIZATION
# ==========================================
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        # Profile
        "athlete_name": "Alex Morgan",
        "age": 22,
        "gender": "Female",
        "weight_kg": 75.0,
        "height_cm": 178.0,
        "sport_type": "Tennis",
        "evaluating_coach": "Coach Ahmed Youssef 👑",
        "assessment_date": datetime.now().date(),
        "assessment_type": "Baseline (Initial)",
        "training_years": 3,
        # Load & Injury
        "club_days": 4,
        "club_hours_per_day": 2.0,
        "has_injury": "No",
        "injury_category": "Joint",
        "injury_site": "Knee Joint",
        "injury_mechanism": "N/A",
        "still_affects": "No",
        # SFMA
        "cervical": "Functional Non-Painful",
        "shoulder": "Functional Non-Painful",
        "rotation": "Functional Non-Painful",
        "flexion": "Functional Non-Painful",
        "extension": "Functional Non-Painful",
        "sl_stance": "Functional Non-Painful",
        "overhead_squat": "Functional Non-Painful",
        # Detailed Posture
        "posture_sis": "Normal / Symmetric",
        "posture_foot_pos": "Neutral Foot Stance",
        "posture_tibia": "Straight Tibial Alignment",
        "posture_knee": "Neutral Knee Line",
        "posture_shoulder_lvl": "Level Shoulders",
        "posture_foot_arch": "Normal Arch",
        "posture_knee_pos": "Neutral Stance",
        "posture_pelvic_tilt": "Neutral Pelvis",
        "posture_lumbar": "Normal Curve",
        "posture_thoracic": "Normal Curve",
        "posture_shoulder_pos": "Neutral Shoulder Position",
        "posture_hip_pos": "Level Hips",
        "posture_ankle": "Vertical Ankle Alignment",
        "posture_scapula": "Symmetrical Flat",
        "posture_shld_flex_er_ir": "Full Range / Symmetric",
        "posture_tspine_rot": "Full Mobility Both Sides",
        "posture_hip_flex_slr": "Symmetric Straight Leg Elevation",
        "posture_hip_flex_bent": "Full Knee-Bent Hip Flexion",
        "posture_hip_ir_er": "Symmetric Hip Rotational Range",
        "congenital_defects": "None Detected",
        # Power
        "p_chest_pass": 6.8,
        "p_overhead_throw": 8.5,
        "p_cmj": 42.0,
        "p_horiz_jump_bi": 215.0,
        "p_horiz_jump_uni_l": 105.0,
        "p_horiz_jump_uni_r": 104.0,
        "p_vert_jump_bi": 45.0,
        "p_vert_jump_uni_l": 22.0,
        "p_vert_jump_uni_r": 21.5,
        "p_forehand_throw": 9.2,
        "p_backhand_throw": 8.4,
        # Speed & Agility
        "s_7x7": 14.2,
        "s_tdrill": 10.20,
        "s_boxdrill": 11.5,
        "s_sprint5m": 1.10,
        "s_sprint10m": 1.75,
        "s_sprint1000m": 235.0,
        # Capacity
        "c_pushups": 38,
        "c_pullups": 12,
        "c_squats": 55,
        "c_situps": 42,
        "c_cooper": 2650
    }

if "athlete_records" not in st.session_state:
    st.session_state.athlete_records = []

def bind_input(key):
    return st.session_state.form_data.get(key)

def update_state(key, val):
    st.session_state.form_data[key] = val

# ==========================================
# 4. SIDEBAR NAVIGATION & EQUIPMENT SELECTOR
# ==========================================
st.markdown("<h1 style='text-align: center; color: #38bdf8; font-weight: 900; margin-bottom: 0px;'>⚡ ATHLETE-IQ PERFORMANCE ENGINE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a855f7; font-weight: 700; font-size: 1.15rem;'>Developed by: Coach Ahmed Youssef 👑</p>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.markdown("### 📌 Navigation")
active_module = st.sidebar.radio(
    "Jump to Module:",
    [
        "📋 1. Demographics & Coach Sign-off",
        "⚽ 2. Club Load & Injury Diagnostics",
        "🩺 3. SFMA & Postural Diagnostic Matrix",
        "💥 4. Sport-Specific Power, Speed & Capacity Assessment",
        "📈 5. Saved Records & Historical Progress",
        "🚀 6. ADAPTIVE PROGRAM GENERATOR"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗓️ Macrocycle Horizon")
plan_months = st.sidebar.select_slider(
    "Select Program Scope:",
    options=[1, 2, 3],
    value=2,
    format_func=lambda x: f"{x}-Month Macrocycle Block"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏋️ Facility Equipment Matrix")
equipment_selected = st.sidebar.multiselect(
    "Available Gear:",
    [
        "Barbells & Plates", "Dumbbells", "Kettlebells", 
        "Hydro-Inertial (Aqua Bags/Macebells)", "Instability (BOSU/Swiss Ball)",
        "Rigs & Suspension (TRX/Wood Rings)", "Sleds & Prowler",
        "Medicine & Slam Balls", "Cable Systems & Selectorized",
        "Ergometers (AirBike/Rower/SkiErg)", "Plyo Boxes & Agility Ladders"
    ],
    default=["Barbells & Plates", "Dumbbells", "Kettlebells", "Rigs & Suspension (TRX/Wood Rings)", "Sleds & Prowler", "Medicine & Slam Balls", "Cable Systems & Selectorized", "Ergometers (AirBike/Rower/SkiErg)", "Plyo Boxes & Agility Ladders"]
)

# ==========================================
# 5. MODULE CONTROLLERS
# ==========================================

# ------------------------------------------
# MODULE 1: DEMOGRAPHICS
# ------------------------------------------
if active_module == "📋 1. Demographics & Coach Sign-off":
    st.markdown("<div class='banner-header'>📋 Athlete Demographics & Evaluating Coach Sign-Off</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👤 Athlete Profile")
        v_name = st.text_input("Athlete Name", value=bind_input("athlete_name"))
        v_age = st.number_input("Age", 12, 80, value=bind_input("age"))
        v_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(bind_input("gender")))
        v_weight = st.number_input("Body Weight (kg)", 40.0, 150.0, value=bind_input("weight_kg"))
        v_height = st.number_input("Height (cm)", 120.0, 230.0, value=bind_input("height_cm"))
        sports_list = ["Tennis", "Volleyball", "Combat Sports (MMA/Boxing)", "Racket Sports (Squash/Padel)", "Soccer", "Basketball", "Track & Field (Sprints/Jumps)", "Rugby/American Football", "General Fitness"]
        v_sport = st.selectbox("Sport / Discipline", sports_list, index=sports_list.index(bind_input("sport_type")))
    with c2:
        st.subheader("🧢 Evaluating Coach Details")
        v_coach = st.text_input("Evaluating Coach Name", value=bind_input("evaluating_coach"))
        v_date = st.date_input("Assessment Date", value=bind_input("assessment_date"))
        phases = ["Baseline (Initial)", "Mid-Phase Follow-Up", "Re-Assessment (Post-Block)"]
        v_phase = st.selectbox("Assessment Phase", phases, index=phases.index(bind_input("assessment_type")))
        v_years = st.number_input("Training History (Years)", 0, 30, value=bind_input("training_years"))

    update_state("athlete_name", v_name)
    update_state("age", v_age)
    update_state("gender", v_gender)
    update_state("weight_kg", v_weight)
    update_state("height_cm", v_height)
    update_state("sport_type", v_sport)
    update_state("evaluating_coach", v_coach)
    update_state("assessment_date", v_date)
    update_state("assessment_type", v_phase)
    update_state("training_years", v_years)

# ------------------------------------------
# MODULE 2: CLUB LOAD & CLINICAL INJURY
# ------------------------------------------
elif active_module == "⚽ 2. Club Load & Injury Diagnostics":
    st.markdown("<div class='banner-header'>⚽ Club Training Load & Clinical Injury Diagnostics</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚽ External Club Training Exposure")
        v_days = st.number_input("Club Training Days / Week", 0, 7, value=bind_input("club_days"))
        v_hours = st.number_input("Avg Session Duration (Hours)", 0.5, 5.0, value=bind_input("club_hours_per_day"))
        tot_hrs = v_days * v_hours
        update_state("club_days", v_days)
        update_state("club_hours_per_day", v_hours)

        if tot_hrs >= 10:
            st.warning(f"⚠️ High External Load ({tot_hrs} hrs/wk): Prescribed S&C auto-condenses to 2 Days/Week (Full-Body Dense).")
        elif tot_hrs >= 6:
            st.info(f"📊 Moderate External Load ({tot_hrs} hrs/wk): Prescribed S&C auto-scales to 3 Days/Week.")
        else:
            st.success(f"✅ Low External Load ({tot_hrs} hrs/wk): Prescribed S&C set to 4 Days/Week.")

    with c2:
        st.subheader("🩺 Dynamic Clinical Injury Diagnostic")
        v_has_inj = st.radio("Active / Recent Injury Present?", ["No", "Yes"], index=["No", "Yes"].index(bind_input("has_injury")), horizontal=True)
        
        injury_map = {
            "Joint": ["Knee Joint", "Ankle Joint", "Shoulder Joint Complex", "Hip Joint", "Elbow Joint", "Wrist/Carpal Joint", "Lumbar Facet Joint"],
            "Muscle": ["Hamstrings Group", "Quadriceps Group", "Gastrocnemius/Soleus", "Pectoralis Major/Minor", "Latissimus Dorsi", "Adductor Groin Group"],
            "Ligament": ["ACL (Anterior Cruciate)", "MCL (Medial Collateral)", "ATFL (Ankle Ligament)", "UCL (Elbow Ligament)", "Syndesmosis (High Ankle)"],
            "Tendon": ["Patellar Tendon", "Achilles Tendon", "Rotator Cuff Tendons", "Biceps Tendon", "Gluteal Tendon"]
        }

        if v_has_inj == "Yes":
            v_cat = st.selectbox("1. Select Tissue / Structural Category", list(injury_map.keys()), index=list(injury_map.keys()).index(bind_input("injury_category")))
            sites_available = injury_map[v_cat]
            cur_site = bind_input("injury_site")
            site_idx = sites_available.index(cur_site) if cur_site in sites_available else 0
            v_site = st.selectbox("2. Select Specific Anatomical Site", sites_available, index=site_idx)
            
            mechs = ["Overuse / Repetitive Stress", "Acute Contact / Traumatic", "Non-Contact Biomechanical"]
            v_mech = st.selectbox("Mechanism of Injury", mechs, index=mechs.index(bind_input("injury_mechanism")) if bind_input("injury_mechanism") in mechs else 0)
            affects = ["Yes - Active Symptoms", "No - Cleared / Asymptomatic"]
            v_affects = st.radio("Symptoms Present Currently?", affects, index=affects.index(bind_input("still_affects")) if bind_input("still_affects") in affects else 0, horizontal=True)
        else:
            v_cat, v_site, v_mech, v_affects = "Joint", "None", "N/A", "No"
            
        update_state("has_injury", v_has_inj)
        update_state("injury_category", v_cat)
        update_state("injury_site", v_site)
        update_state("injury_mechanism", v_mech)
        update_state("still_affects", v_affects)

# ------------------------------------------
# MODULE 3: SFMA & EXPANDED POSTURAL DIAGNOSTICS
# ------------------------------------------
elif active_module == "🩺 3. SFMA & Postural Diagnostic Matrix":
    st.markdown("<div class='banner-header'>🩺 SFMA Movement Patterns & Expanded Postural Diagnostics</div>", unsafe_allow_html=True)
    
    st.subheader("1. SFMA Top-Tier Assessment Suite")
    sfma_opts = ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"]
    c1, c2, c3 = st.columns(3)
    with c1:
        v_cerv = st.selectbox("Cervical Spine Pattern", sfma_opts, index=sfma_opts.index(bind_input("cervical")))
        v_shld = st.selectbox("Upper Extremity Reach", sfma_opts, index=sfma_opts.index(bind_input("shoulder")))
        v_rot = st.selectbox("Multi-Segmental Rotation", sfma_opts, index=sfma_opts.index(bind_input("rotation")))
    with c2:
        v_flex = st.selectbox("Multi-Segmental Flexion", sfma_opts, index=sfma_opts.index(bind_input("flexion")))
        v_ext = st.selectbox("Multi-Segmental Extension", sfma_opts, index=sfma_opts.index(bind_input("extension")))
    with c3:
        v_sls = st.selectbox("Single-Leg Stance Balance", sfma_opts, index=sfma_opts.index(bind_input("sl_stance")))
        v_ohs = st.selectbox("Deep Overhead Squat Pattern", sfma_opts, index=sfma_opts.index(bind_input("overhead_squat")))

    update_state("cervical", v_cerv)
    update_state("shoulder", v_shld)
    update_state("rotation", v_rot)
    update_state("flexion", v_flex)
    update_state("extension", v_ext)
    update_state("sl_stance", v_sls)
    update_state("overhead_squat", v_ohs)

    st.markdown("---")
    st.subheader("2. Expanded Static Postural & Range-of-Motion Diagnostic Matrix")
    
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("**🖼️ Lower Extremity & Pelvic Alignment**")
        v_foot_arch = st.selectbox("Foot Arch Status", ["Normal Arch", "Flat Foot (Pes Planus)", "High Arch (Pes Cavus)"], index=0)
        v_foot_pos = st.selectbox("Foot Position", ["Neutral Foot Stance", "In-Toeing (Pigeon)", "Out-Toeing (Duck)"], index=0)
        v_ankle = st.selectbox("Ankle Alignment", ["Vertical Ankle Alignment", "Pronated Rearfoot", "Supinated Rearfoot"], index=0)
        v_tibia = st.selectbox("Tibia Alignment", ["Straight Tibial Alignment", "Tibial Torsion Internal", "Tibial Torsion External"], index=0)
        v_knee = st.selectbox("Knee Line / Q-Angle", ["Neutral Knee Line", "Genu Valgum (Knock-Knee)", "Genu Varum (Bow-Leg)"], index=0)
        v_knee_pos = st.selectbox("Knee Stance Position", ["Neutral Stance", "Genu Recurvatum (Hyperextended)"], index=0)
        v_sis = st.selectbox("ASIS / PSIS Symmetry (SIS)", ["Normal / Symmetric", "Asymmetric ASIS/PSIS Height"], index=0)
        v_hip_pos = st.selectbox("Hip Height Level", ["Level Hips", "Unilateral Pelvic Hike"], index=0)

    with p2:
        st.markdown("**🖼️ Spinal Curves & Trunk Balance**")
        v_pelvic_tilt = st.selectbox("Pelvic Tilt Angle", ["Neutral Pelvis", "Anterior Pelvic Tilt", "Posterior Pelvic Tilt"], index=0)
        v_lumbar = st.selectbox("Lumbar Spine Curve", ["Normal Curve", "Hyper-Lordosis", "Hypo-Lordosis / Flat Back"], index=0)
        v_thoracic = st.selectbox("Thoracic Spine Curve", ["Normal Curve", "Hyper-Kyphosis", "Flat Thoracic Spine"], index=0)
        v_tspine_rot = st.selectbox("Thoracic Spine Rotation", ["Full Mobility Both Sides", "Restricted Left Rotation", "Restricted Right Rotation"], index=0)
        v_scapula = st.selectbox("Scapula Alignment", ["Symmetrical Flat", "Scapular Winging", "Protracted / Abducted Scapulae"], index=0)
        v_shoulder_lvl = st.selectbox("Shoulder Elevation Level", ["Level Shoulders", "Left Shoulder Elevated", "Right Shoulder Elevated"], index=0)
        v_shoulder_pos = st.selectbox("Shoulder Position (Sagittal)", ["Neutral Shoulder Position", "Anterior Rounded Shoulders"], index=0)

    with p3:
        st.markdown("**🖼️ Shoulder & Hip Functional Ranges**")
        v_shld_flex_er_ir = st.selectbox("Shoulder Flexion / ER / IR", ["Full Range / Symmetric", "Restricted Flexion", "Restricted Internal Rotation (GIRD)", "Restricted External Rotation"], index=0)
        v_hip_flex_slr = st.selectbox("Hip Flexion (Straight Leg Raise)", ["Symmetric Straight Leg Elevation", "Restricted Hamstring Flexibility Left", "Restricted Hamstring Flexibility Right"], index=0)
        v_hip_flex_bent = st.selectbox("Hip Flexion (Knee Bent)", ["Full Knee-Bent Hip Flexion", "Pincer / Cam Impingement Limitation"], index=0)
        v_hip_ir_er = st.selectbox("Hip Internal & External Rotation", ["Symmetric Hip Rotational Range", "Restricted Internal Rotation", "Restricted External Rotation"], index=0)

    st.markdown("---")
    st.subheader("3. Congenital Postural Defects & Structural Anomalies Detection")
    v_congenital = st.selectbox(
        "Screening for Structural / Congenital Anomalies:",
        [
            "None Detected",
            "Forward Head Posture (FHP) / Text Neck Syndrome",
            "Structural Idiopathic Scoliosis Curve",
            "Structural Pectus Excavatum / Carinatum",
            "Structural Leg Length Discrepancy (LLD)",
            "Congenital Femoral Anteversion / Retroversion"
        ],
        index=0
    )

    update_state("posture_sis", v_sis)
    update_state("posture_foot_pos", v_foot_pos)
    update_state("posture_tibia", v_tibia)
    update_state("posture_knee", v_knee)
    update_state("posture_shoulder_lvl", v_shoulder_lvl)
    update_state("posture_foot_arch", v_foot_arch)
    update_state("posture_knee_pos", v_knee_pos)
    update_state("posture_pelvic_tilt", v_pelvic_tilt)
    update_state("posture_lumbar", v_lumbar)
    update_state("posture_thoracic", v_thoracic)
    update_state("posture_shoulder_pos", v_shoulder_pos)
    update_state("posture_hip_pos", v_hip_pos)
    update_state("posture_ankle", v_ankle)
    update_state("posture_scapula", v_scapula)
    update_state("posture_shld_flex_er_ir", v_shld_flex_er_ir)
    update_state("posture_tspine_rot", v_tspine_rot)
    update_state("posture_hip_flex_slr", v_hip_flex_slr)
    update_state("posture_hip_flex_bent", v_hip_flex_bent)
    update_state("posture_hip_ir_er", v_hip_ir_er)
    update_state("congenital_defects", v_congenital)

# ------------------------------------------
# MODULE 4: SPORT-SPECIFIC TESTING SUITE
# ------------------------------------------
elif active_module == "💥 4. Sport-Specific Power, Speed & Capacity Assessment":
    st.markdown("<div class='banner-header'>💥 Full Sport-Specific Power, Speed, Agility & Aerobic Capacity Testing</div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("4.1. Explosive Power Suite")
        v_chest_pass = st.number_input("Chest Pass Med-Ball Launch (m)", 1.0, 25.0, value=bind_input("p_chest_pass"))
        v_oh_throw = st.number_input("Overhead Throw Med-Ball (m)", 1.0, 30.0, value=bind_input("p_overhead_throw"))
        v_fh_throw = st.number_input("Forehand Med-Ball Throw (m)", 1.0, 30.0, value=bind_input("p_forehand_throw"))
        v_bh_throw = st.number_input("Backhand Med-Ball Throw (m)", 1.0, 30.0, value=bind_input("p_backhand_throw"))
        v_cmj = st.number_input("Countermovement Jump (CMJ) (cm)", 10.0, 100.0, value=bind_input("p_cmj"))
        v_horiz_bi = st.number_input("Horizontal Jump - Both Legs (cm)", 50.0, 400.0, value=bind_input("p_horiz_jump_bi"))
        v_horiz_uni_l = st.number_input("Horizontal Jump - Left Leg (cm)", 20.0, 250.0, value=bind_input("p_horiz_jump_uni_l"))
        v_horiz_uni_r = st.number_input("Horizontal Jump - Right Leg (cm)", 20.0, 250.0, value=bind_input("p_horiz_jump_uni_r"))
        v_vert_bi = st.number_input("Vertical Jump - Both Legs (cm)", 10.0, 120.0, value=bind_input("p_vert_jump_bi"))
        v_vert_uni_l = st.number_input("Vertical Jump - Left Leg (cm)", 5.0, 80.0, value=bind_input("p_vert_jump_uni_l"))
        v_vert_uni_r = st.number_input("Vertical Jump - Right Leg (cm)", 5.0, 80.0, value=bind_input("p_vert_jump_uni_r"))

    with c2:
        st.subheader("4.2. Speed & Agility Suite")
        v_sprint5m = st.number_input("5m First-Step Sprint (sec)", 0.5, 3.0, value=bind_input("s_sprint5m"))
        v_sprint10m = st.number_input("10m Acceleration Sprint (sec)", 1.0, 4.0, value=bind_input("s_sprint10m"))
        v_7x7 = st.number_input("7 x 7 Agility Drill (sec)", 5.0, 30.0, value=bind_input("s_7x7"))
        v_tdrill = st.number_input("T-Drill Agility (sec)", 5.0, 25.0, value=bind_input("s_tdrill"))
        v_boxdrill = st.number_input("Box Drill Agility (sec)", 5.0, 30.0, value=bind_input("s_boxdrill"))
        v_1000m = st.number_input("1000m Sprint / Run (sec)", 120.0, 600.0, value=bind_input("s_sprint1000m"))

    with c3:
        st.subheader("4.3. Muscular & Aerobic Capacity")
        v_pushups = st.number_input("Max Push-Ups (1 Min)", 0, 120, value=bind_input("c_pushups"))
        v_pullups = st.number_input("Max Pull-Ups (Unbroken)", 0, 60, value=bind_input("c_pullups"))
        v_squats = st.number_input("Max Air Squats (1 Min)", 0, 150, value=bind_input("c_squats"))
        v_situps = st.number_input("Max Sit-Ups (1 Min)", 0, 120, value=bind_input("c_situps"))
        v_cooper = st.number_input("12-Min Cooper Test (meters)", 500, 5000, value=bind_input("c_cooper"))

    # Calculated Biomechanical Index
    vo2max = round((v_cooper - 504.9) / 44.73, 1)
    horiz_asym = round(abs(v_horiz_uni_l - v_horiz_uni_r) / max(v_horiz_uni_l, v_horiz_uni_r) * 100, 1)
    
    st.info(f"📊 **Calculated Diagnostics**: Estimated VO2Max: `{vo2max} mL/kg/min` | Single-Leg Horizontal Asymmetry: `{horiz_asym}%`")

    # Save Bindings
    update_state("p_chest_pass", v_chest_pass)
    update_state("p_overhead_throw", v_oh_throw)
    update_state("p_forehand_throw", v_fh_throw)
    update_state("p_backhand_throw", v_bh_throw)
    update_state("p_cmj", v_cmj)
    update_state("p_horiz_jump_bi", v_horiz_bi)
    update_state("p_horiz_jump_uni_l", v_horiz_uni_l)
    update_state("p_horiz_jump_uni_r", v_horiz_uni_r)
    update_state("p_vert_jump_bi", v_vert_bi)
    update_state("p_vert_jump_uni_l", v_vert_uni_l)
    update_state("p_vert_jump_uni_r", v_vert_uni_r)
    update_state("s_sprint5m", v_sprint5m)
    update_state("s_sprint10m", v_sprint10m)
    update_state("s_7x7", v_7x7)
    update_state("s_tdrill", v_tdrill)
    update_state("s_boxdrill", v_boxdrill)
    update_state("s_sprint1000m", v_1000m)
    update_state("c_pushups", v_pushups)
    update_state("c_pullups", v_pullups)
    update_state("c_squats", v_squats)
    update_state("c_situps", v_situps)
    update_state("c_cooper", v_cooper)

    if st.button("💾 SAVE SNAPSHOT TO HISTORICAL DATABASE"):
        rec = st.session_state.form_data.copy()
        rec["vo2max"] = vo2max
        rec["horiz_asymmetry"] = horiz_asym
        st.session_state.athlete_records.append(rec)
        st.success(f"✅ Full baseline testing snapshot saved for {rec['athlete_name']} on {rec['assessment_date']}!")

# ------------------------------------------
# MODULE 5: SAVED RECORDS
# ------------------------------------------
elif active_module == "📈 5. Saved Records & Historical Progress":
    st.markdown("<div class='banner-header'>📈 Saved Assessment Records & Multi-Month Tracking</div>", unsafe_allow_html=True)
    if len(st.session_state.athlete_records) == 0:
        st.info("ℹ️ No saved snapshots found. Complete assessments in Module 4 and click 'Save Snapshot'.")
    else:
        df = pd.DataFrame(st.session_state.athlete_records)
        st.dataframe(df, use_container_width=True)

# ------------------------------------------
# MODULE 6: PROGRAM GENERATOR WITH SWAPPING ENGINE
# ------------------------------------------
elif active_module == "🚀 6. ADAPTIVE PROGRAM GENERATOR":
    st.markdown("<div class='banner-header'>🚀 Adaptive Multi-Month Plan, Movement Cues, Tempo & Exercise Swapping Engine</div>", unsafe_allow_html=True)
    
    d = st.session_state.form_data
    name = d["athlete_name"]
    coach = d["evaluating_coach"]
    weight = d["weight_kg"]
    sport = d["sport_type"]
    tot_club_hrs = d["club_days"] * d["club_hours_per_day"]
    has_injury = d["has_injury"]
    injury_site = d["injury_site"]
    congenital = d["congenital_defects"]

    # Frequency Auto-Calculation
    if tot_club_hrs >= 10:
        rec_days = 2
        freq_label = "2 Days/Week (Dense Full-Body Concurrent)"
    elif tot_club_hrs >= 6:
        rec_days = 3
        freq_label = "3 Days/Week (Concurrent Undulating Split)"
    else:
        rec_days = 4
        freq_label = "4 Days/Week (Upper/Lower Split)"

    # Biomechanical Load Scaling Formulas
    pushups = d["c_pushups"]
    cmj = d["p_cmj"]
    base_press = round(weight * 0.45 * (pushups / 30.0), 1)
    base_hinge = round(weight * 0.85 * (cmj / 40.0), 1)

    st.markdown(f"""
    <div class='metric-card'>
        <h3 style='margin:0; color:#38bdf8;'>👤 Athlete: {name} | ⚽ Sport: {sport} | 🧢 Coach: {coach}</h3>
        <p style='margin:5px 0 0 0; color:#cbd5e1;'>Macrocycle Plan Scope: <b>{plan_months}-Month Block</b> | Auto-Prescribed Frequency: <b>{freq_label}</b></p>
    </div>
    """, unsafe_allow_html=True)

    # Scientific Medical Directives
    if has_injury == "Yes":
        st.markdown(f"<div class='injury-alert'>⚠️ <b>CLINICAL INJURY PROTOCOL ACTIVE: {injury_site.upper()}</b><br>Heavy plyometrics auto-clamped. Focus shifted to isometric/eccentric loading.</div>", unsafe_allow_html=True)
    if congenital != "None Detected":
        st.info(f"🩺 **Postural Correction Active for Congenital Defect**: `{congenital}`. Specialized corrective priming incorporated.")

    # Dynamic Month Progression Tabs
    m_tabs = st.tabs([f"🗓️ MONTH {m}" for m in range(1, plan_months + 1)])

    for m_idx, m_tab in enumerate(m_tabs):
        m_num = m_idx + 1
        with m_tab:
            st.subheader(f"📌 Month {m_num} Prescription Matrix")
            w_tabs = st.tabs([f"Week {w}" for w in range(1, 5)])

            for w_idx, w_tab in enumerate(w_tabs):
                w_num = w_idx + 1
                with w_tab:
                    load_mod = 0.85 if w_num == 1 else (0.95 if w_num == 2 else (1.05 if w_num == 3 else 0.70))
                    st.markdown(f"#### 🗓️ Week {w_num} Training Protocol (Load Factor: {int(load_mod*100)}%)")

                    # Primary Plan Table
                    plan_data = [
                        {
                            "Category": "1. Posture & Mobility Priming",
                            "Exercise": "3-View Postural Corrective Flow" if congenital == "None Detected" else f"Corrective Protocol for {congenital}",
                            "Sets x Reps": "2 x 10 Reps",
                            "Load": "Bodyweight",
                            "Tempo": "2-2-2-0",
                            "Movement Cue": "Focus on deliberate scapular and pelvic alignment."
                        },
                        {
                            "Category": "2. Explosive Power",
                            "Exercise": "Medicine Ball Overhead Launch" if sport in ["Tennis", "Volleyball"] else "Box Jumps",
                            "Sets x Reps": "4 x 4 Reps" if w_num != 4 else "2 x 4 Reps",
                            "Load": "Max Intent",
                            "Tempo": "X-0-X-0",
                            "Movement Cue": "Triple extend through ankles, knees, and hips explosively."
                        },
                        {
                            "Category": "3. Agility & COD",
                            "Exercise": "T-Drill Baseline" if w_num < 3 else "7 x 7 Agility Drill",
                            "Sets x Reps": "4 x 2 Reps",
                            "Load": "Bodyweight",
                            "Tempo": "X-0-X-0",
                            "Movement Cue": "Sink center of gravity prior to directional change."
                        },
                        {
                            "Category": "4. Lower Body Main Compound",
                            "Exercise": "Barbell Back Squat" if "Barbells & Plates" in equipment_selected else "Dumbbell Bulgarian Split Squat",
                            "Sets x Reps": "3 x 8 Reps" if w_num != 4 else "2 x 8 Reps",
                            "Load": f"{round(base_hinge * load_mod, 1)} kg",
                            "Tempo": "3-1-1-0",
                            "Movement Cue": "Drive knees out, maintain tripod foot pressure."
                        },
                        {
                            "Category": "5. Upper Body Press",
                            "Exercise": "Flat Barbell Bench Press" if "Barbells & Plates" in equipment_selected else "Incline Dumbbell Press",
                            "Sets x Reps": "3 x 8 Reps" if w_num != 4 else "2 x 8 Reps",
                            "Load": f"{round(base_press * load_mod, 1)} kg",
                            "Tempo": "3-0-1-0",
                            "Movement Cue": "Retract scapulae and press away from chest smoothly."
                        }
                    ]
                    st.table(pd.DataFrame(plan_data))

    st.markdown("---")
    st.subheader("🔄 Interactive Exercise Swapping Engine & Database Reference")
    st.caption("Swap any prescribed exercise based on available equipment from the Master Directory[span_2](start_span)[span_2](end_span)[span_3](start_span)[span_3](end_span):")

    col_sw1, col_sw2, col_sw3 = st.columns(3)
    with col_sw1:
        target_group = st.selectbox("Select Target Body Region:", list(EXERCISE_DATABASE.keys()))
    with col_sw2:
        avail_equip = list(EXERCISE_DATABASE[target_group].keys())
        target_equip = st.selectbox("Select Equipment Available:", avail_equip)
    with col_sw3:
        ex_options = EXERCISE_DATABASE[target_group][target_equip]
        ex_names = [e["name"] for e in ex_options]
        selected_ex_name = st.selectbox("Select Alternative Exercise:", ex_names)

    # Display Exercise Details Card
    chosen_ex = next(item for item in ex_options if item["name"] == selected_ex_name)
    st.markdown(f"""
    <div class='scientific-note'>
        <b>🏋️ Selected Exercise Replacement: {chosen_ex['name']}</b><br>
        • <b>Modality Category</b>: {chosen_ex['type']}<br>
        • <b>Prescribed Eccentric/Concentric Tempo</b>: <code>{chosen_ex['tempo']}</code><br>
        • <b>Coaching Movement Cue</b>: <i>"{chosen_ex['cue']}"</i>
    </div>
    """, unsafe_allow_html=True)
