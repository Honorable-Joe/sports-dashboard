import streamlit as st
import pandas as pd
import numpy as np
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Optional, Tuple

# ==========================================
# 1. ENUMS & CONSTANTS (TYPED DOMAIN ARCHITECTURE)
# ==========================================

class SportType(str, Enum):
    SOCCER = "Soccer"
    BASKETBALL = "Basketball"
    RACQUET_SPORTS = "Racquet Sports (Padel/Tennis)"
    GENERAL_ATHLETE = "General Athleticism"

class SeasonPhase(str, Enum):
    OFF_SEASON = "Off-Season (Hypertrophy/Max Strength)"
    PRE_SEASON = "Pre-Season (Power/Speed Threshold)"
    IN_SEASON = "In-Season (Maintenance/Micro-dosing)"

class DysfunctionalCategory(str, Enum):
    TED = "Tissue Extensibility Dysfunction (TED)"
    JMD = "Joint Mobility Dysfunction (JMD)"
    SMCD = "Stability & Motor Control Dysfunction (SMCD)"
    PAIN = "Pain (Requires Clinical Referral)"

class AnimalFlowPattern(str, Enum):
    BEAST = "Quadrupedal Beast / Traveling Beast"
    CRAB = "Crab Reach & Extension"
    APE = "Deep Squat Ape Transitions"
    SCORPION = "Scorpion Sweep & Thoracic Flow"

# ==========================================
# 2. DATA MODELS WITH VALIDATION & SERIALIZATION
# ==========================================

@dataclass
class MovementAssessment:
    pattern_name: str
    active_rom_deg: float
    passive_rom_deg: float
    has_pain: bool
    required_rom_deg: float

    @property
    def sfma_diagnosis(self) -> DysfunctionalCategory:
        """SFMA Diagnostic Breakout Logic based on Cook et al."""
        if self.has_pain:
            return DysfunctionalCategory.PAIN
        if self.active_rom_deg >= self.required_rom_deg:
            return DysfunctionalCategory.SMCD  # Full ROM present actively, motor control deficit elsewhere
        if self.passive_rom_deg >= self.required_rom_deg:
            return DysfunctionalCategory.SMCD  # Passive normal, active restricted = SMCD
        return DysfunctionalCategory.TED  # Both active and passive restricted = TED/JMD

@dataclass
class AthleteProfile:
    id: str
    name: str
    sport: SportType
    season_phase: SeasonPhase
    cmj_height_cm: float
    sprint_10m_sec: float
    mas_time_1000m_sec: float
    flywheel_10min_watts: float
    squat_1rm_kg: float
    bench_1rm_kg: float
    assessments: Dict[str, MovementAssessment] = field(default_factory=dict)

    @property
    def f_v_ratio(self) -> float:
        """Force-Velocity Ratio with Zero-Division Protection"""
        if self.sprint_10m_sec <= 0:
            return 0.0
        return round(self.cmj_height_cm / (self.sprint_10m_sec * 10.0), 2)

    @property
    def f_v_category(self) -> str:
        ratio = self.f_v_ratio
        if ratio < 0.85:
            return "Force Deficient (Requires Heavy Loading & Eccentric Slow)"
        elif ratio > 1.15:
            return "Velocity Deficient (Requires RFD, Ballistics & Elasticity)"
        return "Balanced Force-Velocity Profile"

    @property
    def mas_mps(self) -> float:
        """Maximal Aerobic Speed in m/s"""
        if self.mas_time_1000m_sec <= 0:
            return 0.0
        return round(1000.0 / self.mas_time_1000m_sec, 2)

    def to_dict(self) -> dict:
        return asdict(self)

# ==========================================
# 3. KNOWLEDGE-BASE DATABASE & ENGINES
# ==========================================

EXERCISE_DATABASE = [
    {
        "name": "Traveling Beast (Animal Flow)",
        "category": "Ground-Based Mobility & SMCD",
        "primary_pattern": "Quadrupedal Core/Shoulder SMCD",
        "contraindications": ["Wrist JMD", "Acute Shoulder Pain"],
        "tempo": "3-1-3-0",
        "regression": "Static Quadruped Hold",
        "progression": "Beast to Crab Underswitch"
    },
    {
        "name": "Barbell Back Squat",
        "category": "Maximal Strength / Compound",
        "primary_pattern": "Bilateral Lower Push",
        "contraindications": ["Ankle Dorsiflexion TED", "Lumbar SMCD"],
        "tempo": "3-1-1-0",
        "regression": "Heels-Elevated Goblet Squat",
        "progression": "Accentuated Eccentric Back Squat"
    },
    {
        "name": "Single-Leg Drop Jump & Rebound",
        "category": "Plyometric / Elastic Power",
        "primary_pattern": "Unilateral Dynamic Ankle/Knee",
        "contraindications": ["Knee Pain", "Acute Hamstring Strain"],
        "tempo": "X-0-X-0",
        "regression": "Bilateral Pogo Jumps",
        "progression": "Depth Jump to Hurdle Rebound"
    },
    {
        "name": "Rotational Kettlebell Med-Ball Scoop Throw",
        "category": "Racket / Soccer Sport-Specific",
        "primary_pattern": "Transverse Rotational Power",
        "contraindications": ["T-Spine Rotation JMD"],
        "tempo": "X-0-X-0",
        "regression": "Half-Kneeling Cable Lift",
        "progression": "Step-Into Rotational Med-Ball Slam"
    }
]

@st.cache_data
def generate_periodized_macrocycle(
    sport: SportType, 
    season: SeasonPhase, 
    squat_1rm: float,
    f_v_category: str
) -> pd.DataFrame:
    """Computes OPEX/NASM 3-Month Macrocycle Prescription."""
    
    # Season-based volume/intensity modifiers
    modifiers = {
        SeasonPhase.OFF_SEASON: {"vol": "High (4-5 sets)", "int_mult": [0.75, 0.85, 0.90]},
        SeasonPhase.PRE_SEASON: {"vol": "Moderate (3-4 sets)", "int_mult": [0.80, 0.88, 0.93]},
        SeasonPhase.IN_SEASON: {"vol": "Low Micro-dose (2-3 sets)", "int_mult": [0.70, 0.75, 0.80]}
    }[season]

    m1_wt = round(squat_1rm * modifiers["int_mult"][0], 1)
    m2_wt = round(squat_1rm * modifiers["int_mult"][1], 1)
    m3_wt = round(squat_1rm * modifiers["int_mult"][2], 1)

    macro_data = [
        {
            "Month": "Month 1 (Accumulation)",
            "Focus Phase": "Hypertrophy & Work Capacity",
            "Target Squat (kg)": f"{m1_wt} kg ({int(modifiers['int_mult'][0]*100)}%)",
            "Tempo String": "3-1-1-0",
            "Volume Standard": modifiers["vol"],
            "ESD Protocol": "110% MAS Shuttles (15s On / 15s Off)"
        },
        {
            "Month": "Month 2 (Intensification)",
            "Focus Phase": "Max Strength & Neural Drive",
            "Target Squat (kg)": f"{m2_wt} kg ({int(modifiers['int_mult'][1]*100)}%)",
            "Tempo String": "2-0-X-0",
            "Volume Standard": "Moderate (3-4 sets)",
            "ESD Protocol": "120% MAS Shuttles (10s On / 20s Off)"
        },
        {
            "Month": "Month 3 (Realization)",
            "Focus Phase": "Peak Power & Taper",
            "Target Squat (kg)": f"{m3_wt} kg ({int(modifiers['int_mult'][2]*100)}%)",
            "Tempo String": "X-0-X-0",
            "Volume Standard": "Low (2-3 sets)",
            "ESD Protocol": "Alactic Repeated Sprints (10m Sprint / 50s Rest)"
        }
    ]
    return pd.DataFrame(macro_data)

# ==========================================
# 4. STREAMLIT HUD DASHBOARD LAYOUT
# ==========================================

st.set_page_config(page_title="Athlete-IQ Engine", layout="wide", page_icon="⚡")

# HUD Styling Injection
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    .hud-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155; border-radius: 10px; padding: 18px; margin-bottom: 12px;
    }
    .hud-title { color: #38bdf8; font-family: 'Courier New', monospace; font-size: 1.1rem; font-weight: bold; }
    .hud-metric { font-size: 1.8rem; font-weight: 800; color: #f8fafc; }
    .tag-badge {
        background-color: #0284c7; color: white; padding: 3px 8px;
        border-radius: 4px; font-size: 0.75rem; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Application Header HUD
st.markdown("<h1 style='text-align: center; color: #38bdf8;'>ATHLETE-IQ // PERFORMANCE & CLINICAL ENGINE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Advanced Sports Science Assessment, SFMA Breakouts & Periodization Engine</p>", unsafe_allow_html=True)
st.divider()

# Sidebar Setup
st.sidebar.header("🕹️ Athlete Profile Controls")
athlete_name = st.sidebar.text_input("Athlete Name", "Marcus Vance")
sport_choice = st.sidebar.selectbox("Sport Discipline", [s.value for s in SportType])
season_choice = st.sidebar.selectbox("Periodization Season", [p.value for p in SeasonPhase])

# Primary Navigation Tabs
tab_profile, tab_sfma, tab_macro, tab_database = st.tabs([
    "📊 Performance Profile & F-V", 
    "🩺 SFMA Diagnostic Breakout", 
    "📅 3-Month Periodized Plan", 
    "🏋️ Exercise Database & Animal Flow"
])

# Initialize Session State Profile
if "athlete" not in st.session_state:
    st.session_state.athlete = AthleteProfile(
        id="ATH-001",
        name=athlete_name,
        sport=SportType(sport_choice),
        season_phase=SeasonPhase(season_choice),
        cmj_height_cm=42.5,
        sprint_10m_sec=1.72,
        mas_time_1000m_sec=215.0,
        flywheel_10min_watts=285.0,
        squat_1rm_kg=140.0,
        bench_1rm_kg=100.0
    )

athlete = st.session_state.athlete

# TAB 1: PERFORMANCE PROFILE
with tab_profile:
    st.markdown("### 🏃 Biomechanical & Energy System Profile")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='hud-card'><div class='hud-title'>F-V RATIO</div>"
                    f"<div class='hud-metric'>{athlete.f_v_ratio}</div>"
                    f"<p style='font-size:0.8rem; color:#94a3b8;'>CMJ / (10m Sprint x 10)</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='hud-card'><div class='hud-title'>MAX AEROBIC SPEED</div>"
                    f"<div class='hud-metric'>{athlete.mas_mps} m/s</div>"
                    f"<p style='font-size:0.8rem; color:#94a3b8;'>1000m Aerobic Threshold</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='hud-card'><div class='hud-title'>FLYWHEEL POWER</div>"
                    f"<div class='hud-metric'>{athlete.flywheel_10min_watts} W</div>"
                    f"<p style='font-size:0.8rem; color:#94a3b8;'>OPEX 10-Min Aerobic Test</p></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='hud-card'><div class='hud-title'>SQUAT 1RM</div>"
                    f"<div class='hud-metric'>{athlete.squat_1rm_kg} kg</div>"
                    f"<p style='font-size:0.8rem; color:#94a3b8;'>Max Strength Benchmark</p></div>", unsafe_allow_html=True)

    st.info(f"**Diagnostic Categorization:** {athlete.f_v_category}")

# TAB 2: SFMA DIAGNOSTIC BREAKOUT
with tab_sfma:
    st.markdown("### 🩺 SFMA Movement Assessment Engine")
    st.caption("Categorizes dysfunction into Tissue Extensibility (TED), Joint Mobility (JMD), or Stability/Motor Control (SMCD).")
    
    c1, c2, c3, c4 = st.columns(4)
    pattern = c1.selectbox("Movement Pattern", ["Ankle Dorsiflexion", "Overhead Squat", "T-Spine Rotation", "Active Straight Leg Raise"])
    act_rom = c2.number_input("Active ROM (°)", value=15.0)
    pas_rom = c3.number_input("Passive ROM (°)", value=28.0)
    pain = c4.checkbox("Pain Present?")

    assessment = MovementAssessment(
        pattern_name=pattern,
        active_rom_deg=act_rom,
        passive_rom_deg=pas_rom,
        has_pain=pain,
        required_rom_deg=25.0
    )
    
    st.markdown("<div class='hud-card'>", unsafe_allow_html=True)
    st.write(f"**Diagnostic Result for {pattern}:**")
    st.subheader(f"🏷️ {assessment.sfma_diagnosis.value}")
    if assessment.sfma_diagnosis == DysfunctionalCategory.SMCD:
        st.warning("Action Required: Program motor control retraining, quadrupedal flows, and stability drills. Passive mobility is sufficient.")
    elif assessment.sfma_diagnosis == DysfunctionalCategory.TED:
        st.error("Action Required: Program soft tissue release, contract-relax PNF stretching, and joint mobilizations.")
    st.markdown("</div>", unsafe_allow_html=True)

# TAB 3: PERIODIZED PLAN
with tab_macro:
    st.markdown("### 📅 3-Month Periodization Macrocycle")
    macro_df = generate_periodized_macrocycle(
        sport=SportType(sport_choice),
        season=SeasonPhase(season_choice),
        squat_1rm=athlete.squat_1rm_kg,
        f_v_category=athlete.f_v_category
    )
    st.dataframe(macro_df, use_container_width=True)

# TAB 4: EXERCISE DATABASE & ANIMAL FLOW
with tab_database:
    st.markdown("### 🏋️ Prescriptive Exercise Database & Animal Flow")
    
    ex_df = pd.DataFrame(EXERCISE_DATABASE)
    st.dataframe(ex_df, use_container_width=True)
    
    st.markdown("#### 🐊 Ground-Based Animal Flow Integration")
    st.markdown("""
    * **Traveling Beast:** Builds closed-kinetic chain scapular stability and anti-rotational core SMCD.
    * **Crab Reach:** Restores posterior chain extension and thoracic mobility JMD.
    * **Scorpion Sweep:** Multi-planar hip rotative control for racquet and soccer athletes.
    """)
