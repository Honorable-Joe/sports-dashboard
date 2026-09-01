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
st.selectbox=lambda label,opts,**k:opts[0]; st.multiselect=lambda label,opts,**k:k.get('default',[]); st.text_input=lambda *a,**k:k.get('value',''); st.text_area=lambda *a,**k:k.get('value',''); st.number_input=lambda label,*a,**k:k.get('value',(a[1] if len(a)>1 else 0)); st.slider=lambda label,*a,**k:k.get('value',(a[1] if len(a)>1 else 0)); st.checkbox=lambda *a,**k:k.get('value',False); st.file_uploader=lambda *a,**k:None; st.button=lambda *a,**k:False; st.select_slider=lambda *a,**k:k.get('value',3); st.expander=lambda *a,**k:C()
sys.modules['streamlit']=st
spec=importlib.util.spec_from_file_location('aiq','/mnt/data/Athlete_IQ_V11_app.py'); aiq=importlib.util.module_from_spec(spec); spec.loader.exec_module(aiq)

def base():
    d=dict(aiq.DEFAULTS); return aiq.AthleteProfile(**d)
def names(program):
    out=[]
    for m in program.values():
      for ws in m.values():
       for s in ws:
        out += [x.name for x in s['exercises']]
        if s.get('complex'): out += [aiq.EXERCISES[e].name for e in s['complex'].exercises if e in aiq.EXERCISES]
        out += s['conditioning']['stations']
    return out

# 1 swimming equipment
x=base(); x.sport='Swimming'; x.position='Freestyle'; x.equipment=['Bodyweight','Dumbbells']; x.primary_goal='Strength'; p,e=aiq.build_program(x,3); ns=names(p)
assert 'Shadow Boxing' not in ns and 'Sled Push' not in ns, 'Swimming equipment/sport leakage'
# 2 soccer winger cannot get goalkeeper dive
x=base(); x.sport='Soccer'; x.position='Winger'; x.equipment=['Bodyweight','Dumbbells','Cones / Timing Gates']; p,e=aiq.build_program(x,3); ns=names(p)
assert 'Goalkeeper Lateral Dive Pattern' not in ns, 'Goalkeeper drill leaked to winger'
# 3 equipment hard filter
x=base(); x.sport='Soccer'; x.position='Winger'; x.equipment=['Bodyweight','Dumbbells']; p,e=aiq.build_program(x,3); ns=names(p)
for bad in ['Sled Push','Bench Press','Barbell Back Squat','Barbell Bench Press']:
    assert bad not in ns, f'{bad} leaked through equipment filter'
# 4 goal changes architecture
x=base(); x.sport='MMA'; x.position='MMA General'; x.equipment=aiq.EQUIPMENT.copy(); x.primary_goal='Strength'; p1,e1=aiq.build_program(x,3)
x.primary_goal='Speed'; p2,e2=aiq.build_program(x,3)
s1=[s['phase']+str([z.name for z in s['exercises']]) for m in p1.values() for w in m.values() for s in w]
s2=[s['phase']+str([z.name for z in s['exercises']]) for m in p2.values() for w in m.values() for s in w]
assert s1!=s2, 'Strength vs Speed produced identical program'
# 5 actual exercise variation across months
x=base(); x.sport='Soccer'; x.position='Winger'; x.equipment=aiq.EQUIPMENT.copy(); x.primary_goal='Strength'; p,e=aiq.build_program(x,3)
month_sets=[]
for mi in [1,2,3]:
  month_sets.append(tuple(s['exercises'][0].name for s in p[mi][1]))
assert len(set(month_sets))>1, 'No month-to-month exercise variation'
# 6 multiple metcon protocols
protocols=[]
for m in p.values():
  for w in m.values():
    for s in w: protocols.append(s['conditioning']['protocol'])
assert len(set(protocols))>=3, 'MetCon lacks protocol variety'
# 7 indices respond to data
x=base(); a1=aiq.stability_index(x); x.stability_tests['Single-Leg Stance L']=5; x.stability_tests['Single-Leg Stance R']=5; x.stability_tests['Landing Control']=30; a2=aiq.stability_index(x); assert a2<a1
print('ALL V11 REGRESSION TESTS PASS')
# 8 goalkeeper vs winger and sport-specific program differ
x=base(); x.sport='Soccer'; x.position='Goalkeeper'; x.equipment=aiq.EQUIPMENT.copy(); pg,_=aiq.build_program(x,3)
x.position='Winger'; pw,_=aiq.build_program(x,3)
g=[z.name for z in pg[1][1][0]['exercises']]; w=[z.name for z in pw[1][1][0]['exercises']]
assert g!=w, 'Goalkeeper and Winger produced identical session'
# 9 tennis vs MMA differ
x.sport='Tennis'; x.position='Singles'; pt,_=aiq.build_program(x,3)
x.sport='MMA'; x.position='MMA General'; pm,_=aiq.build_program(x,3)
assert [z.name for z in pt[1][1][0]['exercises']] != [z.name for z in pm[1][1][0]['exercises']], 'Tennis and MMA identical'
# 10 warm-up responds to systems
x=base(); x.primary_goal='Strength'; x.sport='Bodybuilding'; x.position='Off-Season'; p,_=aiq.build_program(x,1)
wa=aiq.smart_warmup(x,p[1][1][0]); x.primary_goal='Speed'; p2,_=aiq.build_program(x,1); wb=aiq.smart_warmup(x,p2[1][1][0]); assert wa!=wb, 'Warm-up did not respond to session demands'
# 11 no known mojibake markers in source
src=open('/mnt/data/Athlete_IQ_V11_app.py',encoding='utf-8').read();
for bad in ['Ã','â','ð','�']:
    assert bad not in src, f'Mojibake marker {bad} found'
print('EXTENDED V11 TESTS PASS')
