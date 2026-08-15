import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

# ============================================================
# ATHLETE-IQ v5 — WHOLE-ATHLETE DECISION + COMPLEX TRAINING ENGINE
# Intake -> Constraints -> Screening -> Performance -> Demands
# -> Priorities -> System Allocation -> Exercise Selection
# -> Dose -> Session Sequencing -> Progression -> Rotation
# -> Feedback -> Reassessment
# ============================================================

st.set_page_config(
    page_title="Athlete-IQ Performance Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# HUD UI — preserves the v3 visual language
# ============================================================
st.markdown(
    """
<style>
.stApp{
    background:
      linear-gradient(rgba(15,23,42,.94),rgba(2,6,23,.985)),
      url('https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1920&auto=format&fit=crop');
    background-size:cover;background-position:center;background-attachment:fixed;
    color:#f8fafc;font-family:Inter,system-ui,sans-serif;
}
.banner-header{
    background:linear-gradient(90deg,#6366f1 0%,#a855f7 50%,#ec4899 100%);
    padding:14px 22px;border-radius:10px;color:#fff;font-weight:800;
    font-size:1.3rem;margin:10px 0 18px;box-shadow:0 4px 15px rgba(168,85,247,.35);
}
.hud-card,.plan-card{
    background:rgba(15,23,42,.88);border:1px solid rgba(255,255,255,.08);
    border-radius:12px;padding:16px;margin-bottom:12px;backdrop-filter:blur(10px);
}
.goal-card{
    background:linear-gradient(135deg,rgba(30,41,59,.9),rgba(15,23,42,.88));
    border:1px solid rgba(56,189,248,.28);border-radius:14px;padding:16px;margin-bottom:12px;
}
.small-label{color:#94a3b8;font-size:.76rem;text-transform:uppercase;letter-spacing:.08em;font-weight:800}
.big-value{font-size:1.5rem;font-weight:800;color:#f8fafc}
.decision-card{background:rgba(15,23,42,.82);border:1px solid rgba(56,189,248,.18);border-radius:12px;padding:13px;margin:8px 0}
.rule{color:#38bdf8;font-weight:800}
.good{color:#34d399;font-weight:800}.warn{color:#fbbf24;font-weight:800}.bad{color:#fb7185;font-weight:800}
[data-testid="stMetricLabel"],[data-testid="stMetricValue"]{white-space:normal!important;word-break:break-word!important;overflow-wrap:break-word!important}
div[data-testid="stMetricValue"]>div{font-size:1.1rem!important;line-height:1.25!important}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# TAXONOMY
# ============================================================
GOALS = [
    "Overall Development", "General Fitness", "Fat Loss", "Hypertrophy",
    "Strength", "Max Strength", "Power", "Speed", "Agility", "Endurance", "Sport Performance"
]
SECONDARY_OPTIONS = [
    "Strength", "Hypertrophy", "Max Strength", "Power", "Speed", "Agility",
    "Aerobic Capacity", "Anaerobic Capacity", "Mobility", "Stability",
    "Core / Trunk", "Plyometric Ability", "Movement Quality", "Body Composition",
    "Recovery / Work Capacity"
]
SYSTEMS = [
    "Corrective / Activation", "Mobility", "Stability / Core", "Plyometrics",
    "Acceleration / Speed", "Agility / COD", "Resistance", "Aerobic", "Anaerobic / Repeated Sprint"
]
SEASONS = ["General / No Competition", "Off-Season", "Pre-Season", "In-Season / Competition", "Taper / Peak"]

SPORT_DEMANDS = {
    "General Fitness": {"Strength":.20,"Hypertrophy":.15,"Power":.08,"Acceleration":.04,"COD":.04,"Aerobic":.20,"Anaerobic":.05,"Stability":.12,"Mobility":.12},
    "Soccer": {"Strength":.12,"Hypertrophy":.03,"Power":.14,"Acceleration":.16,"COD":.16,"Aerobic":.15,"Anaerobic":.10,"Stability":.08,"Mobility":.06},
    "Basketball": {"Strength":.13,"Hypertrophy":.03,"Power":.18,"Acceleration":.12,"COD":.15,"Aerobic":.13,"Anaerobic":.10,"Stability":.10,"Mobility":.06},
    "Tennis": {"Strength":.10,"Hypertrophy":.03,"Power":.18,"Acceleration":.09,"COD":.14,"Aerobic":.14,"Anaerobic":.10,"Stability":.13,"Mobility":.09},
    "Racket Sports (Squash/Padel)": {"Strength":.10,"Hypertrophy":.03,"Power":.18,"Acceleration":.12,"COD":.15,"Aerobic":.13,"Anaerobic":.11,"Stability":.10,"Mobility":.08},
    "Volleyball": {"Strength":.13,"Hypertrophy":.03,"Power":.22,"Acceleration":.08,"COD":.10,"Aerobic":.08,"Anaerobic":.10,"Stability":.14,"Mobility":.12},
    "Combat Sports (MMA/Boxing)": {"Strength":.14,"Hypertrophy":.03,"Power":.22,"Acceleration":.08,"COD":.06,"Aerobic":.15,"Anaerobic":.14,"Stability":.10,"Mobility":.08},
    "Track & Field (Sprints/Jumps)": {"Strength":.18,"Hypertrophy":.02,"Power":.22,"Acceleration":.22,"COD":.04,"Aerobic":.05,"Anaerobic":.08,"Stability":.10,"Mobility":.09},
    "Rugby/American Football": {"Strength":.22,"Hypertrophy":.06,"Power":.18,"Acceleration":.14,"COD":.09,"Aerobic":.08,"Anaerobic":.10,"Stability":.08,"Mobility":.05},
}
SPORT_POSITIONS = {
    "General Fitness":["General"],
    "Soccer":["Goalkeeper","Center Back","Full Back","Midfielder","Winger","Striker"],
    "Basketball":["Guard","Wing","Forward","Center"],
    "Tennis":["Singles","Doubles"],
    "Racket Sports (Squash/Padel)":["Singles","Doubles"],
    "Volleyball":["Setter","Outside Hitter","Opposite","Middle Blocker","Libero"],
    "Combat Sports (MMA/Boxing)":["Boxing","MMA","Kickboxing","Wrestling","BJJ"],
    "Track & Field (Sprints/Jumps)":["100m/200m","400m","Long Jump","High Jump"],
    "Rugby/American Football":["Forward/Front Seven","Back/Skill Position","Hybrid"],
}
EQUIPMENT = [
    "Barbells & Plates","Dumbbells","Kettlebells","Rigs & Suspension (TRX/Wood Rings)",
    "Sleds & Prowler","Medicine & Slam Balls","Cable Systems & Selectorized",
    "Ergometers (AirBike/Rower/SkiErg)","Plyo Boxes & Agility Ladders","Bands",
    "Cones / Timing Gates","Bodyweight"
]

# ============================================================
# DATA MODELS
# ============================================================
@dataclass
class Exercise:
    id: str
    name: str
    system: str
    pattern: str
    quality: List[str]
    equipment: List[str]
    level: str
    plane: str = "Sagittal"
    tier: str = "Free Weight"
    impact: str = "Low"
    fatigue: int = 2
    unilateral: bool = False
    sport_tags: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    avoid_if: List[str] = field(default_factory=list)
    regression: str = ""
    progression: str = ""
    tempo_strength: str = "2-0-1-0"
    tempo_hypertrophy: str = "3-1-1-0"
    tempo_power: str = "X-0-X-0"

@dataclass
class TrainingComplex:
    id: str
    name: str
    method: str
    primary_quality: str
    secondary_qualities: List[str]
    exercises: List[str]
    sport_tags: List[str] = field(default_factory=list)
    min_level: str = "Intermediate"
    impact: str = "Moderate"
    fatigue: int = 3
    equipment: List[str] = field(default_factory=list)
    rest_between: str = "15–30 s"
    rest_rounds: str = "2–3 min"
    notes: str = ""


@dataclass
class AthleteProfile:
    name: str
    age: int
    sex: str
    height_cm: float
    weight_kg: float
    sport: str
    position: str
    primary_goal: str
    secondary_goals: List[str]
    season: str
    competition_days: int
    team_days: int
    team_minutes: int
    gym_days_available: int
    session_minutes: int
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
    posture_anterior: Dict[str,str] = field(default_factory=dict)
    posture_lateral: Dict[str,str] = field(default_factory=dict)
    posture_posterior: Dict[str,str] = field(default_factory=dict)
    movement_screen: Dict[str,str] = field(default_factory=dict)
    forehand_throw_m: float = 0.0
    backhand_throw_m: float = 0.0
    rotational_throw_m: float = 0.0
    overhead_throw_m: float = 0.0
    weekly_sport_rpe: float = 6.0
    weekly_steps_or_activity: int = 7000
    notes: str = ""

# ============================================================
# EXERCISE / DRILL DATABASE
# ============================================================
def ex(*args, **kwargs):
    return Exercise(*args, **kwargs)

E = [
    # Corrective / activation
    ex("ca1","Glute Bridge","Corrective / Activation","Activation",["Activation","Stability"],["Bodyweight"],"Beginner",fatigue=1,regression="Isometric Glute Squeeze",progression="Single-Leg Glute Bridge"),
    ex("ca2","Band Pull-Apart","Corrective / Activation","Scapular",["Activation","Stability"],["Bands"],"Beginner",fatigue=1),
    ex("ca3","Wall Slide","Corrective / Activation","Scapular",["Mobility","Stability"],["Bodyweight"],"Beginner",fatigue=1),
    ex("ca4","Dead Bug","Corrective / Activation","Core",["Core / Trunk","Stability"],["Bodyweight"],"Beginner",fatigue=1),
    ex("ca5","Bird Dog","Corrective / Activation","Core",["Core / Trunk","Stability"],["Bodyweight"],"Beginner",fatigue=1),
    # Mobility
    ex("m1","Ankle Dorsiflexion Mobilization","Mobility","Ankle",["Mobility"],["Bodyweight"],"Beginner",fatigue=1),
    ex("m2","90/90 Hip Flow","Mobility","Hip",["Mobility","Rotation"],["Bodyweight"],"Beginner",plane="Transverse",fatigue=1),
    ex("m3","T-Spine Rotation","Mobility","T-Spine",["Mobility","Rotation"],["Bodyweight"],"Beginner",plane="Transverse",fatigue=1),
    ex("m4","World's Greatest Stretch","Mobility","Full Body",["Mobility"],["Bodyweight"],"Beginner",plane="Multi-planar",fatigue=1),
    ex("m5","Shoulder CARs","Mobility","Shoulder",["Mobility","Movement Quality"],["Bodyweight"],"Beginner",fatigue=1),
    ex("m6","Adductor Rockback","Mobility","Adductor",["Mobility"],["Bodyweight"],"Beginner",plane="Frontal",fatigue=1),
    # Stability / core
    ex("st1","Pallof Press","Stability / Core","Anti-Rotation",["Stability","Core / Trunk"],["Cable Systems & Selectorized","Bands"],"Beginner",plane="Transverse",fatigue=1),
    ex("st2","Side Plank","Stability / Core","Lateral Core",["Stability","Core / Trunk"],["Bodyweight"],"Beginner",plane="Frontal",fatigue=1),
    ex("st3","Single-Leg Balance Reach","Stability / Core","Unilateral Stability",["Stability","Movement Quality"],["Bodyweight"],"Beginner",fatigue=1,unilateral=True),
    ex("st4","Suitcase Carry","Stability / Core","Carry",["Stability","Core / Trunk","Strength"],["Dumbbells","Kettlebells"],"Beginner",plane="Frontal",fatigue=2),
    # Resistance
    ex("r1","Barbell Back Squat","Resistance","Squat",["Strength","Hypertrophy"],["Barbells & Plates"],"Intermediate",fatigue=4,prerequisites=["ankle"],sport_tags=["Soccer","Basketball","Rugby/American Football"],avoid_if=["knee","back"],regression="Goblet Squat",progression="Front Squat"),
    ex("r2","Goblet Squat","Resistance","Squat",["Strength","Hypertrophy","Movement Quality"],["Dumbbells"],"Beginner",fatigue=2,regression="Box Squat",progression="Front Squat"),
    ex("r3","Front Squat","Resistance","Squat",["Strength","Hypertrophy"],["Barbells & Plates"],"Intermediate",fatigue=4,prerequisites=["ankle"],regression="Goblet Squat",progression="Paused Front Squat"),
    ex("r4","Rear-Foot-Elevated Split Squat","Resistance","Unilateral Squat",["Strength","Stability","Hypertrophy"],["Dumbbells","Barbells & Plates"],"Intermediate",fatigue=3,unilateral=True,sport_tags=["Soccer","Basketball"],avoid_if=["knee"],regression="Split Squat",progression="Loaded RFESS"),
    ex("r5","Split Squat","Resistance","Unilateral Squat",["Strength","Stability"],["Dumbbells","Bodyweight"],"Beginner",fatigue=2,unilateral=True,regression="Assisted Split Squat",progression="RFESS"),
    ex("r6","Trap-Bar Deadlift","Resistance","Hinge",["Strength","Power"],["Barbells & Plates"],"Intermediate",fatigue=4,sport_tags=["Rugby/American Football","Track & Field (Sprints/Jumps)"],avoid_if=["back"],regression="Elevated Trap-Bar Deadlift",progression="Heavy Trap-Bar Deadlift"),
    ex("r7","Romanian Deadlift","Resistance","Hinge",["Strength","Hypertrophy"],["Barbells & Plates","Dumbbells"],"Intermediate",fatigue=3,tags=["Hamstring"],sport_tags=["Soccer","Basketball","Tennis"],avoid_if=["back","hamstring"],regression="DB RDL",progression="Single-Leg RDL"),
    ex("r8","Hip Thrust","Resistance","Hinge",["Strength","Hypertrophy"],["Barbells & Plates","Dumbbells"],"Beginner",fatigue=2,sport_tags=["Soccer","Track & Field (Sprints/Jumps)"],regression="Glute Bridge",progression="Single-Leg Hip Thrust"),
    ex("r9","Barbell Bench Press","Resistance","Horizontal Push",["Strength","Hypertrophy"],["Barbells & Plates"],"Intermediate",fatigue=3,sport_tags=["Rugby/American Football","Combat Sports (MMA/Boxing)"],avoid_if=["shoulder"],regression="DB Bench Press",progression="Paused Bench Press"),
    ex("r10","Dumbbell Bench Press","Resistance","Horizontal Push",["Strength","Hypertrophy","Stability"],["Dumbbells"],"Beginner",fatigue=3,avoid_if=["shoulder"],regression="Push-Up",progression="Single-Arm DB Press"),
    ex("r11","Push-Up","Resistance","Horizontal Push",["Strength","Hypertrophy","Strength Endurance"],["Bodyweight"],"Beginner",tier="Bodyweight CKC",fatigue=2,regression="Incline Push-Up",progression="Weighted Push-Up"),
    ex("r12","Standing Overhead Press","Resistance","Vertical Push",["Strength","Hypertrophy"],["Barbells & Plates","Dumbbells"],"Intermediate",fatigue=3,prerequisites=["shoulder"],avoid_if=["shoulder"],regression="Landmine Press",progression="Push Press"),
    ex("r13","Half-Kneeling Landmine Press","Resistance","Vertical Push",["Strength","Power","Stability"],["Barbells & Plates"],"Beginner",plane="Transverse",tier="Unilateral",fatigue=2,sport_tags=["Combat Sports (MMA/Boxing)","Tennis"],regression="Cable Press",progression="Standing Landmine Press"),
    ex("r14","Pull-Up","Resistance","Pull",["Strength","Hypertrophy"],["Bodyweight","Rigs & Suspension (TRX/Wood Rings)"],"Intermediate",tier="Bodyweight CKC",fatigue=3,prerequisites=["shoulder"],avoid_if=["shoulder"],regression="Lat Pulldown",progression="Weighted Pull-Up"),
    ex("r15","Lat Pulldown","Resistance","Pull",["Strength","Hypertrophy"],["Cable Systems & Selectorized"],"Beginner",tier="Machine",fatigue=2,regression="Band Pulldown",progression="Pull-Up"),
    ex("r16","Chest-Supported Row","Resistance","Pull",["Strength","Hypertrophy"],["Dumbbells","Cable Systems & Selectorized"],"Beginner",fatigue=2,regression="Seated Cable Row",progression="Heavy Row"),
    ex("r17","TRX Row","Resistance","Pull",["Strength","Stability","Strength Endurance"],["Rigs & Suspension (TRX/Wood Rings)"],"Beginner",fatigue=2,regression="High TRX Row",progression="Feet-Elevated TRX Row"),
    ex("r18","Nordic Hamstring Curl","Resistance","Accessory",["Strength","Hamstring","Injury Resilience"],["Bodyweight"],"Intermediate",fatigue=3,tags=["Hamstring"],sport_tags=["Soccer","Rugby/American Football"],avoid_if=["hamstring"],regression="Assisted Nordic",progression="Unassisted Nordic"),
    ex("r19","Calf Isometric","Resistance","Accessory",["Strength","Tendon"],["Bodyweight","Dumbbells"],"Beginner",fatigue=1),
    ex("r20","Band External Rotation","Resistance","Accessory",["Stability","Shoulder"],["Bands"],"Beginner",fatigue=1,sport_tags=["Tennis","Volleyball","Racket Sports (Squash/Padel)"]),
    # Plyometrics
    ex("p1","Pogo Hops","Plyometrics","Elasticity",["Plyometric Ability","Power"],["Bodyweight"],"Beginner",impact="Moderate",fatigue=2),
    ex("p2","Countermovement Jump","Plyometrics","Vertical Jump",["Power","Plyometric Ability"],["Bodyweight"],"Beginner",impact="Moderate",fatigue=2,sport_tags=["Basketball","Volleyball","Soccer"],regression="Squat Jump",progression="Loaded Jump"),
    ex("p3","Box Jump","Plyometrics","Vertical Jump",["Power","Plyometric Ability"],["Plyo Boxes & Agility Ladders"],"Beginner",impact="Moderate",fatigue=2,sport_tags=["Basketball","Soccer"],regression="Low Box Jump",progression="Reactive Box Jump"),
    ex("p4","Lateral Bound","Plyometrics","Lateral Jump",["Power","COD","Plyometric Ability"],["Bodyweight"],"Intermediate",plane="Frontal",impact="Moderate",fatigue=2,unilateral=True,sport_tags=["Soccer","Basketball","Tennis"],regression="Skater Step",progression="Continuous Bounds"),
    ex("p5","Depth Drop + Stick","Plyometrics","Landing",["Landing","Movement Quality","Stability"],["Plyo Boxes & Agility Ladders"],"Beginner",impact="Moderate",fatigue=2,regression="Snap Down",progression="Depth Jump"),
    ex("p6","Depth Jump","Plyometrics","Reactive Jump",["Power","Reactive Strength"],["Plyo Boxes & Agility Ladders"],"Advanced",impact="High",fatigue=4,prerequisites=["landing"],avoid_if=["knee","ankle"]),
    ex("p7","Med-Ball Rotational Throw","Plyometrics","Rotational Throw",["Power","Rotation"],["Medicine & Slam Balls"],"Beginner",plane="Transverse",fatigue=2,sport_tags=["Tennis","Racket Sports (Squash/Padel)","Combat Sports (MMA/Boxing)"],regression="Tall-Kneeling Throw",progression="Step-Behind Throw"),
    ex("p8","Med-Ball Chest Pass","Plyometrics","Upper Power",["Power"],["Medicine & Slam Balls"],"Beginner",fatigue=1,regression="Wall Chest Pass",progression="Reactive Chest Pass"),
    ex("p9","Single-Leg Hop & Stick","Plyometrics","Unilateral Jump",["Plyometric Ability","Stability"],["Bodyweight"],"Intermediate",impact="Moderate",fatigue=2,unilateral=True,avoid_if=["knee","ankle"]),
    # Agility / COD
    ex("a1","5-10-5 Shuttle","Agility / COD","COD",["COD","Agility"],["Cones / Timing Gates"],"Beginner",impact="Moderate",fatigue=3,sport_tags=["Soccer","Basketball","Tennis","Racket Sports (Squash/Padel)"]),
    ex("a2","Lateral Shuffle to Sprint","Agility / COD","COD",["COD","Acceleration","Agility"],["Cones / Timing Gates"],"Beginner",impact="Moderate",fatigue=3,sport_tags=["Soccer","Basketball","Tennis"]),
    ex("a3","Reactive Cone Drill","Agility / COD","Reactive Agility",["Agility","COD","Reaction"],["Cones / Timing Gates"],"Intermediate",impact="Moderate",fatigue=3,sport_tags=["Soccer","Basketball","Tennis","Racket Sports (Squash/Padel)"]),
    ex("a4","T-Drill","Agility / COD","COD",["COD","Agility"],["Cones / Timing Gates"],"Intermediate",impact="Moderate",fatigue=3,sport_tags=["Basketball","Soccer"]),
    ex("a5","Mirror Drill","Agility / COD","Reactive Agility",["Agility","Reaction","COD"],["Cones / Timing Gates"],"Intermediate",impact="Moderate",fatigue=3,sport_tags=["Soccer","Basketball","Combat Sports (MMA/Boxing)"]),
    ex("a6","Lateral Bound to Stick","Agility / COD","Deceleration",["Deceleration","Stability","COD"],["Bodyweight"],"Intermediate",plane="Frontal",impact="Moderate",fatigue=2,unilateral=True,avoid_if=["knee","ankle"]),
    # Speed
    ex("s1","Wall Acceleration March","Acceleration / Speed","Acceleration",["Acceleration","Technique"],["Bodyweight"],"Beginner",fatigue=1),
    ex("s2","Falling Start Sprint","Acceleration / Speed","Acceleration",["Acceleration","Speed"],["Bodyweight"],"Beginner",fatigue=2,sport_tags=["Soccer","Basketball","Rugby/American Football"]),
    ex("s3","Sled Acceleration","Acceleration / Speed","Acceleration",["Acceleration","Power"],["Sleds & Prowler"],"Intermediate",fatigue=3,sport_tags=["Soccer","Rugby/American Football"]),
    ex("s4","Flying 10 m Sprint","Acceleration / Speed","Max Velocity",["Speed","Technique"],["Cones / Timing Gates"],"Advanced",fatigue=3,avoid_if=["hamstring"]),
    # Aerobic / anaerobic
    ex("c1","AirBike Intervals","Aerobic","Aerobic",["Aerobic","Work Capacity"],["Ergometers (AirBike/Rower/SkiErg)"],"Beginner",fatigue=3),
    ex("c2","Rower Intervals","Aerobic","Aerobic",["Aerobic","Work Capacity"],["Ergometers (AirBike/Rower/SkiErg)"],"Beginner",fatigue=3),
    ex("c3","Zone 2 Run / Bike","Aerobic","Aerobic",["Aerobic","Recovery / Work Capacity"],["Ergometers (AirBike/Rower/SkiErg)","Bodyweight"],"Beginner",fatigue=2),
    ex("c4","Tempo Shuttle","Aerobic","Aerobic",["Aerobic","COD"],["Cones / Timing Gates"],"Intermediate",fatigue=3,sport_tags=["Soccer","Basketball","Tennis"]),
    ex("n1","Repeated Sprint 10 x 20 m","Anaerobic / Repeated Sprint","Repeated Sprint",["Anaerobic","Speed","Acceleration"],["Cones / Timing Gates"],"Intermediate",fatigue=4,sport_tags=["Soccer","Basketball","Rugby/American Football"]),
    ex("n2","Shuttle Sprint 15/15","Anaerobic / Repeated Sprint","Repeated Sprint",["Anaerobic","COD"],["Cones / Timing Gates"],"Intermediate",fatigue=4,sport_tags=["Soccer","Basketball","Tennis"]),
    ex("n3","AirBike 30/30","Anaerobic / Repeated Sprint","Intervals",["Anaerobic","Work Capacity"],["Ergometers (AirBike/Rower/SkiErg)"],"Intermediate",fatigue=4),
    # Additional compound / ballistic building blocks
    ex("p1","Countermovement Jump","Plyometrics","Vertical Jump",["Power","Plyometric Ability"],["Bodyweight"],"Beginner",impact="Moderate",fatigue=2),
    ex("p2","Standing Broad Jump","Plyometrics","Horizontal Jump",["Power","Plyometric Ability","Acceleration"],["Bodyweight"],"Beginner",impact="Moderate",fatigue=2),
    ex("p3","Lateral Bound","Plyometrics","Lateral Jump",["Power","Plyometric Ability","COD"],["Bodyweight"],"Intermediate",plane="Frontal",impact="High",fatigue=2,unilateral=True,avoid_if=["knee","ankle"]),
    ex("p4","Medicine-Ball Chest Pass","Plyometrics","Upper-Body Ballistic",["Power"],["Medicine & Slam Balls"],"Beginner",impact="Low",fatigue=2),
    ex("p5","Rotational Medicine-Ball Scoop Toss","Plyometrics","Rotational Throw",["Power","Rotational Power"],["Medicine & Slam Balls"],"Intermediate",plane="Transverse",impact="Low",fatigue=2,sport_tags=["Tennis","Racket Sports (Squash/Padel)","Combat Sports (MMA/Boxing)"],avoid_if=["low back"]),
    ex("p6","Medicine-Ball Overhead Throw","Plyometrics","Overhead Throw",["Power"],["Medicine & Slam Balls"],"Intermediate",impact="Low",fatigue=2),
    ex("r13","Landmine Rotation","Resistance","Rotation",["Strength","Power","Core / Trunk"],["Barbells & Plates"],"Intermediate",plane="Transverse",fatigue=3,sport_tags=["Tennis","Racket Sports (Squash/Padel)","Combat Sports (MMA/Boxing)"],avoid_if=["back"]),
    ex("r14","Kettlebell Swing","Resistance","Hinge Ballistic",["Power","Strength","Work Capacity"],["Kettlebells"],"Intermediate",fatigue=3,avoid_if=["back"]),
    ex("n4","Sled Push","Anaerobic / Repeated Sprint","Loaded Locomotion",["Power","Anaerobic","Work Capacity"],["Sleds & Prowler"],"Intermediate",fatigue=4,sport_tags=["Soccer","Basketball","Rugby/American Football"]),
]
EXERCISES = {x.id:x for x in E}

# ============================================================
# ADVANCED COMPOUND / COMPLEX / CONTRAST LIBRARY
# ============================================================
COMPLEXES = [
    TrainingComplex("cx1","Squat → Vertical Jump","Contrast","Power",["Strength"],["r1","p1"],sport_tags=["Soccer","Basketball","Volleyball","Rugby/American Football"],min_level="Advanced",impact="High",fatigue=4,equipment=["Barbells & Plates"],notes="High-force squat paired with a biomechanically related jump."),
    TrainingComplex("cx2","Trap-Bar Deadlift → Broad Jump → Sprint","Complex","Acceleration",["Power","Speed"],["r6","p2","s2"],sport_tags=["Soccer","Rugby/American Football","Track & Field (Sprints/Jumps)"],min_level="Advanced",impact="High",fatigue=5,equipment=["Barbells & Plates"],rest_between="20–30 s",rest_rounds="3 min"),
    TrainingComplex("cx3","RFESS → Lateral Bound → COD","Complex","Agility",["Strength","Power","COD"],["r4","p3","a3"],sport_tags=["Soccer","Basketball","Tennis","Racket Sports (Squash/Padel)"],min_level="Advanced",impact="High",fatigue=4,equipment=["Dumbbells"],rest_between="20–30 s",rest_rounds="2–3 min"),
    TrainingComplex("cx4","Bench Press → Medicine-Ball Chest Pass","Contrast","Upper-Body Power",["Strength","Power"],["r9","p4"],sport_tags=["Combat Sports (MMA/Boxing)","Rugby/American Football","Basketball"],min_level="Advanced",impact="Moderate",fatigue=3,equipment=["Barbells & Plates","Medicine & Slam Balls"],rest_between="15–20 s",rest_rounds="2–3 min"),
    TrainingComplex("cx5","Rotational Scoop Toss → Landmine Rotation → Lateral Sprint","Sport Power Complex","Rotational Power",["Power","COD","Acceleration"],["p5","r13","a2"],sport_tags=["Tennis","Racket Sports (Squash/Padel)","Combat Sports (MMA/Boxing)"],min_level="Intermediate",impact="Moderate",fatigue=3,equipment=["Medicine & Slam Balls","Barbells & Plates","Cones / Timing Gates"],rest_between="20–30 s",rest_rounds="2–3 min"),
    TrainingComplex("cx6","Front Squat → Box Jump","Contrast","Power",["Strength","Plyometric Ability"],["r3","p2"],sport_tags=["Basketball","Volleyball","Soccer","Track & Field (Sprints/Jumps)"],min_level="Advanced",impact="High",fatigue=4,equipment=["Barbells & Plates","Plyo Boxes & Agility Ladders"],rest_between="15–30 s",rest_rounds="3 min"),
    TrainingComplex("cx7","Push Press → Med-Ball Overhead Throw","Complex","Upper-Body Power",["Strength","Power"],["r12","p6"],sport_tags=["Volleyball","Combat Sports (MMA/Boxing)","Rugby/American Football"],min_level="Intermediate",impact="Moderate",fatigue=3,equipment=["Barbells & Plates","Medicine & Slam Balls"],rest_between="20–30 s",rest_rounds="2 min"),
    TrainingComplex("cx8","Lateral Bound → Stick → Reactive Cone Drill","Agility Complex","Agility",["Plyometric Ability","COD","Stability"],["a6","a2","a5"],sport_tags=["Tennis","Racket Sports (Squash/Padel)","Soccer","Basketball"],min_level="Intermediate",impact="High",fatigue=3,equipment=["Cones / Timing Gates"],rest_between="20–30 s",rest_rounds="2 min"),
    TrainingComplex("cx9","Kettlebell Swing → Sled Push → Shuttle","Power-Endurance Complex","Anaerobic",["Power","Work Capacity","Acceleration"],["r14","n4","n2"],sport_tags=["Soccer","Basketball","Rugby/American Football","General Fitness"],min_level="Intermediate",impact="Moderate",fatigue=5,equipment=["Kettlebells","Sleds & Prowler","Cones / Timing Gates"],rest_between="30–45 s",rest_rounds="2–3 min"),
]
COMPLEXES_BY_ID={c.id:c for c in COMPLEXES}

# ============================================================
# SCREENING / WARM-UP DATA
# ============================================================
POSTURE_OPTIONS = ["Not assessed","No notable deviation","Mild deviation","Marked deviation"]
POSTURE_FIELDS = {
    "Anterior":["Head / neck","Shoulder height","Pelvic level","Knee alignment","Foot / arch position"],
    "Lateral":["Head position","Thoracic curve","Lumbar curve","Pelvic tilt","Knee position"],
    "Posterior":["Scapular position","Spinal alignment","Pelvic level","Knee alignment","Foot / heel alignment"],
}
MOVEMENT_SCREEN_PATTERNS = ["Deep Squat","Hurdle Step","Inline Lunge","Shoulder Mobility","Active Straight Leg Raise","Trunk Stability Push-Up","Rotary Stability"]
MOVEMENT_SCREEN_OPTIONS = ["Not assessed","FN — Functional / Non-painful","FP — Functional / Painful","DN — Dysfunctional / Non-painful","DP — Dysfunctional / Painful"]
SPORT_WARMUPS = {
    "Soccer":["Dynamic Hamstring Sweeps","Ankle Mobility + Single-Leg Balance","Multi-Directional Shuttles"],
    "Basketball":["Ankle/Achilles Prep","Landing Mechanics","Reactive Jump Hops"],
    "Tennis":["Wrist/Forearm Rotations","T-Spine Openers","Lateral Multi-Directional Shuttles"],
    "Racket Sports (Squash/Padel)":["Wrist/Forearm Rotations","T-Spine Openers","Lateral Multi-Directional Shuttles"],
    "Volleyball":["Scapular Activation","Ankle Stiffness Hops","Lateral Bounds + Block Hops"],
    "Combat Sports (MMA/Boxing)":["T-Spine Windmills","Hip 90/90 Flow","Footwork + Rotational Prep"],
    "Track & Field (Sprints/Jumps)":["A-Skips / Ankling","Dynamic Hamstring Sweeps","Acceleration Wall Drills"],
    "Rugby/American Football":["Neck Prep","Groin/Adductor Mobility","Resisted Acceleration Starts"],
    "General Fitness":["World's Greatest Stretch","Band Pull-Aparts + Glute Bridges","Bodyweight Squats + Arm Circles"],
}

# ============================================================
# DEFAULTS / STATE
# ============================================================
DEFAULTS = {
    "name":"New Athlete","age":25,"sex":"Male","height_cm":180.0,"weight_kg":80.0,
    "sport":"General Fitness","position":"General","primary_goal":"Overall Development",
    "secondary_goals":["Strength","Mobility","Stability"],"season":"General / No Competition",
    "competition_days":0,"team_days":0,"team_minutes":0,"gym_days_available":3,"session_minutes":60,
    "training_years":2.0,"equipment":EQUIPMENT.copy(),"injuries":[],"pain_present":False,"pain_score":0,
    "sleep_hours":7.5,"readiness":80,"stress":3,"soreness":3,"weekly_sport_rpe":6.0,"weekly_steps_or_activity":7000,
    "rom_ankle":35.0,"rom_hip_flex":120.0,"rom_hip_ext":15.0,"rom_tspine":45.0,"rom_shoulder":170.0,
    "cmj":40.0,"broad_jump":210.0,"sprint_5m":1.10,"sprint_10m":1.80,"cod":10.50,"squat_1rm":100.0,
    "bench_1rm":70.0,"ohp_1rm":45.0,"pullups":8,"pushups":30,"cooper_m":2400.0,"left_jump":105.0,"right_jump":104.0,
    "posture_anterior":{},"posture_lateral":{},"posture_posterior":{},"movement_screen":{},
    "forehand_throw_m":8.0,"backhand_throw_m":7.5,"rotational_throw_m":8.0,"overhead_throw_m":7.0,"notes":"",
}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v
if "generated_plan" not in st.session_state: st.session_state.generated_plan = None
if "decision_state" not in st.session_state: st.session_state.decision_state = None
if "profiles" not in st.session_state: st.session_state.profiles = {}
if "records" not in st.session_state: st.session_state.records = []
if "rotation_map" not in st.session_state: st.session_state.rotation_map = {}
if "feedback" not in st.session_state: st.session_state.feedback = {"session_rpe":[],"pain":[],"performance":[]}

# ============================================================
# CORE UTILITIES
# ============================================================
def athlete() -> AthleteProfile:
    d={k:st.session_state.get(k,v) for k,v in DEFAULTS.items()}
    return AthleteProfile(**d)

def setv(key,value):
    st.session_state[key]=value
    if key not in {"name","notes"}:
        st.session_state.generated_plan=None
        st.session_state.decision_state=None

def training_level(years):
    if years < 1: return "Beginner"
    if years < 4: return "Intermediate"
    if years < 8: return "Advanced"
    return "Elite"

def bmi(a):
    h=a.height_cm/100
    return a.weight_kg/(h*h) if h else 0

def relative_strength(load,weight): return load/max(weight,1)
def asymmetry(l,r): return abs(l-r)/max(abs(l),abs(r),1e-9)*100

def readiness_score(a):
    sleep=np.clip((a.sleep_hours-5)/4,0,1)*100
    fatigue=np.clip(100-(a.stress*10+a.soreness*8),0,100)
    score=.45*a.readiness+.30*sleep+.25*fatigue
    if a.pain_present: score-=a.pain_score*5
    return float(np.clip(score,0,100))

def readiness_band(score):
    if score < 45: return "RED", "Reduce volume/intensity; emphasize recovery and low-impact work."
    if score < 65: return "YELLOW", "Keep quality high; reduce non-essential fatigue."
    if score < 80: return "GREEN", "Normal planned training with standard progression."
    return "BLUE", "High readiness; quality overload can be considered if other constraints allow."

def phase_for(a,week):
    if a.season=="In-Season / Competition": return ["Maintenance","Strength Retention","Power Maintenance","Deload / Taper"][week-1]
    if a.season=="Taper / Peak": return ["Specificity","Speed / Power","Taper","Competition Readiness"][week-1]
    if a.primary_goal in ["Max Strength","Strength"]: return ["Accumulation","Intensification","Realization","Deload"][week-1]
    if a.primary_goal in ["Power","Speed","Agility","Sport Performance"]: return ["Capacity","Strength-Speed","Specific Power","Deload"][week-1]
    if a.primary_goal=="Hypertrophy": return ["Volume","Overload","Peak Volume","Deload"][week-1]
    return ["Foundation","Build","Progress","Deload"][week-1]

def weekly_load_reference(a,week):
    level=training_level(a.training_years)
    base={
        "Beginner":{1:(3,8,.65),2:(3,8,.70),3:(3,7,.72),4:(2,8,.55)},
        "Intermediate":{1:(3,8,.70),2:(4,7,.75),3:(4,5,.82),4:(2,6,.60)},
        "Advanced":{1:(4,6,.75),2:(4,5,.80),3:(5,3,.87),4:(2,5,.62)},
        "Elite":{1:(4,5,.78),2:(5,4,.83),3:(5,2,.90),4:(2,4,.65)},
    }[level][week]
    sets,reps,pct=base
    if a.primary_goal=="Hypertrophy":
        sets={1:3,2:4,3:4,4:2}[week]; reps={1:10,2:8,3:8,4:8}[week]; pct={1:.65,2:.70,3:.75,4:.55}[week]
    if a.primary_goal in ["Power","Speed","Agility","Sport Performance"]:
        sets={1:3,2:3,3:4,4:2}[week]; reps={1:5,2:4,3:3,4:3}[week]; pct={1:.65,2:.70,3:.75,4:.50}[week]
    if a.season in ["In-Season / Competition","Taper / Peak"]:
        sets=min(sets,2 if week!=3 else 3); pct={1:.70,2:.75,3:.80,4:.55}[week]
    return {"sets":sets,"reps":reps,"pct":pct,"rpe":{1:7,2:7.5,3:8,4:6}[week]}

# ============================================================
# STAGE 1 — CONSTRAINT ENGINE
# ============================================================
def screening_flags(a):
    flags=[]
    for view,d in [("Anterior",a.posture_anterior),("Lateral",a.posture_lateral),("Posterior",a.posture_posterior)]:
        for item,val in d.items():
            if val in ("Mild deviation","Marked deviation"):
                flags.append(f"{view}: {item} = {val}")
    for pattern,result in a.movement_screen.items():
        if result in ("FP — Functional / Painful","DP — Dysfunctional / Painful"):
            flags.append(f"Movement screen: {pattern} is painful")
        elif result=="DN — Dysfunctional / Non-painful":
            flags.append(f"Movement screen: {pattern} is dysfunctional")
    if a.rom_ankle<30: flags.append("Limited ankle dorsiflexion")
    if a.rom_hip_flex<120: flags.append("Limited hip flexion")
    if a.rom_hip_ext<15: flags.append("Limited hip extension")
    if a.rom_tspine<45: flags.append("Limited T-spine rotation")
    if a.rom_shoulder<165: flags.append("Limited shoulder flexion")
    return flags

def injury_keys(a):
    text=" ".join(a.injuries).lower()
    keys=[]
    mapping={
        "knee / acl / mcl / patellar":"knee","hamstring":"hamstring","ankle / achilles":"ankle",
        "shoulder / rotator cuff":"shoulder","low back":"back","groin / adductor":"groin","quadriceps":"quad"
    }
    for label,key in mapping.items():
        if label in text: keys.append(key)
    return keys

def constraint_engine(a):
    r=readiness_score(a); band,_=readiness_band(r)
    pain_gate=a.pain_present and a.pain_score>=5
    return {
        "readiness":r,"band":band,"pain_gate":pain_gate,"injury_keys":injury_keys(a),
        "screen_flags":screening_flags(a),
        "low_impact": band=="RED" or pain_gate,
        "volume_multiplier": .55 if band=="RED" else .75 if band=="YELLOW" else .90 if band=="GREEN" else 1.0,
        "intensity_multiplier": .85 if band=="RED" else .92 if band=="YELLOW" else 1.0,
        "high_impact_allowed": not (band=="RED" or pain_gate),
        "high_fatigue_allowed": not (band in ["RED","YELLOW"] or a.season in ["In-Season / Competition","Taper / Peak"]),
    }

# ============================================================
# STAGE 2 — PERFORMANCE PROFILE
# ============================================================
def performance_scores(a):
    return {
        "Strength":float(np.clip(relative_strength(a.squat_1rm,a.weight_kg)/2*100,0,100)),
        "Upper Strength":float(np.clip(relative_strength(a.bench_1rm,a.weight_kg)/1.25*100,0,100)),
        "Power":float(np.clip(a.cmj/60*100,0,100)),
        "Acceleration":float(np.clip((2.2-a.sprint_10m)/1.2*100,0,100)),
        "COD / Agility":float(np.clip((13-a.cod)/4*100,0,100)),
        "Aerobic":float(np.clip((a.cooper_m-1600)/1800*100,0,100)),
        "Stability":float(np.clip(100-asymmetry(a.left_jump,a.right_jump)*4,0,100)),
        "Rotational Power":float(np.clip(a.rotational_throw_m/12*100,0,100)),
        "Forehand Power":float(np.clip(a.forehand_throw_m/12*100,0,100)),
        "Backhand Power":float(np.clip(a.backhand_throw_m/12*100,0,100)),
        "Racket Power Symmetry":float(np.clip(100-asymmetry(a.forehand_throw_m,a.backhand_throw_m),0,100)),
        "Mobility":float(np.mean([
            np.clip(a.rom_ankle/40*100,0,100),np.clip(a.rom_hip_flex/130*100,0,100),
            np.clip(a.rom_hip_ext/20*100,0,100),np.clip(a.rom_tspine/50*100,0,100),np.clip(a.rom_shoulder/175*100,0,100)
        ])),
    }

def screening_adjustments(a):
    out={q:0.0 for q in ["Mobility","Stability","Strength","Power","Agility","Speed","Aerobic","Anaerobic"]}
    flags=screening_flags(a)
    for f in flags:
        s=f.lower()
        if any(k in s for k in ["ankle","hip","t-spine","shoulder","mobility","rotation","flexion","extension"]): out["Mobility"]+=3
        if any(k in s for k in ["pelvic","knee alignment","scapular","stability","landing","rotary"]): out["Stability"]+=3
        if "painful" in s: out["Power"]-=8; out["Agility"]-=8; out["Speed"]-=6
        if "dysfunctional" in s: out["Power"]-=3; out["Agility"]-=3
    if asymmetry(a.left_jump,a.right_jump)>=8: out["Stability"]+=8; out["Plyometric Ability"] = out.get("Plyometric Ability",0)+2
    return out

# ============================================================
# STAGE 3 — GOAL + SPORT + GAP DECISION ENGINE
# ============================================================
def priorities(a):
    scores=performance_scores(a)
    demands=SPORT_DEMANDS.get(a.sport,SPORT_DEMANDS["General Fitness"])
    adj=screening_adjustments(a)
    raw={"Strength":0.0,"Hypertrophy":0.0,"Power":0.0,"Acceleration":0.0,"COD":0.0,"Aerobic":0.0,"Anaerobic":0.0,"Mobility":0.0,"Stability":0.0,"Rotational Power":0.0}
    quality_score={
        "Strength":scores["Strength"],"Power":scores["Power"],"Acceleration":scores["Acceleration"],
        "COD":scores["COD / Agility"],"Aerobic":scores["Aerobic"],"Stability":scores["Stability"],"Mobility":scores["Mobility"]
    }
    for q in raw:
        score=quality_score.get(q,50)
        gap=max(0,100-score)
        demand=demands.get(q,.05)
        raw[q]+=gap*demand
    if a.sport in ["Tennis","Racket Sports (Squash/Padel)"]:
        raw["Rotational Power"] += max(0,100-scores["Rotational Power"])*0.18
        raw["Power"] += max(0,100-scores["Racket Power Symmetry"])*0.10
        raw["COD"] += max(0,100-scores["COD / Agility"])*0.06
    goal_map={
        "Strength":"Strength","Max Strength":"Strength","Hypertrophy":"Hypertrophy","Power":"Power",
        "Speed":"Acceleration","Agility":"COD","Endurance":"Aerobic","Sport Performance":"Power",
        "Fat Loss":"Aerobic","General Fitness":"Strength"
    }
    if a.primary_goal=="Overall Development":
        for q in raw: raw[q]*=1.08
        raw["Mobility"]+=max(0,100-scores["Mobility"])*.12
        raw["Stability"]+=max(0,100-scores["Stability"])*.12
    elif a.primary_goal in goal_map:
        raw[goal_map[a.primary_goal]]*=1.45
    for g in a.secondary_goals:
        key={
            "Strength":"Strength","Max Strength":"Strength","Hypertrophy":"Hypertrophy","Power":"Power","Speed":"Acceleration",
            "Agility":"COD","Aerobic Capacity":"Aerobic","Anaerobic Capacity":"Anaerobic","Mobility":"Mobility",
            "Stability":"Stability","Plyometric Ability":"Power","Movement Quality":"Mobility","Core / Trunk":"Stability",
            "Recovery / Work Capacity":"Aerobic","Body Composition":"Aerobic"
        }.get(g)
        if key: raw[key]+=9
    raw["Mobility"]+=adj.get("Mobility",0); raw["Stability"]+=adj.get("Stability",0)
    raw["Power"]+=adj.get("Power",0); raw["COD"]+=adj.get("Agility",0); raw["Acceleration"]+=adj.get("Speed",0)
    if a.season=="In-Season / Competition":
        raw["Hypertrophy"]*=.45; raw["Strength"]*=.80; raw["Aerobic"]*=.85; raw["Power"]*=1.05; raw["Speed"] if "Speed" in raw else None
    if a.season=="Taper / Peak":
        raw["Hypertrophy"]*=.25; raw["Strength"]*=.55; raw["Power"]*=1.25; raw["Acceleration"]*=1.20; raw["COD"]*=1.15
    total=sum(max(v,0) for v in raw.values()) or 1
    return {k:round(max(v,0)/total*100,1) for k,v in sorted(raw.items(),key=lambda x:x[1],reverse=True)}

def system_allocation(a, p, constraints):
    mapping={
        "Corrective / Activation":["Mobility","Stability"],"Mobility":["Mobility"],"Stability / Core":["Stability"],
        "Plyometrics":["Power"],"Acceleration / Speed":["Acceleration"],"Agility / COD":["COD"],
        "Resistance":["Strength","Hypertrophy"],"Aerobic":["Aerobic"],"Anaerobic / Repeated Sprint":["Anaerobic"]
    }
    scores={}
    for system,qualities in mapping.items(): scores[system]=max([p.get(q,0) for q in qualities]+[0])
    # Screening and readiness gates are allowed to override normal priority.
    if screening_flags(a): scores["Corrective / Activation"]+=8; scores["Mobility"]+=5
    if constraints["low_impact"]:
        scores["Mobility"]+=10; scores["Stability / Core"]+=8; scores["Aerobic"]+=5
        scores["Plyometrics"]*=.35; scores["Agility / COD"]*=.45; scores["Acceleration / Speed"]*=.50; scores["Anaerobic / Repeated Sprint"]*=.40
    if not constraints["high_fatigue_allowed"]: scores["Anaerobic / Repeated Sprint"]*=.65
    if a.season=="In-Season / Competition":
        scores["Resistance"]*=.85; scores["Plyometrics"]*=1.05; scores["Acceleration / Speed"]*=1.05
    return {k:round(v,2) for k,v in sorted(scores.items(),key=lambda x:x[1],reverse=True)}

# ============================================================
# STAGE 4 — EXERCISE SAFETY / MATCHING
# ============================================================
def exercise_allowed(x,a,constraints):
    if not any(eq in a.equipment for eq in x.equipment): return False
    order={"Beginner":0,"Intermediate":1,"Advanced":2,"Elite":3}
    if order[training_level(a.training_years)]+1<order[x.level]: return False
    if "ankle" in x.prerequisites and a.rom_ankle<25: return False
    if "shoulder" in x.prerequisites and a.rom_shoulder<155: return False
    if "landing" in x.prerequisites and asymmetry(a.left_jump,a.right_jump)>=12: return False
    keys=constraints["injury_keys"]
    for k in keys:
        if k in x.avoid_if: return False
    if constraints["pain_gate"] and x.system in ["Plyometrics","Agility / COD","Acceleration / Speed","Anaerobic / Repeated Sprint"]: return False
    if constraints["low_impact"] and x.impact=="High": return False
    return True

def exercise_score(x,a,p,system_scores,month,used_ids):
    score=0.0
    if a.sport in x.sport_tags: score+=18
    if "General Fitness" in x.sport_tags: score+=3
    score+=max([p.get(q,0) for q in x.quality]+[0])*.18
    score+=system_scores.get(x.system,0)*.08
    if x.unilateral and asymmetry(a.left_jump,a.right_jump)>=6: score+=10
    if x.id in used_ids: score-=30
    score-=x.fatigue*max(0,70-readiness_score(a))/100*8
    if a.season in ["In-Season / Competition","Taper / Peak"] and x.fatigue>=4: score-=10
    # Rotation deliberately prefers a close variant instead of random novelty.
    score += max(0,month-1)*0.4 if x.id not in used_ids else 0
    return score

def select_exercises(a,p,system_scores,system,n,month,used_ids,constraints):
    candidates=[x for x in E if x.system==system and exercise_allowed(x,a,constraints)]
    candidates.sort(key=lambda x:exercise_score(x,a,p,system_scores,month,used_ids),reverse=True)
    return candidates[:n]

# ============================================================
# STAGE 5 — DOSE / SEQUENCING / ENERGY SYSTEMS
# ============================================================
def volume_modifier(a,constraints,week):
    mod=constraints["volume_multiplier"]
    if week==4: mod*=.60
    if a.season=="In-Season / Competition": mod*=.85
    return float(np.clip(mod,.35,1.0))

def resistance_dose(a,week,slot,constraints):
    ref=weekly_load_reference(a,week); vm=volume_modifier(a,constraints,week)
    sets=max(1,round(ref["sets"]*vm))
    reps=ref["reps"] if slot=="primary" else max(6,min(12,ref["reps"]+1))
    if slot=="accessory": reps=max(8,min(15,ref["reps"]+2))
    pct=ref["pct"]*constraints["intensity_multiplier"]
    rpe=ref["rpe"]
    if constraints["band"]=="RED": rpe=min(rpe,6.5)
    elif constraints["band"]=="YELLOW": rpe=min(rpe,7.0)
    return sets,reps,pct,rpe

def plyo_dose(a,week,constraints):
    if not constraints["high_impact_allowed"]: return "2 × 3–5 low-impact contacts", "Full recovery", "Technique / landing quality"
    sets=2 if week==4 else 3 if week<3 else 4
    reps=3 if week>=2 else 4
    return f"{sets} × {reps} quality contacts", "90–150 s", "Max intent; stop when landing/height quality falls"

def agility_dose(a,week,constraints):
    sets=1 if week==4 or constraints["band"]=="RED" else 2 if constraints["band"]=="YELLOW" else 3
    return f"{sets} × 3–5 reps", "60–120 s", "Quality COD / reactive decision; avoid conditioning failure"

def speed_dose(a,week,constraints):
    sets=2 if week==4 else 3 if constraints["band"]=="YELLOW" else 4
    return f"{sets} × 10–30 m", "90–180 s", "Max intent; full recovery"

def conditioning_decision(a,p,constraints,week):
    # Every upstream change changes this block.
    if constraints["pain_gate"]:
        return {"system":"Aerobic","name":"Low-impact recovery conditioning","stations":["Bike / AirBike easy","Walking or easy cyclical work","Mobility reset"],"work":"15–25 min","rest":"As needed","intensity":"RPE 4–5/10","reason":"Pain/readiness gate"}
    if constraints["band"]=="RED":
        return {"system":"Aerobic","name":"Recovery aerobic station","stations":["Bike / Rower easy","Easy walk","Breathing + mobility reset"],"work":"15–20 min","rest":"As needed","intensity":"RPE 4–5/10","reason":"Low readiness"}
    if a.season in ["In-Season / Competition","Taper / Peak"] and a.competition_days>0:
        return {"system":"Aerobic","name":"Competition-support aerobic work","stations":["Bike / Rower","Easy tempo movement","Mobility reset"],"work":"6–8 × 45 s / 60 s easy","rest":"60 s","intensity":"RPE 5–6/10","reason":"Protect sport performance around competition"}
    if p.get("Anaerobic",0)>=20 and constraints["high_fatigue_allowed"]:
        return {"system":"Anaerobic / Repeated Sprint","name":"Repeated Sprint Station","stations":["10–20 m shuttle sprint","Lateral cone shuffle","AirBike 15–20 s hard"],"work":"2–3 rounds × 3 stations","rest":"40–60 s between reps; 3 min rounds","intensity":"RPE 8–9/10","reason":"Anaerobic gap + sport demand"}
    if p.get("COD",0)>=18:
        return {"system":"Agility / COD","name":"Agility Station Circuit","stations":["5-10-5 Shuttle","Reactive Cone Drill","Lateral Shuffle → Sprint"],"work":"2–3 rounds × 3 stations","rest":"60–90 s","intensity":"High quality, not failure","reason":"COD/agility priority"}
    if p.get("Aerobic",0)>=20:
        return {"system":"Aerobic","name":"Aerobic Interval Station","stations":["AirBike / Rower","Tempo Shuttle or Bike","Easy walk / mobility reset"],"work":"6–10 × 2 min work","rest":"1 min easy","intensity":"RPE 6–7/10","reason":"Aerobic gap + work capacity target"}
    return {"system":"Aerobic","name":"Mixed Energy-System Circuit","stations":["Cyclical aerobic station","Tempo locomotion","Core / mobility reset"],"work":"3–4 rounds × 4 min","rest":"60–90 s","intensity":"RPE 6–7/10","reason":"Whole-athlete work-capacity balance"}

def session_template(a,day,system_scores,constraints):
    # The template is not fixed: the highest priorities determine the slots.
    ranked=list(system_scores.keys())
    high=[s for s in ranked if s not in ["Corrective / Activation","Mobility","Stability / Core"]]
    if day==1: preferred=["Plyometrics","Acceleration / Speed","Resistance","Resistance","Stability / Core"]
    elif day==2: preferred=["Agility / COD","Resistance","Resistance","Mobility","Stability / Core"]
    elif day==3: preferred=["Plyometrics","Resistance","Acceleration / Speed","Resistance","Anaerobic / Repeated Sprint"]
    else: preferred=["Agility / COD","Resistance","Resistance","Stability / Core","Aerobic"]
    # Replace systems that are strongly suppressed by readiness.
    if constraints["low_impact"]:
        preferred=["Corrective / Activation","Mobility","Stability / Core","Resistance","Aerobic"]
    # Pull one high-priority system into the day if it is not already represented.
    if high and high[0] not in preferred and not constraints["low_impact"]:
        preferred[-1]=high[0]
    return preferred

# ============================================================
# STAGE 6 — MACROCYCLE / ROTATION / PROGRESSION
# ============================================================
def build_rotation(a,months,p,system_scores,constraints):
    rotation={}; history={}
    for month in range(1,months+1):
        rotation[month]={}
        for system in SYSTEMS:
            candidates=[x for x in E if x.system==system and exercise_allowed(x,a,constraints)]
            if not candidates: continue
            used=history.get(system,[])
            candidates.sort(key=lambda x:exercise_score(x,a,p,system_scores,month,used),reverse=True)
            # Novelty is secondary to objective, equipment and safety.
            chosen=next((x for x in candidates if x.id not in used),candidates[0])
            rotation[month][system]=chosen.id
            history.setdefault(system,[]).append(chosen.id)
    return rotation

def progression_rule(a,week,exercise,slot,constraints):
    # Week-to-week change is constrained by readiness and season.
    if week==4: return "Deload: reduce volume; preserve movement quality and speed."
    if constraints["band"]=="RED": return "Autoregulate: no planned load increase; stop well before fatigue changes technique."
    if constraints["band"]=="YELLOW": return "Hold or add only a small load/repetition increase if all reps are technically strong."
    if a.primary_goal in ["Power","Speed","Agility","Sport Performance"] or exercise.system in ["Plyometrics","Acceleration / Speed","Agility / COD"]:
        return "Progress quality first: faster execution, cleaner mechanics, slightly more exposure—not fatigue accumulation."
    if a.primary_goal=="Hypertrophy": return "Progress reps within the range, then add a small load while maintaining target RPE."
    return "Progress load conservatively when the prescribed reps are completed at or below target RPE."

def complex_allowed(c,a,constraints):
    levels={"Beginner":0,"Intermediate":1,"Advanced":2,"Elite":3}
    if levels[training_level(a.training_years)] < levels[c.min_level]: return False
    if not constraints["high_impact_allowed"] and c.impact=="High": return False
    if not constraints["high_fatigue_allowed"] and c.fatigue>=4: return False
    if any(e not in a.equipment for e in c.equipment): return False
    text=" ".join(a.injuries).lower()
    if any(k in text for k in ["knee","ankle","achilles","hamstring","low back","shoulder"]):
        if c.id in {"cx1","cx2","cx3","cx6","cx8"}: return False
    return True

def choose_complex(a,p,systems,constraints,month):
    if not constraints["high_impact_allowed"] or not constraints["high_fatigue_allowed"]:
        # Advanced complexes are deliberately suppressed under high fatigue/pain gates.
        return None
    candidates=[c for c in COMPLEXES if complex_allowed(c,a,constraints)]
    if not candidates: return None
    scores=performance_scores(a)
    def score(c):
        s=0.0
        if a.sport in c.sport_tags: s+=25
        if c.primary_quality in ["Power","Upper-Body Power","Rotational Power"]: s+=max(0,100-scores.get("Power",50))*0.20
        if c.primary_quality=="Agility": s+=max(0,100-scores.get("COD / Agility",50))*0.18
        if c.primary_quality=="Acceleration": s+=max(0,100-scores.get("Acceleration",50))*0.18
        if c.primary_quality=="Rotational Power": s+=max(0,100-scores.get("Rotational Power",50))*0.25
        if "Power" in p: s+=p.get("Power",0)*0.10
        if "COD" in p and c.primary_quality=="Agility": s+=p.get("COD",0)*0.12
        if a.sport in ["Tennis","Racket Sports (Squash/Padel)"] and "Rotational" in c.name: s+=20
        s-=c.fatigue*2
        return s
    return max(candidates,key=score)

def complex_dose(c,a,week,constraints):
    if c.method in ["Contrast","Sport Power Complex"]:
        rounds={1:3,2:3,3:4,4:2}[week]
        if training_level(a.training_years) in ["Intermediate"]: rounds=max(2,rounds-1)
        return rounds, "2–3 reps per exercise", c.rest_between, c.rest_rounds
    rounds={1:2,2:3,3:3,4:2}[week]
    return rounds, "4–6 reps / 5–10 s per drill", c.rest_between, c.rest_rounds

def build_session(a,week,day,month,rotation,p,system_scores,constraints):
    systems=session_template(a,day,system_scores,constraints)
    used=[]; exercises=[]
    for system in systems:
        rid=rotation.get(month,{}).get(system)
        candidate=EXERCISES.get(rid) if rid else None
        if candidate and exercise_allowed(candidate,a,constraints) and candidate.id not in used:
            x=candidate
        else:
            selected=select_exercises(a,p,system_scores,system,1,month,used,constraints)
            if not selected: continue
            x=selected[0]
        used.append(x.id); exercises.append(x)
    cond=conditioning_decision(a,p,constraints,week)
    complex_block=None
    # Place a complex only when power/agility demand and readiness justify advanced methods.
    if day==1 and (p.get("Power",0)+p.get("COD",0)+p.get("Acceleration",0)+p.get("Rotational Power",0))>22:
        complex_block=choose_complex(a,p,systems,constraints,month)
    return {"day":day,"week":week,"month":month,"phase":phase_for(a,week),"systems":systems,"exercises":exercises,"conditioning":cond,"complex":complex_block,"readiness":constraints["readiness"]}

def build_program(a,months):
    constraints=constraint_engine(a); p=priorities(a); systems=system_allocation(a,p,constraints)
    rotation=build_rotation(a,months,p,systems,constraints)
    days=max(1,min(a.gym_days_available,4))
    program={m:{w:[build_session(a,w,d,m,rotation,p,systems,constraints) for d in range(1,days+1)] for w in range(1,5)} for m in range(1,months+1)}
    return program,{"constraints":constraints,"priorities":p,"systems":systems,"rotation":rotation}

# ============================================================
# ADAPTATION LOOP — FEEDBACK CHANGES THE NEXT DECISION
# ============================================================
def apply_feedback(base_state,session_rpe,pain_after,performance_change):
    s=dict(base_state)
    if session_rpe>=9 or pain_after>=5:
        s["volume_multiplier"]*=.80; s["intensity_multiplier"]*=.95
    elif session_rpe<=5 and pain_after<=2 and performance_change>=1:
        s["volume_multiplier"]*=1.05
    if pain_after>=5:
        s["high_impact_allowed"]=False; s["high_fatigue_allowed"]=False
    return s

# ============================================================
# DECISION TRACE
# ============================================================
def decision_trace(a,months):
    program,engine=build_program(a,months)
    c=engine["constraints"]; p=engine["priorities"]; systems=engine["systems"]
    trace=[]
    trace.append(("01 Intake",f"{a.sport} / {a.position} • {a.primary_goal} • {a.season}"))
    trace.append(("02 Goal interaction",f"Primary goal + {len(a.secondary_goals)} secondary targets are combined rather than treated independently."))
    trace.append(("03 Readiness gate",f"{c['readiness']:.0f}/100 → {c['band']} • volume ×{c['volume_multiplier']:.2f} • intensity ×{c['intensity_multiplier']:.2f}"))
    if c["pain_gate"]: trace.append(("04 Safety gate","Pain threshold triggered: high-impact/high-fatigue systems are blocked from normal selection."))
    elif c["screen_flags"]: trace.append(("04 Screening gate",f"{len(c['screen_flags'])} screening flags increase corrective/mobility/stability priority."))
    else: trace.append(("04 Screening gate","No major screening constraint recorded."))
    top=" • ".join([f"{k} {v:.1f}%" for k,v in list(p.items())[:5]])
    trace.append(("05 Performance gaps",top))
    trace.append(("06 Sport demand",f"Sport demands are blended with individual gaps for {a.sport}."))
    trace.append(("07 System allocation"," • ".join([f"{k} {v:.1f}" for k,v in list(systems.items())[:6]])))
    trace.append(("08 Exercise selection","Equipment + level + injury gates + screening + sport relevance + fatigue + monthly novelty."))
    trace.append(("09 Dose","Sets/reps/intensity change with training level, goal, week, season and readiness."))
    trace.append(("10 Metabolic decision",program[1][1][0]["conditioning"]["name"]+" selected from the same upstream state."))
    trace.append(("11 Progression","Progression is conditional on technical quality, RPE, readiness and pain—not calendar alone."))
    trace.append(("12 Advanced methods","Compound/contrast/complex training is gated by training age, readiness, impact tolerance, equipment and current priorities."))
    if program[1][1][0].get("complex"):
        trace.append(("13 Complex selection",program[1][1][0]["complex"].name+" selected as an advanced power/agility stimulus."))
    trace.append(("14 Rotation","Monthly variants preserve the same system/movement objective while avoiding unnecessary repetition."))
    return trace,engine

# ============================================================
# RENDER HELPERS
# ============================================================
ACCENTS={
    "Corrective / Activation":"#38bdf8","Mobility":"#06b6d4","Stability / Core":"#a855f7",
    "Plyometrics":"#ec4899","Acceleration / Speed":"#f97316","Agility / COD":"#f59e0b",
    "Resistance":"#6366f1","Aerobic":"#10b981","Anaerobic / Repeated Sprint":"#ef4444"
}

def render_card(category,name,prescription,intensity,tempo,plane,tier,accent):
    st.markdown(f"""<div class="plan-card" style="border-left:5px solid {accent}">
    <div style="font-size:.75rem;font-weight:800;color:{accent};text-transform:uppercase;letter-spacing:.08em">{category}</div>
    <div style="font-size:1.15rem;font-weight:700;color:#fff;margin:8px 0 10px;line-height:1.4">{name}</div>
    <div style="display:flex;flex-wrap:wrap;gap:8px">
    <span>📌 <b>{prescription}</b></span><span style="color:#38bdf8">⚡ {intensity}</span>
    <span style="color:#a855f7">⏱️ {tempo}</span><span style="color:#ec4899">📐 {plane}</span>
    <span style="color:#10b981">🛡️ {tier}</span></div></div>""",unsafe_allow_html=True)

def render_exercise(a,x,week,constraints,slot):
    if x.system=="Resistance":
        sets,reps,pct,rpe=resistance_dose(a,week,slot,constraints)
        intensity=f"{pct*100:.0f}% estimated 1RM / RPE {rpe:g}"
        tempo=x.tempo_hypertrophy if a.primary_goal=="Hypertrophy" else x.tempo_strength
        pres=f"{sets} Sets × {reps} Reps"
    elif x.system=="Plyometrics":
        pres,rest,intensity=plyo_dose(a,week,constraints); tempo=f"Explosive • {rest}"
    elif x.system=="Agility / COD":
        pres,rest,intensity=agility_dose(a,week,constraints); tempo=f"Full recovery • {rest}"
    elif x.system=="Acceleration / Speed":
        pres,rest,intensity=speed_dose(a,week,constraints); tempo=f"Full recovery • {rest}"
    elif x.system=="Mobility": pres="2 Sets × 6–10 controlled reps/side"; intensity="Controlled ROM"; tempo="2-1-2-0"
    elif x.system in ["Stability / Core","Corrective / Activation"]: pres="2–3 Sets × 8–12 reps or 20–40 s"; intensity="RPE 5–7"; tempo="Controlled"
    elif x.system=="Anaerobic / Repeated Sprint": pres="2–3 Sets × 4–6 reps"; intensity="RPE 8–9"; tempo="Full quality recovery"
    else: pres="2–3 Sets × 8–12"; intensity="RPE 6–7"; tempo="2-1-2-0"
    render_card(x.system,x.name,pres,intensity,tempo,x.plane,x.tier,ACCENTS.get(x.system,"#38bdf8"))
    if x.regression or x.progression:
        st.caption(f"Regression: {x.regression or '—'} • Progression: {x.progression or '—'}")
    st.caption(progression_rule(a,week,x,slot,constraints))

def render_session(a,session,week,engine):
    c=engine["constraints"]
    warmups=" + ".join(SPORT_WARMUPS.get(a.sport,SPORT_WARMUPS["General Fitness"]))
    render_card("1. Corrective / Sport Prep",f"{a.sport}: {warmups}","2 rounds × 5–10 reps/side","Controlled, symptom-free","2-1-2-0","Multi-planar","Activation",ACCENTS["Corrective / Activation"])
    for i,x in enumerate(session["exercises"]):
        slot="primary" if i<2 else "secondary"
        render_exercise(a,x,week,c,slot)
    if session.get("complex"):
        cx=session["complex"]
        rounds,reps,between,round_rest=complex_dose(cx,a,week,c)
        st.markdown("#### ⚡ Complex / Compound Athletic Power Block")
        names=[EXERCISES[eid].name for eid in cx.exercises if eid in EXERCISES]
        render_card(cx.method,cx.name,f"{rounds} rounds • {reps}",f"Rest {round_rest} between rounds",f"{between} between exercises","Multi-planar","Advanced / Athletic",ACCENTS.get("Plyometrics","#ec4899"))
        st.caption(" → ".join(names))
        if cx.notes: st.caption(cx.notes)
    cond=session["conditioning"]
    st.markdown("#### 🔥 Metabolic / ESD Station")
    render_card("5. Dynamic MetCon / ESD Protocol",cond["name"]+" — "+" | ".join(cond["stations"]),cond["work"]+" • Rest: "+cond["rest"],cond["intensity"]+" • "+cond["reason"],"Dynamic Pace","Multi-planar","Energy System / Conditioning",ACCENTS["Aerobic"])

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("## ⚡ ATHLETE-IQ")
st.sidebar.caption("Every input propagates through the decision tree → the program")
module=st.sidebar.radio("Jump to Module",[
    "1. Athlete Profile","2. Load, Injury & Readiness","3. Comprehensive Screening","4. Performance Testing",
    "5. Decision Tree","6. Adaptive Program Generator","7. Feedback / Reassessment","8. Data / Profiles"
])
plan_months=st.sidebar.select_slider("Macrocycle Horizon",options=[1,2,3,4,5,6],value=3,format_func=lambda x:f"{x}-Month Block")

# ============================================================
# HEADER
# ============================================================
st.markdown("<h1 style='text-align:center;color:#38bdf8;font-weight:900;margin-bottom:0'>ATHLETE-IQ PERFORMANCE ENGINE</h1>",unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#a855f7;font-weight:700;font-size:1.1rem'>Coach Ahmed Youssef • Whole-Athlete Decision Tree</p>",unsafe_allow_html=True)

# ============================================================
# MODULE 1 — PROFILE / GOALS
# ============================================================
if module=="1. Athlete Profile":
    st.markdown('<div class="banner-header">01 • Athlete Profile & Goal Architecture</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:
        setv("name",st.text_input("Athlete Name",st.session_state.name)); setv("age",st.number_input("Age",12,80,int(st.session_state.age),1))
        setv("sex",st.selectbox("Sex",["Male","Female","Other"],index=["Male","Female","Other"].index(st.session_state.sex)))
        setv("height_cm",st.number_input("Height (cm)",120.0,230.0,float(st.session_state.height_cm),0.5)); setv("weight_kg",st.number_input("Weight (kg)",30.0,250.0,float(st.session_state.weight_kg),0.5))
    with c2:
        sports=list(SPORT_DEMANDS); sport=st.selectbox("Sport / Discipline",sports,index=sports.index(st.session_state.sport)); setv("sport",sport)
        pos=SPORT_POSITIONS[sport]; setv("position",st.selectbox("Position / Event",pos,index=pos.index(st.session_state.position) if st.session_state.position in pos else 0))
        setv("primary_goal",st.selectbox("Primary Goal",GOALS,index=GOALS.index(st.session_state.primary_goal)))
        setv("season",st.selectbox("Season / Calendar Phase",SEASONS,index=SEASONS.index(st.session_state.season)))
    with c3:
        setv("secondary_goals",st.multiselect("Secondary Development Targets",SECONDARY_OPTIONS,default=[x for x in st.session_state.secondary_goals if x in SECONDARY_OPTIONS]))
        setv("training_years",st.number_input("S&C Experience (years)",0.0,30.0,float(st.session_state.training_years),0.5))
        setv("gym_days_available",st.slider("Gym Days / Week",1,7,int(st.session_state.gym_days_available)))
        setv("session_minutes",st.slider("Session Duration (min)",30,120,int(st.session_state.session_minutes),5))
        setv("equipment",st.multiselect("Available Equipment",EQUIPMENT,default=st.session_state.equipment))
    a=athlete(); st.markdown("---")
    c1,c2,c3,c4=st.columns(4); c1.metric("Model","Whole Athlete"); c2.metric("Level",training_level(a.training_years)); c3.metric("BMI",f"{bmi(a):.1f}"); c4.metric("Secondary Targets",len(a.secondary_goals))
    st.markdown('<div class="goal-card"><b>🎯 Interaction rule:</b> Primary goal sets emphasis; secondary goals remain active; sport demands, screening, readiness, equipment and calendar can override or reshape that emphasis.</div>',unsafe_allow_html=True)
    setv("notes",st.text_area("Coach Notes",st.session_state.notes,height=120))

# ============================================================
# MODULE 2 — LOAD / READINESS
# ============================================================
elif module=="2. Load, Injury & Readiness":
    st.markdown('<div class="banner-header">02 • External Load • Injury Screen • Readiness Gate</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:
        setv("team_days",st.slider("Team / Sport Sessions per Week",0,14,int(st.session_state.team_days)))
        setv("team_minutes",st.number_input("Average Team Session Minutes",0,300,int(st.session_state.team_minutes),5))
        setv("competition_days",st.slider("Competitions / Matches per Week",0,4,int(st.session_state.competition_days)))
        setv("weekly_sport_rpe",st.slider("Typical Sport Session RPE",1.0,10.0,float(st.session_state.weekly_sport_rpe),0.5))
    with c2:
        setv("sleep_hours",st.slider("Sleep (hours)",3.0,12.0,float(st.session_state.sleep_hours),0.5))
        setv("readiness",st.slider("Subjective Readiness",0,100,int(st.session_state.readiness)))
        setv("stress",st.slider("Stress",0,10,int(st.session_state.stress))); setv("soreness",st.slider("Soreness",0,10,int(st.session_state.soreness)))
    with c3:
        setv("pain_present",st.checkbox("Pain currently present",bool(st.session_state.pain_present))); setv("pain_score",st.slider("Pain score (0–10)",0,10,int(st.session_state.pain_score)))
        injury_opts=["Knee / ACL / MCL / Patellar","Hamstring","Ankle / Achilles","Shoulder / Rotator Cuff","Low Back","Groin / Adductor","Quadriceps","Wrist / Elbow","Other"]
        setv("injuries",st.multiselect("Current / recent injury history",injury_opts,default=[x for x in st.session_state.injuries if x in injury_opts]))
    a=athlete(); c=constraint_engine(a); band,txt=readiness_band(c["readiness"])
    st.markdown(f'<div class="hud-card"><span class="small-label">Decision Gate</span><div class="big-value">{c["readiness"]:.0f}/100 • {band}</div><div>{txt}</div></div>',unsafe_allow_html=True)
    if c["pain_gate"]: st.error("Pain gate active: normal high-impact/high-fatigue programming is blocked.")
    st.caption("The engine is coaching/programming decision support. It does not diagnose or rehabilitate injuries.")

# ============================================================
# MODULE 3 — SCREENING
# ============================================================
elif module=="3. Comprehensive Screening":
    st.markdown('<div class="banner-header">03 • Comprehensive Screening • ROM • SFMA-Compatible • 3-View Posture</div>',unsafe_allow_html=True)
    st.subheader("A. Range of Motion")
    cs=st.columns(5)
    fields=[("rom_ankle","Ankle Dorsiflexion (°)",0.0,50.0,0.5),("rom_hip_flex","Hip Flexion (°)",50.0,150.0,0.5),("rom_hip_ext","Hip Extension (°)",0.0,40.0,0.5),("rom_tspine","T-Spine Rotation (°)",10.0,70.0,0.5),("rom_shoulder","Shoulder Flexion (°)",90.0,180.0,0.5)]
    for col,(key,label,mn,mx,step) in zip(cs,fields):
        with col: setv(key,st.number_input(label,mn,mx,float(st.session_state[key]),step))
    st.markdown("---"); st.subheader("B. Three-View Postural Screen")
    st.caption("Coach-observed documentation. Photo references can be uploaded; the app does not diagnose structural conditions.")
    tabs=st.tabs(["Anterior View","Lateral View","Posterior View"])
    for tab,view in zip(tabs,["Anterior","Lateral","Posterior"]):
        with tab:
            key="posture_"+view.lower(); current=dict(st.session_state.get(key,{}))
            upload=st.file_uploader(f"Optional {view.lower()} photo",type=["png","jpg","jpeg"],key="upload_"+view.lower())
            if upload: st.image(upload,caption=view,use_container_width=True)
            cols=st.columns(2)
            for i,item in enumerate(POSTURE_FIELDS[view]):
                with cols[i%2]: current[item]=st.selectbox(item,POSTURE_OPTIONS,index=POSTURE_OPTIONS.index(current.get(item,"Not assessed")),key=f"{view}_{i}")
            setv(key,current)
    st.markdown("---"); st.subheader("C. SFMA-Compatible Movement Screen")
    st.caption("Record the coach's classification. Use the licensed/official protocol where applicable.")
    current=dict(st.session_state.get("movement_screen",{})); cols=st.columns(2)
    for i,pattern in enumerate(MOVEMENT_SCREEN_PATTERNS):
        with cols[i%2]: current[pattern]=st.selectbox(pattern,MOVEMENT_SCREEN_OPTIONS,index=MOVEMENT_SCREEN_OPTIONS.index(current.get(pattern,"Not assessed")),key=f"ms_{i}")
    setv("movement_screen",current)
    a=athlete(); flags=screening_flags(a); c1,c2,c3,c4=st.columns(4)
    c1.metric("Screen Flags",len(flags)); c2.metric("ROM Flags",sum("Limited" in f for f in flags)); c3.metric("Postural Flags",sum(any(v in f for v in ["Anterior:","Lateral:","Posterior:"]) for f in flags)); c4.metric("Painful Movement",sum("painful" in f.lower() for f in flags))
    for f in flags: st.warning(f)

# ============================================================
# MODULE 4 — PERFORMANCE TESTING
# ============================================================
elif module=="4. Performance Testing":
    st.markdown('<div class="banner-header">04 • Performance Testing</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:
        setv("cmj",st.number_input("Countermovement Jump (cm)",5.0,100.0,float(st.session_state.cmj),0.5)); setv("broad_jump",st.number_input("Broad Jump (cm)",50.0,350.0,float(st.session_state.broad_jump),1.0))
        setv("left_jump",st.number_input("Single-Leg Jump Left (cm)",5.0,250.0,float(st.session_state.left_jump),0.5)); setv("right_jump",st.number_input("Single-Leg Jump Right (cm)",5.0,250.0,float(st.session_state.right_jump),0.5))
    with c2:
        setv("sprint_5m",st.number_input("5m Sprint (s)",0.50,4.00,float(st.session_state.sprint_5m),0.01)); setv("sprint_10m",st.number_input("10m Sprint (s)",1.00,5.00,float(st.session_state.sprint_10m),0.01))
        setv("cod",st.number_input("COD / T-Drill (s)",5.00,30.00,float(st.session_state.cod),0.01)); setv("cooper_m",st.number_input("12-Min Cooper Distance (m)",500.0,5000.0,float(st.session_state.cooper_m),50.0))
    with c3:
        setv("squat_1rm",st.number_input("Back Squat 1RM (kg)",20.0,350.0,float(st.session_state.squat_1rm),2.5)); setv("bench_1rm",st.number_input("Bench Press 1RM (kg)",20.0,250.0,float(st.session_state.bench_1rm),2.5)); setv("ohp_1rm",st.number_input("Overhead Press 1RM (kg)",10.0,180.0,float(st.session_state.ohp_1rm),1.0))
        setv("pullups",st.number_input("Max Pull-Ups",0,60,int(st.session_state.pullups),1)); setv("pushups",st.number_input("Max Push-Ups",0,120,int(st.session_state.pushups),1))
    if a.sport in ["Tennis","Racket Sports (Squash/Padel)"]:
        st.markdown("### 🎾 Racket-Sport Power Battery")
        r1,r2,r3,r4=st.columns(4)
        with r1: setv("forehand_throw_m",st.number_input("Forehand Throw (m)",1.0,30.0,float(st.session_state.forehand_throw_m),0.1))
        with r2: setv("backhand_throw_m",st.number_input("Backhand Throw (m)",1.0,30.0,float(st.session_state.backhand_throw_m),0.1))
        with r3: setv("rotational_throw_m",st.number_input("Rotational Scoop Toss (m)",1.0,30.0,float(st.session_state.rotational_throw_m),0.1))
        with r4: setv("overhead_throw_m",st.number_input("Overhead Throw (m)",1.0,30.0,float(st.session_state.overhead_throw_m),0.1))
        asym=asymmetry(a.forehand_throw_m,a.backhand_throw_m)
        rr1,rr2=st.columns(2); rr1.metric("Forehand / Backhand Asymmetry",f"{asym:.1f}%"); rr2.metric("Rotational Power Index",f"{performance_scores(a)['Rotational Power']:.0f}/100")
        st.caption("Use the same standardized medicine-ball mass, technique, distance convention and testing conditions each time. The app treats these as performance tests, not diagnostic tests.")
    a=athlete(); scores=performance_scores(a); vals=[("Relative Squat",relative_strength(a.squat_1rm,a.weight_kg)),("Relative Bench",relative_strength(a.bench_1rm,a.weight_kg)),("Jump Asymmetry",asymmetry(a.left_jump,a.right_jump)),("Estimated VO₂max",(a.cooper_m-504.9)/44.73)]
    cols=st.columns(4)
    for c,(lab,val) in zip(cols,vals): c.metric(lab,f"{val:.1f}" if "VO₂" in lab else f"{val:.2f}")

# ============================================================
# MODULE 5 — DECISION TREE
# ============================================================
elif module=="5. Decision Tree":
    st.markdown('<div class="banner-header">05 • Whole-Athlete Decision Tree</div>',unsafe_allow_html=True)
    a=athlete(); trace,engine=decision_trace(a,plan_months); c=engine["constraints"]; p=engine["priorities"]; systems=engine["systems"]
    c1,c2,c3,c4=st.columns(4); c1.metric("Readiness",f"{c['readiness']:.0f}/100"); c2.metric("Gate",c["band"]); c3.metric("Top Quality",next(iter(p))); c4.metric("Top System",next(iter(systems)))
    st.markdown("### Decision path")
    for title,text in trace:
        st.markdown(f'<div class="decision-card"><span class="rule">{title}</span><br>{text}</div>',unsafe_allow_html=True)
    st.markdown("### Priority distribution")
    st.dataframe(pd.DataFrame({"Quality":list(p.keys()),"Priority %":list(p.values())}),use_container_width=True,hide_index=True)
    st.markdown("### System allocation")
    st.dataframe(pd.DataFrame({"System":list(systems.keys()),"Signal":list(systems.values())}),use_container_width=True,hide_index=True)
    if c["screen_flags"]: st.warning(f"{len(c['screen_flags'])} screening findings are feeding back into selection and dose.")
    cx=choose_complex(a,p,systems,c,1)
    if cx:
        st.markdown("### ⚡ Advanced Method Eligibility")
        st.success(f"Eligible complex: {cx.name} • {cx.method} • {', '.join(cx.exercises)}")
    else:
        st.info("No advanced complex selected under the current readiness, training-level, equipment and safety gates.")

# ============================================================
# MODULE 6 — PROGRAM
# ============================================================
elif module=="6. Adaptive Program Generator":
    st.markdown('<div class="banner-header">06 • Adaptive Multi-Month Program Generator</div>',unsafe_allow_html=True)
    a=athlete(); program,engine=build_program(a,plan_months); st.session_state.generated_plan=program; st.session_state.decision_state=engine; st.session_state.rotation_map=engine["rotation"]
    c=engine["constraints"]; p=engine["priorities"]; systems=engine["systems"]
    st.markdown(f'<div class="goal-card"><b>Whole-athlete architecture:</b> {a.primary_goal} + {", ".join(a.secondary_goals) if a.secondary_goals else "balanced secondary development"}. Every upstream change is propagated through safety, priorities, system allocation, exercise choice, dose and conditioning.</div>',unsafe_allow_html=True)
    c1,c2,c3,c4,c5=st.columns(5); c1.metric("Readiness",f"{c['readiness']:.0f}/100"); c2.metric("Top Priority",next(iter(p))); c3.metric("Top System",next(iter(systems))); c4.metric("Gym Days",a.gym_days_available); c5.metric("Months",plan_months)
    for m in range(1,plan_months+1):
        with st.expander(f"MONTH {m} • Adaptive Rotation",expanded=(m==1)):
            rot=[]
            for system,eid in engine["rotation"].get(m,{}).items(): rot.append(f"**{system}:** {EXERCISES[eid].name}")
            st.markdown(" • ".join(rot) if rot else "No compatible exercise found for this system/equipment profile.")
            st.caption("Rotation preserves the training objective while changing suitable exercise variants; it is constrained by screening, injuries, equipment, level and fatigue.")
            tabs=st.tabs([f"Week {w}" for w in range(1,5)])
            for w,tab in enumerate(tabs,1):
                with tab:
                    ref=weekly_load_reference(a,w)
                    st.markdown(f"**{phase_for(a,w)}** • Resistance reference {ref['sets']}×{ref['reps']} @ {ref['pct']*100:.0f}% • Target RPE {ref['rpe']:g}")
                    for session in program[m][w]:
                        st.markdown(f"<div class='banner-header' style='font-size:1.05rem'>DAY {session['day']} • {session['phase']} • Readiness {session['readiness']:.0f}/100</div>",unsafe_allow_html=True)
                        render_session(a,session,w,engine)
                        st.markdown("---")
    st.warning("Coaching/programming software only. It does not diagnose injuries or replace qualified clinical assessment.")

# ============================================================
# MODULE 7 — FEEDBACK / REASSESSMENT
# ============================================================
elif module=="7. Feedback / Reassessment":
    st.markdown('<div class="banner-header">07 • Feedback Loop — Today Changes Tomorrow</div>',unsafe_allow_html=True)
    st.write("This module closes the loop: completed-session feedback becomes a new input to the same decision engine.")
    c1,c2,c3=st.columns(3)
    with c1: session_rpe=st.slider("Last Session RPE",1.0,10.0,7.0,0.5)
    with c2: pain_after=st.slider("Pain During/After Session",0,10,0)
    with c3: performance_change=st.slider("Performance vs. Previous Exposure",-2,2,0)
    if st.button("🔄 APPLY FEEDBACK TO NEXT DECISION",type="primary"):
        st.session_state.feedback["session_rpe"].append(float(session_rpe)); st.session_state.feedback["pain"].append(int(pain_after)); st.session_state.feedback["performance"].append(int(performance_change))
        a=athlete(); base=constraint_engine(a); adapted=apply_feedback(base,session_rpe,pain_after,performance_change); st.session_state.decision_state={"constraints":adapted,"feedback_applied":True}
        st.success("Feedback applied. The next program generation will use the updated load gate.")
    if st.session_state.feedback["session_rpe"]:
        st.dataframe(pd.DataFrame(st.session_state.feedback),use_container_width=True,hide_index=True)
    st.markdown("### Reassessment triggers")
    st.write("• Persistent pain → safety gate remains active.\n• Unexpectedly high session RPE → reduce future volume/intensity.\n• Good performance + acceptable RPE → progression can be considered.\n• End of mesocycle → re-test key performance qualities and regenerate priorities.")

# ============================================================
# MODULE 8 — DATA / PROFILES
# ============================================================
elif module=="8. Data / Profiles":
    st.markdown('<div class="banner-header">08 • Profiles • Historical Snapshots • Export</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("💾 Save Current Profile"):
            st.session_state.profiles[st.session_state.name]=dict((k,st.session_state[k]) for k in DEFAULTS); st.success("Profile saved in this Streamlit session.")
    with c2:
        if st.button("📸 Save Assessment Snapshot"):
            a=athlete(); rec=dict((k,st.session_state[k]) for k in DEFAULTS); rec.update({"timestamp":datetime.now().isoformat(timespec="seconds"),"readiness_score":readiness_score(a),"top_priority":next(iter(priorities(a)))})
            st.session_state.records.append(rec); st.success("Snapshot saved.")
    with c3:
        if st.button("🧹 Clear Session Data"):
            st.session_state.records=[]; st.session_state.profiles={}; st.session_state.generated_plan=None; st.session_state.decision_state=None; st.success("Session data cleared.")
    if st.session_state.profiles:
        names=list(st.session_state.profiles); selected=st.selectbox("Saved Profiles",names)
        if st.button("Load Selected Profile"):
            for k,v in st.session_state.profiles[selected].items(): st.session_state[k]=v
            st.session_state.generated_plan=None; st.session_state.decision_state=None; st.rerun()
    if st.session_state.records:
        st.subheader("Historical Assessment Records"); st.dataframe(pd.DataFrame(st.session_state.records),use_container_width=True,hide_index=True)
        st.download_button("⬇️ Download CSV",pd.DataFrame(st.session_state.records).to_csv(index=False),"athlete_iq_history.csv","text/csv")
    payload=json.dumps(dict((k,st.session_state[k]) for k in DEFAULTS),default=str,indent=2)
    st.download_button("⬇️ Export Current Athlete JSON",payload,"athlete_iq_profile.json","application/json")

st.markdown("---")
st.caption("Athlete-IQ v5 • Rule-based coaching software. Screening thresholds and performance classifications are heuristics unless explicitly validated. The engine is designed so upstream changes propagate downstream; it does not diagnose or prescribe medical treatment.")
