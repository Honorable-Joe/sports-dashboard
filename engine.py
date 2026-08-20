from exercises import EX
from screening import metrics
SPORT={'Soccer':{'speed','agility','coordination','power','sport','anaerobic'},'Swimming':{'upper','aerobic','coordination','sport'},'Tennis':{'agility','speed','coordination','power','unilateral','sport'},'Boxing':{'speed','coordination','upper','anaerobic','sport'},'MMA':{'coordination','power','anaerobic','agility','upper','lower','sport'},'Karate':{'speed','agility','coordination','power','sport'},'Basketball':{'power','agility','speed','coordination'},'Handball':{'power','agility','speed','coordination','upper'},'Volleyball':{'power','agility','speed','coordination','plyometric'},'Wrestling':{'strength','power','coordination','anaerobic','agility'},'Bodybuilding':{'strength','hypertrophy','upper','lower'},'General Fitness':{'strength','aerobic','mobility','stability'}}
POS={'Goalkeeper':{'agility','power','coordination'},'Winger':{'speed','agility','anaerobic'},'Striker':{'speed','power'},'Center Back':{'strength','power'},'Full Back':{'speed','agility'},'Freestyle':{'upper','aerobic'},'Backstroke':{'upper','aerobic'},'Breaststroke':{'lower','mobility'},'Butterfly':{'upper','power'},'Individual Medley':{'upper','lower','aerobic'},'Singles':{'agility','speed','unilateral'},'Doubles':{'coordination','agility'},'Kumite':{'speed','agility','coordination'},'Kata':{'coordination','mobility','stability'},'Kumite + Kata':{'speed','coordination','mobility'},'Off-Season':{'hypertrophy','strength'},'Striking':{'speed','power','agility'},'Grappling':{'strength','coordination','anaerobic'}}
GOAL={'Overall Development':{'strength','power','speed','agility','mobility','stability','coordination','aerobic','anaerobic'},'Strength':{'strength'},'Max Strength':{'strength'},'Hypertrophy':{'strength','upper','lower'},'Power':{'power','plyometric'},'Speed':{'speed','agility'},'Agility':{'agility','coordination'},'Aerobic Capacity':{'aerobic','metcon'},'Anaerobic Capacity':{'anaerobic','metcon'},'Sport Performance':{'sport','coordination','power','speed'},'Fat Loss':{'aerobic','metcon','strength'},'General Fitness':{'strength','aerobic','mobility','stability'}}
SECTION={'corrective':{'corrective','activation','mobility','stability'},'strength':{'strength','hypertrophy'},'power':{'power','plyometric'},'agility':{'agility','speed'},'coordination':{'coordination','neuromuscular'},'sport':{'sport'},'metcon':{'metcon','anaerobic','aerobic'}}
LEVEL={'General':1,'Intermediate':2,'Advanced':3,'Elite':4}
def readiness(s):
 m=metrics(s); r=.4*m['movement']+.3*m['stability']+.3*m['neuromuscular']; return max(25,min(100,round(r))),m
def blocked(s):
 b=set(); inj=s.get('injuries',[])
 if 'Knee' in inj:b|={'Depth Drop to Stick','Lateral Bound and Stick','Pogo Jump'}
 if 'Ankle' in inj:b|={'Lateral Bound and Stick','Pogo Jump'}
 if 'Low Back' in inj:b|={'Barbell Back Squat','Romanian Deadlift','Trap Bar Deadlift'}
 if 'Shoulder' in inj:b|={'Overhead Press','Single Arm Dumbbell Press','Bench Press'}
 return b
def sport_ok(s,n):
 sp=s['sport']; q=n.lower()
 if sp not in {'Boxing','MMA'} and ('shadow boxing' in q):return False
 if sp not in {'Karate'} and ('kumite' in q or 'shadow kick' in q):return False
 if sp=='Swimming' and any(x in q for x in ['forehand','backhand','shuttle sprint','reactive cone']):return False
 return True
def choose(s,section,n,used,m,d):
 r,_=readiness(s); maxc=5 if LEVEL.get(s.get('level','General'),1)>=4 and r>=80 else 4 if LEVEL.get(s.get('level','General'),1)>=3 and r>=65 else 3
 desired=set(GOAL.get(s['primary'],()))|SPORT.get(s['sport'],set())
 for x in s.get('secondary',[]):desired|=GOAL.get(x,set())
 for x in s.get('positions',[]):desired|=POS.get(x,set())
 out=[]; used_patterns=set(); scores=[]
 for name,e in EX.items():
  if name in used or name in blocked(s) or e['equipment'] not in s.get('equipment',[]) or e['complexity']>maxc or not e['systems']&SECTION.get(section,set()) or not sport_ok(s,name):continue
  sc=3*len(e['systems']&desired)+4*len(e['systems']&SECTION[section])-8*(name in used)-4*(e['pattern'] in used_patterns)
  # screening creates corrective AND performance pressure, not an either/or decision
  if any('Pelvic' in x for x in s.get('posture',[])) and e['pattern'] in {'hip_extension','hinge','anti_extension'}:sc+=4
  if any('Scapular' in x or 'Shoulder' in x for x in s.get('posture',[])) and e['systems']&{'upper','stability'}:sc+=3
  if readiness(s)[1]['movement']<70 and e['systems']&{'corrective','mobility','stability'}:sc+=4
  if readiness(s)[1]['neuromuscular']<70 and e['systems']&{'coordination','neuromuscular','unilateral'}:sc+=4
  sc+=(sum(ord(c) for c in name)+m*17+d*7)%11*.03
  scores.append((sc,name))
 scores.sort(reverse=True)
 for _,name in scores:
  if len(out)>=n:break
  out.append(name);used_patterns.add(EX[name]['pattern'])
 return out
def metcon(s,m,w,used):
 formats=['Tabata','AMRAP','EMOM','Intervals']; fmt=formats[(m+w-2)%4]
 pools={'Tabata':['Battle Rope Intervals','Burpee','Bike Sprint'],'AMRAP':['Shuttle Sprint','Burpee','Bike Sprint'],'EMOM':['Bike Sprint','Row Intervals','Battle Rope Intervals'],'Intervals':['Bike Sprint','Row Intervals','SkiErg Intervals','Shuttle Sprint']}
 vals=[x for x in pools[fmt] if x in EX and EX[x]['equipment'] in s.get('equipment',[]) and sport_ok(s,x) and x not in used]
 return fmt,vals[:3] or [x for x in pools[fmt] if x in EX and EX[x]['equipment'] in s.get('equipment',[])][:3]
def generate(s):
 r,mx=readiness(s); months=[]
 for month in range(1,s.get('months',3)+1):
  weeks=[]
  for week in range(1,5):
   days=[]
   for day in range(1,s.get('days',4)+1):
    used=[]; sections={}
    for sec,n in [('corrective',2),('strength',4),('power',2),('agility',2),('coordination',2),('sport',2)]:
     sections[sec]=choose(s,sec,n,used,month,day);used+=sections[sec]
    fmt,mc=metcon(s,month,week,used);sections['metcon']=mc
    days.append({'day':day,'sections':sections,'metcon_format':fmt,'load':load(s['primary'],month),'warmup':warmup(sections)})
   weeks.append(days)
  months.append({'month':month,'phase':['Accumulation','Intensification','Realization'][min(month-1,2)],'weeks':weeks})
 return {'readiness':r,'metrics':mx,'months':months}
def load(goal,m):
 if goal in {'Strength','Max Strength'}:return [('3-4x6-8','75-82%'),('4-5x4-6','80-88%'),('3-5x2-5','85-92%')][min(m-1,2)]
 if goal=='Hypertrophy':return [('3-4x8-12','65-78%'),('3-4x6-10','70-82%'),('3-4x6-8','72-85%')][min(m-1,2)]
 return [('3-4x6-10','RPE 6-8'),('3-5x4-8','RPE 7-8'),('2-4x3-6','high quality')][min(m-1,2)]
def warmup(sections):
 names=sum(sections.values(),[]); out=[]
 if any(EX[x]['pattern'] in {'squat','lunge'} for x in names):out.append('Dynamic squat/lunge preparation')
 if any(EX[x]['pattern'] in {'hinge','hip_extension'} for x in names):out.append('Hip hinge activation')
 if any('upper' in EX[x]['systems'] or 'horizontal_push'==EX[x]['pattern'] or 'vertical_push'==EX[x]['pattern'] for x in names):out.append('Scapular + shoulder activation')
 if any(EX[x]['systems']&{'power','plyometric','speed','agility'} for x in names):out.append('Low-volume neural potentiation')
 return out or ['General RAMP preparation']
