import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import sqlite3
from datetime import datetime

# ==========================================
# 0. DATABASE & STATE INITIALIZATION
# ==========================================
DB_FILE = "athlete_performance.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    age INTEGER,
                    gender TEXT,
                    height REAL,
                    weight REAL,
                    sport TEXT,
                    evaluator TEXT,
                    phase TEXT,
                    data_json TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS assessment_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    athlete_name TEXT,
                    assessment_date TEXT,
                    data_json TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# Page Setup
st.set_page_config(
    page_title="Performance & Conditioning Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom HUD Styling
st.markdown("""
<style>
    .main { background-color: #0b0f19; color: #e2e8f0; }
    .stApp { background-color: #0b0f19; }
    .hud-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .hud-metric-title { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
    .hud-metric-value { font-size: 1.8rem; font-weight: 700; color: #38bdf8; margin-top: 5px; }
    .hud-metric-sub { font-size: 0.8rem; color: #64748b; margin-top: 2px; }
    .alert-box {
        background-color: #450a0a; border: 1px solid #991b1b;
        color: #fca5a5; padding: 12px; border-radius: 8px; margin-bottom: 15px;
    }
    .success-box {
        background-color: #064e3b; border: 1px solid #065f46;
        color: #a7f3d0; padding: 12px; border-radius: 8px; margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'athlete_data' not in st.session_state:
    st.session_state.athlete_data = {
        "name": "Alex Mercer", "age": 22, "gender": "Male", "height": 180.0, "weight": 78.0,
        "sport": "Soccer", "evaluator": "Coach Vance", "phase": "Off-Season", "training_years": 4,
        "club_days": 4, "club_hours": 6.0,
        "injuries": {"Knee": False, "Shoulder": False, "Lumbar": False, "Ankle": False},
        "sfma": {
            "Cervical Spine": "FN", "Upper Extremity Pattern": "FN", "Multi-Segment Flexion": "FN",
            "Multi-Segment Extension": "FN", "Multi-Segment Rotation": "FN", "Single Leg Stance": "FN", "Overhead Squat": "FN"
        },
        "posture": {"Anterior": "Normal", "Posterior": "Normal", "Lateral": "Normal"},
        "rom": {"Ankle Dorsiflexion": 25, "Hip Extension": 15, "Thoracic Extension": 50, "Shoulder Flexion": 180},
        "performance": {
            "medball_forehand": 12.5, "medball_backhand": 11.8, "cmj_height": 42.0,
            "vj_left": 18.0, "vj_right": 20.0, "hj_left": 190.0, "hj_right": 205.0,
            "sprint_5m": 1.12, "sprint_10m": 1.85, "tdrill_time": 9.8, "cooper_dist": 2800,
            "squat_1rm": 140, "bench_1rm": 100, "ohp_1rm": 65, "pushups_max": 45
        }
    }

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("⚡ ATHLETE ENGINE")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate Modules:",
    [
        "1. Demographics & Coach Sign-off",
        "2. Club Load & Multi-Injury Diagnostics",
        "3. SFMA, Anatomical Views & ROM Matrix",
        "4. Sport-Specific Assessment & 1RM Suite",
        "5. Saved Records & Historical Progress",
        "6. ADAPTIVE PROGRAM GENERATOR"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Powered by NASM OPT, OPEX & Science for Sport Frameworks")

# ==========================================
# PAGE 1: DEMOGRAPHICS & COACH SIGN-OFF
# ==========================================
if page == "1. Demographics & Coach Sign-off":
    st.title("📋 Demographics & Assessment Sign-off")
    st.markdown("Database Profile Management and Core Demographic Logging.")
    
    col_db1, col_db2, col_db3 = st.columns(3)
    with col_db1:
        profile_action = st.selectbox("Database Action", ["Load Existing Profile", "Create New Profile"])
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name FROM profiles")
    existing_profiles = [r[0] for r in c.fetchall()]
    conn.close()

    if profile_action == "Load Existing Profile" and existing_profiles:
        selected_prof = st.selectbox("Select Profile", existing_profiles)
        if st.button("Load Profile"):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT data_json FROM profiles WHERE name=?", (selected_prof,))
            row = c.fetchone()
            conn.close()
            if row:
                st.session_state.athlete_data = json.loads(row[0])
                st.success(f"Profile '{selected_prof}' loaded successfully!")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Athlete Profile")
        st.session_state.athlete_data["name"] = st.text_input("Athlete Name", st.session_state.athlete_data["name"])
        st.session_state.athlete_data["age"] = st.number_input("Age", 10, 80, int(st.session_state.athlete_data["age"]))
        st.session_state.athlete_data["gender"] = st.selectbox("Gender", ["Male", "Female", "Other"], index=0 if st.session_state.athlete_data["gender"]=="Male" else 1)
        st.session_state.athlete_data["height"] = st.number_input("Height (cm)", 100.0, 230.0, float(st.session_state.athlete_data["height"]))
        st.session_state.athlete_data["weight"] = st.number_input("Weight (kg)", 30.0, 200.0, float(st.session_state.athlete_data["weight"]))
        st.session_state.athlete_data["sport"] = st.selectbox("Sport Specialty", ["Soccer", "Basketball", "Tennis / Racket", "Track & Field", "General Fitness"], index=0)

    with c2:
        st.subheader("Coach Metadata")
        st.session_state.athlete_data["evaluator"] = st.text_input("Evaluator / Coach", st.session_state.athlete_data["evaluator"])
        st.session_state.athlete_data["phase"] = st.selectbox("Season Phase", ["Off-Season", "Pre-Season", "In-Season", "Rehab / Transition"], index=0)
        st.session_state.athlete_data["training_years"] = st.number_input("Training Experience (Years)", 0, 30, int(st.session_state.athlete_data["training_years"]))

    if st.button("💾 Save Profile Snapshot to Local DB"):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""INSERT OR REPLACE INTO profiles (name, age, gender, height, weight, sport, evaluator, phase, data_json)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (st.session_state.athlete_data["name"], st.session_state.athlete_data["age"], st.session_state.athlete_data["gender"],
                   st.session_state.athlete_data["height"], st.session_state.athlete_data["weight"], st.session_state.athlete_data["sport"],
                   st.session_state.athlete_data["evaluator"], st.session_state.athlete_data["phase"],
                   json.dumps(st.session_state.athlete_data)))
        conn.commit()
        conn.close()
        st.success(f"Snapshot for {st.session_state.athlete_data['name']} saved to SQLite DB.")

# ==========================================
# PAGE 2: CLUB LOAD & MULTI-INJURY DIAGNOSTICS
# ==========================================
elif page == "2. Club Load & Multi-Injury Diagnostics":
    st.title("⚽ Club Load & Multi-Injury Diagnostics")
    st.markdown("External Exposure Tracking & Injury-Triggered Auto-Regressions.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("External Exposure & Load")
        st.session_state.athlete_data["club_days"] = st.slider("Club Training Days / Week", 0, 7, int(st.session_state.athlete_data["club_days"]))
        st.session_state.athlete_data["club_hours"] = st.number_input("Weekly External Exposure (Hours)", 0.0, 30.0, float(st.session_state.athlete_data["club_hours"]))
        
        tot_vol = st.session_state.athlete_data["club_hours"]
        if tot_vol > 12.0:
            st.warning("⚠️ High External Volume Detected: Engine will limit S&C frequency to 2 sessions/week to prevent overtraining.")
        else:
            st.info("✅ Moderate External Volume: Standard 3-4 session S&C split permitted.")

    with c2:
        st.subheader("Multi-Injury Diagnostic Inputs")
        st.markdown("Select active pain/pathology sites to enforce exercise regressions:")
        injuries = st.session_state.athlete_data["injuries"]
        injuries["Knee"] = st.checkbox("Knee Pain / Patellar Tendinopathy", value=injuries.get("Knee", False))
        injuries["Shoulder"] = st.checkbox("Shoulder Impingement / AC Joint", value=injuries.get("Shoulder", False))
        injuries["Lumbar"] = st.checkbox("Lumbar Spine / Lower Back Strain", value=injuries.get("Lumbar", False))
        injuries["Ankle"] = st.checkbox("Ankle Instability / Achilles Tendinitis", value=injuries.get("Ankle", False))
        st.session_state.athlete_data["injuries"] = injuries

# ==========================================
# PAGE 3: SFMA, ANATOMICAL VIEWS & ROM MATRIX
# ==========================================
elif page == "3. SFMA, Anatomical Views & ROM Matrix":
    st.title("🩺 Movement Screening, Posture & Goniometry")
    st.markdown("Selective Functional Movement Assessment (SFMA), Static Posture, & ROM Matrix.")

    t1, t2, t3 = st.tabs(["SFMA Screening", "Static Posture", "Goniometry ROM Matrix"])

    with t1:
        st.subheader("SFMA 7 Core Movement Assessment")
        sfma_opts = ["FN", "DN", "DP"]
        sfma_desc = {"FN": "Functional Non-Painful", "DN": "Dysfunctional Non-Painful", "DP": "Dysfunctional Painful"}
        
        sfma = st.session_state.athlete_data["sfma"]
        for key in sfma.keys():
            sfma[key] = st.selectbox(f"{key}", sfma_opts, index=sfma_opts.index(sfma.get(key, "FN")),
                                     format_func=lambda x: f"{x} - {sfma_desc[x]}")
        st.session_state.athlete_data["sfma"] = sfma

    with t2:
        st.subheader("3-View Static Posture Evaluation")
        posture = st.session_state.athlete_data["posture"]
        posture["Anterior"] = st.selectbox("Anterior View", ["Normal", "Pes Planus (Flat Feet)", "Genu Valgum (Knock Knees)", "Genu Varum (Bow Legs)"])
        posture["Posterior"] = st.selectbox("Posterior View", ["Normal", "Scapular Winging", "Asymmetric Pelvic Height"])
        posture["Lateral"] = st.selectbox("Lateral View", ["Normal", "Anterior Pelvic Tilt", "Excessive Thoracic Kyphosis", "Forward Head Posture"])
        st.session_state.athlete_data["posture"] = posture

    with t3:
        st.subheader("Goniometric Range of Motion (Degrees)")
        rom = st.session_state.athlete_data["rom"]
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            rom["Ankle Dorsiflexion"] = st.number_input("Ankle Dorsiflexion (Norm: 20°)", 0, 50, int(rom.get("Ankle Dorsiflexion", 25)))
            rom["Hip Extension"] = st.number_input("Hip Extension (Norm: 15-20°)", -10, 45, int(rom.get("Hip Extension", 15)))
        with col_r2:
            rom["Thoracic Extension"] = st.number_input("Thoracic Extension (Norm: 45°)", 0, 90, int(rom.get("Thoracic Extension", 50)))
            rom["Shoulder Flexion"] = st.number_input("Shoulder Flexion (Norm: 180°)", 0, 200, int(rom.get("Shoulder Flexion", 180)))
        st.session_state.athlete_data["rom"] = rom

# ==========================================
# PAGE 4: SPORT-SPECIFIC ASSESSMENT & 1RM SUITE
# ==========================================
elif page == "4. Sport-Specific Assessment & 1RM Suite":
    st.title("💥 Performance Diagnostics & 1RM Suite")
    st.markdown("Explosive Power, Speed, Agility, Aerobic Capacity & Maximal Strength Metrics.")

    perf = st.session_state.athlete_data["performance"]

    t1, t2, t3 = st.tabs(["Speed & Power", "Cardiovascular / MAS", "1RM & Muscular Strength"])

    with t1:
        st.subheader("Racket & Jump Metrics")
        c1, c2 = st.columns(2)
        with c1:
            perf["medball_forehand"] = st.number_input("Medball Forehand Throw (m)", 0.0, 40.0, float(perf.get("medball_forehand", 12.5)))
            perf["medball_backhand"] = st.number_input("Medball Backhand Throw (m)", 0.0, 40.0, float(perf.get("medball_backhand", 11.8)))
            perf["cmj_height"] = st.number_input("Countermovement Jump Height (cm)", 0.0, 100.0, float(perf.get("cmj_height", 42.0)))
        with c2:
            perf["vj_left"] = st.number_input("Unilateral Vertical Jump - Left (cm)", 0.0, 60.0, float(perf.get("vj_left", 18.0)))
            perf["vj_right"] = st.number_input("Unilateral Vertical Jump - Right (cm)", 0.0, 60.0, float(perf.get("vj_right", 20.0)))
            perf["hj_left"] = st.number_input("Horizontal Jump - Left (cm)", 0.0, 350.0, float(perf.get("hj_left", 190.0)))
            perf["hj_right"] = st.number_input("Horizontal Jump - Right (cm)", 0.0, 350.0, float(perf.get("hj_right", 205.0)))

        st.subheader("Sprint & Agility Times")
        c3, c4 = st.columns(2)
        with c3:
            perf["sprint_5m"] = st.number_input("5m Acceleration Sprint (s)", 0.5, 3.0, float(perf.get("sprint_5m", 1.12)))
            perf["sprint_10m"] = st.number_input("10m Sprint (s)", 1.0, 5.0, float(perf.get("sprint_10m", 1.85)))
        with c4:
            perf["tdrill_time"] = st.number_input("T-Drill Agility Time (s)", 5.0, 25.0, float(perf.get("tdrill_time", 9.8)))

    with t2:
        st.subheader("Aerobic & Maximal Aerobic Speed (MAS)")
        perf["cooper_dist"] = st.number_input("12-Min Cooper Test Distance (meters)", 500, 5000, int(perf.get("cooper_dist", 2800)))
        
        # MAS Calculation: (Distance - 504) / 45 / 3.6 -> m/s
        mas = round((perf["cooper_dist"] - 504) / 720.0, 2)
        vo2 = round((perf["cooper_dist"] - 504.9) / 44.73, 1)
        st.info(f"📊 Calculated VO2Max: **{vo2} mL/kg/min** | Maximal Aerobic Speed (MAS): **{mas} m/s**")

    with t3:
        st.subheader("1RM Lifts & Muscular Endurance")
        c1, c2 = st.columns(2)
        with c1:
            perf["squat_1rm"] = st.number_input("Back Squat 1RM (kg)", 0, 400, int(perf.get("squat_1rm", 140)))
            perf["bench_1rm"] = st.number_input("Bench Press 1RM (kg)", 0, 300, int(perf.get("bench_1rm", 100)))
        with c2:
            perf["ohp_1rm"] = st.number_input("Overhead Press 1RM (kg)", 0, 200, int(perf.get("ohp_1rm", 65)))
            perf["pushups_max"] = st.number_input("Max Push-ups (reps)", 0, 150, int(perf.get("pushups_max", 45)))

    st.session_state.athlete_data["performance"] = perf

# ==========================================
# PAGE 5: SAVED RECORDS & HISTORICAL PROGRESS
# ==========================================
elif page == "5. Saved Records & Historical Progress":
    st.title("📈 Historical Progress & Longitudinal Tracking")
    st.markdown("Track performance adaptations and assessment snapshots over time.")

    if st.button("📌 Log Current Snapshot to History"):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute("INSERT INTO assessment_history (athlete_name, assessment_date, data_json) VALUES (?, ?, ?)",
                  (st.session_state.athlete_data["name"], now_str, json.dumps(st.session_state.athlete_data)))
        conn.commit()
        conn.close()
        st.success(f"Snapshot logged for {st.session_state.athlete_data['name']} at {now_str}")

    conn = sqlite3.connect(DB_FILE)
    df_hist = pd.read_sql_query("SELECT * FROM assessment_history WHERE athlete_name=?", conn, params=(st.session_state.athlete_data["name"],))
    conn.close()

    if not df_hist.empty:
        st.subheader("Logged History Snapshots")
        st.dataframe(df_hist[["id", "assessment_date", "athlete_name"]])
    else:
        st.info("No historical snapshots logged for this athlete yet.")

# ==========================================
# PAGE 6: ADAPTIVE PROGRAM GENERATOR
# ==========================================
elif page == "6. ADAPTIVE PROGRAM GENERATOR":
    st.title("🚀 Adaptive Program Generator & HUD")
    st.markdown("Integrated NASM OPT Periodization, SFMA/Injury Safety Rules, OPEX Tempo Tags & Animal Flow Ground Mobility.")

    data = st.session_state.athlete_data
    perf = data["performance"]
    injuries = data["injuries"]
    rom = data["rom"]

    # Calculate HUD Metrics
    vj_asym = round(abs(perf["vj_left"] - perf["vj_right"]) / max(perf["vj_left"], perf["vj_right"], 1) * 100, 1)
    hj_asym = round(abs(perf["hj_left"] - perf["hj_right"]) / max(perf["hj_left"], perf["hj_right"], 1) * 100, 1)
    mas_val = round((perf["cooper_dist"] - 504) / 720.0, 2)
    
    # 1. Performance HUD Row
    st.subheader("📊 Performance HUD Status")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="hud-card">
            <div class="hud-metric-title">Force-Velocity Profile</div>
            <div class="hud-metric-value">{"Velocity-Dominant" if perf["cmj_height"] > 40 else "Force-Deficient"}</div>
            <div class="hud-metric-sub">CMJ: {perf["cmj_height"]} cm</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="hud-card">
            <div class="hud-metric-title">Max Aerobic Speed</div>
            <div class="hud-metric-value">{mas_val} m/s</div>
            <div class="hud-metric-sub">Cooper: {perf["cooper_dist"]} m</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="hud-card">
            <div class="hud-metric-title">Limb Asymmetry</div>
            <div class="hud-metric-value">{hj_asym}%</div>
            <div class="hud-metric-sub">HJ Left: {perf["hj_left"]} | Right: {perf["hj_right"]}</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="hud-card">
            <div class="hud-metric-title">Weekly S&C Target</div>
            <div class="hud-metric-value">{"2 Sessions" if data["club_hours"] > 12 else "3 Sessions"}</div>
            <div class="hud-metric-sub">Club Volume: {data["club_hours"]} hrs/wk</div>
        </div>""", unsafe_allow_html=True)

    # 2. Safety Alerts
    if hj_asym > 10 or vj_asym > 10:
        st.markdown(f"""<div class="alert-box">
            ⚠️ <b>High Asymmetry Detected ({max(hj_asym, vj_asym)}%):</b> Unilateral plyometric & strength progressions enforced to restore balance.
        </div>""", unsafe_allow_html=True)
    
    active_injuries = [k for k, v in injuries.items() if v]
    if active_injuries:
        st.markdown(f"""<div class="alert-box">
            🩹 <b>Active Clinical Regressions Enforced For:</b> {', '.join(active_injuries)}
        </div>""", unsafe_allow_html=True)

    # 3. Dynamic Workout Prescription Engine
    st.subheader("🏋️ Prescribed Workout Plan")
    
    selected_opt = st.selectbox("Select NASM OPT Phase Target", [
        "Phase 1: Stabilization Endurance",
        "Phase 2: Strength Endurance",
        "Phase 3: Hypertrophy / Development",
        "Phase 4: Maximal Strength",
        "Phase 5: Power / Explosiveness"
    ])

    # Dynamic Exercise Rule System
    squat_exercise = "Barbell Back Squat"
    ohp_exercise = "Barbell Overhead Press"
    plyo_exercise = "Depth Rebound Jumps (Fast Plyo, GCT < 250ms)"
    warmup_flow = "Dynamic Arm Swings & Leg Swings"

    if injuries["Knee"]:
        squat_exercise = "Box Squat to Parallel / Sled Drag"
        plyo_exercise = "Submaximal Ankle Pogos (Low Impact)"
    if injuries["Shoulder"]:
        ohp_exercise = "Landmine Press / Neutral Grip DB Press"
    if rom["Ankle Dorsiflexion"] < 20:
        warmup_flow += " + Ankle Mobility & Animal Flow Beast Reach"
    if rom["Thoracic Extension"] < 45:
        warmup_flow += " + T-Spine Foam Roll & Crab Reach"

    # Define Workout Tabs
    w_tab1, w_tab2, w_tab3 = st.tabs(["Day 1: Lower / Power", "Day 2: Upper / Strength", "Day 3: Conditioning & MAS"])

    with w_tab1:
        st.markdown("### 🦵 Lower Body & Ground Power Block")
        st.write(f"**Dynamic Warm-Up & Mobility:** {warmup_flow}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div class="hud-card">
                <h4>Primary Lower Lift</h4>
                <p><b>Exercise:</b> {squat_exercise}</p>
                <p><b>Prescription:</b> 4 Sets x 5 Reps @ 82% 1RM</p>
                <p><b>OPEX Tempo:</b> <code>3-1-1-0</code> (3s Eccentric, 1s Pause, Fast Concentric)</p>
                <p><b>Rest:</b> 180 seconds</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="hud-card">
                <h4>Plyometric Power Block</h4>
                <p><b>Exercise:</b> {plyo_exercise}</p>
                <p><b>Prescription:</b> 3 Sets x 5 Contacts</p>
                <p><b>OPEX Tempo:</b> <code>X-X-X-X</code> (Max Explosive Rebound)</p>
                <p><b>Rest:</b> 120 seconds</p>
            </div>""", unsafe_allow_html=True)

    with w_tab2:
        st.markdown("### 🏋️ Upper Body & Rotational Power Block")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div class="hud-card">
                <h4>Primary Press</h4>
                <p><b>Exercise:</b> {ohp_exercise}</p>
                <p><b>Prescription:</b> 4 Sets x 6 Reps @ 78% 1RM</p>
                <p><b>OPEX Tempo:</b> <code>2-1-1-0</code></p>
                <p><b>Rest:</b> 120 seconds</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="hud-card">
                <h4>Rotational Power (Sport-Specific)</h4>
                <p><b>Exercise:</b> Medball Rotational Scoop Throws</p>
                <p><b>Prescription:</b> 3 Sets x 6 Reps / Side</p>
                <p><b>OPEX Tempo:</b> <code>1-0-X-0</code></p>
                <p><b>Rest:</b> 90 seconds</p>
            </div>""", unsafe_allow_html=True)

    with w_tab3:
        st.markdown("### 🏃 Aerobic Conditioning & Energy System Development")
        work_pace = round(mas_val * 1.05, 2)
        rec_pace = round(mas_val * 0.70, 2)
        st.markdown(f"""<div class="hud-card">
            <h4>Maximal Aerobic Speed (MAS) Intervals</h4>
            <p><b>Protocol:</b> 15s / 15s HIIT Intervals x 12 Reps (2 Sets)</p>
            <p><b>Target Work Speed (105% MAS):</b> {work_pace} m/s ({round(work_pace * 3.6, 1)} km/h)</p>
            <p><b>Active Recovery Speed (70% MAS):</b> {rec_pace} m/s ({round(rec_pace * 3.6, 1)} km/h)</p>
            <p><b>Set Rest:</b> 3 minutes</p>
        </div>""", unsafe_allow_html=True)
