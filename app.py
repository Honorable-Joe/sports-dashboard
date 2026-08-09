from datetime import datetime
import pandas as pd
import streamlit as st

# ------------------------------------------
# STREAMLIT CONFIGURATION & CUSTOM STYLING
# ------------------------------------------
st.set_page_config(
    page_title="Athlete-IQ Performance Engine", page_icon="⚡", layout="wide"
)

# Custom CSS Styling
st.markdown(
    """
    <style>
    .banner-header {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        border-left: 5px solid #38bdf8;
    }
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .injury-alert {
        background-color: #451a03;
        border-left: 4px solid #f97316;
        color: #ffedd5;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------
# SESSION STATE INITIALIZATION (MOCK DATA)
# ------------------------------------------
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "athlete_name": "Alex Mercer",
        "evaluating_coach": "Coach Marcus",
        "weight_kg": 75.0,
        "sport_type": "Basketball",
        "club_days": 4,
        "club_hours_per_day": 2.0,
        "has_injury": "No",
        "injury_site": "None",
        "max_pushups": 25,
        "cmj_cm": 42.0,
        "sleep_quality": 8,
        "muscle_soreness": 3,
        "stress_level": 3,
    }

# Sidebar Navigation / Controls
st.sidebar.title("⚡ Navigation")
active_module = st.sidebar.radio(
    "Select Module:", ["🚀 7. GENERATE ADAPTIVE PROGRAM & CARD"]
)
plan_months = st.sidebar.slider("Program Duration (Months):", 1, 3, 2)
equipment_selected = st.sidebar.multiselect(
    "Available Equipment:",
    ["Barbells & Plates", "Dumbbells", "Kettlebells", "Landmine Attachment"],
    default=["Barbells & Plates", "Dumbbells"],
)

# ------------------------------------------
# MODULE 7: GENERATE PROGRAM & CARD
# ------------------------------------------
if active_module == "🚀 7. GENERATE ADAPTIVE PROGRAM & CARD":
    st.markdown(
        "<div class='banner-header'>🚀 Dynamic Multi-Month Concurrent Program & Printable Card</div>",
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

    # Frequency Logic
    if tot_club_hrs >= 10:
        rec_days = 2
        freq_label = "2 Days/Week (Dense Full-Body Concurrent)"
    elif tot_club_hrs >= 6:
        rec_days = 3
        freq_label = "3 Days/Week (Concurrent Undulating Split)"
    else:
        rec_days = 4
        freq_label = "4 Days/Week (Upper/Lower Concurrent Split)"

    # Base Load Calculations with Readiness Auto-regulation
    pushups = d["max_pushups"]
    cmj = d.get("cmj_cm", 40.0)
    sleep = d.get("sleep_quality", 8)
    soreness = d.get("muscle_soreness", 3)
    stress = d.get("stress_level", 3)
    readiness = (sleep + (11 - soreness) + (11 - stress)) / 30.0
    readiness_mod = 0.90 if readiness < 0.6 else (1.05 if readiness > 0.85 else 1.00)

    base_press = round(weight * 0.45 * (pushups / 30.0) * readiness_mod, 1)
    base_hinge = round(weight * 0.85 * (cmj / 40.0) * readiness_mod, 1)

    st.markdown(
        f"""
    <div class='metric-card'>
        <h3 style='margin:0; color:#38bdf8;'>👤 Athlete: {name} | ⚽ Sport: {sport} | 🧢 Coach: {coach}</h3>
        <p style='margin:5px 0 0 0; color:#cbd5e1;'>Scope: <b>{plan_months}-Month Macrocycle</b> | Weekly Frequency: <b>{freq_label}</b> | Readiness Mod: <b>{int(readiness_mod*100)}%</b></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if has_injury == "Yes":
        st.markdown(
            f"<div class='injury-alert'>⚠️ <b>CLINICAL INJURY PROTOCOL ACTIVE ({injury_site})</b><br>Substituted high-impact plyometrics with controlled eccentric/isometric progressions.</div>",
            unsafe_allow_html=True,
        )

    # Dynamic Month Progression Logic
    m_tabs = st.tabs([f"🗓️ MONTH {m}" for m in range(1, plan_months + 1)])

    for m_idx, m_tab in enumerate(m_tabs):
        m_num = m_idx + 1
        with m_tab:
            if m_num == 1:
                focus_desc = "Phase 1: Base Work Capacity, Postural Alignment & Movement Quality"
                ex_mob = "3-View Posture Flow (Thoracic Extension & Hip Capsule Priming)"
                ex_pow = (
                    "Rotational Med-Ball Scoop Throws"
                    if sport
                    in [
                        "Tennis",
                        "Volleyball",
                        "Combat Sports (MMA/Boxing)",
                        "Racket Sports (Squash/Padel)",
                    ]
                    else "Non-Countermovement Plyo Box Jump"
                )
                ex_agil = (
                    "T-Drill Sharp Deceleration & Agility Ladder Quick-Feet"
                )
                ex_low = (
                    "Barbell Romanian Deadlift (RDL)"
                    if "Barbells & Plates" in equipment_selected
                    else "Dumbbell Single-Leg RDL"
                )
                ex_upp = (
                    "Barbell Strict Overhead Press"
                    if "Barbells & Plates" in equipment_selected
                    else "Half-Kneeling Dumbbell Press"
                )
                ex_pull = "Single-Arm Cable Row with Thoracic Rotation"
                ex_esd = "AirBike Extensive Interval Repeats"
                tempo_str = "3-1-1-0 (Eccentric Control)"
            elif m_num == 2:
                focus_desc = "Phase 2: Dynamic Force Production, Kinetic Chain Power & COD Velocity"
                ex_mob = (
                    "Multi-Planar Lunge with Thoracic-Hip Dissociation Reach"
                )
                ex_pow = (
                    "Rotational Landmine Explosive Punches"
                    if "Landmine Attachment" in equipment_selected
                    else "Med-Ball Overhead Stepping Slam"
                )
                ex_agil = "Pro Agility (5-10-5) Shuttle & Reactive Cone Cutting"
                ex_low = (
                    "Barbell Front Squat / Trap Bar Deadlift"
                    if "Barbells & Plates" in equipment_selected
                    else "Heavy Dumbbell Bulgarian Split Squat"
                )
                ex_upp = "Landmine Rotational Press / Push Press"
                ex_pull = "Chest-Supported T-Bar / TRX Suspended Row"
                ex_esd = "High-Intensity Shuttle Sprints (Lactate Buffer)"
                tempo_str = "2-0-1-0 (Force Escalation)"
            else:
                focus_desc = "Phase 3: Rate of Force Development (RFD), Speed-Power Peak & Reactive Agility"
                ex_mob = "Dynamic Elastic Priming & Ankling Pre-Activation Drops"
                ex_pow = (
                    "French Contrast Jumps / Dynamic Med-Ball Launch Drops"
                )
                ex_agil = "Reactive Light/Visual Trigger Sprints & Change-of-Direction Cuts"
                ex_low = "Barbell Snatch-Grip High Pull / Dynamic Contrast Trap Bar Jumps"
                ex_upp = "Explosive Banded Push Press / Plyometric Push-Ups"
                ex_pull = "Weighted Pull-Ups / Explosive High Cable Rows"
                ex_esd = "Tabata AirBike Sprint Repeats"
                tempo_str = "1-0-X-0 (Max Intent / Velocity)"

            st.subheader(f"📌 Month {m_num}: {focus_desc}")

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
                        sets_reps = "2 x 8 Reps (Reduced Volume)"
                        load_mod = 0.70

                    st.markdown(f"#### 🗓️ {w_label}")

                    m_df = pd.DataFrame(
                        {
                            "Fitness Component": [
                                "1. Mobility & Posture Priming",
                                "2. Explosive Power",
                                "3. Agility & Change of Direction (COD)",
                                "4. Lower Body Strength (Hinge/Squat)",
                                "5. Upper Body Press",
                                "6. Unilateral Pull & Core",
                                "7. Energy Systems (ESD)",
                            ],
                            "Prescribed Exercise": [
                                ex_mob,
                                ex_pow,
                                ex_agil,
                                ex_low,
                                ex_upp,
                                ex_pull,
                                ex_esd,
                            ],
                            "Tempo": [
                                "2-1-2-0",
                                "Explosive",
                                "Max Speed",
                                tempo_str,
                                tempo_str,
                                "2-0-1-1",
                                "Interval",
                            ],
                            "Sets x Reps": [
                                "2 x 8 /side",
                                "4 x 4",
                                "4 x 3 /side",
                                sets_reps,
                                sets_reps,
                                sets_reps,
                                "12-18 Mins",
                            ],
                            "Prescribed Load": [
                                "Bodyweight",
                                "Max Speed Intent",
                                "Cones / High Speed",
                                f"{round(base_hinge * load_mod, 1)} kg",
                                f"{round(base_press * load_mod, 1)} kg",
                                f"{round(base_press * 0.65 * load_mod, 1)} kg",
                                "80-95% HRMax",
                            ],
                            "Coaching Cue": [
                                "Drive big toe into floor; open thoracic spine.",
                                "Explode violently; full triple extension at hips.",
                                "Drop center of mass prior to plant foot cut.",
                                "Hinge at hips; keep spine braced & rigid.",
                                "Pack shoulders; drive vertically overhead.",
                                "Squeeze scapula for 1 sec at peak contraction.",
                                "Maintain cadence; push through anaerobic threshold.",
                            ],
                        }
                    )

                    st.table(m_df)

    # --- PRINTABLE GYM FLOOR WORKOUT CARD GENERATOR ---
    st.markdown("---")
    st.subheader("📋 Printable Gym Floor Workout Card")
    st.caption(
        "Generate a clean summary block to copy/print for clipboard use on the weight room floor."
    )

    with st.expander("📄 Click to View / Print Floor Card"):
        card_content = f"""================================================================================
⚡ ATHLETE-IQ PERFORMANCE ENGINE - GYM FLOOR CARD
================================================================================
ATHLETE  : {name:<25} SPORT  : {sport}
COACH    : {coach:<25} DATE   : {datetime.now().strftime('%Y-%m-%d')}
SCOPE    : Month 1 - Week 1         FREQUENCY: {freq_label}
--------------------------------------------------------------------------------
[ ] 1. MOBILITY : 3-View Posture Priming Flow       | 2 Sets x 8 Reps  | BW
[ ] 2. POWER    : Rotational Med-Ball Throws        | 4 Sets x 4 Reps  | MAX INTENT
[ ] 3. AGILITY  : T-Drill Deceleration & Ladder     | 4 Sets x 3 Reps  | MAX SPEED
[ ] 4. STRENGTH : Barbell / DB Romanian Deadlift    | 3 Sets x 10 Reps | {round(base_hinge*0.85, 1)} kg
[ ] 5. PRESS    : Overhead Strict / DB Press        | 3 Sets x 10 Reps | {round(base_press*0.85, 1)} kg
[ ] 6. PULL     : Single-Arm Cable / TRX Row        | 3 Sets x 10 Reps | {round(base_press*0.55, 1)} kg
[ ] 7. ESD      : High-Intensity Shuttle Sprints     | 12 Mins          | 85-90% HR
================================================================================
COACH NOTES: Maintain strict posture bracing on all compound hinge movements.
================================================================================"""
        st.code(card_content, language="text")
