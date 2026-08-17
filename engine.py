from exercises import EX
import math, random

META = {x[0]: {'cats':x[1], 'equipment':x[2], 'pattern':x[3], 'plane':x[4], 'level':x[5], 'purpose':x[6]} for x in EX}

SPORT_CATS = {
 'Soccer': ['sport','speed','agility','coordination','power','anaerobic'],
 'Swimming': ['sport','upper','power','coordination','aerobic'],
 'Boxing': ['sport','upper','coordination','speed','anaerobic','agility'],
 'MMA': ['sport','coordination','power','anaerobic','agility','upper','lower'],
 'Karate': ['sport','coordination','speed','agility','power','anaerobic'],
 'Tennis': ['sport','agility','coordination','speed','power','unilateral'],
 'Basketball': ['sport','power','agility','speed','coordination','anaerobic'],
 'Handball': ['sport','power','agility','speed','coordination','upper'],
 'Bodybuilding': ['strength','hypertrophy','upper','lower'],
 'General Fitness': ['strength','aerobic','mobility','stability']
}
POS_BIAS = {
 'Goalkeeper':['lateral','agility','power','coordination'], 'Winger':['speed','agility','anaerobic'], 'Striker':['power','speed'],
 'Center Back':['strength','power','coordination'], 'Full Back':['speed','agility','anaerobic'], 'Defensive Midfielder':['strength','aerobic','coordination'],
 'Central Midfielder':['aerobic','coordination','agility'], 'Attacking Midfielder':['speed','power','coordination'],
 'Freestyle':['upper','aerobic'], 'Backstroke':['upper','aerobic'], 'Breaststroke':['lower','mobility'], 'Butterfly':['upper','power'], 'Individual Medley':['upper','lower','aerobic'],
 'Kumite':['speed','agility','coordination'], 'Kata':['coordination','mobility','stability'], 'Kumite + Kata':['speed','coordination','mobility'],
 'Singles':['agility','speed','unilateral'], 'Doubles':['coordination','agility'], 'Off-season':['hypertrophy','strength'], 'Pre-contest':['strength','aerobic']
}
GOAL_CATS = {
 'Strength':['strength'], 'Max Strength':['strength'], 'Hypertrophy':['strength','upper','lower'], 'Power':['power','plyometric'], 'Speed':['speed','agility'],
 'Agility':['agility','coordination'], 'Aerobic Capacity':['aerobic','metcon'], 'Anaerobic Capacity':['anaerobic','metcon'], 'Sport Performance':['sport','coordination'],
 'Fat Loss':['aerobic','metcon','strength'], 'General Fitness':['strength','aerobic','mobility','stability'], 'Overall Development':['strength','power','speed','agility','mobility','stability','coordination']
}
POSTURE = {
 'Anterior Pelvic Tilt':['Dead Bug','Glute Bridge','Single Leg RDL'], 'Rounded Shoulders':['Band Face Pull','Seated Cable Row','Incline Dumbbell Press'],
 'Forward Head':['Band Face Pull','Seated Cable Row'], 'Knee Valgus':['Lateral Lunge','Single Leg RDL','Side Plank'],
 'Limited Ankle Dorsiflexion':['Ankle Dorsiflexion Rocker','Goblet Squat'], 'Limited T-Spine Rotation':['T-Spine Windmill','Half Kneeling Pallof Press'],
 'Poor Hip Mobility':['90/90 Hip Flow','Lateral Lunge'], 'Poor Scapular Control':['Band Face Pull','Single Arm Dumbbell Row']
}
INJURY_BLOCK = {'Knee':['Depth Drop to Stick','Repeated Sprint 20m'], 'Ankle':['Lateral Bound and Stick','Pogo Jumps'], 'Hip':['Deep Squat'], 'Low Back':['Barbell Back Squat'], 'Shoulder':['Overhead Press','Push Press','Dip'], 'Elbow/Wrist':['Dip'], 'Groin/Hamstring':['Repeated Sprint 20m']}


def score_ex(name, profile, section, used):
    m=META[name]; score=0
    cats=m['cats']
    desired=set(GOAL_CATS.get(profile['primary'],[])+sum((GOAL_CATS.get(g,[]) for g in profile['secondary']),[])+SPORT_CATS.get(profile['sport'],[]))
    score += 3*len(set(cats)&desired)
    for p in profile['positions']:
        score += 1.4*len(set(cats)&set(POS_BIAS.get(p,[])))
    # Screening findings and performance metrics influence exercise priority, not only corrective work.
    if any(issue in profile.get('posture', []) for issue in ['Anterior Pelvic Tilt','Poor Hip Mobility','Knee Valgus']):
        if 'lower' in cats or 'core' in cats or 'stability' in cats: score += 1.5
    if any(issue in profile.get('posture', []) for issue in ['Rounded Shoulders','Forward Head','Poor Scapular Control']):
        if 'upper' in cats or 'pull' in cats: score += 1.5
    if profile.get('cmj', 45) < 40 and ('power' in cats or 'plyometric' in cats): score += 2.5
    if profile.get('sprint', 2.0) > 2.1 and ('speed' in cats or 'agility' in cats): score += 2.0
    if profile.get('change_dir', 7) < 6 and ('agility' in cats or 'coordination' in cats): score += 2.0
    if section=='strength' and 'strength' in cats: score+=5
    if section=='power' and ('power' in cats or 'plyometric' in cats): score+=5
    if section=='agility' and 'agility' in cats: score+=5
    if section=='coordination' and 'coordination' in cats: score+=6
    if section=='sport' and 'sport' in cats: score+=7
    if section=='metcon' and ('metcon' in cats or 'anaerobic' in cats or 'aerobic' in cats): score+=6
    if section=='corrective' and ('corrective' in cats or 'activation' in cats): score+=7
    if section=='warmup' and ('mobility' in cats or 'activation' in cats or 'corrective' in cats): score+=5
    if m['equipment'] in profile['equipment']: score+=4
    else: return -999
    score -= 10 * used.count(name)
    for h in profile['history']:
        if h.lower()==name.lower(): score-=24
    # full-body balance: upper/lower sections receive explicit preference
    if section=='strength' and profile['sport'] in ['Soccer','Basketball','Handball','Tennis','MMA','Karate']:
        if 'upper' in cats: score+=2
    # avoid excessive repetition of a pattern/plane
    return score


def choose(profile, section, n, used, exclude_names=None):
    exclude=set(exclude_names or [])
    allowed = {
        'strength': {'strength'},
        'power': {'power','plyometric'},
        'agility': {'agility','speed'},
        'coordination': {'coordination'},
        'sport': {'sport'},
        'corrective': {'corrective','activation'},
        'warmup': {'mobility','activation','corrective'},
        'metcon': {'metcon','anaerobic','aerobic'},
        'recovery': {'mobility','stability','corrective'}
    }.get(section, set())
    candidates=[]
    blocked=set()
    for injury in profile.get('injury', []):
        if injury != 'None':
            blocked.update(INJURY_BLOCK.get(injury, []))
    for x in EX:
        cats=set(x[1])
        if x[0] in exclude or x[0] in blocked or not (cats & allowed):
            continue
        # Combat skills never leak into non-combat sports, even when they share coordination/anaerobic tags.
        combat_names={'Shadow Boxing','Sprawl to Stand','Shadow Kick Combination','Kumite Reaction Step'}
        if x[0] in combat_names and profile['sport'] not in {'Boxing','MMA','Karate'}:
            continue
        # Sport-specific skill pool: never let combat drills leak into swimming, etc.
        if section=='sport':
            sport_pool={
                'Soccer': {'Soccer Ball Reactive Touch','Goalkeeper Lateral Dive Pattern','Winger Curved Sprint'},
                'Swimming': {'Swimming Band Pull Pattern','Streamline Squat Jump'},
                'Boxing': {'Shadow Boxing','Reaction Ball Catch'},
                'MMA': {'Shadow Boxing','Sprawl to Stand','Reaction Ball Catch'},
                'Karate': {'Shadow Kick Combination','Kumite Reaction Step','Reaction Ball Catch'},
                'Tennis': {'Tennis Split Step + Crossover','Reaction Ball Catch'},
                'Basketball': {'Reaction Ball Catch','Mirror Footwork'},
                'Handball': {'Reaction Ball Catch','Mirror Footwork'},
                'Bodybuilding': set(), 'General Fitness': set()
            }.get(profile['sport'], set())
            if x[0] not in sport_pool:
                continue
        candidates.append(x[0])
    ranked=sorted(((score_ex(x,profile,section,used),x) for x in candidates), reverse=True)
    out=[]
    used_patterns=set(); used_planes=set()
    for sc,name in ranked:
        if sc < -100: continue
        m=META[name]
        # Encourage movement diversity inside a session.
        diversity = (m['pattern'] not in used_patterns) + (m['plane'] not in used_planes)
        if out and diversity==0 and len(out)<n: continue
        out.append(name); used_patterns.add(m['pattern']); used_planes.add(m['plane'])
        if len(out)>=n: break
    return out


def prescription(name, section, month, week, day, profile):
    m=META[name]
    if section=='warmup': sets='2 rounds x 6-10 reps / 20-30 sec'; tempo='Controlled'; rest='20 sec';
    elif section=='corrective': sets='2-3 sets x 8-12'; tempo='2-1-2-0'; rest='30-45 sec'
    elif section=='strength':
        base = 8 if month==1 else 6 if month==2 else 4 if month>=3 else 8
        sets=f'3-4 sets x {base} reps'; tempo='Controlled'; rest='90-150 sec'
    elif section=='power': sets='3-5 sets x 2-5 reps'; tempo='Explosive'; rest='120-180 sec'
    elif section in ['agility','coordination','sport']: sets='3-5 sets x 3-6 reps / 10-20 sec'; tempo='Fast / quality'; rest='45-90 sec'
    elif section=='metcon': sets='3-5 rounds'; tempo='Work / recovery'; rest='60-120 sec'
    else: sets='5-10 min'; tempo='Easy'; rest='As needed'
    return {'name':name,'sets':sets,'tempo':tempo,'rest':rest,'plane':m['plane'],'pattern':m['pattern'],'equipment':m['equipment'],'purpose':m['purpose']}


def metcon_for(profile, month, week, day, used):
    formats=['EMOM','AMRAP','TABATA','Intervals','Chipper','Tempo Circuit']
    fmt=formats[((month-1)*4+(week-1)*1+(day-1)) % len(formats)]
    if profile['sport'] in ['Swimming']:
        options=['Bike Sprint','Row Intervals','Battle Rope Intervals','Burpee']
    elif profile['sport'] in ['Boxing','MMA','Karate']:
        options=['Shadow Boxing','Battle Rope Intervals','Bike Sprint','Burpee']
    elif profile['sport']=='Soccer':
        options=['Bike Sprint','Repeated Sprint 20m','Burpee','Battle Rope Intervals']
    else:
        options=['Bike Sprint','Row Intervals','Battle Rope Intervals','Burpee']
    if 'Sled' not in profile['equipment']:
        options=[x for x in options if META[x]['equipment']!='Sled']
    available=[x for x in options if META[x]['equipment'] in profile['equipment'] and x not in used]
    if not available: available=[x for x in options if META[x]['equipment'] in profile['equipment']]
    chosen=available[(month+week+day-2)%len(available)]
    m=META[chosen]
    if fmt=='EMOM': sets='10 min EMOM: 30 sec work / 30 sec easy'
    elif fmt=='AMRAP': sets='12 min AMRAP: quality continuous rounds'
    elif fmt=='TABATA': sets='4 min Tabata: 20 sec work / 10 sec recovery'
    elif fmt=='Intervals': sets='4 rounds: 30 sec work / 30 sec recovery'
    elif fmt=='Chipper': sets='For time, controlled pacing, 2-3 rounds'
    else: sets='6 rounds: 40 sec work / 20 sec transition'
    return {'name':chosen+' | '+fmt,'sets':sets,'tempo':'RPE 6-8','rest':'60-90 sec between rounds','plane':m['plane'],'pattern':m['pattern'],'equipment':m['equipment'],'purpose':f'{profile["sport"]} conditioning using {fmt} format'}


def generate_plan(profile):
    readiness=round(50 + profile['stability']*3 + profile['mobility']*2 + profile['coordination']*2 - (15 if profile['injury']!=['None'] else 0))
    readiness=max(20,min(100,readiness))
    focus=profile['primary'] if profile['primary']!='Overall Development' else 'Balanced development'
    tags=[f'Sport: {profile["sport"]}',f'Position: {", ".join(profile["positions"])}',f'Primary: {profile["primary"]}',f'Equipment: {len(profile["equipment"])} types']
    if profile['posture']: tags.append('Correct posture findings')
    if profile['injury']!=['None']: tags.append('Protect current limitations')
    if profile['secondary']: tags.append('Secondary goals included')
    months=[]
    global_used=[]
    for mi in range(1,profile['months']+1):
        weeks=[]
        phase=['Accumulation','Intensification','Performance'][min(mi-1,2)]
        for wi in range(1,5):
            days=[]
            for di in range(1,profile['days_per_week']+1):
                # Training-history rotation: use month/week/day in deterministic seed and penalize used.
                used=[]
                # corrective priorities from screening, but rotate multiple solutions
                corr_names=[]
                for issue in profile['posture']:
                    corr_names += POSTURE.get(issue,[])
                corr_names=[x for x in corr_names if x in META and META[x]['equipment'] in profile['equipment']]
                corr=[]
                for nm in corr_names:
                    if nm not in global_used and nm not in corr: corr.append(nm)
                if not corr: corr=choose(profile,'corrective',1,global_used)
                corr=corr[:2]
                used += corr
                strength=choose(profile,'strength',4,global_used+used)
                # alternate upper/lower emphasis by day, while keeping full-body coverage across week
                if di%2==1:
                    strength=sorted(strength,key=lambda x: ('upper' not in META[x]['cats'], x))
                else:
                    strength=sorted(strength,key=lambda x: ('lower' not in META[x]['cats'], x))
                used += strength
                power=choose(profile,'power',2,global_used+used); used+=power
                agility=choose(profile,'agility',2,global_used+used); used+=agility
                coord=choose(profile,'coordination',1,global_used+used); used+=coord
                sport=choose(profile,'sport',2,global_used+used); used+=sport
                # warmup is derived from actual selected session demands
                warm_candidates=[]
                demands=set()
                for nm in strength+power+agility+sport:
                    demands.update(META[nm]['cats'])
                if 'upper' in demands: warm_candidates += ['Band Face Pull','Swimming Band Pull Pattern']
                if 'lower' in demands: warm_candidates += ['Ankle Dorsiflexion Rocker','90/90 Hip Flow']
                if 'rotation' in demands or profile['sport'] in ['Tennis','Boxing','MMA','Karate']: warm_candidates += ['T-Spine Windmill']
                if not warm_candidates: warm_candidates=['90/90 Hip Flow','Ankle Dorsiflexion Rocker']
                warm=[x for x in warm_candidates if x in META and META[x]['equipment'] in profile['equipment']]
                warm=list(dict.fromkeys(warm))[:3]
                used += warm
                met=metcon_for(profile,mi,wi,di,global_used+used); used.append(met['name'].split(' | ')[0])
                # recovery responds to training load
                rec=['90/90 Hip Flow','T-Spine Windmill'] if profile['mobility']<7 else ['Dead Bug','Side Plank']
                rec=[x for x in rec if META[x]['equipment'] in profile['equipment']][:2]
                energy='High' if profile['level'] in ['Advanced','Elite'] and readiness>=70 else 'Moderate'
                theme=['Strength Base','Power + Skill','Speed / Agility','Capacity'][ (di-1)%4 ]
                reasons=[f'Goal weighting prioritizes {profile["primary"]}.',f'{profile["sport"]} and {", ".join(profile["positions"])} shape sport-specific demands.', 'Exercise history penalty reduces repeated movements across the plan.']
                if profile['posture']: reasons.append('Corrective choices address: '+', '.join(profile['posture'])+'.')
                if profile['injury']!=['None']: reasons.append('Current limitations are used as exercise exclusion constraints.')
                session={'theme':theme,'phase':phase,'rpe':7+min(2,mi-1),'energy':energy,'emphasis':profile['primary'],
                         'warmup':[prescription(x,'warmup',mi,wi,di,profile) for x in warm],
                         'corrective':[prescription(x,'corrective',mi,wi,di,profile) for x in corr],
                         'strength':[prescription(x,'strength',mi,wi,di,profile) for x in strength],
                         'power':[prescription(x,'power',mi,wi,di,profile) for x in power],
                         'agility':[prescription(x,'agility',mi,wi,di,profile) for x in agility],
                         'coordination':[prescription(x,'coordination',mi,wi,di,profile) for x in coord],
                         'sport':[prescription(x,'sport',mi,wi,di,profile) for x in sport],
                         'metcon':[met], 'recovery':[prescription(x,'recovery',mi,wi,di,profile) for x in rec], 'reasons':reasons}
                days.append(session)
                global_used += [x for x in used if ' | ' not in x]
            weeks.append({'week':wi,'days':days})
        months.append({'month':mi,'phase':phase,'weeks':weeks})
    return {'readiness':readiness,'focus':focus,'decision_tags':tags,'metcon_rotation':'EMOM / AMRAP / TABATA / Intervals','months':months}
