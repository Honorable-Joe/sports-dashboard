import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. PAGE CONFIG & HIGH-ENERGY CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="Athlete-IQ Performance Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-energy Dark Theme styling with glowing neon accents
st.markdown("""
<style>
    /* Global Page Styling */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #020617 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, sans-serif;
    }
    
    /* Neon Glow Accent Header Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.15);
        backdrop-filter: blur(8px);
        margin-bottom: 12px;
    }
    
    .metric-title {
        color: #38bdf8;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-value {
        color: #f3f4f6;
        font-size: 1.6rem;
        font-weight: 800;
        margin-top: 4px;
    }

    /* Section Header Banners */
    .banner-header {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        padding: 12px 20px;
        border-radius: 10px;
        color: white;
        font-weight: 800;
        font-size: 1.2rem;
        margin-top: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
    }
    
    /* SFMA Indicator Badges */
    .badge-fn { background-color: #10b981; color: white; padding: 3px 8px; border-radius: 6px; font-weight: bold; }
    .badge-fp { background-color: #f59e0b; color: white; padding: 3px 8px; border-radius: 6px; font-weight: bold; }
    .badge-dn { background-color: #06b6d4; color: white; padding: 3px 8px; border-radius: 6px; font-weight: bold; }
    .badge-dp { background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 6px; font-weight: bold; }

    /* Custom Streamlit UI Overrides */
    div.stButton > button {
        background: linear-gradient(90deg, #06b6d4 0%, #3b82f6 100%);
        color: white;
        border: none;
        font-weight: 700;
        border-radius: 8px;
        padding: 10px 24px;
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.7);
    }
</style>
""", unsafe_allow_html=unsafe_allow_html)

# ==========================================
# 2. APPLICATION HEADER & SIDEBAR FILTERS
# ==========================================
st.markdown("<h1 style='text-align: center; color: #38bdf8; font-weight: 900; letter-spacing: 1px;'>⚡ ATHLETE-IQ PERFORMANCE ENGINE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.1rem;'>Clinical SFMA Screening • Multi-View Posture • Dynamic 1-Month Plan Generator</p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar Configuration Controls
st.sidebar.markdown("### 🎛️ Athlete & Facility Settings")

sport_profile = st.sidebar.selectbox(
    "Primary Sport Profile",
    ["General Fitness / Health", "Field & Court Sports (Soccer/Basketball)", "Overhead & Racket Sports (Tennis/Baseball)", "Endurance Sports (Running/Cycling)", "Tactical & Combat"]
)

in_season_toggle = st.sidebar.toggle("In-Season Athlete Mode", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏋️ Facility Equipment Available")
equipment_selected = st.sidebar.multiselect(
    "Select All Equipment in Facility:",
    ["Barbells & Plates", "Dumbbells", "Kettlebells", "Cable Columns", "Resistance Bands", "TRX / Rings", "Medicine Balls", "AirBike / Rower", "Sleds / Prowler"],
    default=["Dumbbells", "Kettlebells", "Resistance Bands", "Medicine Balls", "AirBike / Rower"]
)

# Sport-based disabled filters
is_gen_fitness = sport_profile == "General Fitness / Health"
is_endurance = sport_profile == "Endurance Sports (Running/Cycling)"

# ==========================================
# 3. ASSESSMENT MODULE TABS
# ==========================================
tabs = st.tabs([
    "📋 1. Demographics & History",
    "🩺 2. SFMA Top-Tier Screen",
    "📐 3. 3-View Posture Matrix",
    "💥 4. Explosive Power & Jumps",
    "🏃 5. Agility & Speed",
    "🫁 6. Endurance & Capacity",
    "🚀 7. GENERATE 1-MONTH PLAN"
])

# ------------------------------------------
# TAB 1: DEMOGRAPHICS
# ------------------------------------------
with tabs[0]:
    st.markdown("<div class='banner-header'>👤 Athlete Profile & Medical History</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        athlete_name = st.text_input("Athlete Name", "Alex Morgan")
        age = st.number_input("Age", 14, 80, 24)
    with c2:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        weight_kg = st.number_input("Body Weight (kg)", 40.0, 150.0, 75.0)
    with c3:
        height_cm = st.number_input("Height (cm)", 120.0, 230.0, 178.0)
        training_age = st.number_input("Training History (Years)", 0, 30, 4)
    with c4:
        primary_goal = st.selectbox("Primary Goal", ["Hypertrophy / Power", "Speed & Agility", "Rehab / Injury Prevention", "Aerobic Conditioning"])
        injury_flags = st.multiselect("Active Injury Sites", ["Ankle", "Knee", "Lumbar Spine", "Shoulder", "Wrist/Elbow"])

# ------------------------------------------
# TAB 2: SFMA TOP-TIER SCREENING
# ------------------------------------------
with tabs[1]:
    st.markdown("<div class='banner-header'>🩺 SFMA Top-Tier Movement Assessment</div>", unsafe_allow_html=True)
    st.info("💡 **Scoring Guide:** **FN** = Functional Non-Painful | **FP** = Functional Painful | **DN** = Dysfunctional Non-Painful | **DP** = Dysfunctional Painful")
    
    sfma_results = {}
    sfma_patterns = [
        "1. Cervical Flexion (Chin to Chest)",
        "2. Cervical Extension (Look Overhead)",
        "3. Cervical Rotation (Left & Right)",
        "4. Upper Extremity Pattern 1 (Reach Behind Back)",
        "5. Upper Extremity Pattern 2 (Reach Overhead/Neck)",
        "6. Multi-Segmental Flexion (Toe Touch)",
        "7. Multi-Segmental Extension (Backward Bend)",
        "8. Multi-Segmental Rotation (Trunk Rotation)",
        "9. Single-Leg Stance (Eyes Open / Eyes Closed)",
        "10. Deep Overhead / Arms-Down Squat"
    ]
    
    col_a, col_b = st.columns(2)
    for idx, pattern in enumerate(sfma_patterns):
        target_col = col_a if idx < 5 else col_b
        with target_col:
            sfma_results[pattern] = st.radio(
                pattern,
                ["FN", "FP", "DN", "DP"],
                index=0,
                horizontal=True,
                key=f"sfma_{idx}"
            )

# ------------------------------------------
# TAB 3: 3-VIEW POSTURAL MATRIX
# ------------------------------------------
with tabs[2]:
    st.markdown("<div class='banner-header'>📐 Static Postural Analysis Matrix</div>", unsafe_allow_html=True)
    p_tab1, p_tab2, p_tab3 = st.tabs(["👁️ Anterior (Front) View", "👁️ Lateral (Side) View", "👁️ Posterior (Back) View"])
    
    posture_data = {}
    
    with p_tab1:
        c1, c2, c3 = st.columns(3)
        with c1:
            posture_data["ant_shoulder"] = st.selectbox("Shoulder Level", ["Symmetrical", "Left Elevated", "Right Elevated"])
            posture_data["ant_hip"] = st.selectbox("Hip / ASIS Position", ["Level", "Left High", "Right High"])
        with c2:
            posture_data["ant_knee"] = st.selectbox("Knee Position", ["Neutral", "Genu Valgus (Knock-Knees)", "Genu Varum (Bow-Legged)"])
            posture_data["ant_tibia"] = st.selectbox("Tibia Alignment", ["Neutral Alignment", "Internal Tibial Torsion", "External Tibial Torsion"])
        with c3:
            posture_data["ant_foot_arch"] = st.selectbox("Foot Arch", ["Normal Arch", "Collapsed Arch (Pronation)", "High Arch (Supination)"])
            posture_data["ant_foot_pos"] = st.selectbox("Foot Position", ["Parallel / Forward", "Toe-Out (External Rotation)", "Toe-In (Internal Rotation)"])

    with p_tab2:
        c1, c2, c3 = st.columns(3)
        with c1:
            posture_data["lat_shoulder"] = st.selectbox("Shoulder Position", ["Neutral Alignment", "Forward Rounded (Protracted)"])
            posture_data["lat_pelvis"] = st.selectbox("Pelvic Tilt", ["Neutral Pelvis", "Anterior Pelvic Tilt (APT)", "Posterior Pelvic Tilt (PPT)"])
        with c2:
            posture_data["lat_thoracic"] = st.selectbox("Thoracic Spine", ["Normal Curve", "Hyper-Kyphosis (Hunchback)", "Flat Thoracic Spine"])
            posture_data["lat_lumbar"] = st.selectbox("Lumbar Spine", ["Normal Lordosis", "Hyper-Lordosis", "Flat Lumbar Curve"])
        with c3:
            posture_data["lat_knee"] = st.selectbox("Lateral Knee Line", ["Neutral Stance", "Genu Recurvatum (Hyperextended)", "Slightly Flexed Stance"])
            posture_data["lat_ankle"] = st.selectbox("Ankle Alignment", ["Vertical Gravity Line", "Anterior Weight Shift", "Posterior Weight Shift"])

    with p_tab3:
        c1, c2, c3 = st.columns(3)
        with c1:
            posture_data["post_scapula"] = st.selectbox("Scapula Alignment", ["Neutral & Flat", "Scapular Winging", "Abducted / Protracted"])
            posture_data["post_sit_bone"] = st.selectbox("Sit Bone / PSIS Level", ["Symmetrical / Level", "Left PSIS High", "Right PSIS High"])
        with c2:
            posture_data["post_spine"] = st.selectbox("Spine Line", ["Straight Vertical", "Scoliotic Lateral Curve"])
            posture_data["post_hip"] = st.selectbox("Gluteal Shift", ["Centered Alignment", "Left Hip Shift", "Right Hip Shift"])
        with c3:
            posture_data["post_ankle"] = st.selectbox("Rearfoot / Achilles Line", ["Neutral Calcaneus", "Calcaneal Valgus (Everted)", "Calcaneal Varus (Inverted)"])
            posture_data["post_toes"] = st.selectbox("Toe Visibility (Behind)", ["Normal Digits Visible", "Too-Many-Toes Sign (Toes Out)"])

# ------------------------------------------
# TAB 4: EXPLOSIVE POWER & JUMPS
# ------------------------------------------
with tabs[3]:
    st.markdown("<div class='banner-header'>💥 Ballistic Power & Jump Testing</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🏋️ Upper-Body Med-Ball Throws")
        mb_chest = st.number_input("Med-Ball Chest Pass (m)", 0.0, 20.0, 6.5, disabled=is_endurance)
        mb_overhead = st.number_input("Med-Ball Overhead Throw (m)", 0.0, 25.0, 9.2, disabled=is_endurance)
        mb_forehand = st.number_input("Med-Ball Forehand Throw (m)", 0.0, 20.0, 7.8, disabled=is_endurance)
        mb_backhand = st.number_input("Med-Ball Backhand Throw (m)", 0.0, 20.0, 6.9, disabled=is_endurance)
        
        # Rotational Asymmetry Calculation
        if mb_forehand > 0 and mb_backhand > 0:
            rot_diff = abs(mb_forehand - mb_backhand) / max(mb_forehand, mb_backhand) * 100
            if rot_diff > 15:
                st.warning(f"⚠️ Rotational Sling Asymmetry Detected: {rot_diff:.1f}% imbalance between forehand & backhand!")

    with c2:
        st.subheader("🦵 Lower-Body Jump & Landing Screen")
        cmj_height = st.number_input("Countermovement Jump (CMJ) (cm)", 0.0, 100.0, 42.0)
        broad_jump = st.number_input("Bilateral Broad Jump (cm)", 0.0, 400.0, 210.0)
        sl_jump_left = st.number_input("Single-Leg Broad Jump LEFT (cm)", 0.0, 300.0, 95.0)
        sl_jump_right = st.number_input("Single-Leg Broad Jump RIGHT (cm)", 0.0, 300.0, 88.0)
        
        landing_flaws = st.multiselect(
            "Landing Mechanics Screen Flaws",
            ["Dynamic Knee Valgus (Cave)", "Stiff Landing (Poor Force Absorption)", "Asymmetrical Weight Landing", "Loss of Balance / Step Out"]
        )

# ------------------------------------------
# TAB 5: AGILITY & SPEED
# ------------------------------------------
with tabs[4]:
    st.markdown("<div class='banner-header'>🏃 Agility & Speed Testing</div>", unsafe_allow_html=True)
    if is_gen_fitness or is_endurance or in_season_toggle:
        st.info("ℹ️ High-fatigue anaerobic agility tests are currently grayed out based on selected Sport Profile / In-Season status.")
        
    c1, c2 = st.columns(2)
    with c1:
        sprint_5m = st.number_input("5-Meter Acceleration Sprint (sec)", 0.5, 5.0, 1.25, disabled=(is_gen_fitness or is_endurance))
        t_drill = st.number_input("T-Drill Agility Test (sec)", 5.0, 20.0, 10.4, disabled=(is_gen_fitness or is_endurance))
    with c2:
        box_drill = st.number_input("Box Drill / 4-Cone (sec)", 5.0, 25.0, 12.1, disabled=(is_gen_fitness or is_endurance))
        drill_7x7 = st.number_input("7 x 7 COD Test (sec)", 10.0, 60.0, 22.5, disabled=(is_gen_fitness or is_endurance or in_season_toggle))

# ------------------------------------------
# TAB 6: ENDURANCE & CAPACITY
# ------------------------------------------
with tabs[5]:
    st.markdown("<div class='banner-header'>🫁 Muscular & Aerobic Endurance</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("💪 Muscular Endurance Battery")
        pushups_reps = st.number_input("Max Push-Ups (1-Min Cap)", 0, 100, 35)
        pullups_reps = st.number_input("Max Pull-Ups (Unbroken Set)", 0, 50, 12)
        squats_reps = st.number_input("Max Bodyweight Squats (1-Min Cap)", 0, 120, 48)
        situps_reps = st.number_input("Max Sit-Ups (1-Min Cap)", 0, 100, 40)
        
    with c2:
        st.subheader("🏃 Cardiovascular Capacity")
        run_1000m = st.number_input("1000m Sprint / Run (seconds)", 120, 600, 240)
        cooper_meters = st.number_input("Cooper Test - 12-Min Distance (meters)", 500, 5000, 2600)
        
        # Real-time VO2max estimation from Cooper Test
        estimated_vo2 = (cooper_meters - 504.9) / 44.73
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Calculated Estimated VO2Max</div>
            <div class='metric-value'>{estimated_vo2:.1f} mL/kg/min</div>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 7: GENERATE 1-MONTH PERIODIZED PLAN
# ------------------------------------------
with tabs[6]:
    st.markdown("<div class='banner-header'>🚀 Dynamic 1-Month Training Plan Generator</div>", unsafe_allow_html=True)
    
    if st.button("🔥 GENERATE 1-MONTH DYNAMIC PROGRAM"):
        st.success("✅ Program successfully compiled using Athlete-IQ Logic!")
        
        # Collect Key Diagnostic Flags
        dn_patterns = [k for k, v in sfma_results.items() if v in ["DN", "DP"]]
        has_landing_flaw = len(landing_flaws) > 0
        
        # --- TOP SUMMARY METRIC DASHBOARD ---
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Movement Flags</div><div class='metric-value'>{len(dn_patterns)} Flags</div></div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Est. VO2Max</div><div class='metric-value'>{estimated_vo2:.1f}</div></div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Jump Power</div><div class='metric-value'>{cmj_height:.1f} cm</div></div>", unsafe_allow_html=True)
        with m4:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Selected Tools</div><div class='metric-value'>{len(equipment_selected)} Available</div></div>", unsafe_allow_html=True)

        st.markdown("---")
        
        # --- 5-TIER DAILY SESSION STRUCTURE DISPLAY ---
        st.subheader("🏋️ Daily 5-Tier Workout Structure Architecture")
        
        t1, t2, t3, t4, t5 = st.tabs([
            "Tier 1: Mobility & Priming",
            "Tier 2: Power & Speed",
            "Tier 3: Strength & Hypertrophy",
            "Tier 4: Conditioning / ESD",
            "Tier 5: Down-Regulation"
        ])
        
        with t1:
            st.markdown("#### 🧘 Corrective Mobility & Priming Block")
            if dn_patterns:
                st.warning(f"Targeting active SFMA restrictions: {', '.join([p.split('.')[1] for p in dn_patterns])}")
                st.write("• **90/90 Hip Rotational Flow** - 2 sets x 8 reps/side")
                st.write("• **Thoracic Spine Extension & CARs** - 2 sets x 10 reps (using Foam Roller)")
                st.write("• **Ankle Dorsiflexion Wall Mobilization** - 2 sets x 12 reps")
            else:
                st.write("• **Full Body Dynamic World's Greatest Stretch** - 2 sets x 5 reps/side")
                st.write("• **Band-Resisted Glute Activation Bridges** - 2 sets x 15 reps")

        with t2:
            st.markdown("#### ⚡ Neuromuscular Speed, Power & Deceleration")
            if "Dynamic Knee Valgus (Cave)" in landing_flaws or "Stiff Landing (Poor Force Absorption)" in landing_flaws:
                st.error("⚠️ Landing mechanics risk detected: High-impact drop jumps BLACKLISTED. Substituted with stick deceleration.")
                st.write("• **TRX-Assisted Single-Leg Stick Landings** - 3 sets x 5 reps/side")
                st.write("• **Medicine Ball Dynamic Chest Passes** - 3 sets x 6 reps")
            else:
                st.write("• **Countermovement Box Jumps** - 4 sets x 3 reps")
                st.write("• **Med-Ball Rotational Wall Throws** - 3 sets x 5 reps/side")

        with t3:
            st.markdown("#### 🏋️ Main Functional Strength Component")
            st.write(f"Adapted for available tools: {', '.join(equipment_selected)}")
            st.write("• **Primary Hinge:** Kettlebell / Barbell Romanian Deadlifts - 4 sets x 8 reps @ RPE 8")
            st.write("• **Primary Push:** DB / Cable Neutral Grip Overhead Press - 3 sets x 10 reps")
            st.write("• **Unilateral Pull:** Single-Arm Cable / Kettlebell Rows - 3 sets x 10 reps/side")

        with t4:
            st.markdown("#### 🫁 Energy System Development (ESD) & Endurance")
            if estimated_vo2 < 45.0:
                st.info("Aerobic base focus based on Cooper Test output:")
                st.write("• **AirBike / Rower Zone 2 Aerobic Intervals:** 20 mins @ 65-75% HR Max")
            else:
                st.write("• **High-Intensity Lactic Intervals:** 10 sec Sprint / 50 sec Rest x 8 rounds")

        with t5:
            st.markdown("#### 🧘 Parasympathetic Recovery & Regeneration")
            st.write("• **Box Breathing (4-4-4-4 tempo):** 3-5 minutes lying supine")
            st.write("• **Lower Limb SMR Foam Rolling:** 2 minutes per leg (Calves & Quadriceps)")

        # --- 4-WEEK PERIODIZATION SCHEDULE TABLE ---
        st.markdown("---")
        st.subheader("📅 4-Week Periodized Macro-Structure")
        
        plan_df = pd.DataFrame({
            "Week": ["Week 1: Accumulation", "Week 2: Loading", "Week 3: Overreach", "Week 4: Deload / Re-Test"],
            "Intensity (% 1RM / RPE)": ["70-75% (RPE 7)", "75-80% (RPE 8)", "80-85% (RPE 9)", "60-65% (RPE 5)"],
            "Primary Focus": [
                "Movement Quality & Structural Balance",
                "Force Production & Speed Development",
                "Maximal Aerobic & Muscular Output",
                "Recovery, Taper & Re-Assessment"
            ],
            "Volume (Sets x Reps)": ["3-4 Sets x 10-12 Reps", "4 Sets x 8-10 Reps", "4-5 Sets x 6-8 Reps", "2-3 Sets x 8 Reps"]
        })
        
        st.table(plan_df)
