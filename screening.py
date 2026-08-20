POSTURE={'Anterior':['Anterior Pelvic Tilt','Knee Valgus','Forward Head','Rounded Shoulders','Foot Pronation'], 'Lateral':['Anterior Pelvic Tilt','Posterior Pelvic Tilt','Thoracic Kyphosis','Lumbar Hyperlordosis','Forward Head','Knee Hyperextension'], 'Posterior':['Scapular Winging','Scapular Asymmetry','Pelvic Obliquity','Knee Varus','Foot Pronation']}
FMS=['Deep Squat','Hurdle Step','Inline Lunge','Shoulder Mobility','Active Straight-Leg Raise','Trunk Stability Push-Up','Rotary Stability']
SFMA=['Cervical Flexion','Cervical Extension','Cervical Rotation','UE Pattern 1','UE Pattern 2','Multi-Segmental Flexion','Multi-Segmental Extension','Multi-Segmental Rotation','Single Leg Stance','Deep Squat']
SFMA_STATES=['FN','FP','DN','DP']; INJURIES=['None','Knee','Ankle','Hip','Low Back','Shoulder','Elbow/Wrist','Groin/Hamstring','Neck']
def asym(a,b): return round(abs(a-b)/max((a+b)/2,1e-6)*100,1)
def metrics(s):
 f=s.get('fms',[]); fms=sum(f)/len(f) if f else 2.5
 sf=s.get('sfma',{}); weights={'FN':100,'FP':70,'DN':60,'DP':35}; sfma=sum(weights.get(x,70) for x in sf.values())/len(sf) if sf else 70
 posture=len(s.get('posture',[])); sls=asym(s.get('sls_l',30),s.get('sls_r',30)); jump=asym(s.get('jump_l',25),s.get('jump_r',25))
 movement=max(0,min(100,fms/3*60+sfma*.4-posture*3)); stability=max(0,min(100,100-sls*2-jump*1.5)); neuro=max(0,min(100,100-s.get('reaction',.75)*45+s.get('landing',75)*.15-jump*.5))
 return {'movement':round(movement),'stability':round(stability),'neuromuscular':round(neuro),'fms':round(fms,2),'sfma':round(sfma,1),'jump_asym':jump,'sls_asym':sls}
