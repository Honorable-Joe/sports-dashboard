import sys, types, importlib.util
class C:
    def __enter__(self): return self
    def __exit__(self,*a): return False
    def metric(self,*a,**k): pass
class Session(dict):
    __getattr__=dict.get
    __setattr__=dict.__setitem__
st=types.ModuleType('streamlit'); st.session_state=Session(); st.set_page_config=lambda *a,**k:None
for fn in ['markdown','caption','info','warning','error','success','write','subheader','metric','dataframe','divider','title']:
    setattr(st,fn,lambda *a,**k:None)
st.tabs=lambda xs:[C() for _ in xs]; st.columns=lambda n:[C() for _ in range(n)]
st.sidebar=types.SimpleNamespace(markdown=st.markdown,caption=st.caption,radio=lambda label,opts,**k:opts[0],select_slider=lambda *a,**k:k.get('value',3))
st.selectbox=lambda label,opts,**k:opts[0]; st.multiselect=lambda label,opts,**k:k.get('default',[]); st.pills=lambda *a,**k:[]
st.text_input=lambda *a,**k:k.get('value',''); st.text_area=lambda *a,**k:k.get('value',''); st.number_input=lambda label,*a,**k:k.get('value',(a[1] if len(a)>1 else 0)); st.slider=lambda label,*a,**k:k.get('value',(a[1] if len(a)>1 else 0)); st.checkbox=lambda *a,**k:k.get('value',False); st.file_uploader=lambda *a,**k:None; st.button=lambda *a,**k:False; st.select_slider=lambda *a,**k:k.get('value',3); st.expander=lambda *a,**k:C(); st.download_button=lambda *a,**k:False
sys.modules['streamlit']=st
spec=importlib.util.spec_from_file_location('aiq','/mnt/data/aiq_work/app.py'); aiq=importlib.util.module_from_spec(spec); spec.loader.exec_module(aiq)

def base(): return aiq.AthleteProfile(**dict(aiq.DEFAULTS))

def resistance_names(session): return [x.name for x in session['exercises'] if x.system=='Resistance']

# 1 Height/weight are active in decision outputs
x=base(); p1=aiq.priorities(x); x.height_cm=190; p2=aiq.priorities(x)
assert aiq.performance_scores(x)['Height-Normalized CMJ'] != aiq.performance_scores(base())['Height-Normalized CMJ']
assert 'Weight Loss' in aiq.GOALS and 'Weight Gain' in aiq.GOALS
x.primary_goal='Weight Loss'; wl=aiq.system_allocation(x,aiq.priorities(x),aiq.constraint_engine(x)); x.primary_goal='Weight Gain'; wg=aiq.system_allocation(x,aiq.priorities(x),aiq.constraint_engine(x)); assert wl['Aerobic']>wg['Aerobic'] and wg['Resistance']>wl['Resistance']

# 2 Explicit right/left scapular depression is recognized and side-aware
x=base(); x.posture_posterior={'Scapular position':'Right scapular depression || Moderate ||'}
cs=aiq.screening_correctives(x,{'exercises':[],'day':1,'week':1,'month':1},limit=3)
assert cs and any(side=='R' for _,side,_ in cs), 'Right scapular depression did not remain right-sided'
x.posture_posterior={'Scapular position':'Left scapular depression || Moderate ||'}
cs=aiq.screening_correctives(x,{'exercises':[],'day':1,'week':1,'month':1},limit=3)
assert cs and any(side=='L' for _,side,_ in cs), 'Left scapular depression did not remain left-sided'

# 3 DB RDL load is a pair-total practical load, not one 112 kg DB
x=base(); x.deadlift_1rm=120; db=[e for e in aiq.EXERCISES.values() if e.name=='Dumbbell Romanian Deadlift']
assert db, 'DB RDL missing'
load,_=aiq.adaptive_exercise_load(x,db[0],1,'primary')
assert load < 90, f'DB RDL total load too high: {load}'
assert 'pair load' in aiq._v13_load_display(db[0],load).lower() and 'kg/hand' in aiq._v13_load_display(db[0],load), 'DB load display is not explicit'

# 4 General Fitness: whole-body and upper-body coverage across days, no four-day deadlift repeat
x=base(); x.primary_goal='General Fitness'; x.gym_days_available=4; x.equipment=['Dumbbells','Barbells & Plates','Kettlebells']
p,_=aiq.build_program(x,1)
week=p[1][1]
allr=[resistance_names(s) for s in week]
flat=[n for row in allr for n in row]
assert len(flat)>=8, f'General Fitness resistance volume too low: {allr}'
assert len(set(flat))>=6, f'General Fitness resistance diversity too low: {allr}'
assert any(any(k in n.lower() for k in ['bench','press','row','pull','push-up']) for n in flat), f'No upper body resistance: {allr}'
assert sum('deadlift' in n.lower() for n in flat) <= 2, f'Deadlift repeated excessively: {allr}'
met=[tuple(s['conditioning']['stations']) for s in week]
assert len(set(met))>=3, f'General Fitness MetCon repeated: {met}'

# 5 Soccer: varied main lifts and MetCon across a week with DB/barbell/KB only
x=base(); x.sport='Soccer'; x.position='Winger'; x.gym_days_available=4; x.equipment=['Dumbbells','Barbells & Plates','Kettlebells']
p,_=aiq.build_program(x,2)
for month in [1,2]:
    week=p[month][1]
    rows=[resistance_names(s) for s in week]
    flat=[n for row in rows for n in row]
    assert len(set(flat))>=6, f'Soccer month {month} resistance repeated: {rows}'
    assert len(set(tuple(s['conditioning']['stations']) for s in week))>=3, f'Soccer month {month} MetCon repeated'
    # Same screening correctives should not be forced identically every day
    x.posture_posterior={'Scapular position':'Right scapular depression || Moderate ||'}
    # rebuild with finding present
p,_=aiq.build_program(x,1)
cs=[tuple(z[0].name for z in aiq.screening_correctives(x,s,3)) for s in p[1][1]]
assert len(set(cs))>=2, f'Correctives did not rotate: {cs}'

# 6 Full-session feedback storage supports non-resistance components
x=base(); sess={'month':1,'week':1,'day':1}
aiq.st.session_state.exercise_feedback_log=[]; aiq.st.session_state.session_feedback_log=[]; aiq.st.session_state.session_component_feedback_log=[]; aiq.st.session_state.feedback={'session_rpe':[],'pain':[],'performance':[]}
aiq.save_exercise_feedback(x,sess,[],7,0,'ok',component_rows=[{'component_type':'Warm-up','component_name':'A','status':'Completed','rpe':3},{'component_type':'MetCon','component_name':'B','status':'Partial','performance':'Hard','rpe':8}],performance_change=-1,duration_min=70)
assert len(aiq.st.session_state.session_component_feedback_log)==2
assert aiq.st.session_state.last_feedback['performance_change']==-1

# 7 SFMA UI source contains action-level instructions, not generic placeholders
src=open('/mnt/data/aiq_work/app.py',encoding='utf-8').read()
for phrase in ['Keep the trunk still','Keep the shoulders from rotating','reverse the arm positions','feet together and knees straight','arms overhead','feet planted']:
    assert phrase in src, f'Missing SFMA instruction detail: {phrase}'
for bad in ['Perform the standardized upper-extremity pattern and observe mobility, pain and compensation.','Stand tall; ask the athlete to flex the cervical spine']:
    assert bad not in src, f'Old generic SFMA instruction remains: {bad}'
print('V13 USER-REPORTED ISSUE TESTS PASS')
