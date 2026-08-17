import streamlit as st
import pandas as pd
from engine import generate_plan
from sports import SPORTS,GOALS,SECONDARY,EQUIPMENT,DAYS
from screening import POSTURE_FINDINGS,SFMA,INJURIES

st.set_page_config(page_title="ATHLETE-IQ PERFORMANCE ENGINE",page_icon="⚡",layout="wide",initial_sidebar_state="expanded")
st.markdown("""<style>
.stApp{background:#0d1117;color:#c9d1d9}.block-container{max-width:1450px;padding-top:1rem}
.title{text-align:center}.title h1{color:#38bdf8;font-size:2.5rem;font-weight:800;letter-spacing:1.5px;margin:0}.title p{color:#a855f7;font-weight:700}
.banner{background:linear-gradient(90deg,#7c3aed,#ec4899);color:white;padding:14px 20px;border-radius:12px;font-size:1.25rem;font-weight:700;margin:16px 0;box-shadow:0 4px 15px rgba(124,58,237,.3)}
.card{background:linear-gradient(145deg,#111827,#161b22);border:1px solid #30363d;border-radius:16px;padding:16px;margin:8px 0}.ex{background:linear-gradient(145deg,#111827,#1b1430);border:1px solid #334155;border-left:4px solid #38bdf8;border-radius:14px;padding:14px;margin:8px 0}
.tag{display:inline-block;background:#172554;border:1px solid #334155;border-radius:999px;padding:4px 9px;margin:2px 4px 2px 0;font-size:.78rem}.small{color:#94a3b8;font-size:.88rem}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="title"><h1>⚡ ATHLETE-IQ PERFORMANCE ENGINE</h1><p>Integrated athlete assessment • closed-loop development • automatic periodized programming</p></div>',unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page="Athlete Profile"
pages=["Athlete Profile","Sport & Goals","Full Screening","Performance","Club Load","Equipment","Athlete Analysis","Program"]
with st.sidebar:
    st.markdown("## 🧭 ATHLETE-IQ")
    st.session_state.page=st.radio("Pages",pages,index=pages.index(st.session_state.page))
    st.caption("No Generate Plan button. The program rebuilds from the current state automatically.")

S=st.session_state
defaults={"name":"Athlete","age":25,"level":"Advanced","sport":"Soccer","positions":["Goalkeeper"],"primary":"Overall Development","secondary":["Strength","Power","Mobility"],"equipment":["Bodyweight","Dumbbells","Barbell","Cable/Machine","Cones","Box/Bench"],"injuries":["None"],"club_days":["Tuesday","Thursday","Saturday"]}
for k,v in defaults.items():
    if k not in S:S[k]=v

page=S.page
if page=="Athlete Profile":
    st.markdown('<div class="banner">👤 1. ATHLETE PROFILE</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1: st.text_input("Athlete name",key="name"); st.number_input("Age",12,80,key="age")
    with c2: st.selectbox("Athlete level",["General","Intermediate","Advanced","Elite"],key="level"); st.number_input("Height (cm)",100.,230.,175.,key="height")
    with c3: st.number_input("Weight (kg)",30.,250.,75.,key="weight"); st.selectbox("Context",["Recreational","Competitive","High Performance","Return to Performance"],key="context")
elif page=="Sport & Goals":
    st.markdown('<div class="banner">🏟️ 2. SPORT, POSITION & DEVELOPMENT GOALS</div>',unsafe_allow_html=True)
    st.selectbox("Sport",list(SPORTS),key="sport")
    st.multiselect("Position / specialization — multiple allowed",SPORTS[S.sport]["positions"],key="positions")
    st.selectbox("Primary Development Goal",GOALS,key="primary")
    st.multiselect("Secondary Development Goals",SECONDARY,key="secondary")
    st.success("Overall Development means the engine develops the complete athlete while still prioritizing the identified needs.")
elif page=="Full Screening":
    st.markdown('<div class="banner">🔎 3. FULL ATHLETE SCREENING</div>',unsafe_allow_html=True)
    st.caption("Anterior + lateral + posterior observation, SFMA-style movement screening and injury context all feed the same decision engine.")
    for view in ["Anterior","Lateral","Posterior"]:
        with st.expander(f"{view} View",expanded=True): st.multiselect(f"{view} findings",POSTURE_FINDINGS[view],key="post_"+view)
    st.markdown("### SFMA / Movement Screen")
    for i,t in enumerate(SFMA): st.selectbox(t,["Good","Limited","Poor","Pain"],key=f"sfma_{i}")
    st.markdown("### Injury / Limitation")
    st.multiselect("Current injury / limitation",INJURIES,key="injuries")
    st.text_area("Previous injury / relevant history",key="injury_history")
    a,b,c=st.columns(3)
    with a: st.slider("Mobility",1,10,7,key="mobility")
    with b: st.slider("Stability",1,10,7,key="stability")
    with c: st.slider("Neuromuscular Coordination",1,10,7,key="coordination")
elif page=="Performance":
    st.markdown('<div class="banner">📊 4. PERFORMANCE METRICS & TEST BATTERY</div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a:
        st.number_input("CMJ (cm)",0.,120.,45.,key="cmj"); st.number_input("Approach Vertical (cm)",0.,150.,50.,key="approach")
        st.number_input("Broad Jump (cm)",0.,400.,220.,key="broad"); st.number_input("Single-Leg Vertical L (cm)",0.,100.,25.,key="vl")
        st.number_input("Single-Leg Vertical R (cm)",0.,100.,27.,key="vr")
    with b:
        st.number_input("5m Sprint (sec)",.5,5.,1.2,key="s5"); st.number_input("10m Sprint (sec)",.8,6.,1.9,key="s10")
        st.number_input("20m Sprint (sec)",1.,10.,3.2,key="s20"); st.number_input("505 COD (sec)",1.,8.,2.4,key="cod")
        st.number_input("T-Test (sec)",5.,30.,10.,key="ttest")
    with c:
        st.number_input("Back Squat 1RM (kg)",20.,300.,110.,key="squat"); st.number_input("Bench Press 1RM (kg)",20.,250.,75.,key="bench")
        st.number_input("Overhead Press 1RM (kg)",10.,180.,50.,key="ohp"); st.number_input("Pull-Ups (reps)",0,50,10,key="pullups")
        st.number_input("Push-Ups (reps)",0,100,30,key="pushups")
    st.markdown("### Sport-Specific Power")
    a,b,c,d=st.columns(4)
    with a: st.number_input("Chest Pass (m)",0.,30.,6.8,key="chest")
    with b: st.number_input("Overhead Throw (m)",0.,30.,8.5,key="overhead")
    with c: st.number_input("Forehand Throw (m)",0.,30.,7.2,key="forehand")
    with d: st.number_input("Backhand Throw (m)",0.,30.,6.9,key="backhand")
elif page=="Club Load":
    st.markdown('<div class="banner">📅 5. CLUB / TEAM TRAINING LOAD</div>',unsafe_allow_html=True)
    st.multiselect("Club training days",DAYS,key="club_days"); st.number_input("Club training hours / week",0.,40.,4.5,key="club_hours")
    st.multiselect("Competition / match days",DAYS,key="match_days"); st.number_input("Competition hours / week",0.,20.,1.5,key="match_hours")
    st.text_area("Fixed weekly constraints",key="schedule")
elif page=="Equipment":
    st.markdown('<div class="banner">🏋️ 6. AVAILABLE EQUIPMENT</div>',unsafe_allow_html=True)
    st.multiselect("Equipment available",EQUIPMENT,key="equipment")
    st.info("Equipment is a hard constraint: an unavailable tool cannot appear in the plan.")
elif page=="Athlete Analysis":
    st.markdown('<div class="banner">🧠 7. ATHLETE ANALYSIS</div>',unsafe_allow_html=True)
    findings=sum([S.get("post_"+v,[]) for v in ["Anterior","Lateral","Posterior"]],[])
    a,b,c,d=st.columns(4)
    with a: st.metric("Sport",S.sport)
    with b: st.metric("Primary",S.primary)
    with c: st.metric("Positions",len(S.positions))
    with d: st.metric("Screening Findings",len(findings))
    st.markdown('<div class="card"><b>Decision model:</b> screening → performance → sport/position → goals → equipment → external club load → training history → exercise selection → warm-up → training → conditioning → feedback.</div>',unsafe_allow_html=True)
    if findings: st.warning("Active findings: "+", ".join(findings))
    else: st.success("No postural findings entered.")
elif page=="Program":
    st.markdown('<div class="banner">🚀 8. DYNAMIC MULTI-MONTH PERIODIZATION ENGINE</div>',unsafe_allow_html=True)
    months=st.slider("Program length",1,6,3,key="months"); days=st.slider("Gym days / week",2,6,4,key="days")
    st.text_area("Recent exercises to avoid unnecessary repetition",key="history")
    findings=sum([S.get("post_"+v,[]) for v in ["Anterior","Lateral","Posterior"]],[])
    sf={t:S.get(f"sfma_{i}","Good") for i,t in enumerate(SFMA)}
    p={"sport":S.sport,"positions":S.positions or ["General"],"primary":S.primary,"secondary":S.secondary,"equipment":S.equipment or ["Bodyweight"],"injuries":S.injuries or ["None"],"posture_findings":findings,"sfma":sf,"cmj":S.get("cmj",45),"sprint10":S.get("s10",1.9),"broad":S.get("broad",220),"cod":S.get("cod",2.4),"mobility":S.get("mobility",7),"stability":S.get("stability",7),"coordination":S.get("coordination",7),"level":S.level,"history":[x.strip() for x in S.get("history","").splitlines() if x.strip()],"months":months,"days_per_week":days}
    plan=generate_plan(p)
    a,b,c,d=st.columns(4)
    with a: st.metric("Readiness",f"{plan['readiness']}/100")
    with b: st.metric("Development",p["primary"])
    with c: st.metric("Position",", ".join(p["positions"]))
    with d: st.metric("Priorities",len(plan["weaknesses"]))
    if plan["weaknesses"]: st.write("**Development priorities:** "+" • ".join(plan["weaknesses"]))
    m=st.selectbox("Month",range(1,months+1),format_func=lambda x:f"Month {x}",key="vm")
    w=st.selectbox("Week",range(1,5),format_func=lambda x:f"Week {x}",key="vw")
    d=st.selectbox("Day",range(1,days+1),format_func=lambda x:f"Day {x}",key="vd")
    ses=plan["months"][m-1]["weeks"][w-1]["days"][d-1]
    st.markdown(f'<div class="card"><h2>Day {d} • {ses["theme"]}</h2><span class="tag">{ses["phase"]}</span><span class="tag">{ses["phase_focus"]}</span><span class="tag">RPE {ses["rpe"]}</span><span class="tag">{ses["energy"]}</span></div>',unsafe_allow_html=True)
    titles={"warmup":"1. Smart Warm-up","corrective":"2. Corrective / Activation","strength":"3. Muscular Strength","power":"4. Power / Plyometrics","agility":"5. Speed / Agility","coordination":"6. Neuromuscular Coordination","sport":"7. Sport-Specific","metcon":"8. Metabolic Conditioning","recovery":"9. Recovery"}
    for sec in titles:
        if not ses[sec]: continue
        st.markdown("### "+titles[sec])
        for ex in ses[sec]:
            html=f"""<div class="ex"><h3>{ex["name"]}</h3><span class="tag">{ex.get("sets","")}</span><span class="tag">{ex.get("reps","")}</span><span class="tag">{ex.get("intensity","")}</span><span class="tag">Tempo {ex.get("tempo","")}</span><span class="tag">Rest {ex.get("rest","")}</span><span class="tag">{ex.get("plane","")}</span><span class="tag">{ex.get("pattern","")}</span><span class="tag">{ex.get("equipment","")}</span><p class="small">{ex.get("purpose","")}</p></div>"""
            st.markdown(html,unsafe_allow_html=True)
    st.markdown("### 🔄 Decision Loop")
    for r in ses["reasons"]: st.write("•",r)

st.caption("ATHLETE-IQ • assessment → analysis → plan → warm-up → training → conditioning → feedback → adaptation")
