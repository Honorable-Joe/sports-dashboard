from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ==========================================
# 1. DATA MODELS & ATHLETE PROFILE
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
        if base_1rm:
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
# 4. MASTER WORKOUT GENERATOR
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
# 5. SAMPLE DATABASE & TEST EXECUTION
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

if __name__ == "__main__":
    # Create an athlete with Ankle and Shoulder restrictions
    athlete = Athlete(
        name="Jordan (Restricted Ankle & Shoulder)",
        experience_level="Intermediate",
        equipment=["barbell", "dumbbells", "machines", "cables"],
        mobility=MobilityProfile(ankle_dorsiflexion="FAIL", overhead_flexion="FAIL", hip_extension="PASS"),
        estimated_1rm={
            "Squat": 140.0, 
            "Overhead Press": 70.0, 
            "Horizontal Push": 100.0,
            "Hinge": 160.0
        }
    )

    patterns_to_train = ["Squat", "Overhead Press", "Horizontal Push", "Hinge"]
    engine = WorkoutProgramEngine(exercise_database)
    program = engine.generate_full_3_month_plan(athlete, patterns_to_train)

    # Print summary output for Month 1 and Month 2
    for month_key, weeks in program.items():
        print(f"\n========================================================")
        print(f"               PROGRAM OUTPUT: {month_key.upper()}")
        print(f"========================================================")
        
        for week_key, exercises in weeks.items():
            print(f"\n  --- {week_key.upper()} ---")
            for item in exercises:
                if "error" in item:
                    print(f"   * [{item['pattern']}] ERROR: {item['error']}")
                else:
                    print(f"   * [{item['pattern']}] {item['exercise']} ({item['equipment'].upper()})")
                    print(f"     Rx: {item['sets']} sets x {item['reps']} reps @ {item['target_load']} ({item['intensity_pct']} 1RM) | Tempo: {item['tempo']} | ({item['weekly_note']})")
