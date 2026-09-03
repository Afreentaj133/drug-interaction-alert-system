# Drug Interaction Alert System Using Machine Learning

An educational final-year project that screens drug pairs for known interactions and uses a Random Forest model to estimate potential interaction risk.

## Features

- Drug-pair interaction screening
- Known-interaction lookup from curated prototype data
- Random Forest ML risk prediction
- Minor, Moderate, and Major severity categories
- Explainability through active feature indicators
- Suggested lower-risk alternative information
- FastAPI REST API
- Web dashboard
- SQLite alert history
- Docker-ready deployment

## Technology Stack

- Python
- FastAPI
- Scikit-learn
- Pandas
- SQLite
- HTML, CSS, JavaScript
- Joblib
- Docker
- Render

## Run Locally

```bash
python -m venv .venv
```

Activate the virtual environment and run:

```bash
pip install -r requirements.txt
python train_model.py
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Important Disclaimer

This project is an educational decision-support prototype. It is not medical advice and must not be used for autonomous prescribing or real clinical decisions.