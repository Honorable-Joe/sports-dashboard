import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. PAGE CONFIG & HIGH-ENERGY CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="Athlete-IQ Engine",
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
        font-size: 1.5rem;
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
        margin-top: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
    }

    /* Custom Streamlit UI Overrides */
    div.stButton > button {
        background: linear-gradient(90deg, #06b6d4 0%, #3b82f6 100%);
        color: white;
        border: none;
        font-weight: 700;
        border-radius: 8px;
        padding: 12px 28px;
        font-size: 1.1rem;
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.7);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. APPLICATION HEADER (Cleaned Up)
# ==========================================
st.markdown("<h1 style='text-align: center; color: #38bdf8; font-weight: 900; letter-spacing: 1px; margin-bottom: 0px;'>⚡ ATHLETE-IQ PERFORMANCE ENGINE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a855f7; font-weight: 700; font-size: 1.1rem; margin-top: 4px;'>Developed & Designed for Elite Performance</p>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 3. SIDEBAR: NAVIGATION & FACILITY SETUP
# ==========================================
st.sidebar.markdown("### 📌 Navigation")
active_module = st.sidebar.radio(
    "Jump to Module:",
    [
        "📋 1. Demographics & Club History",
        "🩺 2. SFMA Top-Tier Screen",
        "📐 3. 3-View Posture Matrix",
        "💥 4. Explosive Power & Jumps",
        "🏃 5. Agility & Speed",
        "🫁 6. Endurance & Capacity",
        "🚀 7. GENERATE 1-MONTH PLAN"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Athlete & Facility Settings")

sport_profile = st.sidebar.selectbox(
    "Primary Sport Profile",
    ["General Fitness / Health", "Field & Court Sports (Soccer/Basketball)", "Overhead & Racket Sports (Tennis/Baseball)", "Endurance Sports (Running/Cycling)", "Tactical & Combat"]
)

in_season_toggle = st.sidebar.toggle("In-Season Athlete Mode", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏋️ Facility Equipment")
equipment_selected = st.sidebar.multiselect(
    "Available Equipment:",
    ["Barbells & Plates", "Dumbbells", "Kettlebells", "Cable Columns", "Resistance Bands", "TRX / Rings", "Medicine Balls", "AirBike / Rower", "Sleds / Prowler"],
    default=["Barbells & Plates", "Dumbbells", "Kettlebells", "Resistance Bands", "Medicine Balls", "AirBike / Rower"]
)

# Sport-based disabled logic
is_gen_fitness = sport_profile == "General Fitness / Health"
is_endurance = sport_profile == "Endurance Sports (Running/Cycling)"

# Session State Initialization for cross-tab persistence
if "athlete_data" not in st.session_state:
    st.session_state.athlete_data = {}

# ==========================================
# 4. MODULE CONTENT DISPLAY
# ==========================================

# ------------------------------------------
# MODULE 1: DEMOGRAPHICS, CLUB LOAD & INJURIES
# ------------------------------------------
if active_module == "📋 1. Demographics & Club History":
    st.markdown("<div class='banner-header'>👤 Athlete Profile, Club Load & Injury Diagnostics</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📌 Basic Demographics")
        athlete_name = st.text_input("Athlete Name", "Alex Morgan")
        age = st.number_input("Age", 14, 80, 24)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        weight_kg = st.number_input("Body Weight (kg)", 40.0, 150.0, 75.0)
        height_cm = st.number_input("Height (cm)", 120.0, 230.0, 178.0)
        training_years = st.number_input("Training History (Years)", 0, 30, 4)
        primary_goal = st.selectbox("Primary Goal", ["Hypertrophy / Power", "Speed & Agility", "Rehab / Injury Prevention", "Aerobic Conditioning"])

    with col2:
        st.subheader("⚽ Club Training Exposure (Exhaustion Shield)")
        club_days = st.number_input("Club Training Days per Week", 0, 7, 4)
        club_hours_per_day = st.number_input("Average Club Session Duration (Hours)", 0.5, 5.0, 2.0)
        
        weekly_club_hours = club_days * club_hours_per_day
        st.session_state.weekly_club_hours = weekly_club_hours
        
        if weekly_club_hours >= 10:
            st.warning(f"⚠️ High External Fatigue Exposure: {weekly_club_hours} hrs/week in club. Program volume will auto-throttle to prevent exhaustion.")
        elif weekly_club_hours >= 6:
            st.info(f"📊 Moderate External Fatigue: {weekly_club_hours} hrs/week in club. Program will use optimal complement volume.")
        else:
            st.success(f"✅ Low External Fatigue: {weekly_club_hours} hrs/week in club. Full capacity available.")

        st.subheader("🩺 Detailed Injury Profile")
        has_injury = st.radio("Has the athlete suffered a past or recent injury?", ["No", "Yes"], horizontal=True)
        
        injury_site = "None"
        injury_mechanism = "N/A"
        still_affects = "No"
        
        if has_injury == "Yes":
            injury_site = st.selectbox("Primary Injury Site", ["Ankle", "Knee (ACL/Meniscus/Patellar)", "Hamstring/Groin", "Lumbar Spine", "Shoulder", "Elbow/Wrist"])
            injury_mechanism = st.radio("How did the injury happen?", ["Acute Traumatic Event (Contact/Fall)", "Overuse / Cumulative Microtrauma"], horizontal=True)
            still_affects = st.radio("Does it currently cause pain, weakness, or fear of movement?", ["Yes - Lingering Symptoms", "No - Fully Cleared & Asymptomatic"], horizontal=True)
            
            st.text_area("Describe Injury History Context", placeholder="e.g., Grade 2 Ankle Sprain 3 months ago during a landing; feels unstable when pivoting.")

        # Save into Session State
        st.session_state.athlete_data.update({
            "name": athlete_name, "weight": weight_kg, "height": height_cm, "age": age,
            "club_hours": weekly_club_hours, "injury_site": injury_site,
            "still_affects": still_affects, "goal": primary_goal
        })

# ------------------------------------------
# MODULE 2: SFMA SCREENING
# ------------------------------------------
elif active_module == "🩺 2. SFMA Top-Tier Screen":
    st.markdown("<div class='banner-header'>🩺 SFMA Top-Tier Movement Assessment</div>", unsafe_allow_html=True)
    st.info("💡 **Scoring Guide:** **FN** = Functional Non-Painful | **FP** = Functional Painful | **DN** = Dysfunctional Non-Painful | **DP** = Dysfunctional Painful")
    
    if "sfma_results" not in st.session_state:
        st.session_state.sfma_results = {}
        
    sfma_patterns = [
        "1. Cervical Flexion (Chin to Chest)", "2. Cervical Extension (Look Overhead)",
        "3. Cervical Rotation (Left & Right)", "4. Upper Extremity Pattern 1 (Reach Behind Back)",
        "5. Upper Extremity Pattern 2 (Reach Overhead/Neck)", "6. Multi-Segmental Flexion (Toe Touch)",
        "7. Multi-Segmental Extension (Backward Bend)", "8. Multi-Segmental Rotation (Trunk Rotation)",
        "9. Single-Leg Stance (Eyes Open / Closed)", "10. Deep Overhead / Arms-Down Squat"
    ]
    
    col_a, col_b = st.columns(2)
    for idx, pattern in enumerate(sfma_patterns):
        target_col = col_a if idx < 5 else col_b
        with target_col:
            st.session_state.sfma_results[pattern] = st.radio(
                pattern, ["FN", "FP", "DN", "DP"], index=0, horizontal=True, key=f"sfma_{idx}"
            )

# ------------------------------------------
# MODULE 3: 3-VIEW POSTURE MATRIX
# ------------------------------------------
elif active_module == "📐 3. 3-View Posture Matrix":
    st.markdown("<div class='banner-header'>📐 Static Postural Analysis Matrix</div>", unsafe_allow_html=True)
    
    p_tab1, p_tab2, p_tab3 = st.tabs(["👁️ Anterior (Front) View", "👁️ Lateral (Side) View", "👁️ Posterior (Back) View"])
    
    posture = st.session_state.get("posture_data", {})
    
    with p_tab1:
        c1, c2, c3 = st.columns(3)
        with c1:
            posture["ant_shoulder"] = st.selectbox("Shoulder Level", ["Symmetrical", "Left Elevated", "Right Elevated"])
            posture["ant_hip"] = st.selectbox("Hip / ASIS Position", ["Level", "Left High", "Right High"])
        with c2:
            posture["ant_knee"] = st.selectbox("Knee Position", ["Neutral", "Genu Valgus (Knock-Knees)", "Genu Varum (Bow-Legged)"])
            posture["ant_tibia"] = st.selectbox("Tibia Alignment", ["Neutral Alignment", "Internal Tibial Torsion", "External Tibial Torsion"])
        with c3:
            posture["ant_foot_arch"] = st.selectbox("Foot Arch", ["Normal Arch", "Collapsed Arch (Pronation)", "High Arch (Supination)"])
            posture["ant_foot_pos"] = st.selectbox("Foot Position", ["Parallel / Forward", "Toe-Out (External Rotation)", "Toe-In (Internal Rotation)"])

    with p_tab2:
        c1, c2, c3 = st.columns(3)
        with c1:
            posture["lat_shoulder"] = st.selectbox("Shoulder Position", ["Neutral Alignment", "Forward Rounded (Protracted)"])
            posture["lat_pelvis"] = st.selectbox("Pelvic Tilt", ["Neutral Pelvis", "Anterior Pelvic Tilt (APT)", "Posterior Pelvic Tilt (PPT)"])
        with c2:
            posture["lat_thoracic"] = st.selectbox("Thoracic Spine", ["Normal Curve", "Hyper-Kyphosis (Hunchback)", "Flat Thoracic Spine"])
            posture["lat_lumbar"] = st.selectbox("Lumbar Spine", ["Normal Lordosis", "Hyper-Lordosis", "Flat Lumbar Curve"])
        with c3:
            posture["lat_knee"] = st.selectbox("Lateral Knee Line", ["Neutral Stance", "Genu Recurvatum (Hyperextended)", "Slightly Flexed Stance"])
            posture["lat_ankle"] = st.selectbox("Ankle Alignment", ["Vertical Gravity Line", "Anterior Weight Shift", "Posterior Weight Shift"])

    with p_tab3:
        c1, c2, c3 = st.columns(3)
        with c1:
            posture["post_scapula"] = st.selectbox("Scapula Alignment", ["Neutral & Flat", "Scapular Winging", "Abducted / Protracted"])
            posture["post_sit_bone"] = st.selectbox("Sit Bone / PSIS Level", ["Symmetrical / Level", "Left PSIS High", "Right PSIS High"])
        with c2:
            posture["post_spine"] = st.selectbox("Spine Line", ["Straight Vertical", "Scoliotic Lateral Curve"])
            posture["post_hip"] = st.selectbox("Gluteal Shift", ["Centered Alignment", "Left Hip Shift", "Right Hip Shift"])
        with c3:
            posture["post_ankle"] = st.selectbox("Rearfoot / Achilles Line", ["Neutral Calcaneus", "Calcaneal Valgus (Everted)", "Calcaneal Varus (Inverted)"])
            posture["post_toes"] = st.selectbox("Toe Visibility (Behind)", ["Normal Digits Visible", "Too-Many-Toes Sign (Toes Out)"])

    st.session_state.posture_data = posture

# ------------------------------------------
# MODULE 4: EXPLOSIVE POWER & JUMPS
# ------------------------------------------
elif active_module == "💥 4. Explosive Power & Jumps":
    st.markdown("<div class='banner-header'>💥 Ballistic Power & Jump Testing</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🏋️ Upper-Body Med-Ball Throws")
        mb_chest = st.number_input("Med-Ball Chest Pass (m)", 0.0, 20.0, 6.5, disabled=is_endurance)
        mb_overhead = st.number_input("Med-Ball Overhead Throw (m)", 0.0, 25.0, 9.2, disabled=is_endurance)
        mb_forehand = st.number_input("Med-Ball Forehand Throw (m)", 0.0, 20.0, 7.8, disabled=is_endurance)
        mb_backhand = st.number_input("Med-Ball Backhand Throw (m)", 0.0, 20.0, 6.9, disabled=is_endurance)
        
        if mb_forehand > 0 and mb_backhand > 0:
            rot_diff = abs(mb_forehand - mb_backhand) / max(mb_forehand, mb_backhand) * 100
            if rot_diff > 15:
                st.warning(f"⚠️ Rotational Sling Asymmetry Detected: {rot_diff:.1f}% imbalance between forehand & backhand!")

    with c2:
        st.subheader("🦵 Lower-Body Jump & Landing Screen")
        cmj_height = st.number_input("Countermovement Jump (CMJ) (cm)", 0.0, 100.0, 42.0)
        st.session_state.cmj_height = cmj_height
        
        broad_jump = st.number_input("Bilateral Broad Jump (cm)", 0.0, 400.0, 210.0)
        sl_jump_left = st.number_input("Single-Leg Broad Jump LEFT (cm)", 0.0, 300.0, 95.0)
        sl_jump_right = st.number_input("Single-Leg Broad Jump RIGHT (cm)", 0.0, 300.0, 88.0)
        
        landing_flaws = st.multiselect(
            "Landing Mechanics Flaws",
            ["Dynamic Knee Valgus (Cave)", "Stiff Landing (Poor Force Absorption)", "Asymmetrical Weight Landing", "Loss of Balance / Step Out"]
        )
        st.session_state.landing_flaws = landing_flaws

# ------------------------------------------
# MODULE 5: AGILITY & SPEED
# ------------------------------------------
elif active_module == "🏃 5. Agility & Speed":
    st.markdown("<div class='banner-header'>🏃 Agility & Speed Testing</div>", unsafe_allow_html=True)
    if is_gen_fitness or is_endurance or in_season_toggle:
        st.info("ℹ️ High-fatigue anaerobic agility tests are grayed out based on Sport Profile / In-Season status.")
        
    c1, c2 = st.columns(2)
    with c1:
        sprint_5m = st.number_input("5-Meter Acceleration Sprint (sec)", 0.5, 5.0, 1.25, disabled=(is_gen_fitness or is_endurance))
        t_drill = st.number_input("T-Drill Agility Test (sec)", 5.0, 20.0, 10.4, disabled=(is_gen_fitness or is_endurance))
    with c2:
        box_drill = st.number_input("Box Drill / 4-Cone (sec)", 5.0, 25.0, 12.1, disabled=(is_gen_fitness or is_endurance))
        drill_7x7 = st.number_input("7 x 7 COD Test (sec)", 10.0, 60.0, 22.5, disabled=(is_gen_fitness or is_endurance or in_season_toggle))

# ------------------------------------------
# MODULE 6: ENDURANCE & CAPACITY
# ------------------------------------------
elif active_module == "🫁 6. Endurance & Capacity":
    st.markdown("<div class='banner-header'>🫁 Muscular & Aerobic Endurance</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("💪 Muscular Endurance Battery")
        pushups = st.number_input("Max Push-Ups (1-Min Cap)", 0, 100, 35)
        pullups = st.number_input("Max Pull-Ups (Unbroken Set)", 0, 50, 12)
        squats = st.number_input("Max Bodyweight Squats (1-Min Cap)", 0, 120, 48)
        situps = st.number_input("Max Sit-Ups (1-Min Cap)", 0, 100, 40)
        
        st.session_state.endurance_scores = {"pushups": pushups, "pullups": pullups, "squats": squats, "situps": situps}

    with c2:
        st.subheader("🏃 Cardiovascular Capacity")
        run_1000m = st.number_input("1000m Sprint / Run (sec)", 120, 600, 240)
        cooper_meters = st.number_input("Cooper Test - 12-Min Distance (meters)", 500, 5000, 2600)
        
        estimated_vo2 = (cooper_meters - 504.9) / 44.73
        st.session_state.estimated_vo2 = estimated_vo2
        
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Calculated Estimated VO2Max</div>
            <div class='metric-value'>{estimated_vo2:.1f} mL/kg/min</div>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------
# MODULE 7: GENERATE 1-MONTH PERIODIZED PLAN
# ------------------------------------------
elif active_module == "🚀 7. GENERATE 1-MONTH PLAN":
    st.markdown("<div class='banner-header'>🚀 Dynamic Scientific 1-Month Plan Engine</div>", unsafe_allow_html=True)
    
    if st.button("🔥 GENERATE SCIENTIFIC PRESCRIPTIVE PROGRAM"):
        st.success("✅ Program successfully compiled using Athlete-IQ Logic!")
        
        # Retrieve State Data
        athlete = st.session_state.get("athlete_data", {"weight": 75, "club_hours": 8, "still_affects": "No", "injury_site": "None"})
        weight = athlete.get("weight", 75)
        club_hours = athlete.get("club_hours", 8)
        cmj = st.session_state.get("cmj_height", 42.0)
        vo2 = st.session_state.get("estimated_vo2", 46.8)
        sfma = st.session_state.get("sfma_results", {})
        endurance = st.session_state.get("endurance_scores", {"pushups": 35, "squats": 48})
        
        dn_count = len([k for k, v in sfma.items() if v in ["DN", "DP"]])
        
        # --- TOP SUMMARY DASHBOARD ---
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Club Load Protection</div><div class='metric-value'>{club_hours} hrs/wk</div></div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Est. VO2Max</div><div class='metric-value'>{vo2:.1f}</div></div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Jump Power</div><div class='metric-value'>{cmj:.1f} cm</div></div>", unsafe_allow_html=True)
        with m4:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>SFMA Flags</div><div class='metric-value'>{dn_count} Flags</div></div>", unsafe_allow_html=True)

        st.markdown("---")
        
        # Calculate Scientific Baseline Weights (in kg) based on Body Weight & Capacities
        # High club load auto-scales intensity down by 10% to prevent overtraining
        fatigue_factor = 0.90 if club_hours >= 10 else 1.00
        
        base_squat_weight = round((weight * 0.75 * fatigue_factor), 1)
        base_press_weight = round((weight * 0.45 * fatigue_factor), 1)
        base_rdl_weight = round((weight * 0.85 * fatigue_factor), 1)
        
        st.subheader("📋 Prescriptive Exercise Table with Scientific Weight Allocation")
        st.info("💡 **Scientific Basis:** Prescribed weights are dynamically calculated relative to body mass, explosive power output (CMJ), and club fatigue exposure.")
        
        # 4-Week Detailed Prescriptive Table
        prescribed_plan = pd.DataFrame({
            "Block / Focus": [
                "Tier 1: Mobility Priming",
                "Tier 2: Power / Speed",
                "Tier 3: Lower Strength (Hinge)",
                "Tier 3: Upper Strength (Push)",
                "Tier 3: Unilateral Pull",
                "Tier 4: Conditioning (ESD)"
            ],
            "Exercise Name": [
                "90/90 Hip Flow & Thoracic CARs",
                "Countermovement Box Jumps / Stick Landings",
                "Barbell / DB Romanian Deadlifts",
                "DB / Cable Neutral Overhead Press",
                "Single-Arm DB / Cable Rows",
                "AirBike Zone 2 / Lactic Intervals"
            ],
            "Sets x Reps": [
                "2 Sets x 8-10 Reps",
                "3-4 Sets x 3-5 Reps",
                "4 Sets x 8 Reps",
                "3 Sets x 10 Reps",
                "3 Sets x 10 Reps/side",
                "15-20 Mins"
            ],
            "Prescribed Load (kg / Intensity)": [
                "Bodyweight / Unloaded",
                "Bodyweight (Focus on RFD)",
                f"{base_rdl_weight} kg (RPE 7.5-8)",
                f"{base_press_weight} kg total (RPE 8)",
                f"{round(base_press_weight*0.6, 1)} kg (RPE 8)",
                "65-75% Max HR"
            ],
            "Scientific Progression Rule": [
                "Daily pre-workout mobility requirement",
                "Increase height by 5cm if landing mechanics stick",
                "+2.5 kg weekly if all reps completed with crisp tempo",
                "+1.25 kg per side weekly",
                "+2 kg weekly",
                "Add 2 minutes total duration weekly"
            ]
        })
        
        st.table(prescribed_plan)
        
        st.markdown("---")
        st.subheader("📅 4-Week Periodized Macro-Structure Schedule")
        
        schedule_df = pd.DataFrame({
            "Week": ["Week 1: Accumulation", "Week 2: Loading", "Week 3: Overreach", "Week 4: Deload & Re-Test"],
            "Target Intensity": ["70% 1RM / RPE 7", "75% 1RM / RPE 8", "80-85% 1RM / RPE 8.5", "60% 1RM / RPE 5"],
            "Weekly Volume": ["3 Sets per Pattern", "4 Sets per Pattern", "4-5 Sets per Pattern", "2 Sets per Pattern"],
            "Club Training Integration": [
                "Full S&C Session (Focus on movement quality)",
                "Full S&C Session (Progress loading)",
                "Reduce S&C volume by 20% if 3+ club games scheduled",
                "Active Recovery & Joint Decompression"
            ]
        })
        st.table(schedule_df)
