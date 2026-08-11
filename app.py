import streamlit as st
import pandas as pd
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ==========================================
# 1. PAGE CONFIG & CUSTOM STYLING (FROM CODE A)
# ==========================================
st.set_page_config(
    page_title="Athlete-IQ Performance & Clinical Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.94), rgba(2, 6, 23, 0.97)), 
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
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. CODE B OBJECT-ORIENTED DATA STRUCTURES
# ==========================================

@dataclass
class MobilityProfile:
    ankle_dorsiflexion: str = "PASS"
    overhead_flexion: str = "PASS"
    hip_extension: str = "PASS"

@dataclass
class AthleteProfile:
    name: str
    experience_level: str
    equipment: List[str]
    mobility: MobilityProfile
    estimated_1rm: Dict[str, float]

@dataclass
class Exercise:
    id: str
    name: str
    pattern: str                 # "Squat", "Horizontal Push", "Overhead Press", "Hinge", "Power"
    equipment_type: str          # "Barbells & Plates", "Dumbbells", "Cable Systems & Selectorized", etc.
    prerequisites: List[str]     # ["ankle_dorsiflexion", "overhead_flexion", "hip_extension"]
    month_block: int             # 1, 2, or 3


# ==========================================
# 3. CODE B EXERCISE DATABASE
# ==========================================

EXERCISE_DATABASE = [
    # --- SQUAT PATTERN ---
    Exercise("sq01", "Barbell Back Squat", "Squat", "Barbells & Plates", ["ankle_dorsiflexion"], 1),
    Exercise("sq02", "Heel-Elevated Goblet Squat", "Squat", "Dumbbells", [], 1),
    Exercise("sq03", "Barbell Front Squat", "Squat", "Barbells & Plates", ["ankle_dorsiflexion"], 2),
    Exercise("sq04", "Machine Hack Squat", "Squat", "Cable Systems & Selectorized", [], 2),
    Exercise("sq05", "Seated Leg Press", "Squat", "Cable Systems & Selectorized", [], 3),

    # --- HORIZONTAL PUSH PATTERN ---
    Exercise("hp01", "Flat Barbell Bench Press", "Horizontal Push", "Barbells & Plates", [], 1),
    Exercise("hp02", "Incline Dumbbell Bench Press", "Horizontal Push", "Dumbbells", [], 2),
    Exercise("hp03", "Seated Chest Press Machine", "Horizontal Push", "Cable Systems & Selectorized", [], 3),
    Exercise("hp04", "Weighted Ring Push-Up", "Horizontal Push", "Rigs & Suspension (TRX/Wood Rings)", [], 1),

    # --- OVERHEAD PRESS PATTERN ---
    Exercise("oh01", "Barbell Standing OHP", "Overhead Press", "Barbells & Plates", ["overhead_flexion"], 1),
    Exercise("oh02", "Landmine Angled Press", "Overhead Press", "Barbells & Plates", [], 1),
    Exercise("oh03", "Dumbbell Overhead Press", "Overhead Press", "Dumbbells", ["overhead_flexion"], 2),
    Exercise("oh04", "Seated Machine Shoulder Press", "Overhead Press", "Cable Systems & Selectorized", [], 3),

    # --- HINGE PATTERN ---
    Exercise("hg01", "Barbell Conventional Deadlift", "Hinge", "Barbells & Plates", ["hip_extension"], 1),
    Exercise("hg02", "Dumbbell Romanian Deadlift", "Hinge", "Dumbbells", [], 1),
    Exercise("hg03", "Barbell Romanian Deadlift", "Hinge", "Barbells & Plates", [], 2),
    Exercise("hg04", "Cable Hip Thrust", "Hinge", "Cable Systems & Selectorized", [], 3),

    # --- POWER / SPEED PATTERN ---
    Exercise("pw01", "Medicine Ball Rotational Launch", "Power", "Medicine & Slam Balls", [], 1),
    Exercise("pw02", "Heavy Trap-Bar Jump Squat", "Power", "Barbells & Plates", [], 2),
    Exercise("pw03", "Plyometric Box Jumps", "Power", "Plyo Boxes & Agility Ladders", [], 3),
    Exercise("pw04", "Sled Acceleration Starts", "Power", "Sleds & Prowler", [], 1)
]


# ==========================================
# 4. CODE B FILTER & SELECTION ENGINE
# ==========================================

class ExerciseFilterEngine:
    def __init__(self, database: List[Exercise]):
        self.database = database

    def get_valid_exercise(self, pattern: str, month: int, athlete: AthleteProfile) -> Optional[Exercise]:
        candidates = [ex for ex in self.database if ex.pattern == pattern and ex.month_block == month]
        candidates = [ex for ex in candidates if ex.equipment_type in athlete.equipment]
        
        safe_candidates = []
        for ex in candidates:
            is_safe = True
            for prereq in ex.prerequisites:
                if getattr(athlete.mobility, prereq, "PASS") == "FAIL":
                    is_safe = False
                    break
            if is_safe:
                safe_candidates.append(ex)

        if safe_candidates:
            return safe_candidates[0]

        fallbacks = [
            ex for ex in self.database
            if ex.pattern == pattern 
            and ex.equipment_type in ["Cable Systems & Selectorized", "Dumbbells"]
            and ex.equipment_type in athlete.equipment
            and not any(getattr(athlete.mobility, p, "PASS") == "FAIL" for p in ex.prerequisites)
        ]
        return fallbacks[0] if fallbacks else None


# ==========================================
# 5. INTEGRATED ATHLETE-IQ INTELLIGENT LOGIC ENGINE
# ==========================================

class AthleteIQEngine:
    def __init__(self, data: dict, equipment: list):
        self.d = data
        self.equipment = equipment
        self.warnings = []
        
        # Build Mobility Profile from SFMA/Postural inputs
        ankle_flag = "FAIL" if self.d.get("posture_ankle") in ["Pronated Rearfoot", "Supinated Rearfoot"] else "PASS"
        overhead_flag = "FAIL" if self.d.get("shoulder") == "Dysfunctional Painful" or self.d.get("posture_shoulder_pos") == "Anterior Rounded Shoulders" else "PASS"
        hip_flag = "FAIL" if self.d.get("posture_pelvic_tilt") == "Anterior Pelvic Tilt" else "PASS"

        self.mobility = MobilityProfile(
            ankle_dorsiflexion=ankle_flag,
            overhead_flexion=overhead_flag,
            hip_extension=hip_flag
        )

        self.athlete = AthleteProfile(
            name=self.d.get("athlete_name", "Athlete"),
            experience_level="Intermediate",
            equipment=self.equipment,
            mobility=self.mobility,
            estimated_1rm={
                "Squat": 100.0,
                "Horizontal Push": 80.0,
                "Overhead Press": 50.0,
                "Hinge": 120.0,
                "Power": 0.0
            }
        )
        self.filter_engine = ExerciseFilterEngine(EXERCISE_DATABASE)

    def calculate_mas(self) -> float:
        sprint_1000 = self.d.get("s_sprint1000m", 235)
        if sprint_1000 > 0:
            return round(1000.0 / sprint_1000, 2)
        cooper_m = self.d.get("c_cooper", 2500)
        return round((cooper_m / 720.0), 2)

    def evaluate_force_velocity_deficit(self) -> str:
        cmj = self.d.get("p_cmj", 42.0)
        sprint_10m = self.d.get("s_sprint10m", 1.75)
        fv_index = cmj / (sprint_10m * 10)
        if fv_index < 2.0:
            return "Force Deficient (Needs Maximal Strength Loading)"
        elif fv_index > 2.8:
            return "Velocity Deficient (Needs High-Speed Elastic Ballistics)"
        return "Balanced Force-Velocity Profile"

    def evaluate_asymmetry(self) -> float:
        left = self.d.get("p_horiz_jump_uni_l", 105.0)
        right = self.d.get("p_horiz_jump_uni_r", 104.0)
        return round(abs(left - right) / max(left, right) * 100, 1)

    def get_postural_corrective_prep(self) -> str:
        correctives = []
        if self.d.get("posture_foot_arch") == "Flat Foot (Pes Planus)":
            correctives.append("Short-Foot Activation & Tibialis Posterior Loading")
        if self.d.get("posture_ankle") in ["Pronated Rearfoot", "Supinated Rearfoot"]:
            correctives.append("Ankle Dorsiflexion Wall Mob & Iso Holds")
        if self.d.get("posture_pelvic_tilt") == "Anterior Pelvic Tilt":
            correctives.append("Half-Kneeling Hip Flexor Deactivation & Deadbugs")
        elif self.d.get("posture_pelvic_tilt") == "Posterior Pelvic Tilt":
            correctives.append("Hamstring Mobility & Cobra Lumbar Extensions")
        if self.d.get("posture_thoracic") == "Hyper-Kyphosis":
            correctives.append("Foam Roller T-Spine Extensions & Wall Angels")
        if self.d.get("posture_shoulder_pos") == "Anterior Rounded Shoulders":
            correctives.append("Band Face Pulls & Y-T-W Scapular Series")
        if self.d.get("posture_knee") == "Genu Valgum (Knock-Knee)":
            correctives.append("Banded Glute Medius Clamshells & Monster Walks")

        if self.d.get("congenital_defects") != "None Detected":
            correctives.append(f"Protocol for {self.d.get('congenital_defects')}")

        return " + ".join(correctives) if correctives else "Dynamic World's Greatest Stretch & Hip Opener"

    def evaluate_speed_agility_deficits(self) -> dict:
        s5m = self.d.get("s_sprint5m", 1.10)
        tdrill = self.d.get("s_tdrill", 10.2)
        s7x7 = self.d.get("s_7x7", 14.2)
        return {
            "has_accel_deficit": s5m > 1.25,
            "has_cod_deficit": (tdrill > 10.8) or (s7x7 > 15.0)
        }

    def evaluate_upper_capacity(self) -> str:
        pushups = self.d.get("c_pushups", 38)
        pullups = self.d.get("c_pullups", 12)
        if pushups < 15 or pullups < 3:
            return "Low Capacity (Assisted / High Rep Base)"
        elif pushups > 45 and pullups > 15:
            return "High Capacity (Weighted Progressions)"
        return "Standard Capacity"

    def select_lower_compound(self, month: int) -> str:
        has_injury = self.d.get("has_injury") == "Yes"
        injury_site = self.d.get("injury_site", "")
        sfma_ohs = self.d.get("overhead_squat", "Functional Non-Painful")

        if has_injury:
            if any(k in injury_site for k in ["Knee", "ACL", "Patellar"]):
                self.warnings.append("🚨 Knee/ACL Injury: Dynamic knee bending regressed to Isometric Spanish Squats.")
                return "Spanish Squat Isometric Hold (Knee Sparing)"
            elif "Hamstring" in injury_site:
                self.warnings.append("🚨 Hamstring Injury: Swapped for Glute Bridge / Hip Thrust.")
                return "Barbell Glute Bridge / Hip Thrust"
            elif any(k in injury_site for k in ["Lumbar", "Facet"]):
                self.warnings.append("🚨 Lumbar Spine Injury: Axially unloaded movement prescribed.")
                return "Supported Dumbbell Step-Ups"
            elif any(k in injury_site for k in ["Ankle", "Achilles"]):
                self.warnings.append("🚨 Ankle/Achilles Strain: Restricted dorsiflexion.")
                return "Heel-Elevated Goblet Box Squat"

        if sfma_ohs == "Dysfunctional Painful":
            self.warnings.append("🚨 Painful Overhead Squat: Regressed to Supported Box Squats.")
            return "Supported Goblet Box Squat to Parallel"
            
        if self.evaluate_asymmetry() > 10.0:
            self.warnings.append(f"⚠️ Asymmetry >10% ({self.evaluate_asymmetry()}%): Auto-switched to Unilateral Primaries.")
            return "Bulgarian Split Squat (Unilateral Correction)"

        # DB Search Engine
        ex = self.filter_engine.get_valid_exercise("Squat", month, self.athlete)
        return ex.name if ex else "Tempo Bodyweight Pistol Squat"

    def select_upper_press(self, month: int) -> str:
        has_injury = self.d.get("has_injury") == "Yes"
        injury_site = self.d.get("injury_site", "")
        sfma_shld = self.d.get("shoulder", "Functional Non-Painful")

        if has_injury and any(k in injury_site for k in ["Shoulder", "Rotator", "Pectoralis"]):
            self.warnings.append("🚨 Shoulder/Chest Injury: Replaced with Neutral-Grip Incline.")
            return "Neutral-Grip Dumbbell Press"

        if sfma_shld == "Dysfunctional Painful":
            self.warnings.append("🚨 Dysfunctional Upper Reach: Prescribed Landmine Press.")
            return "Half-Kneeling Landmine Press"

        # DB Search Engine
        ex = self.filter_engine.get_valid_exercise("Horizontal Push", month, self.athlete)
        return ex.name if ex else "Bodyweight Deficit Push-Ups"

    def select_power_exercise(self, month: int) -> str:
        has_injury = self.d.get("has_injury") == "Yes"
        injury_site = self.d.get("injury_site", "")

        if has_injury and any(k in injury_site for k in ["Ankle", "Achilles", "Knee"]):
            self.warnings.append("🚨 Lower Limb Injury: High impact plyometrics replaced with Seated Med-Ball Throws.")
            return "Seated Upper-Body Explosive Med-Ball Launch"

        sa = self.evaluate_speed_agility_deficits()
        if sa["has_accel_deficit"]:
            self.warnings.append("⚡ Speed Diagnostic: Acceleration deficit detected -> Added Heavy Sled Starts.")
            return "Heavy Sled Sprints / Band-Resisted Acceleration Starts"

        ex = self.filter_engine.get_valid_exercise("Power", month, self.athlete)
        return ex.name if ex else "Plyometric Box Jumps / Broad Jumps"

    def select_esd_protocol(self) -> str:
        mas = self.calculate_mas()
        sa = self.evaluate_speed_agility_deficits()
        shuttle_dist = round(mas * 1.20 * 15, 1)

        if sa["has_cod_deficit"]:
            self.warnings.append("🏃 Agility Diagnostic: COD deficit detected -> Integrated COD Shuttle Drills.")
            return f"Pro-Agility Shuttle (10m-5m-10m) @ 120% MAS ({shuttle_dist}m Target / 15s Work / 15s Rest)"
        
        return f"15s Linear Shuttle Run @ {shuttle_dist}m Target / 15s Rest (10-12 Mins Total)"

    def generate_program_for_month(self, month: int) -> dict:
        club_hours = self.d.get("club_days", 4) * self.d.get("club_hours_per_day", 2.0)
        vol_schema = "2 Sets / Ex (Low Vol, High Density)" if club_hours >= 10 else "4 Sets / Ex (Standard Build)"

        return {
            "Corrective Prep": self.get_postural_corrective_prep(),
            "Lower Exercise": self.select_lower_compound(month),
            "Upper Exercise": self.select_upper_press(month),
            "Power Exercise": self.select_power_exercise(month),
            "ESD Protocol": self.select_esd_protocol(),
            "FV Profile": self.evaluate_force_velocity_deficit(),
            "MAS": self.calculate_mas(),
            "Asymmetry": self.evaluate_asymmetry(),
            "Upper Capacity": self.evaluate_upper_capacity(),
            "Volume Schema": vol_schema,
            "Alerts": list(set(self.warnings))
        }


# ==========================================
# 6. SESSION STATE INITIALIZATION & HELPERS
# ==========================================

if "form_data" not in st.session_state:
    st.session_state.form_data = {
        # Profile
        "athlete_name": "Alex Morgan",
        "age": 22,
        "gender": "Female",
        "weight_kg": 75.0,
        "height_cm": 178.0,
        "sport_type": "Soccer",
        "evaluating_coach": "Coach Ahmed Youssef 👑",
        "assessment_date": datetime.now().date(),
        "assessment_type": "Baseline (Initial)",
        "training_years": 3,
        # Load & Injury
        "club_days": 4,
        "club_hours_per_day": 2.0,
        "has_injury": "No",
        "injury_category": "Joint",
        "injury_site": "Knee Joint",
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
        # Postural Screening
        "posture_foot_arch": "Normal Arch",
        "posture_foot_pos": "Neutral Foot Stance",
        "posture_ankle": "Vertical Ankle Alignment",
        "posture_tibia": "Straight Tibial Alignment",
        "posture_knee": "Neutral Knee Line",
        "posture_knee_pos": "Neutral Stance",
        "posture_sis": "Normal / Symmetric",
        "posture_hip_pos": "Level Hips",
        "posture_pelvic_tilt": "Neutral Pelvis",
        "posture_lumbar": "Normal Curve",
        "posture_thoracic": "Normal Curve",
        "posture_tspine_rot": "Full Mobility Both Sides",
        "posture_scapula": "Symmetrical Flat",
        "posture_shoulder_lvl": "Level Shoulders",
        "posture_shoulder_pos": "Neutral Shoulder Position",
        "posture_shld_flex_er_ir": "Full Range / Symmetric",
        "posture_hip_flex_slr": "Symmetric Straight Leg Elevation",
        "posture_hip_flex_bent": "Full Knee-Bent Hip Flexion",
        "posture_hip_ir_er": "Symmetric Hip Rotational Range",
        "congenital_defects": "None Detected",
        # Power, Speed, Capacity
        "p_chest_pass": 6.8,
        "p_overhead_throw": 8.5,
        "p_forehand_throw": 0.0,
        "p_backhand_throw": 0.0,
        "p_cmj": 42.0,
        "p_horiz_jump_bi": 215.0,
        "p_horiz_jump_uni_l": 105.0,
        "p_horiz_jump_uni_r": 104.0,
        "p_vert_jump_bi": 45.0,
        "p_vert_jump_uni_l": 22.0,
        "p_vert_jump_uni_r": 21.5,
        "s_sprint5m": 1.10,
        "s_sprint10m": 1.75,
        "s_7x7": 14.2,
        "s_tdrill": 10.20,
        "s_boxdrill": 11.5,
        "s_sprint1000m": 235.0,
        "c_pushups": 38,
        "c_pullups": 12,
        "c_squats": 55,
        "c_situps": 42,
        "c_cooper": 2650
    }

if "athlete_records" not in st.session_state:
    st.session_state.athlete_records = []

def bind_input(key):
    return st.session_state.form_data.get(key)

def update_state(key, val):
    st.session_state.form_data[key] = val

def safe_index(options_list, key):
    val = bind_input(key)
    return options_list.index(val) if val in options_list else 0

def get_macrocycle_phase(month_num: int, week_num: int):
    macro = {
        1: {
            "title": "Month 1: Accumulation Phase (Work Capacity & Base Build)",
            "weeks": {
                1: {"sets": "3 x 10 Reps", "intensity": "65% 1RM (RPE 7)", "phase": "Base Accumulation", "tempo": "3-1-1-0"},
                2: {"sets": "4 x 8 Reps", "intensity": "70% 1RM (RPE 7.5)", "phase": "Volume Build", "tempo": "3-1-1-0"},
                3: {"sets": "4 x 8 Reps", "intensity": "75% 1RM (RPE 8)", "phase": "Overload Peak", "tempo": "3-1-1-0"},
                4: {"sets": "2 x 8 Reps", "intensity": "60% 1RM (RPE 6)", "phase": "Deload & Regeneration", "tempo": "2-0-1-0"}
            }
        },
        2: {
            "title": "Month 2: Intensification Phase (Max Strength & Dynamic Force)",
            "weeks": {
                1: {"sets": "4 x 6 Reps", "intensity": "78% 1RM (RPE 8)", "phase": "Strength Introduction", "tempo": "2-1-1-0"},
                2: {"sets": "4 x 5 Reps", "intensity": "82% 1RM (RPE 8.5)", "phase": "Heavy Loading", "tempo": "2-1-1-0"},
                3: {"sets": "5 x 3 Reps", "intensity": "88% 1RM (RPE 9)", "phase": "Maximal Load Peak", "tempo": "2-0-1-0"},
                4: {"sets": "2 x 5 Reps", "intensity": "65% 1RM (RPE 6)", "phase": "Deload & Regeneration", "tempo": "2-0-1-0"}
            }
        },
        3: {
            "title": "Month 3: Realization Phase (Peak Power, Speed & Taper)",
            "weeks": {
                1: {"sets": "4 x 3 Reps", "intensity": "85% 1RM (RPE 8.5 - Explosive)", "phase": "Power Realization", "tempo": "1-0-1-0"},
                2: {"sets": "4 x 2 Reps", "intensity": "90% 1RM (RPE 9 - Velocity Focus)", "phase": "Peaking Block", "tempo": "1-0-1-0"},
                3: {"sets": "3 x 2 Reps", "intensity": "93% 1RM (RPE 9.5)", "phase": "Maximal Output Peak", "tempo": "1-0-1-0"},
                4: {"sets": "2 x 3 Reps", "intensity": "50% 1RM (Explosive Speed)", "phase": "Match-Ready Taper", "tempo": "1-0-1-0"}
            }
        }
    }
    m_data = macro.get(month_num, macro[1])
    w_data = m_data["weeks"].get(week_num, m_data["weeks"][1])
    return m_data["title"], w_data


# ==========================================
# 7. MAIN INTERFACE & NAVIGATION
# ==========================================

st.markdown("<h1 style='text-align: center; color: #38bdf8; font-weight: 900; margin-bottom: 0px;'>⚡ ATHLETE-IQ PERFORMANCE ENGINE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a855f7; font-weight: 700; font-size: 1.15rem;'>Developed by: Coach Ahmed Youssef 👑</p>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.markdown("### 📌 Navigation")
active_module = st.sidebar.radio(
    "Jump to Module:",
    [
        "📋 1. Demographics & Coach Sign-off",
        "⚽ 2. Club Load & Injury Diagnostics",
        "🩺 3. SFMA & Postural Diagnostic Matrix",
        "💥 4. Sport-Specific Assessment Suite",
        "📈 5. Saved Records & Historical Progress",
        "🚀 6. ADAPTIVE PROGRAM GENERATOR"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗓️ Macrocycle Horizon")
plan_months = st.sidebar.select_slider(
    "Select Program Scope:",
    options=[1, 2, 3],
    value=2,
    format_func=lambda x: f"{x}-Month Macrocycle Block"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏋️ Facility Equipment Matrix")
equipment_selected = st.sidebar.multiselect(
    "Available Gear:",
    [
        "Barbells & Plates", "Dumbbells", "Kettlebells", 
        "Hydro-Inertial (Aqua Bags/Macebells)", "Instability (BOSU/Swiss Ball)",
        "Rigs & Suspension (TRX/Wood Rings)", "Sleds & Prowler",
        "Medicine & Slam Balls", "Cable Systems & Selectorized",
        "Ergometers (AirBike/Rower/SkiErg)", "Plyo Boxes & Agility Ladders"
    ],
    default=["Barbells & Plates", "Dumbbells", "Kettlebells", "Rigs & Suspension (TRX/Wood Rings)", "Sleds & Prowler", "Medicine & Slam Balls", "Cable Systems & Selectorized", "Ergometers (AirBike/Rower/SkiErg)", "Plyo Boxes & Agility Ladders"]
)


# ==========================================
# 8. MODULE CONTROLLERS
# ==========================================

# ------------------------------------------
# MODULE 1: DEMOGRAPHICS
# ------------------------------------------
if active_module == "📋 1. Demographics & Coach Sign-off":
    st.markdown("<div class='banner-header'>📋 Athlete Demographics & Evaluating Coach Sign-Off</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👤 Athlete Profile")
        v_name = st.text_input("Athlete Name", value=bind_input("athlete_name"))
        v_age = st.number_input("Age", 12, 80, value=bind_input("age"))
        g_opts = ["Male", "Female", "Other"]
        v_gender = st.selectbox("Gender", g_opts, index=safe_index(g_opts, "gender"))
        v_weight = st.number_input("Body Weight (kg)", 40.0, 150.0, value=bind_input("weight_kg"))
        v_height = st.number_input("Height (cm)", 120.0, 230.0, value=bind_input("height_cm"))
        sports_list = ["Tennis", "Volleyball", "Combat Sports (MMA/Boxing)", "Racket Sports (Squash/Padel)", "Soccer", "Basketball", "Track & Field (Sprints/Jumps)", "Rugby/American Football", "General Fitness"]
        v_sport = st.selectbox("Sport / Discipline", sports_list, index=safe_index(sports_list, "sport_type"))
    with c2:
        st.subheader("🧢 Evaluating Coach Details")
        v_coach = st.text_input("Evaluating Coach Name", value=bind_input("evaluating_coach"))
        v_date = st.date_input("Assessment Date", value=bind_input("assessment_date"))
        phases = ["Baseline (Initial)", "Mid-Phase Follow-Up", "Re-Assessment (Post-Block)"]
        v_phase = st.selectbox("Assessment Phase", phases, index=safe_index(phases, "assessment_type"))
        v_years = st.number_input("Training History (Years)", 0, 30, value=bind_input("training_years"))

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
# MODULE 2: CLUB LOAD & INJURY DIAGNOSTICS
# ------------------------------------------
elif active_module == "⚽ 2. Club Load & Injury Diagnostics":
    st.markdown("<div class='banner-header'>⚽ Club Training Load & Clinical Injury Diagnostics</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚽ External Club Training Exposure")
        v_days = st.number_input("Club Training Days / Week", 0, 7, value=bind_input("club_days"))
        v_hours = st.number_input("Avg Session Duration (Hours)", 0.5, 5.0, value=bind_input("club_hours_per_day"))
        tot_hrs = v_days * v_hours
        update_state("club_days", v_days)
        update_state("club_hours_per_day", v_hours)

        if tot_hrs >= 10:
            st.warning(f"⚠️ High External Load ({tot_hrs} hrs/wk): Prescribed S&C auto-condenses to 2 Days/Week (Dense Full-Body).")
        elif tot_hrs >= 6:
            st.info(f"📊 Moderate External Load ({tot_hrs} hrs/wk): Prescribed S&C auto-scales to 3 Days/Week.")
        else:
            st.success(f"✅ Low External Load ({tot_hrs} hrs/wk): Prescribed S&C set to 4 Days/Week.")

    with c2:
        st.subheader("🩺 Dynamic Clinical Injury Diagnostic")
        inj_opts = ["No", "Yes"]
        v_has_inj = st.radio("Active / Recent Injury Present?", inj_opts, index=safe_index(inj_opts, "has_injury"), horizontal=True)
        
        injury_map = {
            "Joint": ["Knee Joint", "Ankle Joint", "Shoulder Joint Complex", "Hip Joint", "Elbow Joint", "Wrist/Carpal Joint", "Lumbar Facet Joint"],
            "Muscle": ["Hamstrings Group", "Quadriceps Group", "Gastrocnemius/Soleus", "Pectoralis Major/Minor", "Latissimus Dorsi", "Adductor Groin Group"],
            "Ligament": ["ACL (Anterior Cruciate)", "MCL (Medial Collateral)", "ATFL (Ankle Ligament)", "UCL (Elbow Ligament)", "Syndesmosis (High Ankle)"],
            "Tendon": ["Patellar Tendon", "Achilles Tendon", "Rotator Cuff Tendons", "Biceps Tendon", "Gluteal Tendon"]
        }

        if v_has_inj == "Yes":
            cat_keys = list(injury_map.keys())
            v_cat = st.selectbox("1. Tissue / Structural Category", cat_keys, index=safe_index(cat_keys, "injury_category"))
            sites_available = injury_map[v_cat]
            v_site = st.selectbox("2. Specific Anatomical Site", sites_available, index=safe_index(sites_available, "injury_site"))
            mechs = ["Overuse / Repetitive Stress", "Acute Contact / Traumatic", "Non-Contact Biomechanical"]
            v_mech = st.selectbox("Mechanism of Injury", mechs, index=safe_index(mechs, "injury_mechanism"))
            affects = ["Yes - Active Symptoms", "No - Cleared / Asymptomatic"]
            v_affects = st.radio("Symptoms Present Currently?", affects, index=safe_index(affects, "still_affects"), horizontal=True)
        else:
            v_cat, v_site, v_mech, v_affects = "Joint", "None", "N/A", "No"
            
        update_state("has_injury", v_has_inj)
        update_state("injury_category", v_cat)
        update_state("injury_site", v_site)
        update_state("injury_mechanism", v_mech)
        update_state("still_affects", v_affects)

# ------------------------------------------
# MODULE 3: SFMA & POSTURAL DIAGNOSTICS
# ------------------------------------------
elif active_module == "🩺 3. SFMA & Postural Diagnostic Matrix":
    st.markdown("<div class='banner-header'>🩺 SFMA Movement Patterns & Expanded Postural Diagnostics</div>", unsafe_allow_html=True)
    
    st.subheader("1. SFMA Top-Tier Assessment Suite")
    sfma_opts = ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"]
    c1, c2, c3 = st.columns(3)
    with c1:
        v_cerv = st.selectbox("Cervical Spine Pattern", sfma_opts, index=safe_index(sfma_opts, "cervical"))
        v_shld = st.selectbox("Upper Extremity Reach", sfma_opts, index=safe_index(sfma_opts, "shoulder"))
        v_rot = st.selectbox("Multi-Segmental Rotation", sfma_opts, index=safe_index(sfma_opts, "rotation"))
    with c2:
        v_flex = st.selectbox("Multi-Segmental Flexion", sfma_opts, index=safe_index(sfma_opts, "flexion"))
        v_ext = st.selectbox("Multi-Segmental Extension", sfma_opts, index=safe_index(sfma_opts, "extension"))
    with c3:
        v_sls = st.selectbox("Single-Leg Stance Balance", sfma_opts, index=safe_index(sfma_opts, "sl_stance"))
        v_ohs = st.selectbox("Deep Overhead Squat Pattern", sfma_opts, index=safe_index(sfma_opts, "overhead_squat"))

    update_state("cervical", v_cerv)
    update_state("shoulder", v_shld)
    update_state("rotation", v_rot)
    update_state("flexion", v_flex)
    update_state("extension", v_ext)
    update_state("sl_stance", v_sls)
    update_state("overhead_squat", v_ohs)

    st.markdown("---")
    st.subheader("2. Expanded Static Postural & Range-of-Motion Diagnostic Matrix")
    
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("**🖼️ Lower Extremity & Pelvic Alignment**")
        opts_arch = ["Normal Arch", "Flat Foot (Pes Planus)", "High Arch (Pes Cavus)"]
        opts_foot = ["Neutral Foot Stance", "In-Toeing (Pigeon)", "Out-Toeing (Duck)"]
        opts_ankle = ["Vertical Ankle Alignment", "Pronated Rearfoot", "Supinated Rearfoot"]
        opts_knee = ["Neutral Knee Line", "Genu Valgum (Knock-Knee)", "Genu Varum (Bow-Leg)"]
        v_foot_arch = st.selectbox("Foot Arch Status", opts_arch, index=safe_index(opts_arch, "posture_foot_arch"))
        v_foot_pos = st.selectbox("Foot Position", opts_foot, index=safe_index(opts_foot, "posture_foot_pos"))
        v_ankle = st.selectbox("Ankle Alignment", opts_ankle, index=safe_index(opts_ankle, "posture_ankle"))
        v_knee = st.selectbox("Knee Line / Q-Angle", opts_knee, index=safe_index(opts_knee, "posture_knee"))

    with p2:
        st.markdown("**🖼️ Spinal Curves & Trunk Balance**")
        opts_pelvis = ["Neutral Pelvis", "Anterior Pelvic Tilt", "Posterior Pelvic Tilt"]
        opts_lumbar = ["Normal Curve", "Hyper-Lordosis", "Hypo-Lordosis / Flat Back"]
        opts_thoracic = ["Normal Curve", "Hyper-Kyphosis", "Flat Thoracic Spine"]
        v_pelvic_tilt = st.selectbox("Pelvic Tilt Angle", opts_pelvis, index=safe_index(opts_pelvis, "posture_pelvic_tilt"))
        v_lumbar = st.selectbox("Lumbar Spine Curve", opts_lumbar, index=safe_index(opts_lumbar, "posture_lumbar"))
        v_thoracic = st.selectbox("Thoracic Spine Curve", opts_thoracic, index=safe_index(opts_thoracic, "posture_thoracic"))

    with p3:
        st.markdown("**🖼️ Shoulder & Structural Screening**")
        opts_shld_pos = ["Neutral Shoulder Position", "Anterior Rounded Shoulders"]
        opts_congenital = ["None Detected", "Forward Head Posture (FHP)", "Idiopathic Scoliosis Curve", "Leg Length Discrepancy (LLD)"]
        v_shld_pos = st.selectbox("Shoulder Position", opts_shld_pos, index=safe_index(opts_shld_pos, "posture_shoulder_pos"))
        v_congenital = st.selectbox("Congenital Defects", opts_congenital, index=safe_index(opts_congenital, "congenital_defects"))

    update_state("posture_foot_arch", v_foot_arch)
    update_state("posture_foot_pos", v_foot_pos)
    update_state("posture_ankle", v_ankle)
    update_state("posture_knee", v_knee)
    update_state("posture_pelvic_tilt", v_pelvic_tilt)
    update_state("posture_lumbar", v_lumbar)
    update_state("posture_thoracic", v_thoracic)
    update_state("posture_shoulder_pos", v_shld_pos)
    update_state("congenital_defects", v_congenital)

# ------------------------------------------
# MODULE 4: SPORT-SPECIFIC ASSESSMENT SUITE
# ------------------------------------------
elif active_module == "💥 4. Sport-Specific Assessment Suite":
    st.markdown("<div class='banner-header'>💥 Sport-Specific Power, Speed, Agility & Capacity Testing</div>", unsafe_allow_html=True)
    
    current_sport = bind_input("sport_type")
    is_racket_sport = current_sport in ["Tennis", "Racket Sports (Squash/Padel)"]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("4.1. Explosive Power")
        v_chest_pass = st.number_input("Chest Pass Med-Ball (m)", 1.0, 25.0, value=bind_input("p_chest_pass"))
        v_oh_throw = st.number_input("Overhead Throw Med-Ball (m)", 1.0, 30.0, value=bind_input("p_overhead_throw"))
        v_fh_throw = st.number_input("Forehand Med-Ball Throw (m)", 0.0, 30.0, value=bind_input("p_forehand_throw"), disabled=not is_racket_sport)
        v_bh_throw = st.number_input("Backhand Med-Ball Throw (m)", 0.0, 30.0, value=bind_input("p_backhand_throw"), disabled=not is_racket_sport)
        v_cmj = st.number_input("Countermovement Jump (CMJ) (cm)", 10.0, 100.0, value=bind_input("p_cmj"))
        v_horiz_uni_l = st.number_input("Horizontal Jump Left (cm)", 20.0, 250.0, value=bind_input("p_horiz_jump_uni_l"))
        v_horiz_uni_r = st.number_input("Horizontal Jump Right (cm)", 20.0, 250.0, value=bind_input("p_horiz_jump_uni_r"))

    with c2:
        st.subheader("4.2. Speed & Agility")
        v_sprint5m = st.number_input("5m First-Step Sprint (sec)", 0.5, 3.0, value=bind_input("s_sprint5m"))
        v_sprint10m = st.number_input("10m Sprint (sec)", 1.0, 4.0, value=bind_input("s_sprint10m"))
        v_7x7 = st.number_input("7 x 7 Agility Drill (sec)", 5.0, 30.0, value=bind_input("s_7x7"))
        v_tdrill = st.number_input("T-Drill Agility (sec)", 5.0, 25.0, value=bind_input("s_tdrill"))
        v_1000m = st.number_input("1000m Sprint (sec)", 120.0, 600.0, value=bind_input("s_sprint1000m"))

    with c3:
        st.subheader("4.3. Muscular & Capacity")
        v_pushups = st.number_input("Max Push-Ups (1 Min)", 0, 120, value=bind_input("c_pushups"))
        v_pullups = st.number_input("Max Pull-Ups", 0, 60, value=bind_input("c_pullups"))
        v_cooper = st.number_input("12-Min Cooper Test (m)", 500, 5000, value=bind_input("c_cooper"))

    vo2max = round((v_cooper - 504.9) / 44.73, 1)
    horiz_asym = round(abs(v_horiz_uni_l - v_horiz_uni_r) / max(v_horiz_uni_l, v_horiz_uni_r) * 100, 1)
    
    st.info(f"📊 **Calculated Diagnostics**: VO2Max: `{vo2max} mL/kg/min` | Single-Leg Asymmetry: `{horiz_asym}%`")

    update_state("p_chest_pass", v_chest_pass)
    update_state("p_overhead_throw", v_oh_throw)
    update_state("p_forehand_throw", v_fh_throw)
    update_state("p_backhand_throw", v_bh_throw)
    update_state("p_cmj", v_cmj)
    update_state("p_horiz_jump_uni_l", v_horiz_uni_l)
    update_state("p_horiz_jump_uni_r", v_horiz_uni_r)
    update_state("s_sprint5m", v_sprint5m)
    update_state("s_sprint10m", v_sprint10m)
    update_state("s_7x7", v_7x7)
    update_state("s_tdrill", v_tdrill)
    update_state("s_sprint1000m", v_1000m)
    update_state("c_pushups", v_pushups)
    update_state("c_pullups", v_pullups)
    update_state("c_cooper", v_cooper)

    if st.button("💾 SAVE SNAPSHOT TO HISTORICAL DATABASE"):
        rec = st.session_state.form_data.copy()
        rec["vo2max"] = vo2max
        rec["horiz_asymmetry"] = horiz_asym
        st.session_state.athlete_records.append(rec)
        st.success(f"✅ Baseline snapshot saved for {rec['athlete_name']} on {rec['assessment_date']}!")

# ------------------------------------------
# MODULE 5: SAVED RECORDS
# ------------------------------------------
elif active_module == "📈 5. Saved Records & Historical Progress":
    st.markdown("<div class='banner-header'>📈 Saved Assessment Records & Multi-Month Tracking</div>", unsafe_allow_html=True)
    if len(st.session_state.athlete_records) == 0:
        st.info("ℹ️ No saved snapshots found. Complete assessments in Module 4 and click 'Save Snapshot'.")
    else:
        df = pd.DataFrame(st.session_state.athlete_records)
        st.dataframe(df, use_container_width=True)

# ------------------------------------------
# MODULE 6: ADAPTIVE PROGRAM GENERATOR
# ------------------------------------------
elif active_module == "🚀 6. ADAPTIVE PROGRAM GENERATOR":
    st.markdown("<div class='banner-header'>🚀 Dynamic Multi-Month Periodization Engine</div>", unsafe_allow_html=True)
    
    engine = AthleteIQEngine(st.session_state.form_data, equipment_selected)

    # Base Metrics Display
    rx_m1 = engine.generate_program_for_month(1)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Force-Velocity Profile", rx_m1["FV Profile"])
    m2.metric("Max Aerobic Speed", f"{rx_m1['MAS']} m/s")
    m3.metric("Bilateral Asymmetry", f"{rx_m1['Asymmetry']}%")
    m4.metric("Upper Capacity", rx_m1["Upper Capacity"])

    if rx_m1["Alerts"]:
        st.subheader("⚠️ Clinical & Performance Engine Alerts")
        for alert in rx_m1["Alerts"]:
            st.warning(alert)

    st.markdown(f"**Auto-Prescribed Volume Scaling:** `{rx_m1['Volume Schema']}`")
    st.markdown("---")

    m_tabs = st.tabs([f"🗓️ MONTH {m}" for m in range(1, plan_months + 1)])

    for m_idx, m_tab in enumerate(m_tabs):
        m_num = m_idx + 1
        rx_month = engine.generate_program_for_month(m_num)
        
        with m_tab:
            m_title, _ = get_macrocycle_phase(m_num, 1)
            st.subheader(f"📌 {m_title}")
            
            w_tabs = st.tabs([f"Week {w}" for w in range(1, 5)])

            for w_idx, w_tab in enumerate(w_tabs):
                w_num = w_idx + 1
                _, p_info = get_macrocycle_phase(m_num, w_num)
                
                with w_tab:
                    st.caption(f"**Phase Focus**: {p_info['phase']} | **Target Load & Volume**: {p_info['intensity']} ({p_info['sets']})")

                    plan_data = [
                        {
                            "Category": "1. Postural Corrective Prep",
                            "Exercise": rx_month["Corrective Prep"],
                            "Prescription": "2 Sets x 10 Reps / Side",
                            "Target Intensity": "Controlled Mobility",
                            "Tempo": "2-1-2-0"
                        },
                        {
                            "Category": "2. Neuromuscular Power / Speed",
                            "Exercise": rx_month["Power Exercise"],
                            "Prescription": "4 Sets x 3 Reps" if w_num != 4 else "2 Sets x 3 Reps",
                            "Target Intensity": "Maximal Explosive Intent",
                            "Tempo": "X-0-X-0"
                        },
                        {
                            "Category": "3. Lower Body Primary Lift",
                            "Exercise": rx_month["Lower Exercise"],
                            "Prescription": p_info["sets"],
                            "Target Intensity": p_info["intensity"],
                            "Tempo": p_info["tempo"]
                        },
                        {
                            "Category": "4. Upper Body Primary Press",
                            "Exercise": rx_month["Upper Exercise"],
                            "Prescription": p_info["sets"],
                            "Target Intensity": p_info["intensity"],
                            "Tempo": p_info["tempo"]
                        },
                        {
                            "Category": "5. Energy System Development (ESD)",
                            "Exercise": rx_month["ESD Protocol"],
                            "Prescription": "12 Minutes Total Work",
                            "Target Intensity": "Zone 4 (120% MAS)",
                            "Tempo": "Dynamic Shuttle"
                        }
                    ]
                    st.dataframe(pd.DataFrame(plan_data), use_container_width=True)
