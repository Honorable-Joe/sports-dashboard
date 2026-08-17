import streamlit as st
from engine import generate_plan
from sports import SPORTS, POSITIONS

st.set_page_config(page_title='Athlete-IQ V9', page_icon='🏋️', layout='wide')

st.markdown('''
<style>
.stApp {background: radial-gradient(circle at top, #111a33 0%, #060a14 55%, #03050a 100%); color:#f4f7ff;}
.block-container {max-width:1400px; padding-top:1.2rem;}
.hero {padding:24px 28px; border-radius:22px; background:linear-gradient(135deg,#172554,#31165e 55%,#111827); border:1px solid #334155; box-shadow:0 15px 45px rgba(0,0,0,.3); margin-bottom:18px;}
.hero h1 {margin:0; font-size:2.2rem;}
.hero p {color:#cbd5e1; margin:.45rem 0 0;}
.card {background:linear-gradient(145deg,#10192d,#0b1222); border:1px solid #263653; border-radius:18px; padding:18px; margin:10px 0; box-shadow:0 8px 24px rgba(0,0,0,.22);}
.card h3 {margin:0 0 8px;}
.tag {display:inline-block; padding:4px 9px; border-radius:999px; background:#172554; border:1px solid #334155; margin:2px 4px 2px 0; font-size:.82rem; color:#cbd5e1;}
.section {font-size:1.35rem; font-weight:800; margin:18px 0 8px;}
.small {color:#94a3b8; font-size:.9rem;}
.metric {font-size:1.8rem; font-weight:800;}
</style>
''', unsafe_allow_html=True)

st.markdown('''<div class="hero"><h1>ATHLETE-IQ V9</h1><p>Closed-loop sports performance planning engine — screening, strengths, weaknesses, goals, equipment, periodization and training history all influence the plan automatically.</p></div>''', unsafe_allow_html=True)

with st.sidebar:
    st.header('Athlete Profile')
    athlete = st.text_input('Athlete name', 'Athlete')
    age = st.number_input('Age', 12, 70, 25)
    level = st.selectbox('Athlete level', ['General', 'Intermediate', 'Advanced', 'Elite'])
    sport = st.selectbox('Sport', list(SPORTS))
    positions = POSITIONS.get(sport, ['General'])
    position = st.multiselect('Position / specialization', positions, default=positions[:1])
    if not position:
        position = ['General']

    st.subheader('Goals')
    primary = st.selectbox('Primary goal', ['Overall Development','Strength','Max Strength','Hypertrophy','Power','Speed','Agility','Aerobic Capacity','Anaerobic Capacity','Sport Performance','Fat Loss','General Fitness'])
    secondary = st.multiselect('Secondary goals', ['Strength','Max Strength','Hypertrophy','Power','Speed','Agility','Aerobic Capacity','Anaerobic Capacity','Mobility','Stability','Neuromuscular Coordination'], default=['Mobility'])

    st.subheader('Equipment')
    equipment = st.multiselect('Available equipment', ['Bodyweight','Dumbbells','Kettlebells','Barbell','Cable/Machine','Resistance Bands','Medicine Ball','Landmine','TRX','Sled','Battle Rope','Box/Bench','Cones','Plyo Hurdles','Pull-up Bar','Dip Station','Bike/Row/SkiErg'], default=['Bodyweight','Dumbbells','Barbell','Cable/Machine','Cones','Box/Bench'])

    st.subheader('Screening')
    posture = st.multiselect('Posture / movement findings', ['Anterior Pelvic Tilt','Rounded Shoulders','Forward Head','Knee Valgus','Limited Ankle Dorsiflexion','Limited T-Spine Rotation','Poor Hip Mobility','Poor Scapular Control'], default=[])
    injury = st.multiselect('Current injury / limitation', ['None','Knee','Ankle','Hip','Low Back','Shoulder','Elbow/Wrist','Groin/Hamstring'], default=['None'])
    stability = st.slider('Stability score', 1, 10, 7)
    mobility = st.slider('Mobility score', 1, 10, 7)
    coordination = st.slider('Neuromuscular coordination', 1, 10, 7)

    st.subheader('Performance Metrics')
    cmj = st.number_input('CMJ (cm)', 0.0, 150.0, 45.0)
    sprint = st.number_input('10 m sprint (sec)', 1.0, 5.0, 1.9)
    broad = st.number_input('Broad jump (cm)', 0.0, 400.0, 220.0)
    change_dir = st.number_input('COD / agility score (1-10)', 1.0, 10.0, 7.0)

    st.subheader('Club Schedule')
    club_days = st.multiselect('Club training days', ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], default=['Tuesday','Thursday','Saturday'])
    club_hours = st.number_input('Club training hours / week', 0.0, 30.0, 4.5)

    st.subheader('Planning')
    months = st.slider('Months', 1, 6, 3)
    days_per_week = st.slider('Gym days / week', 2, 6, 4)
    history = st.text_area('Recent exercises to avoid repeating (optional)', 'Rear Foot Elevated Split Squat\nGlute Bridge')

profile = {
    'name': athlete, 'age': age, 'level': level, 'sport': sport, 'positions': position,
    'primary': primary, 'secondary': secondary, 'equipment': equipment,
    'posture': posture, 'injury': injury, 'stability': stability, 'mobility': mobility,
    'coordination': coordination, 'cmj': cmj, 'sprint': sprint, 'broad': broad,
    'change_dir': change_dir, 'club_days': club_days, 'club_hours': club_hours,
    'months': months, 'days_per_week': days_per_week,
    'history': [x.strip() for x in history.splitlines() if x.strip()]
}

plan = generate_plan(profile)

c1,c2,c3,c4 = st.columns(4)
with c1: st.markdown('<div class="card"><div class="small">Readiness</div><div class="metric">%d/100</div></div>' % plan['readiness'], unsafe_allow_html=True)
with c2: st.markdown('<div class="card"><div class="small">Development focus</div><div class="metric" style="font-size:1.25rem">%s</div></div>' % plan['focus'], unsafe_allow_html=True)
with c3: st.markdown('<div class="card"><div class="small">Position</div><div class="metric" style="font-size:1.25rem">%s</div></div>' % ', '.join(position), unsafe_allow_html=True)
with c4: st.markdown('<div class="card"><div class="small">Metcon rotation</div><div class="metric" style="font-size:1.25rem">%s</div></div>' % plan['metcon_rotation'], unsafe_allow_html=True)

st.markdown('<div class="section">Closed-loop decision summary</div>', unsafe_allow_html=True)
st.markdown('<div class="card">%s</div>' % ' '.join(f'<span class="tag">{x}</span>' for x in plan['decision_tags']), unsafe_allow_html=True)

st.markdown('<div class="section">Training Plan</div>', unsafe_allow_html=True)
month = st.selectbox('Month', list(range(1, months+1)), format_func=lambda x: f'Month {x}')
week = st.selectbox('Week', [1,2,3,4], format_func=lambda x: f'Week {x}')
day = st.selectbox('Day', list(range(1, days_per_week+1)), format_func=lambda x: f'Day {x}')

session = plan['months'][month-1]['weeks'][week-1]['days'][day-1]
st.markdown(f'<div class="card"><h3>Day {day} • {session["theme"]}</h3><span class="tag">{session["phase"]}</span><span class="tag">RPE {session["rpe"]}</span><span class="tag">{session["energy"]}</span><span class="tag">{session["emphasis"]}</span></div>', unsafe_allow_html=True)

for section_name in ['warmup','corrective','strength','power','agility','coordination','sport','metcon','recovery']:
    items = session.get(section_name, [])
    if not items: continue
    titles = {'warmup':'1. Smart Warm-up','corrective':'2. Corrective / Activation','strength':'3. Muscular Strength','power':'4. Power / Plyometrics','agility':'5. Speed / Agility','coordination':'6. Neuromuscular Coordination','sport':'7. Sport-Specific','metcon':'8. Metabolic / ESD','recovery':'9. Recovery'}
    st.markdown(f'<div class="section">{titles[section_name]}</div>', unsafe_allow_html=True)
    for ex in items:
        st.markdown(f'''<div class="card"><h3>{ex["name"]}</h3><span class="tag">{ex["sets"]}</span><span class="tag">{ex["tempo"]}</span><span class="tag">{ex["rest"]}</span><span class="tag">{ex["plane"]}</span><span class="tag">{ex["pattern"]}</span><span class="tag">{ex["equipment"]}</span><p class="small">Purpose: {ex["purpose"]}</p></div>''', unsafe_allow_html=True)

st.markdown('<div class="section">Why this session was selected</div>', unsafe_allow_html=True)
for reason in session['reasons']:
    st.write('•', reason)

st.caption('V9 automatically regenerates whenever a sidebar input changes. Exercise selection uses needs, goals, sport/position, equipment, screening, performance metrics, phase, day and repetition history.')
