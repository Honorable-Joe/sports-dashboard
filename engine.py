from exercises import META
from screening import BLOCK,priorities
from periodization import phase,load
SPORT={"Soccer":{"speed","agility","coordination","power","sport","anaerobic"},"Swimming":{"upper","aerobic","coordination","sport"},"Tennis":{"agility","speed","coordination","power","unilateral","sport"},"Boxing":{"speed","coordination","upper","anaerobic","sport"},"MMA":{"coordination","power","anaerobic","agility","upper","lower","sport"},"Karate":{"speed","agility","coordination","power","sport"},"Basketball":{"power","agility","speed","coordination","sport"},"Handball":{"power","agility","speed","coordination","upper","sport"},"Bodybuilding":{"strength","hypertrophy","upper","lower"},"General Fitness":{"strength","aerobic","mobility","stability"}}
POS={"Goalkeeper":{"lateral","agility","power","coordination"},"Winger":{"speed","agility","anaerobic"},"Striker":{"power","speed"},"Center Back":{"strength","power"},"Full Back":{"speed","agility"},"Defensive Midfielder":{"strength","coordination"},"Central Midfielder":{"aerobic","coordination","agility"},"Attacking Midfielder":{"speed","power"},"Freestyle":{"upper","aerobic"},"Backstroke":{"upper","aerobic"},"Breaststroke":{"lower","mobility"},"Butterfly":{"upper","power"},"Individual Medley":{"upper","lower","aerobic"},"Singles":{"agility","speed","unilateral"},"Doubles":{"coordination","agility"},"Kumite":{"speed","agility","coordination"},"Kata":{"coordination","mobility","stability"},"Kumite + Kata":{"speed","coordination","mobility"},"Off-Season":{"hypertrophy","strength"},"Pre-Contest":{"strength","aerobic"}}
GOAL={"Overall Development":{"strength","power","speed","agility","mobility","stability","coordination","aerobic","anaerobic"},"Strength":{"strength"},"Max Strength":{"strength"},"Hypertrophy":{"strength","upper","lower"},"Power":{"power","plyometric"},"Speed":{"speed","agility"},"Agility":{"agility","coordination"},"Aerobic Capacity":{"aerobic","metcon"},"Anaerobic Capacity":{"anaerobic","metcon"},"Sport Performance":{"sport","coordination","power","speed"},"Fat Loss":{"aerobic","metcon","strength"},"General Fitness":{"strength","aerobic","mobility","stability"}}
SEC={"strength":{"strength"},"corrective":{"corrective","activation","mobility","stability"},"power":{"power","plyometric"},"agility":{"agility","speed"},"coordination":{"coordination","neuromuscular"},"sport":{"sport"},"recovery":{"mobility","stability","corrective"}}
def readiness(p):
    r=78+(p.get("mobility",7)-7)*2+(p.get("stability",7)-7)*3+(p.get("coordination",7)-7)*2
    if p.get("injuries") and p["injuries"]!=["None"]: r-=12
    return max(30,min(100,round(r)))
def blocked(p):
    b=set()
    for i in p.get("injuries",[]): b|=BLOCK.get(i,set())
    return b
def score(n,p,s,used,m,d):
    M=META[n]; c=M["cats"]; desired=GOAL.get(p["primary"],set())|SPORT.get(p["sport"],set())
    for g in p.get("secondary",[]): desired|=GOAL.get(g,set())
    for pos in p.get("positions",[]): desired|=POS.get(pos,set())
    x=3*len(c&desired)+5*len(c&SEC.get(s,set()))
    f=p.get("posture_findings",[])
    if any("Pelvic" in q or "Hip" in q for q in f) and c&{"core","stability","lower","hinge"}: x+=2.2
    if any("Scapular" in q or "Shoulder" in q for q in f) and c&{"upper","pull","stability"}: x+=2.2
    if any("Knee" in q for q in f) and c&{"unilateral","stability","lower"}: x+=2
    if p.get("cmj",45)<40 and c&{"power","plyometric"}: x+=2.5
    if p.get("sprint10",1.9)>2.1 and c&{"speed","agility"}: x+=2.5
    if p.get("cod",2.4)>3 and c&{"agility","coordination"}: x+=1.5
    if M["equipment"] not in p["equipment"]: return -999
    x-=used.count(n)*18
    if n in p.get("history",[]): x-=30
    if M["level"]=="Elite" and p.get("level") in {"Elite","Advanced"}: x+=1.5
    x+=((hash(n)+m*19+d*11)%7)*.15
    return x
def choose(p,s,n,used,m,d):
    allowed=SEC[s]; blocked_names=blocked(p); combat={"Shadow Boxing","Sprawl to Stand","Kumite Reaction Step","Shadow Kick Combination"}
    pool=[]
    for name,M in META.items():
        if name in blocked_names or M["equipment"] not in p["equipment"] or not M["cats"]&allowed: continue
        if name in combat and p["sport"] not in {"Boxing","MMA","Karate"}: continue
        if s=="sport":
            pools={"Soccer":{"Soccer Ball Reactive Touch","Goalkeeper Lateral Dive Pattern","Winger Curved Sprint"},"Swimming":{"Swimming Band Pull Pattern","Streamline Squat Jump"},"Tennis":{"Tennis Split Step + Crossover","Medicine Ball Forehand Throw","Medicine Ball Backhand Throw"},"Boxing":{"Shadow Boxing","Reaction Ball Catch"},"MMA":{"Shadow Boxing","Sprawl to Stand","Reaction Ball Catch"},"Karate":{"Kumite Reaction Step","Shadow Kick Combination","Reaction Ball Catch"},"Basketball":{"Mirror Footwork","Reaction Ball Catch"},"Handball":{"Mirror Footwork","Reaction Ball Catch"},"Bodybuilding":set(),"General Fitness":set()}
            if name not in pools.get(p["sport"],set()): continue
        pool.append((score(name,p,s,used,m,d),name))
    pool.sort(reverse=True); out=[]; pats=set(); planes=set()
    for _,name in pool:
        M=META[name]
        if out and M["pattern"] in pats and M["plane"] in planes: continue
        out.append(name); pats.add(M["pattern"]); planes.add(M["plane"])
        if len(out)>=n: break
    return out
def pres(n,s,m,p):
    M=META[n]
    if s=="strength": sets,reps,intensity=load(m,p["primary"]); tempo="2-1-2-0" if m==1 else "2-0-X-0" if m==2 else "X-0-X-0"; rest="90-150 sec"
    elif s=="corrective": sets,reps,intensity="2-3 sets","8-12 reps","RPE 5-7";tempo="controlled";rest="30-45 sec"
    elif s=="power": sets,reps,intensity="3-5 sets","2-5 reps","max quality";tempo="explosive";rest="120-180 sec"
    elif s in {"agility","coordination","sport"}: sets,reps,intensity="3-5 sets","3-6 reps / 10-20 sec","high quality";tempo="fast";rest="45-90 sec"
    else: sets,reps,intensity="5-10 min","controlled","easy";tempo="easy";rest="as needed"
    return {"name":n,"sets":sets,"reps":reps,"intensity":intensity,"tempo":tempo,"rest":rest,"plane":M["plane"],"pattern":M["pattern"],"equipment":M["equipment"],"purpose":M["purpose"]}
def metcon(p,m,w,d,used):
    fm=["EMOM","AMRAP","TABATA","Intervals","Chipper","Tempo Circuit"]; f=fm[((m-1)*4+(w-1)*2+d-1)%len(fm)]
    pools={"Swimming":["Bike Sprint","Row Intervals","SkiErg Intervals"],"Soccer":["Bike Sprint","Shuttle Sprint","Burpee"],"Tennis":["Bike Sprint","Shuttle Sprint","Battle Rope Intervals"],"Boxing":["Shadow Boxing","Battle Rope Intervals","Bike Sprint"],"MMA":["Shadow Boxing","Battle Rope Intervals","Bike Sprint"],"Karate":["Shadow Kick Combination","Battle Rope Intervals","Bike Sprint"],"Basketball":["Bike Sprint","Shuttle Sprint","Row Intervals"],"Handball":["Bike Sprint","Shuttle Sprint","Battle Rope Intervals"],"Bodybuilding":["Bike Sprint","Row Intervals","SkiErg Intervals"],"General Fitness":["Bike Sprint","Row Intervals","Burpee"]}
    opts=[x for x in pools.get(p["sport"],[]) if x in META and META[x]["equipment"] in p["equipment"] and x not in blocked(p)]
    if not opts: opts=[x for x,M in META.items() if "metcon" in M["cats"] and M["equipment"] in p["equipment"] and x not in blocked(p)]
    n=opts[(m*3+w+d-2)%len(opts)]; text={"EMOM":"10 min EMOM: minute 1 / minute 2 alternating","AMRAP":"12 min AMRAP: quality rounds","TABATA":"4 min: 20s work / 10s recovery","Intervals":"6 rounds: 30s work / 30-60s recovery","Chipper":"For time: controlled pace","Tempo Circuit":"6 rounds: 40s work / 20s transition"}[f]
    M=META[n]; return {"name":n,"format":f,"sets":text,"reps":"","intensity":"RPE 6-8","tempo":"sport-specific","rest":"as prescribed","plane":M["plane"],"pattern":M["pattern"],"equipment":M["equipment"],"purpose":f"{p['sport']} conditioning"}
def generate_plan(p):
    weak=priorities(p.get("posture_findings",[]),p.get("sfma",{}),p.get("injuries",[])); months=[]; used=[]
    for m in range(1,p["months"]+1):
        ph,pf=phase(m); weeks=[]
        for w in range(1,5):
            days=[]
            for d in range(1,p["days_per_week"]+1):
                u=used[-35:]; cor=choose(p,"corrective",2,u,m,d); st=choose(p,"strength",5,u+cor,m,d); pw=choose(p,"power",2,u+cor+st,m,d); ag=choose(p,"agility",2,u+cor+st+pw,m,d); co=choose(p,"coordination",1,u+cor+st+pw+ag,m,d); sp=choose(p,"sport",2,u+cor+st+pw+ag+co,m,d)
                main=cor+st+pw+ag+co+sp
                demands=set().union(*(META[x]["cats"] for x in main))
                warm=[]
                if "upper" in demands: warm+=["Band Face Pull","T-Spine Windmill"]
                if "lower" in demands: warm+=["Ankle Dorsiflexion Rocker","90/90 Hip Flow"]
                if any("Pelvic" in x or "Hip" in x for x in p.get("posture_findings",[])): warm+=["Glute Bridge"]
                if any("Scapular" in x or "Shoulder" in x for x in p.get("posture_findings",[])): warm+=["Band Face Pull"]
                warm=list(dict.fromkeys(x for x in warm if x in META and META[x]["equipment"] in p["equipment"]))[:4]
                rec=choose(p,"recovery",2,u+main,m,d); mc=metcon(p,m,w,d,u+main)
                sess={"theme":["Strength Base","Power + Skill","Speed / Agility","Capacity"][min(d-1,3)],"phase":ph,"phase_focus":pf,"rpe":min(9,6+m),"energy":"High" if readiness(p)>=75 else "Moderate","emphasis":"Full-spectrum development" if p["primary"]=="Overall Development" else p["primary"],
                "warmup":[pres(x,"warmup",m,p) for x in warm],"corrective":[pres(x,"corrective",m,p) for x in cor],"strength":[pres(x,"strength",m,p) for x in st],"power":[pres(x,"power",m,p) for x in pw],"agility":[pres(x,"agility",m,p) for x in ag],"coordination":[pres(x,"coordination",m,p) for x in co],"sport":[pres(x,"sport",m,p) for x in sp],"metcon":[mc],"recovery":[pres(x,"recovery",m,p) for x in rec],
                "reasons":[f"{p['sport']} + {', '.join(p['positions'])} shape sport demands.",f"Primary: {p['primary']}; secondary: {', '.join(p['secondary']) or 'none'}.","Strong qualities are maintained while weaknesses receive targeted exposure.","Exercise history and movement-pattern diversity reduce unnecessary repetition."]+([f"Screening priorities: {', '.join(weak)}."] if weak else [])}
                days.append(sess); used+=main
            weeks.append({"week":w,"days":days})
        months.append({"month":m,"phase":ph,"phase_focus":pf,"weeks":weeks})
    return {"readiness":readiness(p),"weaknesses":weak,"months":months}
