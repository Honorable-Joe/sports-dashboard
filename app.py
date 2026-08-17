import streamlit as st
import pandas as pd
import json, math, random
from dataclasses import dataclass, field, asdict
from datetime import datetime

st.set_page_config(page_title='Athlete-IQ v8', page_icon='AIQ', layout='wide')

# ============================================================
# ATHLETE-IQ v8.0 - CLOSED LOOP ADAPTIVE PROGRAMMING ENGINE
# One state -> one decision engine -> one program -> feedback -> next state.
# Rule-based coaching software; screening is observational, not diagnosis.
# ============================================================

SPORTS = {
    'General Fitness': ['General'],
    'Soccer': ['Goalkeeper','Center Back','Full Back','Central Midfielder','Winger','Striker'],
    'Basketball': ['Guard','Wing','Forward','Center'],
    'Volleyball': ['Setter','Outside Hitter','Opposite','Middle Blocker','Libero'],
    'Tennis': ['Singles','Doubles'],
    'Swimming': ['Freestyle','Backstroke','Breaststroke','Butterfly','Individual Medley'],
    'Boxing': ['Boxer'], 'MMA': ['MMA Athlete'],
    'Karate': ['Kumite','Kata','Kumite + Kata'],
    'Handball': ['Goalkeeper','Wing','Backcourt','Pivot'],
    'Rugby': ['Back','Forward'],
    'Track & Field': ['Sprinter','Middle Distance','Jumper','Thrower'],
}

SPORT_DEMANDS = {
 'General Fitness': ['strength','hypertrophy','mobility','aerobic'],
 'Soccer': ['unilateral','acceleration','deceleration','cod','reactive','hamstring','adductor','ankle','aerobic'],
 'Basketball': ['jump','landing','cod','reactive','unilateral','ankle','strength','aerobic'],
 'Volleyball': ['jump','landing','reactive','shoulder','unilateral','strength','power'],
 'Tennis': ['unilateral','cod','reactive','rotation','shoulder','deceleration','power'],
 'Swimming': ['pull','shoulder','scapular','trunk','mobility','aerobic','anaerobic'],
 'Boxing': ['reaction','rotation','footwork','power','conditioning','shoulder','trunk'],
 'MMA': ['strength','power','rotation','anti_rotation','grip','reaction','conditioning','unilateral'],
 'Karate': ['reaction','unilateral','rotation','cod','balance','power','mobility','trunk'],
 'Handball': ['throw','shoulder','jump','cod','reactive','unilateral','power'],
 'Rugby': ['strength','acceleration','contact','power','conditioning','unilateral'],
 'Track & Field': ['power','speed','strength','elasticity','event_specific'],
}

POSITION_DEMANDS = {
 'Goalkeeper':['lateral_power','reaction','landing','adductor','trunk','shoulder'],
 'Winger':['acceleration','max_velocity','deceleration','cod','hamstring','calf','unilateral'],
 'Striker':['acceleration','deceleration','unilateral','hamstring','power'],
 'Center Back':['strength','deceleration','jump','trunk','adductor'],
 'Full Back':['acceleration','cod','unilateral','aerobic'],
 'Central Midfielder':['aerobic','repeated_sprint','cod','unilateral','trunk'],
 'Singles':['rotation','cod','unilateral','reaction','shoulder'],
 'Doubles':['reaction','cod','rotation','shoulder','lateral'],
 'Freestyle':['pull','shoulder','scapular','trunk','aerobic'],
 'Backstroke':['shoulder','scapular','trunk','aerobic'],
 'Breaststroke':['adductor','hip','trunk','mobility','aerobic'],
 'Butterfly':['shoulder','trunk','power','aerobic'],
 'Individual Medley':['pull','shoulder','trunk','mobility','aerobic'],
 'Kumite + Kata':['reaction','balance','rotation','cod','power','mobility'],
 'Kumite':['reaction','cod','power','rotation'],
 'Kata':['balance','mobility','control','rotation'],
}

GOAL_WEIGHTS = {
 'Strength': {'strength':1.0,'hypertrophy':.55,'power':.35,'coordination':.25,'conditioning':.15},
 'Hypertrophy': {'hypertrophy':1.0,'strength':.55,'coordination':.15,'conditioning':.10},
 'Power': {'power':1.0,'strength':.65,'coordination':.55,'hypertrophy':.25,'conditioning':.15},
 'Speed': {'speed':1.0,'power':.75,'strength':.45,'coordination':.65,'conditioning':.20},
 'Agility': {'cod':1.0,'reactive':.85,'coordination':.75,'power':.60,'strength':.35},
 'Endurance': {'aerobic':1.0,'conditioning':.90,'strength':.30,'hypertrophy':.15},
 'Sports Performance': {'power':.75,'speed':.75,'coordination':.75,'strength':.65,'conditioning':.55},
 'General Fitness': {'strength':.65,'hypertrophy':.45,'aerobic':.50,'mobility':.40,'conditioning':.45},
}

EQUIPMENT = ['Bodyweight','Dumbbells','Kettlebells','Barbells','Cable/Machines','Medicine Ball','Resistance Bands','Pull-up Bar','Dip Belt','Sled','TRX','Plyo Box','Battle Rope','Stability Ball']

@dataclass
class Exercise:
    name: str
    family: str
    qualities: tuple
    equipment: tuple
    laterality: str='Bilateral'
    coordination: str='Standard'
    plane: str='Sagittal'
    level: str='Intermediate'
    complexity: int=2
    fatigue: int=2
    impact: int=0
    sports: tuple=()
    positions: tuple=()
    phases: tuple=('Foundation','Development','Performance')

EX = [
 # lower
 Exercise('Goblet Squat','Knee Dominant',('strength','hypertrophy'),('Dumbbells','Kettlebells'),level='Beginner',complexity=1),
 Exercise('Barbell Back Squat','Knee Dominant',('strength','hypertrophy'),('Barbells',),level='Advanced',complexity=2,fatigue=4),
 Exercise('Front Squat','Knee Dominant',('strength','power'),('Barbells',),level='Advanced',complexity=3,fatigue=4),
 Exercise('DB Bulgarian Split Squat','Unilateral Lower',('strength','hypertrophy','unilateral'),('Dumbbells',),laterality='Unilateral',level='Intermediate',complexity=2),
 Exercise('Rear Foot Elevated Split Squat','Unilateral Lower',('strength','hypertrophy','unilateral'),('Dumbbells','Barbells'),laterality='Unilateral',level='Intermediate',complexity=2),
 Exercise('Lateral Lunge','Frontal Lower',('unilateral','strength','cod'),('Bodyweight','Dumbbells','Kettlebells'),laterality='Unilateral',plane='Frontal',complexity=2),
 Exercise('Single-Leg Squat to Box','Unilateral Lower',('unilateral','strength','coordination'),('Bodyweight','Dumbbells','Plyo Box'),laterality='Unilateral',level='Advanced',complexity=3),
 Exercise('Romanian Deadlift','Hip Hinge',('strength','hypertrophy','hamstring'),('Dumbbells','Barbells'),level='Intermediate',complexity=2),
 Exercise('Single-Leg RDL','Hip Hinge',('unilateral','hamstring','coordination'),('Bodyweight','Dumbbells','Kettlebells'),laterality='Unilateral',coordination='Contralateral',level='Intermediate',complexity=3),
 Exercise('Barbell Hip Thrust','Hip Extension',('strength','hypertrophy'),('Barbells',),level='Intermediate',complexity=2,fatigue=3),
 Exercise('Single-Leg Hip Thrust','Hip Extension',('unilateral','strength'),('Bodyweight','Dumbbells'),laterality='Unilateral',level='Intermediate',complexity=2),
 Exercise('Standing Calf Raise','Calf/Ankle',('strength','ankle'),('Bodyweight','Dumbbells','Barbells'),level='Beginner',complexity=1),
 Exercise('Single-Leg Calf Raise','Calf/Ankle',('unilateral','ankle'),('Bodyweight','Dumbbells'),laterality='Unilateral',level='Intermediate',complexity=2),
 # push
 Exercise('Barbell Bench Press','Horizontal Push',('strength','hypertrophy'),('Barbells',),level='Intermediate',complexity=2,fatigue=3),
 Exercise('Dumbbell Bench Press','Horizontal Push',('strength','hypertrophy'),('Dumbbells',),level='Beginner',complexity=1,fatigue=3),
 Exercise('Incline Dumbbell Press','Horizontal Push',('strength','hypertrophy','shoulder'),('Dumbbells',),level='Intermediate',complexity=2),
 Exercise('Single-Arm Dumbbell Floor Press','Horizontal Push',('strength','unilateral','anti_rotation'),('Dumbbells',),laterality='Unilateral',coordination='Contralateral',level='Intermediate',complexity=3),
 Exercise('Dumbbell Shoulder Press','Vertical Push',('strength','hypertrophy','shoulder'),('Dumbbells',),level='Beginner',complexity=1),
 Exercise('Single-Arm Landmine Press','Vertical Push',('strength','power','anti_rotation'),('Barbells',),laterality='Unilateral',coordination='Contralateral',level='Advanced',complexity=3),
 Exercise('Push Press','Vertical Push',('power','strength','coordination'),('Barbells','Dumbbells'),level='Advanced',complexity=3,fatigue=3),
 Exercise('Half-Kneeling Single-Arm Press','Vertical Push',('shoulder','anti_rotation','strength'),('Dumbbells','Cable/Machines'),laterality='Unilateral',coordination='Contralateral',level='Intermediate',complexity=3),
 # pull
 Exercise('1-Arm Dumbbell Row','Horizontal Pull',('strength','hypertrophy','scapular'),('Dumbbells',),laterality='Unilateral',level='Beginner',complexity=2),
 Exercise('Chest-Supported DB Row','Horizontal Pull',('strength','hypertrophy','scapular'),('Dumbbells',),level='Beginner',complexity=1),
 Exercise('Barbell Row','Horizontal Pull',('strength','hypertrophy'),('Barbells',),level='Advanced',complexity=2),
 Exercise('Pull-Up','Vertical Pull',('strength','hypertrophy','scapular'),('Pull-up Bar',),level='Intermediate',complexity=2),
 Exercise('Weighted Pull-Up','Vertical Pull',('strength','power','scapular'),('Pull-up Bar','Dip Belt'),level='Advanced',complexity=3,fatigue=3),
 Exercise('Lat Pulldown','Vertical Pull',('strength','hypertrophy'),('Cable/Machines',),level='Beginner',complexity=1),
 # trunk / stability
 Exercise('Pallof Press','Anti-Rotation',('anti_rotation','coordination','trunk'),('Cable/Machines','Resistance Bands'),laterality='Unilateral',coordination='Contralateral',plane='Transverse',complexity=2),
 Exercise('Half-Kneeling Pallof Press','Anti-Rotation',('anti_rotation','trunk','stability'),('Resistance Bands','Cable/Machines'),laterality='Unilateral',coordination='Contralateral',plane='Transverse',complexity=3),
 Exercise('Suitcase Carry','Carry',('anti_rotation','stability','unilateral'),('Dumbbells','Kettlebells'),laterality='Unilateral',coordination='Contralateral',plane='Frontal',complexity=2),
 Exercise('Front Rack Carry','Carry',('trunk','stability','strength'),('Dumbbells','Kettlebells','Barbells'),level='Intermediate',complexity=2),
 Exercise('Farmer Carry','Carry',('strength','trunk','grip'),('Dumbbells','Kettlebells'),complexity=1),
 Exercise('Copenhagen Plank','Stability',('adductor','stability','trunk'),('Bodyweight',),laterality='Unilateral',plane='Frontal',level='Advanced',complexity=3),
 Exercise('Dead Bug','Core Control',('trunk','coordination','stability'),('Bodyweight',),coordination='Contralateral',level='Beginner',complexity=1),
 Exercise('Bird Dog Row','Core Control',('trunk','coordination','anti_rotation','scapular'),('Dumbbells',),laterality='Unilateral',coordination='Contralateral',level='Advanced',complexity=4),
 Exercise('Single-Arm Row + Opposite-Arm Press on Stability Ball','Integrated Neuromuscular',('strength','coordination','stability','anti_rotation','scapular'),('Dumbbells','Stability Ball'),laterality='Unilateral',coordination='Contralateral',level='Elite',complexity=5,fatigue=4,sports=('Soccer','Tennis','MMA','Karate','Basketball','Volleyball')),
 Exercise('Single-Leg RDL + Row','Integrated Neuromuscular',('strength','unilateral','coordination','stability'),('Dumbbells',),laterality='Unilateral',coordination='Contralateral',level='Advanced',complexity=4),
 Exercise('Shadow Boxing','Sport Skill',('reaction','coordination','conditioning','footwork'),('Bodyweight',),level='Beginner',complexity=2,sports=('Boxing','MMA')),
 Exercise('Reactive Footwork','Sport Skill',('reaction','coordination','cod'),('Bodyweight',),level='Intermediate',complexity=3,sports=('Boxing','MMA')),
 Exercise('Band Pull-Apart','Warmup / Activation',('scapular','shoulder'),('Resistance Bands',),level='Beginner',complexity=1),
 Exercise('Mountain Climber','Conditioning',('conditioning','trunk'),('Bodyweight',),level='Beginner',complexity=1),
 Exercise('Bodyweight Squat','Conditioning',('conditioning','knee'),('Bodyweight',),level='Beginner',complexity=1),
 Exercise('Bear Crawl','Sport Skill',('coordination','trunk','conditioning'),('Bodyweight',),level='Intermediate',complexity=3,sports=('MMA',)),
 # corrective / control
 Exercise('Glute Bridge','Corrective Hip',('hip_control','trunk','activation'),('Bodyweight',),level='Beginner',complexity=1),
 Exercise('Hip Airplane','Corrective Hip',('hip_control','unilateral','stability','coordination'),('Bodyweight',),laterality='Unilateral',level='Advanced',complexity=4),
 Exercise('Wall Slide','Corrective Shoulder',('scapular','mobility','shoulder'),('Bodyweight',),level='Beginner',complexity=1),
 Exercise('Serratus Wall Push-Up','Corrective Shoulder',('scapular','shoulder','stability'),('Bodyweight',),level='Beginner',complexity=2),
 Exercise('Adductor Rock Back','Corrective Hip',('mobility','adductor'),('Bodyweight',),level='Beginner',complexity=1),
 # plyo/agility
 Exercise('Lateral Bound to Stick','Agility',('cod','lateral_power','landing','unilateral'),('Bodyweight',),laterality='Unilateral',plane='Frontal',level='Intermediate',complexity=3,impact=3,sports=('Soccer','Tennis','Basketball','Volleyball','Karate')),
 Exercise('Reactive Cone Drill','Agility',('reactive','cod','coordination'),('Bodyweight','Plyo Box'),level='Intermediate',complexity=3,impact=2,sports=('Soccer','Tennis','Basketball','Karate')),
 Exercise('Crossover Step to Sprint','Agility',('acceleration','cod','coordination'),('Bodyweight',),laterality='Unilateral',level='Intermediate',complexity=3,impact=2,sports=('Soccer','Tennis','Basketball')),
 Exercise('Deceleration to Re-Acceleration','Agility',('deceleration','acceleration','cod'),('Bodyweight',),level='Advanced',complexity=4,impact=3,sports=('Soccer','Basketball','Tennis')),
 Exercise('Reactive Mirror Shuffle','Agility',('reactive','cod','coordination'),('Bodyweight',),level='Advanced',complexity=4,impact=2,sports=('Soccer','Tennis','Basketball','Karate','MMA')),
 Exercise('Single-Leg Hop and Stick','Plyometric',('power','landing','unilateral','coordination'),('Bodyweight',),laterality='Unilateral',level='Intermediate',complexity=3,impact=3),
 Exercise('Lateral Skater Jump','Plyometric',('power','lateral_power','unilateral'),('Bodyweight',),laterality='Unilateral',plane='Frontal',level='Intermediate',complexity=2,impact=3),
 Exercise('Depth Jump to Stick','Plyometric',('power','landing','reactive'),('Plyo Box',),level='Elite',complexity=5,impact=5),
 Exercise('Medicine Ball Rotational Throw','Power',('power','rotation','coordination'),('Medicine Ball',),laterality='Unilateral',plane='Transverse',level='Intermediate',complexity=3,impact=2),
 Exercise('Medicine Ball Scoop Toss','Power',('power','rotation','coordination'),('Medicine Ball',),plane='Transverse',level='Intermediate',complexity=3,impact=2),
]

# Warm-up building blocks. They are deliberately low fatigue.
WARMUPS = {
 'general': [('Easy Bike / Jog',3),('Dynamic March + Arm Swing',1)],
 'knee': [('Bodyweight Squat',1),('Reverse Lunge Reach',1)],
 'hinge': [('Hip Hinge Drill',1),('Glute Bridge',1)],
 'push': [('Scapular Push-Up',1),('Light Push-Up',1)],
 'pull': [('Band Pull-Apart',1),('Light Row',1)],
 'shoulder': [('Wall Slide',1),('Band External Rotation',1)],
 'trunk': [('Dead Bug',1),('Bird Dog',1)],
 'unilateral': [('Single-Leg Balance',1),('Lateral Lunge Reach',1)],
 'power': [('Pogo Hops',1),('Build-Up Jump',1)],
 'agility': [('Low-Level Lateral Shuffle',1),('Progressive Change of Direction',1)],
}

DEFAULTS = {
 'name':'Athlete','age':25,'sex':'Male','height':180.0,'weight':80.0,
 'sport':'General Fitness','position':'General','primary':'General Fitness','secondary':[],
 'phase':'Foundation','level':'Intermediate','days':4,'equipment':['Bodyweight','Dumbbells','Barbells','Cable/Machines'],
 'readiness':8,'pain':0,'training_load':5,'weeks_training':8,
 'screening':{},'tests':{},'feedback':[]
}

# ---------------- STATE ----------------
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v
if 'program' not in st.session_state: st.session_state.program=None
if 'athlete_state' not in st.session_state: st.session_state.athlete_state=None

# ---------------- HELPERS ----------------
def setv(k,v): st.session_state[k]=v

def level_num(level): return {'Beginner':1,'Intermediate':2,'Advanced':3,'Elite':4}.get(level,2)

def phase_for(month):
    return 'Foundation' if month == 1 else ('Development' if month < 4 else 'Performance')

def norm(v):
    return max(0.0,min(1.0,float(v)))

def screen_findings():
    return [k for k,v in st.session_state.screening.items() if v]

def performance_profile():
    t=st.session_state.tests
    # User-entered relative ratings 1-10 are intentionally simple and transparent.
    return {k:float(v) for k,v in t.items() if isinstance(v,(int,float)) and v>0}

def build_athlete_state():
    a={k:st.session_state[k] for k in DEFAULTS}
    a['screening']=dict(st.session_state.screening)
    a['tests']=dict(st.session_state.tests)
    a['feedback']=list(st.session_state.feedback)
    demands=list(SPORT_DEMANDS.get(a['sport'],[]))+list(POSITION_DEMANDS.get(a['position'],[]))
    goal=GOAL_WEIGHTS.get(a['primary'],GOAL_WEIGHTS['General Fitness'])
    # Need map: screening and tests become modifiers, not direct prescriptions.
    needs={}
    for q in set(demands + list(goal.keys())): needs[q]=0.35
    for q in demands: needs[q]=needs.get(q,0)+0.25
    for q,w in goal.items(): needs[q]=needs.get(q,0)+w
    # Screening findings create a corrective priority, while never replacing performance work.
    if a['screening'].get('Anterior Pelvic Tilt'): needs['hip_control']=needs.get('hip_control',0)+0.85; needs['trunk']=needs.get('trunk',0)+0.25
    if a['screening'].get('Posterior Pelvic Tilt'): needs['hip_control']=needs.get('hip_control',0)+0.65; needs['mobility']=needs.get('mobility',0)+0.35
    if a['screening'].get('Scapular Winging'): needs['scapular']=needs.get('scapular',0)+0.9; needs['shoulder']=needs.get('shoulder',0)+0.35
    if a['screening'].get('Forward Head'): needs['scapular']=needs.get('scapular',0)+0.45; needs['mobility']=needs.get('mobility',0)+0.35
    if a['screening'].get('Knee Valgus'): needs['unilateral']=needs.get('unilateral',0)+0.55; needs['stability']=needs.get('stability',0)+0.55
    if a['screening'].get('Pelvic Hike'): needs['unilateral']=needs.get('unilateral',0)+0.45; needs['hip_control']=needs.get('hip_control',0)+0.45
    sfma_map={'Deep Squat':'mobility','Hurdle Step':'unilateral','Inline Lunge':'unilateral','Shoulder Mobility':'shoulder','Active Straight Leg Raise':'mobility','Trunk Stability Push-Up':'stability','Rotary Stability':'coordination'}
    for item in a['screening'].get('SFMA',[]): needs[sfma_map.get(item,'mobility')]=needs.get(sfma_map.get(item,'mobility'),0)+0.55
    # Performance tests: low rating = weakness, high rating = strength to maintain/progress.
    strengths=[]; weaknesses=[]
    for q,v in performance_profile().items():
        if v <= 4: weaknesses.append(q); needs[q]=needs.get(q,0)+0.8
        elif v >= 8: strengths.append(q); needs[q]=needs.get(q,0)+0.35
    # Readiness/fatigue is a global modifier.
    readiness=float(a['readiness'])
    fatigue=max(0,10-readiness)+float(a['pain'])*0.8
    return {'profile':a,'demands':sorted(set(demands)),'needs':needs,'strengths':strengths,'weaknesses':weaknesses,'fatigue':fatigue}

# ---------------- CLOSED-LOOP SELECTION ----------------
def equipment_ok(ex): return all(e in st.session_state.equipment for e in ex.equipment)

def sport_ok(ex,a):
    if not ex.sports: return True
    return a['sport'] in ex.sports

def phase_ok(ex,phase): return phase in ex.phases

def history_counts():
    counts={}
    for fb in st.session_state.feedback:
        for n in fb.get('exercise_names',[]): counts[n]=counts.get(n,0)+1
    return counts

def family_counts():
    counts={}
    for fb in st.session_state.feedback:
        for f in fb.get('families',[]): counts[f]=counts.get(f,0)+1
    return counts

def exercise_score(ex, astate, slot, month, used_names, used_families):
    a=astate['profile']; needs=astate['needs']; demands=astate['demands']
    score=0.0
    q=set(ex.qualities)
    for x in q: score += needs.get(x,0)*2.0
    if slot in ex.family: score += 4.0
    slot_alias={'push':['Horizontal Push','Vertical Push'],'pull':['Horizontal Pull','Vertical Pull'],'knee':['Knee Dominant','Unilateral Lower','Frontal Lower'],'hinge':['Hip Hinge','Hip Extension','Unilateral Lower'],'trunk':['Anti-Rotation','Stability','Core Control','Carry'],'unilateral':['Unilateral Lower','Frontal Lower','Integrated Neuromuscular'],'integrated':['Integrated Neuromuscular'],'corrective':['Corrective Hip','Corrective Shoulder'],'power':['Power','Plyometric'],'agility':['Agility']}
    if ex.family in slot_alias.get(slot,[]): score += 7
    if a['sport'] in ex.sports: score += 4
    if a['position'] in ex.positions: score += 3
    if ex.level == 'Elite' and level_num(a['level'])>=4: score += 3
    elif level_num(ex.level) <= level_num(a['level']): score += 1
    else: score -= (level_num(ex.level)-level_num(a['level']))*3
    if month==1 and ex.complexity>=4: score -= 1
    if month>=3 and level_num(a['level'])>=3: score += ex.complexity*0.5
    # Controlled variation: exercise and stimulus history penalties.
    if ex.name in used_names: score -= 7
    score -= history_counts().get(ex.name,0)*1.7
    score -= family_counts().get(ex.family,0)*0.5
    if ex.name in ['Glute Bridge','Suitcase Carry'] and month>1: score -= 1.5
    # Goal-specific direct bonuses.
    primary=a['primary']
    if primary=='Strength' and ex.family in ['Knee Dominant','Hip Hinge','Horizontal Push','Vertical Push','Horizontal Pull','Vertical Pull']: score += 2.5
    if primary=='Hypertrophy' and ex.family in ['Horizontal Push','Vertical Push','Horizontal Pull','Vertical Pull','Knee Dominant','Hip Hinge','Hip Extension']: score += 2.2
    if primary in ['Speed','Power'] and ('power' in q or 'coordination' in q): score += 2.0
    if primary=='Agility' and ex.family=='Agility': score += 4
    # Strong points get maintained, not discarded.
    if astate['strengths'] and ex.family in ['Knee Dominant','Hip Hinge','Horizontal Push','Horizontal Pull','Vertical Push','Vertical Pull']: score += 0.8
    # Fatigue gate: avoid high-fatigue/impact choices when readiness is poor.
    if astate['fatigue']>=5: score -= ex.fatigue*1.1 + ex.impact*0.8
    elif astate['fatigue']<=2 and ex.complexity>=4: score += 0.7
    return score

def select_exercises(astate, month, day, n=7):
    a=astate['profile']; phase=phase_for(month)
    pool=[e for e in EX if equipment_ok(e) and sport_ok(e,a) and phase_ok(e,phase)]
    if not pool: pool=[e for e in EX if equipment_ok(e)]
    used=[]; families=[]
    # Stable session architecture with full-body coverage.
    slots=['knee','hinge','push','pull','unilateral','trunk']
    if a['primary'] in ['Speed','Power','Agility','Sports Performance']: slots += ['power']
    else: slots += ['integrated'] if level_num(a['level'])>=3 else ['corrective']
    # Screening is integrated, not allowed to consume the whole session.
    if any(k in a['screening'] for k in ['Anterior Pelvic Tilt','Posterior Pelvic Tilt','Pelvic Hike','Knee Valgus']):
        slots[-1]='corrective'
    chosen=[]
    for slot in slots:
        candidates=[e for e in pool if e.name not in used and e.family in {'Knee Dominant','Hip Hinge','Hip Extension','Unilateral Lower','Frontal Lower','Horizontal Push','Vertical Push','Horizontal Pull','Vertical Pull','Anti-Rotation','Stability','Core Control','Carry','Integrated Neuromuscular','Corrective Hip','Corrective Shoulder','Power','Plyometric','Agility'}]
        if slot=='integrated': candidates=[e for e in candidates if e.complexity>=3]
        if slot=='corrective': candidates=[e for e in candidates if e.family.startswith('Corrective') or 'hip_control' in e.qualities or 'scapular' in e.qualities]
        if not candidates: candidates=pool[:]
        ranked=sorted(candidates,key=lambda e:exercise_score(e,astate,slot,month,set(used),set(families)),reverse=True)
        ex=ranked[0]
        chosen.append(ex); used.append(ex.name); families.append(ex.family)
    return chosen

def dose(ex,a,month):
    primary=a['primary']; phase=phase_for(month)
    if ex.family in ['Power','Plyometric','Agility']:
        reps='3-5 reps' if phase!='Foundation' else '3-4 reps'; sets='3-5'; rest='90-180 s'; tempo='Explosive / controlled landing'
    elif primary=='Strength': sets='3-5'; reps='4-8'; rest='120-180 s'; tempo='Controlled eccentric / explosive intent'
    elif primary=='Hypertrophy': sets='3-4'; reps='8-12'; rest='60-120 s'; tempo='2-0-2'
    elif primary=='Endurance': sets='2-3'; reps='10-15'; rest='45-75 s'; tempo='Controlled'
    else: sets='3-4'; reps='6-10'; rest='75-120 s'; tempo='Controlled / intent'
    if month>=3 and primary=='Strength': reps='3-6'
    return sets,reps,rest,tempo

def load_note(a,month):
    r=a['readiness'];
    if r<=4 or a['pain']>=4: return 'Reduced load: prioritize technique and keep effort submaximal.'
    if r<=6: return 'Conservative load: keep 2-3 reps in reserve and reduce volume if quality drops.'
    if a['primary']=='Strength': return 'Progress load when all sets meet target RPE with stable technique.'
    if a['primary']=='Hypertrophy': return 'Progress load or reps when target RPE is achieved across sets.'
    return 'Progress only when speed, quality and target RPE remain acceptable.'

def build_warmup(astate, exercises, month):
    a=astate['profile']; names=[]; minutes=[]
    # General preparation always first, but low fatigue.
    names += WARMUPS['general'];
    families={e.family for e in exercises}; qualities=set(q for e in exercises for q in e.qualities)
    if any(f in families for f in ['Knee Dominant','Unilateral Lower','Frontal Lower']): names += WARMUPS['knee']
    if any(f in families for f in ['Hip Hinge','Hip Extension']): names += WARMUPS['hinge']
    if any(f in families for f in ['Horizontal Push','Vertical Push']): names += WARMUPS['push']
    if any(f in families for f in ['Horizontal Pull','Vertical Pull']): names += WARMUPS['pull']
    if 'shoulder' in qualities or a['sport'] in ['Swimming','Tennis','Boxing','MMA','Handball']: names += WARMUPS['shoulder']
    if any(q in qualities for q in ['trunk','anti_rotation','stability']): names += WARMUPS['trunk']
    if any(q in qualities for q in ['unilateral','coordination']): names += WARMUPS['unilateral']
    if any(f in families for f in ['Power','Plyometric']): names += WARMUPS['power']
    if any(f in families for f in ['Agility']): names += WARMUPS['agility']
    # Deduplicate while keeping order.
    out=[]; seen=set()
    for n,m in names:
        if n not in seen: out.append((n,m)); seen.add(n)
    # Fatigue-aware cap.
    cap=8 if a['readiness']<=5 else 12
    total=0; final=[]
    for n,m in out:
        if total+m>cap: break
        final.append((n,m)); total+=m
    return final

def metcon(astate, month, day):
    a=astate['profile']; protocols=['EMOM','AMRAP','Intervals','Tabata','Every 90s','Circuit']
    protocol=protocols[(month+day-2)%len(protocols)]
    if a['primary']=='Strength' and month==1: protocol='Intervals'
    sport=a['sport']
    base={
      'Soccer':['Crossover Step to Sprint','Reactive Mirror Shuffle','Lateral Bound to Stick'],
      'Tennis':['Reactive Mirror Shuffle','Lateral Bound to Stick','Medicine Ball Rotational Throw'],
      'Swimming':['Dead Bug','Medicine Ball Scoop Toss','Bodyweight Squat'],
      'Boxing':['Shadow Boxing','Reactive Footwork','Medicine Ball Rotational Throw'],
      'MMA':['Reactive Footwork','Medicine Ball Rotational Throw','Bear Crawl'],
      'Karate':['Reactive Mirror Shuffle','Medicine Ball Rotational Throw','Lateral Bound to Stick'],
      'Basketball':['Reactive Mirror Shuffle','Single-Leg Hop and Stick','Crossover Step to Sprint'],
      'Volleyball':['Lateral Bound to Stick','Single-Leg Hop and Stick','Medicine Ball Scoop Toss'],
      'Handball':['Medicine Ball Rotational Throw','Reactive Mirror Shuffle','Single-Leg Hop and Stick'],
      'General Fitness':['Bodyweight Squat','Mountain Climber','Dead Bug']
    }.get(sport,['Bodyweight Squat','Mountain Climber','Dead Bug'])
    # Hard equipment gate: unknown stations are never emitted. Sport-specific drills are bodyweight.
    allowed=[]
    for s in base:
        match=next((e for e in EX if e.name==s),None)
        if match is not None and equipment_ok(match): allowed.append(s)
    if not allowed:
        allowed=['Bodyweight Squat','Mountain Climber','Dead Bug']
    if protocol=='EMOM': detail='10-20 min | Minute 1: '+allowed[0]+' | Minute 2: '+allowed[min(1,len(allowed)-1)]+' | Minute 3: '+allowed[min(2,len(allowed)-1)]
    elif protocol=='AMRAP': detail='12 min AMRAP | '+', '.join(allowed)
    elif protocol=='Tabata': detail='4 min Tabata | 20s work / 10s rest | '+allowed[0]+' / '+allowed[min(1,len(allowed)-1)]
    elif protocol=='Every 90s': detail='8 rounds every 90s | '+allowed[0]+' + '+allowed[min(1,len(allowed)-1)]
    elif protocol=='Circuit': detail='3-5 rounds | '+', '.join(allowed)+' | 60-90s between rounds'
    else: detail='6-10 rounds | 20-30s work / 40-60s recovery | '+', '.join(allowed)
    return protocol,detail

def generate_program(astate, months=3):
    a=astate['profile']; program=[]
    for m in range(1,months+1):
        for w in range(1,5):
            for d in range(1,max(1,min(a['days'],6))+1):
                exs=select_exercises(astate,m,d)
                warm=build_warmup(astate,exs,m)
                mc=metcon(astate,m,d)
                items=[]
                for ex in exs:
                    sets,reps,rest,tempo=dose(ex,a,m)
                    items.append({'name':ex.name,'family':ex.family,'sets':sets,'reps':reps,'rest':rest,'tempo':tempo,'equipment':', '.join(ex.equipment),'laterality':ex.laterality,'coordination':ex.coordination,'complexity':ex.complexity})
                program.append({'month':m,'week':w,'day':d,'phase':phase_for(m),'warmup':warm,'exercises':items,'metcon':mc,'load_note':load_note(a,m)})
    return program

def update_feedback(feedback):
    if not feedback: return
    # Feedback is retained as part of state. Readiness/RPE are used on next generation.
    last=feedback[-1]
    if last.get('session_rpe',0)>=9: st.session_state.readiness=max(1,st.session_state.readiness-1)
    elif last.get('session_rpe',0)<=6 and last.get('performance_change',0)>=1: st.session_state.readiness=min(10,st.session_state.readiness+1)

def generate():
    state=build_athlete_state(); st.session_state.athlete_state=state; st.session_state.program=generate_program(state,st.session_state.plan_months)

# ---------------- UI ----------------
ACCENT='#38bdf8'
st.markdown(f'''<style>
body {{ background:#07111f; }} .block-container {{ padding-top:1.2rem; }}

        st.markdown(f'<div class="card"><b>Month {m} | Week {w} | Day {d}</b><br>Phase: {s["phase"]}<br>{s["load_note"]}</div>',unsafe_allow_html=True)
        st.subheader('Smart Warm-up')
        st.write(' -> '.join(f'{n} ({mins} min)' for n,mins in s['warmup']))
        st.subheader('Resistance / Integrated Work')
        st.dataframe(pd.DataFrame(s['exercises']),use_container_width=True,hide_index=True)
        st.subheader('Metabolic Conditioning')
        st.write(f'**{s["metcon"][0]}** — {s["metcon"][1]}')
    else: st.info('Generate the program after completing the athlete inputs.')

elif page=='6. Feedback & Reassessment':
    st.header('06 | Feedback -> Reassessment -> Next Plan')
    rpe=st.slider('Session RPE',1,10,7); perf=st.slider('Performance change vs expected',-2,2,0); pain_after=st.slider('Pain after session',0,10,0); notes=st.text_area('Coach notes')
    if st.button('SAVE SESSION FEEDBACK'):
        names=[]; families=[]
        if st.session_state.program:
            names=[e['name'] for e in st.session_state.program if e['month']==1 and e['week']==1 and e['day']==1 for _ in [0]][:7]
            families=[]
        rec={'timestamp':datetime.now().isoformat(timespec='seconds'),'session_rpe':rpe,'performance_change':perf,'pain_after':pain_after,'exercise_names':names,'families':families,'notes':notes}
        st.session_state.feedback.append(rec); update_feedback(st.session_state.feedback); st.session_state.program=None; st.success('Feedback stored. The next generation will use the updated athlete state.')
    if st.session_state.feedback: st.dataframe(pd.DataFrame(st.session_state.feedback),use_container_width=True,hide_index=True)

elif page=='7. Data / Export':
    st.header('07 | Data, Profiles & Export')
    state=build_athlete_state(); payload=json.dumps(state,indent=2,default=str)
    st.download_button('Download Athlete State JSON',payload,'athlete_iq_v8_state.json','application/json')
    if st.session_state.feedback: st.download_button('Download Feedback CSV',pd.DataFrame(st.session_state.feedback).to_csv(index=False),'athlete_iq_v8_feedback.csv','text/csv')
    st.json({'sport':state['profile']['sport'],'position':state['profile']['position'],'goal':state['profile']['primary'],'screening':screen_findings(),'strengths':state['strengths'],'weaknesses':state['weaknesses']})

st.markdown('---')
st.caption('Athlete-IQ v8.0 | Rule-based adaptive coaching software. Screening observations are not diagnoses. The engine is designed as a closed loop: assess -> prioritize -> plan -> prepare -> train -> measure -> adapt.')

.aiq-title {{text-align:center;font-size:2.2rem;font-weight:900;color:{ACCENT};letter-spacing:1px;}}
.aiq-sub {{text-align:center;color:#a855f7;font-weight:700;}}
.card {{background:linear-gradient(135deg,#0d1b2e,#101b30);border:1px solid #223552;border-radius:14px;padding:14px;margin:8px 0;}}
.badge {{display:inline-block;border:1px solid #28405f;border-radius:999px;padding:4px 9px;margin:2px;font-size:.78rem;}}
</style>''',unsafe_allow_html=True)
st.markdown('<div class="aiq-title">ATHLETE-IQ V8</div><div class="aiq-sub">Closed-Loop Whole-Athlete Adaptive Programming Engine</div>',unsafe_allow_html=True)

with st.sidebar:
    st.markdown('## ATHLETE-IQ')
    page=st.radio('Module',['1. Athlete Profile','2. Readiness & Screening','3. Performance Tests','4. Decision Engine','5. Program Generator','6. Feedback & Reassessment','7. Data / Export'])
    st.session_state.plan_months=st.select_slider('Macrocycle Horizon',[1,2,3,4,5,6],value=3)

if page=='1. Athlete Profile':
    st.header('01 | Athlete Profile & Goal Architecture')
    c1,c2,c3=st.columns(3)
    with c1:
        setv('name',st.text_input('Athlete Name',st.session_state.name)); setv('age',st.number_input('Age',12,80,st.session_state.age)); setv('height',st.number_input('Height (cm)',120.0,230.0,st.session_state.height)); setv('weight',st.number_input('Weight (kg)',30.0,250.0,st.session_state.weight))
    with c2:
        sport=st.selectbox('Sport / Discipline',list(SPORTS),index=list(SPORTS).index(st.session_state.sport)); setv('sport',sport)
        pos=st.selectbox('Position / Specialization',SPORTS[sport],index=SPORTS[sport].index(st.session_state.position) if st.session_state.position in SPORTS[sport] else 0); setv('position',pos)
        level=st.selectbox('Training Level',['Beginner','Intermediate','Advanced','Elite'],index=['Beginner','Intermediate','Advanced','Elite'].index(st.session_state.level)); setv('level',level)
    with c3:
        primary=st.selectbox('Primary Goal',list(GOAL_WEIGHTS),index=list(GOAL_WEIGHTS).index(st.session_state.primary)); setv('primary',primary)
        secondary=st.multiselect('Secondary Development Targets',['Strength','Power','Speed','Agility','Hypertrophy','Endurance','Mobility','Stability','Neuromuscular Coordination'],default=st.session_state.secondary); setv('secondary',secondary)
        phase=st.selectbox('Training Phase',['Foundation','Development','Performance','Off-Season','In-Season','Transition'],index=['Foundation','Development','Performance','Off-Season','In-Season','Transition'].index(st.session_state.phase)); setv('phase',phase)
    setv('days',st.slider('Training days / week',1,6,st.session_state.days))
    eq=st.multiselect('Available Equipment (hard filter)',EQUIPMENT,default=st.session_state.equipment); setv('equipment',eq)
    st.info('V8 principle: goals, sport, position, screening, performance, equipment, history and feedback all feed one central selection engine.')

elif page=='2. Readiness & Screening':
    st.header('02 | Readiness, Movement Screening & Observations')
    setv('readiness',st.slider('Readiness today',1,10,st.session_state.readiness)); setv('pain',st.slider('Pain / discomfort today',0,10,st.session_state.pain)); setv('training_load',st.slider('Recent training load',1,10,st.session_state.training_load))
    st.subheader('Postural / movement observations')
    opts=['Anterior Pelvic Tilt','Posterior Pelvic Tilt','Pelvic Hike','Scapular Winging','Forward Head','Knee Valgus']
    for o in opts:
        st.session_state.screening[o]=st.checkbox(o,value=st.session_state.screening.get(o,False))
    st.subheader('SFMA-style movement observations')
    sfma=['Deep Squat','Hurdle Step','Inline Lunge','Shoulder Mobility','Active Straight Leg Raise','Trunk Stability Push-Up','Rotary Stability']
    sfma_sel=st.multiselect('Select movements requiring attention',sfma,default=st.session_state.screening.get('SFMA',[])); st.session_state.screening['SFMA']=sfma_sel
    st.caption('These observations inform training priorities and exercise modifications; they are not a medical diagnosis.')

elif page=='3. Performance Tests':
    st.header('03 | Performance Testing')
    tests=['Squat Strength','Bench Strength','Pulling Strength','Jump Power','Sprint Speed','Change of Direction','Aerobic Capacity','Upper Body Power','Unilateral Control','Reaction']
    for t in tests:
        key=t.lower().replace(' ','_'); st.session_state.tests[key]=st.slider(t+' | relative rating',1,10,int(st.session_state.tests.get(key,5)))
    st.info('Low ratings become development priorities. High ratings are maintained and can still progress; they are never discarded.')

elif page=='4. Decision Engine':
    st.header('04 | Whole-Athlete Decision Engine')
    state=build_athlete_state(); st.session_state.athlete_state=state
    a=state['profile']
    c1,c2,c3=st.columns(3)
    c1.metric('Sport / Position',f"{a['sport']} / {a['position']}"); c2.metric('Primary Goal',a['primary']); c3.metric('Readiness',f"{a['readiness']}/10")
    st.subheader('Priority signals')
    top=sorted(state['needs'].items(),key=lambda x:x[1],reverse=True)[:12]
    st.dataframe(pd.DataFrame(top,columns=['Quality / Need','Priority Score']),use_container_width=True,hide_index=True)
    st.subheader('Whole-athlete balance')
    st.write('Correct issues + develop weaknesses + progress strengths + satisfy sport demands + manage fatigue.')
    st.write('**Weaknesses:**', ', '.join(state['weaknesses']) if state['weaknesses'] else 'None flagged by current performance ratings')
    st.write('**Strengths to maintain/progress:**', ', '.join(state['strengths']) if state['strengths'] else 'No high ratings recorded')
    st.write('**Screening observations:**', ', '.join(screen_findings()) if screen_findings() else 'None')

elif page=='5. Program Generator':
    st.header('05 | Adaptive Program Generator')
    if st.button('GENERATE / REGENERATE V8 PROGRAM',type='primary'): generate(); st.success('Program generated from the current athlete state.')
    if st.session_state.program:
        prog=st.session_state.program
        m=st.selectbox('Month',sorted(set(x['month'] for x in prog))); w=st.selectbox('Week',[1,2,3,4]); d=st.selectbox('Day',sorted(set(x['day'] for x in prog if x['month']==m)))
        s=next(x for x in prog if x['month']==m and x['week']==w and x['day']==d)






