import streamlit as st
from sports import SPORTS,GOALS,SECONDARY,EQUIPMENT
from screening import POSTURE,FMS,SFMA,SFMA_STATES,INJURIES
from engine import generate
st.set_page_config(page_title='ATHLETE-IQ V11',layout='wide')
st.markdown('''<style>body{background:#07111f}.block-container{padding-top:1rem}.title{text-align:center;color:#38bdf8;font-size:2.4rem;font-weight:900}.sub{text-align:center;color:#a855f7;font-weight:700}.banner{background:linear-gradient(90deg,#7c3aed,#ec4899);padding:14px;border-radius:12px;color:white;font-size:1.2rem;font-weight:800}.card{background:#0d1b2e;border:1px solid #223552;border-radius:14px;padding:14px;margin:8px 0}.ex{background:#101b30;border:1px solid #28405f;border-left:4px solid #38bdf8;border-radius:12px;padding:12px;margin:7px 0}.tag{border:1px solid #28405f;border-radius:999px;padding:3px 8px;margin-right:5px;font-size:.78rem}</style>''',unsafe_allow_html=True)
st.markdown('<div class="title">ATHLETE-IQ V11</div><div class="sub">Closed-Loop Whole-Athlete Adaptive Programming Engine</div>',unsafe_allow_html=True)
P=['Athlete Profile','Sport / Position Context','Health / History','Posture','FMS','SFMA','Mobility','Stability','Neuromuscular Coordination','Performance','Asymmetry','Programming Priorities','Club Load','Equipment','Program']
if 'page' not in st.session_state:st.session_state.page=P[0]
with st.sidebar:
 st.markdown('## ATHLETE-IQ');st.session_state.page=st.radio('Jump to module',P,index=P.index(st.session_state.page));st.caption('The plan regenerates automatically from the current athlete state.')
def init(k,v):
 if k not in st.session_state:st.session_state[k]=v
init('sport','Soccer');init('positions',['Goalkeeper']);init('primary','Overall Development');init('secondary',['Strength','Power']);init('equipment',['Bodyweight','Dumbbells','Barbell','Cable/Machine','Cones','Box/Bench']);init('level','Advanced');init('injuries',['None']);init('posture',[])
page=st.session_state.page
if page=='Athlete Profile':
 st.markdown('<div class="banner">01 | Athlete Profile</div>',unsafe_allow_html=True);c1,c2,c3=st.columns(3);c1.text_input('Name',key='name');c1.number_input('Age',12,80,25,key='age');c2.selectbox('Level',['General','Intermediate','Advanced','Elite'],key='level');c2.number_input('Height cm',100.,230.,180.,key='height');c3.number_input('Weight kg',30.,250.,80.,key='weight')
elif page=='Sport / Position Context':
 st.markdown('<div class="banner">02 | Sport / Position Context</div>',unsafe_allow_html=True);st.selectbox('Sport',list(SPORTS),key='sport');st.multiselect('Positions / specializations - multiple allowed',SPORTS[st.session_state.sport],key='positions');st.selectbox('Primary goal',GOALS,key='primary');st.multiselect('Secondary development targets',SECONDARY,key='secondary')
elif page=='Health / History':
 st.markdown('<div class="banner">03 | Health / History</div>',unsafe_allow_html=True);st.multiselect('Current limitations',INJURIES,key='injuries');st.text_area('Previous injury / history',key='history');st.slider('Pain today',0,10,0,key='pain')
elif page=='Posture':
 st.markdown('<div class="banner">04 | Posture</div>',unsafe_allow_html=True);st.info('Coach observation layer. Findings influence programming but are not clinical diagnoses.');
 for v,items in POSTURE.items():st.multiselect(v+' view',items,key='post_'+v)
 st.session_state.posture=sum([st.session_state.get('post_'+v,[]) for v in POSTURE],[])
elif page=='FMS':
 st.markdown('<div class="banner">05 | FMS</div>',unsafe_allow_html=True);[st.selectbox(x,[0,1,2,3],index=2,key='fms_'+str(i)) for i,x in enumerate(FMS)]
elif page=='SFMA':
 st.markdown('<div class="banner">06 | SFMA</div>',unsafe_allow_html=True);[st.selectbox(x,SFMA_STATES,key='sfma_'+str(i)) for i,x in enumerate(SFMA)]
elif page=='Mobility':
 st.markdown('<div class="banner">07 | Mobility</div>',unsafe_allow_html=True);st.number_input('Ankle dorsiflexion cm',0.,30.,10.,key='ankle');st.number_input('Hip ROM deg',0.,180.,110.,key='hip');st.number_input('Shoulder ROM deg',0.,250.,170.,key='shoulder')
elif page=='Stability':
 st.markdown('<div class="banner">08 | Stability</div>',unsafe_allow_html=True);c1,c2=st.columns(2);c1.number_input('Single-leg stance L sec',0.,180.,30.,key='sls_l');c2.number_input('Single-leg stance R sec',0.,180.,30.,key='sls_r')
elif page=='Neuromuscular Coordination':
 st.markdown('<div class="banner">09 | Neuromuscular Coordination</div>',unsafe_allow_html=True);st.number_input('Reaction time sec',.1,3.,.75,key='reaction');st.slider('Landing control',0,100,75,key='landing');[st.slider(x,0,100,75,key='n_'+x) for x in ['Unilateral','Bilateral','Ipsilateral','Contralateral','Decision / dual task']]
elif page=='Performance':
 st.markdown('<div class="banner">10 | Performance</div>',unsafe_allow_html=True);c1,c2,c3=st.columns(3);c1.number_input('CMJ cm',0.,150.,45.,key='cmj');c1.number_input('Broad jump cm',0.,400.,220.,key='broad');c2.number_input('5m sprint sec',.5,5.,1.2,key='s5');c2.number_input('10m sprint sec',.8,7.,1.9,key='s10');c2.number_input('20m sprint sec',1.,12.,3.2,key='s20');c3.number_input('Squat 1RM kg',20.,400.,110.,key='sq');c3.number_input('Bench 1RM kg',20.,300.,75.,key='bench');c3.number_input('OHP 1RM kg',10.,200.,50.,key='ohp');st.caption('Sport-specific tests are filtered conceptually by sport/position; irrelevant tests can be left unused.')
elif page=='Asymmetry':
 st.markdown('<div class="banner">11 | Asymmetry</div>',unsafe_allow_html=True);c1,c2=st.columns(2);c1.number_input('Single-leg jump L cm',0.,120.,25.,key='jump_l');c2.number_input('Single-leg jump R cm',0.,120.,27.,key='jump_r')
elif page=='Programming Priorities':
 st.markdown('<div class="banner">12 | Programming Priorities</div>',unsafe_allow_html=True);st.multiselect('Coach emphasis',SECONDARY,key='coach_priority');st.info('The engine does not choose between fixing weaknesses and developing strengths. It allocates both, with dose and complexity adjusted by readiness.')
elif page=='Club Load':
 st.markdown('<div class="banner">Club Training Days / Hours</div>',unsafe_allow_html=True);st.multiselect('Club days',['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],key='club_days');st.number_input('Club hours/week',0.,40.,4.5,key='club_hours');st.number_input('Competition hours/week',0.,20.,1.5,key='match_hours')
elif page=='Equipment':
 st.markdown('<div class="banner">Equipment</div>',unsafe_allow_html=True);st.multiselect('Available equipment - hard filter',EQUIPMENT,key='equipment')
elif page=='Program':
 st.markdown('<div class="banner">Adaptive Multi-Month Program</div>',unsafe_allow_html=True);months=st.slider('Months',1,6,3);days=st.slider('Training days/week',2,6,4)
 fms=[st.session_state.get('fms_'+str(i),2) for i in range(len(FMS))];sf={x:st.session_state.get('sfma_'+str(i),'FN') for i,x in enumerate(SFMA)}
 s={'sport':st.session_state.sport,'positions':st.session_state.positions or ['General'],'primary':st.session_state.primary,'secondary':st.session_state.secondary,'equipment':st.session_state.equipment or ['Bodyweight'],'level':st.session_state.level,'injuries':st.session_state.injuries or ['None'],'posture':st.session_state.get('posture',[]),'fms':fms,'sfma':sf,'sls_l':st.session_state.get('sls_l',30),'sls_r':st.session_state.get('sls_r',30),'jump_l':st.session_state.get('jump_l',25),'jump_r':st.session_state.get('jump_r',27),'reaction':st.session_state.get('reaction',.75),'landing':st.session_state.get('landing',75),'months':months,'days':days}
 plan=generate(s);a,b,c=st.columns(3);a.metric('Readiness',plan['readiness']);b.metric('Movement',plan['metrics']['movement']);c.metric('Neuromuscular',plan['metrics']['neuromuscular']);m=st.selectbox('Month',range(1,months+1));w=st.selectbox('Week',range(1,5));d=st.selectbox('Day',range(1,days+1));ses=plan['months'][m-1]['weeks'][w-1][d-1]
 st.markdown(f'<div class="card"><b>Month {m} • Week {w} • Day {d}</b> • {plan["months"][m-1]["phase"]} • {ses["metcon_format"]}</div>',unsafe_allow_html=True)
 st.markdown('### 1. Smart Warm-up');st.write(' → '.join(ses['warmup']))
 labels={'corrective':'2. Corrective / Activation','strength':'3. Muscular Strength / Resistance','power':'4. Power / Plyometrics','agility':'5. Speed / Agility','coordination':'6. Neuromuscular Coordination','sport':'7. Sport-Specific Transfer'}
 from exercises import EX
 for sec,title in labels.items():
  st.markdown('### '+title)
  for n in ses['sections'][sec]:
   e=EX[n];st.markdown(f'<div class="ex"><b>{n}</b><br><span class="tag">{e["equipment"]}</span><span class="tag">{e["pattern"]}</span><span class="tag">{e["plane"]}</span><span class="tag">complexity {e["complexity"]}/5</span></div>',unsafe_allow_html=True)
 st.markdown(f'### 8. MetCon — {ses["metcon_format"]}')
 protocol={'Tabata':'8 rounds: 20s work / 10s transition','AMRAP':'12-minute AMRAP','EMOM':'12-minute EMOM','Intervals':'4-6 quality rounds with full recovery'}[ses['metcon_format']];st.write(protocol);[st.write(f'{i}. {n}') for i,n in enumerate(ses['sections']['metcon'],1)]
else: st.markdown('<div class="banner">Use the sidebar to move through the assessment in order.</div>',unsafe_allow_html=True)
