import json
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

# ============================================================
# ATHLETE-IQ PERFORMANCE ENGINE v2
# A single-file Streamlit application.
# ============================================================

st.set_page_config(
    page_title="Athlete-IQ Performance Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# UI / HUD STYLE
# -----------------------------
st.markdown(
    """
<style>
.stApp {
    background:
        linear-gradient(rgba(15,23,42,.94), rgba(2,6,23,.98)),
        url('https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1920&auto=format&fit=crop');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: #f8fafc;
    font-family: Inter, system-ui, sans-serif;
}
.metric-card {
    background: rgba(30,41,59,.84);
    border: 1px solid rgba(56,189,248,.35);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 20px rgba(14,165,233,.16);
    backdrop-filter: blur(10px);
    margin-bottom: 15px;
}
.banner-header {
    background: linear-gradient(90deg,#6366f1 0%,#a855f7 50%,#ec4899 100%);
    padding: 14px 22px;
    border-radius: 10px;
    color: white;
    font-weight: 800;
    font-size: 1.3rem;
    margin-top: 10px;
    margin-bottom: 18px;
    box-shadow: 0 4px 15px rgba(168,85,247,.35);
}
.hud-card {
    background: rgba(15,23,42,.82);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 12px;
    backdrop-filter: blur(8px);
}
.small-label {
    color:#94a3b8;
    font-size:.76rem;
    text-transform:uppercase;
    letter-spacing:.08em;
    font-weight:800;
}
.big-value {font-size:1.5rem;font-weight:800;color:#f8fafc;}
.good {color:#34d399;font-weight:800;}
.warn {color:#fbbf24;font-weight:800;}
.bad {color:#fb7185;font-weight:800;}
.info {color:#38bdf8;font-weight:800;}
[data-testid="stMetricLabel"],[data-testid="stMetricValue"]{white-space:normal!important;word-break:break-word!important;overflow-wrap:break-word!important;}
div[data-testid="stMetricValue"]>div{font-size:1.1rem!important;line-height:1.25!important;}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# DATA MODELS
# ============================================================
@dataclass
class Exercise:
    id: str
    name: str
    pattern: str
    quality: List[str]
    equipment: List[str]
    level: str
    plane: str = "Sagittal"
    stability: str = "Free Weight"
    impact: str = "Low"
    complexity: int = 1
    fatigue: int = 2
    unilateral: bool = False
    sport_tags: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    regressions: List[str] = field(default_factory=list)
    progressions: List[str] = field(default_factory=list)
    contraindication_flags: List[str] = field(default_factory=list)
    tempo_strength: str = "2-0-1-0"
    tempo_hypertrophy: str = "3-1-1-0"
    tempo_power: str = "X-0-X-0"


@dataclass
class AthleteProfile:
    name: str
    age: int
    sex: str
    height_cm: float
    weight_kg: float
    sport: str
    position: str
    goal: str
    secondary_goal: str
    season: str
    competition_days: int
    team_days: int
    team_minutes: int
    gym_days_available: int
    training_years: float
    equipment: List[str]
    injuries: List[str]
    pain_present: bool
    pain_score: int
    sleep_hours: float
    readiness: int
    stress: int
    soreness: int
    rom_ankle: float
    rom_hip_flex: float
    rom_hip_ext: float
    rom_tspine: float
    rom_shoulder: float
    cmj: float
    broad_jump: float
    sprint_5m: float
    sprint_10m: float
    cod: float
    squat_1rm: float
    bench_1rm: float
    ohp_1rm: float
    pullups: int
    pushups: int
    cooper_m: float
    left_jump: float
    right_jump: float
    notes: str = ""


# ============================================================
# EXERCISE DATABASE
# ============================================================
E = [
    Exercise("sq01","Barbell Back Squat","Squat",["Strength","Hypertrophy"],["Barbells & Plates"],"Intermediate",fatigue=4,prerequisites=["ankle"],sport_tags=["Soccer","Basketball","Rugby/American Football"]),
    Exercise("sq02","Heel-Elevated Goblet Squat","Squat",["Strength","Hypertrophy"],["Dumbbells"],"Beginner",fatigue=2,sport_tags=["General Fitness","Basketball"]),
    Exercise("sq03","Front Squat","Squat",["Strength","Hypertrophy"],["Barbells & Plates"],"Intermediate",fatigue=4,prerequisites=["ankle"],sport_tags=["Rugby/American Football","Track & Field (Sprints/Jumps)"]),
    Exercise("sq04","Hack Squat","Squat",["Strength","Hypertrophy"],["Cable Systems & Selectorized"],"Intermediate",stability="Stable/Machine",fatigue=3),
    Exercise("sq05","Split Squat","Squat",["Strength","Hypertrophy","Stability"],["Dumbbells","Bodyweight"],"Beginner",unilateral=True,fatigue=2,sport_tags=["Soccer","Basketball","Tennis"]),
    Exercise("sq06","Rear-Foot-Elevated Split Squat","Squat",["Strength","Hypertrophy","Stability"],["Dumbbells","Barbells & Plates"],"Intermediate",unilateral=True,fatigue=3,sport_tags=["Soccer","Basketball"]),
    Exercise("hg01","Trap-Bar Deadlift","Hinge",["Strength","Power"],["Barbells & Plates"],"Intermediate",fatigue=4,sport_tags=["Rugby/American Football","Track & Field (Sprints/Jumps)"]),
    Exercise("hg02","Romanian Deadlift","Hinge",["Strength","Hypertrophy"],["Barbells & Plates","Dumbbells"],"Intermediate",fatigue=3,tags=["Hamstring"],sport_tags=["Soccer","Basketball","Tennis"]),
    Exercise("hg03","Hip Thrust","Hinge",["Strength","Hypertrophy"],["Barbells & Plates","Dumbbells"],"Beginner",fatigue=2,sport_tags=["Soccer","Track & Field (Sprints/Jumps)"]),
    Exercise("hg04","Single-Leg RDL","Hinge",["Strength","Stability"],["Dumbbells","Kettlebells"],"Intermediate",unilateral=True,fatigue=2,sport_tags=["Soccer","Tennis","Basketball"]),
    Exercise("hp01","Barbell Bench Press","Horizontal Push",["Strength","Hypertrophy"],["Barbells & Plates"],"Intermediate",fatigue=3,sport_tags=["Rugby/American Football","Combat Sports (MMA/Boxing)"]),
    Exercise("hp02","Dumbbell Bench Press","Horizontal Push",["Dumbbells"],["Dumbbells"],"Beginner",fatigue=3,sport_tags=["General Fitness","Basketball"]),
    Exercise("hp03","Push-Up","Horizontal Push",["Strength Endurance","Hypertrophy"],["Bodyweight"],"Beginner",stability="Bodyweight CKC",fatigue=2),
    Exercise("hp04","Ring Push-Up","Horizontal Push",["Strength","Stability"],["Rigs & Suspension (TRX/Wood Rings)"],"Intermediate",stability="Bodyweight CKC",fatigue=2,sport_tags=["Volleyball","Tennis"]),
    Exercise("op01","Standing Overhead Press","Overhead Press",["Strength","Hypertrophy"],["Barbells & Plates","Dumbbells"],"Intermediate",fatigue=3,prerequisites=["shoulder"]),
    Exercise("op02","Half-Kneeling Landmine Press","Overhead Press",["Strength","Power","Stability"],["Barbells & Plates"],"Beginner",stability="Unilateral/Unstable",fatigue=2,sport_tags=["Combat Sports (MMA/Boxing)","Tennis"]),
    Exercise("pl01","Pull-Up","Pull",["Strength","Hypertrophy"],["Bodyweight","Rigs & Suspension (TRX/Wood Rings)"],"Intermediate",stability="Bodyweight CKC",fatigue=3,prerequisites=["shoulder"]),
    Exercise("pl02","Lat Pulldown","Pull",["Strength","Hypertrophy"],["Cable Systems & Selectorized"],"Beginner",stability="Stable/Machine",fatigue=2),
    Exercise("pl03","Chest-Supported Row","Pull",["Strength","Hypertrophy"],["Dumbbells","Cable Systems & Selectorized"],"Beginner",fatigue=2),
    Exercise("pl04","TRX Row","Pull",["Strength","Strength Endurance","Stability"],["Rigs & Suspension (TRX/Wood Rings)"],"Beginner",fatigue=2),
    Exercise("pw01","Medicine-Ball Rotational Throw","Power",["Power","Rotational Power"],["Medicine & Slam Balls"],"Beginner",plane="Transverse",fatigue=2,sport_tags=["Tennis","Racket Sports (Squash/Padel)","Combat Sports (MMA/Boxing)"]),
    Exercise("pw02","Countermovement Jump","Power",["Power","Elasticity"],["Bodyweight"],"Beginner",impact="Moderate",fatigue=2,sport_tags=["Basketball","Volleyball","Soccer"]),
    Exercise("pw03","Box Jump","Power",["Power","Elasticity"],["Plyo Boxes & Agility Ladders"],"Beginner",impact="Moderate",fatigue=2,sport_tags=["Basketball","Soccer"]),
    Exercise("pw04","Sled Acceleration","Power",["Acceleration","Power"],["Sleds & Prowler"],"Intermediate",fatigue=3,sport_tags=["Soccer","Rugby/American Football"]),
    Exercise("pw05","Kettlebell Swing","Power",["Power","Hinge Velocity"],["Kettlebells"],"Beginner",fatigue=2),
    Exercise("pw06","Med-Ball Chest Pass","Power",["Power"],["Medicine & Slam Balls"],"Beginner",fatigue=1),
    Exercise("st01","Lateral Bound","Power","Bodyweight" if False else ["Power","COD","Elasticity"],["Bodyweight"],"Intermediate",plane="Frontal",impact="Moderate",unilateral=True,fatigue=2,sport_tags=["Soccer","Basketball","Tennis"]),
    Exercise("ac01","AirBike Intervals","Conditioning",["Aerobic","Anaerobic"],["Ergometers (AirBike/Rower/SkiErg)"],"Beginner",fatigue=3),
    Exercise("ac02","Rower Intervals","Conditioning",["Aerobic","Anaerobic"],["Ergometers (AirBike/Rower/SkiErg)"],"Beginner",fatigue=3),
    Exercise("ac03","Shuttle Intervals","Conditioning",["Acceleration","COD","Anaerobic"],["Bodyweight","Plyo Boxes & Agility Ladders"],"Intermediate",fatigue=4,sport_tags=["Soccer","Basketball","Tennis"]),
    Exercise("co01","Dead Bug","Core",["Stability"],["Bodyweight"],"Beginner",fatigue=1),
    Exercise("co02","Pallof Press","Core",["Stability","Anti-Rotation"],["Cable Systems & Selectorized"],"Beginner",plane="Transverse",fatigue=1),
    Exercise("co03","Side Plank","Core",["Stability"],["Bodyweight"],"Beginner",plane="Frontal",fatigue=1),
    Exercise("mo01","Ankle Dorsiflexion Mobilization","Mobility",["Mobility"],["Bodyweight"],"Beginner",fatigue=1),
    Exercise("mo02","T-Spine Rotation","Mobility",["Mobility"],["Bodyweight"],"Beginner",plane="Transverse",fatigue=1),
    Exercise("pr01","Nordic Hamstring Curl","Accessory",["Strength","Hamstring"],["Bodyweight"],"Intermediate",fatigue=3,sport_tags=["Soccer","Rugby/American Football"]),
    Exercise("pr02","Calf Isometric","Accessory",["Strength","Tendon"],["Bodyweight","Dumbbells"],"Beginner",fatigue=1),
    Exercise("pr03","Band External Rotation","Accessory",["Stability"],["Bodyweight"],"Beginner",fatigue=1,sport_tags=["Tennis","Volleyball","Racket Sports (Squash/Padel)"]),
]

EXERCISES = {x.id: x for x in E}

SPORT_DEMANDS = {
    "General Fitness": {"Strength": .25,"Hypertrophy": .30,"Power": .10,"Acceleration": .05,"COD": .05,"Aerobic": .15,"Stability": .10},
    "Soccer": {"Strength": .15,"Hypertrophy": .05,"Power": .15,"Acceleration": .20,"COD": .15,"Aerobic": .20,"Stability": .10},
    "Basketball": {"Strength": .15,"Hypertrophy": .05,"Power": .20,"Acceleration": .15,"COD": .15,"Aerobic": .15,"Stability": .15},
    "Tennis": {"Strength": .10,"Hypertrophy": .05,"Power": .20,"Acceleration": .10,"COD": .15,"Aerobic": .15,"Stability": .25},
    "Racket Sports (Squash/Padel)": {"Strength": .10,"Hypertrophy": .05,"Power": .20,"Acceleration": .15,"COD": .15,"Aerobic": .15,"Stability": .20},
    "Volleyball": {"Strength": .15,"Hypertrophy": .05,"Power": .25,"Acceleration": .10,"COD": .10,"Aerobic": .10,"Stability": .25},
    "Combat Sports (MMA/Boxing)": {"Strength": .15,"Hypertrophy": .05,"Power": .25,"Acceleration": .10,"COD": .05,"Aerobic": .20,"Stability": .20},
    "Track & Field (Sprints/Jumps)": {"Strength": .20,"Hypertrophy": .05,"Power": .25,"Acceleration": .25,"COD": .05,"Aerobic": .05,"Stability": .15},
    "Rugby/American Football": {"Strength": .25,"Hypertrophy": .10,"Power": .20,"Acceleration": .15,"COD": .10,"Aerobic": .10,"Stability": .10},
}

SPORT_POSITIONS = {
    "General Fitness": ["General"],
    "Soccer": ["Goalkeeper","Center Back","Full Back","Midfielder","Winger","Striker"],
    "Basketball": ["Guard","Wing","Forward","Center"],
    "Tennis": ["Singles","Doubles"],
    "Racket Sports (Squash/Padel)": ["Singles","Doubles"],
    "Volleyball": ["Setter","Outside Hitter","Opposite","Middle Blocker","Libero"],
    "Combat Sports (MMA/Boxing)": ["Boxing","MMA","Kickboxing","Wrestling","BJJ"],
    "Track & Field (Sprints/Jumps)": ["100m/200m","400m","Long Jump","High Jump"],
    "Rugby/American Football": ["Forward/Front Seven","Back/Skill Position","Hybrid"],
}

EQUIPMENT = [
    "Barbells & Plates","Dumbbells","Kettlebells","Rigs & Suspension (TRX/Wood Rings)",
    "Sleds & Prowler","Medicine & Slam Balls","Cable Systems & Selectorized",
    "Ergometers (AirBike/Rower/SkiErg)","Plyo Boxes & Agility Ladders","Bodyweight"
]

# ============================================================
# SESSION STATE / UTILITIES
# ============================================================
DEFAULTS = {
    "name":"New Athlete","age":25,"sex":"Male","height_cm":180.0,"weight_kg":80.0,
    "sport":"General Fitness","position":"General","goal":"General Fitness","secondary_goal":"Strength",
    "season":"General / No Competition","competition_days":0,"team_days":0,"team_minutes":0,
    "gym_days_available":3,"training_years":2.0,"equipment":EQUIPMENT.copy(),
    "injuries":[],"pain_present":False,"pain_score":0,"sleep_hours":7.5,"readiness":80,"stress":3,"soreness":3,
    "rom_ankle":35.0,"rom_hip_flex":120.0,"rom_hip_ext":15.0,"rom_tspine":45.0,"rom_shoulder":170.0,
    "cmj":40.0,"broad_jump":210.0,"sprint_5m":1.10,"sprint_10m":1.80,"cod":10.5,
    "squat_1rm":100.0,"bench_1rm":70.0,"ohp_1rm":45.0,"pullups":8,"pushups":30,"cooper_m":2400,
    "left_jump":105.0,"right_jump":104.0,"notes":"",
}

if "athlete" not in st.session_state:
    st.session_state.athlete = DEFAULTS.copy()
if "profiles" not in st.session_state:
    st.session_state.profiles = {}
if "records" not in st.session_state:
    st.session_state.records = []
if "generated_plan" not in st.session_state:
    st.session_state.generated_plan = None


def update(key, value):
    st.session_state.athlete[key] = value


def profile_from_state() -> AthleteProfile:
    d = st.session_state.athlete
    return AthleteProfile(**d)


def load_profile(name: str):
    st.session_state.athlete = dict(st.session_state.profiles[name])
    st.session_state.generated_plan = None


def save_profile():
    name = st.session_state.athlete["name"].strip() or "Unnamed Athlete"
    st.session_state.profiles[name] = dict(st.session_state.athlete)


def bmi(a: AthleteProfile) -> float:
    h = a.height_cm / 100
    return a.weight_kg / (h*h) if h else 0


def relative_strength(load: float, weight: float) -> float:
    return load / max(weight, 1)


def asymmetry(left: float, right: float) -> float:
    return abs(left-right) / max(abs(left), abs(right), 1e-9) * 100


def readiness_score(a: AthleteProfile) -> float:
    sleep = np.clip((a.sleep_hours - 5) / 4, 0, 1) * 100
    fatigue_component = 100 - (a.stress * 10 + a.soreness * 8)
    score = 0.45*a.readiness + 0.30*sleep + 0.25*np.clip(fatigue_component,0,100)
    if a.pain_present:
        score -= a.pain_score * 5
    return float(np.clip(score,0,100))


def training_level(years: float) -> str:
    if years < 1: return "Beginner"
    if years < 4: return "Intermediate"
    if years < 8: return "Advanced"
    return "Elite"


def phase_for(a: AthleteProfile, week: int) -> str:
    if a.season == "In-Season / Competition":
        return ["Maintenance","Strength Retention","Power Maintenance","Deload / Taper"][week-1]
    if a.goal in ["Max Strength","Strength"]:
        return ["Accumulation","Intensification","Realization","Deload"][week-1]
    if a.goal in ["Power","Sport Performance"]:
        return ["Capacity","Strength-Speed","Power","Deload"][week-1]
    if a.goal == "Hypertrophy":
        return ["Volume","Overload","Peak Volume","Deload"][week-1]
    return ["Base","Build","Progress","Deload"][week-1]


def week_loading(a: AthleteProfile, week: int) -> Dict[str, object]:
    level = training_level(a.training_years)
    base = {
        "Beginner": {1:(3,8,0.65),2:(3,8,0.70),3:(3,7,0.72),4:(2,8,0.55)},
        "Intermediate": {1:(3,8,0.70),2:(4,7,0.75),3:(4,5,0.82),4:(2,6,0.60)},
        "Advanced": {1:(4,6,0.75),2:(4,5,0.80),3:(5,3,0.87),4:(2,5,0.62)},
        "Elite": {1:(4,5,0.78),2:(5,4,0.83),3:(5,2,0.90),4:(2,4,0.65)},
    }[level][week]
    sets,reps,pct = base
    if a.goal == "Hypertrophy":
        reps = {1:10,2:8,3:8,4:8}[week]
        pct = {1:.65,2:.70,3:.75,4:.55}[week]
        sets = {1:3,2:4,3:4,4:2}[week]
    elif a.goal in ["Power","Sport Performance"]:
        reps = {1:5,2:4,3:3,4:3}[week]
        pct = {1:.65,2:.70,3:.75,4:.50}[week]
        sets = {1:3,2:3,3:4,4:2}[week]
    if a.season == "In-Season / Competition":
        sets = min(sets,2 if week != 3 else 3)
        pct = {1:.70,2:.75,3:.80,4:.55}[week]
    rpe = {1:7,2:7.5,3:8,4:6}[week]
    return {"sets":sets,"reps":reps,"pct":pct,"rpe":rpe}


def test_profile(a: AthleteProfile) -> Dict[str,float]:
    rs = relative_strength(a.squat_1rm,a.weight_kg)
    rb = relative_strength(a.bench_1rm,a.weight_kg)
    asym = asymmetry(a.left_jump,a.right_jump)
    # These are intentionally heuristic classifications, not clinical norms.
    scores = {
        "Strength": np.clip(rs/2.0*100,0,100),
        "Upper Strength": np.clip(rb/1.25*100,0,100),
        "Power": np.clip(a.cmj/60*100,0,100),
        "Acceleration": np.clip((2.2-a.sprint_10m)/1.2*100,0,100),
        "COD": np.clip((13.0-a.cod)/4.0*100,0,100),
        "Aerobic": np.clip((a.cooper_m-1600)/1800*100,0,100),
        "Stability": np.clip(100-asym*4,0,100),
        "Mobility": np.mean([
            np.clip(a.rom_ankle/40*100,0,100),
            np.clip(a.rom_hip_flex/130*100,0,100),
            np.clip(a.rom_hip_ext/20*100,0,100),
            np.clip(a.rom_tspine/50*100,0,100),
            np.clip(a.rom_shoulder/175*100,0,100),
        ]),
    }
    return {k:round(float(v),1) for k,v in scores.items()}


def priorities(a: AthleteProfile) -> Dict[str,float]:
    sport = SPORT_DEMANDS.get(a.sport, SPORT_DEMANDS["General Fitness"])
    scores = test_profile(a)
    mapping = {"Strength":"Strength","Power":"Power","Acceleration":"Acceleration","COD":"COD","Aerobic":"Aerobic","Stability":"Stability"}
    deficits = {k:max(0,100-scores.get(k,50)) for k in mapping}
    weighted = {k: deficits[k]*sport.get(k,0.1) for k in deficits}
    # Goal boost
    goal_map = {"Max Strength":"Strength","Strength":"Strength","Hypertrophy":"Strength","Power":"Power","Speed":"Acceleration","Agility":"COD","Endurance":"Aerobic","Sport Performance":"Power","Fat Loss":"Aerobic","General Fitness":"Strength"}
    if goal_map.get(a.goal) in weighted:
        weighted[goal_map[a.goal]] *= 1.35
    total = sum(weighted.values()) or 1
    return {k:round(v/total*100,1) for k,v in sorted(weighted.items(), key=lambda x:x[1], reverse=True)}


def mobility_flags(a: AthleteProfile) -> List[str]:
    flags=[]
    if a.rom_ankle < 30: flags.append("Limited ankle dorsiflexion")
    if a.rom_hip_flex < 120: flags.append("Limited hip flexion")
    if a.rom_hip_ext < 15: flags.append("Limited hip extension")
    if a.rom_tspine < 45: flags.append("Limited thoracic rotation")
    if a.rom_shoulder < 165: flags.append("Limited shoulder flexion")
    return flags


def injury_flags(a: AthleteProfile) -> List[str]:
    out=[]
    if a.pain_present:
        out.append("Pain currently reported: exercise selection must be conservative and symptom-led.")
    for x in a.injuries:
        out.append(f"Reported injury/history: {x}")
    return out


def exercise_allowed(ex: Exercise, a: AthleteProfile) -> bool:
    if not any(eq in a.equipment for eq in ex.equipment):
        return False
    level_order={"Beginner":0,"Intermediate":1,"Advanced":2,"Elite":3}
    if level_order[training_level(a.training_years)] + 1 < level_order[ex.level]:
        return False
    if "ankle" in ex.prerequisites and a.rom_ankle < 25:
        return False
    if "shoulder" in ex.prerequisites and a.rom_shoulder < 155:
        return False
    if a.pain_present:
        text=" ".join(a.injuries).lower()
        if "shoulder" in text and ex.pattern in ["Overhead Press"]:
            return False
        if ("knee" in text or "acl" in text) and ex.impact == "High":
            return False
        if "hamstring" in text and "Hamstring" in ex.tags:
            return False
    return True


def score_exercise(ex: Exercise, a: AthleteProfile, priority: Dict[str,float]) -> float:
    score=0.0
    if a.sport in ex.sport_tags: score += 20
    if "General Fitness" in ex.sport_tags: score += 4
    level_order={"Beginner":0,"Intermediate":1,"Advanced":2,"Elite":3}
    gap=level_order[training_level(a.training_years)]-level_order[ex.level]
    score += max(-5,min(8,gap*3))
    if ex.unilateral and asymmetry(a.left_jump,a.right_jump)>=8: score += 15
    if a.rom_ankle<30 and "ankle" not in ex.prerequisites: score += 4
    if a.rom_shoulder<165 and ex.pattern != "Overhead Press": score += 3
    for q in ex.quality:
        score += priority.get(q,0)*0.15
    score -= ex.fatigue * (max(0, 80-readiness_score(a))/100) * 8
    if a.season == "In-Season / Competition" and ex.fatigue >= 4: score -= 8
    return score


def select_exercises(a: AthleteProfile, pattern: str, priority: Dict[str,float], n: int=1) -> List[Exercise]:
    candidates=[x for x in E if x.pattern==pattern and exercise_allowed(x,a)]
    candidates.sort(key=lambda x:score_exercise(x,a,priority), reverse=True)
    return candidates[:n]


def estimate_load(arm: float, pct: float) -> float:
    if arm <= 0: return 0
    return round(arm*pct/2.5)*2.5


def conditioning(a: AthleteProfile, priority: Dict[str,float], week: int) -> Dict[str,str]:
    r=readiness_score(a)
    if r < 45:
        return {"mode":"Recovery aerobic","work":"15–25 min easy cyclical work","intensity":"RPE 4–5/10","reason":"Low readiness"}
    if a.season == "In-Season / Competition":
        return {"mode":"Low-fatigue conditioning","work":"8–12 × 15 s work / 45 s easy","intensity":"RPE 6–7/10","reason":"Protect competition readiness"}
    if priority.get("Aerobic",0) >= 25:
        return {"mode":"Aerobic intervals","work":f"6–10 × 2 min work / 1 min easy","intensity":"RPE 7/10","reason":"Aerobic development priority"}
    if priority.get("COD",0) >= 22:
        return {"mode":"COD intervals","work":"6–10 × 15–20 s shuttle / 40–60 s recovery","intensity":"High quality, full technical control","reason":"Change-of-direction priority"}
    return {"mode":"Mixed conditioning","work":"8–12 × 30 s work / 30–60 s recovery","intensity":"RPE 7–8/10","reason":"General work capacity"}


SPORT_WARMUPS = {
    "Racket Sports (Squash/Padel)": ["Wrist & Forearm Dynamic Rotations", "Thoracic Spine Openers (Transverse Plane)", "Lateral Multi-Directional Shuttles"],
    "Tennis": ["Wrist & Forearm Dynamic Rotations", "Thoracic Spine Openers (Transverse Plane)", "Lateral Multi-Directional Shuttles"],
    "Soccer": ["Dynamic Hamstring Sweeps & Adductor Mobilization", "Ankle Mobility & Single-Leg Balance Hops", "Multi-Directional Change of Direction (COD) Shuttles"],
    "Basketball": ["Ankle Mobility & Achilles Stiffness Hops", "Drop Landings (Landing Mechanics Prep)", "Reactive Vertical Jump Hops"],
    "Volleyball": ["Scapular Y-T-W Wall Slides & Rotator Cuff Band Mobilization", "Ankle Stiffness Hops & Depth Landings", "Multi-Planar Lateral Bounds & Block Hops"],
    "Combat Sports (MMA/Boxing)": ["Thoracic Dynamic Windmills & Neck Isometric Prep", "Hip 90/90 Flow & Dynamic Adductor Sweeps", "Explosive Banded Rotational Punches & Footwork Shuttles"],
    "Track & Field (Sprints/Jumps)": ["A-Skips, B-Skips & Ankling Drills", "Dynamic Hamstring Decompression Sweeps", "Banded Glute Activation & Sprint Acceleration Wall Drills"],
    "Rugby/American Football": ["Neck Isometric Holds & Upper Trapezius Prep", "Dynamic Groin / Adductor Mobilization", "Resisted Sled / Banded Acceleration Starts"],
    "General Fitness": ["World's Greatest Stretch", "Band Pull-Aparts & Glute Bridges", "Bodyweight Squats & Arm Circles"],
}

def render_program_card(category, exercise_name, prescription, intensity, tempo, plane, tier, accent):
    html = f"""<div style='background:rgba(15,23,42,.82);border:1px solid rgba(255,255,255,.08);border-left:5px solid {accent};border-radius:12px;padding:16px;margin-bottom:12px;backdrop-filter:blur(10px);'>
<div style='font-size:.75rem;font-weight:800;color:{accent};text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;'>{category}</div>
<div style='font-size:1.15rem;font-weight:700;color:#fff;margin-bottom:10px;line-height:1.45;word-break:break-word;'>{exercise_name}</div>
<div style='display:flex;flex-wrap:wrap;gap:8px;'>
<span style='background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:#f8fafc;padding:5px 10px;border-radius:7px;font-size:.8rem;font-weight:600;'>📌 {prescription}</span>
<span style='background:rgba(56,189,248,.10);border:1px solid rgba(56,189,248,.30);color:#38bdf8;padding:5px 10px;border-radius:7px;font-size:.8rem;font-weight:600;'>⚡ {intensity}</span>
<span style='background:rgba(168,85,247,.10);border:1px solid rgba(168,85,247,.30);color:#a855f7;padding:5px 10px;border-radius:7px;font-size:.8rem;font-weight:600;'>⏱️ OPEX Tempo (E-P-C-P): {tempo}</span>
<span style='background:rgba(236,72,153,.10);border:1px solid rgba(236,72,153,.30);color:#ec4899;padding:5px 10px;border-radius:7px;font-size:.8rem;font-weight:600;'>📐 Plane: {plane}</span>
<span style='background:rgba(16,185,129,.10);border:1px solid rgba(16,185,129,.30);color:#10b981;padding:5px 10px;border-radius:7px;font-size:.8rem;font-weight:600;'>🛡️ Tier: {tier}</span>
</div></div>"""
    st.markdown(html, unsafe_allow_html=True)

def render_session_cards(a, session, week):
    exercises=session["exercises"]
    power=next((x for x in exercises if x["exercise"].pattern=="Power"),None)
    lower=next((x for x in exercises if x["exercise"].pattern in ["Squat","Hinge"]),None)
    upper=next((x for x in exercises if x["exercise"].pattern in ["Horizontal Push","Overhead Press"]),None)
    extra=next((x for x in exercises if x["exercise"].pattern in ["Pull","Accessory","Core"]),None)
    warmups=SPORT_WARMUPS.get(a.sport,SPORT_WARMUPS["General Fitness"])
    render_program_card("1. Postural & ROM Corrective Prep",f"Sport Prep ({a.sport}): {' + '.join(warmups)}","2 Sets x 10 Reps / Side","Controlled Mobility","2-1-2-0","Sagittal / Multi-planar","Corrective / Activation","#38bdf8")
    if power:
        ex=power["exercise"]; render_program_card("2. Neuromuscular Power / Speed",ex.name,f"{power['sets']} Sets x {power['reps']} Reps","Maximal Explosive Intent",power["tempo"],ex.plane,ex.stability,"#ec4899")
    if lower:
        ex=lower["exercise"]; render_program_card("3. Lower Body Primary Lift",ex.name,f"{lower['sets']} Sets x {lower['reps']} Reps",lower["intensity"],lower["tempo"],ex.plane,ex.stability,"#6366f1")
    if upper:
        ex=upper["exercise"]; render_program_card("4. Upper Body Primary Press",ex.name,f"{upper['sets']} Sets x {upper['reps']} Reps",upper["intensity"],upper["tempo"],ex.plane,ex.stability,"#a855f7")
    cond=conditioning(a,priorities(a),week)
    render_program_card("5. Dynamic MetCon / ESD Protocol",cond["mode"],cond["work"],f"Selected Mode: {cond['intensity']}","Dynamic Pace","Multi-planar","Metabolic Conditioning","#10b981")
    if extra:
        ex=extra["exercise"]; render_program_card("6. Supplemental / Core",ex.name,f"{extra['sets']} Sets x {extra['reps']} Reps",extra["intensity"],extra["tempo"],ex.plane,ex.stability,"#f59e0b")

def build_week(a: AthleteProfile, week: int) -> List[Dict[str,object]]:
    priority=priorities(a)
    load=week_loading(a,week)
    days=max(1,min(a.gym_days_available,4))
    if a.season=="In-Season / Competition": days=min(days,3)
    if readiness_score(a)<40: days=min(days,2)
    sessions=[]
    pattern_days={
        1:["Power","Squat","Horizontal Push","Pull","Core"],
        2:["Hinge","Horizontal Push","Pull","Core"],
        3:["Power","Squat","Hinge","Overhead Press","Core"],
        4:["Hinge","Horizontal Push","Pull","Accessory"],
    }
    for day in range(1,days+1):
        patterns=pattern_days[day]
        exercises=[]
        for pat in patterns:
            if pat=="Accessory":
                opts=[x for x in E if x.pattern in ["Accessory","Core"] and exercise_allowed(x,a)]
                opts.sort(key=lambda x:score_exercise(x,a,priority),reverse=True)
                if opts: exercises.append(opts[0])
            else:
                opts=select_exercises(a,pat,priority)
                if opts: exercises.append(opts[0])
        session=[]
        for idx,ex in enumerate(exercises):
            if ex.pattern=="Power":
                sets=3 if week<4 else 2; reps=3
                pct=None; tempo=ex.tempo_power; intensity="Maximal intent; stop if velocity/technique drops"
            elif ex.pattern in ["Core","Accessory"]:
                sets=2; reps=10 if ex.pattern=="Accessory" else 8
                pct=None; tempo="2-1-2-0"; intensity="RPE 6–7"
            else:
                sets=load["sets"] if idx<3 else max(2,load["sets"]-1)
                reps=load["reps"] if idx<3 else max(6,min(12,load["reps"]+2))
                if ex.pattern=="Squat": pct=load["pct"]
                elif ex.pattern in ["Horizontal Push","Overhead Press"]: pct=load["pct"]
                else: pct=max(.55,load["pct"]-.05)
                tempo=ex.tempo_hypertrophy if a.goal=="Hypertrophy" else ex.tempo_strength
                intensity=f"{int(round(pct*100))}% estimated 1RM / RPE {load['rpe']}"
            if readiness_score(a)<60:
                sets=max(1,sets-1)
                intensity += " | Readiness adjustment: -1 set"
            session.append({"exercise":ex,"sets":sets,"reps":reps,"pct":pct,"tempo":tempo,"intensity":intensity})
        sessions.append({"day":day,"focus":phase_for(a,week),"exercises":session})
    return sessions


def build_macrocycle(a: AthleteProfile, months: int=3) -> Dict[int,Dict[int,List[Dict[str,object]]]]:
    return {m:{w:build_week(a,w) for w in range(1,5)} for m in range(1,months+1)}


def explain_plan(a: AthleteProfile) -> List[str]:
    p=priorities(a); top=list(p.items())[:3]
    reasons=[f"Top physical priorities: {', '.join(k for k,_ in top)}."]
    if a.season=="In-Season / Competition": reasons.append("In-season mode caps gym frequency and reduces fatigue cost.")
    if readiness_score(a)<60: reasons.append("Current readiness is below the normal training target, so volume is reduced.")
    if asymmetry(a.left_jump,a.right_jump)>=8: reasons.append("Meaningful left/right jump asymmetry increases the selection score for unilateral work.")
    if mobility_flags(a): reasons.append("ROM flags are used to exclude exercises with higher prerequisite demands.")
    return reasons

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("## ⚡ ATHLETE-IQ")
st.sidebar.caption("Assessment → Decision Engine → Program → Adaptation")

module=st.sidebar.radio("Jump to Module",[
    "1. Athlete Profile",
    "2. Load, Injury & Readiness",
    "3. Movement & ROM",
    "4. Performance Testing",
    "5. Analysis Dashboard",
    "6. Adaptive Program Generator",
    "7. Data / Profiles",
])

plan_months=st.sidebar.select_slider("Macrocycle Horizon",options=[1,2,3],value=2,format_func=lambda x:f"{x}-Month Block")

# ============================================================
# HEADER
# ============================================================
st.markdown("<h1 style='text-align:center;color:#38bdf8;font-weight:900;margin-bottom:0'>ATHLETE-IQ PERFORMANCE ENGINE</h1>",unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#a855f7;font-weight:700;font-size:1.1rem'>Coach Ahmed Youssef • Assessment-Driven Training System</p>",unsafe_allow_html=True)

# ============================================================
# MODULE 1
# ============================================================
if module=="1. Athlete Profile":
    st.markdown('<div class="banner-header">Athlete Profile & Goal Architecture</div>',unsafe_allow_html=True)
    d=st.session_state.athlete
    c1,c2,c3=st.columns(3)
    with c1:
        update("name",st.text_input("Athlete Name",d["name"]))
        update("age",st.number_input("Age",12,80,d["age"]))
        update("sex",st.selectbox("Sex",["Male","Female","Other"],index=["Male","Female","Other"].index(d["sex"])))
        update("height_cm",st.number_input("Height (cm)",min_value=120.0,max_value=230.0,value=float(d["height_cm"]),step=0.5))
        update("weight_kg",st.number_input("Weight (kg)",min_value=30.0,max_value=250.0,value=float(d["weight_kg"]),step=0.5))
    with c2:
        sport_options=list(SPORT_DEMANDS.keys())
        sport=st.selectbox("Sport / Discipline",sport_options,index=sport_options.index(d["sport"]))
        update("sport",sport)
        positions=SPORT_POSITIONS[sport]
        pos=st.selectbox("Position / Event",positions,index=positions.index(d["position"]) if d["position"] in positions else 0)
        update("position",pos)
        goals=["General Fitness","Fat Loss","Hypertrophy","Strength","Max Strength","Power","Speed","Agility","Endurance","Sport Performance"]
        update("goal",st.selectbox("Primary Goal",goals,index=goals.index(d["goal"])))
        update("secondary_goal",st.selectbox("Secondary Goal",goals,index=goals.index(d["secondary_goal"])))
    with c3:
        seasons=["General / No Competition","Off-Season","Pre-Season","In-Season / Competition","Taper / Peak"]
        update("season",st.selectbox("Season / Calendar Phase",seasons,index=seasons.index(d["season"])))
        update("training_years",st.number_input("Strength & Conditioning Experience (years)",min_value=0.0,max_value=30.0,value=float(d["training_years"]),step=0.5))
        update("gym_days_available",st.slider("Gym Days Available / Week",1,7,d["gym_days_available"]))
        update("equipment",st.multiselect("Available Equipment",EQUIPMENT,default=d["equipment"]))
    st.markdown("---")
    st.info(f"Training level detected: **{training_level(d['training_years'])}** • BMI: **{bmi(profile_from_state()):.1f}** • Position: **{d['position']}**")
    update("notes",st.text_area("Coach Notes",d["notes"],height=120))

# ============================================================
# MODULE 2
# ============================================================
elif module=="2. Load, Injury & Readiness":
    st.markdown('<div class="banner-header">External Load • Injury Screening • Readiness</div>',unsafe_allow_html=True)
    d=st.session_state.athlete
    c1,c2,c3=st.columns(3)
    with c1:
        update("team_days",st.slider("Team / Sport Sessions per Week",0,14,d["team_days"]))
        update("team_minutes",st.number_input("Average Team Session Minutes",0,300,d["team_minutes"]))
        update("competition_days",st.slider("Competitions / Matches per Week",0,4,d["competition_days"]))
        team_hours=d["team_days"]*d["team_minutes"]/60
        st.metric("Team Exposure",f"{team_hours:.1f} h/week")
    with c2:
        update("sleep_hours",st.slider("Sleep (hours)",min_value=3.0,max_value=12.0,value=float(d["sleep_hours"]),step=0.5))
        update("readiness",st.slider("Subjective Readiness",0,100,d["readiness"]))
        update("stress",st.slider("Stress",0,10,d["stress"]))
        update("soreness",st.slider("Soreness",0,10,d["soreness"]))
    with c3:
        update("pain_present",st.checkbox("Pain currently present",d["pain_present"]))
        update("pain_score",st.slider("Pain score (0–10)",0,10,d["pain_score"]))
        injuries=["Knee / ACL / MCL / Patellar","Hamstring","Ankle / Achilles","Shoulder / Rotator Cuff","Low Back","Groin / Adductor","Quadriceps","Wrist / Elbow","Other"]
        update("injuries",st.multiselect("Current / recent injury history",injuries,default=d["injuries"]))
    r=readiness_score(profile_from_state())
    st.markdown(f'<div class="hud-card"><span class="small-label">Calculated Readiness</span><div class="big-value">{r:.0f}/100</div></div>',unsafe_allow_html=True)
    if d["pain_present"] and d["pain_score"]>=5:
        st.error("High pain reported. The generator will not attempt to diagnose or rehabilitate the condition. Use conservative training and obtain qualified clinical assessment when appropriate.")

# ============================================================
# MODULE 3
# ============================================================
elif module=="3. Movement & ROM":
    st.markdown('<div class="banner-header">Movement Quality • ROM Matrix • Screening Flags</div>',unsafe_allow_html=True)
    d=st.session_state.athlete
    c1,c2,c3,c4,c5=st.columns(5)
    with c1: update("rom_ankle",st.number_input("Ankle Dorsiflexion (°)",min_value=0.0,max_value=50.0,value=float(d["rom_ankle"]),step=0.5))
    with c2: update("rom_hip_flex",st.number_input("Hip Flexion (°)",min_value=50.0,max_value=150.0,value=float(d["rom_hip_flex"]),step=0.5))
    with c3: update("rom_hip_ext",st.number_input("Hip Extension (°)",min_value=0.0,max_value=40.0,value=float(d["rom_hip_ext"]),step=0.5))
    with c4: update("rom_tspine",st.number_input("T-Spine Rotation (°)",min_value=10.0,max_value=70.0,value=float(d["rom_tspine"]),step=0.5))
    with c5: update("rom_shoulder",st.number_input("Shoulder Flexion (°)",min_value=90.0,max_value=180.0,value=float(d["rom_shoulder"]),step=0.5))
    st.markdown("---")
    st.subheader("Screening flags")
    flags=mobility_flags(profile_from_state())
    if flags:
        for f in flags: st.warning(f)
    else: st.success("No ROM flags triggered by the current thresholds.")
    st.caption("ROM thresholds in this application are screening heuristics, not diagnoses or universal clinical norms.")

# ============================================================
# MODULE 4
# ============================================================
elif module=="4. Performance Testing":
    st.markdown('<div class="banner-header">Power • Speed • Strength • Capacity Testing</div>',unsafe_allow_html=True)
    d=st.session_state.athlete
    c1,c2,c3=st.columns(3)
    with c1:
        update("cmj",st.number_input("Countermovement Jump (cm)",min_value=5.0,max_value=100.0,value=float(d["cmj"]),step=0.5))
        update("broad_jump",st.number_input("Broad Jump (cm)",min_value=50.0,max_value=350.0,value=float(d["broad_jump"]),step=1.0))
        update("left_jump",st.number_input("Single-Leg Jump Left (cm)",min_value=5.0,max_value=250.0,value=float(d["left_jump"]),step=0.5))
        update("right_jump",st.number_input("Single-Leg Jump Right (cm)",min_value=5.0,max_value=250.0,value=float(d["right_jump"]),step=0.5))
    with c2:
        update("sprint_5m",st.number_input("5m Sprint (s)",min_value=0.5,max_value=4.0,value=float(d["sprint_5m"]),step=0.01))
        update("sprint_10m",st.number_input("10m Sprint (s)",min_value=1.0,max_value=5.0,value=float(d["sprint_10m"]),step=0.01))
        update("cod",st.number_input("COD / T-Drill (s)",min_value=5.0,max_value=30.0,value=float(d["cod"]),step=0.01))
        update("cooper_m",st.number_input("12-Min Cooper Distance (m)",min_value=500.0,max_value=5000.0,value=float(d["cooper_m"]),step=50.0))
    with c3:
        update("squat_1rm",st.number_input("Back Squat 1RM (kg)",min_value=20.0,max_value=350.0,value=float(d["squat_1rm"]),step=2.5))
        update("bench_1rm",st.number_input("Bench Press 1RM (kg)",min_value=20.0,max_value=250.0,value=float(d["bench_1rm"]),step=2.5))
        update("ohp_1rm",st.number_input("Overhead Press 1RM (kg)",min_value=10.0,max_value=180.0,value=float(d["ohp_1rm"]),step=1.0))
        update("pullups",st.number_input("Max Pull-Ups",0,60,d["pullups"]))
        update("pushups",st.number_input("Max Push-Ups",0,120,d["pushups"]))
    a=profile_from_state(); scores=test_profile(a); p=priorities(a)
    st.markdown("---")
    cols=st.columns(4)
    vals=[("Relative Squat",relative_strength(a.squat_1rm,a.weight_kg)),("Relative Bench",relative_strength(a.bench_1rm,a.weight_kg)),("Jump Asymmetry",asymmetry(a.left_jump,a.right_jump)),("Estimated VO₂max",(a.cooper_m-504.9)/44.73)]
    for c,(lab,val) in zip(cols,vals): c.metric(lab,f"{val:.2f}" if "VO₂" not in lab else f"{val:.1f}")
    st.caption("Performance classifications are heuristic coaching outputs and should not be treated as validated clinical diagnoses.")

# ============================================================
# MODULE 5
# ============================================================
elif module=="5. Analysis Dashboard":
    st.markdown('<div class="banner-header">Athlete Intelligence Dashboard</div>',unsafe_allow_html=True)
    a=profile_from_state(); scores=test_profile(a); p=priorities(a); r=readiness_score(a)
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Training Level",training_level(a.training_years))
    c2.metric("Readiness",f"{r:.0f}/100")
    c3.metric("Squat / BW",f"{relative_strength(a.squat_1rm,a.weight_kg):.2f}×")
    c4.metric("Jump Asymmetry",f"{asymmetry(a.left_jump,a.right_jump):.1f}%")
    c5.metric("Sport",a.sport)
    st.markdown("---")
    left,right=st.columns(2)
    with left:
        st.subheader("Physical Quality Scores")
        df=pd.DataFrame({"Quality":list(scores.keys()),"Score":list(scores.values())})
        st.bar_chart(df.set_index("Quality"))
    with right:
        st.subheader("Training Priority Matrix")
        pdf=pd.DataFrame({"Quality":list(p.keys()),"Priority":list(p.values())})
        st.dataframe(pdf,use_container_width=True,hide_index=True)
    st.markdown("---")
    st.subheader("Why the engine is making these decisions")
    for reason in explain_plan(a): st.write("• "+reason)
    st.subheader("Flags")
    for f in injury_flags(a)+mobility_flags(a): st.warning(f)

# ============================================================
# MODULE 6
# ============================================================
elif module=="6. Adaptive Program Generator":
    st.markdown('<div class="banner-header">Adaptive Multi-Month Program Generator</div>',unsafe_allow_html=True)
    a=profile_from_state()
    if st.button("⚡ GENERATE / REFRESH PROGRAM",type="primary"):
        st.session_state.generated_plan=build_macrocycle(a,plan_months)
    if st.session_state.generated_plan is None:
        st.info("Complete the assessment modules, then generate the program.")
    else:
        p=priorities(a); r=readiness_score(a)
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Readiness",f"{r:.0f}/100")
        c2.metric("Top Priority",next(iter(p)))
        c3.metric("Gym Days",a.gym_days_available)
        c4.metric("Season",a.season)
        for m in range(1,plan_months+1):
            with st.expander(f"MONTH {m} — {phase_for(a,1)} / Progressive Block",expanded=(m==1)):
                tabs=st.tabs([f"Week {w}" for w in range(1,5)])
                for w,tab in enumerate(tabs,1):
                    with tab:
                        load=week_loading(a,w); st.markdown(f"**Phase:** {phase_for(a,w)}  |  **Loading:** {load['sets']}×{load['reps']} @ {load['pct']*100:.0f}% estimated 1RM  |  **Target RPE:** {load['rpe']}")
                        for session in st.session_state.generated_plan[m][w]:
                            st.markdown(f"<div class='banner-header' style='font-size:1.05rem;'>DAY {session['day']} • {session['focus']}</div>",unsafe_allow_html=True)
                            render_session_cards(a,session,w)
                            st.markdown("---")
        st.warning("This is a coaching/programming engine, not a medical diagnostic or rehabilitation system. Pain, acute injury, or unexplained symptoms require appropriate professional assessment.")

# ============================================================
# MODULE 7
# ============================================================
elif module=="7. Data / Profiles":
    st.markdown('<div class="banner-header">Profiles • Historical Snapshots • Export</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("💾 Save Current Profile"):
            save_profile(); st.success("Profile saved in this Streamlit session.")
    with c2:
        if st.button("📸 Save Assessment Snapshot"):
            rec=dict(st.session_state.athlete)
            rec["timestamp"]=datetime.now().isoformat(timespec="seconds")
            rec["readiness_score"]=readiness_score(profile_from_state())
            rec["squat_relative"]=relative_strength(profile_from_state().squat_1rm,profile_from_state().weight_kg)
            rec["jump_asymmetry"]=asymmetry(profile_from_state().left_jump,profile_from_state().right_jump)
            st.session_state.records.append(rec)
            st.success("Snapshot saved.")
    with c3:
        if st.button("🧹 Clear Session Records"):
            st.session_state.records=[]; st.session_state.profiles={}; st.success("Session records cleared.")
    st.markdown("---")
    if st.session_state.profiles:
        names=list(st.session_state.profiles.keys())
        selected=st.selectbox("Saved Profiles",names)
        c1,c2=st.columns(2)
        if c1.button("Load Selected Profile"):
            load_profile(selected); st.success(f"Loaded {selected}"); st.rerun()
        if c2.button("Delete Selected Profile"):
            del st.session_state.profiles[selected]; st.rerun()
    else:
        st.info("No profiles saved in this session.")
    if st.session_state.records:
        df=pd.DataFrame(st.session_state.records)
        st.subheader("Historical Assessment Records")
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button("⬇️ Download CSV",df.to_csv(index=False),"athlete_iq_history.csv","text/csv")
    payload=json.dumps(st.session_state.athlete,default=str,indent=2)
    st.download_button("⬇️ Export Current Athlete JSON",payload,"athlete_iq_profile.json","application/json")

# ============================================================
# FOOTER / SAFETY
# ============================================================
st.markdown("---")
st.caption("Athlete-IQ v2 • Rule-based coaching software. Screening thresholds and performance classifications are heuristic unless explicitly validated. This application does not diagnose, prescribe medical treatment, or replace qualified clinical assessment.")
