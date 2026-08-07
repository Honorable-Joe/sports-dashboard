import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ATHLETE-IQ Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DEVELOPER & STAFF BRANDING ---
DEVELOPER_NAME = "Coach / Ahmed Youssef"

# --- ENERGETIC RGB & GLASSMORPHISM THEME ---
custom_theme = """
<style>
.stApp {
    background: linear-gradient(rgba(10, 12, 18, 0.88), rgba(10, 12, 18, 0.94)), 
                url('https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=1920&q=80');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

h1 {
    color: #ffffff !important;
    text-shadow: 0 0 15px rgba(0, 210, 255, 0.6), 0 0 30px rgba(0, 210, 255, 0.2);
    font-weight: 800 !important;
}

h2, h3 {
    color: #e0e6ed !important;
    text-shadow: 0 0 10px rgba(255, 0, 128, 0.4);
}

div[data-testid="stMetric"] {
    background: rgba(18, 22, 32, 0.85) !important;
    border: 1px solid rgba(0, 210, 255, 0.35) !important;
    border-radius: 14px 14px 0px 0px !important;
    padding: 16px !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: 0 0 20px rgba(0, 210, 255, 0.15) !important;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #ff007f, #7f00ff, #00d2ff) !important;
    border-radius: 10px !important;
}

.rating-badge {
    background: rgba(10, 14, 23, 0.9) !important;
    border: 1px solid rgba(255, 0, 128, 0.4) !important;
    border-radius: 0px 0px 14px 14px !important;
    padding: 8px 12px !important;
    margin-top: -15px !important;
    margin-bottom: 15px !important;
    text-align: center !important;
    font-size: 0.88rem !important;
    color: #00d2ff !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5) !important;
}

section[data-testid="stSidebar"] {
    background-color: rgba(12, 15, 23, 0.92) !important;
    border-right: 1px solid rgba(255, 0, 128, 0.3) !important;
    backdrop-filter: blur(10px) !important;
}

.stButton > button {
    background: linear-gradient(45deg, #ff007f, #7f00ff, #00d2ff) !important;
    background-size: 200% 200% !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    box-shadow: 0 0 20px rgba(255, 0, 128, 0.4) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: scale(1.03) !important;
    box-shadow: 0 0 30px rgba(0, 210, 255, 0.8) !important;
}

hr {
    border-color: rgba(0, 210, 255, 0.2) !important;
}
</style>
"""
st.markdown(custom_theme, unsafe_allow_html=True)

# --- SCIENTIFIC 1-10 RATING ENGINE ---
def calculate_ratings(rsr, dsd, mobility, fatigue):
    score_rsr = max(1.0, min(10.0, 1.0 + ((rsr - 0.8) / 1.7) * 9.0))
    score_dsd = max(1.0, 10.0 - (abs(dsd - 0.70) / 0.25) * 9.0)
    score_mobility = max(1.0, min(10.0, 1.0 + ((mobility - 4.0) / 11.0) * 9.0))
    score_fatigue = max(1.0, min(10.0, 10.0 - ((fatigue - 2.0) / 13.0) * 9.0))
    
    overall_iq = (score_rsr * 0.30) + (score_dsd * 0.30) + (score_mobility * 0.20) + (score_fatigue * 0.20)
    
    return {
        "rsr": round(score_rsr, 1),
        "dsd": round(score_dsd, 1),
        "mobility": round(score_mobility, 1),
        "fatigue": round(score_fatigue, 1),
        "overall": round(overall_iq, 1)
    }

def render_stars(score):
    filled = int(round(score))
    return "★" * filled + "☆" * (10 - filled)

# --- INITIALIZE DATABASE / SESSION STATE ---
if "history" not in st.session_state:
    base_date = datetime.today()
    st.session_state.history = pd.DataFrame([
        {
            "Date": (base_date - timedelta(days=60)).strftime("%Y-%m-%d"),
            "Coach": DEVELOPER_NAME,
            "Player": "Marcus Vance",
            "Weight": 78.0,
            "1RM": 110.0,
            "RSR": 1.41,
            "CMJ": 1600,
            "IMTP": 3000,
            "DSD": 0.53,
            "Mobility": 8.0,
            "Fatigue": 10.5,
            "Pain_VAS": 0
        },
        {
            "Date": (base_date - timedelta(days=30)).strftime("%Y-%m-%d"),
            "Coach": DEVELOPER_NAME,
            "Player": "Marcus Vance",
            "Weight": 77.5,
            "1RM": 125.0,
            "RSR": 1.61,
            "CMJ": 1800,
            "IMTP": 3150,
            "DSD": 0.57,
            "Mobility": 10.0,
            "Fatigue": 8.2,
            "Pain_VAS": 1
        },
        {
            "Date": (base_date - timedelta(days=30)).strftime("%Y-%m-%d"),
            "Coach": "Coach Sarah",
            "Player": "Jordan Lee",
            "Weight": 68.0,
            "1RM": 130.0,
            "RSR": 1.91,
            "CMJ": 2100,
            "IMTP": 2900,
            "DSD": 0.72,
            "Mobility": 12.0,
            "Fatigue": 4.1,
            "Pain_VAS": 0
        }
    ])

# --- NAVIGATION SIDEBAR ---
st.sidebar.title("🧠 Navigation")
app_mode = st.sidebar.radio("Select View", ["1. Live Assessment Dashboard", "2. 1-Month Plan Generator"])

st.sidebar.divider()
st.sidebar.header("📋 Staff & Athlete Selection")
selected_coach = st.sidebar.text_input("Coach Name", value=DEVELOPER_NAME)

# Get list of unique players from history + option to add new
existing_players = list(st.session_state.history["Player"].unique())
selected_player = st.sidebar.selectbox("Select Active Player", options=existing_players + ["+ Add New Athlete"])

if selected_player == "+ Add New Athlete":
    selected_player = st.sidebar.text_input("Enter New Athlete Name", value="New Athlete")

st.sidebar.divider()

# Dark Plotly Layout Configuration
dark_layout = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#E0E6ED'),
    xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
)

# ==========================================
# PAGE 1: LIVE ASSESSMENT DASHBOARD
# ==========================================
if app_mode == "1. Live Assessment Dashboard":
    st.title("🧠 ATHLETE-IQ Assessment Engine")
    st.caption(f"⚡ Lead Architect: **{DEVELOPER_NAME}** | Active Coach: **{selected_coach}** | Athlete: **{selected_player}**")

    st.sidebar.header("Testing Inputs")
    test_date = st.sidebar.date_input("Assessment Date", datetime.today())
    body_weight = st.sidebar.number_input("Body Weight (kg)", min_value=40.0, max_value=150.0, value=75.0, step=0.5)

    st.sidebar.subheader("Mobility Screening")
    ankle_dorsiflexion = st.sidebar.number_input("Ankle Dorsiflexion (cm)", min_value=0.0, max_value=25.0, value=10.0)
    pain_vas = st.sidebar.slider("Current Pain VAS (0–10)", min_value=0, max_value=10, value=0)

    st.sidebar.subheader("Force & Power Diagnostics")
    cmj_force = st.sidebar.number_input("CMJ Peak Force (N)", min_value=500, max_value=6000, value=1850)
    imtp_force = st.sidebar.number_input("IMTP Peak Force (N)", min_value=1000, max_value=8000, value=3200)

    st.sidebar.subheader("Strength & Conditioning")
    one_rm_squat = st.sidebar.number_input("Estimated 1RM Squat/Trap Bar (kg)", min_value=0.0, max_value=400.0, value=125.0)
    best_sprint = st.sidebar.number_input("Best 30m Sprint Time (s)", min_value=3.0, max_value=10.0, value=4.20)
    worst_sprint = st.sidebar.number_input("Worst 30m Sprint Time (s)", min_value=3.0, max_value=10.0, value=4.51)

    # Core Calculations
    rsr = one_rm_squat / body_weight
    dsd = cmj_force / imtp_force if imtp_force > 0 else 0
    fatigue_index = ((worst_sprint - best_sprint) / best_sprint) * 100 if best_sprint > 0 else 0

    ratings = calculate_ratings(rsr, dsd, ankle_dorsiflexion, fatigue_index)

    # Save Session Action
    if st.sidebar.button("💾 Save Assessment to History"):
        new_entry = pd.DataFrame([{
            "Date": test_date.strftime("%Y-%m-%d"),
            "Coach": selected_coach,
            "Player": selected_player,
            "Weight": body_weight,
            "1RM": one_rm_squat,
            "RSR": round(rsr, 2),
            "CMJ": cmj_force,
            "IMTP": imtp_force,
            "DSD": round(dsd, 2),
            "Mobility": ankle_dorsiflexion,
            "Fatigue": round(fatigue_index, 1),
            "Pain_VAS": pain_vas
        }])
        st.session_state.history = pd.concat([st.session_state.history, new_entry], ignore_index=True)
        st.sidebar.success(f"Saved entry for {selected_player}!")

    st.divider()

    # CORE METRICS WITH 1-10 SUB-RATINGS
    st.header(f"1. Performance Metrics: {selected_player}")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric("Relative Strength", f"{rsr:.2f} x BW", delta="Target ≥ 2.0x")
        st.progress(ratings['rsr'] / 10.0)
        st.markdown(f"""
        <div class="rating-badge">
            <b>RATING: {ratings['rsr']} / 10</b><br>
            <span style="color:#ff007f;">{render_stars(ratings['rsr'])}</span>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.metric("Dynamic Strength Deficit", f"{dsd:.2f}", delta="Velocity-Deficient" if dsd > 0.80 else ("Strength-Deficient" if dsd < 0.60 else "Balanced"))
        st.progress(ratings['dsd'] / 10.0)
        st.markdown(f"""
        <div class="rating-badge">
            <b>RATING: {ratings['dsd']} / 10</b><br>
            <span style="color:#ff007f;">{render_stars(ratings['dsd'])}</span>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.metric("Ankle Mobility", f"{ankle_dorsiflexion} cm", delta="Restricted" if ankle_dorsiflexion < 10.0 else "Passed ✅")
        st.progress(ratings['mobility'] / 10.0)
        st.markdown(f"""
        <div class="rating-badge">
            <b>RATING: {ratings['mobility']} / 10</b><br>
            <span style="color:#ff007f;">{render_stars(ratings['mobility'])}</span>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        st.metric("Fatigue Index", f"{fatigue_index:.1f}%", delta="- High Fatigue" if fatigue_index > 8.0 else "Optimal Buffer", delta_color="inverse")
        st.progress(ratings['fatigue'] / 10.0)
        st.markdown(f"""
        <div class="rating-badge">
            <b>RATING: {ratings['fatigue']} / 10</b><br>
            <span style="color:#ff007f;">{render_stars(ratings['fatigue'])}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # INTERACTIVE PROFILING
    st.header("2. Interactive Profiling")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("⚡ Force-Velocity Curve")
        v_max = 4.2  
        f_zero = imtp_force  
        v_range = np.linspace(0, v_max, 50)
        f_range = f_zero * (1 - v_range / v_max)
        p_range = f_range * v_range  
        est_v_cmj = (1 - (cmj_force / f_zero)) * v_max if f_zero > cmj_force else 1.5

        fig_fv = go.Figure()
        fig_fv.add_trace(go.Scatter(x=v_range, y=f_range, mode='lines', name='Force-Velocity Line', line=dict(color='#00D2FF', width=3)))
        fig_fv.add_trace(go.Scatter(x=v_range, y=p_range, mode='lines', name='Power Curve', line=dict(color='#FF007F', width=3, dash='dash'), yaxis='y2'))
        fig_fv.add_trace(go.Scatter(x=[est_v_cmj], y=[cmj_force], mode='markers+text', name='CMJ Operating Point',
                                    marker=dict(size=14, color='#7F00FF', symbol='diamond'),
                                    text=["Operating Point"], textposition="top center"))

        fig_fv.update_layout(
            **dark_layout,
            xaxis_title="Velocity (m/s)",
            yaxis_title="Force (N)",
            yaxis2=dict(title=dict(text="Power (Watts)", font=dict(color='#FF007F')), overlaying='y', side='right', gridcolor='rgba(0,0,0,0)'),
            legend=dict(x=0.05, y=0.1),
            margin=dict(l=20, r=20, t=30, b=20),
            height=380
        )
        st.plotly_chart(fig_fv, use_container_width=True)

    with col_right:
        st.subheader("🎯 1–10 Radar Profile")
        categories = ['Relative Strength', 'Explosive Power', 'Ankle Mobility', 'Repeat Sprint Buffer']
        scores_10 = [ratings['rsr'], ratings['dsd'], ratings['mobility'], ratings['fatigue']]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=scores_10, theta=categories, fill='toself', name='Athlete Score', fillcolor='rgba(0, 210, 255, 0.35)', line=dict(color='#00D2FF', width=2)))
        fig_radar.add_trace(go.Scatterpolar(r=[10, 10, 10, 10], theta=categories, mode='lines', name='Elite Target (10/10)', line=dict(dash='dash', color='#FF007F')))
        
        fig_radar.update_layout(
            **dark_layout,
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[0, 10], gridcolor='rgba(255,255,255,0.1)'),
                angularaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            ),
            showlegend=True,
            margin=dict(l=40, r=40, t=30, b=20),
            height=380
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()

    # LONGITUDINAL PROGRESS TRACKER
    st.header(f"3. Assessment History & Progress: {selected_player}")
    player_history = st.session_state.history[st.session_state.history["Player"] == selected_player].sort_values(by="Date")

    if not player_history.empty:
        st.dataframe(player_history[["Date", "Coach", "Weight", "1RM", "RSR", "DSD", "Mobility", "Fatigue", "Pain_VAS"]], use_container_width=True)
        
        fig_progress = px.line(player_history, x="Date", y=["RSR", "DSD"], markers=True, title=f"Progress Over Time ({selected_player})")
        fig_progress.update_layout(**dark_layout)
        st.plotly_chart(fig_progress, use_container_width=True)
    else:
        st.info("No recorded history for this athlete yet. Complete an assessment and click 'Save Assessment to History'.")


# ==========================================
# PAGE 2: 1-MONTH PLAN GENERATOR
# ==========================================
elif app_mode == "2. 1-Month Plan Generator":
    st.title("🏋️ 1-Month Periodized Plan Generator")
    st.caption(f"⚡ Lead Architect: **{DEVELOPER_NAME}** | Prescribed for Athlete: **{selected_player}**")

    # Get latest athlete stats from history or defaults
    player_history = st.session_state.history[st.session_state.history["Player"] == selected_player].sort_values(by="Date")
    if not player_history.empty:
        latest = player_history.iloc[-1]
        p_rsr, p_dsd, p_mob, p_fatigue = latest["RSR"], latest["DSD"], latest["Mobility"], latest["Fatigue"]
    else:
        p_rsr, p_dsd, p_mob, p_fatigue = 1.6, 0.55, 10.0, 8.5

    ratings = calculate_ratings(p_rsr, p_dsd, p_mob, p_fatigue)

    st.divider()

    # SETUP OPTIONS & INJURY CHECKBOXES
    col_opt1, col_opt2 = st.columns(2)

    with col_opt1:
        st.subheader("1. Training Parameters")
        season_phase = st.selectbox("Season Phase", ["Off-Season Hypertrophy/Strength", "In-Season Maintenance"])
        days_per_week = st.radio("Frequency", ["3 Days / Week", "4 Days / Week"], horizontal=True)
        equip_available = st.checkbox("Barbell & Free Weights Available", value=True)

    with col_opt2:
        st.subheader("2. Medical & Injury Screen (Auto Substitutions)")
        knee_pain = st.checkbox("Anterior Knee Pain / Patellofemoral Strain", value=False)
        back_pain = st.checkbox("Lumbar Spine / Low Back Strain", value=False)
        shoulder_pain = st.checkbox("Shoulder Impingement / AC Joint Pain", value=False)
        hamstring_strain = st.checkbox("Hamstring Strain (Acute / Subacute)", value=False)

    st.divider()

    # AUTOMATED EXERCISE SUBSTITUTION ENGINE
    squat_ex = "Barbell Back Squat"
    hinge_ex = "Conventional Deadlift"
    press_ex = "Overhead Barbell Press"
    hams_ex = "Nordic Hamstring Curls"

    substitutions = []

    if knee_pain:
        squat_ex = "Box Squat (Vertical Tibia) / Spanish Squats"
        substitutions.append("⚠️ **Knee Pain:** Replaced Deep Squats with Box Squats & Spanish Squat holds to reduce patellofemoral shear.")

    if back_pain:
        hinge_ex = "Trap Bar Deadlift / Single-Leg RDL"
        substitutions.append("⚠️ **Low Back Strain:** Replaced Floor Deadlifts with Trap Bar & Single-Leg RDLs to limit spinal axial compression.")

    if shoulder_pain:
        press_ex = "Landmine Press / Neutral-Grip DB Bench Press"
        substitutions.append("⚠️ **Shoulder Impingement:** Replaced Barbell Overhead Press with Landmine Press to allow free scapular rhythm.")

    if hamstring_strain:
        hams_ex = "Isometric Hamstring Bridge Holds & Cable Hips"
        substitutions.append("⚠️ **Hamstring Strain:** Replaced Eccentric Nordics with Submaximal Isometrics to control strain rate.")

    if substitutions:
        st.subheader("🛠️ Active Exercise Safety Modifications")
        for sub in substitutions:
            st.warning(sub)
        st.divider()

    # GENERATED 4-WEEK PROGRAM TABLE
    st.header(f"3. Prescribed 1-Month Program for {selected_player}")
    st.write(f"**Primary Limiter Identified:** {'Maximal Strength' if ratings['rsr'] < 6.0 else ('Rate of Force Development' if ratings['dsd'] < 6.0 else 'Balanced Maintenance')}")

    tab_w1, tab_w2, tab_w3, tab_w4 = st.tabs(["Week 1: Accumulation", "Week 2: Intensification", "Week 3: Peak Load", "Week 4: Deload & Re-Test"])

    with tab_w1:
        st.markdown("### Week 1: Accumulation Phase (Volume Focus)")
        w1_data = [
            {"Day": "Day 1 (Lower Force)", "Primary Movement": f"{squat_ex} (3x5 @ 75% 1RM)", "Accessory 1": f"{hams_ex} (3x6)", "Conditioning/Mobility": "Ankle Dorsiflexion Glides (3x12)"},
            {"Day": "Day 2 (Upper Force)", "Primary Movement": f"{press_ex} (3x5 @ 75% 1RM)", "Accessory 1": "Chest-Supported Row (3x8)", "Conditioning/Mobility": "Band Facepulls (3x15)"},
            {"Day": "Day 3 (Lower Hinge)", "Primary Movement": f"{hinge_ex} (3x5 @ 75% 1RM)", "Accessory 1": "Bulgarian Split Squat (3x8/leg)", "Conditioning/Mobility": "HIIT Bike Erg (15s sprint / 45s rest)"}
        ]
        st.table(pd.DataFrame(w1_data))

    with tab_w2:
        st.markdown("### Week 2: Intensification Phase (Force & Velocity)")
        w2_data = [
            {"Day": "Day 1 (Lower Force)", "Primary Movement": f"{squat_ex} (4x3 @ 82.5% 1RM)", "Accessory 1": f"{hams_ex} (3x5)", "Conditioning/Mobility": "Ankle Dorsiflexion Glides (3x12)"},
            {"Day": "Day 2 (Upper Force)", "Primary Movement": f"{press_ex} (4x3 @ 82.5% 1RM)", "Accessory 1": "Heavy DB Row (3x6)", "Conditioning/Mobility": "Band Facepulls (3x15)"},
            {"Day": "Day 3 (Lower Hinge)", "Primary Movement": f"{hinge_ex} (4x3 @ 82.5% 1RM)", "Accessory 1": "Step-Ups (3x6/leg)", "Conditioning/Mobility": "Repeat Sprint Ability (6x30m)"}
        ]
        st.table(pd.DataFrame(w2_data))

    with tab_w3:
        st.markdown("### Week 3: Peak Load Phase (Maximal Neuromuscular Drive)")
        w3_data = [
            {"Day": "Day 1 (Lower Force)", "Primary Movement": f"{squat_ex} (4x2 @ 87.5% 1RM)", "Accessory 1": f"{hams_ex} (2x4)", "Conditioning/Mobility": "Dynamic Mobility Warm-Up"},
            {"Day": "Day 2 (Upper Force)", "Primary Movement": f"{press_ex} (4x2 @ 87.5% 1RM)", "Accessory 1": "Weighted Pull-Ups (3x4)", "Conditioning/Mobility": "Shoulder CARs"},
            {"Day": "Day 3 (Lower Hinge)", "Primary Movement": f"{hinge_ex} (4x2 @ 87.5% 1RM)", "Accessory 1": "Single-Leg RDL (3x5/leg)", "Conditioning/Mobility": "Max Velocity Sprints (4x20m)"}
        ]
        st.table(pd.DataFrame(w3_data))

    with tab_w4:
        st.markdown("### Week 4: Deload & Re-Assessment Phase")
        w4_data = [
            {"Day": "Day 1 (Recovery Light)", "Primary Movement": f"{squat_ex} (2x3 @ 60% 1RM)", "Accessory 1": "Glute Bridges (2x10)", "Conditioning/Mobility": "Full Body Mobility Routine"},
            {"Day": "Day 2 (Recovery Light)", "Primary Movement": f"{press_ex} (2x3 @ 60% 1RM)", "Accessory 1": "Lat Pulldowns (2x10)", "Conditioning/Mobility": "Thoracic Spine Rotations"},
            {"Day": "Day 3 (RE-TEST DAY)", "Primary Movement": "Re-Test CMJ, IMTP, & Sprint Times", "Accessory 1": "Log New 1-10 Ratings", "Conditioning/Mobility": "Update History Profile"}
        ]
        st.table(pd.DataFrame(w4_data))
