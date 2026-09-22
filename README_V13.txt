Athlete-IQ V13
By: Coach Ahmed Youssef

V13 focuses on the issues found during the first real V12 testing pass.

Changes:
- Height and body mass now influence normalized performance, relative-strength priorities and training decisions rather than being display-only intake values.
- Added Weight Loss and Weight Gain as explicit primary goals, with target-weight input.
- Posterior scapular screening now supports bilateral, right-sided and left-sided elevation/depression/winging/protraction observations.
- SFMA entries now include concrete coach-facing movement instructions and what to observe instead of generic placeholder text.
- Replaced mobile-unfriendly multi-select dropdowns with touch-friendly visible checkbox multi-selection.
- State-bound sliders were fixed so correcting a value no longer snaps back to the previous number after rerun.
- Dumbbell loading is implement-aware: bilateral DB prescriptions are shown as total pair load plus kg/hand, with a practical reference multiplier instead of treating a barbell 1RM as one dumbbell.
- General Fitness now has guaranteed whole-body resistance coverage across sessions, including upper-body pushing/pulling, and varied conditioning stimuli.
- Same-name duplicate exercise records are treated as the same stimulus for diversity.
- Soccer conditioning now rotates by month + week + day, not only month.
- Soccer main resistance selection is more diverse across the week while preserving limited same-week anchor re-exposure for progression.
- Screening correctives rotate across relevant choices and preserve left/right emphasis.
- Session Follow-Up now records the full session: warm-up, correctives, resistance, other main exercises, complex/athletic block, MetCon and session summary.
- Full-session feedback is stored and conditioning/load decisions can respond to difficult or painful session outcomes.
- Selected Month/Week/Day is stored correctly in the session log.

Validation:
- Python compile PASS.
- Existing V11/V12 regression suite PASS.
- V13 user-reported issue regression suite PASS.
- Previous General Fitness combat-drill leakage protection retained.
- Previous equipment filtering, sport/position separation, adaptive resistance loading, same-week anchor and MetCon variety protections retained.

Important:
- Screening observations are coaching/screening inputs, not medical diagnoses.
- BMI is used only as a broad contextual signal; it should not be treated as a standalone assessment of athletic body composition.
- Body-mass goals should be interpreted with sport demands, performance, readiness and appropriate nutrition/clinical guidance where relevant.
