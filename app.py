import streamlit as st
import pandas as pd
import numpy as np

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Athlete-IQ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Energetic RGB Cyberpunk / Sports-Tech CSS Theme
st.markdown("""
<style>
    /* Main Background Dark Mesh Gradient */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #151d30 0%, #080a0f 80%) !important;
        color: #F0F6FC;
    }
    
    /* Energetic RGB Title Styling */
    .main-header { 
        font-size: 2.8rem; 
        font-weight: 900; 
        background: linear-gradient(90deg, #00E5FF 0%, #7C4DFF 50%, #FF4081 100%); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        text-shadow: 0 0 25px rgba(0, 229, 255, 0.4);
        margin-bottom: 0px; 
        letter-spacing: -0.5px;
    }
    
    .sub-header { 
        font-size: 1.2rem; 
        color: #00E5FF; 
        font-weight: 700; 
        margin-bottom: 25px; 
        letter-spacing: 1.5px;
        text-transform: uppercase;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
    }
    
    /* Neon RGB Glowing Card Containers */
    .card { 
        background: rgba(18, 22, 31, 0.85) !important; 
        backdrop-filter: blur(12px);
        color: #E0E0E0; 
        border-radius: 12px; 
        padding: 20px; 
        border: 1px solid rgba(0, 229, 255, 0.25);
        border-left: 5px solid #00E5FF; 
        margin-bottom: 20px; 
        box-shadow: 0 0 18px rgba(0, 229, 255, 0.15);
    }
    
    .alert-card { 
        background: rgba(35, 12, 18, 0.9) !important; 
        backdrop-filter: blur(12px);
        color: #FFCDD2; 
        border-radius: 12px; 
        padding: 20px; 
        border: 1px solid rgba(255, 64, 129, 0.4);
        border-left: 5px solid #FF4081; 
        margin-bottom: 20px; 
        box-shadow: 0 0 22px rgba(255, 64, 129, 0.25);
    }
    
    .warning-card { 
        background: rgba(35, 28, 5, 0.9) !important; 
        backdrop-filter: blur(12px);
        color: #FFF59D; 
        border-radius: 12px; 
        padding: 20px; 
        border: 1px solid rgba(255, 215, 0, 0.4);
        border-left: 5px solid #FFD700; 
        margin-bottom: 20px; 
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
    }

    /* Custom Sidebar Glow */
    section[data-testid="stSidebar"] {
        background-color: #0a0d14 !important;
        border-right: 1px solid rgba(124, 77, 255, 0.25) !important;
    }

    /* Metric Display Highlight */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #00E5FF !important;
        text-shadow: 0 0 12px rgba(0, 229, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATABASE: 60+ CLINICAL INJURIES
# -----------------------------------------------------------------------------
INJURY_DATABASE = {
    "Upper Extremity": {
        "Shoulder & Scapula": {
            "Muscles / Tendons": [
                "Rotator Cuff Tear / Tendinopathy", "Biceps Tendonitis / Tear",
                "Pectoralis Major Tear", "Deltoid Strain"
            ],
            "Ligaments & Joint Capsules": [
                "Glenohumeral Instability / Dislocation", "AC Joint Sprain ('Separation')",
                "SLAP Lesion", "Bankart Lesion", "Adhesive Capsulitis ('Frozen Shoulder')"
            ]
        },
        "Upper Arm (Brachium)": {
            "Muscles / Tendons": ["Biceps Brachii Strain", "Triceps Brachii Strain / Tendonitis", "Brachialis Strain"],
            "Ligaments & Connective Tissue": ["Intermuscular Septa Fascial Strain"]
        },
        "Elbow & Forearm": {
            "Muscles / Tendons": [
                "Lateral Epicondylitis ('Tennis Elbow')", "Medial Epicondylitis ('Golfer's Elbow')",
                "Distal Biceps Tendon Rupture", "Forearm Flexor / Extensor Strain"
            ],
            "Ligaments & Joint Capsules": [
                "Ulnar Collateral Ligament (UCL) Tear", "Radial Collateral Ligament (RCL) Sprain",
                "Annular Ligament Sprain / Subluxation"
            ]
        },
        "Wrist, Hand & Fingers": {
            "Muscles / Tendons": [
                "De Quervain’s Tenosynovitis", "Flexor Tendon Avulsion ('Jersey Finger')",
                "Extensor Tendon Rupture ('Mallet Finger')", "Trigger Finger (Stenosing Tenosynovitis)"
            ],
            "Ligaments & Joint Capsules": [
                "TFCC Tear", "Scapholunate Ligament Disruption",
                "Ulnar Collateral Ligament Tear ('Gamekeeper’s/Skier’s Thumb')", "Volar Plate Avulsion"
            ]
        }
    },
    "Core, Spine & Pelvis": {
        "Cervical & Thoracic Spine": {
            "Muscles / Tendons": ["Whiplash / Cervical Paraspinal Strain", "Rhomboid & Thoracic Erector Sprain"],
            "Ligaments & Discs": ["Cervical / Thoracic Disc Herniation", "Facet Joint Sprain", "Ligamentum Nuchae / Interspinous Ligament Sprain"]
        },
        "Lumbar Spine, Abdomen & Pelvis": {
            "Muscles / Tendons": ["Lumbar Erector Spinae / Multifidus Strain", "Rectus Abdominis / Oblique Strain", "Athletic Pubalgia ('Sports Hernia')"],
            "Ligaments & Discs": ["Lumbar Disc Bulge / Herniation", "Sacroiliac (SI) Joint Sprain", "Iliolumbar Ligament Sprain"]
        }
    },
    "Lower Extremity": {
        "Hip & Groin": {
            "Muscles / Tendons": ["Groin Strain (Adductors)", "Iliopsoas Strain / Bursitis", "Gluteal Tendinopathy / Tear", "Hamstring Complex Strain (Proximal)"],
            "Ligaments & Joint Capsules": ["Acetabular Labral Tear", "Ligamentum Teres Tear", "Iliofemoral / Ischiofemoral Ligament Sprain"]
        },
        "Thigh (Anterior & Posterior)": {
            "Muscles / Tendons": ["Quadriceps Strain / Contusion", "Hamstring Muscle Belly Tear", "Iliotibial (IT) Band Friction Syndrome"]
        },
        "Knee": {
            "Muscles / Tendons": ["Patellar Tendinopathy ('Jumper’s Knee')", "Quadriceps Tendon Rupture", "Popliteus Strain"],
            "Ligaments, Cartilage & Capsules": ["Anterior Cruciate Ligament (ACL) Tear", "Posterior Cruciate Ligament (PCL) Tear", "Medial Collateral Ligament (MCL) Sprain", "Lateral Collateral Ligament (LCL) Sprain", "Meniscal Tear (Medial / Lateral)", "Patellofemoral Medial Retinaculum Tear"]
        },
        "Lower Leg (Calf & Shin)": {
            "Muscles / Tendons": ["Gastrocnemius Strain ('Tennis Leg')", "Soleus Strain", "Shin Splints (MTSS)", "Tibialis Anterior / Posterior Tendinopathy"],
            "Connective Tissue": ["Exertional Compartment Syndrome"]
        },
        "Ankle & Foot": {
            "Muscles / Tendons": ["Achilles Tendonitis / Rupture", "Peroneal Tendon Subluxation / Strain", "Plantaris Tendon Rupture"],
            "Ligaments & Joint Capsules": ["Inversion Ankle Sprain (ATFL/CFL)", "Eversion Ankle Sprain (Deltoid)", "High Ankle Sprain (Syndesmosis)", "Plantofascial Rupture / Fasciitis", "Lisfranc Ligament Complex Injury", "Turf Toe"]
        }
    }
}

# Header Banner
st.markdown("<p class='main-header'>🧠 Athlete-IQ</p>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Coach Ahmed Youssef</p>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# COLLAPSIBLE SIDEBAR MENU
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Navigation")
    page = st.radio(
        "Select Section:",
        [
            "1. Demographics & Workload",
            "2. Clinical Medical Engine",
            "3. Posture & Mobility",
            "4. Power & Performance",
            "5. 1-Month Plan Generator"
        ]
    )
    st.markdown("---")
    st.caption("⚡ Powered by Athlete-IQ Engine")

# Initialize Session States
if "blacklisted_movements" not in st.session_state:
    st.session_state.blacklisted_movements = []
if "in_season" not in st.session_state:
    st.session_state.in_season = False
if "sport_category" not in st.session_state:
    st.session_state.sport_category = "General Fitness / Body Recomp"
if "total_external_hours" not in st.session_state:
    st.session_state.total_external_hours = 0.0

# -----------------------------------------------------------------------------
# PAGE 1: DEMOGRAPHICS & WORKLOAD
# -----------------------------------------------------------------------------
if page == "1. Demographics & Workload":
    st.subheader("1. Athlete Profile & Sport Context")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        athlete_name = st.text_input("Athlete Full Name", "Marcus Vance")
        age = st.number_input("Age", min_value=10, max_value=80, value=24)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    with col2:
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=182.0)
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=80.0)
        level = st.selectbox("Competitive Level", ["Pro/Elite", "College", "Youth", "General Fitness / Gen Pop"])
    with col3:
        st.session_state.sport_category = st.selectbox("Primary Sport Focus", [
            "Field & Court (Football, Basketball, Soccer, Rugby)",
            "Overhead & Racket (Tennis, Volleyball, Swimming)",
            "Combat & Contact (MMA, Boxing, Wrestling)",
            "Endurance (Running, Cycling)",
            "General Fitness / Body Recomp"
        ])
        st.session_state.in_season = st.checkbox("Athlete is Currently IN-SEASON", value=st.session_state.in_season)
        readiness = st.slider("Daily Readiness Score (1-10)", 1, 10, 8)

    st.markdown("---")
    st.subheader("2. External Club & Training Load")
    col_c1, col_c2, col_c3 = st.columns(3)
    
    is_general_fitness = "General Fitness" in st.session_state.sport_category
    
    with col_c1:
        club_days = st.number_input("Club Practice Days / Week", min_value=0, max_value=7, value=0 if is_general_fitness else 4, disabled=is_general_fitness)
    with col_c2:
        club_hours = st.number_input("Avg Hours / Practice Day", min_value=0.0, max_value=8.0, value=0.0 if is_general_fitness else 2.5, step=0.5, disabled=is_general_fitness)
    with col_c3:
        st.session_state.total_external_hours = club_days * club_hours
        st.metric("Total External Sport Load", f"{st.session_state.total_external_hours:.1f} hrs/wk")
        if st.session_state.total_external_hours >= 10:
            st.warning("⚡ High External Load: Gym volume will be auto-adjusted to micro-dosing.")
        elif st.session_state.total_external_hours > 0:
            st.info("ℹ️ Moderate External Load: Moderate gym volume recommended.")

# -----------------------------------------------------------------------------
# PAGE 2: CLINICAL MEDICAL ENGINE
# -----------------------------------------------------------------------------
elif page == "2. Clinical Medical Engine":
    st.subheader("Clinical Injury & Pathology Logging")
    
    st.markdown("#### 3-Tier Cascading Pathology Picker")
    m_col1, m_col2, m_col3 = st.columns(3)
    
    with m_col1:
        selected_region = st.selectbox("Select Body Region", list(INJURY_DATABASE.keys()))
    with m_col2:
        selected_subregion = st.selectbox("Select Joint / Sub-Region", list(INJURY_DATABASE[selected_region].keys()))
    with m_col3:
        tissue_categories = INJURY_DATABASE[selected_region][selected_subregion]
        all_pathologies = []
        for cat, items in tissue_categories.items():
            all_pathologies.extend(items)
        selected_injuries = st.multiselect("Tagged Pathologies", all_pathologies)
        
    st.markdown("---")
    st.subheader("Mechanism of Injury (MOI) & Manual Coach Override")
    
    o_col1, o_col2 = st.columns(2)
    with o_col1:
        pain_score = st.slider("Current Pain Scale (VAS 0-10)", 0, 10, 0)
        manual_cause = st.text_input("Specific Trigger / Exercise Cause (e.g., Heavy Back Squat at 90% 1RM)", "")
    
    with o_col2:
        st.session_state.blacklisted_movements = st.multiselect(
            "Blacklist Movement Patterns (Auto-substitutions will apply)",
            ["Barbell Back Squat", "Axial Compression", "Floor Deadlift / Spinal Shear", 
             "Overhead Pressing", "Max-Velocity Sprinting", "Deep Knee Flexion", "High-Impact Plyometrics"],
            default=["Barbell Back Squat", "Axial Compression"] if "squat" in manual_cause.lower() else st.session_state.blacklisted_movements
        )
        coach_override = st.checkbox("Enable Executive Coach Manual Override", value=True)

    if pain_score > 3 or len(selected_injuries) > 0 or len(st.session_state.blacklisted_movements) > 0:
        st.markdown(f"""
        <div class='alert-card'>
            <b>🔴 CLINICAL RED FLAGS ACTIVE</b><br>
            <b>Tagged Pathologies:</b> {', '.join(selected_injuries) if selected_injuries else 'None'}<br>
            <b>Stated Trigger:</b> {manual_cause if manual_cause else 'Unspecified'}<br>
            <b>Barred Patterns:</b> {', '.join(st.session_state.blacklisted_movements) if st.session_state.blacklisted_movements else 'None'}
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PAGE 3: POSTURE & MOBILITY
# -----------------------------------------------------------------------------
elif page == "3. Posture & Mobility":
    st.subheader("Structural Posture & Range of Motion (ROM)")
    
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.markdown("#### Static Plumb Line Deviations")
        st.checkbox("Forward Head Position")
        st.checkbox("Anterior Pelvic Tilt")
        st.checkbox("Genu Valgus (Knee Cave)")
        st.checkbox("Foot Pronation / Flat Arches")
        st.checkbox("Scapular Winging")
        
    with p_col2:
        st.markdown("#### Dynamic FMS & Movement Screening")
        ohs_score = st.radio("Overhead Squat Score", [3, 2, 1], horizontal=True, help="3=Clean, 2=Compensated, 1=Pain")
        sls_score = st.radio("Single-Leg Squat Score", [3, 2, 1], horizontal=True)
        pushup_score = st.radio("Core / Push-Up Hold Score", [3, 2, 1], horizontal=True)

    st.markdown("---")
    st.markdown("#### Joint ROM Inputs & Asymmetry Calculator")
    r_col1, r_col2, r_col3 = st.columns(3)
    with r_col1:
        ank_l = st.number_input("Ankle Dorsiflexion Left (cm)", value=12.0)
        ank_r = st.number_input("Ankle Dorsiflexion Right (cm)", value=9.0)
    with r_col2:
        hip_l = st.number_input("Hip Int Rotation Left (°)", value=40.0)
        hip_r = st.number_input("Hip Int Rotation Right (°)", value=42.0)
    with r_col3:
        sh_l = st.number_input("Shoulder Flexion Left (°)", value=175.0)
        sh_r = st.number_input("Shoulder Flexion Right (°)", value=180.0)

    if ank_l > 0 and ank_r > 0:
        ankle_diff = abs(ank_l - ank_r) / max(ank_l, ank_r) * 100
        if ankle_diff > 10:
            st.markdown(f"<div class='warning-card'>⚠️ <b>Asymmetry Alert:</b> {ankle_diff:.1f}% Ankle Dorsiflexion Asymmetry detected. Auto-populating mobility interventions.</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PAGE 4: POWER & PERFORMANCE
# -----------------------------------------------------------------------------
elif page == "4. Power & Performance":
    st.subheader("Neuromuscular Power & Diagnostic Testing")
    
    if st.session_state.in_season:
        st.info("ℹ️ IN-SEASON MODE: High-fatigue maximal tests are greyed out to preserve match readiness.")

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        cmj_height = st.number_input("CMJ Height (cm)", value=42.0)
        sj_height = st.number_input("Squat Jump Height (cm)", value=38.0)
    with f_col2:
        imtp_force = st.number_input("IMTP Peak Force (N)", value=2800.0, disabled=st.session_state.in_season or "Axial Compression" in st.session_state.blacklisted_movements)
        rsi_index = st.number_input("Reactive Strength Index (RSI)", value=2.1)
    with f_col3:
        eur_ratio = cmj_height / sj_height if sj_height > 0 else 0
        st.metric("Eccentric Utilization Ratio (EUR)", f"{eur_ratio:.2f}")

    st.markdown("---")
    st.subheader("Sport-Specific Functional Battery")
    
    is_gen_fit = "General Fitness" in st.session_state.sport_category
    if is_gen_fit:
        st.warning("🔒 Sport-specific high-level metrics are greyed out for General Fitness profile.")
        
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        pro_agility = st.number_input("5-10-5 Pro Agility Time (s)", value=4.35, disabled=is_gen_fit)
        rsa_fatigue = st.number_input("Sprint Fatigue Index (%)", value=5.2, disabled=is_gen_fit)
    with s_col2:
        gird_deficit = st.number_input("GIRD Shoulder IR Deficit (°)", value=4.0, disabled=is_gen_fit or "Field" in st.session_state.sport_category)
        grip_str = st.number_input("Grip Dynamometry (kg)", value=55.0, disabled=is_gen_fit)

# -----------------------------------------------------------------------------
# PAGE 5: 1-MONTH PERIODIZED PLAN GENERATOR
# -----------------------------------------------------------------------------
elif page == "5. 1-Month Plan Generator":
    st.subheader("Periodized 1-Month Program Builder")
    
    plan_col1, plan_col2, plan_col3 = st.columns(3)
    with plan_col1:
        gym_days = st.selectbox("Gym Training Days / Week (Coach Choice)", [2, 3, 4, 5], index=1)
    with plan_col2:
        session_focus = st.selectbox("Primary Microcycle Focus", ["Hypertrophy / Base", "Max Strength", "Power / Velocity", "Rehab / Movement Efficiency"])
    with plan_col3:
        auto_adjust = st.button("🔄 Regenerate Dynamic Plan")

    st.markdown("---")
    
    st.markdown("##### Active Programming Rules Applied:")
    rule_text = f"• **Gym Days:** {gym_days} Days/Week | **External Practice:** {st.session_state.total_external_hours} hrs/week\n"
    if st.session_state.in_season:
        rule_text += "• **In-Season Capping:** Overall volume reduced by 35%. Peak intensity limited to 82.5% 1RM.\n"
    if len(st.session_state.blacklisted_movements) > 0:
        rule_text += f"• **Exercise Blacklist Active:** Replacing {', '.join(st.session_state.blacklisted_movements)} with safe patterns.\n"
    st.markdown(rule_text)

    main_squat_sub = "Barbell Back Squat"
    main_hinge_sub = "Barbell Deadlift"
    
    if "Barbell Back Squat" in st.session_state.blacklisted_movements or "Axial Compression" in st.session_state.blacklisted_movements:
        main_squat_sub = "Belt Squat OR Banded Spanish Box Squat (Zero Axial Load)"
    if "Floor Deadlift / Spinal Shear" in st.session_state.blacklisted_movements or "Axial Compression" in st.session_state.blacklisted_movements:
        main_hinge_sub = "Elevated Trap Bar Deadlift OR Single-Leg RDL"

    st.markdown(f"### 4-Week Microcycle Matrix ({gym_days} Days / Week)")
    weeks = ["Week 1: Accumulation / Isometrics", "Week 2: Intensification / Eccentrics", "Week 3: Peak Load / Explosive", "Week 4: Deload & Re-Test"]
    
    for w_idx, week_title in enumerate(weeks):
        with st.expander(f"📌 {week_title}", expanded=(w_idx == 0)):
            days_data = []
            for d in range(1, gym_days + 1):
                if d == 1:
                    focus = "Lower Body Force & Trunk"
                    ex1 = f"Lower Compound: {main_squat_sub}"
                    ex2 = "Unilateral: Bulgarian Split Squat"
                    ex3 = "SMR Quads & Hip Flexors"
                elif d == 2:
                    focus = "Upper Body Power & Core"
                    ex1 = "Upper Press: Neutral Grip DB Bench Press"
                    ex2 = "Upper Pull: Chest Supported T-Bar Row"
                    ex3 = "Core: Pallof Press Anti-Rotation Holds"
                elif d == 3:
                    focus = "Posterior Chain & Speed"
                    ex1 = f"Hinge Compound: {main_hinge_sub}"
                    ex2 = "Hamstring: Single-Leg Isometric Hamstring Bridge"
                    ex3 = "Power: Low-Impact Concentric Box Jumps"
                else:
                    focus = "Full Body Dynamic / Conditioning"
                    ex1 = "Multi-planar Lunge Complex"
                    ex2 = "Active Mobility Circuit"
                    ex3 = "Low-Impact Bike Ergometer HIIT"
                    
                days_data.append({
                    "Day": f"Day {d}",
                    "Session Focus": focus,
                    "Primary Exercise Pattern": ex1,
                    "Accessory / Corrective": ex2,
                    "Recovery / Mobility": ex3,
                    "Volume": "2-3 Sets" if (st.session_state.in_season or st.session_state.total_external_hours >= 10) else "3-4 Sets",
                    "Intensity": "RPE 6-7" if w_idx == 3 else ("RPE 7" if st.session_state.in_season else "RPE 8-9")
                })
            
            df_plan = pd.DataFrame(days_data)
            st.table(df_plan)

    st.markdown("---")
    st.download_button(
        label="📥 Export Full Assessment & 1-Month Plan (CSV)",
        data=df_plan.to_csv(index=False),
        file_name="Athlete_IQ_Plan.csv",
        mime="text/csv"
    )
