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

# --- USER BRANDING CONFIG ---
DEVELOPER_NAME = "[Coach / Ahmed Youssef]"  # Replace with your full name or handle

# --- ENERGETIC RGB & GLASSMORPHISM THEME (CUSTOM CSS) ---
custom_theme = """
<style>
/* Dark Athletic Background with Dark Overlay */
.stApp {
    background: linear-gradient(rgba(10, 12, 18, 0.88), rgba(10, 12, 18, 0.94)), 
                url('https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=1920&q=80');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Glowing Neon Headers */
h1 {
    color: #ffffff !important;
    text-shadow: 0 0 15px rgba(0, 210, 255, 0.6), 0 0 30px rgba(0, 210, 255, 0.2);
    font-weight: 800 !important;
}

h2, h3 {
    color: #e0e6ed !important;
    text-shadow: 0 0 10px rgba(255, 0, 128, 0.4);
}

/* Glassmorphism Metric Cards */
div[data-testid="stMetric"] {
    background: rgba(18, 22, 32, 0.85) !important;
    border: 1px solid rgba(0, 210, 255, 0.35) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: 0 0 20px rgba(0, 210, 255, 0.15) !important;
    transition: all 0.3s ease-in-out !important;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-4px) !important;
    border-color: rgba(0, 210, 255, 0.8) !important;
    box-shadow: 0 0 30px rgba(0, 210, 255, 0.4) !important;
}

/* Sidebar Dark Glass Styling */
section[data-testid="stSidebar"] {
    background-color: rgba(12, 15, 23, 0.92) !important;
    border-right: 1px solid rgba(255, 0, 128, 0.3) !important;
    backdrop-filter: blur(10px) !important;
}

/* Glowing Primary Button */
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
    # 1. Relative Strength (Stone et al., 2003) - Baseline 0.8x BW to Elite 2.5x BW
    score_rsr = max(1.0, min(10.0, 1.0 + ((rsr - 0.8) / 1.7) * 9.0))
    
    # 2. Dynamic Strength Deficit (Suchomel et al., 2016) - Optimal window around 0.70
    score_dsd = max(1.0, 10.0 - (abs(dsd - 0.70) / 0.25) * 9.0)
    
    # 3. Ankle Mobility (Bennell et al., 1998) - Range 4cm to 15cm
    score_mobility = max(1.0, min(10.0, 1.0 + ((mobility - 4.0) / 11.0) * 9.0))
    
    # 4. Fatigue Index (Bishop et al., 2011) - Drop-off range 2% (Elite) to 15% (Low)
    score_fatigue = max(1.0, min(10.0, 10.0 - ((fatigue - 2.0) / 13.0) * 9.0))
    
    # Weighted Composite ATHLETE-IQ Rating
    overall_iq = (score_rsr * 0.30) + (score_dsd * 0.30) + (score_mobility * 0.20) + (score_fatigue * 0.20)
    
    return {
        "rsr": round(score_rsr, 1),
        "dsd": round(score_dsd, 1),
        "mobility": round(score_mobility, 1),
        "fatigue": round(score_fatigue, 1),
        "overall": round(overall_iq, 1)
    }

# --- SESSION STATE SIMULATION ---
if "history" not in st.session_state:
    base_date = datetime.today()
    st.session_state.history = pd.DataFrame([
        {"Date": (base_date - timedelta(days=90)).strftime("%Y-%m-%d"), "Weight": 76.0, "1RM": 105.0, "RSR": 1.38, "CMJ": 1500, "IMTP": 2900, "DSD": 0.51, "Fatigue": 11.2},
        {"Date": (base_date - timedelta(days=60)).strftime("%Y-%m-%d"), "Weight": 75.5, "1RM": 112.5, "RSR": 1.49, "CMJ": 1620, "IMTP": 3050, "DSD": 0.53, "Fatigue": 9.8},
        {"Date": (base_date - timedelta(days=30)).strftime("%Y-%m-%d"), "Weight": 75.0, "1RM": 118.0, "RSR": 1.57, "CMJ": 1710, "IMTP": 3150, "DSD": 0.54, "Fatigue": 8.5},
    ])

# --- LANDING TITLE ---
st.title("🧠 ATHLETE-IQ Engine")
st.caption(f"⚡ Lead Performance Architect: **{DEVELOPER_NAME}** | Evidence-Based Athletic Profiling")

# --- SIDEBAR INPUTS ---
st.sidebar.markdown(f"### 👤 Lead Sports Scientist\n**{DEVELOPER_NAME}**")
st.sidebar.divider()

st.sidebar.header("1. Assessment Inputs")
test_date = st.sidebar.date_input("Assessment Date", datetime.today())
body_weight = st.sidebar.number_input("Body Weight (kg)", min_value=40.0, max_value=150.0, value=75.0, step=0.5)

st.sidebar.subheader("Mobility Screening")
ankle_dorsiflexion = st.sidebar.number_input("Ankle Dorsiflexion (cm)", min_value=0.0, max_value=25.0, value=11.0)
fms_asymmetry = st.sidebar.checkbox("FMS Asymmetry or Joint Pain Present?", value=False)

st.sidebar.subheader("Force & Power Diagnostics")
cmj_force = st.sidebar.number_input("CMJ Peak Force (N)", min_value=500, max_value=6000, value=2200)
imtp_force = st.sidebar.number_input("IMTP Peak Force (N)", min_value=1000, max_value=8000, value=3100)

st.sidebar.subheader("Strength & Conditioning")
one_rm_squat = st.sidebar.number_input("Estimated 1RM Squat/Trap Bar (kg)", min_value=0.0, max_value=400.0, value=140.0)
best_sprint = st.sidebar.number_input("Best 30m Sprint Time (s)", min_value=3.0, max_value=10.0, value=4.10)
worst_sprint = st.sidebar.number_input("Worst 30m Sprint Time (s)", min_value=3.0, max_value=10.0, value=4.35)

# --- CALCULATIONS & RATINGS ---
rsr = one_rm_squat / body_weight
dsd = cmj_force / imtp_force if imtp_force > 0 else 0
fatigue_index = ((worst_sprint - best_sprint) / best_sprint) * 100 if best_sprint > 0 else 0

ratings = calculate_ratings(rsr, dsd, ankle_dorsiflexion, fatigue_index)

# --- SAVE SESSION BUTTON ---
if st.sidebar.button("💾 Save Assessment to History"):
    new_entry = pd.DataFrame([{
        "Date": test_date.strftime("%Y-%m-%d"),
        "Weight": body_weight,
        "1RM": one_rm_squat,
        "RSR": round(rsr, 2),
        "CMJ": cmj_force,
        "IMTP": imtp_force,
        "DSD": round(dsd, 2),
        "Fatigue": round(fatigue_index, 1)
    }])
    st.session_state.history = pd.concat([st.session_state.history, new_entry], ignore_index=True)
    st.sidebar.success("Saved successfully!")

st.divider()

# --- COMPOSITE OVERALL SCORE BANNER ---
st.header("🏆 Composite Performance Score")
c1, c2 = st.columns([1, 2])
with c1:
    st.metric("OVERALL ATHLETE-IQ RATING", f"{ratings['overall']} / 10.0", delta=f"{'ELITE' if ratings['overall'] >= 8.5 else ('OPTIMAL' if ratings['overall'] >= 6.5 else 'NEEDS WORK')}")
with c2:
    st.write(f"The **ATHLETE-IQ Composite Rating** is a weighted aggregate of the athlete's neuromuscular, structural, and metabolic capacity derived from published strength & conditioning research.")

st.divider()

# --- SCIENTIFIC 1-10 RATINGS METRICS ---
st.header("1. Peer-Reviewed Element Ratings (1–10 Scale)")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Relative Strength", f"{ratings['rsr']} / 10", delta=f"Raw: {rsr:.2f}x BW (Stone 2003)")
kpi2.metric("Explosive Power (DSD)", f"{ratings['dsd']} / 10", delta=f"Raw: {dsd:.2f} (Suchomel 2016)")
kpi3.metric("Ankle Mobility", f"{ratings['mobility']} / 10", delta=f"Raw: {ankle_dorsiflexion} cm (Bennell 1998)")
kpi4.metric("Anaerobic Buffer", f"{ratings['fatigue']} / 10", delta=f"Fatigue: {fatigue_index:.1f}% (Bishop 2011)")

st.divider()

# --- VISUALIZATIONS ---
st.header("2. Interactive Profiling")

col_left, col_right = st.columns(2)

dark_layout = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#E0E6ED'),
    xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
)

with col_left:
    st.subheader("⚡ Theoretical Force-Velocity Curve")
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
    st.subheader("🎯 1–10 Radar Profile vs. Elite Benchmark")
    categories = ['Relative Strength', 'Explosive Power', 'Ankle Mobility', 'Anaerobic Buffer']
    scores_10 = [ratings['rsr'], ratings['dsd'], ratings['mobility'], ratings['fatigue']]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=scores_10, theta=categories, fill='toself', name='Athlete Score (1-10)', fillcolor='rgba(0, 210, 255, 0.35)', line=dict(color='#00D2FF', width=2)))
    fig_radar.add_trace(go.Scatterpolar(r=[10, 10, 10, 10], theta=categories, mode='lines', name='Elite Standard (10/10)', line=dict(dash='dash', color='#FF007F')))
    
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

# --- SCIENTIFIC BENCHMARK BREAKDOWN TABLE ---
st.header("3. Scientific Reference & Benchmark Matrix")
st.markdown("""
| Fitness Pillar | Tested Metric | Peer-Reviewed Reference | Target Standard (10/10 Rating) |
| :--- | :--- | :--- | :--- |
| **Relative Strength** | 1RM Squat / Body Mass | *Stone et al. (2003) & Baker (2001)* | $\ge 2.50\times\text{ Body Weight}$ |
| **Dynamic Deficit** | CMJ Force / IMTP Force | *Suchomel et al. (2016)* | $0.65 - 0.75\text{ (Optimal Transfer)}$ |
| **Ankle Mobility** | Weight-Bearing Lunge Test | *Bennell et al. (1998) & Pope (1998)* | $\ge 15.0\text{ cm Range of Motion}$ |
| **Sprint Fatigue** | 30m Repeat Sprint Decay | *Bishop et al. (2011) & Girard (2011)* | $\le 2.0\%\text{ Speed Drop-off}$ |
""")

st.divider()

# --- PROGRAMMING ENGINE ---
st.header("4. Automated Program Recommendations")
col_p1, col_p2, col_p3 = st.columns(3)

with col_p1:
    st.subheader("Phase 1: Warm-Up Focus")
    if fms_asymmetry or ankle_dorsiflexion < 10.0:
        st.error("⚠️ Corrective Priority")
        if ankle_dorsiflexion < 10.0:
            st.write(f"- Ankle restriction ({ankle_dorsiflexion} cm vs 10 cm target). Perform soleus/gastrocnemius myofascial release and dorsiflexion glides.")
        if fms_asymmetry:
            st.write("- Clear joint pain / unilateral asymmetries prior to heavy dynamic loading.")
    else:
        st.success("✅ Mobility Optimal")
        st.write("- Proceed with standard athletic dynamic warm-up.")

with col_p2:
    st.subheader("Phase 2: Strength Focus")
    if dsd < 0.60:
        st.info("🏋️ Maximal Strength Focus")
        st.write("Load heavy compound lifts at 80–90% 1RM (3–5 sets x 3–5 reps).")
    elif dsd > 0.80:
        st.warning("⚡ Rate of Force Development Focus")
        st.write("Prioritize velocity: ballistic jumps, plyometrics, and dynamic lifts at 40–60% 1RM.")
    else:
        st.success("⚖️ Balanced Power Profile")
        st.write("Maintain contrast/complex loading across force-velocity spectrum (60–80% 1RM).")

with col_p3:
    st.subheader("Phase 3: Conditioning Focus")
    if fatigue_index > 8.0:
        st.error(f"🫁 High Fatigue ({fatigue_index:.1f}%)")
        st.write("Prescribe Repeat Sprint Ability (RSA) and short HIIT intervals (15s work / 15s rest).")
    else:
        st.success(f"✅ Aerobic Buffer Optimal ({fatigue_index:.1f}%)")
        st.write("Maintain sport-specific field work.")

st.divider()

# --- LONGITUDINAL TRENDS ---
st.header("5. Longitudinal Trends")
if not st.session_state.history.empty:
    hist_df = st.session_state.history.sort_values(by="Date")
    tab1, tab2 = st.tabs(["Strength & Mass Progress", "Power Output"])
    
    with tab1:
        fig_str = px.line(hist_df, x="Date", y=["RSR", "1RM"], markers=True, title="Relative Strength (RSR) vs 1RM (kg)")
        fig_str.update_layout(**dark_layout)
        st.plotly_chart(fig_str, use_container_width=True)
        
    with tab2:
        fig_power = px.line(hist_df, x="Date", y=["CMJ", "IMTP"], markers=True, title="Force Output (N)")
        fig_power.update_layout(**dark_layout)
        st.plotly_chart(fig_power, use_container_width=True)
