import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

# ============================================================
# ATHLETE-IQ v5 - WHOLE-ATHLETE DECISION + COMPLEX TRAINING ENGINE
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
# HUD UI - preserves the v3 visual language
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
    "Handball": {"Strength":.14,"Hypertrophy":.03,"Power":.20,"Acceleration":.10,"COD":.14,"Aerobic":.12,"Anaerobic":.12,"Stability":.11,"Mobility":.08},
    "Boxing": {"Strength":.13,"Hypertrophy":.02,"Power":.24,"Acceleration":.10,"COD":.08,"Aerobic":.15,"Anaerobic":.16,"Stability":.08,"Mobility":.04},
    "MMA": {"Strength":.16,"Hypertrophy":.03,"Power":.21,"Acceleration":.08,"COD":.07,"Aerobic":.14,"Anaerobic":.16,"Stability":.10,"Mobility":.08},
    "Track & Field (Sprints/Jumps)": {"Strength":.18,"Hypertrophy":.02,"Power":.22,"Acceleration":.22,"COD":.04,"Aerobic":.05,"Anaerobic":.08,"Stability":.10,"Mobility":.09},
    "Rugby/American Football": {"Strength":.22,"Hypertrophy":.06,"Power":.18,"Acceleration":.14,"COD":.09,"Aerobic":.08,"Anaerobic":.10,"Stability":.08,"Mobility":.05},
    "Swimming": {"Strength":.14,"Hypertrophy":.04,"Power":.12,"Acceleration":.04,"COD":.01,"Aerobic":.28,"Anaerobic":.13,"Stability":.13,"Mobility":.11},
    "Karate": {"Strength":.12,"Hypertrophy":.02,"Power":.22,"Acceleration":.15,"COD":.16,"Aerobic":.10,"Anaerobic":.17,"Stability":.09,"Mobility":.09},
}
SPORT_POSITIONS = {
    "General Fitness":["General"],
    "Soccer":["Goalkeeper","Center Back","Full Back","Midfielder","Winger","Striker"],
    "Basketball":["Guard","Wing","Forward","Center"],
    "Tennis":["Singles","Doubles"],
    "Racket Sports (Squash/Padel)":["Singles","Doubles"],
    "Volleyball":["Setter","Outside Hitter","Opposite","Middle Blocker","Libero"],
    "Handball":["Wing","Backcourt","Pivot","Goalkeeper"],
    "Boxing":["Amateur / Competitive Boxing","Professional Boxing"],
    "MMA":["MMA"],
    "Track & Field (Sprints/Jumps)":["100m/200m","400m","Long Jump","High Jump"],
    "Rugby/American Football":["Forward/Front Seven","Back/Skill Position","Hybrid"],
    "Swimming":["Freestyle","Backstroke","Breaststroke","Butterfly","Individual Medley"],
    "Karate":["Kumite","Kata","Kumite + Kata"],
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
    rest_between: str = "15-30 s"
    rest_rounds: str = "2-3 min"
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
    secondary_positions: List[str]
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
    fms_scores: Dict[str,int] = field(default_factory=dict)
    fms_sides: Dict[str,Dict[str,int]] = field(default_factory=dict)
    sfma_results: Dict[str,str] = field(default_factory=dict)
    mobility_rom: Dict[str,Dict[str,float]] = field(default_factory=dict)
    stability_tests: Dict[str,float] = field(default_factory=dict)
    neuromuscular_tests: Dict[str,float] = field(default_factory=dict)
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
    ex("bx1","Shadow Boxing - Technical Flow","Agility / COD","Sport Skill",["Reaction","Coordination","Work Capacity"],["Bodyweight"],"Beginner",plane="Multi-planar",fatigue=2,sport_tags=["Boxing"],tags=["Boxing","Shadow Boxing"]),
    ex("bx2","Shadow Boxing - High Output Flurries","Anaerobic / Repeated Sprint","Sport Conditioning",["Anaerobic","Speed","Work Capacity"],["Bodyweight"],"Beginner",plane="Multi-planar",fatigue=3,sport_tags=["Boxing"],tags=["Boxing","Shadow Boxing"]),
    ex("bx3","Boxing Reaction Callout Drill","Agility / COD","Reactive Striking",["Reaction","Agility","Coordination"],["Bodyweight"],"Intermediate",plane="Multi-planar",fatigue=3,sport_tags=["Boxing"],tags=["Boxing","Reaction"]),
    ex("bx4","Slip -> Roll -> Counter Shadow Sequence","Agility / COD","Defensive Footwork",["Agility","Reaction","COD"],["Bodyweight"],"Intermediate",plane="Multi-planar",fatigue=3,sport_tags=["Boxing"],tags=["Boxing","Footwork"]),
    ex("bx5","Medicine-Ball Punch Throw","Plyometrics","Upper-Body Rotation",["Power","Rotation","Speed"],["Medicine & Slam Balls"],"Intermediate",plane="Transverse",fatigue=2,sport_tags=["Boxing"],tags=["Boxing","Punch Power"]),
    ex("kz1","Karate Shadow Kumite - Technical Flow","Agility / COD","Sport Skill",["Reaction","Coordination","Agility"],["Bodyweight"],"Beginner",plane="Multi-planar",fatigue=2,sport_tags=["Karate"],tags=["Karate","Kumite","Shadow"]),
    ex("kz2","Karate Reaction Callout - Strike / Check / Exit","Agility / COD","Reactive Striking",["Reaction","Agility","COD"],["Bodyweight","Cones / Timing Gates"],"Intermediate",plane="Multi-planar",fatigue=3,sport_tags=["Karate"],tags=["Karate","Kumite","Reaction"]),
    ex("kz3","Medicine-Ball Rotational Punch Throw","Plyometrics","Rotational Throw",["Power","Rotation","Speed"],["Medicine & Slam Balls"],"Intermediate",plane="Transverse",fatigue=2,sport_tags=["Karate"],tags=["Karate","Power","Kumite"]),
    ex("kz4","Split-Stance Punch -> Lateral Exit","Agility / COD","Acceleration / COD",["Acceleration","COD","Agility"],["Bodyweight","Cones / Timing Gates"],"Intermediate",plane="Multi-planar",fatigue=3,sport_tags=["Karate"],tags=["Karate","Footwork"]),
    ex("kz5","Band-Resisted Straight Punch","Resistance","Sport-Specific Push",["Strength","Power","Speed"],["Bands"],"Beginner",plane="Transverse",fatigue=2,sport_tags=["Karate"],tags=["Karate","Punch"]),
    ex("sw1","SkiErg Swim-Pull Intervals","Aerobic","Swim-Specific Pull",["Aerobic","Work Capacity","Pulling"],["Ergometers (AirBike/Rower/SkiErg)"],"Beginner",fatigue=3,sport_tags=["Swimming"],tags=["Swimming","Pull"]),
    ex("sw2","Straight-Arm Cable Pulldown","Resistance","Swim Pull",["Strength","Strength Endurance"],["Cable Systems & Selectorized"],"Beginner",fatigue=2,sport_tags=["Swimming"],tags=["Swimming","Lat"]),
    ex("sw3","Band Straight-Arm Swim Pull","Resistance","Swim Pull",["Strength Endurance","Stability"],["Bands"],"Beginner",fatigue=1,sport_tags=["Swimming"],tags=["Swimming","Scapular"]),
    ex("sw4","Prone Y-T-W","Corrective / Activation","Scapular",["Stability","Movement Quality"],["Bodyweight","Bands"],"Beginner",fatigue=1,sport_tags=["Swimming"],tags=["Swimming","Scapular"]),
    ex("sw5","Medicine-Ball Streamline Slam","Plyometrics","Overhead Ballistic",["Power","Core / Trunk"],["Medicine & Slam Balls"],"Intermediate",fatigue=2,sport_tags=["Swimming"],tags=["Swimming","Power"]),
    ex("sw6","Swimmer Hollow-Body Hold","Stability / Core","Streamline Core",["Core / Trunk","Stability"],["Bodyweight"],"Beginner",fatigue=1,sport_tags=["Swimming"],tags=["Swimming","Streamline"]),
]
EXERCISES = {x.id:x for x in E}

# ============================================================
# ADVANCED COMPOUND / COMPLEX / CONTRAST LIBRARY
# ============================================================
COMPLEXES = [
    TrainingComplex("cx1","Squat -> Vertical Jump","Contrast","Power",["Strength"],["r1","p1"],sport_tags=["Soccer","Basketball","Volleyball","Rugby/American Football"],min_level="Advanced",impact="High",fatigue=4,equipment=["Barbells & Plates"],notes="High-force squat paired with a biomechanically related jump."),
    TrainingComplex("cx2","Trap-Bar Deadlift -> Broad Jump -> Sprint","Complex","Acceleration",["Power","Speed"],["r6","p2","s2"],sport_tags=["Soccer","Rugby/American Football","Track & Field (Sprints/Jumps)"],min_level="Advanced",impact="High",fatigue=5,equipment=["Barbells & Plates"],rest_between="20-30 s",rest_rounds="3 min"),
    TrainingComplex("cx3","RFESS -> Lateral Bound -> COD","Complex","Agility",["Strength","Power","COD"],["r4","p3","a3"],sport_tags=["Soccer","Basketball","Tennis","Racket Sports (Squash/Padel)"],min_level="Advanced",impact="High",fatigue=4,equipment=["Dumbbells"],rest_between="20-30 s",rest_rounds="2-3 min"),
    TrainingComplex("cx4","Bench Press -> Medicine-Ball Chest Pass","Contrast","Upper-Body Power",["Strength","Power"],["r9","p4"],sport_tags=["Combat Sports (MMA/Boxing)","Rugby/American Football","Basketball"],min_level="Advanced",impact="Moderate",fatigue=3,equipment=["Barbells & Plates","Medicine & Slam Balls"],rest_between="15-20 s",rest_rounds="2-3 min"),
    TrainingComplex("cx5","Rotational Scoop Toss -> Landmine Rotation -> Lateral Sprint","Sport Power Complex","Rotational Power",["Power","COD","Acceleration"],["p5","r13","a2"],sport_tags=["Tennis","Racket Sports (Squash/Padel)","Combat Sports (MMA/Boxing)"],min_level="Intermediate",impact="Moderate",fatigue=3,equipment=["Medicine & Slam Balls","Barbells & Plates","Cones / Timing Gates"],rest_between="20-30 s",rest_rounds="2-3 min"),
    TrainingComplex("cx6","Front Squat -> Box Jump","Contrast","Power",["Strength","Plyometric Ability"],["r3","p2"],sport_tags=["Basketball","Volleyball","Soccer","Track & Field (Sprints/Jumps)"],min_level="Advanced",impact="High",fatigue=4,equipment=["Barbells & Plates","Plyo Boxes & Agility Ladders"],rest_between="15-30 s",rest_rounds="3 min"),
    TrainingComplex("cx7","Push Press -> Med-Ball Overhead Throw","Complex","Upper-Body Power",["Strength","Power"],["r12","p6"],sport_tags=["Volleyball","Combat Sports (MMA/Boxing)","Rugby/American Football"],min_level="Intermediate",impact="Moderate",fatigue=3,equipment=["Barbells & Plates","Medicine & Slam Balls"],rest_between="20-30 s",rest_rounds="2 min"),
    TrainingComplex("cx8","Lateral Bound -> Stick -> Reactive Cone Drill","Agility Complex","Agility",["Plyometric Ability","COD","Stability"],["a6","a2","a5"],sport_tags=["Tennis","Racket Sports (Squash/Padel)","Soccer","Basketball"],min_level="Intermediate",impact="High",fatigue=3,equipment=["Cones / Timing Gates"],rest_between="20-30 s",rest_rounds="2 min"),
    TrainingComplex("cx9","Kettlebell Swing -> Sled Push -> Shuttle","Power-Endurance Complex","Anaerobic",["Power","Work Capacity","Acceleration"],["r14","n4","n2"],sport_tags=["Soccer","Basketball","Rugby/American Football","General Fitness"],min_level="Intermediate",impact="Moderate",fatigue=5,equipment=["Kettlebells","Sleds & Prowler","Cones / Timing Gates"],rest_between="30-45 s",rest_rounds="2-3 min"),
]
COMPLEXES.append(TrainingComplex("cx12","Karate Rotational Throw -> Split-Stance Strike -> Reactive Exit","Karate Sport Power Complex","Rotational Power",["Power","Acceleration","COD"],["kz3","kz4","kz2"],sport_tags=["Karate"],min_level="Intermediate",impact="Moderate",fatigue=4,equipment=["Medicine & Slam Balls","Cones / Timing Gates"],rest_between="20-30 s",rest_rounds="2-3 min"))
COMPLEXES_BY_ID={c.id:c for c in COMPLEXES}

# ============================================================
# SCREENING / WARM-UP DATA
# ============================================================
# Structured postural-observation taxonomy. This is intentionally an observation
# screen, not a medical diagnosis. Findings are coach-observed and should be
# confirmed by an appropriately qualified clinician when clinically relevant.
POSTURE_SEVERITY = ["Not assessed", "None / neutral", "Mild", "Moderate", "Marked"]
POSTURE_FINDINGS = {
    "Anterior": {
        "Head / neck": ["Not assessed", "Neutral", "Forward head", "Head tilt", "Head rotation asymmetry"],
        "Shoulder height": ["Not assessed", "Level", "Right elevated", "Left elevated", "Right depressed", "Left depressed"],
        "Pelvic level": ["Not assessed", "Level", "Right pelvic hike", "Left pelvic hike", "Pelvic rotation asymmetry"],
        "Knee alignment": ["Not assessed", "Neutral", "Dynamic/static valgus appearance", "Varus appearance", "Hyperextension appearance"],
        "Foot / arch position": ["Not assessed", "Neutral", "Excessive pronation", "Supination", "Toe-out", "Toe-in", "Arch asymmetry"],
    },
    "Lateral": {
        "Head position": ["Not assessed", "Neutral", "Forward head", "Chin protraction", "Excessive extension"],
        "Shoulder position": ["Not assessed", "Neutral", "Rounded / protracted", "Retracted", "Anterior shoulder translation"],
        "Thoracic curve": ["Not assessed", "Neutral", "Increased kyphotic posture", "Reduced kyphotic posture", "Thoracic asymmetry"],
        "Lumbar curve": ["Not assessed", "Neutral", "Increased lordotic posture", "Reduced lordotic posture", "Lumbar asymmetry"],
        "Pelvic tilt": ["Not assessed", "Neutral", "Anterior pelvic tilt", "Posterior pelvic tilt", "Pelvic rotation"],
        "Knee position": ["Not assessed", "Neutral", "Hyperextension posture", "Flexed posture", "Anterior/posterior translation"],
        "Ankle / foot": ["Not assessed", "Neutral", "Limited dorsiflexed posture", "Excessive pronation", "Supination", "Heel lift asymmetry"],
    },
    "Posterior": {
        "Scapular position": ["Not assessed", "Neutral", "Scapular winging", "Scapular elevation", "Scapular depression", "Scapular protraction", "Scapular asymmetry"],
        "Spinal alignment": ["Not assessed", "Neutral", "Lateral shift", "Lateral curvature appearance", "Thoracic asymmetry", "Lumbar asymmetry"],
        "Pelvic level": ["Not assessed", "Level", "Right pelvic hike", "Left pelvic hike", "Pelvic rotation asymmetry"],
        "Knee alignment": ["Not assessed", "Neutral", "Valgus appearance", "Varus appearance", "Knee height asymmetry"],
        "Foot / heel alignment": ["Not assessed", "Neutral", "Heel eversion", "Heel inversion", "Excessive pronation", "Supination", "Foot asymmetry"],
    },
}
# Backward-compatible aliases for older saved profiles.
POSTURE_OPTIONS = POSTURE_SEVERITY
POSTURE_FIELDS = {view: list(fields.keys()) for view, fields in POSTURE_FINDINGS.items()}
MOVEMENT_SCREEN_PATTERNS = ["Deep Squat","Hurdle Step","Inline Lunge","Shoulder Mobility","Active Straight Leg Raise","Trunk Stability Push-Up","Rotary Stability"]
MOVEMENT_SCREEN_OPTIONS = ["Not assessed","FN - Functional / Non-painful","FP - Functional / Painful","DN - Dysfunctional / Non-painful","DP - Dysfunctional / Painful"]
SPORT_WARMUPS = {
    "Soccer":["Dynamic Hamstring Sweeps","Ankle Mobility + Single-Leg Balance","Multi-Directional Shuttles"],
    "Basketball":["Ankle/Achilles Prep","Landing Mechanics","Reactive Jump Hops"],
    "Tennis":["Wrist/Forearm Rotations","T-Spine Openers","Lateral Multi-Directional Shuttles"],
    "Racket Sports (Squash/Padel)":["Wrist/Forearm Rotations","T-Spine Openers","Lateral Multi-Directional Shuttles"],
    "Volleyball":["Scapular Activation","Ankle Stiffness Hops","Lateral Bounds + Block Hops"],
    "Boxing":["T-Spine Windmills","Hip 90/90 Flow","Footwork + Shadow Boxing Flow","Scapular/Shoulder Prep"],
    "MMA":["T-Spine Windmills","Hip 90/90 Flow","Footwork + Sprawl Prep"],
    "Track & Field (Sprints/Jumps)":["A-Skips / Ankling","Dynamic Hamstring Sweeps","Acceleration Wall Drills"],
    "Rugby/American Football":["Neck Prep","Groin/Adductor Mobility","Resisted Acceleration Starts"],
    "Swimming":["Shoulder CARs","Scapular Activation","T-Spine Rotation","Streamline Core Prep"],
    "Karate":["Hip 90/90 Flow","Ankle + Calf Prep","T-Spine Rotation","Karate Footwork + Shadow Kumite"],
    "General Fitness":["World's Greatest Stretch","Band Pull-Aparts + Glute Bridges","Bodyweight Squats + Arm Circles"],
}

# ============================================================
# DEFAULTS / STATE
# ============================================================
DEFAULTS = {
    "name":"New Athlete","age":25,"sex":"Male","height_cm":180.0,"weight_kg":80.0,
    "sport":"General Fitness","position":"General","secondary_positions":[],"primary_goal":"Overall Development",
    "secondary_goals":["Strength","Mobility","Stability"],"season":"General / No Competition",
    "competition_days":0,"team_days":0,"team_minutes":0,"gym_days_available":3,"session_minutes":60,
    "training_years":2.0,"equipment":EQUIPMENT.copy(),"injuries":[],"pain_present":False,"pain_score":0,
    "sleep_hours":7.5,"readiness":80,"stress":3,"soreness":3,"weekly_sport_rpe":6.0,"weekly_steps_or_activity":7000,
    "rom_ankle":35.0,"rom_hip_flex":120.0,"rom_hip_ext":15.0,"rom_tspine":45.0,"rom_shoulder":170.0,
    "cmj":40.0,"broad_jump":210.0,"sprint_5m":1.10,"sprint_10m":1.80,"cod":10.50,"squat_1rm":100.0,
    "bench_1rm":70.0,"ohp_1rm":45.0,"pullups":8,"pushups":30,"cooper_m":2400.0,"left_jump":105.0,"right_jump":104.0,
    "posture_anterior":{},"posture_lateral":{},"posture_posterior":{},"movement_screen":{},
    "fms_scores":{"Deep Squat":2,"Hurdle Step":2,"Inline Lunge":2,"Shoulder Mobility":2,"ASLR":2,"Trunk Stability Push-Up":2,"Rotary Stability":2},
    "fms_sides":{"Hurdle Step":{"L":2,"R":2},"Inline Lunge":{"L":2,"R":2},"Shoulder Mobility":{"L":2,"R":2},"ASLR":{"L":2,"R":2},"Rotary Stability":{"L":2,"R":2}},
    "sfma_results":{},
    "mobility_rom":{
        "Cervical Flexion":{"L":50.0,"R":50.0},"Cervical Extension":{"L":60.0,"R":60.0},"Cervical Rotation":{"L":70.0,"R":70.0},
        "Shoulder Flexion":{"L":170.0,"R":170.0},"Shoulder Abduction":{"L":170.0,"R":170.0},"Shoulder IR":{"L":60.0,"R":60.0},"Shoulder ER":{"L":90.0,"R":90.0},
        "Thoracic Rotation":{"L":45.0,"R":45.0},
        "Hip Flexion":{"L":120.0,"R":120.0},"Hip Extension":{"L":15.0,"R":15.0},"Hip Abduction":{"L":45.0,"R":45.0},"Hip Adduction":{"L":30.0,"R":30.0},"Hip IR":{"L":35.0,"R":35.0},"Hip ER":{"L":45.0,"R":45.0},
        "Knee Flexion":{"L":135.0,"R":135.0},"Ankle Dorsiflexion":{"L":35.0,"R":35.0},"Ankle Plantarflexion":{"L":50.0,"R":50.0},"Ankle Inversion":{"L":30.0,"R":30.0},"Ankle Eversion":{"L":15.0,"R":15.0},
        "Wrist Flexion":{"L":80.0,"R":80.0},"Wrist Extension":{"L":70.0,"R":70.0}
    },
    "stability_tests":{"Single-Leg Stance L":30.0,"Single-Leg Stance R":30.0,"Y Balance ANT L":70.0,"Y Balance ANT R":70.0,"Y Balance PM L":100.0,"Y Balance PM R":100.0,"Y Balance PL L":100.0,"Y Balance PL R":100.0,"Landing Control":80.0,"Trunk Stability":80.0,"Single-Leg Squat Control L":80.0,"Single-Leg Squat Control R":80.0},
    "neuromuscular_tests":{"Reaction Time":0.75,"Proprioception L":80.0,"Proprioception R":80.0,"Reactive Balance":80.0,"Coordination L":80.0,"Coordination R":80.0,"Dual Task":80.0},
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
# STAGE 1 - CONSTRAINT ENGINE
# ============================================================
def screening_flags(a):
    flags=[]
    for view,d in [("Anterior",a.posture_anterior),("Lateral",a.posture_lateral),("Posterior",a.posture_posterior)]:
        for item,val in d.items():
            # New format stores a structured observation string: finding || severity.
            # Legacy profiles may still contain the old severity-only values.
            if isinstance(val, str) and " || " in val:
                finding, severity = val.split(" || ", 1)
                if finding not in ("Not assessed", "Neutral", "Level") and severity not in ("Not assessed", "None / neutral"):
                    flags.append(f"{view}: {item} - {finding} ({severity})")
            elif val in ("Mild deviation", "Moderate deviation", "Marked deviation"):
                flags.append(f"{view}: {item} = {val}")
    for pattern,result in a.movement_screen.items():
        if result in ("FP - Functional / Painful","DP - Dysfunctional / Painful"):
            flags.append(f"Movement screen: {pattern} is painful")
        elif result=="DN - Dysfunctional / Non-painful":
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
# STAGE 2 - PERFORMANCE PROFILE
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
# STAGE 3 - GOAL + SPORT + GAP DECISION ENGINE
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
    goal_bonus={
        "Max Strength":{"Resistance":30},"Strength":{"Resistance":24},"Hypertrophy":{"Resistance":28},
        "Power":{"Plyometrics":24,"Resistance":10,"Acceleration / Speed":8},
        "Speed":{"Acceleration / Speed":30,"Plyometrics":12},"Agility":{"Agility / COD":30,"Plyometrics":10},
        "Endurance":{"Aerobic":30,"Anaerobic / Repeated Sprint":8},
        "Sport Performance":{"Plyometrics":18,"Acceleration / Speed":16,"Agility / COD":16},
        "Fat Loss":{"Aerobic":22,"Anaerobic / Repeated Sprint":18,"Resistance":10},
        "General Fitness":{"Resistance":12,"Aerobic":10,"Agility / COD":8},
        "Overall Development":{"Resistance":8,"Plyometrics":8,"Agility / COD":8,"Aerobic":8},
    }
    for system,bonus in goal_bonus.get(a.primary_goal,{}).items(): scores[system]=scores.get(system,0)+bonus
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
# STAGE 4 - EXERCISE SAFETY / MATCHING
# ============================================================
SPORT_COMPATIBILITY = {
    "Boxing":{"Boxing","Combat Sports (MMA/Boxing)"},
    "MMA":{"MMA","Combat Sports (MMA/Boxing)"},
    "Tennis":{"Tennis"},
    "Racket Sports (Squash/Padel)":{"Racket Sports (Squash/Padel)"},
}

def sport_tag_matches(tag,sport):
    if not tag or tag=="General Fitness": return True
    if tag==sport: return True
    if sport in SPORT_COMPATIBILITY and tag in SPORT_COMPATIBILITY[sport]: return True
    # Keep explicit combined tags compatible with their named member sports.
    if sport in tag and ("Combat Sports" in tag or "Racket Sports" in tag): return True
    return False

def exercise_sport_compatible(x,a):
    # Untagged exercises are transferable/general. Tagged exercises are locked to the tagged sport(s).
    if not x.sport_tags or "General Fitness" in x.sport_tags: return True
    return any(sport_tag_matches(tag,a.sport) for tag in x.sport_tags)

def exercise_allowed(x,a,constraints):
    if not any(eq in a.equipment for eq in x.equipment): return False
    if not exercise_sport_compatible(x,a): return False
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

def athlete_position_labels(a):
    return [a.position] + [x for x in getattr(a,"secondary_positions",[]) if x and x != a.position]

POSITION_KEYWORDS = {
    "Soccer": {
        "Goalkeeper":["reaction","lateral","stability","power"], "Center Back":["strength","acceleration","stability"],
        "Full Back":["acceleration","cod","aerobic"], "Midfielder":["aerobic","cod","work capacity"],
        "Winger":["acceleration","speed","cod"], "Striker":["power","acceleration","speed"]},
    "Basketball": {"Guard":["acceleration","cod","reaction"], "Wing":["power","speed","cod"], "Forward":["power","strength"], "Center":["strength","stability"]},
    "Volleyball": {"Setter":["reaction","stability","power"], "Outside Hitter":["power","jump","shoulder"], "Opposite":["power","jump","strength"], "Middle Blocker":["jump","power","lateral"], "Libero":["reaction","cod","stability"]},
    "Handball": {"Wing":["speed","cod","aerobic"], "Backcourt":["power","throw","cod"], "Pivot":["strength","power"], "Goalkeeper":["reaction","lateral","stability"]},
    "Tennis": {"Singles":["cod","aerobic","reaction"], "Doubles":["reaction","cod","acceleration"]},
    "Racket Sports (Squash/Padel)": {"Singles":["cod","aerobic","reaction"], "Doubles":["reaction","cod","acceleration"]},
    "Swimming": {"Freestyle":["pull","aerobic","streamline"], "Backstroke":["pull","shoulder","aerobic"], "Breaststroke":["hip","adductor","mobility"], "Butterfly":["power","shoulder","core"], "Individual Medley":["aerobic","mobility","whole-body"]},
    "Karate": {"Kumite":["reaction","cod","acceleration","rotation"], "Kata":["mobility","stability","control"], "Kumite + Kata":["reaction","cod","mobility"]},
}

def position_match_score(x,a):
    labels=athlete_position_labels(a)
    if not labels or labels==["General"]: return 0
    text=(x.name+" "+" ".join(x.tags)+" "+" ".join(x.quality)).lower()
    score=0.0
    sport_map=POSITION_KEYWORDS.get(a.sport,{})
    for label in labels:
        for kw in sport_map.get(label,[]):
            if kw.lower() in text:
                score += 8.0 if label==a.position else 3.0
    return score

PRIMARY_GOAL_SYSTEM_BONUS = {
    "Max Strength":{"Resistance":30},"Strength":{"Resistance":24},"Hypertrophy":{"Resistance":28},
    "Power":{"Plyometrics":24,"Resistance":10,"Acceleration / Speed":8},
    "Speed":{"Acceleration / Speed":30,"Plyometrics":12},
    "Agility":{"Agility / COD":30,"Plyometrics":10},
    "Endurance":{"Aerobic":30,"Anaerobic / Repeated Sprint":8},
    "Sport Performance":{"Plyometrics":18,"Acceleration / Speed":16,"Agility / COD":16},
    "Fat Loss":{"Aerobic":22,"Anaerobic / Repeated Sprint":18,"Resistance":10},
    "General Fitness":{"Resistance":12,"Aerobic":10,"Agility / COD":8},
    "Overall Development":{"Resistance":8,"Plyometrics":8,"Agility / COD":8,"Aerobic":8},
}

def exercise_score(x,a,p,system_scores,month,used_ids):
    score=0.0
    if exercise_sport_compatible(x,a) and a.sport in x.sport_tags: score+=24
    score += position_match_score(x,a)
    if "General Fitness" in x.sport_tags: score+=2
    score+=max([p.get(q,0) for q in x.quality]+[0])*.18
    score+=system_scores.get(x.system,0)*.10
    score+=PRIMARY_GOAL_SYSTEM_BONUS.get(a.primary_goal,{}).get(x.system,0)
    if x.unilateral and asymmetry(a.left_jump,a.right_jump)>=6: score+=10
    if x.id in used_ids: score-=30
    score-=x.fatigue*max(0,70-readiness_score(a))/100*8
    if a.season in ["In-Season / Competition","Taper / Peak"] and x.fatigue>=4: score-=10
    score += max(0,month-1)*0.4 if x.id not in used_ids else 0
    return score

def select_exercises(a,p,system_scores,system,n,month,used_ids,constraints):
    candidates=[x for x in E if x.system==system and exercise_allowed(x,a,constraints)]
    candidates.sort(key=lambda x:exercise_score(x,a,p,system_scores,month,used_ids),reverse=True)
    return candidates[:n]

# ============================================================
# STAGE 5 - DOSE / SEQUENCING / ENERGY SYSTEMS
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
    if not constraints["high_impact_allowed"]: return "2 x 3-5 low-impact contacts", "Full recovery", "Technique / landing quality"
    sets=2 if week==4 else 3 if week<3 else 4
    reps=3 if week>=2 else 4
    return f"{sets} x {reps} quality contacts", "90-150 s", "Max intent; stop when landing/height quality falls"

def agility_dose(a,week,constraints):
    sets=1 if week==4 or constraints["band"]=="RED" else 2 if constraints["band"]=="YELLOW" else 3
    return f"{sets} x 3-5 reps", "60-120 s", "Quality COD / reactive decision; avoid conditioning failure"

def speed_dose(a,week,constraints):
    sets=2 if week==4 else 3 if constraints["band"]=="YELLOW" else 4
    return f"{sets} x 10-30 m", "90-180 s", "Max intent; full recovery"

MESOCYCLE_PHASES = {
    1: "Foundation | Capacity + Movement Quality",
    2: "Development | Load + Density",
    3: "Specificity | Sport Transfer + Power-Endurance",
    4: "Realization | High Quality + Specificity",
    5: "Performance | Competition Support",
    6: "Performance | Competition Support",
}


def mesocycle_phase(a, month):
    # Competition phases override the generic calendar so the same 3-month
    # horizon can be used for both development and competitive athletes.
    if a.season == "In-Season / Competition":
        return ["Maintenance | Capacity", "Maintenance | Specific Repeatability", "Maintenance | Speed/Power", "Deload | Competition Support", "Maintenance | Specificity", "Maintenance | Specificity"][min(month-1,5)]
    if a.season == "Taper / Peak":
        return ["Specificity | Low Volume", "Specificity | Speed/Power", "Taper | High Quality", "Competition Readiness", "Competition Readiness", "Competition Readiness"][min(month-1,5)]
    return MESOCYCLE_PHASES.get(month, "Development | Progressive Variation")


def _has(a, equipment):
    return equipment in a.equipment


def _tool(a, family):
    # Pick one exact implement from the athlete's available equipment.
    choices = {
        "cyclical": [("Ergometers (AirBike/Rower/SkiErg)", "AirBike"), ("Bodyweight", "Tempo Run / Shuttle")],
        "sled": [("Sleds & Prowler", "Sled Push"), ("Bands", "Band-Resisted March")],
        "medball": [("Medicine & Slam Balls", "Medicine-Ball"), ("Dumbbells", "Dumbbell"), ("Bodyweight", "Bodyweight")],
        "load": [("Barbells & Plates", "Barbell"), ("Dumbbells", "Dumbbell"), ("Kettlebells", "Kettlebell")],
        "cone": [("Cones / Timing Gates", "Cone"), ("Bodyweight", "Line")],
    }
    for eq, label in choices.get(family, []):
        if _has(a, eq):
            return label
    return choices.get(family, [("Bodyweight", "Bodyweight")])[-1][1]


def conditioning_decision(a,p,constraints,week,month=1,day=1):
    """Build an executable ESD block from sport, gaps, secondary targets,
    readiness, mesocycle and day. The conditioning block is intentionally not
    a fixed monthly template: the training objective stays stable while the
    stimulus, density and exercise menu evolve.
    """
    phase = mesocycle_phase(a, month)
    # Safety first: recovery work remains executable and equipment-aware.
    if constraints["pain_gate"]:
        bike = _tool(a,"cyclical")
        return {"system":"Aerobic","name":"Low-Impact Recovery ESD - Day %d"%day,
                "stations":[f"Minute 1 - {bike}: 60 s easy @ RPE 4-5",
                            "Minute 2 - Walking: 40 s easy",
                            "Minute 3 - Mobility reset: 40 s",
                            "Minute 4 - Breathing reset: 30 s"],
                "work":"EMOM 16 min - 4 rounds","rest":"Remaining minute",
                "intensity":"RPE 4-5/10","reason":f"Pain/readiness gate | {phase}"}
    if constraints["band"]=="RED":
        bike = _tool(a,"cyclical")
        return {"system":"Aerobic","name":"Recovery Aerobic Circuit - Day %d"%day,
                "stations":[f"Minute 1 - {bike}: 60 s easy",
                            "Minute 2 - Walk: 45 s",
                            "Minute 3 - Mobility: 30 s",
                            "Minute 4 - Breathing: 30 s"],
                "work":"EMOM 16 min - 4 rounds","rest":"Remaining minute",
                "intensity":"RPE 4-5/10","reason":f"Low readiness | {phase}"}

    sport=a.sport
    racket = sport in ["Tennis","Racket Sports (Squash/Padel)"]
    court = sport in ["Soccer","Basketball","Volleyball","Handball"]
    boxing = sport=="Boxing"
    combat = sport=="MMA"
    swimming = sport=="Swimming"
    collision = sport=="Rugby/American Football"
    sprint = sport=="Track & Field (Sprints/Jumps)"
    cyc=_tool(a,"cyclical"); med=_tool(a,"medball"); sled=_tool(a,"sled")

    # Month controls the dominant conditioning stimulus.
    # Week controls density/volume; day rotates the station menu.
    if week==4:
        density="Deload: 3 rounds"; rounds=3; work_rpe="RPE 6/10"
    elif month==1:
        density="Base: 4 rounds"; rounds=4; work_rpe="RPE 6-7/10"
    elif month==2:
        density="Development: 4 rounds"; rounds=4; work_rpe="RPE 7-8/10"
    else:
        density="Specific: 4-5 rounds"; rounds=4 if week<3 else 5; work_rpe="RPE 7-9/10"

    # Secondary targets can intentionally redirect the ESD stimulus.
    target = ""
    if p.get("Anaerobic",0)>=p.get("Aerobic",0)+8 or "Anaerobic Capacity" in a.secondary_goals:
        target="anaerobic"
    elif p.get("Aerobic",0)>=p.get("Anaerobic",0)+8 or "Aerobic Capacity" in a.secondary_goals or "Recovery / Work Capacity" in a.secondary_goals:
        target="aerobic"
    elif p.get("COD",0)>=18 or "Agility" in a.secondary_goals:
        target="cod"
    else:
        target="mixed"

    if sport=="Karate":
        phase = "Base" if month==1 else "Development" if month==2 else "Specific / Peak"
        rounds={1:4,2:4,3:5,4:3}[week]
        patterns=[
            ["Minute 1 - Karate Shadow Kumite: 40 s technical flow","Minute 2 - Footwork: forward/back + lateral exit: 30 s","Minute 3 - Medicine-Ball Rotational Punch Throw: 4/side",f"Minute 4 - {cyc}: 30 s @ RPE 6-7"],
            ["Minute 1 - Karate Reaction Callout: 25 s","Minute 2 - Split-Stance Punch -> Lateral Exit: 20 s","Minute 3 - Medicine-Ball Rotational Punch Throw: 5/side",f"Minute 4 - {cyc}: 25 s hard / 35 s easy"],
            ["Minute 1 - Shadow Kumite: 15 s flurry / 15 s reset x 2","Minute 2 - Reactive Strike + Exit Callout: 20 s","Minute 3 - Band-Resisted Straight Punch: 8/side",f"Minute 4 - {cyc}: 15-20 s hard"],
        ]
        stations=patterns[(day+month-2)%len(patterns)]
        name=f"Karate {phase} Mixed ESD EMOM"
        return {"system":"Anaerobic / Repeated Sprint" if month>=2 else "Aerobic","name":name,"stations":stations,"work":f"EMOM {rounds*4} min - {rounds} rounds | sport-specific striking / footwork density","rest":"Remaining minute","intensity":work_rpe,"reason":f"Karate-specific reaction, striking, footwork, rotational power and repeat-effort conditioning | {phase}"}

    if boxing:
        day_variant = (day-1 + week-1) % 3
        if month==1:
            menus=[
                ["Minute 1 - Shadow Boxing: 40 s technical flow","Minute 2 - Footwork: forward/back + lateral: 30 s","Minute 3 - {med} Rotational Scoop Toss: 4/side","Minute 4 - {cyc}: 30 s @ RPE 6-7"],
                ["Minute 1 - Shadow Boxing: 30 s + 10 s reset","Minute 2 - Boxing Reaction Callout Drill: 20 s","Minute 3 - {med} Punch Throw: 4/side","Minute 4 - {cyc}: 30 s @ RPE 6-7"],
                ["Minute 1 - Slip -> Roll -> Counter Shadow Sequence: 30 s","Minute 2 - Lateral Footwork + Exit: 30 s","Minute 3 - {med} Ground Slam: 8 reps","Minute 4 - {cyc}: 30 s @ RPE 6-7"]
            ]
            name="Boxing Aerobic-Skill Base EMOM"
        elif month==2:
            menus=[
                ["Minute 1 - Shadow Boxing: 40 s high-output combinations","Minute 2 - Boxing Reaction Callout Drill: 25 s","Minute 3 - {med} Punch Throw: 5/side","Minute 4 - {cyc}: 25 s hard / 35 s easy"],
                ["Minute 1 - 3-Punch Flurry + Footwork: 25 s","Minute 2 - Slip -> Roll -> Counter: 25 s","Minute 3 - {med} Rotational Scoop Toss: 5/side","Minute 4 - {cyc}: 20 s hard / 40 s easy"],
                ["Minute 1 - Shadow Boxing: 20 s burst / 20 s technical","Minute 2 - Reactive Direction + Punch Callout: 20 s","Minute 3 - {med} Ground Slam: 10 reps","Minute 4 - {cyc}: 20 s hard / 40 s easy"]
            ]
            name="Boxing Repeat-Effort Development EMOM"
        else:
            menus=[
                ["Minute 1 - Shadow Boxing: 20 s maximal flurry / 40 s technical","Minute 2 - Reaction Callout + Punch Combination: 20 s","Minute 3 - {med} Punch Throw: 5/side","Minute 4 - {cyc}: 15-20 s hard"],
                ["Minute 1 - Footwork -> Reactive Exit -> Shadow Flurry: 20 s","Minute 2 - Slip -> Roll -> Counter: 20 s","Minute 3 - {med} Rotational Scoop Toss: 5/side","Minute 4 - {cyc}: 15-20 s hard"],
                ["Minute 1 - Shadow Boxing: 15 s flurry / 15 s reset x 2","Minute 2 - Reactive Boxing Callout: 20 s","Minute 3 - {med} Ground Slam: 10 reps","Minute 4 - {cyc}: 15-20 s hard"]
            ]
            name="Boxing Specific Power-Endurance EMOM"
        stations=[x.format(med=med,cyc=cyc) for x in menus[day_variant]]
        return {"system":"Anaerobic / Repeated Sprint" if month>=2 else "Aerobic","name":name,"stations":stations,"work":f"EMOM {rounds*4} min - {rounds} rounds | {density}","rest":"Remaining minute","intensity":work_rpe,"reason":f"Boxing-specific striking, reaction, footwork and repeated-effort conditioning | {phase}"}

    if swimming:
        day_variant=(day-1 + week-1)%3
        if month==1:
            menus=[
                ["Minute 1 - SkiErg: 40 s @ RPE 6-7","Minute 2 - Band Straight-Arm Swim Pull: 12 reps","Minute 3 - Streamline Hollow-Body Hold: 25 s","Minute 4 - Shoulder CARs + T-Spine reset: 30 s"],
                ["Minute 1 - Rower: 40 s @ RPE 6-7","Minute 2 - Straight-Arm Cable Pulldown: 10 reps","Minute 3 - Prone Y-T-W: 6/position","Minute 4 - Dead Bug + breathing reset: 30 s"],
                ["Minute 1 - SkiErg: 30 s @ RPE 7","Minute 2 - Medicine-Ball Streamline Slam: 8 reps","Minute 3 - Streamline Hollow-Body Hold: 25 s","Minute 4 - Shoulder mobility reset: 30 s"]
            ]
            name="Swimming Aerobic-Strength Base EMOM"
        elif month==2:
            menus=[
                ["Minute 1 - SkiErg: 30 s @ RPE 8","Minute 2 - Straight-Arm Cable Pulldown: 12 reps","Minute 3 - Streamline Hollow-Body Hold: 30 s","Minute 4 - Easy SkiErg: 30 s"],
                ["Minute 1 - Rower: 25 s hard / 35 s easy","Minute 2 - Band Straight-Arm Swim Pull: 15 reps","Minute 3 - Medicine-Ball Streamline Slam: 8 reps","Minute 4 - T-Spine rotation reset: 30 s"],
                ["Minute 1 - SkiErg: 20 s hard / 40 s easy","Minute 2 - Straight-Arm Pulldown: 10 reps","Minute 3 - Prone Y-T-W: 8/position","Minute 4 - Hollow-Body Hold: 30 s"]
            ]
            name="Swimming Aerobic-Anaerobic Development EMOM"
        else:
            menus=[
                ["Minute 1 - SkiErg: 20 s hard / 40 s easy","Minute 2 - Swim Pull + 2 s squeeze: 10 reps","Minute 3 - Medicine-Ball Streamline Slam: 6 reps","Minute 4 - Hollow-Body Hold: 30 s"],
                ["Minute 1 - Rower: 15-20 s hard / 40 s easy","Minute 2 - Straight-Arm Cable Pulldown: 8-10 reps","Minute 3 - Prone Y-T-W: 6/position","Minute 4 - Streamline Hold: 30 s"],
                ["Minute 1 - SkiErg: 15 s hard / 45 s easy","Minute 2 - Band Swim Pull: 12 reps","Minute 3 - Medicine-Ball Slam: 6 reps","Minute 4 - Breathing + shoulder reset: 30 s"]
            ]
            name="Swimming Specific Power-Endurance EMOM"
        stations=menus[day_variant]
        return {"system":"Aerobic" if month==1 else "Anaerobic / Repeated Sprint","name":name,"stations":stations,"work":f"EMOM {rounds*4} min - {rounds} rounds | {density}","rest":"Remaining minute","intensity":work_rpe,"reason":f"Swimming-specific aerobic/anaerobic conditioning with pull capacity, scapular endurance and streamline trunk control | {phase}"}

    if racket:
        if month==1:
            stations=["Minute 1 - Split Step + Lateral Shuffle: 20 s",
                      "Minute 2 - Rotational Medicine-Ball Scoop Toss: 4/side",
                      f"Minute 3 - {cyc}: 35 s @ RPE 7",
                      "Minute 4 - Walk + T-spine reset: 30 s"]
            name="Racket Sport Aerobic-COD Base EMOM"
            reason="Build repeatable movement capacity before higher-intensity sport-specific density"
        elif month==2:
            stations=["Minute 1 - Crossover Run -> 5 m Acceleration: 2 reps",
                      "Minute 2 - Lateral Shuffle -> Deceleration: 2/side",
                      "Minute 3 - Rotational Medicine-Ball Scoop Toss: 5/side",
                      f"Minute 4 - {cyc}: 25 s hard / 35 s easy"]
            name="Racket Sport Repeat-COD Development EMOM"
            reason="Increase COD density, braking and rotational repeatability"
        else:
            stations=["Minute 1 - Reactive Split Step -> Direction Call -> Sprint: 15 s",
                      "Minute 2 - Rotational Medicine-Ball Scoop Toss: 5/side",
                      "Minute 3 - Crossover -> Lateral Recovery -> Sprint: 2 reps",
                      f"Minute 4 - {cyc}: 20 s hard / 40 s easy"]
            name="Racket Sport Specific Power-Endurance EMOM"
            reason="Transfer repeat-effort, reactive COD and rotational power to racket-sport demands"
        if target=="aerobic" and month==2:
            stations[3]=f"Minute 4 - {cyc}: 45 s @ RPE 7"
        return {"system":"Agility / COD" if month>=2 else "Aerobic","name":name,
                "stations":stations,"work":f"EMOM {rounds*4} min - {rounds} rounds | {density}","rest":"Remaining minute",
                "intensity":work_rpe,"reason":f"{reason} | {phase}"}

    if combat:
        if month==1:
            stations=["Minute 1 - Technical Sprawl -> Stand: 5 reps",
                      "Minute 2 - Medicine-Ball Rotational Scoop Toss: 4/side",
                      "Minute 3 - Battle-Rope Power Waves: 20 s",
                      f"Minute 4 - {cyc}: 35 s @ RPE 7"]
            name="Combat Aerobic-Power Base EMOM"
        elif month==2:
            stations=["Minute 1 - Sprawl -> Stand: 6 reps",
                      "Minute 2 - Medicine-Ball Ground Slam: 8 reps",
                      "Minute 3 - Battle-Rope Power Waves: 25 s",
                      f"Minute 4 - {cyc}: 20 s hard"]
            name="Combat Repeat-Effort Development EMOM"
        else:
            stations=["Minute 1 - Sprawl -> Stand -> Lateral Exit: 4 reps",
                      "Minute 2 - Rotational Medicine-Ball Throw: 5/side",
                      "Minute 3 - Battle-Rope Power Waves: 30 s",
                      f"Minute 4 - {cyc}: 15-20 s hard"]
            name="Combat Specific Repeat-Power EMOM"
        return {"system":"Anaerobic / Repeated Sprint","name":name,"stations":stations,
                "work":f"EMOM {rounds*4} min - {rounds} rounds | {density}","rest":"Remaining minute",
                "intensity":work_rpe,"reason":f"Combat repeated-effort demand | {phase}"}

    if collision:
        if month==1:
            stations=[f"Minute 1 - {sled}: 15 m @ RPE 7","Minute 2 - Medicine-Ball Ground Slam: 8 reps","Minute 3 - 10 m Acceleration: 2 reps",f"Minute 4 - {cyc}: 30 s @ RPE 7"]
            name="Collision Sport Force-Capacity EMOM"
        elif month==2:
            stations=[f"Minute 1 - {sled}: 20 m heavy","Minute 2 - Bear-Hug Carry / March: 30 s","Minute 3 - 10 m Acceleration Shuttle: 2 reps",f"Minute 4 - {cyc}: 20 s hard"]
            name="Collision Sport Force-Repeatability EMOM"
        else:
            stations=[f"Minute 1 - {sled}: 15 m fast","Minute 2 - Medicine-Ball Scoop Toss: 5/side","Minute 3 - 10 m Acceleration -> 10 m Decel: 2 reps",f"Minute 4 - {cyc}: 15-20 s hard"]
            name="Collision Sport Specific Power-Endurance EMOM"
        return {"system":"Anaerobic / Repeated Sprint","name":name,"stations":stations,
                "work":f"EMOM {rounds*4} min - {rounds} rounds | {density}","rest":"Remaining minute",
                "intensity":work_rpe,"reason":f"Force, acceleration and repeat-effort demand | {phase}"}

    if sprint:
        if month==1:
            stations=["Minute 1 - Sled Acceleration: 15 m @ controlled load","Minute 2 - Pogos: 12 contacts","Minute 3 - Medicine-Ball Chest Pass: 5 reps",f"Minute 4 - {cyc}: 30 s easy/moderate"]
            name="Sprint/Jumps Capacity + Elasticity EMOM"
        elif month==2:
            stations=["Minute 1 - Sled Acceleration: 15 m fast","Minute 2 - Broad Jump: 3 reps","Minute 3 - Medicine-Ball Chest Pass: 5 reps",f"Minute 4 - {cyc}: 15 s hard / 45 s easy"]
            name="Sprint/Jumps Speed-Power Repeatability EMOM"
        else:
            stations=["Minute 1 - Acceleration: 10-20 m, 2 reps","Minute 2 - Broad Jump: 2-3 quality reps","Minute 3 - Medicine-Ball Throw: 4 reps",f"Minute 4 - {cyc}: 15 s hard / 45 s easy"]
            name="Sprint/Jumps Specific Power-Endurance EMOM"
        return {"system":"Acceleration / Speed","name":name,"stations":stations,
                "work":f"EMOM {rounds*4} min - {rounds} rounds | {density}","rest":"Remaining minute",
                "intensity":"Preserve speed; stop if velocity/quality falls","reason":f"Sprint/jump-specific conditioning | {phase}"}

    if court:
        if month==1:
            stations=["Minute 1 - Lateral Shuffle -> 5 m Sprint: 2 reps","Minute 2 - Wall Ball / Medicine-Ball Squat Throw: 8 reps","Minute 3 - Tempo Shuttle: 30 s",f"Minute 4 - {cyc}: 30 s @ RPE 7"]
            name="Court/Field Aerobic-COD Base EMOM"
        elif month==2:
            stations=["Minute 1 - Reactive Cone COD: 15 s","Minute 2 - Lateral Bound -> Stick: 4/side","Minute 3 - 10 m Shuttle: 3 reps",f"Minute 4 - {cyc}: 20 s hard / 40 s easy"]
            name="Court/Field COD + Repeat-Sprint Development EMOM"
        else:
            stations=["Minute 1 - Reactive Shuffle -> Sprint: 15 s","Minute 2 - Lateral Bound -> Sprint: 2/side","Minute 3 - 10-15 m Repeat Sprint: 2 reps",f"Minute 4 - {cyc}: 15-20 s hard"]
            name="Court/Field Specific Repeat-Power EMOM"
        if a.sport=="Volleyball":
            stations[1]="Minute 2 - Approach Jump / Block Jump: 3 quality reps"
        elif a.sport=="Basketball":
            stations[1]="Minute 2 - Low Box Jump -> Stick Landing: 3 reps"
        elif a.sport=="Soccer":
            stations[1]="Minute 2 - Lateral Bound -> 5 m Sprint: 2/side"
        elif a.sport=="Handball":
            stations[1]="Minute 2 - Medicine-Ball Overhead Throw: 5 reps"
        return {"system":"Agility / COD" if month>=2 else "Aerobic","name":name,"stations":stations,
                "work":f"EMOM {rounds*4} min - {rounds} rounds | {density}","rest":"Remaining minute",
                "intensity":work_rpe,"reason":f"{a.sport} court/field movement demand | {phase}"}

    # General / mixed-athlete fallback still changes across months.
    if month==1:
        stations=[f"Minute 1 - {cyc}: 40 s @ RPE 7",f"Minute 2 - {med} Squat Throw: 10 reps","Minute 3 - Tempo Shuttle: 30 s","Minute 4 - Dead Bug + breathing reset: 30 s"]
        name="Whole-Athlete Aerobic Base EMOM"
    elif month==2:
        stations=[f"Minute 1 - {cyc}: 30 s @ RPE 8",f"Minute 2 - {load} Swing: 10 reps","Minute 3 - Lateral Shuffle -> Sprint: 15 s",f"Minute 4 - {load} Suitcase Carry: 30 s"]
        name="Whole-Athlete Mixed Energy-System EMOM"
    else:
        stations=[f"Minute 1 - {cyc}: 20 s hard / 40 s easy",f"Minute 2 - {load} Thruster: 8 reps","Minute 3 - Reactive Cone Drill: 15 s",f"Minute 4 - {load} Carry: 30 s"]
        name="Whole-Athlete Specific Work-Capacity EMOM"
    return {"system":"Anaerobic / Repeated Sprint" if month>=2 else "Aerobic","name":name,
            "stations":stations,"work":f"EMOM {rounds*4} min - {rounds} rounds | {density}","rest":"Remaining minute",
            "intensity":work_rpe,"reason":f"Whole-athlete work-capacity balance | {phase}"}

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
# STAGE 6 - MACROCYCLE / ROTATION / PROGRESSION
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
        return "Progress quality first: faster execution, cleaner mechanics, slightly more exposure-not fatigue accumulation."
    if a.primary_goal=="Hypertrophy": return "Progress reps within the range, then add a small load while maintaining target RPE."
    return "Progress load conservatively when the prescribed reps are completed at or below target RPE."

def complex_allowed(c,a,constraints):
    levels={"Beginner":0,"Intermediate":1,"Advanced":2,"Elite":3}
    if c.sport_tags and not any(sport_tag_matches(tag,a.sport) or tag=="General Fitness" for tag in c.sport_tags): return False
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
        if a.sport=="Boxing" and c.id=="cx10": s+=35
        if a.sport=="Swimming" and c.id=="cx11": s+=45
        if a.sport=="Karate" and c.id=="cx12": s+=45
        s-=c.fatigue*2
        return s
    return max(candidates,key=score)

def complex_dose(c,a,week,constraints):
    if c.method in ["Contrast","Sport Power Complex"]:
        rounds={1:3,2:3,3:4,4:2}[week]
        if training_level(a.training_years) in ["Intermediate"]: rounds=max(2,rounds-1)
        return rounds, "2-3 reps per exercise", c.rest_between, c.rest_rounds
    rounds={1:2,2:3,3:3,4:2}[week]
    return rounds, "4-6 reps / 5-10 s per drill", c.rest_between, c.rest_rounds

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
    cond=conditioning_decision(a,p,constraints,week,month,day)
    complex_block=None
    # Place a complex only when power/agility demand and readiness justify advanced methods.
    sport_complex_eligible = a.sport in ["Boxing","Swimming","Karate"]
    if day==1 and (sport_complex_eligible or (p.get("Power",0)+p.get("COD",0)+p.get("Acceleration",0)+p.get("Rotational Power",0))>22):
        complex_block=choose_complex(a,p,systems,constraints,month)
    return {"day":day,"week":week,"month":month,"phase":phase_for(a,week),"mesocycle_phase":mesocycle_phase(a,month),"systems":systems,"exercises":exercises,"conditioning":cond,"complex":complex_block,"readiness":constraints["readiness"]}

def build_program(a,months):
    constraints=constraint_engine(a); p=priorities(a); systems=system_allocation(a,p,constraints)
    rotation=build_rotation(a,months,p,systems,constraints)
    days=max(1,min(a.gym_days_available,4))
    program={m:{w:[build_session(a,w,d,m,rotation,p,systems,constraints) for d in range(1,days+1)] for w in range(1,5)} for m in range(1,months+1)}
    return program,{"constraints":constraints,"priorities":p,"systems":systems,"rotation":rotation}

# ============================================================
# ADAPTATION LOOP - FEEDBACK CHANGES THE NEXT DECISION
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
    trace.append(("01 Intake",f"{a.sport} / {a.position}" + (f" + {", ".join(a.secondary_positions)}" if getattr(a,"secondary_positions",[]) else "") + f" | {a.primary_goal} | {a.season}"))
    trace.append(("02 Goal interaction",f"Primary goal controls session architecture and system weighting; {len(a.secondary_goals)} secondary targets shape substitutions, priorities and dose."))
    trace.append(("03 Readiness gate",f"{c['readiness']:.0f}/100 -> {c['band']} | volume x{c['volume_multiplier']:.2f} | intensity x{c['intensity_multiplier']:.2f}"))
    if c["pain_gate"]: trace.append(("04 Safety gate","Pain threshold triggered: high-impact/high-fatigue systems are blocked from normal selection."))
    elif c["screen_flags"]: trace.append(("04 Screening gate",f"{len(c['screen_flags'])} screening flags increase corrective/mobility/stability priority."))
    else: trace.append(("04 Screening gate","No major screening constraint recorded."))
    top=" | ".join([f"{k} {v:.1f}%" for k,v in list(p.items())[:5]])
    trace.append(("05 Performance gaps",top))
    trace.append(("06 Sport demand",f"Sport demands are blended with individual gaps for {a.sport}."))
    trace.append(("07 System allocation"," | ".join([f"{k} {v:.1f}" for k,v in list(systems.items())[:6]])))
    trace.append(("08 Exercise selection","Strict sport-lock + equipment gate + level + injury/screening gates + position relevance + primary-goal architecture + fatigue + monthly novelty."))
    trace.append(("09 Dose","Sets/reps/intensity change with training level, goal, week, season and readiness."))
    trace.append(("10 Metabolic decision",program[1][1][0]["conditioning"]["name"]+" selected from sport, gaps, secondary targets, readiness, month and day."))
    trace.append(("11 Progression","Progression is conditional on technical quality, RPE, readiness and pain-not calendar alone."))
    trace.append(("12 Advanced methods","Compound/contrast/complex training is gated by training age, readiness, impact tolerance, equipment and current priorities."))
    if program[1][1][0].get("complex"):
        trace.append(("13 Complex selection",program[1][1][0]["complex"].name+" selected as an advanced power/agility stimulus."))
    trace.append(("14 Periodization","Monthly phases change the training stimulus: foundation -> development -> sport specificity, with week 4 deloading and readiness gates overriding when necessary."))
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
        pres=f"{sets} Sets x {reps} Reps"
    elif x.system=="Plyometrics":
        pres,rest,intensity=plyo_dose(a,week,constraints); tempo=f"Explosive | {rest}"
    elif x.system=="Agility / COD":
        pres,rest,intensity=agility_dose(a,week,constraints); tempo=f"Full recovery | {rest}"
    elif x.system=="Acceleration / Speed":
        pres,rest,intensity=speed_dose(a,week,constraints); tempo=f"Full recovery | {rest}"
    elif x.system=="Mobility": pres="2 Sets x 6-10 controlled reps/side"; intensity="Controlled ROM"; tempo="2-1-2-0"
    elif x.system in ["Stability / Core","Corrective / Activation"]: pres="2-3 Sets x 8-12 reps or 20-40 s"; intensity="RPE 5-7"; tempo="Controlled"
    elif x.system=="Anaerobic / Repeated Sprint": pres="2-3 Sets x 4-6 reps"; intensity="RPE 8-9"; tempo="Full quality recovery"
    else: pres="2-3 Sets x 8-12"; intensity="RPE 6-7"; tempo="2-1-2-0"
    render_card(x.system,x.name,pres,intensity,tempo,x.plane,x.tier,ACCENTS.get(x.system,"#38bdf8"))
    if x.regression or x.progression:
        st.caption(f"Regression: {x.regression or '-'} | Progression: {x.progression or '-'}")
    st.caption(progression_rule(a,week,x,slot,constraints))

def render_session(a,session,week,engine):
    c=engine["constraints"]
    warmups=" + ".join(SPORT_WARMUPS.get(a.sport,SPORT_WARMUPS["General Fitness"]))
    render_card("1. Corrective / Sport Prep",f"{a.sport}: {warmups}","2 rounds x 5-10 reps/side","Controlled, symptom-free","2-1-2-0","Multi-planar","Activation",ACCENTS["Corrective / Activation"])
    for i,x in enumerate(session["exercises"]):
        slot="primary" if i<2 else "secondary"
        render_exercise(a,x,week,c,slot)
    if session.get("complex"):
        cx=session["complex"]
        rounds,reps,between,round_rest=complex_dose(cx,a,week,c)
        st.markdown("#### ⚡ Complex / Compound Athletic Power Block")
        names=[EXERCISES[eid].name for eid in cx.exercises if eid in EXERCISES]
        render_card(cx.method,cx.name,f"{rounds} rounds | {reps}",f"Rest {round_rest} between rounds",f"{between} between exercises","Multi-planar","Advanced / Athletic",ACCENTS.get("Plyometrics","#ec4899"))
        st.caption(" -> ".join(names))
        if cx.notes: st.caption(cx.notes)
    cond=session["conditioning"]
    st.markdown("#### 🔥 Metabolic / ESD Station")
    render_card("5. Dynamic MetCon / ESD Protocol",cond["name"],cond["work"]+" | Rest: "+cond["rest"],cond["intensity"],"Dynamic Pace","Multi-planar","Energy System / Conditioning",ACCENTS["Aerobic"])
    st.markdown("**Exact execution:**")
    for station in cond["stations"]:
        st.markdown(f"- **{station}**")
    st.caption(cond["reason"])


# ============================================================
# ATHLETE-IQ v6 - CLOSED-LOOP ADAPTATION + MULTI-PROTOCOL ESD
# ============================================================
# v6 deliberately does NOT perform automatic photo/posture diagnosis.
# Photos remain coach documentation; structured observations drive the engine.

if "training_log" not in st.session_state:
    st.session_state.training_log=[]
if "test_history" not in st.session_state:
    st.session_state.test_history=[]
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback=None

METCON_METHODS = ["EMOM","AMRAP","Tabata","Intervals","Circuit","Every 90s","Ladder"]

SPORT_ESD_FOCUS = {
    "Boxing":["Reaction","Shadow Boxing","Footwork","Rotational Power","Repeated Effort"],
    "Karate":["Reaction","Shadow Kumite","Footwork","Rotational Power","Repeated Effort"],
    "Swimming":["SkiErg","Swim Pull","Streamline Core","Aerobic Power","Shoulder Endurance"],
    "Tennis":["Reactive COD","Lateral Shuffle","Rotation","Repeated Sprint"],
    "Racket Sports (Squash/Padel)":["Reactive COD","Lateral Shuffle","Rotation","Repeated Sprint"],
    "Soccer":["Acceleration","COD","Repeated Sprint","Aerobic Recovery"],
    "Basketball":["Acceleration","COD","Jump Repeatability","Anaerobic Repeat"],
    "Volleyball":["Jump Repeatability","Lateral COD","Acceleration","Power-Endurance"],
    "Handball":["Acceleration","COD","Throw Power","Repeated Sprint"],
    "Rugby/American Football":["Acceleration","Sled Work","Repeated Effort","Collision Conditioning"],
    "Track & Field (Sprints/Jumps)":["Acceleration","Speed","Elastic Power","Low-Volume High-Quality"],
    "MMA":["Mixed Skill Rounds","Reaction","Grappling-Conditioning","Repeated Effort"],
}

# Specific screening observations -> conservative training responses.
SCREENING_RESPONSE_RULES = {
    "anterior pelvic tilt": {"Mobility":4,"Stability":4},
    "posterior pelvic tilt": {"Mobility":2,"Stability":3},
    "scapular winging": {"Stability":6,"Mobility":2},
    "scapular asymmetry": {"Stability":5},
    "rounded shoulders": {"Mobility":3,"Stability":3},
    "forward head": {"Mobility":3,"Stability":2},
    "thoracic kyphosis": {"Mobility":4,"Stability":2},
    "foot pronation": {"Stability":4,"Mobility":2},
    "knee valgus": {"Stability":5},
    "knee varus": {"Stability":3},
    "pelvic hike": {"Stability":4,"Mobility":2},
}

def _recent_logs():
    return st.session_state.get("training_log", [])[-12:]

def recent_training_load():
    logs=_recent_logs()
    if not logs: return 0.0
    return float(sum(float(x.get("session_rpe",0))*float(x.get("duration_min",60))/60 for x in logs))

def weekly_external_load(a):
    # Simple internal-load proxy: team/sport minutes x session RPE + competition load.
    team_load=float(a.team_days*a.team_minutes*max(a.weekly_sport_rpe,1)/10)
    comp_load=float(a.competition_days*90*max(a.weekly_sport_rpe,1)/10)
    return team_load+comp_load

def load_status(a):
    recent=recent_training_load()
    sport=weekly_external_load(a)
    total=recent+sport
    if total>=450: return "HIGH", total
    if total>=300: return "MODERATE-HIGH", total
    if total>=180: return "MODERATE", total
    return "LOW", total

def adaptive_load_modifier(a):
    status,total=load_status(a)
    mod=1.0
    if status=="HIGH": mod=.72
    elif status=="MODERATE-HIGH": mod=.86
    if st.session_state.get("last_feedback"):
        f=st.session_state.last_feedback
        if f.get("session_rpe",0)>=9: mod*=.82
        if f.get("pain_after",0)>=5: mod*=.75
        if f.get("performance_change",0)>=1 and f.get("session_rpe",10)<=7: mod*=1.03
    return float(np.clip(mod,.55,1.05))

def _screening_response(a):
    out={q:0.0 for q in ["Mobility","Stability","Strength","Power","Agility","Speed","Aerobic","Anaerobic"]}
    severity_weight={"Mild":1.0,"Moderate":1.7,"Marked":2.4}
    for d in [a.posture_anterior,a.posture_lateral,a.posture_posterior]:
        for val in d.values():
            if not isinstance(val,str) or " || " not in val: continue
            finding,severity=val.split(" || ",1)
            rule=SCREENING_RESPONSE_RULES.get(finding.lower())
            if rule:
                w=severity_weight.get(severity,0)
                for q,v in rule.items(): out[q]+=v*w
    return out

# Override the old generic screening adjustment with finding-specific weighting.
def screening_adjustments(a):
    out={q:0.0 for q in ["Mobility","Stability","Strength","Power","Agility","Speed","Aerobic","Anaerobic"]}
    base=screening_adjustments_base(a) if "screening_adjustments_base" in globals() else None
    if base: out.update(base)
    specific=_screening_response(a)
    for q,v in specific.items(): out[q]+=v
    flags=screening_flags(a)
    for f in flags:
        s=f.lower()
        if "painful" in s: out["Power"]-=8; out["Agility"]-=8; out["Speed"]-=6
        if "dysfunctional" in s: out["Power"]-=3; out["Agility"]-=3
    if asymmetry(a.left_jump,a.right_jump)>=8:
        out["Stability"]+=8
    return out

# Preserve the v5.4 version under a new name, then use the enhanced version above.
# This is done once at import time.
if "screening_adjustments_base" not in globals():
    # The original function is still available only if this block runs before replacement;
    # v6 re-implements the general flags below to avoid recursion.
    def screening_adjustments_base(a):
        out={q:0.0 for q in ["Mobility","Stability","Strength","Power","Agility","Speed","Aerobic","Anaerobic"]}
        for f in screening_flags(a):
            s=f.lower()
            if any(k in s for k in ["ankle","hip","t-spine","shoulder","mobility","rotation","flexion","extension"]): out["Mobility"]+=3
            if any(k in s for k in ["pelvic","knee alignment","scapular","stability","landing","rotary"]): out["Stability"]+=3
        return out

# Rebind now that the safe base exists.
_old_screening_adjustments = screening_adjustments

def screening_adjustments(a):
    out=screening_adjustments_base(a)
    for q,v in _screening_response(a).items(): out[q]+=v
    flags=screening_flags(a)
    for f in flags:
        s=f.lower()
        if "painful" in s: out["Power"]-=8; out["Agility"]-=8; out["Speed"]-=6
        elif "dysfunctional" in s: out["Power"]-=3; out["Agility"]-=3
    if asymmetry(a.left_jump,a.right_jump)>=8: out["Stability"]+=8
    return out

# ---------------------------
# Multi-protocol conditioning
# ---------------------------
def _station(name,prescription): return f"{name} - {prescription}"

def _pick_protocol(a,month,week,day,priorities,constraints):
    # Protocol selection is deliberate, not random. Month controls the training emphasis;
    # week controls progression/deload; sport and secondary targets influence method.
    if constraints["low_impact"]: return "Intervals"
    if week==4: return "Intervals"
    if a.sport in ["Boxing","Karate"]:
        return ["Intervals","Tabata","Circuit"][min(month-1,2)]
    if a.sport=="Swimming":
        return ["Intervals","AMRAP","Intervals"][min(month-1,2)]
    if a.sport in ["Tennis","Racket Sports (Squash/Padel)"]:
        return ["Intervals","Every 90s","Circuit"][min(month-1,2)]
    if a.sport in ["Soccer","Basketball","Volleyball","Handball"]:
        return ["Intervals","EMOM","AMRAP"][min(month-1,2)]
    if a.sport=="Track & Field (Sprints/Jumps)": return ["Intervals","Every 90s","Ladder"][min(month-1,2)]
    if a.sport=="Rugby/American Football": return ["Circuit","EMOM","AMRAP"][min(month-1,2)]
    # Goal-driven generic selection
    if priorities.get("Anaerobic",0)>priorities.get("Aerobic",0)+8: return "Tabata" if month>=2 else "EMOM"
    if priorities.get("Aerobic",0)>priorities.get("Anaerobic",0)+8: return "Intervals"
    return ["EMOM","Circuit","AMRAP"][min(month-1,2)]

def _sport_stations(a,month,week,day):
    s=a.sport
    if s=="Boxing":
        return [
            _station("Shadow Boxing - technical combinations", "30 s work"),
            _station("Boxing Reaction Callout Drill", "20 s high-quality reactions"),
            _station("Medicine-Ball Punch Throw", "5/side"),
            _station("Footwork: forward/back + lateral exits", "20 s"),
        ]
    if s=="Karate":
        return [
            _station("Shadow Kumite - combination flow", "30 s"),
            _station("Reaction Callout - strike/check/exit", "20 s"),
            _station("Rotational Medicine-Ball Punch Throw", "5/side"),
            _station("Split-Stance Punch -> Lateral Exit", "4/side"),
        ]
    if s=="Swimming":
        return [
            _station("SkiErg Swim-Pull Intervals", "30-40 s"),
            _station("Straight-Arm Cable Pulldown", "10-12 reps"),
            _station("Swimmer Hollow-Body Hold", "25-35 s"),
            _station("Prone Y-T-W", "6 each position"),
        ]
    if s in ["Tennis","Racket Sports (Squash/Padel)"]:
        return [
            _station("Split Step -> Reactive Lateral Shuffle", "15-20 s"),
            _station("Rotational Medicine-Ball Scoop Toss", "5/side"),
            _station("Crossover -> 5 m Acceleration", "2 reps/side"),
            _station("Bike/Rower", "20-30 s"),
        ]
    if s=="Soccer":
        return [_station("10 m Acceleration", "2 reps"),_station("Lateral/Crossover Shuttle", "20 s"),_station("Sled Push", "15-20 m"),_station("Bike/Rower", "30 s")]
    if s=="Basketball":
        return [_station("Lateral Shuffle -> Closeout", "20 s"),_station("Countermovement Jump", "4 reps"),_station("5-10-5 Shuttle", "1 rep"),_station("Bike/Rower", "30 s")]
    if s=="Volleyball":
        return [_station("Block Hop -> Lateral Shuffle", "20 s"),_station("Approach Jump", "3 reps"),_station("Reactive Cone Drill", "15 s"),_station("Bike/Rower", "30 s")]
    if s=="Handball":
        return [_station("Crossover -> Acceleration", "2 reps/side"),_station("Rotational Medicine-Ball Throw", "5/side"),_station("Shuttle Sprint", "20 s"),_station("Bike/Rower", "30 s")]
    if s=="Rugby/American Football":
        return [_station("Sled Push", "15-20 m"),_station("Acceleration Start", "2 reps"),_station("Battle Rope", "25 s"),_station("Shuttle Sprint", "20 s")]
    if s=="Track & Field (Sprints/Jumps)":
        return [_station("Acceleration Sprint", "10-20 m"),_station("Pogo / Elastic Hops", "10-15 s"),_station("Med-Ball Throw", "4 reps"),_station("Easy Bike", "30 s")]
    if s=="MMA":
        return [_station("Shadow MMA Flow", "30 s"),_station("Sprawl -> Stand", "5 reps"),_station("Med-Ball Slam", "8 reps"),_station("Bike/Rower", "30 s")]
    return [_station("Bike/Rower", "30-40 s"),_station("Wall Ball", "10 reps"),_station("Tempo Shuttle", "20-30 s"),_station("Dead Bug", "30 s")]

def _metcon_sanitize_station(a,station):
    """Hard equipment gate for every conditioning station, including sport-specific templates."""
    s=station
    has_erg=_has(a,"Ergometers (AirBike/Rower/SkiErg)")
    has_med=_has(a,"Medicine & Slam Balls")
    has_sled=_has(a,"Sleds & Prowler")
    has_cable=_has(a,"Cable Systems & Selectorized")
    has_bar=_has(a,"Barbells & Plates")
    has_kb=_has(a,"Kettlebells")
    has_band=_has(a,"Bands")
    has_rope=_has(a,"Battle Rope") or _has(a,"Battle Ropes")
    has_db=_has(a,"Dumbbells")
    has_cone=_has(a,"Cones / Timing Gates")
    if not has_sled and any(k in s.lower() for k in ["sled push","sled acceleration","sled work"]):
        s=s.replace("Sled Push","DB Farmer Carry / March" if has_db else "Tempo Acceleration").replace("Sled Acceleration","DB Farmer Carry / March" if has_db else "Tempo Acceleration").replace("Sled Work","DB Farmer Carry / March" if has_db else "Tempo Acceleration")
    if not has_med and any(k in s.lower() for k in ["medicine-ball","medicine ball","med-ball","wall ball"]):
        s="DB Thruster / Squat-to-Press - 8 reps" if has_db else "Squat Jump / Fast Squat - 8 reps"
    if not has_erg and any(k in s.lower() for k in ["bike/rower","airbike","rower","skierg","ski erg","easy bike"]):
        s="Tempo Shuttle / Fast Walk - 30 s" if _has(a,"Bodyweight") else "Low-Impact March - 30 s"
    if not has_cable and "cable" in s.lower():
        s="Band Straight-Arm Pull - 12 reps" if has_band else ("DB Pullover - 10 reps" if has_db else "Prone Y-T-W - 6/position")
    if not has_bar and "barbell" in s.lower():
        s="Dumbbell substitute - same rep target" if has_db else "Bodyweight squat - same rep target"
    if not has_kb and "kettlebell" in s.lower():
        s="Dumbbell Swing - same rep target" if has_db else "Hip Hinge - same rep target"
    if not has_rope and "battle rope" in s.lower():
        s="DB High-Pull / Fast Punches - 25 s" if has_db else "Fast Feet - 25 s"
    if not has_cone and any(k in s.lower() for k in ["cone","timing gate"]):
        s=s.replace("Reactive Cone Drill","Reactive Direction Change").replace("Cone COD","Reactive COD")
    return s

def sanitize_metcon_stations(a,stations):
    return [_metcon_sanitize_station(a,x) for x in stations]

def conditioning_decision(a,p,constraints,week,month=1,day=1):
    protocol=_pick_protocol(a,month,week,day,p,constraints)
    loadmod=adaptive_load_modifier(a)
    base_rounds={1:3,2:4,3:4,4:2}[week]
    rounds=max(2,int(round(base_rounds*loadmod)))
    if week==4: rounds=max(2,rounds)
    phase=mesocycle_phase(a,month)
    work_rpe=6.5 if month==1 else 7.5 if month==2 else 8.0
    if constraints["band"]=="YELLOW": work_rpe-=.5
    if constraints["band"]=="RED": work_rpe=5.5
    if a.season in ["In-Season / Competition","Taper / Peak"]: work_rpe=min(work_rpe,7.0)
    stations=_sport_stations(a,month,week,day)
    # Rotate station order by day/month while preserving the sport-specific pool.
    shift=(month+day-2)%len(stations)
    stations=stations[shift:]+stations[:shift]
    # Final universal equipment gate: no MetCon station may survive with unavailable equipment.
    stations=sanitize_metcon_stations(a,stations)
    if protocol=="EMOM":
        work=f"EMOM {rounds*4} min - {rounds} rounds"
        rest="Complete the station within the minute; recover with remaining time"
    elif protocol=="AMRAP":
        minutes={1:8,2:10,3:12,4:6}[week]
        minutes=max(6,int(minutes*loadmod))
        work=f"AMRAP {minutes} min - repeat all {len(stations)} stations with quality"
        rest="Self-regulated transitions; stop if technique degrades"
    elif protocol=="Tabata":
        work=f"Tabata-style {rounds} rounds x 4 min - 20 s work / 10 s transition"
        rest="60-90 s between 4-min blocks"
    elif protocol=="Every 90s":
        work=f"Every 90 s x {rounds*4} stations - {rounds} rounds"
        rest="Remaining time in each 90-s window"
    elif protocol=="Ladder":
        work=f"Ladder {rounds} rounds - 20/30/40 s work progression, then reset"
        rest="45-75 s between rounds"
    elif protocol=="Circuit":
        work=f"Circuit {rounds} rounds - 30-40 s work / 20 s transition"
        rest="90 s between rounds"
    else:
        work=f"Intervals {rounds} rounds - 30 s work / 30 s recovery"
        rest="60-90 s between rounds"
    return {"system":"Anaerobic / Repeated Sprint" if month>=2 else "Aerobic","name":f"{a.sport} | {protocol} | {phase}","protocol":protocol,"stations":stations,"work":work,"rest":rest,"intensity":f"Target RPE {work_rpe:.1f} | Load modifier x{loadmod:.2f}","reason":f"Protocol selected from sport demands, training phase, readiness, accumulated load and development priorities. {', '.join(SPORT_ESD_FOCUS.get(a.sport,[]))}."}

# ---------------------------
# Load-aware constraint engine ---------------------------
_old_constraint_engine = constraint_engine
def constraint_engine(a):
    c=_old_constraint_engine(a)
    status,total=load_status(a); lm=adaptive_load_modifier(a)
    c["recent_internal_load"]=recent_training_load(); c["sport_load"]=weekly_external_load(a); c["load_status"]=status; c["load_modifier"]=lm
    c["volume_multiplier"]*=lm
    c["high_fatigue_allowed"] = c["high_fatigue_allowed"] and status not in ["HIGH"]
    if status=="HIGH":
        c["intensity_multiplier"]*=.95
    return c

# ---------------------------
# Exercise history + progression ---------------------------
def exercise_recently_used(ex_id,days=12):
    ids=[]
    for r in st.session_state.get("training_log",[])[-days:]:
        ids.extend(r.get("exercise_ids",[]))
    return ex_id in ids

def progression_rule(a,week,exercise,slot,constraints):
    f=st.session_state.get("last_feedback")
    if week==4: return "Deload: reduce volume; preserve movement quality and speed."
    if constraints["band"]=="RED": return "Autoregulate: no planned load increase; stop before technique changes."
    if f and f.get("session_rpe",0)>=9: return "Previous session was very hard: hold or regress the next exposure before progressing."
    if f and f.get("pain_after",0)>=5: return "Pain response detected: substitute/regress and seek appropriate clinical assessment when indicated."
    if f and f.get("performance_change",0)>=1 and f.get("session_rpe",10)<=7: return "Positive response: progress one variable only (load, reps, density or complexity)."
    if a.primary_goal in ["Power","Speed","Agility","Sport Performance"] or exercise.system in ["Plyometrics","Acceleration / Speed","Agility / COD"]:
        return "Progress quality first: faster execution, cleaner mechanics, then slightly more exposure."
    return "Progress load/reps conservatively when target RPE and technical quality are met."

# ---------------------------
# More intelligent session sequencing ---------------------------
def session_template(a,day,system_scores,constraints):
    # Primary goal now controls the session architecture, not just a scoring multiplier.
    if constraints["low_impact"]:
        return ["Corrective / Activation","Mobility","Stability / Core","Resistance","Aerobic"]
    goal=a.primary_goal
    goal_templates={
        "Max Strength":[
            ["Corrective / Activation","Resistance","Resistance","Stability / Core","Aerobic"],
            ["Corrective / Activation","Resistance","Resistance","Mobility","Anaerobic / Repeated Sprint"],
            ["Corrective / Activation","Resistance","Plyometrics","Resistance","Aerobic"],
        ],
        "Strength":[
            ["Corrective / Activation","Resistance","Resistance","Stability / Core","Anaerobic / Repeated Sprint"],
            ["Corrective / Activation","Resistance","Acceleration / Speed","Resistance","Aerobic"],
            ["Corrective / Activation","Resistance","Plyometrics","Resistance","Anaerobic / Repeated Sprint"],
        ],
        "Hypertrophy":[
            ["Corrective / Activation","Resistance","Resistance","Resistance","Aerobic"],
            ["Corrective / Activation","Resistance","Resistance","Stability / Core","Aerobic"],
            ["Corrective / Activation","Resistance","Resistance","Resistance","Anaerobic / Repeated Sprint"],
        ],
        "Power":[
            ["Corrective / Activation","Plyometrics","Resistance","Acceleration / Speed","Anaerobic / Repeated Sprint"],
            ["Corrective / Activation","Plyometrics","Resistance","Agility / COD","Aerobic"],
            ["Corrective / Activation","Plyometrics","Resistance","Acceleration / Speed","Anaerobic / Repeated Sprint"],
        ],
        "Speed":[
            ["Corrective / Activation","Acceleration / Speed","Plyometrics","Resistance","Aerobic"],
            ["Corrective / Activation","Acceleration / Speed","Agility / COD","Resistance","Anaerobic / Repeated Sprint"],
            ["Corrective / Activation","Acceleration / Speed","Plyometrics","Resistance","Aerobic"],
        ],
        "Agility":[
            ["Corrective / Activation","Agility / COD","Plyometrics","Resistance","Anaerobic / Repeated Sprint"],
            ["Corrective / Activation","Agility / COD","Acceleration / Speed","Resistance","Aerobic"],
            ["Corrective / Activation","Agility / COD","Plyometrics","Resistance","Anaerobic / Repeated Sprint"],
        ],
        "Endurance":[
            ["Corrective / Activation","Aerobic","Resistance","Aerobic","Stability / Core"],
            ["Corrective / Activation","Aerobic","Anaerobic / Repeated Sprint","Resistance","Mobility"],
            ["Corrective / Activation","Aerobic","Resistance","Anaerobic / Repeated Sprint","Stability / Core"],
        ],
        "Sport Performance":[
            ["Corrective / Activation","Plyometrics","Acceleration / Speed","Resistance","Agility / COD"],
            ["Corrective / Activation","Agility / COD","Resistance","Acceleration / Speed","Anaerobic / Repeated Sprint"],
            ["Corrective / Activation","Plyometrics","Resistance","Agility / COD","Anaerobic / Repeated Sprint"],
        ],
        "Fat Loss":[
            ["Corrective / Activation","Resistance","Aerobic","Anaerobic / Repeated Sprint","Stability / Core"],
            ["Corrective / Activation","Resistance","Aerobic","Agility / COD","Anaerobic / Repeated Sprint"],
            ["Corrective / Activation","Resistance","Anaerobic / Repeated Sprint","Aerobic","Mobility"],
        ],
        "General Fitness":[
            ["Corrective / Activation","Resistance","Plyometrics","Agility / COD","Aerobic"],
            ["Corrective / Activation","Resistance","Acceleration / Speed","Stability / Core","Aerobic"],
            ["Corrective / Activation","Resistance","Agility / COD","Plyometrics","Anaerobic / Repeated Sprint"],
        ],
        "Overall Development":[
            ["Corrective / Activation","Resistance","Plyometrics","Agility / COD","Aerobic"],
            ["Corrective / Activation","Resistance","Acceleration / Speed","Stability / Core","Aerobic"],
            ["Corrective / Activation","Plyometrics","Resistance","Agility / COD","Anaerobic / Repeated Sprint"],
        ],
    }
    templates=goal_templates.get(goal,goal_templates["Overall Development"])
    preferred=list(templates[(day-1)%len(templates)])
    # If the decision engine identifies a very strong system priority, replace only the final
    # conditioning slot so the goal architecture remains intact while athlete-specific gaps propagate.
    ranked=list(system_scores.keys())
    if ranked:
        top=ranked[0]
        if top in SYSTEMS and top not in preferred and system_scores.get(top,0)>=80:
            preferred[-1]=top
    return preferred

# Rebuild sessions/program so conditioning and load feedback are truly downstream.
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
            # Prefer not to repeat an exercise that was actually logged recently.
            fresh=[z for z in selected if not exercise_recently_used(z.id)]
            x=(fresh or selected)[0]
        used.append(x.id); exercises.append(x)
    cond=conditioning_decision(a,p,constraints,week,month,day)
    complex_block=None
    if day==1 and constraints["high_impact_allowed"] and constraints["high_fatigue_allowed"]:
        complex_block=choose_complex(a,p,systems,constraints,month)
    return {"day":day,"week":week,"month":month,"phase":phase_for(a,week),"mesocycle_phase":mesocycle_phase(a,month),"systems":systems,"exercises":exercises,"conditioning":cond,"complex":complex_block,"readiness":constraints["readiness"]}

def build_program(a,months):
    constraints=constraint_engine(a); p=priorities(a); systems=system_allocation(a,p,constraints)
    rotation=build_rotation(a,months,p,systems,constraints)
    days=max(1,min(a.gym_days_available,4))
    program={m:{w:[build_session(a,w,d,m,rotation,p,systems,constraints) for d in range(1,days+1)] for w in range(1,5)} for m in range(1,months+1)}
    return program,{"constraints":constraints,"priorities":p,"systems":systems,"rotation":rotation,"load_status":constraints["load_status"]}

def render_session(a,session,week,engine):
    c=engine["constraints"]
    warmups=" + ".join(SPORT_WARMUPS.get(a.sport,SPORT_WARMUPS["General Fitness"]))
    render_card("1. Corrective / Sport Prep",f"{a.sport}: {warmups}","2 rounds x 5-10 reps/side","Controlled, symptom-free","2-1-2-0","Multi-planar","Activation",ACCENTS["Corrective / Activation"])
    for i,x in enumerate(session["exercises"]):
        render_exercise(a,x,week,c,"primary" if i<2 else "secondary")
    if session.get("complex"):
        cx=session["complex"]; rounds,reps,between,round_rest=complex_dose(cx,a,week,c)
        st.markdown("#### ⚡ Complex / Compound Athletic Power Block")
        names=[EXERCISES[eid].name for eid in cx.exercises if eid in EXERCISES]
        render_card(cx.method,cx.name,f"{rounds} rounds | {reps}",f"Rest {round_rest} between rounds",f"{between} between exercises","Multi-planar","Advanced / Athletic",ACCENTS.get("Plyometrics","#ec4899"))
        st.caption(" -> ".join(names))
    cond=session["conditioning"]
    st.markdown("#### 🔥 Metabolic / ESD Protocol")
    render_card("5. Dynamic MetCon / ESD",cond["name"],cond["work"]+" | Rest: "+cond["rest"],cond["intensity"],cond["protocol"],"Multi-planar","Energy System / Conditioning",ACCENTS["Aerobic"])
    st.markdown("**Exact execution:**")
    for i,station in enumerate(cond["stations"],1): st.markdown(f"**{i}.** {station}")
    st.caption(cond["reason"])

# ---------------------------
# Testing trends ---------------------------
def test_snapshot(a):
    return {"timestamp":datetime.now().isoformat(timespec="seconds"),"cmj":a.cmj,"broad_jump":a.broad_jump,"sprint_5m":a.sprint_5m,"sprint_10m":a.sprint_10m,"cod":a.cod,"cooper_m":a.cooper_m,"left_jump":a.left_jump,"right_jump":a.right_jump,"squat_1rm":a.squat_1rm,"bench_1rm":a.bench_1rm,"forehand_throw_m":a.forehand_throw_m,"backhand_throw_m":a.backhand_throw_m,"rotational_throw_m":a.rotational_throw_m}

def log_training_session(a,session_rpe,pain_after,performance_change,duration_min=60,notes=""):
    ids=[]
    if st.session_state.get("generated_plan"):
        # Log the most recent displayed day if available.
        try:
            sess=st.session_state.generated_plan[1][1][0]
            ids=[x.id for x in sess.get("exercises",[])]
        except Exception: ids=[]
    rec={"timestamp":datetime.now().isoformat(timespec="seconds"),"athlete":a.name,"sport":a.sport,"session_rpe":float(session_rpe),"pain_after":int(pain_after),"performance_change":int(performance_change),"duration_min":int(duration_min),"exercise_ids":ids,"notes":notes}
    st.session_state.training_log.append(rec); st.session_state.last_feedback=rec
    return rec


# ============================================================
# ATHLETE-IQ v6.2 - STRENGTH + MOVEMENT + NEUROMUSCULAR INTELLIGENCE
# ============================================================
# This layer intentionally sits above the v6.1 engine.  It makes the
# decision tree stricter without removing the existing UI and data model.

# Expanded resistance library: common gym patterns that were underrepresented in v6.1.
AIQ62_EXTRA_EXERCISES = [
    Exercise("r21","Dumbbell Shoulder Press","Resistance","Vertical Push",["Strength","Hypertrophy"],["Dumbbells"],"Beginner",fatigue=3),
    Exercise("r22","Machine Chest Press","Resistance","Horizontal Push",["Strength","Hypertrophy"],["Cable Systems & Selectorized"],"Beginner",tier="Machine",fatigue=3),
    Exercise("r23","Machine Shoulder Press","Resistance","Vertical Push",["Strength","Hypertrophy"],["Cable Systems & Selectorized"],"Beginner",tier="Machine",fatigue=3),
    Exercise("r24","Cable Chest Press","Resistance","Horizontal Push",["Strength","Hypertrophy","Stability"],["Cable Systems & Selectorized"],"Beginner",fatigue=2),
    Exercise("r25","Seated Cable Row","Resistance","Pull",["Strength","Hypertrophy"],["Cable Systems & Selectorized"],"Beginner",fatigue=2),
    Exercise("r26","Leg Press","Resistance","Squat",["Strength","Hypertrophy"],["Cable Systems & Selectorized"],"Beginner",tier="Machine",fatigue=3),
    Exercise("r27","Seated Leg Curl","Resistance","Accessory",["Strength","Hypertrophy","Hamstring"],["Cable Systems & Selectorized"],"Beginner",tier="Machine",fatigue=2),
    Exercise("r28","Dumbbell Step-Up","Resistance","Unilateral Squat",["Strength","Stability"],["Dumbbells"],"Beginner",unilateral=True,fatigue=2),
    Exercise("r29","Single-Arm Dumbbell Row","Resistance","Pull",["Strength","Hypertrophy","Stability"],["Dumbbells"],"Beginner",unilateral=True,fatigue=2),
]
for _x in AIQ62_EXTRA_EXERCISES:
    EXERCISES[_x.id]=_x

AIQ62_SYSTEMS = [
    "Corrective / Activation", "Mobility", "Stability / Core",
    "Resistance", "Plyometrics", "Acceleration / Speed", "Agility / COD",
    "Neuromuscular Coordination", "Aerobic", "Anaerobic / Repeated Sprint"
]

AIQ62_GOAL_SYSTEMS = {
    "Max Strength": {"Resistance": 34, "Neuromuscular Coordination": 3, "Stability / Core": 5},
    "Strength": {"Resistance": 30, "Neuromuscular Coordination": 4, "Stability / Core": 6},
    "Hypertrophy": {"Resistance": 34, "Stability / Core": 5},
    "Power": {"Plyometrics": 28, "Resistance": 18, "Neuromuscular Coordination": 12, "Acceleration / Speed": 10},
    "Speed": {"Acceleration / Speed": 32, "Plyometrics": 18, "Neuromuscular Coordination": 12, "Resistance": 8},
    "Agility": {"Agility / COD": 30, "Neuromuscular Coordination": 22, "Plyometrics": 12, "Resistance": 8},
    "Endurance": {"Aerobic": 32, "Anaerobic / Repeated Sprint": 14, "Resistance": 12, "Neuromuscular Coordination": 5},
    "Sport Performance": {"Plyometrics": 20, "Acceleration / Speed": 18, "Agility / COD": 18, "Neuromuscular Coordination": 18, "Resistance": 16},
    "Fat Loss": {"Resistance": 20, "Aerobic": 22, "Anaerobic / Repeated Sprint": 18, "Neuromuscular Coordination": 5},
    "General Fitness": {"Resistance": 22, "Aerobic": 14, "Neuromuscular Coordination": 8, "Agility / COD": 7},
    "Overall Development": {"Resistance": 18, "Neuromuscular Coordination": 12, "Plyometrics": 10, "Agility / COD": 10, "Aerobic": 10},
}

AIQ62_SECONDARY_TO_SYSTEM = {
    "Strength":"Resistance", "Max Strength":"Resistance", "Hypertrophy":"Resistance",
    "Power":"Plyometrics", "Speed":"Acceleration / Speed", "Agility":"Agility / COD",
    "Aerobic Capacity":"Aerobic", "Anaerobic Capacity":"Anaerobic / Repeated Sprint",
    "Mobility":"Mobility", "Stability":"Stability / Core", "Plyometric Ability":"Plyometrics",
    "Movement Quality":"Neuromuscular Coordination", "Core / Trunk":"Stability / Core",
    "Recovery / Work Capacity":"Aerobic", "Body Composition":"Resistance"
}

# Movement relationships are deliberately explicit.  The engine uses them for
# weekly coverage, not merely for display labels.
def aiq62_movement_meta(x):
    n=x.name.lower(); pat=x.pattern.lower(); tags=' '.join(x.tags).lower(); q=' '.join(x.quality).lower()
    unilateral = bool(x.unilateral or any(k in n for k in ["single-leg","single leg","split squat","lunge","step-up","rear-foot","half-kneeling","single-arm","one-arm","suitcase"]))
    bilateral = not unilateral and any(k in pat+n for k in ["squat","deadlift","bench","press","push-up","pull-up","pulldown","row","hip thrust"])
    contralateral = any(k in n+pat+tags for k in ["contralateral","bird dog","dead bug","bear crawl","cross-body","opposite","single-leg rdl"])
    ipsilateral = any(k in n+pat+tags for k in ["ipsilateral","same-side","suitcase","single-arm"])
    if "single-leg rdl" in n: contralateral=True
    plane = x.plane
    if "rotation" in n or "rotational" in tags or "anti-rotation" in pat: plane="Transverse"
    if any(k in n for k in ["lateral","side","shuffle","crossover"]): plane="Frontal" if plane=="Sagittal" else plane
    coordination = []
    if unilateral: coordination.append("Unilateral")
    if bilateral: coordination.append("Bilateral")
    if contralateral: coordination.append("Contralateral")
    if ipsilateral: coordination.append("Ipsilateral")
    if not coordination: coordination.append("General")
    neuromuscular = any(k in n+tags+q for k in ["reaction","reactive","coordination","rhythm","mirror","split step","decision","balance","stabil","crawl","pogo","bound","hop"])
    return {"unilateral":unilateral,"bilateral":bilateral,"contralateral":contralateral,"ipsilateral":ipsilateral,"plane":plane,"coordination":coordination,"neuromuscular":neuromuscular}

AIQ62_META={eid:aiq62_movement_meta(x) for eid,x in EXERCISES.items()}

# Sport-locked drills are intentionally narrow.  Resistance exercises are
# treated as transferable unless their names are clearly sport drills.
AIQ62_LOCKED_TERMS = [
    "shadow boxing", "boxing reaction", "shadow kumite", "punch throw", "punch ->",
    "shadow mma", "sprawl -> stand", "swim-pull", "swimmer hollow", "streamline",
    "split step", "tennis", "racket", "soccer ball", "dribble", "volleyball approach",
    "block hop", "handball throw", "rugby sled"
]

def aiq62_is_locked(x):
    n=x.name.lower()
    return any(t in n for t in AIQ62_LOCKED_TERMS) or (x.sport_tags and x.system not in ["Resistance","Mobility","Stability / Core"] and not any(t in n for t in ["jump","hop","bound","sprint","shuffle","shuttle","run"]))

def aiq62_sport_ok(x,a):
    if not aiq62_is_locked(x): return True
    return exercise_sport_compatible(x,a)

def aiq62_equipment_ok(x,a):
    return any(eq in a.equipment for eq in x.equipment)

def aiq62_level_ok(x,a):
    lvl=training_level(a.training_years)
    order={"Beginner":0,"Intermediate":1,"Advanced":2}
    return order.get(x.level,0) <= order.get(lvl,1)+1

def aiq62_system_ok(x,system):
    if system=="Neuromuscular Coordination":
        return AIQ62_META.get(x.id,{}).get("neuromuscular",False) or any(k in ' '.join(x.quality).lower()+x.name.lower() for k in ["coordination","reaction","balance","stability","rhythm"])
    return x.system==system

def aiq62_goal_bonus(a,x):
    g=a.primary_goal; n=x.name.lower(); q=' '.join(x.quality).lower(); pat=x.pattern.lower(); score=0
    if g in ["Max Strength","Strength"]:
        if x.system=="Resistance": score+=28
        if x.fatigue>=3: score+=4
    elif g=="Hypertrophy":
        if x.system=="Resistance": score+=30
        if "hypertrophy" in q: score+=8
    elif g=="Power":
        if x.system in ["Plyometrics","Acceleration / Speed"]: score+=28
        if "power" in q or x.tempo_power.startswith("X"): score+=8
    elif g=="Speed":
        if x.system=="Acceleration / Speed": score+=34
        if x.system=="Plyometrics": score+=12
    elif g=="Agility":
        if x.system=="Agility / COD" or AIQ62_META.get(x.id,{}).get("neuromuscular"): score+=30
    elif g=="Endurance":
        if x.system in ["Aerobic","Anaerobic / Repeated Sprint"]: score+=25
        if "endurance" in q: score+=8
    elif g=="Sport Performance":
        if x.system in ["Plyometrics","Acceleration / Speed","Agility / COD","Neuromuscular Coordination"]: score+=22
        if x.sport_tags and aiq62_sport_ok(x,a): score+=7
    elif g=="Fat Loss":
        if x.system in ["Resistance","Aerobic","Anaerobic / Repeated Sprint"]: score+=18
    elif g in ["General Fitness","Overall Development"]:
        if x.system=="Resistance": score+=18
    return score

def aiq62_position_bonus(x,a):
    pos=(a.position or "").lower(); n=x.name.lower(); score=0
    mapping={
        "goalkeeper":["lateral","reactive","jump","bound","deceleration","acceleration","balance"],
        "winger":["acceleration","sprint","shuttle","crossover","lateral","bound","unilateral"],
        "striker":["acceleration","sprint","unilateral","jump","rotational","hinge"],
        "midfielder":["shuttle","aerobic","acceleration","lateral","single-leg","split squat"],
        "defender":["squat","hinge","lateral","deceleration","jump","acceleration"],
        "freestyle":["swimmer","pull","streamline","shoulder"],
        "butterfly":["swimmer","pull","shoulder","core","streamline"],
        "backstroke":["swimmer","pull","shoulder","core"],
        "breaststroke":["adductor","hip","squat","swimmer","core"],
    }
    for k,terms in mapping.items():
        if k in pos: score += sum(2 for t in terms if t in n)
    return score

def aiq62_exercise_allowed(x,a,constraints):
    if not aiq62_equipment_ok(x,a): return False
    if not aiq62_sport_ok(x,a): return False
    if not aiq62_level_ok(x,a): return False
    # For general resistance, sport tags are preference tags rather than hard locks.
    # Truly sport-locked drills are handled by aiq62_sport_ok.
    if constraints.get("pain_gate") and x.system in ["Plyometrics","Agility / COD","Acceleration / Speed","Anaerobic / Repeated Sprint"]: return False
    if constraints.get("low_impact") and x.impact=="High": return False
    for k in constraints.get("injury_keys",[]):
        if k in x.avoid_if: return False
    return True

def aiq62_select_exercises(a,p,system_scores,system,n,month,used_ids,constraints,coverage=None):
    coverage=coverage or set(); candidates=[]
    for x in EXERCISES.values():
        if x.id in used_ids: continue
        if not aiq62_system_ok(x,system): continue
        if not aiq62_equipment_ok(x,a): continue
        if not aiq62_sport_ok(x,a): continue
        if not aiq62_level_ok(x,a): continue
        if not aiq62_exercise_allowed(x,a,constraints): continue
        meta=AIQ62_META.get(x.id,{})
        score=aiq62_goal_bonus(a,x)+aiq62_position_bonus(x,a)
        score += system_scores.get(system,0)*0.12
        # Whole-athlete coverage: strongly reward missing movement families.
        family= x.pattern.lower()
        family_bonus=0
        if system=="Resistance":
            if any(k in family for k in ["squat","unilateral squat","lunge"]) and "knee" not in coverage: family_bonus+=24
            if "hinge" in family and "hinge" not in coverage: family_bonus+=24
            if "horizontal push" in family and "h_push" not in coverage: family_bonus+=24
            if "vertical push" in family and "v_push" not in coverage: family_bonus+=24
            if "pull" in family and "pull" not in coverage: family_bonus+=24
            if meta.get("unilateral") and "unilateral" not in coverage: family_bonus+=16
            if meta.get("bilateral") and "bilateral" not in coverage: family_bonus+=10
            if meta.get("contralateral") and "contralateral" not in coverage: family_bonus+=12
            if meta.get("ipsilateral") and "ipsilateral" not in coverage: family_bonus+=10
        if system=="Neuromuscular Coordination":
            if meta.get("contralateral") and "contralateral" not in coverage: family_bonus+=25
            if meta.get("ipsilateral") and "ipsilateral" not in coverage: family_bonus+=22
            if meta.get("unilateral") and "unilateral" not in coverage: family_bonus+=15
        if meta.get("plane") not in coverage: family_bonus+=5
        # Monthly diversity: don't just rotate order; prefer a different family/variant.
        if month>1 and exercise_recently_used(x.id,days=30): score-=12
        score+=family_bonus
        candidates.append((score,x))
    candidates.sort(key=lambda z:(z[0],z[1].fatigue),reverse=True)
    return [x for _,x in candidates[:max(n,1)]]

# Replace priorities so primary goal, secondary goals, screening, sport and position all propagate.
def priorities(a):
    base={k:8.0 for k in ["Strength","Hypertrophy","Power","Acceleration","COD","Aerobic","Anaerobic","Mobility","Stability","Rotational Power","Neuromuscular Coordination"]}
    demands=SPORT_DEMANDS.get(a.sport,SPORT_DEMANDS.get("General Fitness",{}))
    for k,v in demands.items():
        if k in base: base[k]+=float(v)*25
    scores=performance_scores(a)
    gapmap={"Strength":"Strength","Power":"Power","Acceleration":"Acceleration","COD":"COD","Aerobic":"Aerobic","Stability":"Stability","Mobility":"Mobility","Rotational Power":"Rotational Power"}
    for q,src in gapmap.items():
        if q in base: base[q]+=max(0,100-float(scores.get(src,50)))*0.22
    goal_quality={"Max Strength":"Strength","Strength":"Strength","Hypertrophy":"Hypertrophy","Power":"Power","Speed":"Acceleration","Agility":"COD","Endurance":"Aerobic","Fat Loss":"Aerobic"}
    if a.primary_goal in goal_quality: base[goal_quality[a.primary_goal]]+=45
    elif a.primary_goal=="Sport Performance":
        for q in ["Power","Acceleration","COD","Neuromuscular Coordination","Strength"]: base[q]+=22
    elif a.primary_goal in ["Overall Development","General Fitness"]:
        for q in ["Strength","Power","Acceleration","COD","Aerobic","Mobility","Stability","Neuromuscular Coordination"]: base[q]+=14
    for g in a.secondary_goals:
        key={"Strength":"Strength","Max Strength":"Strength","Hypertrophy":"Hypertrophy","Power":"Power","Speed":"Acceleration","Agility":"COD","Aerobic Capacity":"Aerobic","Anaerobic Capacity":"Anaerobic","Mobility":"Mobility","Stability":"Stability","Plyometric Ability":"Power","Movement Quality":"Neuromuscular Coordination","Core / Trunk":"Stability","Recovery / Work Capacity":"Aerobic","Body Composition":"Strength"}.get(g)
        if key: base[key]+=16
    if a.sport in ["Tennis","Racket Sports (Squash/Padel)"]: base["Rotational Power"]+=18
    flags=screening_flags(a)
    if flags:
        base["Mobility"]+=12; base["Stability"]+=14; base["Neuromuscular Coordination"]+=8
    # Quantitative screening indices now feed the closed loop directly.
    base["Stability"] += max(0.0, 80.0-stability_index(a))*0.35
    base["Neuromuscular Coordination"] += max(0.0, 80.0-neuromuscular_index(a))*0.35
    base["Mobility"] += max(0.0, 80.0-mobility_index(a))*0.25
    base["Neuromuscular Coordination"] += max(0.0, 80.0-sfma_index(a))*0.15
    base["Stability"] += max(0.0, 80.0-fms_index(a))*0.15
    side_diffs=[]
    for pair in (a.fms_sides or {}).values():
        if isinstance(pair,dict) and "L" in pair and "R" in pair:
            side_diffs.append(abs(float(pair["L"])-float(pair["R"])))
    if side_diffs and max(side_diffs)>=1:
        base["Stability"] += 6; base["Neuromuscular Coordination"] += 6
    if asymmetry(a.left_jump,a.right_jump)>=8: base["Stability"]+=12; base["Neuromuscular Coordination"]+=10
    if a.season=="In-Season / Competition":
        base["Hypertrophy"]*=.55; base["Strength"]*=.82; base["Power"]*=1.05; base["Acceleration"]*=1.05
    if a.season=="Taper / Peak":
        base["Hypertrophy"]*=.35; base["Strength"]*=.60; base["Power"]*=1.20; base["Acceleration"]*=1.15; base["COD"]*=1.10
    total=sum(max(v,0) for v in base.values()) or 1
    return {k:round(max(v,0)/total*100,1) for k,v in sorted(base.items(),key=lambda z:z[1],reverse=True)}

def system_allocation(a,p,constraints):
    mapping={
        "Corrective / Activation":["Mobility","Stability"],"Mobility":["Mobility"],"Stability / Core":["Stability"],
        "Resistance":["Strength","Hypertrophy"],"Plyometrics":["Power"],"Acceleration / Speed":["Acceleration"],
        "Agility / COD":["COD"],"Neuromuscular Coordination":["Neuromuscular Coordination"],"Aerobic":["Aerobic"],"Anaerobic / Repeated Sprint":["Anaerobic"]
    }
    out={s:max([p.get(q,0) for q in qs]+[0]) for s,qs in mapping.items()}
    for s,b in AIQ62_GOAL_SYSTEMS.get(a.primary_goal,AIQ62_GOAL_SYSTEMS["Overall Development"]).items(): out[s]=out.get(s,0)+b
    for g in a.secondary_goals:
        s=AIQ62_SECONDARY_TO_SYSTEM.get(g)
        if s: out[s]=out.get(s,0)+8
    if constraints.get("low_impact"):
        for s in ["Plyometrics","Agility / COD","Acceleration / Speed","Anaerobic / Repeated Sprint"]: out[s]*=.45
        out["Neuromuscular Coordination"]*=1.10
    if not constraints.get("high_fatigue_allowed",True): out["Anaerobic / Repeated Sprint"]*=.65
    return {k:round(v,2) for k,v in sorted(out.items(),key=lambda z:z[1],reverse=True)}

# Goal-specific session architecture with mandatory whole-body resistance coverage.
def session_template(a,day,system_scores,constraints):
    g=a.primary_goal
    if constraints.get("low_impact"):
        return ["Corrective / Activation","Mobility","Resistance","Neuromuscular Coordination","Aerobic"]
    templates={
        "Max Strength":["Corrective / Activation","Resistance","Resistance","Resistance","Neuromuscular Coordination"],
        "Strength":["Corrective / Activation","Resistance","Resistance","Neuromuscular Coordination","Anaerobic / Repeated Sprint"],
        "Hypertrophy":["Corrective / Activation","Resistance","Resistance","Resistance","Aerobic"],
        "Power":["Corrective / Activation","Plyometrics","Resistance","Neuromuscular Coordination","Acceleration / Speed"],
        "Speed":["Corrective / Activation","Acceleration / Speed","Plyometrics","Resistance","Neuromuscular Coordination"],
        "Agility":["Corrective / Activation","Agility / COD","Neuromuscular Coordination","Resistance","Anaerobic / Repeated Sprint"],
        "Endurance":["Corrective / Activation","Aerobic","Resistance","Neuromuscular Coordination","Anaerobic / Repeated Sprint"],
        "Sport Performance":["Corrective / Activation","Plyometrics","Resistance","Neuromuscular Coordination","Agility / COD"],
        "Fat Loss":["Corrective / Activation","Resistance","Aerobic","Neuromuscular Coordination","Anaerobic / Repeated Sprint"],
        "General Fitness":["Corrective / Activation","Resistance","Neuromuscular Coordination","Resistance","Aerobic"],
        "Overall Development":["Corrective / Activation","Resistance","Neuromuscular Coordination","Plyometrics","Aerobic"],
    }
    base=templates.get(g,templates["Overall Development"])
    # Day variation changes the secondary systems, but never removes whole-body strength exposure.
    if day%3==2 and g in ["Power","Speed","Agility","Sport Performance"]:
        base=["Corrective / Activation",base[1],"Resistance",base[3],base[4]]
    if day%3==0 and g in ["Strength","Max Strength","Hypertrophy"]:
        base=["Corrective / Activation","Resistance","Neuromuscular Coordination",base[2],base[4]]
    return base

def build_rotation(a,months,p,system_scores,constraints):
    rotation={}
    used_global=set()
    for m in range(1,months+1):
        rotation[m]={}
        for system in AIQ62_SYSTEMS:
            if system=="Corrective / Activation" and system not in system_scores: continue
            picks=aiq62_select_exercises(a,p,system_scores,system,5,m,list(used_global),constraints,set())
            if picks:
                # Month rotation chooses a genuinely different variant/family when possible.
                x=picks[(m-1)%len(picks)]
                rotation[m][system]=x.id; used_global.add(x.id)
    return rotation

def _aiq62_coverage_add(coverage,x):
    m=AIQ62_META.get(x.id,{})
    p=x.pattern.lower()
    if any(k in p for k in ["squat","unilateral squat","lunge"]): coverage.add("knee")
    if "hinge" in p: coverage.add("hinge")
    if "horizontal push" in p: coverage.add("h_push")
    if "vertical push" in p: coverage.add("v_push")
    if "pull" in p: coverage.add("pull")
    for k in ["unilateral","bilateral","contralateral","ipsilateral"]:
        if m.get(k): coverage.add(k)
    coverage.add(m.get("plane","General"))

def build_session(a,week,day,month,rotation,p,system_scores,constraints):
    systems=session_template(a,day,system_scores,constraints)
    used=[]; exercises=[]; coverage=set()
    # Two resistance slots deliberately use coverage-aware selection so pressing and pulling
    # are not crowded out by sport drills.
    for system in systems:
        selected=[]
        if system=="Corrective / Activation":
            selected=aiq62_select_exercises(a,p,system_scores,system,1,month,used,constraints,coverage)
        else:
            selected=aiq62_select_exercises(a,p,system_scores,system,2 if system=="Resistance" else 1,month,used,constraints,coverage)
        for x in selected:
            if x.id not in used:
                used.append(x.id); exercises.append(x); _aiq62_coverage_add(coverage,x)
                if system!="Resistance": break
    cond=conditioning_decision(a,p,constraints,week,month,day)
    complex_block=None
    if day==1 and constraints.get("high_impact_allowed") and constraints.get("high_fatigue_allowed"):
        complex_block=choose_complex(a,p,systems,constraints,month)
    return {"day":day,"week":week,"month":month,"phase":phase_for(a,week),"mesocycle_phase":mesocycle_phase(a,month),"systems":systems,"exercises":exercises,"conditioning":cond,"complex":complex_block,"readiness":constraints["readiness"],"movement_coverage":sorted(coverage)}

def aiq62_position_stations(a,month,week,day):
    s=a.sport.lower(); p=(a.position or "").lower()
    if "soccer" in s:
        if "goalkeeper" in p: pools=[
            ["Lateral Reaction Shuffle - 15 s","Low Box Jump / Vertical Jump - 4 reps","Reactive Direction Change - 15 s","10 m Acceleration - 2 reps"],
            ["Lateral Bound -> Stick - 4/side","Short Acceleration - 5-10 m","Visual Reaction Direction Change - 15 s","DB Farmer Carry / March - 20 m"],
            ["Deceleration -> Re-acceleration - 3/side","Single-Leg Hop -> Stick - 4/side","Reactive Shuffle - 15 s","DB Split Squat - 8/side"]]
        elif "winger" in p: pools=[
            ["5-10 m Acceleration - 3 reps","Crossover -> Acceleration - 2/side","Reactive Lateral Shuffle - 15 s","DB Reverse Lunge - 8/side"],
            ["Curved Acceleration - 2 reps/side","Lateral Bound - 4/side","Repeated Sprint - 15 s","DB RDL - 8 reps"],
            ["Deceleration -> Re-acceleration - 3 reps","Open-Step COD - 3/side","Tempo Shuttle - 20 s","DB Split Squat - 8/side"]]
        else: pools=[
            ["5-10 m Acceleration - 3 reps","Unilateral Jump -> Stick - 3/side","Reactive Direction Change - 15 s","DB Split Squat - 8/side"],
            ["Acceleration Start - 3 reps","Lateral Bound - 4/side","Short Shuttle Sprint - 20 s","DB RDL - 8 reps"],
            ["Deceleration -> Re-acceleration - 3 reps","Crossover -> Sprint - 2/side","Repeated Sprint - 15 s","DB Reverse Lunge - 8/side"]]
        return pools[(month-1)%len(pools)]
    if "swimming" in s:
        pools=[
            ["DB Pullover - 10 reps","Swimmer Hollow-Body Hold - 30 s","Prone Y-T-W - 6/position","DB Romanian Deadlift - 8 reps"],
            ["DB Bench Press - 8 reps","Dead Bug - 30 s","DB Single-Arm Row - 8/side","Tempo Shuttle - 20 s"],
            ["DB Overhead Press - 8 reps","Bird Dog - 8/side","DB Reverse Lunge - 8/side","Fast March - 30 s"]]
        return pools[(month-1)%3]
    if "boxing" in s or "mma" in s:
        pools=[
            ["Shadow Boxing - 30 s","Reactive Footwork - 20 s","DB Push Press - 6 reps","DB Reverse Lunge - 8/side"],
            ["Visual Reaction Boxing - 20 s","Split-Stance Footwork - 20 s","DB Bench Press - 8 reps","Suitcase Carry - 20 m"],
            ["Shadow Boxing - 30 s","Reaction Callout - 20 s","DB Romanian Deadlift - 8 reps","Push-Up - 10 reps"]]
        return pools[(month-1)%3]
    if "tennis" in s or "racket" in s:
        pools=[
            ["Split Step -> Reactive Lateral Shuffle - 15 s","Rotational DB Press - 6/side","Crossover -> 5 m Acceleration - 2/side","DB Split Squat - 8/side"],
            ["Visual Reaction COD - 15 s","DB Rotational Press - 6/side","Lateral Bound -> Stick - 4/side","DB RDL - 8 reps"],
            ["Open-Stance COD - 3/side","DB Single-Arm Row - 8/side","Reactive Shuffle - 15 s","Suitcase Carry - 20 m"]]
        return pools[(month-1)%3]
    # General fallback is deliberately equipment-neutral and not sport-locked.
    return [["Fast March / Low-Impact Run - 30 s","DB Goblet Squat - 8 reps","DB Row - 8/side","Reactive Direction Change - 15 s"],
            ["DB Reverse Lunge - 8/side","Push-Up - 10 reps","Single-Leg Balance Reach - 6/side","Tempo Shuttle - 20 s"],
            ["DB RDL - 8 reps","DB Bench Press - 8 reps","Lateral Shuffle - 15 s","Dead Bug - 30 s"]][(month-1)%3]

def conditioning_decision(a,p,constraints,week,month=1,day=1):
    protocol=_pick_protocol(a,month,week,day,p,constraints)
    # Goal changes the protocol too; this prevents the same method from surviving every goal change.
    if a.primary_goal in ["Max Strength","Strength"] and month==1: protocol="Intervals"
    if a.primary_goal=="Power": protocol=["Intervals","Every 90s","Circuit"][min(month-1,2)]
    if a.primary_goal=="Agility": protocol=["Intervals","EMOM","AMRAP"][min(month-1,2)]
    if a.primary_goal=="Endurance": protocol=["Intervals","AMRAP","Ladder"][min(month-1,2)]
    if constraints.get("low_impact") or week==4: protocol="Intervals"
    loadmod=adaptive_load_modifier(a); base={1:3,2:4,3:4,4:2}[week]; rounds=max(2,int(round(base*loadmod)))
    if constraints["band"]=="YELLOW": target=7.0
    elif constraints["band"]=="RED": target=5.5
    else: target=6.5 if month==1 else 7.5 if month==2 else 8.0
    stations=aiq62_position_stations(a,month,week,day)
    stations=sanitize_metcon_stations(a,stations)
    # Diversity by month: the pool itself changes, not just its order.
    if protocol=="EMOM": work=f"EMOM {rounds*len(stations)} min - 1 station per minute"; rest="Remaining time in each minute"
    elif protocol=="AMRAP": work=f"AMRAP {max(6,int({1:8,2:10,3:12,4:6}[week]*loadmod))} min - repeat all stations"; rest="Self-regulated transitions"
    elif protocol=="Tabata": work=f"Tabata {rounds} blocks - 20 s work / 10 s transition"; rest="60-90 s between blocks"
    elif protocol=="Every 90s": work=f"Every 90 s x {rounds*len(stations)} station exposures"; rest="Remaining time in each 90-s window"
    elif protocol=="Ladder": work=f"Ladder {rounds} rounds - 20/30/40 s work progression"; rest="45-75 s between rounds"
    elif protocol=="Circuit": work=f"Circuit {rounds} rounds - 30-40 s work / 20 s transition"; rest="90 s between rounds"
    else: work=f"Intervals {rounds} rounds - 30 s work / 30 s recovery"; rest="60-90 s between rounds"
    return {"system":"Anaerobic / Repeated Sprint" if protocol in ["Tabata","EMOM","AMRAP","Circuit"] else "Aerobic","name":f"{a.sport} | {a.position} | {protocol} | Month {month}","protocol":protocol,"stations":stations,"work":work,"rest":rest,"intensity":f"Target RPE {target:.1f} | Load modifier x{loadmod:.2f}","reason":f"Sport + position + primary goal + season + readiness + equipment + monthly stimulus selection."}

def build_program(a,months):
    constraints=constraint_engine(a); p=priorities(a); systems=system_allocation(a,p,constraints); rotation=build_rotation(a,months,p,systems,constraints)
    days=max(1,min(a.gym_days_available,4))
    program={m:{w:[build_session(a,w,d,m,rotation,p,systems,constraints) for d in range(1,days+1)] for w in range(1,5)} for m in range(1,months+1)}
    return program,{"constraints":constraints,"priorities":p,"systems":systems,"rotation":rotation,"load_status":constraints.get("load_status"),"movement_engine":"v6.2","coverage":"whole-body resistance + unilateral/bilateral/ipsilateral/contralateral + neuromuscular coordination"}

# ============================================================
# ATHLETE-IQ v7.0 - ADAPTIVE PROGRAMMING ENGINE OVERRIDE
# ============================================================
# This block intentionally sits before the UI. It replaces the generic
# v6.2 exercise-selection layer while preserving the working screening,
# feedback, profile, and metcon UI.

V7_VERSION = "7.0 Adaptive Programming Engine"

# ---------------------------
# Expanded resistance library
# ---------------------------
V7_EXTRA_EXERCISES = [
    ex("v7r21", "Dumbbell Romanian Deadlift", "Resistance", "Hinge", ["Strength", "Hypertrophy", "Hamstring"], ["Dumbbells"], "Beginner", fatigue=3, tags=["Hamstring", "Posterior Chain"]),
    ex("v7r22", "Single-Leg Romanian Deadlift", "Resistance", "Unilateral Hinge", ["Strength", "Stability", "Hamstring"], ["Dumbbells", "Bodyweight"], "Intermediate", fatigue=3, unilateral=True, tags=["Hamstring", "Posterior Chain", "Unilateral"]),
    ex("v7r23", "Dumbbell Step-Up", "Resistance", "Unilateral Squat", ["Strength", "Stability", "Unilateral"], ["Dumbbells", "Plyo Boxes & Agility Ladders"], "Beginner", fatigue=2, unilateral=True, tags=["Unilateral"]),
    ex("v7r24", "Walking Dumbbell Lunge", "Resistance", "Unilateral Squat", ["Strength", "Hypertrophy", "Unilateral"], ["Dumbbells"], "Beginner", fatigue=3, unilateral=True),
    ex("v7r25", "Lateral Lunge", "Resistance", "Frontal Unilateral", ["Strength", "Mobility", "COD", "Unilateral"], ["Dumbbells", "Bodyweight"], "Beginner", plane="Frontal", fatigue=2, unilateral=True),
    ex("v7r26", "Cossack Squat", "Resistance", "Frontal Unilateral", ["Strength", "Mobility", "Unilateral"], ["Bodyweight", "Dumbbells"], "Intermediate", plane="Frontal", fatigue=2, unilateral=True),
    ex("v7r27", "Barbell Romanian Deadlift", "Resistance", "Hinge", ["Strength", "Hypertrophy"], ["Barbells & Plates"], "Intermediate", fatigue=4, tags=["Hamstring", "Posterior Chain"]),
    ex("v7r28", "Leg Press", "Resistance", "Knee Press", ["Strength", "Hypertrophy"], ["Cable Systems & Selectorized"], "Beginner", fatigue=3, tags=["Bilateral"]),
    ex("v7r29", "Seated Leg Curl", "Resistance", "Knee Flexion", ["Strength", "Hypertrophy", "Hamstring"], ["Cable Systems & Selectorized"], "Beginner", fatigue=2, tags=["Hamstring"]),
    ex("v7r30", "Standing Calf Raise", "Resistance", "Calf", ["Strength", "Tendon"], ["Dumbbells", "Cable Systems & Selectorized"], "Beginner", fatigue=1),
    ex("v7r31", "Tibialis Raise", "Resistance", "Ankle", ["Strength", "Tendon"], ["Bodyweight", "Dumbbells"], "Beginner", fatigue=1),
    ex("v7r32", "Incline Dumbbell Press", "Resistance", "Horizontal Push", ["Strength", "Hypertrophy"], ["Dumbbells"], "Beginner", fatigue=3),
    ex("v7r33", "Single-Arm Dumbbell Press", "Resistance", "Unilateral Horizontal Push", ["Strength", "Stability", "Contralateral"], ["Dumbbells"], "Intermediate", fatigue=3, unilateral=True, tags=["Unilateral", "Contralateral"]),
    ex("v7r34", "Dumbbell Shoulder Press", "Resistance", "Vertical Push", ["Strength", "Hypertrophy"], ["Dumbbells"], "Beginner", fatigue=3),
    ex("v7r35", "Single-Arm Landmine Press", "Resistance", "Unilateral Vertical Push", ["Strength", "Power", "Stability"], ["Barbells & Plates"], "Intermediate", plane="Transverse", fatigue=2, unilateral=True, tags=["Unilateral", "Ipsilateral"]),
    ex("v7r36", "Dumbbell Floor Press", "Resistance", "Horizontal Push", ["Strength", "Hypertrophy"], ["Dumbbells"], "Beginner", fatigue=2),
    ex("v7r37", "Parallel Bar Dip", "Resistance", "Vertical Push", ["Strength", "Hypertrophy"], ["Rigs & Suspension (TRX/Wood Rings)"], "Intermediate", fatigue=3, avoid_if=["shoulder"]),
    ex("v7r38", "Chin-Up", "Resistance", "Pull", ["Strength", "Hypertrophy"], ["Bodyweight", "Rigs & Suspension (TRX/Wood Rings)"], "Intermediate", fatigue=3),
    ex("v7r39", "One-Arm Dumbbell Row", "Resistance", "Unilateral Pull", ["Strength", "Hypertrophy", "Stability", "Ipsilateral", "Contralateral"], ["Dumbbells"], "Beginner", fatigue=2, unilateral=True, tags=["Unilateral", "Ipsilateral", "Contralateral"]),
    ex("v7r40", "Seated Cable Row", "Resistance", "Horizontal Pull", ["Strength", "Hypertrophy"], ["Cable Systems & Selectorized"], "Beginner", fatigue=2),
    ex("v7r41", "Single-Arm Cable Row", "Resistance", "Unilateral Pull", ["Strength", "Stability", "Unilateral"], ["Cable Systems & Selectorized"], "Intermediate", fatigue=2, unilateral=True, tags=["Unilateral"]),
    ex("v7r42", "Face Pull", "Resistance", "Scapular Pull", ["Stability", "Shoulder", "Hypertrophy"], ["Cable Systems & Selectorized", "Bands"], "Beginner", fatigue=1),
    ex("v7r43", "Cable Chest Press", "Resistance", "Horizontal Push", ["Strength", "Hypertrophy", "Stability"], ["Cable Systems & Selectorized"], "Beginner", fatigue=2),
    ex("v7r44", "Cable Lat Pulldown", "Resistance", "Vertical Pull", ["Strength", "Hypertrophy"], ["Cable Systems & Selectorized"], "Beginner", fatigue=2),
    ex("v7r45", "Cable Rotation", "Resistance", "Rotation", ["Strength", "Rotational Power", "Core / Trunk"], ["Cable Systems & Selectorized"], "Beginner", plane="Transverse", fatigue=2, tags=["Rotation"]),
    ex("v7r46", "Pallof Press - Split Stance", "Resistance", "Anti-Rotation", ["Stability", "Core / Trunk", "Unilateral"], ["Cable Systems & Selectorized", "Bands"], "Beginner", plane="Transverse", fatigue=1, unilateral=True, tags=["Unilateral", "Anti-Rotation"]),
    ex("v7r47", "Copenhagen Plank", "Resistance", "Frontal Core", ["Strength", "Stability", "Adductor"], ["Bodyweight", "Plyo Boxes & Agility Ladders"], "Intermediate", plane="Frontal", fatigue=2, unilateral=True, tags=["Unilateral", "Adductor"]),
    ex("v7r48", "Contralateral Dead Bug", "Resistance", "Contralateral Core", ["Stability", "Core / Trunk", "Contralateral", "Neuromuscular Coordination"], ["Bodyweight"], "Beginner", fatigue=1, tags=["Contralateral"]),
    ex("v7r49", "Bird Dog Row", "Resistance", "Contralateral Pull", ["Strength", "Stability", "Contralateral"], ["Dumbbells"], "Intermediate", fatigue=2, unilateral=True, tags=["Contralateral", "Unilateral"]),
    ex("v7r50", "Suitcase Carry - Contralateral March", "Resistance", "Contralateral Carry", ["Strength", "Stability", "Core / Trunk", "Contralateral"], ["Dumbbells", "Kettlebells"], "Beginner", plane="Frontal", fatigue=2, unilateral=True, tags=["Contralateral", "Unilateral"]),
    ex("v7r51", "Farmer Carry", "Resistance", "Bilateral Carry", ["Strength", "Stability", "Core / Trunk"], ["Dumbbells", "Kettlebells"], "Beginner", fatigue=2, tags=["Bilateral"]),
    ex("v7r52", "Kettlebell Goblet Squat", "Resistance", "Squat", ["Strength", "Hypertrophy"], ["Kettlebells"], "Beginner", fatigue=2),
    ex("v7r53", "Kettlebell Front Rack Split Squat", "Resistance", "Unilateral Squat", ["Strength", "Stability", "Unilateral"], ["Kettlebells"], "Intermediate", fatigue=3, unilateral=True, tags=["Unilateral"]),
    ex("v7r54", "Barbell Hip Thrust", "Resistance", "Hinge", ["Strength", "Hypertrophy"], ["Barbells & Plates"], "Intermediate", fatigue=3, tags=["Posterior Chain"]),
    ex("v7r55", "Barbell Row", "Resistance", "Horizontal Pull", ["Strength", "Hypertrophy"], ["Barbells & Plates"], "Intermediate", fatigue=3),
    ex("v7r56", "Close-Grip Bench Press", "Resistance", "Horizontal Push", ["Strength", "Hypertrophy"], ["Barbells & Plates"], "Intermediate", fatigue=3),
]
for _x in V7_EXTRA_EXERCISES:
    EXERCISES[_x.id] = _x
E = list(EXERCISES.values())

# ---------------------------
# Explicit exercise-family taxonomy
# ---------------------------
V7_FAMILY_RULES = [
    ("knee_dominant", ["squat", "lunge", "step-up", "leg press", "knee press", "split"]),
    ("hip_dominant", ["deadlift", "romanian", "hip thrust", "swing", "hinge"]),
    ("horizontal_push", ["bench press", "floor press", "chest press", "push-up", "dip"]),
    ("vertical_push", ["overhead press", "shoulder press", "landmine press", "push press"]),
    ("vertical_pull", ["pull-up", "chin-up", "pulldown"]),
    ("horizontal_pull", ["row", "cable row"]),
    ("calf_ankle", ["calf", "tibialis", "ankle"]),
    ("scapular", ["face pull", "external rotation", "y-t-w", "pull-apart"]),
    ("rotation", ["rotation", "rotational", "scoop toss"]),
    ("anti_rotation", ["pallof", "anti-rotation"]),
    ("unilateral_lower", ["split squat", "lunge", "step-up", "single-leg"]),
    ("contralateral", ["contralateral", "bird dog", "dead bug", "cross-body"]),
    ("carry", ["carry", "march"]),
    ("core", ["plank", "dead bug", "bird dog", "hollow", "core"]),
]

def v7_family(x):
    text=(x.name+" "+x.pattern+" "+" ".join(x.tags)).lower()
    for fam,terms in V7_FAMILY_RULES:
        if any(t in text for t in terms):
            if fam == "unilateral_lower" and any(t in text for t in ["split squat","lunge","step-up","single-leg"]):
                return fam
            if fam not in {"unilateral_lower"}:
                return fam
    return x.pattern.lower().replace(" ", "_")

V7_FAMILY = {eid:v7_family(x) for eid,x in EXERCISES.items()}

V7_SPORT_FOCUS = {
    "General Fitness": ["knee_dominant","hip_dominant","horizontal_push","horizontal_pull","vertical_push","vertical_pull","carry","core"],
    "Soccer": ["unilateral_lower","hip_dominant","horizontal_pull","knee_dominant","calf_ankle","scapular","core"],
    "Basketball": ["knee_dominant","unilateral_lower","hip_dominant","horizontal_pull","horizontal_push","calf_ankle","vertical_push"],
    "Tennis": ["unilateral_lower","hip_dominant","horizontal_pull","vertical_push","anti_rotation","rotation","scapular"],
    "Racket Sports (Squash/Padel)": ["unilateral_lower","hip_dominant","horizontal_pull","vertical_push","anti_rotation","rotation","scapular"],
    "Volleyball": ["knee_dominant","hip_dominant","unilateral_lower","vertical_push","horizontal_pull","scapular","calf_ankle"],
    "Handball": ["unilateral_lower","hip_dominant","horizontal_push","horizontal_pull","vertical_pull","rotation","scapular"],
    "Boxing": ["unilateral_lower","hip_dominant","horizontal_push","horizontal_pull","rotation","anti_rotation","scapular"],
    "MMA": ["unilateral_lower","hip_dominant","horizontal_push","horizontal_pull","rotation","anti_rotation","carry","scapular"],
    "Swimming": ["vertical_pull","horizontal_pull","scapular","horizontal_push","hip_dominant","core","rotation"],
    "Karate": ["unilateral_lower","hip_dominant","horizontal_pull","rotation","anti_rotation","scapular","calf_ankle"],
    "Track & Field (Sprints/Jumps)": ["hip_dominant","knee_dominant","unilateral_lower","calf_ankle","horizontal_pull","core"],
    "Rugby/American Football": ["knee_dominant","hip_dominant","horizontal_push","horizontal_pull","vertical_push","carry","scapular"],
}

V7_POSITION_FOCUS = {
    "Goalkeeper":["unilateral_lower","knee_dominant","scapular","carry"],
    "Center Back":["hip_dominant","knee_dominant","horizontal_push","horizontal_pull"],
    "Full Back":["unilateral_lower","hip_dominant","calf_ankle"],
    "Midfielder":["unilateral_lower","hip_dominant","calf_ankle","core"],
    "Winger":["unilateral_lower","hip_dominant","calf_ankle","core"],
    "Striker":["hip_dominant","unilateral_lower","knee_dominant","core"],
    "Guard":["unilateral_lower","knee_dominant","horizontal_pull","calf_ankle"],
    "Wing":["unilateral_lower","hip_dominant","horizontal_push"],
    "Forward":["knee_dominant","hip_dominant","horizontal_push","horizontal_pull"],
    "Center":["knee_dominant","hip_dominant","horizontal_push","horizontal_pull","carry"],
    "Setter":["unilateral_lower","scapular","vertical_push","core"],
    "Outside Hitter":["knee_dominant","unilateral_lower","scapular","vertical_push"],
    "Opposite":["knee_dominant","hip_dominant","vertical_push"],
    "Middle Blocker":["knee_dominant","calf_ankle","hip_dominant"],
    "Libero":["unilateral_lower","scapular","core"],
    "Wing":["unilateral_lower","calf_ankle","hip_dominant"],
    "Backcourt":["rotation","horizontal_push","horizontal_pull","unilateral_lower"],
    "Pivot":["knee_dominant","hip_dominant","horizontal_push","carry"],
    "Freestyle":["vertical_pull","horizontal_pull","scapular","core"],
    "Backstroke":["vertical_pull","scapular","core"],
    "Breaststroke":["unilateral_lower","knee_dominant","hip_dominant","core"],
    "Butterfly":["vertical_pull","scapular","hip_dominant","core"],
    "Individual Medley":["vertical_pull","horizontal_pull","scapular","unilateral_lower"],
    "Kumite":["unilateral_lower","calf_ankle","rotation","anti_rotation"],
    "Kata":["unilateral_lower","scapular","core","rotation"],
}

V7_GOAL_FOCUS = {
    "Max Strength":["knee_dominant","hip_dominant","horizontal_push","horizontal_pull","vertical_push","vertical_pull"],
    "Strength":["knee_dominant","hip_dominant","horizontal_push","horizontal_pull","unilateral_lower","vertical_push","vertical_pull"],
    "Hypertrophy":["knee_dominant","hip_dominant","horizontal_push","horizontal_pull","vertical_push","vertical_pull","calf_ankle"],
    "Power":["hip_dominant","knee_dominant","unilateral_lower","rotation","horizontal_push"],
    "Speed":["hip_dominant","unilateral_lower","knee_dominant","calf_ankle","core"],
    "Agility":["unilateral_lower","hip_dominant","calf_ankle","anti_rotation","core"],
    "Sport Performance":["unilateral_lower","hip_dominant","horizontal_pull","scapular","core","rotation"],
    "Endurance":["unilateral_lower","hip_dominant","horizontal_pull","core","calf_ankle"],
    "Fat Loss":["knee_dominant","hip_dominant","horizontal_push","horizontal_pull","unilateral_lower","carry"],
    "General Fitness":["knee_dominant","hip_dominant","horizontal_push","horizontal_pull","vertical_push","vertical_pull","carry"],
    "Overall Development":["knee_dominant","hip_dominant","horizontal_push","horizontal_pull","vertical_push","vertical_pull","unilateral_lower"],
}

V7_SECONDARY_FOCUS = {
    "Strength":["knee_dominant","hip_dominant","horizontal_push","horizontal_pull"],
    "Max Strength":["knee_dominant","hip_dominant","horizontal_push","horizontal_pull"],
    "Hypertrophy":["horizontal_push","horizontal_pull","vertical_push","vertical_pull"],
    "Power":["hip_dominant","rotation","unilateral_lower"],
    "Speed":["unilateral_lower","hip_dominant","calf_ankle"],
    "Agility":["unilateral_lower","anti_rotation","calf_ankle"],
    "Core / Trunk":["core","anti_rotation","contralateral"],
    "Stability":["scapular","anti_rotation","unilateral_lower"],
    "Plyometric Ability":["unilateral_lower","calf_ankle"],
    "Movement Quality":["unilateral_lower","scapular","anti_rotation"],
    "Body Composition":["knee_dominant","hip_dominant","horizontal_push","horizontal_pull"],
}

V7_SYSTEM_BY_FAMILY = {
    "knee_dominant":"Resistance","hip_dominant":"Resistance","horizontal_push":"Resistance","vertical_push":"Resistance",
    "vertical_pull":"Resistance","horizontal_pull":"Resistance","calf_ankle":"Resistance","scapular":"Resistance",
    "rotation":"Resistance","anti_rotation":"Resistance","unilateral_lower":"Resistance","contralateral":"Resistance",
    "carry":"Resistance","core":"Resistance",
}

# Recompute movement metadata after adding the expanded library.
AIQ62_META = {eid:aiq62_movement_meta(x) for eid,x in EXERCISES.items()}

# ---------------------------
# Hard sport-lock logic
# ---------------------------
V7_SPORT_LOCKED_TERMS = [
    "shadow boxing", "boxing reaction", "shadow kumite", "punch throw", "sport conditioning",
    "swim-pull", "swimmer", "streamline", "split step", "tennis", "racket", "soccer ball",
    "dribble", "volleyball approach", "block hop", "handball throw", "rugby sled"
]

def v7_is_sport_locked(x):
    n=x.name.lower()
    return any(t in n for t in V7_SPORT_LOCKED_TERMS)

def v7_sport_ok(x,a):
    if v7_is_sport_locked(x):
        return exercise_sport_compatible(x,a)
    return True

# ---------------------------
# Goal-specific dosing
# ---------------------------
def v7_resistance_dose(a, week, slot):
    phase=phase_for(a,week)
    goal=a.primary_goal
    if goal=="Max Strength": return {"sets": 3 if week==4 else 4+(1 if week==3 else 0), "reps": 3 if week==3 else 4 if week in [1,2] else 5, "rpe": 8.5 if week==3 else 7.5 if week==2 else 7.0 if week==1 else 6.0, "rest":"2-4 min", "tempo":"2-0-X-0"}
    if goal=="Strength": return {"sets": 3 if week==4 else 4, "reps": 6 if week==1 else 5 if week==2 else 4 if week==3 else 6, "rpe": 7.0 if week==1 else 7.5 if week==2 else 8.0 if week==3 else 6.0, "rest":"2-3 min", "tempo":"2-0-1-0"}
    if goal=="Hypertrophy": return {"sets": 2 if week==4 else 3 if week==1 else 4, "reps": 10 if week in [1,4] else 8, "rpe": 7.0 if week==1 else 8.0 if week in [2,3] else 6.0, "rest":"60-120 s", "tempo":"3-1-1-0"}
    if goal in ["Power","Speed"]: return {"sets": 2 if week==4 else 3, "reps": 4 if week==1 else 3 if week in [2,3] else 3, "rpe": 6.5 if week==1 else 7.0 if week in [2,3] else 6.0, "rest":"2-3 min", "tempo":"X-0-X-0"}
    if goal in ["Agility","Sport Performance"]: return {"sets": 2 if week==4 else 3, "reps": 6 if week==1 else 5 if week==2 else 4 if week==3 else 5, "rpe": 6.5 if week==1 else 7.0 if week in [2,3] else 6.0, "rest":"90-150 s", "tempo":"2-0-X-0"}
    if goal=="Endurance": return {"sets": 2 if week==4 else 3, "reps": 10 if week in [1,2] else 12 if week==3 else 8, "rpe": 6.5 if week==1 else 7.0 if week in [2,3] else 6.0, "rest":"60-90 s", "tempo":"2-0-1-0"}
    if goal=="Fat Loss": return {"sets": 2 if week==4 else 3, "reps": 10 if week in [1,4] else 12, "rpe": 7.0 if week in [1,2] else 7.5 if week==3 else 6.0, "rest":"45-90 s", "tempo":"2-0-1-0"}
    return {"sets": 2 if week==4 else 3, "reps": 8 if week in [1,4] else 10, "rpe": 7.0 if week in [1,2] else 7.5 if week==3 else 6.0, "rest":"60-120 s", "tempo":"2-0-1-0"}

# ---------------------------
# Resistance selector: sport + position + goal + phase + coverage + equipment
# ---------------------------
def v7_score_resistance(x,a,week,month,used,coverage):
    if x.system!="Resistance" or not aiq62_equipment_ok(x,a) or not v7_sport_ok(x,a) or not aiq62_level_ok(x,a): return -999
    constraints=constraint_engine(a)
    if not aiq62_exercise_allowed(x,a,constraints): return -999
    fam=V7_FAMILY.get(x.id, v7_family(x))
    sport_focus=V7_SPORT_FOCUS.get(a.sport,V7_SPORT_FOCUS["General Fitness"])
    goal_focus=V7_GOAL_FOCUS.get(a.primary_goal,V7_GOAL_FOCUS["Overall Development"])
    position_focus=[]
    for pos in athlete_position_labels(a): position_focus += V7_POSITION_FOCUS.get(pos,[])
    score=0.0
    # Hard architecture: goal and sport both matter.
    if fam in goal_focus: score += 45 - goal_focus.index(fam)*3
    if fam in sport_focus: score += 38 - sport_focus.index(fam)*3
    if fam in position_focus: score += 28
    for g in a.secondary_goals:
        focus=V7_SECONDARY_FOCUS.get(g,[])
        if fam in focus: score += 12
    # Movement coverage prevents a program from becoming row + split squat only.
    if fam not in coverage: score += 35
    else: score -= 12
    # Deliberate monthly variation: months are phases, not shuffled copies.
    month_phase={1:"foundation",2:"development",3:"performance",4:"realization",5:"performance",6:"maintenance"}.get(month,"development")
    if month_phase=="foundation":
        if x.level=="Beginner": score+=6
        if x.fatigue<=3: score+=4
    elif month_phase=="development":
        if x.level in ["Intermediate","Advanced"]: score+=8
        if x.fatigue>=2: score+=3
    elif month_phase in ["performance","realization"]:
        if any(k in " ".join(x.quality).lower() for k in ["strength","power","stability"]): score+=6
    elif month_phase=="maintenance":
        if x.fatigue<=3: score+=6
    # Week progression changes dose and slightly favors stable variants early.
    if week==1 and x.level=="Beginner": score+=3
    if week==3 and x.fatigue>=3: score+=4
    if week==4 and x.fatigue>=4: score-=6
    # Sport-specific tagged resistance is a preference, not a lock.
    if a.sport in x.sport_tags: score+=12
    # Avoid repeating the exact same exercise within the recent generated plan.
    if x.id in used: score-=100
    # Strongly discourage the same exercise family being the only family selected.
    if len(coverage)>=3 and fam in coverage: score-=8
    return score

def v7_pick_resistance(a,week,month,n,used,coverage):
    candidates=[]
    for x in EXERCISES.values():
        s=v7_score_resistance(x,a,week,month,used,coverage)
        if s>-900: candidates.append((s,x))
    candidates.sort(key=lambda z:(z[0], -z[1].fatigue, z[1].id), reverse=True)
    picked=[]
    local=set(used)
    # Pick different families whenever possible.
    for _,x in candidates:
        fam=V7_FAMILY[x.id]
        if x.id in local: continue
        if picked and fam in {V7_FAMILY[y.id] for y in picked} and len(candidates)>n*2: continue
        picked.append(x); local.add(x.id)
        if len(picked)>=n: break
    return picked

# ---------------------------
# Goal-specific session architecture
# ---------------------------
def session_template(a,day,system_scores,constraints):
    if constraints.get("low_impact"):
        return ["Corrective / Activation","Mobility","Resistance","Neuromuscular Coordination","Aerobic"]
    g=a.primary_goal
    templates={
        "Max Strength":["Corrective / Activation","Resistance","Resistance","Neuromuscular Coordination","Aerobic"],
        "Strength":["Corrective / Activation","Resistance","Resistance","Neuromuscular Coordination","Anaerobic / Repeated Sprint"],
        "Hypertrophy":["Corrective / Activation","Resistance","Resistance","Resistance","Aerobic"],
        "Power":["Corrective / Activation","Plyometrics","Resistance","Neuromuscular Coordination","Acceleration / Speed"],
        "Speed":["Corrective / Activation","Acceleration / Speed","Plyometrics","Resistance","Neuromuscular Coordination"],
        "Agility":["Corrective / Activation","Agility / COD","Neuromuscular Coordination","Resistance","Anaerobic / Repeated Sprint"],
        "Endurance":["Corrective / Activation","Aerobic","Resistance","Neuromuscular Coordination","Anaerobic / Repeated Sprint"],
        "Sport Performance":["Corrective / Activation","Plyometrics","Resistance","Neuromuscular Coordination","Agility / COD"],
        "Fat Loss":["Corrective / Activation","Resistance","Aerobic","Neuromuscular Coordination","Anaerobic / Repeated Sprint"],
        "General Fitness":["Corrective / Activation","Resistance","Neuromuscular Coordination","Resistance","Aerobic"],
        "Overall Development":["Corrective / Activation","Resistance","Neuromuscular Coordination","Plyometrics","Aerobic"],
    }
    base=list(templates.get(g,templates["Overall Development"]))
    # Day emphasis changes without breaking the goal architecture.
    if day%3==2:
        if g in ["Strength","Max Strength","Hypertrophy"]: base[2]="Resistance"
        if g in ["Power","Speed","Sport Performance"]: base[4]="Agility / COD"
    if day%3==0:
        if g in ["Strength","Max Strength","Hypertrophy"]: base[4]="Resistance"
        if g in ["Agility","Sport Performance"]: base[1]="Neuromuscular Coordination"
    return base

# ---------------------------
# Improved neuromuscular selection
# ---------------------------
def v7_select_neuromuscular(a,week,month,used):
    pool=[]
    for x in EXERCISES.values():
        if x.id in used or not aiq62_equipment_ok(x,a) or not aiq62_level_ok(x,a): continue
        if x.system not in ["Agility / COD","Plyometrics","Stability / Core","Corrective / Activation"]: continue
        if not v7_sport_ok(x,a): continue
        m=AIQ62_META.get(x.id,{})
        score=0
        if m.get("neuromuscular"): score+=35
        if m.get("unilateral"): score+=10
        if m.get("contralateral"): score+=14
        if m.get("ipsilateral"): score+=10
        if a.primary_goal in ["Agility","Sport Performance"]: score+=18
        if a.sport in x.sport_tags: score+=12
        if month==2 and m.get("contralateral"): score+=8
        if month>=3 and (m.get("neuromuscular") or m.get("plane")=="Frontal"): score+=8
        score-=x.fatigue
        pool.append((score,x))
    pool.sort(key=lambda z:(z[0],z[1].id),reverse=True)
    return pool[0][1] if pool else None

# ---------------------------
# Periodized exercise rotation
# ---------------------------
def build_rotation(a,months,p,system_scores,constraints):
    rotation={}
    used_global=set()
    for month in range(1,months+1):
        rotation[month]={}
        # Keep the map useful for the UI but use the new selector.
        for system in AIQ62_SYSTEMS:
            if system=="Resistance":
                picks=v7_pick_resistance(a,1,month,3,list(used_global),set())
                if picks:
                    rotation[month][system]=picks[0].id
                    used_global.add(picks[0].id)
            elif system=="Neuromuscular Coordination":
                x=v7_select_neuromuscular(a,1,month,list(used_global))
                if x:
                    rotation[month][system]=x.id
                    used_global.add(x.id)
            else:
                picks=aiq62_select_exercises(a,p,system_scores,system,3,month,list(used_global),constraints,set())
                if picks:
                    rotation[month][system]=picks[0].id
                    used_global.add(picks[0].id)
    return rotation

def _aiq62_coverage_add(coverage,x):
    fam=V7_FAMILY.get(x.id,v7_family(x))
    coverage.add(fam)
    m=AIQ62_META.get(x.id,{})
    for k in ["unilateral","bilateral","contralateral","ipsilateral"]:
        if m.get(k): coverage.add(k)
    coverage.add(m.get("plane","General"))

# ---------------------------
# Resistance display / dose
# ---------------------------
def v7_render_resistance_dose(a,week,slot):
    d=v7_resistance_dose(a,week,slot)
    return f"{d['sets']} sets x {d['reps']} reps | RPE {d['rpe']} | Rest {d['rest']} | Tempo {d['tempo']}"

def build_session(a,week,day,month,rotation,p,system_scores,constraints,history=None):
    systems=session_template(a,day,system_scores,constraints)
    # Recent exercise history is a hard diversity constraint for selection.
    # This prevents the same corrective/resistance drill from occupying every
    # week while still allowing reintroduction after a sufficient gap.
    used=list(history or [])[-48:]
    exercises=[]; coverage=set()
    for system in systems:
        if system=="Resistance":
            # Every resistance slot is coverage-driven and sport/goal weighted.
            picks=v7_pick_resistance(a,week,month,2,used,coverage)
        elif system=="Neuromuscular Coordination":
            x=v7_select_neuromuscular(a,week,month,used)
            picks=[x] if x else []
        else:
            picks=aiq62_select_exercises(a,p,system_scores,system,1,month,used,constraints,coverage)
        for x in picks:
            if x and x.id not in used:
                used.append(x.id); exercises.append(x); _aiq62_coverage_add(coverage,x)
    cond=conditioning_decision(a,p,constraints,week,month,day)
    complex_block=None
    if day==1 and constraints.get("high_impact_allowed") and constraints.get("high_fatigue_allowed"):
        complex_block=choose_complex(a,p,systems,constraints,month)
    return {"day":day,"week":week,"month":month,"phase":phase_for(a,week),"mesocycle_phase":mesocycle_phase(a,month),"systems":systems,"exercises":exercises,"conditioning":cond,"complex":complex_block,"readiness":constraints["readiness"],"movement_coverage":sorted(coverage)}

# ---------------------------
# Meaningful periodization of MetCon / ESD
# ---------------------------
V7_PROTOCOLS = {
    "Strength":["Intervals","Every 90s","Circuit","Intervals"],
    "Max Strength":["Intervals","Every 90s","Circuit","Intervals"],
    "Hypertrophy":["Circuit","AMRAP","Intervals","Circuit"],
    "Power":["Intervals","Every 90s","Circuit","Intervals"],
    "Speed":["Intervals","Every 90s","Tabata","Intervals"],
    "Agility":["Intervals","EMOM","AMRAP","Intervals"],
    "Sport Performance":["Intervals","Every 90s","AMRAP","Intervals"],
    "Endurance":["Intervals","AMRAP","Ladder","Intervals"],
    "Fat Loss":["AMRAP","Circuit","Tabata","Intervals"],
    "General Fitness":["Circuit","EMOM","AMRAP","Intervals"],
    "Overall Development":["EMOM","Intervals","AMRAP","Intervals"],
}

def v7_equipment_token_ok(a,station):
    s=station.lower()
    if any(k in s for k in ["sled", "prowler"]) and "Sleds & Prowler" not in a.equipment: return False
    if any(k in s for k in ["barbell", "landmine"]) and "Barbells & Plates" not in a.equipment: return False
    if any(k in s for k in ["db ","dumbbell"]) and "Dumbbells" not in a.equipment: return False
    if any(k in s for k in ["kettlebell", " kb "]) and "Kettlebells" not in a.equipment: return False
    if any(k in s for k in ["medicine-ball", "med-ball", "wall ball"]) and "Medicine & Slam Balls" not in a.equipment: return False
    if any(k in s for k in ["bike", "rower", "skierg", "ski erg"]) and "Ergometers (AirBike/Rower/SkiErg)" not in a.equipment: return False
    if any(k in s for k in ["cable"]) and "Cable Systems & Selectorized" not in a.equipment: return False
    if any(k in s for k in ["cone", "shuffle", "sprint", "shuttle", "reaction", "footwork", "cod"]) and "Cones / Timing Gates" not in a.equipment and "Bodyweight" not in a.equipment:
        # Locomotion can be bodyweight, but reactive cone work specifically needs cones.
        if "cone" in s: return False
    return True

def v7_sport_metcon_pool(a,month):
    sport=a.sport
    pos=a.position
    if sport=="Soccer":
        pools={
            1:["5-10 m Acceleration - 3 reps","Lateral Shuffle to Sprint - 20 s","Tempo Shuttle - 30 s","DB Reverse Lunge - 8/side"],
            2:["Deceleration to Re-acceleration - 3 reps","Crossover to Sprint - 2/side","Repeated Sprint - 15 s","DB Romanian Deadlift - 8 reps"],
            3:["Curved Acceleration - 2/side","Reactive Direction Change - 15 s","Lateral Bound - 4/side","DB Step-Up - 8/side"],
        }
        if pos=="Goalkeeper": pools[1]=["Lateral Reaction Shuffle - 15 s","Reactive Direction Change - 15 s","Low Box Jump - 4 reps","DB Split Squat - 8/side"]
        if pos=="Winger": pools[2]=["Curved Acceleration - 2/side","Crossover to Sprint - 2/side","Repeated Sprint - 15 s","DB RDL - 8 reps"]
        return pools.get(min(month,3),pools[3])
    if sport=="Swimming":
        return {
            1:["Swim-Pull Ergometer - 30 s","Swimmer Hollow-Body Hold - 30 s","Prone Y-T-W - 6/position","DB Romanian Deadlift - 8 reps"],
            2:["DB Pullover - 10 reps","Dead Bug - 30 s","One-Arm Dumbbell Row - 8/side","Fast March - 30 s"],
            3:["Straight-Arm Cable Pulldown - 10 reps","Bird Dog - 8/side","DB Bench Press - 8 reps","Tempo Shuttle - 20 s"],
        }[min(month,3)]
    if sport in ["Boxing","MMA"]:
        return {
            1:["Shadow Boxing - 30 s","Reactive Footwork - 20 s","DB Reverse Lunge - 8/side","DB Push Press - 6 reps"],
            2:["Visual Reaction Boxing - 20 s","Sprawl to Stand - 5 reps","DB Bench Press - 8 reps","Suitcase Carry - 20 m"],
            3:["Reaction Callout - 20 s","Split-Stance Footwork - 20 s","DB Romanian Deadlift - 8 reps","Push-Up - 10 reps"],
        }[min(month,3)]
    if sport in ["Tennis","Racket Sports (Squash/Padel)"]:
        return {
            1:["Split Step to Reactive Lateral Shuffle - 15 s","Crossover to 5 m Acceleration - 2/side","DB Split Squat - 8/side","Rotational DB Press - 6/side"],
            2:["Visual Reaction COD - 15 s","Lateral Bound to Stick - 4/side","DB RDL - 8 reps","One-Arm Dumbbell Row - 8/side"],
            3:["Open-Stance COD - 3/side","Reactive Shuffle - 15 s","Suitcase Carry - 20 m","DB Step-Up - 8/side"],
        }[min(month,3)]
    if sport=="Karate":
        return {
            1:["Karate Reaction Callout - 20 s","Split-Stance Punch to Lateral Exit - 20 s","DB Reverse Lunge - 8/side","Rotational Medicine-Ball Scoop Toss - 5/side"],
            2:["Shadow Kumite - 30 s","Reactive Footwork - 20 s","DB RDL - 8 reps","Suitcase Carry - 20 m"],
            3:["Strike-Check-Exit Reaction - 20 s","Lateral Bound to Stick - 4/side","DB Step-Up - 8/side","Cable Rotation - 8/side"],
        }[min(month,3)]
    if sport=="Volleyball":
        return {
            1:["Approach Jump - 4 reps","Lateral Shuffle - 20 s","DB Split Squat - 8/side","DB Row - 8/side"],
            2:["Block Hop - 4 reps","Reactive Cone Drill - 15 s","DB RDL - 8 reps","DB Shoulder Press - 8 reps"],
            3:["Repeated Jump - 5 reps","Lateral Bound to Stick - 4/side","DB Step-Up - 8/side","Cable Row - 8 reps"],
        }[min(month,3)]
    return {
        1:["Fast March / Low-Impact Run - 30 s","DB Goblet Squat - 8 reps","Push-Up - 10 reps","One-Arm Dumbbell Row - 8/side"],
        2:["Tempo Shuttle - 30 s","DB Reverse Lunge - 8/side","DB Bench Press - 8 reps","Dead Bug - 30 s"],
        3:["Lateral Shuffle - 20 s","DB RDL - 8 reps","DB Shoulder Press - 8 reps","Suitcase Carry - 20 m"],
    }[min(month,3)]

def conditioning_decision(a,p,constraints,week,month=1,day=1):
    protocols=V7_PROTOCOLS.get(a.primary_goal,V7_PROTOCOLS["Overall Development"])
    protocol=protocols[min(month-1,len(protocols)-1)]
    # Week 4 is deload, not another high-fatigue stimulus.
    if week==4: protocol="Intervals"
    if constraints.get("low_impact"): protocol="Intervals"
    loadmod=adaptive_load_modifier(a)
    base={1:3,2:4,3:4,4:2}[week]
    rounds=max(2,int(round(base*loadmod)))
    target=6.5 if constraints["band"] in ["GREEN","BLUE"] else 6.0 if constraints["band"]=="YELLOW" else 5.5
    target += 0.5 if month==2 and week in [2,3] else 0.0
    stations=[s for s in v7_sport_metcon_pool(a,month) if v7_equipment_token_ok(a,s)]
    if not stations: stations=["Bodyweight March / Footwork - 30 s"]
    if protocol=="EMOM": work=f"EMOM {max(8,rounds*len(stations))} min - 1 station/min"; rest="Remaining time in minute"
    elif protocol=="AMRAP": work=f"AMRAP {8 if week==1 else 10 if week in [2,3] else 6} min - repeat stations"; rest="Self-regulated transitions"
    elif protocol=="Tabata": work=f"Tabata {rounds} blocks - 20 s work / 10 s transition"; rest="60-90 s between blocks"
    elif protocol=="Every 90s": work=f"Every 90 s x {rounds*len(stations)} station exposures"; rest="Remaining time in each 90-s window"
    elif protocol=="Circuit": work=f"Circuit {rounds} rounds - 30-40 s work / 20 s transition"; rest="90 s between rounds"
    else: work=f"Intervals {rounds} rounds - 30 s work / 30 s recovery"; rest="60-90 s between rounds"
    return {"system":"Anaerobic / Repeated Sprint" if protocol in ["Tabata","EMOM","AMRAP","Circuit","Every 90s"] else "Aerobic","name":f"{a.sport} | {a.position} | {protocol} | Month {month}","protocol":protocol,"stations":stations,"work":work,"rest":rest,"intensity":f"Target RPE {target:.1f} | Load modifier x{loadmod:.2f}","reason":"Sport + position + primary goal + phase + readiness + equipment + monthly stimulus."}

def build_program(a,months):
    constraints=constraint_engine(a)
    p=priorities(a)
    systems=system_allocation(a,p,constraints)
    rotation=build_rotation(a,months,p,systems,constraints)
    days=max(1,min(a.gym_days_available,4))
    program={}
    history=[]
    for m in range(1,months+1):
        program[m]={}
        for w in range(1,5):
            program[m][w]=[]
            for d in range(1,days+1):
                session=build_session(a,w,d,m,rotation,p,systems,constraints,history)
                program[m][w].append(session)
                history.extend([x.id for x in session.get("exercises",[])])
                if session.get("complex"):
                    history.extend([eid for eid in session["complex"].exercises if eid in EXERCISES])
                history=history[-48:]
    return program,{"constraints":constraints,"priorities":p,"systems":systems,"rotation":rotation,"load_status":constraints.get("load_status"),"movement_engine":V7_VERSION,"coverage":"full-body resistance + sport/position + goal + unilateral/bilateral/ipsilateral/contralateral + neuromuscular coordination + recent-history diversity"}

# ASCII-safe UI text helpers. All generated prescriptions use ASCII punctuation.
def v7_ascii_safe_text(s):
    return str(s).replace("x","x").replace("->","->").replace("|","|").replace("-","-").replace("-","-").replace("(c)","(c)").replace("(tm)","(tm)")



# ============================================================
# V11 SCREENING SCORE LAYER
# ============================================================
def _mean(values, default=75.0):
    vals=[float(v) for v in values if v is not None]
    return sum(vals)/len(vals) if vals else default

def stability_index(a):
    t=a.stability_tests or {}
    stance=min(100.0, _mean([t.get("Single-Leg Stance L",30),t.get("Single-Leg Stance R",30)])/30*100)
    yvals=[t.get(k,70) for k in ["Y Balance ANT L","Y Balance ANT R"]]
    yvals += [t.get(k,100) for k in ["Y Balance PM L","Y Balance PM R","Y Balance PL L","Y Balance PL R"]]
    y=_mean(yvals)
    control=_mean([t.get("Landing Control",80),t.get("Trunk Stability",80),t.get("Single-Leg Squat Control L",80),t.get("Single-Leg Squat Control R",80)])
    return round(max(0,min(100,0.30*stance+0.30*y+0.40*control)),1)

def neuromuscular_index(a):
    t=a.neuromuscular_tests or {}
    reaction=max(0,min(100,(1.50-max(0.25,float(t.get("Reaction Time",0.75)))/1.25)*100))
    return round(max(0,min(100,0.22*reaction+0.20*_mean([t.get("Proprioception L",80),t.get("Proprioception R",80)])+0.25*t.get("Reactive Balance",80)+0.20*_mean([t.get("Coordination L",80),t.get("Coordination R",80)])+0.13*t.get("Dual Task",80))),1)

def fms_index(a):
    vals=list((a.fms_scores or {}).values())
    return round(_mean(vals,2)*25,1)

def sfma_index(a):
    vals=list((a.sfma_results or {}).values())
    if not vals: return 75.0
    weights={"FN - Functional / Non-painful":100,"FP - Functional / Painful":45,"DN - Dysfunctional / Non-painful":55,"DP - Dysfunctional / Painful":25,"Not assessed":75}
    return round(_mean([weights.get(v,75) for v in vals]),1)

def mobility_index(a):
    rom=a.mobility_rom or {}
    if not rom: return 75.0
    # Relative symmetry signal; values are interpreted as coach-recorded ROM, not diagnosis.
    diffs=[]
    for pair in rom.values():
        if isinstance(pair,dict) and "L" in pair and "R" in pair:
            diffs.append(max(0,100-abs(float(pair["L"])-float(pair["R"]))*5))
    base=_mean(diffs,75)
    return round(base,1)



def smart_warmup(a,session):
    """Low-fatigue warm-up built from today's actual movement demands plus screening."""
    systems=set(session.get("systems",[]))
    names=[x.name.lower() for x in session.get("exercises",[])]
    out=[]
    def add(x):
        if x not in out: out.append(x)
    add("Raise: easy cyclical movement 3-5 min")
    if "Resistance" in systems:
        if any(k in " ".join(names) for k in ["squat","split squat","lunge","step-up"]): add("Dynamic lower-body prep: squat/lunge pattern 1-2 sets")
        if any(k in " ".join(names) for k in ["deadlift","rdl","hinge","hip thrust"]): add("Hip hinge prep + glute activation 1-2 sets")
        if any(k in " ".join(names) for k in ["press","push","bench"]): add("Scapular push + light press pattern 1-2 sets")
        if any(k in " ".join(names) for k in ["row","pull","pulldown"]): add("Band row / pull-apart preparation 1-2 sets")
    if "Plyometrics" in systems or "Acceleration / Speed" in systems:
        add("Potentiation: low-amplitude pogo / build-up 2-3 exposures")
    if "Agility / COD" in systems:
        add("Progressive lateral shuffle and deceleration 2-3 quality reps/side")
    if "Neuromuscular Coordination" in systems:
        add("Coordination primer: balance + reaction 2-3 low-fatigue exposures")
    if "Mobility" in systems:
        add("Dynamic mobility for the joints used today, not static fatigue work")
    if any("pelvic" in k.lower() or "hip" in str(v).lower() for d in [a.posture_anterior,a.posture_lateral,a.posture_posterior] for k,v in d.items()):
        add("Screening-informed hip/trunk preparation 1-2 controlled sets")
    if any("scapular" in k.lower() or "shoulder" in str(v).lower() for d in [a.posture_anterior,a.posture_lateral,a.posture_posterior] for k,v in d.items()):
        add("Screening-informed scapular/shoulder preparation 1-2 controlled sets")
    return out[:7]

def render_session(a,session,week,engine):
    c=engine["constraints"]
    warm=smart_warmup(a,session)
    render_card("1. Smart Warm-up","Session-specific preparation","Low fatigue | 5-12 min","Prepare, do not exhaust","Progressive","Multi-planar","RAMP-style preparation",ACCENTS["Corrective / Activation"])
    for item in warm: st.markdown(f"- {item}")
    for i,x in enumerate(session["exercises"]):
        render_exercise(a,x,week,c,"primary" if i<2 else "secondary")
    if session.get("complex"):
        cx=session["complex"]; rounds,reps,between,round_rest=complex_dose(cx,a,week,c)
        st.markdown("#### Complex / Compound Athletic Block")
        names=[EXERCISES[eid].name for eid in cx.exercises if eid in EXERCISES]
        render_card(cx.method,cx.name,f"{rounds} rounds | {reps}",f"Rest {round_rest}",f"{between} between exercises","Multi-planar","Advanced / Athletic",ACCENTS.get("Plyometrics","#ec4899"))
        st.caption(" -> ".join(names))
        if cx.notes: st.caption(cx.notes)
    cond=session["conditioning"]
    st.markdown("#### MetCon / ESD")
    render_card("Metabolic Conditioning",cond["name"],cond["work"]+" | Rest: "+cond["rest"],cond["intensity"],cond["protocol"],"Multi-planar","Energy System / Conditioning",ACCENTS["Aerobic"])
    for i,station in enumerate(cond["stations"],1): st.markdown(f"**{i}.** {station}")
    st.caption(cond["reason"])

# ============================================================
# ATHLETE-IQ V11 UI - CLOSED LOOP, GROUPED PAGES
# ============================================================
# Plain ASCII labels are used deliberately to prevent mojibake in GitHub/Streamlit.
PAGES=[
    "1. Athlete Profile",
    "2. Sport / Position Context",
    "3. Health / History",
    "4. Movement Screening",
    "5. Stability / Neuromuscular",
    "6. Performance",
    "7. Asymmetry",
    "8. Programming Priorities",
    "9. Club Load",
    "10. Equipment",
    "11. Training Program",
    "12. Feedback / Data",
]

st.sidebar.markdown("## ATHLETE-IQ")
st.sidebar.markdown("**By: Coach Ahmed Youssef**")
st.sidebar.caption("Closed-loop whole-athlete programming. Every upstream change is propagated to the plan.")
if "page" not in st.session_state: st.session_state.page=PAGES[0]
st.session_state.page=st.sidebar.radio("Jump to page",PAGES,index=PAGES.index(st.session_state.page))
plan_months=st.sidebar.select_slider("Macrocycle Horizon",options=[1,2,3,4,5,6],value=3,format_func=lambda x:f"{x}-Month Block")

st.markdown("<h1 style='text-align:center;color:#38bdf8;font-weight:900;margin-bottom:0'>ATHLETE-IQ</h1>",unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#a855f7;font-weight:800;font-size:1.05rem'>By: Coach Ahmed Youssef</p>",unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#94a3b8'>Closed-Loop Whole-Athlete Adaptive Programming Engine</p>",unsafe_allow_html=True)

# ------------------------------------------------------------
# Automatic generation: no Generate button.
# The final regeneration happens after page inputs are processed.
# ------------------------------------------------------------
page=st.session_state.page

if page=="1. Athlete Profile":
    st.markdown('<div class="banner-header">01 | Athlete Profile</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:
        setv("name",st.text_input("Athlete Name",st.session_state.name))
        setv("age",st.number_input("Age",12,80,int(st.session_state.age),1))
        setv("sex",st.selectbox("Sex",["Male","Female","Other"],index=["Male","Female","Other"].index(st.session_state.sex)))
    with c2:
        setv("height_cm",st.number_input("Height (cm)",120.0,230.0,float(st.session_state.height_cm),0.5))
        setv("weight_kg",st.number_input("Weight (kg)",30.0,250.0,float(st.session_state.weight_kg),0.5))
        setv("training_years",st.number_input("S&C Experience (years)",0.0,30.0,float(st.session_state.training_years),0.5))
    with c3:
        setv("gym_days_available",st.slider("Gym Days / Week",1,7,int(st.session_state.gym_days_available)))
        setv("session_minutes",st.slider("Session Duration (min)",30,150,int(st.session_state.session_minutes),5))
        setv("notes",st.text_area("Coach Notes",st.session_state.notes,height=100))
    a=athlete(); x,y,z=st.columns(3); x.metric("Training Level",training_level(a.training_years)); y.metric("BMI",f"{bmi(a):.1f}"); z.metric("Plan Status","Auto-generated")

elif page=="2. Sport / Position Context":
    st.markdown('<div class="banner-header">02 | Sport / Position Context</div>',unsafe_allow_html=True)
    sports=list(SPORT_DEMANDS)
    sport=st.selectbox("Sport / Discipline",sports,index=sports.index(st.session_state.sport)); setv("sport",sport)
    pos=SPORT_POSITIONS[sport]
    position=st.selectbox("Primary Position / Event",pos,index=pos.index(st.session_state.position) if st.session_state.position in pos else 0); setv("position",position)
    secondary_options=[x for x in pos if x!=position]
    setv("secondary_positions",st.multiselect("Secondary Positions / Events",secondary_options,default=[x for x in st.session_state.secondary_positions if x in secondary_options]))
    c1,c2=st.columns(2)
    with c1: setv("primary_goal",st.selectbox("Primary Goal",GOALS,index=GOALS.index(st.session_state.primary_goal)))
    with c2: setv("secondary_goals",st.multiselect("Secondary Development Targets",SECONDARY_OPTIONS,default=[x for x in st.session_state.secondary_goals if x in SECONDARY_OPTIONS]))
    setv("season",st.selectbox("Season / Calendar Phase",SEASONS,index=SEASONS.index(st.session_state.season)))
    st.info("Primary goal sets the main emphasis. Secondary goals, sport/position demands, screening findings and current strengths remain active rather than being discarded.")

elif page=="3. Health / History":
    st.markdown('<div class="banner-header">03 | Health / History / Readiness</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:
        setv("pain_present",st.checkbox("Pain currently present",bool(st.session_state.pain_present)))
        setv("pain_score",st.slider("Pain score (0-10)",0,10,int(st.session_state.pain_score)))
        injury_opts=["Knee / ACL / MCL / Patellar","Hamstring","Ankle / Achilles","Shoulder / Rotator Cuff","Low Back","Groin / Adductor","Quadriceps","Wrist / Elbow","Other"]
        setv("injuries",st.multiselect("Current / recent injury history",injury_opts,default=[x for x in st.session_state.injuries if x in injury_opts]))
    with c2:
        setv("sleep_hours",st.slider("Sleep (hours)",3.0,12.0,float(st.session_state.sleep_hours),0.5))
        setv("readiness",st.slider("Subjective Readiness",0,100,int(st.session_state.readiness)))
        setv("stress",st.slider("Stress",0,10,int(st.session_state.stress)))
        setv("soreness",st.slider("Soreness",0,10,int(st.session_state.soreness)))
    with c3:
        setv("team_days",st.slider("Sport / Club Sessions per Week",0,14,int(st.session_state.team_days)))
        setv("team_minutes",st.number_input("Average Club Session Minutes",0,300,int(st.session_state.team_minutes),5))
        setv("weekly_sport_rpe",st.slider("Typical Sport Session RPE",1.0,10.0,float(st.session_state.weekly_sport_rpe),0.5))
    a=athlete(); c=constraint_engine(a); band,txt=readiness_band(c["readiness"])
    st.markdown(f'<div class="hud-card"><span class="small-label">Decision Gate</span><div class="big-value">{c["readiness"]:.0f}/100 | {band}</div><div>{txt}</div></div>',unsafe_allow_html=True)
    if c["pain_gate"]: st.error("Pain gate active: high-impact and high-fatigue choices are restricted.")

elif page=="4. Movement Screening":
    st.markdown('<div class="banner-header">04 | Movement Screening</div>',unsafe_allow_html=True)
    st.caption("Posture, FMS, SFMA and mobility are intentionally grouped on one page. Findings are coach-observation and screening data, not medical diagnoses.")
    tabs=st.tabs(["Posture - Anterior","Posture - Lateral","Posture - Posterior","FMS","SFMA","Mobility"])
    for tab,view in zip(tabs,["Anterior","Lateral","Posterior"]):
        with tab:
            st.subheader(f"{view} View - Complete Observation")
            st.caption("Record the observation, severity and coach note for each region. Use measurements where your protocol supports them.")
            current=dict(st.session_state.get("posture_"+view.lower(),{}))
            cols=st.columns(2)
            for i,item in enumerate(POSTURE_FIELDS[view]):
                with cols[i%2]:
                    legacy=current.get(item,"Not assessed")
                    old_f=legacy.split(" || ",1)[0] if isinstance(legacy,str) and " || " in legacy else "Not assessed"
                    old_s=legacy.split(" || ",1)[1] if isinstance(legacy,str) and " || " in legacy else "Not assessed"
                    opts=POSTURE_FINDINGS[view][item]
                    f=st.selectbox(f"{item} - Observation",opts,index=opts.index(old_f) if old_f in opts else 0,key=f"{view}_{i}_obs")
                    s=st.selectbox(f"{item} - Severity",POSTURE_SEVERITY,index=POSTURE_SEVERITY.index(old_s) if old_s in POSTURE_SEVERITY else 0,key=f"{view}_{i}_sev")
                    note=st.text_input(f"{item} - Coach note",key=f"{view}_{i}_note")
                    current[item]=f"{f} || {s} || {note}"
            setv("posture_"+view.lower(),current)
            st.text_area(f"{view} overall observation",key=f"{view}_overall_note",height=80)
    with tabs[3]:
        st.subheader("Functional Movement Screen")
        st.caption("Record the standardized FMS score for each applicable test. Left/right observations should be recorded separately where the test permits it.")
        fms_names=["Deep Squat","Hurdle Step","Inline Lunge","Shoulder Mobility","ASLR","Trunk Stability Push-Up","Rotary Stability"]
        fs=dict(st.session_state.fms_scores)
        cols=st.columns(2)
        fms_side_tests={"Hurdle Step","Inline Lunge","Shoulder Mobility","ASLR","Rotary Stability"}
        sides=dict(st.session_state.fms_sides)
        for i,n in enumerate(fms_names):
            with cols[i%2]: fs[n]=st.selectbox(f"{n} score",[0,1,2,3],index=int(fs.get(n,2)),key=f"fms_{i}")
            if n in fms_side_tests:
                sc=sides.setdefault(n,{"L":2,"R":2})
                cL,cR=st.columns(2)
                with cL: sc["L"]=st.selectbox(f"{n} Left",[0,1,2,3],index=int(sc.get("L",2)),key=f"fms_{i}_L")
                with cR: sc["R"]=st.selectbox(f"{n} Right",[0,1,2,3],index=int(sc.get("R",2)),key=f"fms_{i}_R")
        st.session_state.fms_scores=fs; st.session_state.fms_sides=sides
        st.metric("FMS Composite (descriptive)",f"{fms_index(athlete()):.1f}/100")
    with tabs[4]:
        st.subheader("Selective Functional Movement Assessment")
        st.caption("Coach instruction: use the standardized SFMA protocol, observe the full movement first, then classify the pattern. Do not use the dropdown as a substitute for the test itself.")
        sf=dict(st.session_state.sfma_results)
        instructions={
            "Cervical Flexion":"Stand tall; ask the athlete to flex the cervical spine without compensating through the trunk.",
            "Cervical Extension":"Stand tall; extend the cervical spine while observing pain and movement quality.",
            "Cervical Rotation":"Rotate left and right under the standardized protocol; compare sides.",
            "UE Pattern 1":"Perform the standardized upper-extremity pattern and observe mobility, pain and compensation.",
            "UE Pattern 2":"Perform the second standardized upper-extremity pattern and compare sides.",
            "Multi-Segmental Flexion":"Observe the complete chain from standing and record the official classification.",
            "Multi-Segmental Extension":"Observe spinal/hip contribution and compensations using the standardized protocol.",
            "Multi-Segmental Rotation":"Compare left and right rotation and note the limiting region.",
            "Single Leg Stance":"Test each side separately; observe balance, trunk strategy and foot/ankle control.",
            "Deep Squat":"Use the standardized deep-squat observation and record pain/dysfunction classification."
        }
        for i,n in enumerate(instructions):
            st.markdown(f"**{n}**")
            st.caption(instructions[n])
            sf[n]=st.selectbox(f"{n} classification",MOVEMENT_SCREEN_OPTIONS,index=MOVEMENT_SCREEN_OPTIONS.index(sf.get(n,"Not assessed")),key=f"sfma_{i}")
        st.session_state.sfma_results=sf
        st.metric("SFMA Screen Index (descriptive)",f"{sfma_index(athlete()):.1f}/100")
    with tabs[5]:
        st.subheader("Joint-by-Joint Mobility")
        st.caption("Record left and right values for each relevant direction. Reference ranges should be interpreted according to the chosen test protocol and measurement method.")
        rom=st.session_state.mobility_rom
        groups={
            "Cervical":{"Cervical Flexion":(0,90),"Cervical Extension":(0,90),"Cervical Rotation":(0,120)},
            "Shoulder":{"Shoulder Flexion":(0,220),"Shoulder Abduction":(0,220),"Shoulder IR":(0,120),"Shoulder ER":(0,120)},
            "Thoracic":{"Thoracic Rotation":(0,90)},
            "Hip":{"Hip Flexion":(0,160),"Hip Extension":(0,60),"Hip Abduction":(0,90),"Hip Adduction":(0,60),"Hip IR":(0,90),"Hip ER":(0,90)},
            "Knee":{"Knee Flexion":(0,160)},
            "Ankle":{"Ankle Dorsiflexion":(0,60),"Ankle Plantarflexion":(0,90),"Ankle Inversion":(0,60),"Ankle Eversion":(0,45)},
            "Wrist":{"Wrist Flexion":(0,100),"Wrist Extension":(0,100)},
        }
        for group,items in groups.items():
            st.markdown(f"### {group}")
            for name,(mn,mx) in items.items():
                c1,c2,c3=st.columns([2,1,1])
                with c1: st.write(name)
                with c2: rom.setdefault(name,{"L":75.0,"R":75.0}); rom[name]["L"]=st.number_input("Left",float(mn),float(mx),float(rom[name]["L"]),0.5,key=f"rom_{name}_L")
                with c3: rom[name]["R"]=st.number_input("Right",float(mn),float(mx),float(rom[name]["R"]),0.5,key=f"rom_{name}_R")
        st.session_state.mobility_rom=rom
        st.metric("Mobility Symmetry Index",f"{mobility_index(athlete()):.1f}/100")
    a=athlete(); flags=screening_flags(a)
    st.markdown("### Screening Summary")
    c1,c2,c3,c4=st.columns(4); c1.metric("FMS",f"{fms_index(a):.1f}"); c2.metric("SFMA",f"{sfma_index(a):.1f}"); c3.metric("Mobility",f"{mobility_index(a):.1f}"); c4.metric("Flags",len(flags))
    for f in flags[:12]: st.warning(f)

elif page=="5. Stability / Neuromuscular":
    st.markdown('<div class="banner-header">05 | Stability + Neuromuscular Coordination</div>',unsafe_allow_html=True)
    st.caption("The values below are coach-recorded performance/control measures. They contribute to the programming engine but are not clinical diagnoses.")
    t=st.session_state.stability_tests
    st.subheader("Stability")
    stability_groups={
        "Static / unilateral":{"Single-Leg Stance L":(0,180),"Single-Leg Stance R":(0,180)},
        "Dynamic balance":{"Y Balance ANT L":(0,150),"Y Balance ANT R":(0,150),"Y Balance PM L":(0,180),"Y Balance PM R":(0,180),"Y Balance PL L":(0,180),"Y Balance PL R":(0,180)},
        "Movement control":{"Landing Control":(0,100),"Trunk Stability":(0,100),"Single-Leg Squat Control L":(0,100),"Single-Leg Squat Control R":(0,100)},
    }
    for group,items in stability_groups.items():
        st.markdown(f"### {group}")
        cols=st.columns(2)
        for i,(n,(mn,mx)) in enumerate(items.items()):
            with cols[i%2]: t[n]=st.number_input(n,float(mn),float(mx),float(t.get(n,(30.0 if "Stance" in n else 80.0))),0.5,key=f"stab_{n}")
    st.session_state.stability_tests=t
    st.metric("Stability Index",f"{stability_index(athlete()):.1f}/100")
    n=st.session_state.neuromuscular_tests
    st.subheader("Neuromuscular Coordination")
    n["Reaction Time"]=st.number_input("Reaction Time (s)",0.20,3.00,float(n.get("Reaction Time",0.75)),0.01)
    cols=st.columns(2)
    for i,k in enumerate(["Proprioception L","Proprioception R","Coordination L","Coordination R","Reactive Balance","Dual Task"]):
        with cols[i%2]: n[k]=st.number_input(k,0.0,100.0,float(n.get(k,80.0)),1.0,key=f"nm_{k}")
    st.session_state.neuromuscular_tests=n
    st.metric("Neuromuscular Index",f"{neuromuscular_index(athlete()):.1f}/100")

elif page=="6. Performance":
    st.markdown('<div class="banner-header">06 | Performance Testing</div>',unsafe_allow_html=True)
    a=athlete()
    st.caption("Tests are filtered by sport/position relevance. Greyed fields are intentionally not required for the current athlete.")
    c1,c2,c3=st.columns(3)
    with c1:
        setv("cmj",st.number_input("CMJ (cm)",5.0,100.0,float(st.session_state.cmj),0.5))
        setv("broad_jump",st.number_input("Broad Jump (cm)",50.0,350.0,float(st.session_state.broad_jump),1.0))
        setv("sprint_5m",st.number_input("5m Sprint (s)",0.50,4.00,float(st.session_state.sprint_5m),0.01))
        setv("sprint_10m",st.number_input("10m Sprint (s)",1.00,5.00,float(st.session_state.sprint_10m),0.01))
    with c2:
        speed_relevant=a.sport not in {"Swimming","Bodybuilding"}
        cod_relevant=a.sport in {"Soccer","Tennis","Basketball","Handball","Karate","MMA"}
        st.number_input("COD / T-Drill (s)",5.0,30.0,float(st.session_state.cod),0.01,disabled=not cod_relevant,key="perf_cod")
        if cod_relevant: setv("cod",st.session_state.perf_cod)
        setv("cooper_m",st.number_input("12-Min Cooper Distance (m)",500.0,5000.0,float(st.session_state.cooper_m),50.0))
        st.number_input("Squat 1RM (kg)",20.0,400.0,float(st.session_state.squat_1rm),1.0,key="perf_sq")
        setv("squat_1rm",st.session_state.perf_sq)
    with c3:
        st.number_input("Bench 1RM (kg)",20.0,300.0,float(st.session_state.bench_1rm),1.0,key="perf_bench")
        setv("bench_1rm",st.session_state.perf_bench)
        st.number_input("Overhead Press 1RM (kg)",10.0,200.0,float(st.session_state.ohp_1rm),1.0,key="perf_ohp")
        setv("ohp_1rm",st.session_state.perf_ohp)
        throw_relevant=a.sport in {"Tennis","Handball","Volleyball","Baseball/Softball"}
        st.number_input("Forehand Throw (m)",1.0,30.0,float(st.session_state.forehand_throw_m),0.1,disabled=not throw_relevant,key="perf_forehand")
        st.number_input("Backhand Throw (m)",1.0,30.0,float(st.session_state.backhand_throw_m),0.1,disabled=not throw_relevant,key="perf_backhand")
        if throw_relevant:
            setv("forehand_throw_m",st.session_state.perf_forehand); setv("backhand_throw_m",st.session_state.perf_backhand)
    scores=performance_scores(athlete()); st.dataframe(pd.DataFrame({"Quality":list(scores.keys()),"Score":list(scores.values())}),use_container_width=True,hide_index=True)

elif page=="7. Asymmetry":
    st.markdown('<div class="banner-header">07 | Asymmetry Analysis</div>',unsafe_allow_html=True)
    a=athlete(); rows=[]
    for name,pair in a.mobility_rom.items():
        if isinstance(pair,dict) and "L" in pair and "R" in pair:
            rows.append((name,float(pair["L"]),float(pair["R"]),asymmetry(float(pair["L"]),float(pair["R"]))))
    rows += [("Single-Leg Jump",a.left_jump,a.right_jump,asymmetry(a.left_jump,a.right_jump))]
    for key in ["Single-Leg Stance","Y Balance ANT","Y Balance PM","Y Balance PL","Single-Leg Squat Control","Proprioception","Coordination"]:
        if key=="Single-Leg Stance": l,r=a.stability_tests.get("Single-Leg Stance L",30),a.stability_tests.get("Single-Leg Stance R",30)
        elif key.startswith("Y Balance"): l,r=a.stability_tests.get(key+" L",70),a.stability_tests.get(key+" R",70)
        elif key=="Single-Leg Squat Control": l,r=a.stability_tests.get(key+" L",80),a.stability_tests.get(key+" R",80)
        else: l,r=a.neuromuscular_tests.get(key+" L",80),a.neuromuscular_tests.get(key+" R",80)
        rows.append((key,l,r,asymmetry(l,r)))
    df=pd.DataFrame(rows,columns=["Measure","Left","Right","Asymmetry %"])
    st.dataframe(df,use_container_width=True,hide_index=True)
    high=df[df["Asymmetry %"]>=10]
    if not high.empty: st.warning("High side-to-side differences are being fed into stability/coordination priorities. Review the underlying test protocol before making clinical decisions.")
    else: st.success("No measured asymmetry above the current coaching flag threshold of 10%.")

elif page=="8. Programming Priorities":
    st.markdown('<div class="banner-header">08 | Programming Priorities</div>',unsafe_allow_html=True)
    a=athlete(); c=constraint_engine(a); p=priorities(a); systems=system_allocation(a,p,c)
    c1,c2,c3,c4=st.columns(4); c1.metric("Readiness",f"{c['readiness']:.0f}"); c2.metric("Top Priority",next(iter(p))); c3.metric("Stability",f"{stability_index(a):.0f}"); c4.metric("Neuromuscular",f"{neuromuscular_index(a):.0f}")
    st.dataframe(pd.DataFrame({"Quality":list(p.keys()),"Priority %":list(p.values())}),use_container_width=True,hide_index=True)
    st.dataframe(pd.DataFrame({"Training System":list(systems.keys()),"Signal":list(systems.values())}),use_container_width=True,hide_index=True)
    st.info("The engine deliberately allocates both correction/weakness work and development of strong qualities. Screening changes dose, exercise choice and complexity; it does not erase the athlete's main goal.")

elif page=="9. Club Load":
    st.markdown('<div class="banner-header">09 | Club Training Days / Hours</div>',unsafe_allow_html=True)
    setv("club_days",st.multiselect("Club / Team Training Days",DAYS if "DAYS" in globals() else ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],default=st.session_state.get("club_days",[])))
    setv("team_minutes",st.number_input("Average Club Session Minutes",0,300,int(st.session_state.team_minutes),5))
    setv("competition_days",st.slider("Competitions / Matches per Week",0,4,int(st.session_state.competition_days)))
    st.info("Club load is treated as external training stress so the gym plan can reduce redundant fatigue and preserve high-quality sport work.")

elif page=="10. Equipment":
    st.markdown('<div class="banner-header">10 | Equipment Constraints</div>',unsafe_allow_html=True)
    setv("equipment",st.multiselect("Available Equipment",EQUIPMENT,default=st.session_state.equipment))
    st.caption("Equipment is a hard constraint. An exercise or MetCon station requiring unavailable equipment is not eligible for selection.")

elif page=="11. Training Program":
    st.markdown('<div class="banner-header">11 | Adaptive Multi-Month Training Program</div>',unsafe_allow_html=True)
    a=athlete(); program,engine=build_program(a,plan_months); st.session_state.generated_plan=program; st.session_state.decision_state=engine; st.session_state.rotation_map=engine.get("rotation",{}); c=engine["constraints"]; p=engine["priorities"]; systems=engine["systems"]
    c1,c2,c3,c4=st.columns(4); c1.metric("Readiness",f"{c['readiness']:.0f}/100"); c2.metric("Primary",a.primary_goal); c3.metric("Top Quality",next(iter(p))); c4.metric("Months",plan_months)
    month=st.selectbox("Month",list(range(1,plan_months+1)),format_func=lambda x:f"Month {x} - {mesocycle_phase(a,x)}")
    week=st.selectbox("Week",[1,2,3,4],format_func=lambda x:f"Week {x}")
    day=st.selectbox("Day",list(range(1,a.gym_days_available+1)),format_func=lambda x:f"Day {x}")
    session=program[month][week][day-1]
    st.markdown(f"<div class='goal-card'><b>Month {month} | Week {week} | Day {day}</b><br>{session['phase']} | Readiness {session['readiness']:.0f}/100</div>",unsafe_allow_html=True)
    render_session(a,session,week,engine)
    st.markdown("### Why this session")
    for reason in session.get("reasons",[]): st.write("- "+str(reason))
    st.caption("The plan is regenerated automatically on every Streamlit rerun. There is intentionally no Generate Plan button.")

elif page=="12. Feedback / Data":
    st.markdown('<div class="banner-header">12 | Feedback / Reassessment / Data</div>',unsafe_allow_html=True)
    a=athlete(); st.subheader("Session Feedback")
    c1,c2,c3=st.columns(3)
    with c1: session_rpe=st.slider("Last Session RPE",1.0,10.0,7.0,0.5)
    with c2: pain_after=st.slider("Pain During/After Session",0,10,0)
    with c3: performance_change=st.slider("Performance vs Previous Exposure",-2,2,0)
    duration=st.number_input("Actual session duration (min)",20,180,int(a.session_minutes),5)
    notes=st.text_input("Session note")
    if st.button("Apply feedback to next decision",type="primary"):
        st.session_state.feedback["session_rpe"].append(float(session_rpe)); st.session_state.feedback["pain"].append(int(pain_after)); st.session_state.feedback["performance"].append(int(performance_change))
        log_training_session(a,session_rpe,pain_after,performance_change,duration,notes)
        st.success("Feedback stored. The next rerun will use the updated state.")
    if st.session_state.feedback["session_rpe"]: st.dataframe(pd.DataFrame(st.session_state.feedback),use_container_width=True,hide_index=True)
    st.subheader("Assessment Snapshot")
    if st.button("Save current performance snapshot"):
        st.session_state.test_history.append(test_snapshot(a)); st.success("Snapshot saved.")
    if st.session_state.get("test_history"):
        st.dataframe(pd.DataFrame(st.session_state.test_history),use_container_width=True,hide_index=True)
    st.subheader("Saved Profiles")
    if st.button("Save current profile"):
        st.session_state.profiles[a.name]=dict((k,st.session_state[k]) for k in DEFAULTS); st.success("Profile saved in this Streamlit session.")
    if st.session_state.profiles:
        st.write(list(st.session_state.profiles.keys()))

# Final automatic regeneration after all current-page inputs have been applied.
# This is what makes every upstream change propagate without a Generate button.
_final_athlete=athlete()
_final_program,_final_engine=build_program(_final_athlete,plan_months)
st.session_state.generated_plan=_final_program
st.session_state.decision_state=_final_engine
st.session_state.rotation_map=_final_engine.get("rotation",{})

# Footer
st.markdown("<hr><div style='text-align:center;color:#64748b;font-size:.85rem'>Athlete-IQ | By: Coach Ahmed Youssef | Coaching and performance-planning software</div>",unsafe_allow_html=True)
