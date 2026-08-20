from engine import generate
from exercises import EX
base={'sport':'Soccer','positions':['Winger'],'primary':'Strength','secondary':['Power','Plyometrics'],'equipment':['Bodyweight','Dumbbells','Barbell','Cones','Box/Bench','Medicine Ball'],'level':'Advanced','injuries':['None'],'posture':['Anterior Pelvic Tilt'],'fms':[2]*7,'sfma':{},'sls_l':30,'sls_r':27,'jump_l':25,'jump_r':28,'reaction':.6,'landing':80,'months':3,'days':4}
p=generate(base);assert len(p['months'])==3 and len(p['months'][0]['weeks'])==4
# Equipment regression
q=dict(base);q.update({'sport':'Swimming','positions':['Freestyle'],'equipment':['Bodyweight','Dumbbells']});r=generate(q)
for M in r['months']:
 for W in M['weeks']:
  for D in W:
   for ns in D['sections'].values():
    for n in ns: assert EX[n]['equipment'] in q['equipment'],(n,EX[n]['equipment'])
# Swimming must not receive boxing
alln=sum([list(D['sections'].values()) for M in r['months'] for W in M['weeks'] for D in W],[]);alln=sum(alln,[])
assert 'Shadow Boxing' not in alln and 'Sled Push' not in alln
# Metcon formats actually change
formats=[p['months'][m]['weeks'][w][0]['metcon_format'] for m in range(3) for w in range(4)]
assert len(set(formats))>=3
print('PASS')
