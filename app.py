import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ==========================================
# 1. PAGE CONFIG & CUSTOM STYLING (HUD Styling)
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
        padding: 14px 22px;
        border-radius: 10px;
        color: white;
        font-weight: 800;
        font-size: 1.3rem;
        margin-top: 10px;
        margin-bottom: 18px;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    .sfma-sub {
        font-size: 0.82rem;
        color: #38bdf8;
        font-weight: 600;
        margin-top: -10px;
        margin-bottom: 8px;
    }
    /* Prevent Text Truncation in Streamlit Metric Labels & Value Containers */
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        white-space: normal !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.1rem !important;
        line-height: 1.25 !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. OBJECT-ORIENTED DATA STRUCTURES
# ==========================================

@dataclass
class MobilityProfile:
    ankle_dorsiflexion_deg: float = 35.0
    overhead_flexion_deg: float = 170.0
    hip_extension_deg: float = 15.0
    hip_flexion_deg: float = 120.0
    tspine_rotation_deg: float = 45.0

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
    equipment_type: str
    prerequisites: List[str]
    month_block: int
    fallback_exercise: str = ""
    fallback_equipment: str = ""
    hypertrophy_tempo: str = "3-1-1-0"
    power_tempo: str = "X-0-X-0"


# ==========================================
# 3. EXERCISE DATABASE & SPORT WARMUPS
# ==========================================

EXERCISE_DATABASE = [
    # --- SQUAT PATTERN ---
    Exercise("sq01", "Barbell Back Squat", "Squat", "Barbells & Plates", ["ankle_dorsiflexion"], 1, "Goblet Squat", "Dumbbells", "4-1-1-0", "X-0-X-0"),
    Exercise("sq02", "Heel-Elevated Goblet Squat", "Squat", "Dumbbells", [], 1, "Bodyweight Heel-Elevated Squat", "Bodyweight", "3-1-1-0", "X-0-X-0"),
    Exercise("sq03", "Barbell Front Squat", "Squat", "Barbells & Plates", ["ankle_dorsiflexion"], 2, "Double KB Front Squat", "Kettlebells", "3-1-1-0", "X-0-X-0"),
    Exercise("sq04", "Machine Hack Squat", "Squat", "Cable Systems & Selectorized", [], 2, "Banded Hack Squat", "Resistance Bands", "3-1-1-0", "X-0-X-0"),
    Exercise("sq05", "Seated Leg Press", "Squat", "Cable Systems & Selectorized", [], 3, "Banded Leg Press Resistance", "Resistance Bands", "3-1-1-0", "X-0-X-0"),
    Exercise("sq06", "Safety Bar Zercher Squat", "Squat", "Barbells & Plates", ["ankle_dorsiflexion"], 3, "Zercher DB Squat", "Dumbbells", "3-1-1-0", "X-0-X-0"),

    # --- HORIZONTAL PUSH PATTERN ---
    Exercise("hp01", "Flat Barbell Bench Press", "Horizontal Push", "Barbells & Plates", [], 1, "Dumbbell Floor Press", "Dumbbells", "3-1-1-0", "X-0-X-0"),
    Exercise("hp02", "Incline Dumbbell Bench Press", "Horizontal Push", "Dumbbells", [], 2, "Incline Push-Up", "Bodyweight", "3-1-1-0", "X-0-X-0"),
    Exercise("hp03", "Seated Chest Press Machine", "Horizontal Push", "Cable Systems & Selectorized", [], 3, "Banded Chest Press", "Resistance Bands", "3-1-1-0", "X-0-X-0"),
    Exercise("hp04", "Weighted Ring Push-Up", "Horizontal Push", "Rigs & Suspension (TRX/Wood Rings)", [], 1, "Deficit Push-Up", "Bodyweight", "3-1-1-0", "X-0-X-0"),

    # --- POWER / SPEED PATTERN ---
    Exercise("pw01", "Medicine Ball Rotational Launch", "Power", "Medicine & Slam Balls", [], 1, "Banded Rotational Punch", "Resistance Bands", "2-0-X-0", "X-0-X-0"),
    Exercise("pw02", "Heavy Trap-Bar Jump Squat", "Power", "Barbells & Plates", [], 2, "Dumbbell Jump Squat", "Dumbbells", "2-0-X-0", "X-0-X-0"),
    Exercise("pw03", "Plyometric Box Jumps", "Power", "Plyo Boxes & Agility Ladders", [], 3, "Tuck Jumps", "Bodyweight", "1-0-X-0", "X-0-X-0"),
    Exercise("pw04", "Sled Acceleration Starts", "Power", "Sleds & Prowler", [], 1, "Banded Sprint Resisted Starts", "Resistance Bands", "1-0-X-0", "X-0-X-0")
]

SPORT_WARMUPS = {
    "Racket Sports (Squash/Padel)": [
        "Wrist & Forearm Dynamic Rotations",
        "Thoracic Spine Openers (Transverse Plane)",
        "Lateral Multi-Directional Shuttles"
    ],
    "Tennis": [
        "Wrist & Forearm Dynamic Rotations",
        "Thoracic Spine Openers (Transverse Plane)",
        "Lateral Multi-Directional Shuttles"
    ],
    "Soccer": [
        "Dynamic Hamstring Sweeps & Adductor Mobilization",
        "Ankle Mobility & Single-Leg Balance Hops",
        "Multi-Directional Change of Direction (COD) Shuttles"
    ],
    "Basketball": [
        "Ankle Mobility & Achilles Stiffness Hops",
        "Drop Landings (Landing Mechanics Prep)",
        "Reactive Vertical Jump Hops"
    ],
    "General Fitness": [
        "World's Greatest Stretch",
        "Band Pull-Aparts & Glute Bridges",
        "Bodyweight Squats & Arm Circles"
    ]
}


# ==========================================
# 4. FILTER & SELECTION ENGINE
# ==========================================

class ExerciseFilterEngine:
    def __init__(self, database: List[Exercise]):
        self.database = database

    def get_valid_exercise(self, pattern: str, month: int, athlete: AthleteProfile) -> Optional[Exercise]:
        candidates = [ex for ex in self.database if ex.pattern == pattern and ex.month_block == month]
        valid_candidates = [ex for ex in candidates if ex.equipment_type in athlete.equipment]
        
        safe_candidates = []
        for ex in valid_candidates:
            is_safe = True
            if "ankle_dorsiflexion" in ex.prerequisites and athlete.mobility.ankle_dorsiflexion_deg < 25.0:
                is_safe = False
            if "overhead_flexion" in ex.prerequisites and athlete.mobility.overhead_flexion_deg < 155.0:
                is_safe = False
            if is_safe:
                safe_candidates.append(ex)

        if safe_candidates:
            return safe_candidates[0]

        fallbacks = [
            ex for ex in self.database
            if ex.pattern == pattern 
            and ex.equipment_type in athlete.equipment
        ]
        return fallbacks[(month - 1) % len(fallbacks)] if fallbacks else None


# ==========================================
# 5. INTEGRATED ATHLETE-IQ LOGIC ENGINE
# ==========================================

class AthleteIQEngine:
    def __init__(self, data: dict, equipment: list):
        self.d = data
        self.equipment = equipment
        self.warnings = []
        
        self.mobility = MobilityProfile(
            ankle_dorsiflexion_deg=self.d.get("rom_ankle_dorsiflexion", 35.0),
            overhead_flexion_deg=self.d.get("rom_shoulder_flexion", 170.0),
            hip_extension_deg=self.d.get("rom_hip_extension", 15.0),
            hip_flexion_deg=self.d.get("rom_hip_flexion", 120.0),
            tspine_rotation_deg=self.d.get("rom_tspine_rotation", 45.0)
        )

        self.athlete = AthleteProfile(
            name=self.d.get("athlete_name", "Athlete"),
            experience_level="Intermediate",
            equipment=self.equipment,
            mobility=self.mobility,
            estimated_1rm={
                "Squat": self.d.get("s_1rm_squat", 100.0),
                "Horizontal Push": self.d.get("s_1rm_bench", 80.0),
                "Overhead Press": self.d.get("s_1rm_ohp", 50.0),
                "Hinge": self.d.get("s_1rm_squat", 100.0) * 1.25,
                "Power": 0.0
            }
        )
        self.filter_engine = ExerciseFilterEngine(EXERCISE_DATABASE)

    def calculate_mas(self) -> float:
        sprint_1000 = self.d.get("s_sprint1000m", 235.0)
        if sprint_1000 > 0:
            return round(1000.0 / sprint_1000, 2)
        cooper_m = self.d.get("c_cooper", 2500)
        return round((cooper_m / 720.0), 2)

    def evaluate_force_velocity_deficit(self) -> str:
        cmj = self.d.get("p_cmj", 42.0)
        sprint_10m = self.d.get("s_sprint10m", 1.75)
        fv_index = cmj / (sprint_10m * 10)
        if fv_index < 2.0:
            return "Force Deficient (Needs Maximal Strength)"
        elif fv_index > 2.8:
            return "Velocity Deficient (Needs High-Speed Elasticity)"
        return "Balanced Force-Velocity Profile"

    def evaluate_horizontal_asymmetry(self) -> float:
        left = self.d.get("p_horiz_jump_uni_l", 105.0)
        right = self.d.get("p_horiz_jump_uni_r", 104.0)
        return round(abs(left - right) / max(left, right, 1.0) * 100, 1)

    def evaluate_vertical_asymmetry(self) -> float:
        left = self.d.get("p_vert_jump_uni_l", 22.0)
        right = self.d.get("p_vert_jump_uni_r", 21.5)
        return round(abs(left - right) / max(left, right, 1.0) * 100, 1)

    def get_postural_corrective_prep(self, month: int) -> str:
        correctives = []
        if self.d.get("posture_foot_arch") == "Flat Foot (Pes Planus)":
            correctives.append("Short-Foot Activation & Tibialis Posterior Loading")
        if self.d.get("posture_ankle") in ["Pronated Rearfoot", "Supinated Rearfoot"] or self.mobility.ankle_dorsiflexion_deg < 25.0:
            correctives.append("Ankle Dorsiflexion Wall Mobilization & Calves Iso Holds")
        if self.d.get("posture_pelvic_tilt") == "Anterior Pelvic Tilt":
            correctives.append("Half-Kneeling Hip Flexor Deactivation & Deadbugs")
        elif self.d.get("posture_pelvic_tilt") == "Posterior Pelvic Tilt":
            correctives.append("Hamstring Mobility & Cobra Lumbar Extensions")
        if self.d.get("posture_thoracic") == "Hyper-Kyphosis" or self.mobility.tspine_rotation_deg < 35.0:
            correctives.append("Foam Roller T-Spine Extensions & Wall Angels")
        if self.d.get("posture_shoulder_pos") == "Anterior Rounded Shoulders" or self.mobility.overhead_flexion_deg < 155.0:
            correctives.append("Band Face Pulls & Scapular Y-T-W Series")
        if self.d.get("posture_knee") == "Genu Valgum (Knock-Knee)":
            correctives.append("Banded Glute Medius Monster Walks")

        if self.d.get("congenital_defects") != "None Detected":
            correctives.append(f"Protocol for {self.d.get('congenital_defects')}")

        sport = self.d.get("sport_type", "General Fitness")
        sport_warmup = " + ".join(SPORT_WARMUPS.get(sport, SPORT_WARMUPS["General Fitness"]))

        if not correctives:
            base_prep = [
                "Dynamic World's Greatest Stretch & Multi-Planar Hip Opener",
                "90/90 Hip Flow & Quadruped Thoracic Rotations",
                "Ankle Banded Distraction & Lateral Tube Walks"
            ]
            return f"Sport Prep ({sport}): {sport_warmup} | Base: {base_prep[(month - 1) % len(base_prep)]}"

        prefix = f"Block {month} Focus ({sport} Prep Included): "
        return prefix + " + ".join(correctives)

    def select_lower_compound(self, month: int) -> str:
        has_injury = self.d.get("has_injury") == "Yes"
        injury_sites = [str(x) for x in self.d.get("injury_sites", [])]

        if has_injury:
            if any("Knee" in k or "ACL" in k for k in injury_sites):
                self.warnings.append("🚨 Knee/ACL Active Injury: Knee flexion loading regressed.")
                knee_regressions = [
                    "Spanish Squat Isometric Hold (Knee-Sparing)",
                    "Terminal Knee Extension (TKE) & Step-Down Iso",
                    "Eccentric Spanish Squat to Box"
                ]
                return knee_regressions[(month - 1) % len(knee_regressions)]

            elif any("Hamstring" in k for k in injury_sites):
                self.warnings.append("🚨 Hamstring Strain: Replaced with Glute Bridge / Hip Thrust variations.")
                ham_regressions = [
                    "Barbell Glute Bridge / Cable Hip Thrust",
                    "Single-Leg Hip Thrust Isometric Hold",
                    "Banded Pull-Through & Glute March"
                ]
                return ham_regressions[(month - 1) % len(ham_regressions)]

            elif any("Lumbar" in k or "Back" in k for k in injury_sites):
                self.warnings.append("🚨 Lumbar Spine Strain: Axially unloaded movement prescribed.")
                lumbar_regressions = [
                    "Supported Dumbbell Step-Ups",
                    "Belt Squat / Cable Iso-Squat",
                    "Rear-Foot Elevated Split Squat (Supported)"
                ]
                return lumbar_regressions[(month - 1) % len(lumbar_regressions)]

        if self.d.get("overhead_squat") == "Dysfunctional Painful":
            self.warnings.append("🚨 Painful Overhead Squat: Regressed to Parallel Box Variations.")
            ohs_regressions = [
                "Supported Goblet Box Squat to Parallel",
                "Dumbbell Suitcase Squat to Bench",
                "Safety Squat Bar Box Squat"
            ]
            return ohs_regressions[(month - 1) % len(ohs_regressions)]
            
        if self.evaluate_horizontal_asymmetry() > 10.0 or self.evaluate_vertical_asymmetry() > 10.0:
            self.warnings.append(f"⚠️ Asymmetry >10%: Prescribed Unilateral Primaries.")
            unilateral_progression = [
                "Bulgarian Split Squat (Unilateral Correction)",
                "Deficit Unilateral Reverse Lunge",
                "Single-Leg Pistol Squat to Box"
            ]
            return unilateral_progression[(month - 1) % len(unilateral_progression)]

        ex = self.filter_engine.get_valid_exercise("Squat", month, self.athlete)
        if ex:
            return ex.name
        
        fallback_ex = [e for e in EXERCISE_DATABASE if e.pattern == "Squat"][0]
        self.warnings.append(f"🔄 Gear Fallback Active: Prescribed {fallback_ex.fallback_exercise}")
        return fallback_ex.fallback_exercise

    def select_upper_press(self, month: int) -> str:
        has_injury = self.d.get("has_injury") == "Yes"
        injury_sites = [str(x) for x in self.d.get("injury_sites", [])]

        if has_injury and any(k in str(injury_sites) for k in ["Shoulder", "Rotator", "Pectoralis"]):
            self.warnings.append("🚨 Upper Extremity Strain: Replaced with Neutral-Grip variations.")
            upper_regressions = [
                "Neutral-Grip Dumbbell Press",
                "Floor Dumbbell Press (Joint Angle Limited)",
                "Half-Kneeling Single-Arm DB Incline Press"
            ]
            return upper_regressions[(month - 1) % len(upper_regressions)]

        if self.d.get("shoulder") == "Dysfunctional Painful" or self.mobility.overhead_flexion_deg < 155.0:
            self.warnings.append("🚨 Shoulder Flexion Restriction: Prescribed Angled Pressing.")
            shoulder_regressions = [
                "Half-Kneeling Landmine Press",
                "Incline Neutral-Grip Dumbbell Press",
                "Standing Angled Cable Chest Press"
            ]
            return shoulder_regressions[(month - 1) % len(shoulder_regressions)]

        ex = self.filter_engine.get_valid_exercise("Horizontal Push", month, self.athlete)
        if ex:
            return ex.name
            
        fallback_ex = [e for e in EXERCISE_DATABASE if e.pattern == "Horizontal Push"][0]
        self.warnings.append(f"🔄 Gear Fallback Active: Prescribed {fallback_ex.fallback_exercise}")
        return fallback_ex.fallback_exercise

    def select_power_exercise(self, month: int) -> str:
        has_injury = self.d.get("has_injury") == "Yes"
        injury_triggers = [str(x) for x in self.d.get("injury_triggers", [])]

        if has_injury and any("Jumping" in trig or "Sprinting" in trig for trig in injury_triggers):
            self.warnings.append("🚨 High-Impact Mechanism Trigger: Regressed to Low-Impact Ballistics.")
            power_regressions = [
                "Seated Upper-Body Explosive Med-Ball Launch",
                "Tall-Kneeling Med-Ball Chest Pass",
                "Standing Cable Explosive Punch / Push"
            ]
            return power_regressions[(month - 1) % len(power_regressions)]

        ex = self.filter_engine.get_valid_exercise("Power", month, self.athlete)
        if ex:
            return ex.name
            
        fallback_ex = [e for e in EXERCISE_DATABASE if e.pattern == "Power"][0]
        self.warnings.append(f"🔄 Gear Fallback Active: Prescribed {fallback_ex.fallback_exercise}")
        return fallback_ex.fallback_exercise

    def select_esd_protocol(self, month: int) -> str:
        mas = self.calculate_mas()
        shuttle_dist = round(mas * (1.15 + (month * 0.05)) * 15, 1)

        if self.d.get("s_tdrill", 10.2) > 10.8 or self.d.get("s_7x7", 14.2) > 15.0:
            self.warnings.append("🏃 Agility Diagnostic: COD deficit detected -> Integrated COD Shuttle Drills.")
            esd_cod = [
                f"Pro-Agility Shuttle (10m-5m-10m) @ {shuttle_dist}m Target / 15s Work / 15s Rest",
                f"3-Cone Drill Shuttle Run @ {shuttle_dist}m Target / 15s Work / 15s Rest",
                f"Box COD Acceleration Shuttle @ {shuttle_dist}m Target / 15s Work / 15s Rest"
            ]
            return esd_cod[(month - 1) % len(esd_cod)]
        
        esd_linear = [
            f"15s Linear Shuttle Run @ {shuttle_dist}m Target / 15s Rest (10 Mins)",
            f"Eurofit 15s-15s Interval @ {shuttle_dist}m Target / 15s Rest (12 Mins)",
            f"Tabata MAS Micro-Intervals @ {shuttle_dist}m Target (14 Mins)"
        ]
        return esd_linear[(month - 1) % len(esd_linear)]

    def generate_program_for_month(self, month: int) -> dict:
        club_hours = self.d.get("club_days", 4) * self.d.get("club_hours_per_day", 2.0)
        vol_schema = "2 Sets / Ex (Low Vol, High Density)" if club_hours >= 10 else "4 Sets / Ex (Standard Build)"

        sq_1rm = self.athlete.estimated_1rm["Squat"]
        bench_1rm = self.athlete.estimated_1rm["Horizontal Push"]

        return {
            "Corrective Prep": self.get_postural_corrective_prep(month),
            "Lower Exercise": self.select_lower_compound(month),
            "Upper Exercise": self.select_upper_press(month),
            "Power Exercise": self.select_power_exercise(month),
            "ESD Protocol": self.select_esd_protocol(month),
            "FV Profile": self.evaluate_force_velocity_deficit(),
            "MAS": self.calculate_mas(),
            "Horiz Asymmetry": self.evaluate_horizontal_asymmetry(),
            "Vert Asymmetry": self.evaluate_vertical_asymmetry(),
            "Volume Schema": vol_schema,
            "Squat 1RM Target": sq_1rm,
            "Bench 1RM Target": bench_1rm,
            "Alerts": list(set(self.warnings))
        }


# ==========================================
# 6. SESSION STATE INITIALIZATION & HELPERS
# ==========================================

if "form_data" not in st.session_state:
    st.session_state.form_data = {
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
        "club_days": 4,
        "club_hours_per_day": 2.0,
        "has_injury": "No",
        "injury_sites": ["Knee Joint / Ligaments (ACL/MCL/Patellar)"],
        "injury_triggers": ["Jumping / Plyometrics / Landing Impact"],
        "still_affects": "No",
        "cervical": "Functional Non-Painful",
        "shoulder": "Functional Non-Painful",
        "rotation": "Functional Non-Painful",
        "flexion": "Functional Non-Painful",
        "extension": "Functional Non-Painful",
        "sl_stance": "Functional Non-Painful",
        "overhead_squat": "Functional Non-Painful",
        "posture_foot_arch": "Normal Arch",
        "posture_foot_pos": "Neutral Foot Stance",
        "posture_ankle": "Vertical Ankle Alignment",
        "posture_tibia": "Straight Tibial Alignment",
        "posture_knee": "Neutral Knee Line",
        "posture_pelvic_tilt": "Neutral Pelvis",
        "posture_lumbar": "Normal Curve",
        "posture_thoracic": "Normal Curve",
        "posture_scapula": "Symmetrical Flat",
        "posture_shoulder_lvl": "Level Shoulders",
        "posture_shoulder_pos": "Neutral Shoulder Position",
        "congenital_defects": "None Detected",
        "rom_ankle_dorsiflexion": 35.0,
        "rom_hip_flexion": 120.0,
        "rom_hip_extension": 15.0,
        "rom_tspine_rotation": 45.0,
        "rom_shoulder_flexion": 170.0,
        "p_chest_pass": 6.8,
        "p_forehand_throw": 7.2,
        "p_backhand_throw": 6.9,
        "p_overhead_throw": 8.5,
        "p_cmj": 42.0,
        "p_horiz_jump_bi": 215.0,
        "p_horiz_jump_uni_l": 105.0,
        "p_horiz_jump_uni_r": 104.0,
        "p_vert_jump_bi": 45.0,
        "p_vert_jump_uni_l": 22.0,
        "p_vert_jump_uni_r": 21.5,
        "s_1rm_squat": 110.0,
        "s_1rm_bench": 85.0,
        "s_1rm_ohp": 55.0,
        "s_sprint5m": 1.10,
        "s_sprint10m": 1.75,
        "s_7x7": 14.2,
        "s_tdrill": 10.20,
        "s_sprint1000m": 235.0,
        "c_pushups": 38,
        "c_situps": 45,
        "c_pullups": 12,
        "c_cooper": 2650
    }

if "athlete_records" not in st.session_state:
    st.session_state.athlete_records = []

if "athlete_profiles_db" not in st.session_state:
    st.session_state.athlete_profiles_db = {}

def bind_input(key):
    return st.session_state.form_data.get(key)

def update_state(key, val):
    st.session_state.form_data[key] = val

def safe_index(options_list, key):
    val = bind_input(key)
    return options_list.index(val) if val in options_list else 0

def get_macrocycle_phase(month_num: int, week_num: int, sq_1rm: float, bench_1rm: float):
    macro = {
        1: {
            "title": "Month 1: Accumulation Phase (Work Capacity & Base Build)",
            "weeks": {
                1: {"sets": "3 x 10 Reps", "intensity": f"65% 1RM (Sq: {round(sq_1rm*0.65,1)}kg, Bench: {round(bench_1rm*0.65,1)}kg)", "phase": "Base Accumulation", "tempo": "3-1-1-0"},
                2: {"sets": "4 x 8 Reps", "intensity": f"70% 1RM (Sq: {round(sq_1rm*0.70,1)}kg, Bench: {round(bench_1rm*0.70,1)}kg)", "phase": "Volume Build", "tempo": "3-1-1-0"},
                3: {"sets": "4 x 8 Reps", "intensity": f"75% 1RM (Sq: {round(sq_1rm*0.75,1)}kg, Bench: {round(bench_1rm*0.75,1)}kg)", "phase": "Overload Peak", "tempo": "3-1-1-0"},
                4: {"sets": "2 x 8 Reps", "intensity": f"60% 1RM (Sq: {round(sq_1rm*0.60,1)}kg, Bench: {round(bench_1rm*0.60,1)}kg)", "phase": "Deload & Regeneration", "tempo": "2-0-1-0"}
            }
        },
        2: {
            "title": "Month 2: Intensification Phase (Max Strength & Dynamic Force)",
            "weeks": {
                1: {"sets": "4 x 6 Reps", "intensity": f"78% 1RM (Sq: {round(sq_1rm*0.78,1)}kg, Bench: {round(bench_1rm*0.78,1)}kg)", "phase": "Strength Introduction", "tempo": "2-1-1-0"},
                2: {"sets": "4 x 5 Reps", "intensity": f"82% 1RM (Sq: {round(sq_1rm*0.82,1)}kg, Bench: {round(bench_1rm*0.82,1)}kg)", "phase": "Heavy Loading", "tempo": "2-1-1-0"},
                3: {"sets": "5 x 3 Reps", "intensity": f"88% 1RM (Sq: {round(sq_1rm*0.88,1)}kg, Bench: {round(bench_1rm*0.88,1)}kg)", "phase": "Maximal Load Peak", "tempo": "2-0-1-0"},
                4: {"sets": "2 x 5 Reps", "intensity": f"65% 1RM (Sq: {round(sq_1rm*0.65,1)}kg, Bench: {round(bench_1rm*0.65,1)}kg)", "phase": "Deload & Regeneration", "tempo": "2-0-1-0"}
            }
        },
        3: {
            "title": "Month 3: Realization Phase (Peak Power, Speed & Taper)",
            "weeks": {
                1: {"sets": "4 x 3 Reps", "intensity": f"85% 1RM (Sq: {round(sq_1rm*0.85,1)}kg, Bench: {round(bench_1rm*0.85,1)}kg)", "phase": "Power Realization", "tempo": "1-0-1-0"},
                2: {"sets": "4 x 2 Reps", "intensity": f"90% 1RM (Sq: {round(sq_1rm*0.90,1)}kg, Bench: {round(bench_1rm*0.90,1)}kg)", "phase": "Peaking Block", "tempo": "1-0-1-0"},
                3: {"sets": "3 x 2 Reps", "intensity": f"93% 1RM (Sq: {round(sq_1rm*0.93,1)}kg, Bench: {round(bench_1rm*0.93,1)}kg)", "phase": "Maximal Output Peak", "tempo": "1-0-1-0"},
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
        "⚽ 2. Club Load & Multi-Injury Diagnostics",
        "🩺 3. SFMA, Anatomical Views & ROM Matrix",
        "💥 4. Sport-Specific Assessment & 1RM Suite",
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
    st.markdown("<div class='banner-header'>📋 Athlete Demographics & Central CRUD Profile Engine</div>", unsafe_allow_html=True)
    
    st.markdown("#### 👤 Profile Management System")
    prof_col1, prof_col2, prof_col3 = st.columns([2, 1, 1])
    
    with prof_col1:
        profile_names = list(st.session_state.athlete_profiles_db.keys())
        selected_prof = st.selectbox("Load Saved Athlete Profile:", ["-- New Profile --"] + profile_names)
        
    with prof_col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("📂 Load Profile") and selected_prof != "-- New Profile --":
            st.session_state.form_data = st.session_state.athlete_profiles_db[selected_prof].copy()
            st.success(f"Loaded profile for {selected_prof}!")
            st.rerun()

    with prof_col3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Delete Profile") and selected_prof != "-- New Profile --":
            del st.session_state.athlete_profiles_db[selected_prof]
            st.warning(f"Deleted profile {selected_prof}.")
            st.rerun()

    st.markdown("---")
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

    if st.button("💾 Save Profile to Database"):
        st.session_state.athlete_profiles_db[v_name] = st.session_state.form_data.copy()
        st.success(f"Profile saved successfully for '{v_name}'!")

# ------------------------------------------
# MODULE 2: CLUB LOAD & MULTI-INJURY DIAGNOSTICS
# ------------------------------------------
elif active_module == "⚽ 2. Club Load & Multi-Injury Diagnostics":
    st.markdown("<div class='banner-header'>⚽ External Club Training Load & Multi-Injury Diagnostic Matrix</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚽ External Club Training Exposure")
        v_days = st.number_input("Club Training Days / Week", 0, 7, value=bind_input("club_days"))
        v_hours = st.number_input("Avg Session Duration (Hours)", 0.5, 5.0, value=bind_input("club_hours_per_day"))
        tot_hrs = v_days * v_hours
        update_state("club_days", v_days)
        update_state("club_hours_per_day", v_hours)

        if tot_hrs >= 10:
            st.warning(f"⚠️ High External Load ({tot_hrs} hrs/wk): S&C auto-condenses to 2 Days/Week (High Density).")
        elif tot_hrs >= 6:
            st.info(f"📊 Moderate External Load ({tot_hrs} hrs/wk): S&C auto-scales to 3 Days/Week.")
        else:
            st.success(f"✅ Low External Load ({tot_hrs} hrs/wk): S&C set to 4 Days/Week.")

    with c2:
        st.subheader("🩺 Advanced Multi-Injury Diagnostic Suite")
        inj_opts = ["No", "Yes"]
        v_has_inj = st.radio("Active / Recent Injury Present?", inj_opts, index=safe_index(inj_opts, "has_injury"), horizontal=True)
        
        all_injury_sites = [
            "Knee Joint / Ligaments (ACL/MCL/Patellar)",
            "Hamstrings Muscle Group",
            "Ankle Joint & Achilles Tendon",
            "Shoulder Joint Complex & Rotator Cuff",
            "Lumbar Facet Joint / Low Back",
            "Adductor Groin Group",
            "Quadriceps Group",
            "Wrist / Elbow Joint Complex"
        ]

        trigger_mechanisms = [
            "Jumping / Plyometrics / Landing Impact",
            "Sprinting / High-Speed Acceleration",
            "Cutting / Rapid Change of Direction",
            "Overuse / Accumulated Fatigue Load",
            "Direct Contact / Collision Traumatic"
        ]

        if v_has_inj == "Yes":
            v_sites = st.multiselect("Select All Active Injury Sites (Multi-Selection):", all_injury_sites, default=bind_input("injury_sites"))
            v_triggers = st.multiselect("Select Injury Occurrence Triggers / Mechanisms:", trigger_mechanisms, default=bind_input("injury_triggers"))
            affects = ["Yes - Active Symptoms", "No - Cleared / Asymptomatic"]
            v_affects = st.radio("Symptoms Present Currently?", affects, index=safe_index(affects, "still_affects"), horizontal=True)
        else:
            v_sites, v_triggers, v_affects = [], [], "No"
            
        update_state("has_injury", v_has_inj)
        update_state("injury_sites", v_sites)
        update_state("injury_triggers", v_triggers)
        update_state("still_affects", v_affects)

# ------------------------------------------
# MODULE 3: SFMA, ANATOMICAL VIEWS & ROM MATRIX
# ------------------------------------------
elif active_module == "🩺 3. SFMA, Anatomical Views & ROM Matrix":
    st.markdown("<div class='banner-header'>🩺 SFMA Diagnostics, Anatomical Postural Views & Joint ROM Goniometry</div>", unsafe_allow_html=True)
    
    st.subheader("1. SFMA Movement Patterns (Simplified Descriptions)")
    sfma_opts = ["Functional Non-Painful", "Dysfunctional Non-Painful", "Dysfunctional Painful"]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        v_cerv = st.selectbox("1. Cervical Spine Pattern", sfma_opts, index=safe_index(sfma_opts, "cervical"))
        st.markdown("<div class='sfma-sub'>💡 Simplified: Neck Flexibility & Head Rotation Quality</div>", unsafe_allow_html=True)
        
        v_shld = st.selectbox("2. Upper Extremity Reach", sfma_opts, index=safe_index(sfma_opts, "shoulder"))
        st.markdown("<div class='sfma-sub'>💡 Simplified: Shoulder Mobility & Overhead Reach</div>", unsafe_allow_html=True)
        
        v_rot = st.selectbox("3. Multi-Segmental Rotation", sfma_opts, index=safe_index(sfma_opts, "rotation"))
        st.markdown("<div class='sfma-sub'>💡 Simplified: Full-Body Torso & Hip Twisting Range</div>", unsafe_allow_html=True)

    with c2:
        v_flex = st.selectbox("4. Multi-Segmental Flexion", sfma_opts, index=safe_index(sfma_opts, "flexion"))
        st.markdown("<div class='sfma-sub'>💡 Simplified: Standing Forward Bend & Toe Touch Ability</div>", unsafe_allow_html=True)
        
        v_ext = st.selectbox("5. Multi-Segmental Extension", sfma_opts, index=safe_index(sfma_opts, "extension"))
        st.markdown("<div class='sfma-sub'>💡 Simplified: Standing Backward Arch & Lumbar Extension</div>", unsafe_allow_html=True)

    with c3:
        v_sls = st.selectbox("6. Single-Leg Stance Balance", sfma_opts, index=safe_index(sfma_opts, "sl_stance"))
        st.markdown("<div class='sfma-sub'>💡 Simplified: One-Legged Balance & Pelvic Stability</div>", unsafe_allow_html=True)
        
        v_ohs = st.selectbox("7. Deep Overhead Squat Pattern", sfma_opts, index=safe_index(sfma_opts, "overhead_squat"))
        st.markdown("<div class='sfma-sub'>💡 Simplified: Full Deep Squat with Arms Extended Overhead</div>", unsafe_allow_html=True)

    update_state("cervical", v_cerv)
    update_state("shoulder", v_shld)
    update_state("rotation", v_rot)
    update_state("flexion", v_flex)
    update_state("extension", v_ext)
    update_state("sl_stance", v_sls)
    update_state("overhead_squat", v_ohs)

    st.markdown("---")
    st.subheader("2. Static Postural Screening: Anterior, Posterior & Lateral Views")
    
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("**🖼️ Anterior View (Frontal Alignment)**")
        opts_arch = ["Normal Arch", "Flat Foot (Pes Planus)", "High Arch (Pes Cavus)"]
        opts_foot = ["Neutral Foot Stance", "In-Toeing (Pigeon)", "Out-Toeing (Duck)"]
        opts_knee = ["Neutral Knee Line", "Genu Valgum (Knock-Knee)", "Genu Varum (Bow-Leg)"]
        opts_shld_lvl = ["Level Shoulders", "Elevated Left Shoulder", "Elevated Right Shoulder"]
        
        v_foot_arch = st.selectbox("Foot Arch Structure", opts_arch, index=safe_index(opts_arch, "posture_foot_arch"))
        v_foot_pos = st.selectbox("Foot Alignment", opts_foot, index=safe_index(opts_foot, "posture_foot_pos"))
        v_knee = st.selectbox("Knee Line / Q-Angle", opts_knee, index=safe_index(opts_knee, "posture_knee"))
        v_shld_lvl = st.selectbox("Shoulder Symmetry", opts_shld_lvl, index=safe_index(opts_shld_lvl, "posture_shoulder_lvl"))

    with p2:
        st.markdown("**🖼️ Posterior View (Back Alignment)**")
        opts_ankle = ["Vertical Ankle Alignment", "Pronated Rearfoot", "Supinated Rearfoot"]
        opts_scap = ["Symmetrical Flat", "Left Scapular Winging", "Right Scapular Winging", "Bilateral Scapular Winging"]
        opts_congenital = ["None Detected", "Forward Head Posture (FHP)", "Idiopathic Scoliosis Curve", "Leg Length Discrepancy (LLD)"]
        
        v_ankle = st.selectbox("Rearfoot / Ankle", opts_ankle, index=safe_index(opts_ankle, "posture_ankle"))
        v_scap = st.selectbox("Scapular Alignment", opts_scap, index=safe_index(opts_scap, "posture_scapula"))
        v_congenital = st.selectbox("Spinal / Structural Defects", opts_congenital, index=safe_index(opts_congenital, "congenital_defects"))

    with p3:
        st.markdown("**🖼️ Lateral View (Side Profile)**")
        opts_pelvis = ["Neutral Pelvis", "Anterior Pelvic Tilt", "Posterior Pelvic Tilt"]
        opts_lumbar = ["Normal Curve", "Hyper-Lordosis", "Hypo-Lordosis / Flat Back"]
        opts_thoracic = ["Normal Curve", "Hyper-Kyphosis", "Flat Thoracic Spine"]
        opts_shld_pos = ["Neutral Shoulder Position", "Anterior Rounded Shoulders"]
        
        v_pelvic_tilt = st.selectbox("Pelvic Tilt Angle", opts_pelvis, index=safe_index(opts_pelvis, "posture_pelvic_tilt"))
        v_lumbar = st.selectbox("Lumbar Spine Curve", opts_lumbar, index=safe_index(opts_lumbar, "posture_lumbar"))
        v_thoracic = st.selectbox("Thoracic Spine Curve", opts_thoracic, index=safe_index(opts_thoracic, "posture_thoracic"))
        v_shld_pos = st.selectbox("Shoulder Position", opts_shld_pos, index=safe_index(opts_shld_pos, "posture_shoulder_pos"))

    update_state("posture_foot_arch", v_foot_arch)
    update_state("posture_foot_pos", v_foot_pos)
    update_state("posture_knee", v_knee)
    update_state("posture_shoulder_lvl", v_shld_lvl)
    update_state("posture_ankle", v_ankle)
    update_state("posture_scapula", v_scap)
    update_state("congenital_defects", v_congenital)
    update_state("posture_pelvic_tilt", v_pelvic_tilt)
    update_state("posture_lumbar", v_lumbar)
    update_state("posture_thoracic", v_thoracic)
    update_state("posture_shoulder_pos", v_shld_pos)

    st.markdown("---")
    st.subheader("3. Joint Maximum Range of Motion (ROM) Goniometry Matrix")
    
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 20px;">
        <svg width="280" height="100" viewBox="0 0 280 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="35" stroke="#38bdf8" stroke-width="3" fill="none"/>
            <path d="M50 15 L50 50 L75 50" stroke="#a855f7" stroke-width="3"/>
            <text x="50" y="95" fill="#f8fafc" font-size="11" text-anchor="middle">Anterior Alignment</text>
            <circle cx="140" cy="50" r="35" stroke="#38bdf8" stroke-width="3" fill="none"/>
            <path d="M140 15 L140 50 L120 70" stroke="#ec4899" stroke-width="3"/>
            <text x="140" y="95" fill="#f8fafc" font-size="11" text-anchor="middle">Posterior Screening</text>
            <circle cx="230" cy="50" r="35" stroke="#38bdf8" stroke-width="3" fill="none"/>
            <path d="M230 15 L230 85" stroke="#6366f1" stroke-width="3"/>
            <text x="230" y="95" fill="#f8fafc" font-size="11" text-anchor="middle">Lateral View</text>
        </svg>
        <div style="color: #38bdf8; font-weight: 600; font-size: 0.9rem; margin-top: 5px;">Anatomical Alignment Goniometry Vector Matrix</div>
    </div>
    """, unsafe_allow_html=True)

    r1, r2, r3, r4, r5 = st.columns(5)
    with r1:
        v_rom_ankle = st.number_input("Ankle Dorsiflexion (°)", 0.0, 50.0, value=bind_input("rom_ankle_dorsiflexion"))
        st.caption("Norm: ≥30°")
    with r2:
        v_rom_hip_flex = st.number_input("Hip Flexion (°)", 50.0, 140.0, value=bind_input("rom_hip_flexion"))
        st.caption("Norm: ≥120°")
    with r3:
        v_rom_hip_ext = st.number_input("Hip Extension (°)", 0.0, 40.0, value=bind_input("rom_hip_extension"))
        st.caption("Norm: ≥15°")
    with r4:
        v_rom_tspine = st.number_input("T-Spine Rotation (°)", 10.0, 70.0, value=bind_input("rom_tspine_rotation"))
        st.caption("Norm: ≥45°")
    with r5:
        v_rom_shld = st.number_input("Shoulder Flexion (°)", 90.0, 180.0, value=bind_input("rom_shoulder_flexion"))
        st.caption("Norm: ≥170°")

    update_state("rom_ankle_dorsiflexion", v_rom_ankle)
    update_state("rom_hip_flexion", v_rom_hip_flex)
    update_state("rom_hip_extension", v_rom_hip_ext)
    update_state("rom_tspine_rotation", v_rom_tspine)
    update_state("rom_shoulder_flexion", v_rom_shld)

# ------------------------------------------
# MODULE 4: SPORT-SPECIFIC ASSESSMENT & 1RM SUITE
# ------------------------------------------
elif active_module == "💥 4. Sport-Specific Assessment & 1RM Suite":
    st.markdown("<div class='banner-header'>💥 Power, Speed, Agility, 1RM Strength & Capacity Testing Suite</div>", unsafe_allow_html=True)
    
    current_sport = bind_input("sport_type")
    is_racket_sport = current_sport in ["Tennis", "Racket Sports (Squash/Padel)"]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("4.1. Explosive Jump & Med-Ball Power")
        v_chest_pass = st.number_input("Chest Pass Med-Ball (m)", 1.0, 25.0, value=bind_input("p_chest_pass"))
        
        if is_racket_sport:
            st.markdown("🎯 **Racquet / Rotational Athlete Metrics**")
            v_fh_throw = st.number_input("Forehand Throw Med-Ball (m)", 1.0, 30.0, value=bind_input("p_forehand_throw"))
            v_bh_throw = st.number_input("Backhand Throw Med-Ball (m)", 1.0, 30.0, value=bind_input("p_backhand_throw"))
            update_state("p_forehand_throw", v_fh_throw)
            update_state("p_backhand_throw", v_bh_throw)
            
        v_oh_throw = st.number_input("Overhead Throw Med-Ball (m)", 1.0, 30.0, value=bind_input("p_overhead_throw"))
        v_cmj = st.number_input("Countermovement Jump (CMJ) (cm)", 10.0, 100.0, value=bind_input("p_cmj"))
        
        v_horiz_bi = st.number_input("Horizontal Jump Both Legs (cm)", 50.0, 350.0, value=bind_input("p_horiz_jump_bi"))
        v_horiz_uni_l = st.number_input("Horizontal Jump Left (cm)", 20.0, 250.0, value=bind_input("p_horiz_jump_uni_l"))
        v_horiz_uni_r = st.number_input("Horizontal Jump Right (cm)", 20.0, 250.0, value=bind_input("p_horiz_jump_uni_r"))
        
        v_vert_uni_l = st.number_input("Vertical Jump Single Leg Left (cm)", 5.0, 60.0, value=bind_input("p_vert_jump_uni_l"))
        v_vert_uni_r = st.number_input("Vertical Jump Single Leg Right (cm)", 5.0, 60.0, value=bind_input("p_vert_jump_uni_r"))

    with c2:
        st.subheader("4.2. Speed & Agility Metrics")
        v_sprint5m = st.number_input("5m First-Step Sprint (sec)", 0.5, 3.0, value=bind_input("s_sprint5m"), help="Fully interactive for all sports profiles including combat sports.")
        v_sprint10m = st.number_input("10m Sprint (sec)", 1.0, 4.0, value=bind_input("s_sprint10m"), help="Fully interactive speed metric.")
        v_7x7 = st.number_input("7 x 7 Agility Drill (sec)", 5.0, 30.0, value=bind_input("s_7x7"))
        v_tdrill = st.number_input("T-Drill Agility (sec)", 5.0, 25.0, value=bind_input("s_tdrill"))
        v_1000m = st.number_input("1000m Sprint (sec)", 120.0, 600.0, value=bind_input("s_sprint1000m"))

    with c3:
        st.subheader("4.3. 1RM Max & Capacity Matrix")
        v_1rm_squat = st.number_input("1RM Max Back Squat (kg)", 20.0, 350.0, value=bind_input("s_1rm_squat"))
        v_1rm_bench = st.number_input("1RM Max Chest / Bench Press (kg)", 20.0, 250.0, value=bind_input("s_1rm_bench"))
        v_1rm_ohp = st.number_input("1RM Max Overhead Press (kg)", 10.0, 180.0, value=bind_input("s_1rm_ohp"))
        
        v_pushups = st.number_input("Max Push-Ups (1 Min)", 0, 120, value=bind_input("c_pushups"))
        v_situps = st.number_input("Max Sit-Ups (1 Min)", 0, 120, value=bind_input("c_situps"))
        v_pullups = st.number_input("Max Pull-Ups", 0, 60, value=bind_input("c_pullups"))
        v_cooper = st.number_input("12-Min Cooper Test (m)", 500, 5000, value=bind_input("c_cooper"))

    vo2max = round((v_cooper - 504.9) / 44.73, 1)
    horiz_asym = round(abs(v_horiz_uni_l - v_horiz_uni_r) / max(v_horiz_uni_l, v_horiz_uni_r) * 100, 1)
    vert_asym = round(abs(v_vert_uni_l - v_vert_uni_r) / max(v_vert_uni_l, v_vert_uni_r) * 100, 1)
    
    st.info(f"📊 **Calculated Performance Diagnostics**: VO2Max: `{vo2max} mL/kg/min` | Horizontal Asymmetry: `{horiz_asym}%` | Vertical Asymmetry: `{vert_asym}%`")

    update_state("p_chest_pass", v_chest_pass)
    update_state("p_overhead_throw", v_oh_throw)
    update_state("p_cmj", v_cmj)
    update_state("p_horiz_jump_bi", v_horiz_bi)
    update_state("p_horiz_jump_uni_l", v_horiz_uni_l)
    update_state("p_horiz_jump_uni_r", v_horiz_uni_r)
    update_state("p_vert_jump_uni_l", v_vert_uni_l)
    update_state("p_vert_jump_uni_r", v_vert_uni_r)
    update_state("s_sprint5m", v_sprint5m)
    update_state("s_sprint10m", v_sprint10m)
    update_state("s_7x7", v_7x7)
    update_state("s_tdrill", v_tdrill)
    update_state("s_sprint1000m", v_1000m)
    update_state("s_1rm_squat", v_1rm_squat)
    update_state("s_1rm_bench", v_1rm_bench)
    update_state("s_1rm_ohp", v_1rm_ohp)
    update_state("c_pushups", v_pushups)
    update_state("c_situps", v_situps)
    update_state("c_pullups", v_pullups)
    update_state("c_cooper", v_cooper)

    if st.button("💾 SAVE SNAPSHOT TO HISTORICAL DATABASE"):
        rec = st.session_state.form_data.copy()
        rec["vo2max"] = vo2max
        rec["horiz_asymmetry"] = horiz_asym
        rec["vert_asymmetry"] = vert_asym
        st.session_state.athlete_records.append(rec)
        st.success(f"✅ Full baseline snapshot saved for {rec['athlete_name']} on {rec['assessment_date']}!")

# ------------------------------------------
# MODULE 5: SAVED RECORDS & HISTORICAL PROGRESS
# ------------------------------------------
elif active_module == "📈 5. Saved Records & Historical Progress":
    st.markdown("<div class='banner-header'>📈 Saved Assessment Records & Longitudinal Progress Tracking</div>", unsafe_allow_html=True)
    
    if len(st.session_state.athlete_records) == 0:
        st.info("ℹ️ No saved snapshots found. Complete assessments in Module 4 and click 'Save Snapshot'.")
    else:
        df = pd.DataFrame(st.session_state.athlete_records)
        
        st.subheader("📊 Performance Trajectory Over Time")
        
        track_metric = st.selectbox(
            "Select Metric to Track Across Assessment Dates:",
            ["s_1rm_squat", "s_1rm_bench", "p_cmj", "vo2max", "s_sprint10m", "horiz_asymmetry"],
            format_func=lambda x: {
                "s_1rm_squat": "Squat 1RM (kg)",
                "s_1rm_bench": "Bench Press 1RM (kg)",
                "p_cmj": "CMJ Vertical Jump (cm)",
                "vo2max": "VO2 Max (mL/kg/min)",
                "s_sprint10m": "10m Sprint Time (sec)",
                "horiz_asymmetry": "Horizontal Asymmetry (%)"
            }.get(x, x)
        )
        
        if "assessment_date" in df.columns:
            chart_data = df[["assessment_date", track_metric]].copy()
            chart_data["assessment_date"] = pd.to_datetime(chart_data["assessment_date"])
            chart_data = chart_data.sort_values("assessment_date").set_index("assessment_date")
            st.line_chart(chart_data, height=280)
            
        st.markdown("---")
        st.subheader("📋 Historical Records Data Table")
        st.dataframe(df, use_container_width=True)

# ------------------------------------------
# MODULE 6: ADAPTIVE PROGRAM GENERATOR (Modern HUD Card View)
# ------------------------------------------
elif active_module == "🚀 6. ADAPTIVE PROGRAM GENERATOR":
    st.markdown("<div class='banner-header'>🚀 Dynamic Multi-Month Periodization Engine</div>", unsafe_allow_html=True)
    
    engine = AthleteIQEngine(st.session_state.form_data, equipment_selected)

    rx_m1 = engine.generate_program_for_month(1)
    
    m1, m2, m3, m4, m5 = st.columns(5)
    
    m1.metric("Force-Velocity Profile", rx_m1["FV Profile"])
    m2.metric("Max Aerobic Speed", f"{rx_m1['MAS']} m/s")
    m3.metric("Horiz Asymmetry", f"{rx_m1['Horiz Asymmetry']}%")
    m4.metric("Vert Asymmetry", f"{rx_m1['Vert Asymmetry']}%")
    m5.metric("Volume Schema", rx_m1["Volume Schema"].split("(")[0])

    if rx_m1["Alerts"]:
        st.subheader("⚠️ Clinical & Performance Engine Alerts")
        for alert in rx_m1["Alerts"]:
            st.warning(alert)

    st.markdown("---")

    m_tabs = st.tabs([f"🗓️ MONTH {m}" for m in range(1, plan_months + 1)])

    for m_idx, m_tab in enumerate(m_tabs):
        m_num = m_idx + 1
        rx_month = engine.generate_program_for_month(m_num)
        
        with m_tab:
            m_title, _ = get_macrocycle_phase(m_num, 1, rx_month["Squat 1RM Target"], rx_month["Bench 1RM Target"])
            st.subheader(f"📌 {m_title}")
            
            w_tabs = st.tabs([f"Week {w}" for w in range(1, 5)])

            for w_idx, w_tab in enumerate(w_tabs):
                w_num = w_idx + 1
                _, p_info = get_macrocycle_phase(m_num, w_num, rx_month["Squat 1RM Target"], rx_month["Bench 1RM Target"])
                
                with w_tab:
                    # Phase Header Banner Card
                    st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.7); border-left: 4px solid #38bdf8; padding: 12px 16px; border-radius: 8px; margin-bottom: 20px;">
                        <span style="color: #38bdf8; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px;">Phase Focus: {p_info['phase']}</span><br>
                        <span style="color: #f8fafc; font-size: 1rem; font-weight: 600;">🎯 Target Prescribed Loading: <span style="color: #a855f7;">{p_info['intensity']}</span> ({p_info['sets']})</span>
                    </div>
                    """, unsafe_allow_html=True)

                    plan_data = [
                        ("1. Postural & ROM Corrective Prep", rx_month["Corrective Prep"], "2 Sets x 10 Reps / Side", "Controlled Mobility", "2-1-2-0", "#38bdf8"),
                        ("2. Neuromuscular Power / Speed", rx_month["Power Exercise"], "4 Sets x 3 Reps" if w_num != 4 else "2 Sets x 3 Reps", "Maximal Explosive Intent", "X-0-X-0", "#ec4899"),
                        ("3. Lower Body Primary Lift", rx_month["Lower Exercise"], p_info["sets"], p_info["intensity"], p_info["tempo"], "#6366f1"),
                        ("4. Upper Body Primary Press", rx_month["Upper Exercise"], p_info["sets"], p_info["intensity"], p_info["tempo"], "#a855f7"),
                        ("5. Energy System Development (ESD)", rx_month["ESD Protocol"], "12 Minutes Total Work", "Zone 4 (120% MAS)", "Dynamic Shuttle", "#10b981")
                    ]

                    # Card-Based Modern Workout Grid
                    for cat, ex_name, rx_sets, intensity, tempo, accent_color in plan_data:
                        st.markdown(f"""
                        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255, 255, 255, 0.08); border-left: 5px solid {accent_color}; border-radius: 12px; padding: 16px; margin-bottom: 12px; backdrop-filter: blur(10px);">
                            <div style="font-size: 0.75rem; font-weight: 800; color: {accent_color}; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px;">
                                {cat}
                            </div>
                            <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff; margin-bottom: 10px;">
                                {ex_name}
                            </div>
                            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                <span style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12); color: #f8fafc; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;">
                                    📌 {rx_sets}
                                </span>
                                <span style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); color: #38bdf8; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;">
                                    ⚡ {intensity}
                                </span>
                                <span style="background: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.3); color: #a855f7; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;">
                                    ⏱️ OPEX Tempo (E-P-C-P): {tempo}
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
