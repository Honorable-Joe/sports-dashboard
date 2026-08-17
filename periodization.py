PHASES=[("Accumulation","Hypertrophy / Work Capacity"),("Intensification","Strength / Force"),("Realization","Power / Speed / Transfer")]
def phase(month): return PHASES[min(month-1,2)]
def load(month,goal):
    if goal in {"Strength","Max Strength"}: return [("3-5 sets","4-6 reps","80-90% 1RM"),("3-5 sets","3-5 reps","85-93% 1RM"),("2-4 sets","2-4 reps","80-88% 1RM")][min(month-1,2)]
    if goal=="Hypertrophy": return [("3-4 sets","8-12 reps","65-78% 1RM"),("3-4 sets","6-10 reps","70-82% 1RM"),("2-4 sets","6-8 reps","72-85% 1RM")][min(month-1,2)]
    return [("3-4 sets","6-10 reps","RPE 6-8"),("3-5 sets","4-8 reps","RPE 7-8"),("2-4 sets","3-6 reps","high quality")][min(month-1,2)]
