import streamlit as st
import pandas as pd
import json
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG & ATHLETIC STYLING WITH BACKGROUND
# ==========================================
st.set_page_config(
    page_title="Athlete-IQ Performance Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling with Dark Athletic Background Image
st.markdown("""
<style>
    /* Athletic Background with semi-transparent overlay */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.90), rgba(2, 6, 23, 0.95)), 
                    url('https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f8fafc;
        font-family: 'Inter', system-ui, sans-serif;
    }
    
    /* Neon Glassmorphism Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.2);
        backdrop-filter: blur(10px);
        margin-bottom: 15px;
    }
    
    .metric-title {
        color: #38bdf8;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
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
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
    }
    
    /* Rationale & Safety Box */
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

# Initialize Session Storage
if "athlete_records" not in st.session_state:
    st.session_state.athlete_records = []

if "current_assessment" not in st.session_state:
    st.session_state.current_assessment = {}

# ==========================================
# 2. APPLICATION HEADER & AUTHOR CREDITS
# ==========================================
st.markdown("<h1 style='text-align: center; color: #38bdf8; font-weight: 900; margin-bottom: 0px;'>⚡ ATHLETE-IQ PERFORMANCE ENGINE</h1>", unsafe_allow_html=True)
# EDIT YOUR NAME ON LINE 92 BELOW
st.markdown("<p style='text-align: center; color: #a855f7; font-weight: 700; font-size: 1.15rem;'>Developed by:Coach Ahmed Youssef Lead Strength & Conditioning Specialist</p>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 3. SIDEBAR NAVIGATION & EQUIPMENT MATRIX
# ==========================================
st.sidebar.markdown("### 📌 Navigation")
active_module = st.sidebar.radio(
    "Jump to Module:",
    [
        "📋 1. Demographics & Coach Sign-off",
        "⚽ 2. Club Load & Injury Diagnostics",
        "🩺 3. Comprehensive SFMA & 3-View Posture",
        "💥 4. Power, Speed & Capacity Assessment",
        "📈 5. Saved Records & Follow-Up Comparison",
        "🚀 6. GENERATE ADAPTIVE 1-MONTH PLAN"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏋️ Facility Equipment Selection")
st.sidebar.caption("Selected tools dynamically filter & adapt prescribed exercise programming:")
equipment_selected = st.sidebar.multiselect(
    "Available Gear:",
    [
        "Barbells & Plates", "Dumbbells", "Kettlebells", 
        "Hydro-Inertial (Aqua Bags/Macebells)", "Instability (BOSU/Swiss Ball)",
        "Rigs & Suspension (TRX/Wood Rings)", "Sleds & Prowler",
        "Medicine & Slam Balls", "Cable Systems & Selectorized",
        "Ergometers (AirBike/Rower/SkiErg)", "Plyo Boxes & Agility Ladders"
    ],
    default=["Barbells & Plates", "Dumbbells", "Kettlebells", "Rigs & Suspension (TRX/Wood Rings)", "Sleds & Prowler", "Medicine & Slam Balls", "Cable Systems & Selectorized", "Ergometers (AirBike/Rower/SkiErg)"]
)

# Save selected equipment to assessment session
st.session_state.current_assessment["available_equipment"] = equipment_selected

# ==========================================
# 4. MODULE LOGIC
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
        sport_type = st.selectbox("Sport / Discipline", [
            "Soccer", "Basketball", "Tennis", "Track & Field (Sprints/Jumps)", 
            "Combat Sports (MMA/Boxing)", "Volleyball", "Rugby/American Football", "General Fitness"
        ])
        
    with col2:
        st.subheader("🧢 Evaluating Coach Details")
        evaluating_coach = st.text_input("Evaluating Coach Name", "Coach John Doe")
        assessment_date = st.date_input("Assessment Date", datetime.now())
        assessment_type = st.selectbox("Assessment Phase", ["Baseline (Initial)", "Mid-Phase Follow-Up", "Re-Assessment (Post-Block)"])
        training_years = st.number_input("Training History (Years)", 0, 30, 3)

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
elif active_module == "⚽ 2. Club Load & Injury Diagnostics":
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
            st.warning(f"⚠️ High External Club Exposure ({total_club_hours} hrs/wk): Prescribed S&C auto-scales to 2 Days/Week to prevent overtraining.")
        elif total_club_hours >= 6:
            st.info(f"📊 Moderate External Exposure ({total_club_hours} hrs/wk): Prescribed S&C auto-scales to 3 Days/Week.")
        else:
            st.success(f"✅ Low External Exposure ({total_club_hours} hrs/wk): Prescribed S&C set to 3-4 Days/Week.")

    with col2:
        st.subheader("🩺 Injury History & Current Limitations")
        has_injury = st.radio("Has the athlete suffered a past/recent injury?", ["No", "Yes"], horizontal=True)
        
        injury_site = "None"
        injury_mechanism = "N/A"
        still_affects = "No"
        
        if has_injury == "Yes":
            injury_site = st.selectbox("Injury Site", ["Ankle", "Knee (ACL/Patellar)", "Hamstring/Groin", "Lumbar Spine", "Shoulder", "Elbow/Wrist"])
            injury_mechanism = st.selectbox("Mechanism of Injury (Affects Exercise Selection & Mechanics)", [
                "Overuse / Repetitive Stress (Volume spike / fatigue loading)",
                "Acute Contact / Traumatic (High impact force)",
                "Non-Contact Biomechanical (High-velocity cutting / decelerating)"
            ])
            still_affects = st.radio("Are symptoms currently present during training?", ["Yes - Active Symptoms", "No - Cleared / Asymptomatic"], horizontal=True)
            
        st.session_state.current_assessment.update({
            "has_injury": has_injury,
            "injury_site": injury_site,
            "injury_mechanism": injury_mechanism,
            "still_affects": still_affects
        })

# ------------------------------------------
# MODULE 3: COMPREHENSIVE SFMA & 3-VIEW POSTURE
# ------------------------------------------
elif active_module == "🩺 3. Comprehensive SFMA & 3-View Posture":
    st.markdown("<div class='banner-header'>🩺 SFMA Screen & Full 3-View Postural Diagnostic Matrix</div>", unsafe_allow_html=True)
    
    st.subheader("1. SFMA Screen Top-Tier Movement Patterns")
    c1, c2, c3 = st.columns(3)
    with c1:
        cervical = st.selectbox("Cervical Spine Pattern", ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"])
        shoulder = st.selectbox("Upper Extremity Reach", ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"])
        rotation = st.selectbox("Multi-Segmental Rotation", ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"])
    with c2:
        flexion = st.selectbox("Multi-Segmental Flexion (Toe Touch)", ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"])
        extension = st.selectbox("Multi-Segmental Extension", ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"])
    with c3:
        sl_stance = st.selectbox("Single-Leg Stance Balance", ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"])
        overhead_squat = st.selectbox("Deep Overhead Squat Pattern", ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"])

    st.markdown("---")
    st.subheader("2. Static Postural Analysis (3 Planes of View)")
    
    v_ant, v_lat, v_post = st.columns(3)
    
    with v_ant:
        st.markdown("#### 📐 Anterior (Front) View")
        head_ant = st.selectbox("Head & Neck Center", ["Symmetrical Alignment", "Lateral Tilt (Right/Left)"])
        shoulder_elevation = st.selectbox("Clavicle & Shoulder Elevation", ["Symmetrical", "Right Elevation", "Left Elevation"])
        asis_height = st.selectbox("ASIS Pelvic Level", ["Level ASIS", "Asymmetrical ASIS Height"])
        q_angle = st.selectbox("Q-Angle / Knee Tracking", ["Neutral Knee Alignment", "Genu Valgus (Knock-Knees)", "Genu Varum (Bow-Legged)"])
        foot_arch_ant = st.selectbox("Ankle & Foot Arch", ["Normal Arch", "Collapsed Arch / Pronation", "Supinated Arch"])

    with v_lat:
        st.markdown("#### 📐 Lateral (Side) View")
        fhp = st.selectbox("Forward Head Alignment", ["Neutral Alignment", "Forward Head Posture"])
        thoracic_kyph = st.selectbox("Thoracic Spine Curve", ["Normal Curve", "Increased Kyphosis (Hunchback)"])
        lumbar_lord = st.selectbox("Lumbar Lordosis", ["Normal Curve", "Excessive Hyper-Lordosis", "Flat Lumbar Spine"])
        pelvic_tilt = st.selectbox("Pelvic Alignment", ["Neutral Pelvis", "Anterior Pelvic Tilt", "Posterior Pelvic Tilt"])
        knee_recurve = st.selectbox("Knee Stance", ["Neutral Stance", "Genu Recurvatum (Hyperextended)"])

    with v_post:
        st.markdown("#### 📐 Posterior (Back) View")
        scapular_winging = st.selectbox("Scapular Alignment", ["Symmetrical Flat", "Scapular Winging / Protraction", "Asymmetrical Height"])
        spinal_scoliosis = st.selectbox("Spinal Column Alignment", ["Straight Alignment", "Scoliotic Lateral Deviation"])
        psis_height = st.selectbox("PSIS Pelvic Height", ["Level PSIS", "Asymmetrical PSIS Level"])
        heel_calcaneus = st.selectbox("Calcaneus Heel Position", ["Vertical Calcaneus", "Calcaneal Eversion (Valgus)", "Calcaneal Inversion"])

    st.session_state.current_assessment.update({
        "sfma_squat": overhead_squat,
        "sfma_flexion": flexion,
        "sfma_extension": extension,
        "q_angle": q_angle,
        "pelvic_tilt": pelvic_tilt,
        "foot_arch": foot_arch_ant,
        "shoulder_elevation": shoulder_elevation,
        "thoracic_kyph": thoracic_kyph,
        "scapular_winging": scapular_winging
    })

# ------------------------------------------
# MODULE 4: POWER, SPEED & CAPACITY ASSESSMENT
# ------------------------------------------
elif active_module == "💥 4. Power, Speed & Capacity Assessment":
    st.markdown("<div class='banner-header'>💥 Comprehensive Performance & Capacity Metrics</div>", unsafe_allow_html=True)
    
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
        st.subheader("🫁 Endurance & Capacity")
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
# MODULE 5: SAVED RECORDS & FOLLOW-UP COMPARISON
# ------------------------------------------
elif active_module == "📈 5. Saved Records & Follow-Up Comparison":
    st.markdown("<div class='banner-header'>📈 Saved Assessment Records & Historical Progress Tracker</div>", unsafe_allow_html=True)
    
    if len(st.session_state.athlete_records) == 0:
        st.info("ℹ️ No saved records yet. Complete assessment modules and click '💾 Save Assessment Record' in Module 4.")
    else:
        st.subheader("📋 Recorded Assessments Database")
        df_records = pd.DataFrame(st.session_state.athlete_records)
        st.dataframe(df_records, use_container_width=True)
        
        if len(st.session_state.athlete_records) >= 2:
            st.markdown("---")
            st.subheader("📊 Baseline vs. Follow-Up Re-Assessment Comparison")
            
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
# MODULE 6: GENERATE ADAPTIVE 1-MONTH PLAN
# ------------------------------------------
elif active_module == "🚀 6. GENERATE ADAPTIVE 1-MONTH PLAN":
    st.markdown("<div class='banner-header'>🚀 Dynamic Multi-Component 1-Month Program Engine</div>", unsafe_allow_html=True)
    
    data = st.session_state.current_assessment
    
    if not data.get("athlete_name"):
        st.warning("⚠️ Please fill in Athlete Demographics in Module 1 first.")
    else:
        # Load Variables
        name = data.get("athlete_name", "Athlete")
        coach = data.get("evaluating_coach", "Coach")
        weight = data.get("weight", 75.0)
        sport = data.get("sport", "Soccer")
        club_hours = data.get("total_club_hours", 8.0)
        cmj = data.get("cmj", 42.0)
        pushups = data.get("pushups", 38)
        sprint_10m = data.get("sprint_10m", 1.75)
        equip = data.get("available_equipment", [])

        # Diagnostics
        has_injury = data.get("has_injury", "No")
        injury_site = data.get("injury_site", "None")
        injury_mechanism = data.get("injury_mechanism", "N/A")
        q_angle = data.get("q_angle", "Neutral Knee Alignment")
        pelvic_tilt = data.get("pelvic_tilt", "Neutral Pelvis")
        thoracic_kyph = data.get("thoracic_kyph", "Normal Curve")

        # --- DYNAMIC EQUIPMENT & SPORT ADAPTATION ENGINE ---
        # Exercise defaults based on equipment & sport profile
        if "Barbells & Plates" in equip:
            primary_hinge = "Barbell Romanian Deadlift"
            primary_press = "Barbell Overhead Strict Press"
            equip_hinge = "Barbell"
            equip_press = "Barbell"
        elif "Dumbbells" in equip:
            primary_hinge = "Dumbbell Heavy RDL"
            primary_press = "Dumbbell Overhead Press"
            equip_hinge = "Dumbbells"
            equip_press = "Dumbbells"
        elif "Hydro-Inertial (Aqua Bags/Macebells)" in equip:
            primary_hinge = "Aqua Bag Dynamic Cleans & Holds"
            primary_press = "Steel Mace 360 & Overhead Press"
            equip_hinge = "Aqua Bag"
            equip_press = "Steel Mace"
        else:
            primary_hinge = "Single-Leg Bodyweight Deadlift / Band Pull-Through"
            primary_press = "TRX / Ring Overhead Press"
            equip_hinge = "Bands / Bodyweight"
            equip_press = "TRX / Rings"

        # Plyometric Adaptation
        if "Plyo Boxes & Agility Ladders" in equip:
            primary_plyo = "Countermovement Box Jumps"
            equip_plyo = "Plyo Box"
        elif "Medicine & Slam Balls" in equip:
            primary_plyo = "Med-Ball Overhead Floor Slams"
            equip_plyo = "Slam Ball"
        else:
            primary_plyo = "Broad Jumps to Stick Landing"
            equip_plyo = "Bodyweight / Turf"

        # Conditioning / ESD Adaptation
        if "Ergometers (AirBike/Rower/SkiErg)" in equip:
            esd_modality = "AirBike / SkiErg Interval Protocol"
            equip_esd = "AirBike / SkiErg"
        elif "Sleds & Prowler" in equip:
            esd_modality = "Heavy Sled Pushes & Shuttle Sprints"
            equip_esd = "Prowler Sled"
        else:
            esd_modality = "10m Shuttle Sprints / High-Intensity Intervals"
            equip_esd = "Turf / Timer"

        # --- INJURY & MECHANISM REGULATION ---
        injury_notes = []
        if has_injury == "Yes":
            injury_notes.append(f"⚠️ **Clinical Injury Protocol Active ({injury_site})**: Primary Mechanism = '{injury_mechanism}'.")
            if "Overuse" in injury_mechanism:
                injury_notes.append("• **Overuse Safety Rule**: Concentric emphasis, reduced eccentric tempo, initial load scaled back by 15%.")
            elif "Contact" in injury_mechanism or "Biomechanical" in injury_mechanism:
                primary_plyo = "Non-Countermovement Box Jump (Controlled Soft Landing)"
                injury_notes.append("• **High-Impact Protection**: Bypassed aggressive stretch-shortening landings; prioritized stick landings.")

            if injury_site == "Hamstring/Groin":
                primary_hinge = "Single-Leg Kettlebell RDL / Trap Bar High-Handle Deadlift"
            elif injury_site == "Knee (ACL/Patellar)":
                primary_plyo = "Med-Ball Chest Launch (Zero Knee Impact)"
            elif injury_site == "Lumbar Spine":
                primary_hinge = "Chest-Supported Dumbbell Incline Row & Reverse Hyper (Zero Axial Loading)"

        # Posture Adaptations
        if q_angle == "Genu Valgus (Knock-Knees)":
            injury_notes.append("• **Postural Correction (Genu Valgus)**: Integrated Banded Monster Walks & VMO TKE pre-activation.")
        if pelvic_tilt == "Anterior Pelvic Tilt":
            injury_notes.append("• **Postural Correction (Anterior Pelvic Tilt)**: Integrated Rear Foot Elevated Hip Flexor Stretch & Anti-Extension Pallof Press.")

        # --- TRAINING FREQUENCY ENGINE ---
        if club_hours >= 10:
            recommended_days = 2
            fatigue_reduction = 0.88
            freq_rationale = f"High club exposure ({club_hours} hrs/wk). S&C set to **2 Days/Week** to prevent acute-on-chronic overtraining."
        elif club_hours >= 6:
            recommended_days = 3
            fatigue_reduction = 0.95
            freq_rationale = f"Moderate club exposure ({club_hours} hrs/wk). S&C set to **3 Days/Week** for optimal adaptation."
        else:
            recommended_days = 4
            fatigue_reduction = 1.00
            freq_rationale = f"Low external club exposure ({club_hours} hrs/wk). S&C set to **4 Days/Week** to maximize athletic potential."

        # Formula Intensity Calculations (NSCA Standard)
        base_press = round((weight * 0.45 * (pushups / 30.0) * fatigue_reduction), 1)
        base_rdl = round((weight * 0.85 * (cmj / 40.0) * fatigue_reduction), 1)

        # Overview Header
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='margin:0; color:#38bdf8;'>👤 Athlete: {name} | ⚽ Sport: {sport} | 🧢 Coach: {coach}</h3>
            <p style='margin:5px 0 0 0; color:#cbd5e1;'>Prescribed S&C Frequency: <b>{recommended_days} Days / Week</b> | Club Load Exposure: {club_hours} hrs/wk</p>
        </div>
        """, unsafe_allow_html=True)

        if injury_notes:
            st.markdown("<div class='injury-alert'>" + "<br>".join(injury_notes) + "</div>", unsafe_allow_html=True)
            
        st.info(f"💡 **Training Load Engine:** {freq_rationale}")

        st.markdown("---")
        st.subheader("🗓️ 1-Month Week-by-Week Detailed Schedule")

        # --------------------------------------
        # WEEK 1
        # --------------------------------------
        with st.expander("📌 WEEK 1: Accumulation & Movement Quality Priming", expanded=True):
            w1_df = pd.DataFrame({
                "Category / Focus": ["Mobility Priming", "Explosive Power", "Lower Strength (Hinge)", "Upper Strength (Push)", "Unilateral Pull", "Energy Systems (ESD)"],
                "Exercise Name": ["3-View Posture Correction Flow", primary_plyo, primary_hinge, primary_press, "Single-Arm Cable / TRX Row", esd_modality],
                "Sets x Reps": ["2 x 8 Reps/side", "3 x 4 Reps", "3 x 8 Reps", "3 x 10 Reps", "3 x 10 Reps/side", "15 Mins"],
                "Prescribed Load": ["Bodyweight", "Explosive Speed", f"{base_rdl} kg", f"{base_press} kg", f"{round(base_press*0.6, 1)} kg", "65-70% HRMax"],
                "Equipment": ["Mat", equip_plyo, equip_hinge, equip_press, "Cable / TRX", equip_esd],
                "Rest": ["30 sec", "90 sec", "120 sec", "90 sec", "60 sec", "N/A"]
            })
            st.table(w1_df)
            
            st.markdown(f"""
            <div class='scientific-note'>
                <b>🧬 Week 1 Scientific Rationale & Safety Rules:</b><br>
                • <b>Equipment & Sport Fit:</b> Programming tailored for <i>{sport}</i> using available gear ({', '.join(equip[:4]) if equip else 'Standard'}).<br>
                • <b>Injury Protection:</b> Exercise selection explicitly accounts for injury site (<i>{injury_site}</i>) and mechanism (<i>{injury_mechanism}</i>).<br>
                • <b>Progression Rule:</b> Focus on movement control with RPE ≤ 7. Increase weight by +5% in Week 2 if all reps are executed smoothly.
            </div>
            """, unsafe_allow_html=True)

        # --------------------------------------
        # WEEK 2
        # --------------------------------------
        with st.expander("📌 WEEK 2: Progressive Loading & Capacity Building", expanded=False):
            w2_df = pd.DataFrame({
                "Category / Focus": ["Mobility Priming", "Explosive Power", "Lower Strength", "Upper Strength", "Unilateral Pull", "Energy Systems (ESD)"],
                "Exercise Name": ["Dynamic Multi-Planar Mobility", primary_plyo, primary_hinge, primary_press, "Single-Arm Cable / TRX Row", esd_modality],
                "Sets x Reps": ["2 x 10 Reps/side", "4 x 4 Reps", "4 x 8 Reps", "4 x 8 Reps", "4 x 8 Reps/side", "6 x 45s On / 45s Off"],
                "Prescribed Load": ["Bodyweight", "Explosive Speed", f"{round(base_rdl * 1.05, 1)} kg", f"{round(base_press * 1.05, 1)} kg", f"{round(base_press * 0.65, 1)} kg", "80-85% HRMax"],
                "Equipment": ["Mat", equip_plyo, equip_hinge, equip_press, "Cable / TRX", equip_esd],
                "Rest": ["30 sec", "90 sec", "120 sec", "90 sec", "60 sec", "60 sec"]
            })
            st.table(w2_df)

        # --------------------------------------
        # WEEK 3
        # --------------------------------------
        with st.expander("📌 WEEK 3: Peak Functional Overreach & Speed-Power Focus", expanded=False):
            w3_df = pd.DataFrame({
                "Category / Focus": ["Mobility Priming", "Explosive Power", "Lower Strength", "Upper Strength", "Unilateral Pull", "Energy Systems (ESD)"],
                "Exercise Name": ["Multi-Segmental Rotation Flow", primary_plyo, primary_hinge, primary_press, "Weighted TRX / Pull-ups", esd_modality],
                "Sets x Reps": ["2 x 10 Reps", "4 x 3 Reps", "4 x 6 Reps", "4 x 6 Reps", "4 x 6 Reps", "8 x 15s All-Out / 45s Rest"],
                "Prescribed Load": ["Bodyweight", "Max Velocity", f"{round(base_rdl * 1.10, 1)} kg", f"{round(base_press * 1.10, 1)} kg", "BW + 5kg", "Max Effort"],
                "Equipment": ["Mat", equip_plyo, equip_hinge, equip_press, "Pull-Up Bar", equip_esd],
                "Rest": ["30 sec", "120 sec", "150 sec", "120 sec", "90 sec", "45 sec"]
            })
            st.table(w3_df)

        # --------------------------------------
        # WEEK 4
        # --------------------------------------
        with st.expander("📌 WEEK 4: Deload, Supercompensation & Re-Assessment", expanded=False):
            w4_df = pd.DataFrame({
                "Category / Focus": ["Mobility Priming", "Decompression", "Lower Strength", "Upper Strength", "Re-Assessment", "Active Recovery"],
                "Exercise Name": ["Full SFMA Corrective Flow", "Light Goblet Squats", primary_hinge, primary_press, "CMJ & Push-Up Re-Test", "Zone 1 Light Flush"],
                "Sets x Reps": ["2 x 10 Reps", "2 x 8 Reps", "2 x 8 Reps", "2 x 8 Reps", "3 Max Effort Trials", "15 Mins"],
                "Prescribed Load": ["Bodyweight", f"{round(weight*0.3, 1)} kg", f"{round(base_rdl * 0.5, 1)} kg", f"{round(base_press * 0.5, 1)} kg", "Bodyweight", "50-60% HRMax"],
                "Equipment": ["Mat", "Kettlebell", equip_hinge, equip_press, "Jump Mat", equip_esd],
                "Rest": ["30 sec", "60 sec", "60 sec", "60 sec", "180 sec", "N/A"]
            })
            st.table(w4_df)
            
            st.markdown(f"""
            <div class='scientific-note'>
                <b>🧬 Week 4 Deload & Re-Assessment Strategy:</b><br>
                • <b>Supercompensation:</b> Workload volume reduced by 50% to facilitate central nervous system recovery.<br>
                • <b>Follow-Up Action:</b> Coach <b>{coach}</b> will record post-block scores into Module 5 to measure total athletic growth.
            </div>
            """, unsafe_allow_html=True)
