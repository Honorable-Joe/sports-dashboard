from datetime import datetime
import pandas as pd
import streamlit as st

# ==========================================
# 1. PAGE CONFIG & ATHLETIC STYLING
# ==========================================
st.set_page_config(
    page_title="Athlete-IQ Performance Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.90), rgba(2, 6, 23, 0.95)), 
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
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. PERSISTENT SESSION STATE INITIALIZATION
# ==========================================
if "form_data" not in st.session_state:
    st.session_state.form_data = {
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
        "club_days": 4,
        "club_hours_per_day": 2.0,
        "has_injury": "No",
        "injury_site": "None",
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
        # 3-View Posture
        "head_ant": "Symmetrical Alignment",
        "shoulder_elevation": "Symmetrical",
        "asis_height": "Level ASIS",
        "q_angle": "Neutral Knee Alignment",
        "foot_arch_ant": "Normal Arch",
        "fhp": "Neutral Alignment",
        "thoracic_kyph": "Normal Curve",
        "lumbar_lord": "Normal Curve",
        "pelvic_tilt": "Neutral Pelvis",
        "knee_recurve": "Neutral Stance",
        "scapular_winging": "Symmetrical Flat",
        "spinal_scoliosis": "Straight Alignment",
        "psis_height": "Level PSIS",
        "heel_calcaneus": "Vertical Calcaneus",
        # Performance
        "max_pushups": 38,
        "max_pullups": 12,
        "cooper_meters": 2650,
        "cmj_cm": 42.0,
        "broad_jump_cm": 215.0,
        "sprint_10m": 1.75,
        "t_drill": 10.20,
        "mb_overhead_m": 8.5,
        "mb_forehand_m": 9.2,
        "mb_backhand_m": 8.4,
        "mb_chest_launch_m": 7.2,
    }

if "athlete_records" not in st.session_state:
    st.session_state.athlete_records = []


def bind_input(key):
    return st.session_state.form_data.get(key)


def update_state(key, val):
    st.session_state.form_data[key] = val


# ==========================================
# 3. HEADER & SIDEBAR NAVIGATION
# ==========================================
st.markdown(
    "<h1 style='text-align: center; color: #38bdf8; font-weight: 900; margin-bottom: 0px;'>⚡ ATHLETE-IQ PERFORMANCE ENGINE</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #a855f7; font-weight: 700; font-size: 1.15rem;'>Developed by: Coach Ahmed Youssef 👑</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.sidebar.markdown("### 📌 Navigation")
active_module = st.sidebar.radio(
    "Jump to Module:",
    [
        "📋 1. Demographics & Coach Sign-off",
        "⚽ 2. Club Load & Injury Diagnostics",
        "🩺 3. SFMA & 3-View Posture Diagnostic",
        "💥 4. Sport-Specific Power & Speed Assessment",
        "📈 5. Saved Records & Historical Progress",
        "🚀 6. GENERATE ADAPTIVE PROGRAM",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗓️ Plan Duration Horizon")
plan_months = st.sidebar.select_slider(
    "Select Total Training Duration:",
    options=[1, 2, 3],
    value=2,
    format_func=lambda x: f"{x}-Month Macrocycle Block",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏋️ Facility Equipment Matrix")
equipment_selected = st.sidebar.multiselect(
    "Available Gear:",
    [
        "Barbells & Plates",
        "Dumbbells",
        "Kettlebells",
        "Hydro-Inertial (Aqua Bags/Macebells)",
        "Instability (BOSU/Swiss Ball)",
        "Rigs & Suspension (TRX/Wood Rings)",
        "Sleds & Prowler",
        "Medicine & Slam Balls",
        "Cable Systems & Selectorized",
        "Ergometers (AirBike/Rower/SkiErg)",
        "Plyo Boxes & Agility Ladders",
    ],
    default=[
        "Barbells & Plates",
        "Dumbbells",
        "Kettlebells",
        "Rigs & Suspension (TRX/Wood Rings)",
        "Sleds & Prowler",
        "Medicine & Slam Balls",
        "Cable Systems & Selectorized",
        "Ergometers (AirBike/Rower/SkiErg)",
        "Plyo Boxes & Agility Ladders",
    ],
)

# ==========================================
# 4. MODULE CONTROLLERS
# ==========================================

# ------------------------------------------
# MODULE 1: DEMOGRAPHICS
# ------------------------------------------
if active_module == "📋 1. Demographics & Coach Sign-off":
    st.markdown(
        "<div class='banner-header'>📋 Athlete Demographics & Evaluating Coach Sign-Off</div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👤 Athlete Profile")
        v_name = st.text_input("Athlete Name", value=bind_input("athlete_name"))
        v_age = st.number_input("Age", 12, 80, value=bind_input("age"))
        v_gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"],
            index=["Male", "Female", "Other"].index(bind_input("gender")),
        )
        v_weight = st.number_input(
            "Body Weight (kg)", 40.0, 150.0, value=bind_input("weight_kg")
        )
        v_height = st.number_input(
            "Height (cm)", 120.0, 230.0, value=bind_input("height_cm")
        )
        sports_list = [
            "Tennis",
            "Volleyball",
            "Combat Sports (MMA/Boxing)",
            "Racket Sports (Squash/Padel)",
            "Soccer",
            "Basketball",
            "Track & Field (Sprints/Jumps)",
            "Rugby/American Football",
            "General Fitness",
        ]
        v_sport = st.selectbox(
            "Sport / Discipline",
            sports_list,
            index=sports_list.index(bind_input("sport_type")),
        )
    with c2:
        st.subheader("🧢 Evaluating Coach Details")
        v_coach = st.text_input(
            "Evaluating Coach Name", value=bind_input("evaluating_coach")
        )
        v_date = st.date_input(
            "Assessment Date", value=bind_input("assessment_date")
        )
        phases = [
            "Baseline (Initial)",
            "Mid-Phase Follow-Up",
            "Re-Assessment (Post-Block)",
        ]
        v_phase = st.selectbox(
            "Assessment Phase",
            phases,
            index=phases.index(bind_input("assessment_type")),
        )
        v_years = st.number_input(
            "Training History (Years)",
            0,
            30,
            value=bind_input("training_years"),
        )

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
# MODULE 2: CLUB LOAD & INJURY
# ------------------------------------------
elif active_module == "⚽ 2. Club Load & Injury Diagnostics":
    st.markdown(
        "<div class='banner-header'>⚽ Club Training Load & Clinical Injury Diagnostics</div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚽ External Club Training Exposure")
        v_days = st.number_input(
            "Club Training Days / Week", 0, 7, value=bind_input("club_days")
        )
        v_hours = st.number_input(
            "Avg Session Duration (Hours)",
            0.5,
            5.0,
            value=bind_input("club_hours_per_day"),
        )
        tot_hrs = v_days * v_hours
        update_state("club_days", v_days)
        update_state("club_hours_per_day", v_hours)

        if tot_hrs >= 10:
            st.warning(
                f"⚠️ High External Load ({tot_hrs} hrs/wk): Prescribed S&C auto-condenses to 2 Days/Week (Full-Body Dense)."
            )
        elif tot_hrs >= 6:
            st.info(
                f"📊 Moderate External Load ({tot_hrs} hrs/wk): Prescribed S&C auto-scales to 3 Days/Week."
            )
        else:
            st.success(
                f"✅ Low External Load ({tot_hrs} hrs/wk): Prescribed S&C set to 4 Days/Week."
            )

    with c2:
        st.subheader("🩺 Injury Assessment")
        v_has_inj = st.radio(
            "Active / Recent Injury?",
            ["No", "Yes"],
            index=["No", "Yes"].index(bind_input("has_injury")),
            horizontal=True,
        )
        if v_has_inj == "Yes":
            sites = [
                "Ankle",
                "Knee (ACL/Patellar)",
                "Hamstring/Groin",
                "Lumbar Spine",
                "Shoulder",
                "Elbow/Wrist",
            ]
            v_site = st.selectbox(
                "Injury Site",
                sites,
                index=sites.index(bind_input("injury_site"))
                if bind_input("injury_site") in sites
                else 0,
            )
            mechs = [
                "Overuse / Repetitive Stress",
                "Acute Contact / Traumatic",
                "Non-Contact Biomechanical",
            ]
            v_mech = st.selectbox(
                "Mechanism",
                mechs,
                index=mechs.index(bind_input("injury_mechanism"))
                if bind_input("injury_mechanism") in mechs
                else 0,
            )
            affects = [
                "Yes - Active Symptoms",
                "No - Cleared / Asymptomatic",
            ]
            v_affects = st.radio(
                "Symptoms Present Currently?",
                affects,
                index=affects.index(bind_input("still_affects"))
                if bind_input("still_affects") in affects
                else 0,
                horizontal=True,
            )
        else:
            v_site, v_mech, v_affects = "None", "N/A", "No"

        update_state("has_injury", v_has_inj)
        update_state("injury_site", v_site)
        update_state("injury_mechanism", v_mech)
        update_state("still_affects", v_affects)

# ------------------------------------------
# MODULE 3: SFMA & 3-VIEW POSTURE DIAGNOSTIC
# ------------------------------------------
elif active_module == "🩺 3. SFMA & 3-View Posture Diagnostic":
    st.markdown(
        "<div class='banner-header'>🩺 SFMA Screen & Full 3-View Postural Diagnostic Matrix</div>",
        unsafe_allow_html=True,
    )
    sfma_opts = [
        "Functional Non-Painful",
        "Dysfunctional Non-Painful",
        "Dysfunctional Painful",
    ]

    st.subheader("1. SFMA Top-Tier Movement Patterns")
    c1, c2, c3 = st.columns(3)
    with c1:
        v_cerv = st.selectbox(
            "Cervical Spine Pattern",
            sfma_opts,
            index=sfma_opts.index(bind_input("cervical")),
        )
        v_shld = st.selectbox(
            "Upper Extremity Reach",
            sfma_opts,
            index=sfma_opts.index(bind_input("shoulder")),
        )
        v_rot = st.selectbox(
            "Multi-Segmental Rotation",
            sfma_opts,
            index=sfma_opts.index(bind_input("rotation")),
        )
    with c2:
        v_flex = st.selectbox(
            "Multi-Segmental Flexion",
            sfma_opts,
            index=sfma_opts.index(bind_input("flexion")),
        )
        v_ext = st.selectbox(
            "Multi-Segmental Extension",
            sfma_opts,
            index=sfma_opts.index(bind_input("extension")),
        )
    with c3:
        v_sls = st.selectbox(
            "Single-Leg Stance Balance",
            sfma_opts,
            index=sfma_opts.index(bind_input("sl_stance")),
        )
        v_ohs = st.selectbox(
            "Deep Overhead Squat Pattern",
            sfma_opts,
            index=sfma_opts.index(bind_input("overhead_squat")),
        )

    update_state("cervical", v_cerv)
    update_state("shoulder", v_shld)
    update_state("rotation", v_rot)
    update_state("flexion", v_flex)
    update_state("extension", v_ext)
    update_state("sl_stance", v_sls)
    update_state("overhead_squat", v_ohs)

    st.markdown("---")
    st.subheader("2. Static Postural Assessment (3-View)")

    p_col1, p_col2, p_col3 = st.columns(3)

    with p_col1:
        st.markdown("**🖼️ Anterior View (Front)**")
        v_head_ant = st.selectbox(
            "Head & Neck Alignment",
            ["Symmetrical Alignment", "Forward/Lateral Tilt"],
            index=0
            if bind_input("head_ant") == "Symmetrical Alignment"
            else 1,
        )
        v_shld_elev = st.selectbox(
            "Shoulder Line",
            ["Symmetrical", "Left Elevated", "Right Elevated"],
            index=0,
        )
        v_asis = st.selectbox(
            "ASIS Level",
            ["Level ASIS", "Asymmetrical ASIS"],
            index=0 if bind_input("asis_height") == "Level ASIS" else 1,
        )
        v_q = st.selectbox(
            "Knee / Q-Angle",
            [
                "Neutral Knee Alignment",
                "Genu Valgum (Knock-Knee)",
                "Genu Varum (Bow-Leg)",
            ],
            index=0,
        )
        v_foot = st.selectbox(
            "Foot Arch",
            [
                "Normal Arch",
                "Flat Foot (Pes Planus)",
                "High Arch (Pes Cavus)",
            ],
            index=0,
        )

    with p_col2:
        st.markdown("**🖼️ Lateral View (Side)**")
        v_fhp = st.selectbox(
            "Forward Head Posture",
            ["Neutral Alignment", "Mild FHP", "Severe FHP"],
            index=0,
        )
        v_kyph = st.selectbox(
            "Thoracic Curve",
            ["Normal Curve", "Hyper-Kyphosis", "Flat Back"],
            index=0,
        )
        v_lord = st.selectbox(
            "Lumbar Curve",
            ["Normal Curve", "Hyper-Lordosis", "Hypo-Lordosis"],
            index=0,
        )
        v_pelvis = st.selectbox(
            "Pelvic Tilt",
            [
                "Neutral Pelvis",
                "Anterior Pelvic Tilt",
                "Posterior Pelvic Tilt",
            ],
            index=0,
        )
        v_knee_rec = st.selectbox(
            "Knee Stance",
            ["Neutral Stance", "Genu Recurvatum (Hyperextended)"],
            index=0,
        )

    with p_col3:
        st.markdown("**🖼️ Posterior View (Back)**")
        v_scap = st.selectbox(
            "Scapular Alignment",
            ["Symmetrical Flat", "Scapular Winging", "Protracted Scapulae"],
            index=0,
        )
        v_scolio = st.selectbox(
            "Spinal Symmetry",
            ["Straight Alignment", "Functional Scoliosis Curve"],
            index=0,
        )
        v_psis = st.selectbox(
            "PSIS Level",
            ["Level PSIS", "Asymmetrical PSIS"],
            index=0,
        )
        v_calc = st.selectbox(
            "Calcaneus Alignment",
            ["Vertical Calcaneus", "Rearfoot Valgus", "Rearfoot Varus"],
            index=0,
        )

    update_state("head_ant", v_head_ant)
    update_state("shoulder_elevation", v_shld_elev)
    update_state("asis_height", v_asis)
    update_state("q_angle", v_q)
    update_state("foot_arch_ant", v_foot)
    update_state("fhp", v_fhp)
    update_state("thoracic_kyph", v_kyph)
    update_state("lumbar_lord", v_lord)
    update_state("pelvic_tilt", v_pelvis)
    update_state("knee_recurve", v_knee_rec)
    update_state("scapular_winging", v_scap)
    update_state("spinal_scoliosis", v_scolio)
    update_state("psis_height", v_psis)
    update_state("heel_calcaneus", v_calc)

# ------------------------------------------
# MODULE 4: POWER & SPEED ASSESSMENT
# ------------------------------------------
elif active_module == "💥 4. Sport-Specific Power & Speed Assessment":
    st.markdown(
        "<div class='banner-header'>💥 Sport-Specific Power, Speed & Capacity Assessment</div>",
        unsafe_allow_html=True,
    )

    current_sport = bind_input("sport_type")
    is_overhead = current_sport in [
        "Tennis",
        "Volleyball",
        "Combat Sports (MMA/Boxing)",
        "Racket Sports (Squash/Padel)",
    ]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("💥 Explosive Power")
        if is_overhead:
            st.caption(
                f"⚡ **Rotational & Overhead Power Suite** ({current_sport}):"
            )
            v_oh_m = st.number_input(
                "Overhead Med-Ball Launch (m)",
                1.0,
                30.0,
                value=bind_input("mb_overhead_m"),
            )
            v_fh_m = st.number_input(
                "Rotational Forehand Launch (m)",
                1.0,
                30.0,
                value=bind_input("mb_forehand_m"),
            )
            v_bh_m = st.number_input(
                "Rotational Backhand Launch (m)",
                1.0,
                30.0,
                value=bind_input("mb_backhand_m"),
            )
            update_state("mb_overhead_m", v_oh_m)
            update_state("mb_forehand_m", v_fh_m)
            update_state("mb_backhand_m", v_bh_m)
        else:
            st.caption(
                f"⚡ **Lower Body Kinetic Power Suite** ({current_sport}):"
            )
            v_cmj = st.number_input(
                "Countermovement Jump (cm)", 10.0, 100.0, value=bind_input("cmj_cm")
            )
            v_bj = st.number_input(
                "Broad Jump (cm)", 50.0, 350.0, value=bind_input("broad_jump_cm")
            )
            v_chest = st.number_input(
                "Med-Ball Chest Launch (m)",
                1.0,
                20.0,
                value=bind_input("mb_chest_launch_m"),
            )
            update_state("cmj_cm", v_cmj)
            update_state("broad_jump_cm", v_bj)
            update_state("mb_chest_launch_m", v_chest)

    with c2:
        st.subheader("🏃 Speed & Agility")
        v_sp10 = st.number_input(
            "10m Acceleration Sprint (sec)",
            1.0,
            4.0,
            value=bind_input("sprint_10m"),
        )
        v_tdrill = st.number_input(
            "T-Drill Agility (sec)", 5.0, 20.0, value=bind_input("t_drill")
        )
        update_state("sprint_10m", v_sp10)
        update_state("t_drill", v_tdrill)

    with c3:
        st.subheader("🫁 Muscular & Aerobic Capacity")
        v_push = st.number_input(
            "Max Push-ups (1 Min)", 0, 100, value=bind_input("max_pushups")
        )
        v_pull = st.number_input(
            "Max Pull-ups (Unbroken)", 0, 50, value=bind_input("max_pullups")
        )
        v_cooper = st.number_input(
            "12-Min Cooper Test (meters)",
            500,
            5000,
            value=bind_input("cooper_meters"),
        )
        update_state("max_pushups", v_push)
        update_state("max_pullups", v_pull)
        update_state("cooper_meters", v_cooper)

    vo2max = round((v_cooper - 504.9) / 44.73, 1)
    st.info(f"📊 **Calculated VO2Max Engine Score**: `{vo2max} mL/kg/min`")

    if st.button("💾 SAVE ASSESSMENT SNAPSHOT TO HISTORICAL DATABASE"):
        rec = st.session_state.form_data.copy()
        rec["vo2max"] = vo2max
        st.session_state.athlete_records.append(rec)
        st.success(
            f"✅ Baseline snapshot saved for {rec['athlete_name']} on {rec['assessment_date']}!"
        )

# ------------------------------------------
# MODULE 5: SAVED RECORDS
# ------------------------------------------
elif active_module == "📈 5. Saved Records & Historical Progress":
    st.markdown(
        "<div class='banner-header'>📈 Saved Assessment Records & Multi-Month Tracking</div>",
        unsafe_allow_html=True,
    )
    if len(st.session_state.athlete_records) == 0:
        st.info(
            "ℹ️ No saved snapshots yet. Complete assessment in Module 4 and click 'Save Assessment Snapshot'."
        )
    else:
        df = pd.DataFrame(st.session_state.athlete_records)
        st.dataframe(df, use_container_width=True)

# ------------------------------------------
# MODULE 6: DYNAMIC CONCURRENT PROGRAM GENERATOR
# ------------------------------------------
elif active_module == "🚀 6. GENERATE ADAPTIVE PROGRAM":
    st.markdown(
        "<div class='banner-header'>🚀 Dynamic Multi-Month Concurrent Training Program</div>",
        unsafe_allow_html=True,
    )

    d = st.session_state.form_data
    name = d["athlete_name"]
    coach = d["evaluating_coach"]
    weight = d["weight_kg"]
    sport = d["sport_type"]
    tot_club_hrs = d["club_days"] * d["club_hours_per_day"]
    has_injury = d["has_injury"]
    injury_site = d["injury_site"]

    # Frequency
    if tot_club_hrs >= 10:
        rec_days = 2
        freq_label = "2 Days/Week (Dense Full-Body Concurrent)"
    elif tot_club_hrs >= 6:
        rec_days = 3
        freq_label = "3 Days/Week (Concurrent Undulating Split)"
    else:
        rec_days = 4
        freq_label = "4 Days/Week (Upper/Lower Concurrent Split)"

    # Base Load Calculations
    pushups = d["max_pushups"]
    cmj = d.get("cmj_cm", 40.0)
    base_press = round(weight * 0.45 * (pushups / 30.0), 1)
    base_hinge = round(weight * 0.85 * (cmj / 40.0), 1)

    st.markdown(
        f"""
    <div class='metric-card'>
        <h3 style='margin:0; color:#38bdf8;'>👤 Athlete: {name} | ⚽ Sport: {sport} | 🧢 Coach: {coach}</h3>
        <p style='margin:5px 0 0 0; color:#cbd5e1;'>Macrocycle Plan Scope: <b>{plan_months}-Month Concurrent Block</b> | Weekly Frequency: <b>{freq_label}</b></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if has_injury == "Yes":
        st.markdown(
            f"<div class='injury-alert'>⚠️ <b>CLINICAL INJURY PROTOCOL ACTIVE ({injury_site})</b><br>Exercises adapted for eccentric control and structural safety. High impact loads restricted.</div>",
            unsafe_allow_html=True,
        )

    # Dynamic Month Progression Logic
    m_tabs = st.tabs([f"🗓️ MONTH {m}" for m in range(1, plan_months + 1)])

    for m_idx, m_tab in enumerate(m_tabs):
        m_num = m_idx + 1
        with m_tab:
            # Exercise Variation by Month
            if m_num == 1:
                focus_desc = "Phase 1: Base Work Capacity, Postural Alignment & Movement Quality"
                ex_mobility = "3-View Posture Correction Flow & Dynamic Mobility"
                ex_power = (
                    "Rotational Med-Ball Slams"
                    if sport
                    in [
                        "Tennis",
                        "Volleyball",
                        "Combat Sports (MMA/Boxing)",
                        "Racket Sports (Squash/Padel)",
                    ]
                    else "Non-Countermovement Box Jump"
                )
                ex_agility = "T-Drill Baseline & Agility Ladder Footwork"
                ex_lower = "Goblet Squats & Romanian Deadlift"
                ex_upper = (
                    "Barbell Strict Press"
                    if "Barbells & Plates" in equipment_selected
                    else "Dumbbell Overhead Press"
                )
                ex_pull = "Single-Arm TRX / Cable Row"
                ex_esd = "AirBike / Shuttle Sprints (Extensive Intervals)"
            elif m_num == 2:
                focus_desc = "Phase 2: Heavy Force Production, Kinetic Chain Power & COD Velocity"
                ex_mobility = (
                    "Thoracic-Hip Dissociation & Active Multi-Planar Mobility"
                )
                ex_power = (
                    "Overhead & Forehand/Backhand Med-Ball Explosive Launches"
                    if sport
                    in [
                        "Tennis",
                        "Volleyball",
                        "Combat Sports (MMA/Boxing)",
                        "Racket Sports (Squash/Padel)",
                    ]
                    else "Explosive Depth Jumps"
                )
                ex_agility = (
                    "Pro Agility (5-10-5) Shuttle & Reactive Deceleration"
                )
                ex_lower = (
                    "Barbell Front Squat / Trap Bar Deadlift"
                    if "Barbells & Plates" in equipment_selected
                    else "Heavy Dumbbell Bulgarian Split Squat"
                )
                ex_upper = "Incline Dumbbell Press / Push Press"
                ex_pull = "Chest-Supported T-Bar / Cable Row"
                ex_esd = "High-Intensity Lactate Threshold Shuttle Repeats"
            else:
                focus_desc = "Phase 3: Rate of Force Development (RFD), Speed-Power Peak & Reactive Agility"
                ex_mobility = (
                    "Dynamic Elastic Priming & Kinetic Chain Pre-Activation"
                )
                ex_power = (
                    "Rotational Med-Ball Step-and-Launch Drops"
                    if sport
                    in [
                        "Tennis",
                        "Volleyball",
                        "Combat Sports (MMA/Boxing)",
                        "Racket Sports (Squash/Padel)",
                    ]
                    else "Contrast Trap Bar Jumps / Banded Plyometrics"
                )
                ex_agility = "Reactive Agility Drills (Visual Trigger Sprints & Cutting)"
                ex_lower = "Barbell Snatch-Grip High Pull / Dynamic Trap Bar Deadlift"
                ex_upper = "Explosive Banded Push Press / Plyo Push-Ups"
                ex_pull = "Weighted Pull-Ups / Explosive High Rows"
                ex_esd = (
                    "Tabata AirBike Repeats & Multi-Directional Anaerobic Sprints"
                )

            st.subheader(f"📌 Month {m_num}: {focus_desc}")

            # Sub-tabs for Weeks 1 to 4
            w_tabs = st.tabs([f"Week {w}" for w in range(1, 5)])

            for w_idx, w_tab in enumerate(w_tabs):
                w_num = w_idx + 1
                with w_tab:
                    if w_num == 1:
                        w_label = "Week 1: Baseline Load Accumulation"
                        sets_reps = "3 x 10 Reps"
                        load_mod = 0.85
                    elif w_num == 2:
                        w_label = "Week 2: Volume & Intensity Escalation"
                        sets_reps = "3 x 8 Reps"
                        load_mod = 0.95
                    elif w_num == 3:
                        w_label = "Week 3: Peak Microcycle Load"
                        sets_reps = "4 x 6 Reps"
                        load_mod = 1.05
                    else:
                        w_label = "Week 4: Strategic Deload & Supercompensation"
                        sets_reps = "2 x 8 Reps (Reduced Load)"
                        load_mod = 0.70

                    st.markdown(f"#### 🗓️ {w_label}")

                    m_df = pd.DataFrame(
                        {
                            "Fitness Component": [
                                "1. Mobility & Priming",
                                "2. Explosive Power",
                                "3. Agility & Change of Direction (COD)",
                                "4. Lower Body Strength (Hinge/Squat)",
                                "5. Upper Body Press",
                                "6. Unilateral Pull & Core",
                                "7. Energy Systems (ESD)",
                            ],
                            "Prescribed Exercise": [
                                ex_mobility,
                                ex_power,
                                ex_agility,
                                ex_lower,
                                ex_upper,
                                ex_pull,
                                ex_esd,
                            ],
                            "Sets x Reps / Time": [
                                "2 x 8 Reps / side",
                                "4 x 4 Reps" if w_num != 4 else "2 x 4 Reps",
                                "4 x 3 Reps / direction"
                                if w_num != 4
                                else "2 x 3 Reps",
                                sets_reps,
                                sets_reps,
                                sets_reps,
                                "12-18 Mins (Intermittent)"
                                if w_num != 4
                                else "10 Mins (Light Zone 2/3)",
                            ],
                            "Prescribed Load": [
                                "Bodyweight",
                                "Max Intent / Speed",
                                "Agility Ladder / Cones (Max Speed)",
                                f"{round(base_hinge * load_mod, 1)} kg",
                                f"{round(base_press * load_mod, 1)} kg",
                                f"{round(base_press * 0.65 * load_mod, 1)} kg",
                                "80-95% HRMax"
                                if w_num != 4
                                else "60-70% HRMax",
                            ],
                            "Rest Interval": [
                                "30s",
                                "90s",
                                "90s",
                                "120s",
                                "90s",
                                "60s",
                                "45-60s",
                            ],
                        }
                    )

                    st.table(m_df)

            st.markdown(
                rf"""
            <div class='scientific-note'>
                <b>🧬 Month {m_num} Concurrent Programming Scientific Rationale:</b><br>
                • <b>Agility & COD Integration</b>: Sport-specific acceleration, deceleration, and lateral change-of-direction drills included in every week.<br>
                • <b>Undulating Microcycle Periodization</b>: Microcycles progress weekly from Week 1 (Base Load) $\rightarrow$ Week 2 (Build) $\rightarrow$ Week 3 (Peak Load) $\rightarrow$ Week 4 (Deload).<br>
                • <b>Month-to-Month Exercise Progression</b>: Exercise selections evolve dynamically across macrocycle months to avoid adaptation plateaus.
            </div>
            """,
                unsafe_allow_html=True,
            )
