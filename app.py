import streamlit as st
import pandas as pd
import json
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG & HIGH-ENERGY STYLING
# ==========================================
st.set_page_config(
    page_title="Athlete-IQ Performance Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global Page Styling */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #020617 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, sans-serif;
    }
    
    /* Neon Glow Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(56, 189, 248, 0.35);
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
        font-size: 1.4rem;
        font-weight: 800;
        margin-top: 4px;
    }

    /* Section Banner */
    .banner-header {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        padding: 12px 20px;
        border-radius: 10px;
        color: white;
        font-weight: 800;
        font-size: 1.25rem;
        margin-top: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
    }
    
    /* Rationale Box */
    .scientific-note {
        background-color: rgba(15, 23, 42, 0.85);
        border-left: 4px solid #38bdf8;
        padding: 14px 18px;
        border-radius: 6px;
        margin-top: 10px;
        margin-bottom: 20px;
        font-size: 0.95rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session Storage
if "athlete_records" not in st.session_state:
    st.session_state.athlete_records = []

if "current_assessment" not in st.session_state:
    st.session_state.current_assessment = {}

# ==========================================
# 2. APPLICATION HEADER
# ==========================================
st.markdown("<h1 style='text-align: center; color: #38bdf8; font-weight: 900; margin-bottom: 0px;'>⚡ ATHLETE-IQ PERFORMANCE ENGINE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a855f7; font-weight: 700; font-size: 1.1rem;'>Total Athletic Development & Assessment System</p>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.markdown("### 📌 Navigation")
active_module = st.sidebar.radio(
    "Jump to Module:",
    [
        "📋 1. Demographics & Coach Sign-off",
        "⚽ 2. Club Load & Injury Profile",
        "🩺 3. SFMA & Posture Assessment",
        "💥 4. Power, Speed & Capacity",
        "📈 5. Saved Records & Follow-Up",
        "🚀 6. GENERATE 1-MONTH PLAN"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏋️ Facility Equipment Available")
equipment_selected = st.sidebar.multiselect(
    "Select Available Equipment:",
    ["Barbells & Plates", "Dumbbells", "Kettlebells", "Cable Columns", "Resistance Bands", "TRX / Rings", "Medicine Balls", "AirBike / Rower", "Sleds / Prowler"],
    default=["Barbells & Plates", "Dumbbells", "Kettlebells", "Resistance Bands", "Medicine Balls", "AirBike / Rower"]
)

# ==========================================
# 4. MODULES LOGIC
# ==========================================

# ------------------------------------------
# MODULE 1: DEMOGRAPHICS & COACH SIGN-OFF
# ------------------------------------------
if active_module == "📋 1. Demographics & Coach Sign-off":
    st.markdown("<div class='banner-header'>📋 Athlete Demographics & Evaluating Coach Sign-Off</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👤 Athlete Profile")
        athlete_name = st.text_input("Athlete Name", "Alex Morgan")
        age = st.number_input("Age", 12, 80, 22)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        weight_kg = st.number_input("Body Weight (kg)", 40.0, 150.0, 75.0)
        height_cm = st.number_input("Height (cm)", 120.0, 230.0, 178.0)
        sport_type = st.selectbox("Sport / Discipline", ["Soccer", "Basketball", "Tennis", "Track & Field", "Combat Sports", "General Athletics"])
        
    with col2:
        st.subheader("🧢 Evaluating Coach Details")
        evaluating_coach = st.text_input("Evaluating Coach Name", "Coach John Doe")
        assessment_date = st.date_input("Assessment Date", datetime.now())
        assessment_type = st.selectbox("Assessment Phase", ["Baseline (Initial)", "Mid-Phase Follow-Up", "Re-Assessment (Post-Block)"])
        training_years = st.number_input("Training History (Years)", 0, 30, 3)

    # Save to dynamic memory
    st.session_state.current_assessment.update({
        "athlete_name": athlete_name,
        "evaluating_coach": evaluating_coach,
        "date": str(assessment_date),
        "phase": assessment_type,
        "age": age,
        "gender": gender,
        "weight": weight_kg,
        "height": height_cm,
        "sport": sport_type,
        "training_years": training_years
    })

# ------------------------------------------
# MODULE 2: CLUB LOAD & INJURY DIAGNOSTICS
# ------------------------------------------
elif active_module == "⚽ 2. Club Load & Injury Profile":
    st.markdown("<div class='banner-header'>⚽ Club Training Load & Clinical Injury Diagnostics</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚽ Club Training Load Exposure")
        club_days = st.number_input("Club Training Days / Week", 0, 7, 4)
        club_hours_per_day = st.number_input("Avg Club Session Duration (Hours)", 0.5, 5.0, 2.0)
        
        total_club_hours = club_days * club_hours_per_day
        st.session_state.current_assessment["club_days"] = club_days
        st.session_state.current_assessment["club_hours_day"] = club_hours_per_day
        st.session_state.current_assessment["total_club_hours"] = total_club_hours

        if total_club_hours >= 10:
            st.warning(f"⚠️ High Club Load Exposure: {total_club_hours} hrs/week. App will scale strength sessions to 2 days/week to prevent overtraining.")
        elif total_club_hours >= 6:
            st.info(f"📊 Moderate Club Load Exposure: {total_club_hours} hrs/week. App will recommend 3 days/week.")
        else:
            st.success(f"✅ Low External Exposure: {total_club_hours} hrs/week. App will recommend 3 to 4 days/week for maximum development.")

    with col2:
        st.subheader("🩺 Injury History & Current Limitations")
        has_injury = st.radio("Has the athlete suffered a past/recent injury?", ["No", "Yes"], horizontal=True)
        
        injury_site = "None"
        injury_mechanism = "N/A"
        still_affects = "No"
        
        if has_injury == "Yes":
            injury_site = st.selectbox("Injury Site", ["Ankle", "Knee (ACL/Patellar)", "Hamstring/Groin", "Lumbar Spine", "Shoulder", "Elbow/Wrist"])
            injury_mechanism = st.radio("Mechanism of Injury", ["Acute Contact / Traumatic", "Overuse / Repetitive Stress"], horizontal=True)
            still_affects = st.radio("Are symptoms currently present during training?", ["Yes - Active Symptoms", "No - Cleared / Asymptomatic"], horizontal=True)
            
        st.session_state.current_assessment.update({
            "has_injury": has_injury,
            "injury_site": injury_site,
            "injury_mechanism": injury_mechanism,
            "still_affects": still_affects
        })

# ------------------------------------------
# MODULE 3: SFMA & POSTURE MATRIX
# ------------------------------------------
elif active_module == "🩺 3. SFMA & Posture Assessment":
    st.markdown("<div class='banner-header'>🩺 Movement Quality & Posture Assessment</div>", unsafe_allow_html=True)
    
    st.subheader("1. SFMA Screen Top-Tier Flags")
    c1, c2, c3 = st.columns(3)
    with c1:
        cervical = st.selectbox("Cervical Spine Pattern", ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"])
        shoulder = st.selectbox("Upper Extremity Reach", ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"])
    with c2:
        flexion = st.selectbox("Multi-Segmental Flexion (Toe Touch)", ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"])
        extension = st.selectbox("Multi-Segmental Extension", ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"])
    with c3:
        sl_stance = st.selectbox("Single-Leg Stance Balance", ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"])
        overhead_squat = st.selectbox("Deep Overhead Squat Pattern", ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"])

    st.subheader("2. Static Posture Deviations")
    p1, p2 = st.columns(2)
    with p1:
        pelvis = st.selectbox("Pelvic Alignment", ["Neutral Pelvis", "Anterior Pelvic Tilt", "Posterior Pelvic Tilt"])
        knee_align = st.selectbox("Knee Alignment", ["Neutral", "Genu Valgus (Knock-Knees)", "Genu Varum (Bow-Legged)"])
    with p2:
        shoulder_align = st.selectbox("Shoulder Position", ["Symmetrical Neutral", "Forward Rounded (Protracted)", "Asymmetrical Elevation"])
        foot_arch = st.selectbox("Foot Arch", ["Normal Arch", "Collapsed Arch (Pronated)", "High Arch (Supinated)"])

    st.session_state.current_assessment.update({
        "sfma_squat": overhead_squat,
        "pelvis": pelvis,
        "knee_align": knee_align
    })

# ------------------------------------------
# MODULE 4: POWER, SPEED & CAPACITY
# ------------------------------------------
elif active_module == "💥 4. Power, Speed & Capacity":
    st.markdown("<div class='banner-header'>💥 Comprehensive Multi-Component Performance Metrics</div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.subheader("💥 Explosive Power")
        cmj_cm = st.number_input("Countermovement Jump (cm)", 10.0, 100.0, 42.0)
        broad_jump_cm = st.number_input("Broad Jump (cm)", 50.0, 350.0, 215.0)
        mb_throw_m = st.number_input("Med-Ball Chest Launch (m)", 1.0, 20.0, 7.2)

    with c2:
        st.subheader("🏃 Speed & Agility")
        sprint_10m = st.number_input("10m Sprint Acceleration (sec)", 1.0, 4.0, 1.75)
        t_drill = st.number_input("T-Drill Agility Test (sec)", 5.0, 20.0, 10.2)

    with c3:
        st.subheader("🫁 Endurance & Strength")
        max_pushups = st.number_input("Max Push-ups (1 Min)", 0, 100, 38)
        max_pullups = st.number_input("Max Pull-ups (Unbroken)", 0, 50, 12)
        cooper_meters = st.number_input("12-Min Cooper Test (meters)", 500, 5000, 2650)
        
    vo2max = (cooper_meters - 504.9) / 44.73
    
    st.session_state.current_assessment.update({
        "cmj": cmj_cm,
        "broad_jump": broad_jump_cm,
        "mb_throw": mb_throw_m,
        "sprint_10m": sprint_10m,
        "t_drill": t_drill,
        "pushups": max_pushups,
        "pullups": max_pullups,
        "cooper_m": cooper_meters,
        "vo2max": round(vo2max, 1)
    })

    st.markdown("---")
    if st.button("💾 SAVE ASSESSMENT RECORD FOR FOLLOW-UP"):
        record = st.session_state.current_assessment.copy()
        st.session_state.athlete_records.append(record)
        st.success(f"✅ Assessment recorded successfully by {record.get('evaluating_coach', 'Coach')} on {record.get('date')}!")

# ------------------------------------------
# MODULE 5: SAVED RECORDS & FOLLOW-UP
# ------------------------------------------
elif active_module == "📈 5. Saved Records & Follow-Up":
    st.markdown("<div class='banner-header'>📈 Saved Assessment Records & Progress Tracker</div>", unsafe_allow_html=True)
    
    if len(st.session_state.athlete_records) == 0:
        st.info("ℹ️ No saved records yet. Fill out the assessment modules and click '💾 Save Assessment Record' in Module 4.")
    else:
        st.subheader("📋 Recorded Assessments Database")
        df_records = pd.DataFrame(st.session_state.athlete_records)
        st.dataframe(df_records, use_container_width=True)
        
        if len(st.session_state.athlete_records) >= 2:
            st.markdown("---")
            st.subheader("📊 Baseline vs. Follow-Up Comparison")
            
            rec1 = st.session_state.athlete_records[0]
            rec2 = st.session_state.athlete_records[-1]
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                cmj_diff = rec2.get("cmj", 0) - rec1.get("cmj", 0)
                st.metric("CMJ Jump Height", f"{rec2.get('cmj')} cm", f"{cmj_diff:+.1f} cm")
            with col_b:
                push_diff = rec2.get("pushups", 0) - rec1.get("pushups", 0)
                st.metric("Push-Up Capacity", f"{rec2.get('pushups')} reps", f"{push_diff:+d} reps")
            with col_c:
                vo2_diff = rec2.get("vo2max", 0) - rec1.get("vo2max", 0)
                st.metric("Estimated VO2Max", f"{rec2.get('vo2max')} mL/kg/min", f"{vo2_diff:+.1f}")

# ------------------------------------------
# MODULE 6: GENERATE 1-MONTH PLAN
# ------------------------------------------
elif active_module == "🚀 6. GENERATE 1-MONTH PLAN":
    st.markdown("<div class='banner-header'>🚀 Dynamic Scientific 1-Month Program Engine</div>", unsafe_allow_html=True)
    
    data = st.session_state.current_assessment
    
    if not data.get("athlete_name"):
        st.warning("⚠️ Please fill in at least Athlete Demographics in Module 1 first.")
    else:
        # Load Variables
        name = data.get("athlete_name", "Athlete")
        coach = data.get("evaluating_coach", "Coach")
        weight = data.get("weight", 75.0)
        club_hours = data.get("total_club_hours", 8.0)
        club_days = data.get("club_days", 4)
        cmj = data.get("cmj", 42.0)
        pushups = data.get("pushups", 35)
        pullups = data.get("pullups", 12)
        vo2 = data.get("vo2max", 46.8)
        injury_site = data.get("injury_site", "None")
        still_affects = data.get("still_affects", "No")
        
        # --- SCIENTIFIC FREQUENCY & REGULATION DECISION ENGINE ---
        if club_hours >= 10:
            recommended_days = 2
            fatigue_reduction = 0.88 # 12% lower load to avoid overtraining
            freq_rationale = f"Due to heavy club exposure ({club_hours} hrs/week across {club_days} days), S&C frequency is set to **2 Days/Week** to avoid overtraining and injury (Gabbett's Acute:Chronic Workload Ratio)."
        elif club_hours >= 6:
            recommended_days = 3
            fatigue_reduction = 0.95
            freq_rationale = f"Moderate club exposure ({club_hours} hrs/week). S&C frequency is set to **3 Days/Week** for optimal adaptation without central fatigue build-up."
        else:
            recommended_days = 4
            fatigue_reduction = 1.00
            freq_rationale = f"Low external club exposure ({club_hours} hrs/week). S&C frequency is set to **4 Days/Week** to maximize all athletic components."

        # Compute Load Targets based on Assessment Metrics
        base_squat = round((weight * 0.80 * (cmj / 40.0) * fatigue_reduction), 1)
        base_press = round((weight * 0.45 * (pushups / 30.0) * fatigue_reduction), 1)
        base_rdl = round((weight * 0.90 * (cmj / 40.0) * fatigue_reduction), 1)

        # Overview Display
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='margin:0; color:#38bdf8;'>👤 Athlete: {name} | 🧢 Evaluating Coach: {coach}</h3>
            <p style='margin:5px 0 0 0; color:#cbd5e1;'>Recommended S&C Training Days: <b>{recommended_days} Days / Week</b> | Club Exposure: {club_hours} hrs/wk</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info(f"💡 **Training Frequency Logic:** {freq_rationale}")

        st.markdown("---")
        st.subheader("🗓️ 1-Month Week-by-Week Detailed Prescriptive Plan")

        # --------------------------------------
        # WEEK 1
        # --------------------------------------
        with st.expander("📌 WEEK 1: Accumulation & Neuromuscular Priming", expanded=True):
            w1_df = pd.DataFrame({
                "Category / Focus": ["Mobility Priming", "Explosive Power", "Lower Strength (Hinge)", "Upper Strength (Push)", "Unilateral Pull", "Energy Systems (ESD)"],
                "Exercise Name": ["90/90 Hip Flow & Thoracic CARs", "Countermovement Box Jumps", "Barbell / DB Romanian Deadlift", "DB Neutral Overhead Press", "Single-Arm Cable Row", "AirBike Zone 2 Aerobic Base"],
                "Sets x Reps": ["2 x 8 Reps/side", "3 x 4 Reps", "3 x 8 Reps", "3 x 10 Reps", "3 x 10 Reps/side", "15 Mins"],
                "Prescribed Load": ["Bodyweight", "Bodyweight (Focus Speed)", f"{base_rdl} kg", f"{base_press} kg", f"{round(base_press*0.6, 1)} kg", "65-70% HRMax"],
                "Equipment": ["Mat", "Plyo Box", "Barbell / DB", "Dumbbells", "Cable Station", "AirBike / Rower"],
                "Rest": ["30 sec", "90 sec", "120 sec", "90 sec", "60 sec", "N/A"]
            })
            st.table(w1_df)
            
            st.markdown("""
            <div class='scientific-note'>
                <b>🧬 Week 1 Scientific Basis & Exercise Rationale:</b><br>
                • <b>Why these exercises?</b> Romanian Deadlifts and Neutral DB Presses were selected to build posterior chain motor control and overhead shoulder stability without overtaxing joints.<br>
                • <b>Progression Rule:</b> Focus strictly on movement quality and crisp tempo (3-1-1-0). If RPE is under 7, add +2.5kg next week.<br>
                • <b>Regression Rule:</b> If knee/spine discomfort occurs (or active injury flags trigger), regress RDLs to Hip Thrusts or Kettlebell Deadlifts from blocks.
            </div>
            """, unsafe_allow_html=True)

        # --------------------------------------
        # WEEK 2
        # --------------------------------------
        with st.expander("📌 WEEK 2: Progressive Loading & Capacity Building", expanded=False):
            w2_df = pd.DataFrame({
                "Category / Focus": ["Mobility Priming", "Explosive Power", "Lower Strength (Hinge)", "Upper Strength (Push)", "Unilateral Pull", "Energy Systems (ESD)"],
                "Exercise Name": ["Dynamic World's Greatest Stretch", "Med-Ball Chest Launches", "Barbell / DB Romanian Deadlift", "DB Neutral Overhead Press", "Single-Arm Cable Row", "Aerobic / Lactic Threshold Intervals"],
                "Sets x Reps": ["2 x 10 Reps/side", "4 x 4 Reps", "4 x 8 Reps", "4 x 8 Reps", "4 x 8 Reps/side", "6 x 45s On / 45s Off"],
                "Prescribed Load": ["Bodyweight", "4 kg Med-Ball", f"{round(base_rdl * 1.05, 1)} kg", f"{round(base_press * 1.05, 1)} kg", f"{round(base_press * 0.65, 1)} kg", "80-85% HRMax"],
                "Equipment": ["Mat", "Med-Ball (4kg)", "Barbell / DB", "Dumbbells", "Cable Station", "AirBike / Shuttle Runs"],
                "Rest": ["30 sec", "90 sec", "120 sec", "90 sec", "60 sec", "60 sec"]
            })
            st.table(w2_df)
            
            st.markdown("""
            <div class='scientific-note'>
                <b>🧬 Week 2 Scientific Basis & Progression Rationale:</b><br>
                • <b>Why progressive loading?</b> Load is increased by 5% in accordance with NSCA progressive overload principles to stimulate structural adaptation.<br>
                • <b>Progression Rule:</b> Maintain technical execution under increased set volume.<br>
                • <b>Regression Rule:</b> Reduce set volume back to 3 sets if club training fatigue creates performance drop-off during speed drills.
            </div>
            """, unsafe_allow_html=True)

        # --------------------------------------
        # WEEK 3
        # --------------------------------------
        with st.expander("📌 WEEK 3: Peak Functional Overreach & Speed-Power Focus", expanded=False):
            w3_df = pd.DataFrame({
                "Category / Focus": ["Mobility Priming", "Explosive Power", "Lower Strength (Hinge)", "Upper Strength (Push)", "Unilateral Pull", "Energy Systems (ESD)"],
                "Exercise Name": ["Multi-Planar Ankle & Hip Flow", "Broad Jump to Stick Landing", "Barbell / DB Romanian Deadlift", "DB Neutral Overhead Press", "Weighted Pull-ups / Cable Lat Pulls", "High-Intensity Repeat Sprint Ability"],
                "Sets x Reps": ["2 x 10 Reps", "4 x 3 Reps", "4 x 6 Reps", "4 x 6 Reps", "4 x 6 Reps", "8 x 15s All-Out / 45s Rest"],
                "Prescribed Load": ["Bodyweight", "Bodyweight", f"{round(base_rdl * 1.10, 1)} kg", f"{round(base_press * 1.10, 1)} kg", "Bodyweight + 5kg", "Max Effort"],
                "Equipment": ["Mat", "Turf / Mat", "Barbell / DB", "Dumbbells", "Pull-Up Bar / Cable", "Turf / Bike"],
                "Rest": ["30 sec", "120 sec", "150 sec", "120 sec", "90 sec", "45 sec"]
            })
            st.table(w3_df)
            
            st.markdown("""
            <div class='scientific-note'>
                <b>🧬 Week 3 Scientific Basis & Peak Rationale:</b><br>
                • <b>Why Peak Overreach?</b> Week 3 introduces peak intensity (+10% load) with reduced rep counts (6 reps) to train high-threshold motor unit recruitment without excess metabolic damage.<br>
                • <b>Progression Rule:</b> If bar speed remains fast, athlete is ready for post-block testing.<br>
                • <b>Regression Rule:</b> Drop load by 10% if technique breaks down on reps 5 and 6.
            </div>
            """, unsafe_allow_html=True)

        # --------------------------------------
        # WEEK 4
        # --------------------------------------
        with st.expander("📌 WEEK 4: Deload, Supercompensation & Re-Assessment", expanded=False):
            w4_df = pd.DataFrame({
                "Category / Focus": ["Mobility Priming", "Decompression", "Lower Strength", "Upper Strength", "Re-Assessment", "Active Recovery"],
                "Exercise Name": ["Full Body SFMA Correctives", "Light Goblet Squats", "DB Romanian Deadlifts", "Light Overhead DB Press", "CMJ & Push-up Re-Test", "Zone 1 Light Flush"],
                "Sets x Reps": ["2 x 10 Reps", "2 x 8 Reps", "2 x 8 Reps", "2 x 8 Reps", "3 Max Effort Trials", "15 Mins"],
                "Prescribed Load": ["Bodyweight", f"{round(base_squat * 0.5, 1)} kg", f"{round(base_rdl * 0.5, 1)} kg", f"{round(base_press * 0.5, 1)} kg", "Bodyweight", "50-60% HRMax"],
                "Equipment": ["Mat", "Kettlebell", "Dumbbells", "Dumbbells", "Jump Mat / Tape", "Rower / Bike"],
                "Rest": ["30 sec", "60 sec", "60 sec", "60 sec", "180 sec", "N/A"]
            })
            st.table(w4_df)
            
            st.markdown("""
            <div class='scientific-note'>
                <b>🧬 Week 4 Scientific Basis & Supercompensation Rationale:</b><br>
                • <b>Why Deload & Re-Test?</b> Volume is dropped by 50% to allow neuromuscular recovery and supercompensation (Bompa & Haff Periodization Model). Re-assessment protocols on Day 3 evaluate progress against baseline metrics.<br>
                • <b>Follow-Up Action:</b> The assessing coach will log scores into <b>Module 5 (Saved Records & Follow-Up)</b> to quantify percentage gains.
            </div>
            """, unsafe_allow_html=True)
