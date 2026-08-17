POSTURE_FINDINGS={
"Anterior":["Anterior Pelvic Tilt","Knee Valgus","Forward Head","Rounded Shoulders","Foot Pronation"],
"Lateral":["Anterior Pelvic Tilt","Posterior Pelvic Tilt","Thoracic Kyphosis","Lumbar Hyperlordosis","Knee Hyperextension"],
"Posterior":["Scapular Winging","Scapular Asymmetry","Pelvic Obliquity","Knee Varus","Foot Pronation"]}
SFMA=["Cervical Flexion","Cervical Extension","Cervical Rotation","UE Pattern 1","UE Pattern 2","Multi-Segmental Flexion","Multi-Segmental Extension","Multi-Segmental Rotation","Single Leg Stance","Deep Squat"]
INJURIES=["None","Knee","Ankle","Hip","Low Back","Shoulder","Elbow/Wrist","Groin/Hamstring","Neck"]
BLOCK={"Knee":{"Depth Drop to Stick","Lateral Bound and Stick","Pogo Jump","Deep Squat"},"Ankle":{"Lateral Bound and Stick","Pogo Jump"},"Hip":{"Deep Squat"},"Low Back":{"Barbell Back Squat","Romanian Deadlift","Trap Bar Deadlift"},"Shoulder":{"Overhead Press","Weighted Dip"},"Elbow/Wrist":{"Weighted Dip"},"Groin/Hamstring":{"Shuttle Sprint"},"Neck":set()}
def priorities(findings,sfma,injuries):
    out=[]
    if any("Pelvic" in x or "Hip" in x for x in findings): out+=["hip/trunk control"]
    if any("Scapular" in x or "Shoulder" in x for x in findings): out+=["scapular control"]
    if any("Knee" in x for x in findings): out+=["knee/single-leg control"]
    if any("Foot" in x for x in findings): out+=["ankle/foot control"]
    if any(v in {"Limited","Poor","Pain"} for v in sfma.values()): out+=["movement quality"]
    if injuries and injuries!=["None"]: out+=["injury-aware loading"]
    return list(dict.fromkeys(out))
