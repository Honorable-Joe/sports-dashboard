# Athlete-IQ V9

A Streamlit sports performance planning prototype with automatic regeneration.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Architecture

- `app.py` — UI and automatic plan regeneration
- `engine.py` — closed-loop selection and periodization engine
- `exercises.py` — exercise database and metadata
- `sports.py` — sports and position/specialization definitions
- `screening.py` — screening extension point
- `periodization.py` — periodization extension point

All source files are UTF-8. Exercise names intentionally use standard ASCII characters to avoid the mobile encoding corruption seen in earlier versions.
