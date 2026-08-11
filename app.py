from dataclasses import dataclass, field
from typing import List, Dict, Optional
import streamlit as st

# ==========================================
# 1. CORE DATA STRUCTURES
# ==========================================

@dataclass
class MobilityProfile:
    ankle_dorsiflexion: str = "PASS"  # "PASS" or "FAIL"
    overhead_flexion: str = "PASS"    # "PASS" or "FAIL"
    hip_extension: str = "PASS"       # "PASS" or "FAIL"

@dataclass
class Athlete:
    name: str
    experience_level: str
    equipment: List[str]               # e.g., ["barbell", "dumbbells", "machines", "cables"]
    mobility: MobilityProfile
    estimated_1rm: Dict[str, float]    # Movement pattern 1RM in kg

@dataclass
class Exercise:
    id: str
    name: str
    pattern: str                       # e.g., "Squat", "Overhead Press", "Horizontal Push", "Hinge"
    equipment_type: str                # "barbell", "dumbbells", "machines", "cables"
    prerequisites: List[str]           # Mobility checks required to execute safely
    month_block: int                   # Mesocycle month target (1, 2, or 3)


# ==========================================
# 2. DIAGNOSTIC & SELECTION FILTER ENGINE
# ==========================================

class ExerciseFilterEngine:
    """Filters exercises based on mobility flags, equipment availability, and monthly rotation."""
    
    def __init__(self, database: List[Exercise]):
        self.database = database

    def get_valid_exercise(self, pattern: str, month: int, athlete: Athlete) -> Optional[Exercise]:
        # Step 1: Match pattern & target month
        candidates = [
            ex for ex in self.database 
            if ex.pattern == pattern and ex.month_block == month
        ]
        
        # Step 2: Match equipment availability
        candidates = [ex for ex in candidates if ex.equipment_type in athlete.equipment]
        
        # Step 3: Screen against joint mobility prerequisites
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
            
        # Step 4: Fallback to machine or cable alternatives if free weights are unsafe/unavailable
        fallbacks = [
            ex for ex in self.database
            if ex.pattern == pattern 
            and ex.equipment_type in ["machines", "cables"]
            and ex.equipment_type in athlete.equipment
            and not any(getattr(athlete.mobility, p, "PASS") == "FAIL" for p in ex.prerequisites)
        ]
        return fallbacks[0] if fallbacks else None


# ==========================================
# 3. PERIODIZATION & PROGRESSIVE OVERLOAD
# ==========================================

class PeriodizationEngine:
    """Manages monthly phases and weekly loading parameters (including deloads)."""
    
    PHASE_CONFIGS = {
        1: {"phase": "Base Hypertrophy", "base_reps": "10-12", "base_sets": 3, "base_intensity": 0.70, "tempo": "3-1-1-0"},
        2: {"phase": "Maximal Strength", "base_reps": "6-8",   "base_sets": 4, "base_intensity": 0.80, "tempo": "2-0-1-0"},
        3: {"phase": "Power & Density",  "base_reps": "4-6",   "base_sets": 4, "base_intensity": 0.85, "tempo": "1-0-1-0"}
    }

    @staticmethod
    def calculate_prescription(exercise: Exercise, month: int, week: int, athlete: Athlete) -> Dict:
        config = PeriodizationEngine.PHASE_CONFIGS[month]
        base_intensity = config["base_intensity"]
        sets = config["base_sets"]
        reps = config["base_reps"]
        
        # Weekly Overload Architecture (3-Week Ramp + 1-Week Deload)
        if week == 1:
            weekly_intensity = base_intensity
            note = "Base Load"
        elif week == 2:
            weekly_intensity = base_intensity + 0.025  # +2.5%
            note = "Overload Step 1"
        elif week == 3:
            weekly_intensity = base_intensity + 0.050  # +5.0%
            note = "Peak Load"
        elif week == 4:
            weekly_intensity = base_intensity - 0.150  # Deload: -15% intensity
            sets = max(2, sets - 1)                    # Reduce volume
            reps = "8-10"                              # Lighter focus
            note = "Active Recovery / Deload"
            
        base_1rm = athlete.estimated_1rm.get(exercise.pattern)
        if base_1rm and base_1rm > 0:
            target_weight = round(base_1rm * weekly_intensity, 1)
            load_display = f"{target_weight} kg"
        else:
            load_display = "Auto-regulate (RPE 8)"

        return {
            "exercise": exercise.name,
            "equipment": exercise.equipment_type,
            "phase": config["phase"],
            "week": week,
            "sets": sets,
            "reps": reps,
            "target_load": load_display,
            "intensity_pct": f"{int(weekly_intensity * 100)}%",
            "tempo": config["tempo"],
            "weekly_note": note
        }


# ==========================================
# 4. MASTER WORKOUT PROGRAM GENERATOR
# ==========================================

class WorkoutProgramEngine:
    def __init__(self, exercise_db: List[Exercise]):
        self.filter_engine = ExerciseFilterEngine(exercise_db)

    def generate_full_3_month_plan(self, athlete: Athlete, movement_patterns: List[str]) -> Dict:
        macrocycle = {}
        for month in [1, 2, 3]:
            month_key = f"Month_{month}"
            macrocycle[month_key] = {}
            for week in range(1, 5):
                week_key = f"Week_{week}"
                weekly_prescriptions = []
                for pattern in movement_patterns:
                    exercise = self.filter_engine.get_valid_exercise(pattern, month, athlete)
                    if exercise:
                        rx = PeriodizationEngine.calculate_prescription(exercise, month, week, athlete)
                        rx["pattern"] = pattern
                        weekly_prescriptions.append(rx)
                    else:
                        weekly_prescriptions.append({
                            "pattern": pattern, 
                            "error": "No safe exercise found matching equipment and mobility profile."
                        })
                macrocycle[month_key][week_key] = weekly_prescriptions
        return macrocycle


# ==========================================
# 5. SAMPLE EXERCISE DATABASE
# ==========================================

exercise_database = [
    # --- SQUAT PATTERN ---
    Exercise("ex01", "Barbell Back Squat", "Squat", "barbell", ["ankle_dorsiflexion"], 1),
    Exercise("ex02", "Heel-Elevated Goblet Squat", "Squat", "dumbbells", [], 1),
    Exercise("ex03", "Barbell Front Squat", "Squat", "barbell", ["ankle_dorsiflexion"], 2),
    Exercise("ex04", "Machine Hack Squat", "Squat", "machines", [], 2),
    Exercise("ex05", "Seated Leg Press", "Squat", "machines", [], 3),

    # --- OVERHEAD PRESS PATTERN ---
    Exercise("ex06", "Barbell Standing OHP", "Overhead Press", "barbell", ["overhead_flexion"], 1),
    Exercise("ex07", "Landmine Angled Press", "Overhead Press", "barbell", [], 1),
    Exercise("ex08", "Dumbbell Overhead Press", "Overhead Press", "dumbbells", ["overhead_flexion"], 2),
    Exercise("ex09", "Seated Machine Shoulder Press", "Overhead Press", "machines", [], 2),
    Exercise("ex10", "High-Incline Cable Press", "Overhead Press", "cables", [], 3),

    # --- HORIZONTAL PUSH PATTERN ---
    Exercise("ex11", "Flat Barbell Bench Press", "Horizontal Push", "barbell", [], 1),
    Exercise("ex12", "Incline Dumbbell Bench Press", "Horizontal Push", "dumbbells", [], 2),
    Exercise("ex13", "Seated Chest Press Machine", "Horizontal Push", "machines", [], 3),

    # --- HINGE PATTERN ---
    Exercise("ex14", "Barbell Conventional Deadlift", "Hinge", "barbell", ["hip_extension"], 1),
    Exercise("ex15", "Dumbbell Romanian Deadlift", "Hinge", "dumbbells", [], 1),
    Exercise("ex16", "Barbell Romanian Deadlift", "Hinge", "barbell", [], 2),
    Exercise("ex17", "Cable Hip Thrust", "Hinge", "cables", [], 3)
]


# ==========================================
# 6. STREAMLIT FRONTEND & UI ENGINE
# ==========================================

st.set_page_config(page_title="Interlocking Workout Engine", page_icon="🏋️", layout="wide")

st.title("🏋️ Interlocking Workout Engine")
st.caption("Diagnostic screening, periodization, and automated exercise rotation in one connected system.")

# --- SIDEBAR: COLLAPSIBLE EXPANDERS ---
st.sidebar.header("⚙️ Configuration Panel")

# Group 1: Athlete Profile & 1RMs
with st.sidebar.expander("👤 Athlete Profile & 1RMs", expanded=False):
    athlete_name = st.text_input("Athlete Name", value="Jordan")
    experience_level = st.selectbox("Experience Level", ["Novice", "Intermediate", "Advanced"], index=1)
    
    st.markdown("**Estimated 1RMs (kg)**")
    squat_1rm = st.number_input("Squat 1RM", min_value=0.0, value=140.0, step=2.5)
    ohp_1rm = st.number_input("Overhead Press 1RM", min_value=0.0, value=70.0, step=2.5)
    bench_1rm = st.number_input("Bench Press 1RM", min_value=0.0, value=100.0, step=2.5)
    hinge_1rm = st.number_input("Hinge 1RM", min_value=0.0, value=160.0, step=2.5)

# Group 2: Equipment Pool
with st.sidebar.expander("🏋️ Equipment Available", expanded=False):
    selected_equipment = st.multiselect(
        "Available Tools:",
        options=["barbell", "dumbbells", "machines", "cables"],
        default=["barbell", "dumbbells", "machines", "cables"]
    )

# Group 3: Joint Mobility Screening (Expanded by default for quick access)
with st.sidebar.expander("🩺 Joint Mobility Screening", expanded=True):
    st.caption("Flag failed tests to automatically filter contraindicated lifts.")
    ankle_status = st.radio("Ankle Dorsiflexion", ["PASS", "FAIL"], index=1, help="Knee-to-wall test (<10cm fails)")
    overhead_status = st.radio("Overhead Flexion", ["PASS", "FAIL"], index=1, help="Back-to-wall thumb touch")
    hip_status = st.radio("Hip Extension", ["PASS", "FAIL"], index=0, help="Thomas test for tight hip flexors")

# Group 4: Target Patterns & Timeline
with st.sidebar.expander("🎯 Target Patterns & Timeline", expanded=False):
    selected_patterns = st.multiselect(
        "Movement Patterns:",
        options=["Squat", "Overhead Press", "Horizontal Push", "Hinge"],
        default=["Squat", "Overhead Press", "Horizontal Push", "Hinge"]
    )
    st.divider()
    selected_month = st.selectbox("View Month", [1, 2, 3], index=0)
    selected_week = st.slider("View Week", min_value=1, max_value=4, value=1)


# ==========================================
# 7. EXECUTION & DASHBOARD RENDERING
# ==========================================

# Instantiate Athlete Object
athlete = Athlete(
    name=athlete_name,
    experience_level=experience_level,
    equipment=selected_equipment,
    mobility=MobilityProfile(
        ankle_dorsiflexion=ankle_status,
        overhead_flexion=overhead_status,
        hip_extension=hip_status
    ),
    estimated_1rm={
        "Squat": squat_1rm,
        "Overhead Press": ohp_1rm,
        "Horizontal Push": bench_1rm,
        "Hinge": hinge_1rm
    }
)

# Run Program Engine
program_engine = WorkoutProgramEngine(exercise_database)
full_program = program_engine.generate_full_3_month_plan(athlete, selected_patterns)

# Display Diagnostic Summary Flags
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Ankle Screening", athlete.mobility.ankle_dorsiflexion, 
              delta="Restricted" if athlete.mobility.ankle_dorsiflexion == "FAIL" else "Normal", 
              delta_color="inverse")
with col_b:
    st.metric("Shoulder Screening", athlete.mobility.overhead_flexion, 
              delta="Restricted" if athlete.mobility.overhead_flexion == "FAIL" else "Normal", 
              delta_color="inverse")
with col_c:
    st.metric("Hip Screening", athlete.mobility.hip_extension, 
              delta="Restricted" if athlete.mobility.hip_extension == "FAIL" else "Normal", 
              delta_color="inverse")

st.divider()

# Get Prescription for Selected Timeline
month_key = f"Month_{selected_month}"
week_key = f"Week_{selected_week}"
current_prescriptions = full_program[month_key][week_key]

phase_name = PeriodizationEngine.PHASE_CONFIGS[selected_month]["phase"]
st.subheader(f"📋 {athlete.name}'s Plan — Month {selected_month} ({phase_name}) | Week {selected_week}")

# Render Exercises as Clean Metric Cards
if not selected_patterns:
    st.warning("Please select at least one movement pattern from the sidebar options.")
else:
    for rx in current_prescriptions:
        if "error" in rx:
            st.error(f"❌ **[{rx['pattern']}]**: {rx['error']}")
        else:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                with c1:
                    st.markdown(f"### **{rx['exercise']}**")
                    st.caption(f"Pattern: **{rx['pattern']}** | Tool: **{rx['equipment'].upper()}**")
                with c2:
                    st.metric("Target Load", rx['target_load'], delta=rx['intensity_pct'])
                with c3:
                    st.metric("Sets & Reps", f"{rx['sets']} × {rx['reps']}")
                with c4:
                    st.metric("Tempo / Focus", rx['tempo'], delta=rx['weekly_note'], delta_color="off")
