# Drug Interaction Alert System Using Machine Learning (DIAS)

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![RDKit](https://img.shields.io/badge/Cheminformatics-RDKit-green.svg)](https://rdkit.org)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![SHAP](https://img.shields.io/badge/Explainability-SHAP-ff69b4.svg)](https://shap.readthedocs.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-8%20Passed-brightgreen.svg)]()

> **Machine Learning-Based Clinical Decision Support for Drug-Drug Interaction Review**  
> *A full-stack, production-grade Clinical Decision Support System (CDSS) prototype engineered to assist physicians and pharmacists in identifying potential adverse drug interactions, triaging severity, and understanding predictive factors through Explainable AI.*

---

## Important Clinical Safety Disclaimer

> [!IMPORTANT]
> **CLINICAL DECISION-SUPPORT PROTOTYPE NOTICE:**  
> This application is an educational and research decision-support prototype. It is **NOT** an autonomous prescribing system, **NOT** a diagnostic tool, **NOT** a replacement for licensed medical doctors or pharmacists, and **DOES NOT** guarantee medication safety. All predictions, severity classifications, and clinical guidance must be independently verified by a qualified healthcare professional before making any prescribing or patient-care decisions.

---

## System Architecture

```
                                  [ CLINICIAN / USER ]
                                           │
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │              React.js Frontend Dashboard               │
               │   (Vite + Plus Jakarta Sans + Lucide Icons + Recharts) │
               └───────────────────────────┬────────────────────────────┘
                                           │  REST API (JSON)
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │                 FastAPI REST Backend                   │
               │          (Lifespan Cache, CORS, Pydantic v2)           │
               └─────────────┬────────────────────────────┬─────────────┘
                             │                            │
                             ▼                            ▼
              ┌───────────────────────────┐  ┌───────────────────────────┐
              │     RDKit Cheminformatics │  │     Database Storage      │
              │  • Canonical SMILES       │  │  • SQLite (Local Fallback)│
              │  • 1024-bit Morgan ECFP4  │  │  • PostgreSQL (Production)│
              │  • Tanimoto & Descriptors │  │  • Alerts Audit Trail     │
              └──────────────┬────────────┘  └───────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────────────────────────────────┐
              │ Machine Learning & Explainable AI (XAI)                  │
              │  • Random Forest Ensemble (Champion Model: ROC-AUC 0.85) │
              │  • Benchmark Comparisons: Logistic Regression & XGBoost  │
              │  • SHAP TreeExplainer Local Attribution Quantification   │
              └──────────────────────────────────────────────────────────┘
```

---

## Key Features

- **Molecular Representation & Chemical Processing**: Parses canonical SMILES to generate 1024-bit Morgan Fingerprints (ECFP4), calculates pairwise Tanimoto structural similarity, and derives Lipinski physicochemical descriptors ($\text{MW}$, $\log P$, $\text{TPSA}$, $\text{HBD}$, $\text{HBA}$).
- **Multi-Algorithm ML Framework**: Rigorously benchmarked across **Logistic Regression**, **Random Forest**, and **XGBoost**, with the Random Forest champion model achieving **0.8485 ROC-AUC** and **0.8718 PR-AUC** on hold-out evaluation partitions.
- **Explainable AI via SHAP**: Integrates `shap.TreeExplainer` to compute exact directional Shapley attribution values for every feature on a per-interaction basis.
- **Severity Classification**: Triages interaction risk into **Major (Severe)**, **Moderate**, and **Minor (Mild)** tiers with pharmacological mechanism and clinical effect descriptions.
- **Clinician-Only Alternatives**: Displays evidence-based alternative therapies strictly for clinical evaluation; never substitutes medications autonomously.
- **Real Database Dashboard**: Live analytics generated from authentic SQLite/PostgreSQL records (Total Inquiries, Severity Distribution Donut Chart, 7-Day Activity Trends, Top Flagged Medications).
- **Audit History**: Searchable, filterable audit log of historical interaction alerts with detail modals and deletion capabilities.
- **Drug Catalog**: Searchable directory of verified pharmaceuticals with chemical formulas, SMILES preview, and molecular properties.

---

## Repository Structure

```
drug-interaction-alert-system/
├── frontend/                     # React.js SPA (Vite + Tailwind/CSS + Lucide Icons + Recharts)
│   ├── src/
│   │   ├── components/           # Navbar, Footer, RiskBadge
│   │   ├── pages/                # 8 Complete Views (Landing, Checker, History, Dashboard, Drugs, About, Disclaimer)
│   │   ├── services/api.js       # Centralized REST API client
│   │   ├── App.jsx & main.jsx    # Application router & entrypoint
│   │   └── index.css             # Healthcare design system tokens
│   ├── package.json & vite.config.js
│   └── vercel.json               # Optional Vercel deployment config
│
├── backend/                      # FastAPI Modular Backend
│   ├── app/
│   │   ├── main.py               # FastAPI application, CORS, lifespan handlers, static mount
│   │   ├── api/endpoints/        # health, drugs, interactions, alerts, dashboard, model_info
│   │   ├── database/             # connection.py (SQLite + Postgres), init_db.py
│   │   ├── models/               # SQLAlchemy ORM (Drug, DrugInteraction, Alert)
│   │   ├── schemas/              # Pydantic v2 validation models
│   │   ├── services/             # DrugService, InteractionService, AlertService, DashboardService
│   │   ├── ml/                   # MLPredictor, SHAPExplainerService
│   │   └── utils/                # Settings config, structured logger
│   └── requirements.txt
│
├── ml/                           # Offline Training & Evaluation Pipeline
│   ├── data/                     # Verified drugs & interactions database CSVs
│   ├── preprocessing/            # extract_features.py (RDKit Morgan ECFP4 + Descriptors)
│   ├── training/                 # train_pipeline.py (Multi-model trainer)
│   ├── evaluation/               # metrics.json (Actual reproducible evaluation data)
│   └── models/                   # champion_model.joblib, shap_explainer.joblib
│
├── tests/                        # Automated Pytest Suite (8 Comprehensive Suites)
├── docs/                         # research-paper-material.md, dataset docs
├── Dockerfile                    # Multi-stage production build (Node + Python)
├── docker-compose.yml            # Containerized App + PostgreSQL 16
├── render.yaml                   # One-click Render cloud deployment blueprint
├── .env.example                  # Environment configuration template
└── README.md
```

---

## Local Setup and Installation

### Prerequisites
- **Python 3.12+**
- **Node.js 20+** and **npm**
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/Afreentaj133/drug-interaction-alert-system.git
cd drug-interaction-alert-system
```

### 2. Set Up Python Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Install Frontend Dependencies & Build Bundle
```bash
cd frontend
npm install
npm run build
cd ..
```

### 5. Launch the Application
Start the FastAPI application (it serves both the REST API and the React frontend on a single port):
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser and navigate to:
- **Web Application**: `http://127.0.0.1:8000`
- **Interactive OpenAPI Documentation (Swagger UI)**: `http://127.0.0.1:8000/docs`

---

## Machine Learning Pipeline & Retraining

To execute feature extraction with RDKit and benchmark model training:

```bash
# Ensure virtual environment is active
python ml/training/train_pipeline.py
```

### Actual Experimental Benchmark Results (Hold-Out Test Set)
| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Baseline)** | 85.71% | 0.6250 | **0.8333** | 0.7143 | 0.8030 | 0.7121 |
| **Random Forest (Champion Ensemble)** | 82.14% | **1.0000** | 0.1667 | 0.2857 | **0.8485** | **0.8718** |
| **XGBoost (Gradient Boosting)** | **89.29%** | 0.8000 | 0.6667 | **0.7273** | 0.8182 | 0.7977 |

All evaluation metrics are serialized reproducibly to `ml/evaluation/metrics.json`.

---

## Running Automated Tests

Run the complete pytest test suite:
```bash
python -m pytest tests/ -v
```

Tests verified:
- `test_health.py`: Health endpoint status and uptime.
- `test_drug_api.py`: Search queries, partial matching, 404 on missing drug.
- `test_validation.py`: Reject same drug, reject empty drug, handle invalid input.
- `test_features.py`: RDKit molecule parsing, Morgan fingerprints, Tanimoto calculation, bad SMILES recovery.
- `test_predictions.py`: Predict known severe pair, predict low-risk pair, verify probability bounds [0.0, 1.0], verify severity strings.
- `test_shap.py`: Verify SHAP explanation array format and non-empty contributions.
- `test_alerts.py`: Verify alert creation in database, retrieval, and dashboard count increments.

---

## Docker Deployment

The application includes a production-ready, multi-stage `Dockerfile` and `docker-compose.yml` with PostgreSQL 16:

```bash
# Build and run the entire stack with Docker Compose
docker compose up --build
```
Access the application at `http://localhost:8000`.

---

## Cloud Deployment (Render / Vercel / Railway)

### One-Click Deploy to Render
The repository includes `render.yaml`:
1. Push this repository to GitHub.
2. Log into [Render Dashboard](https://dashboard.render.com).
3. Click **New +** -> **Blueprint** and select your GitHub repository.
4. Render will automatically detect `render.yaml`, spin up a managed PostgreSQL database, build the multi-stage Docker container, and provide a public HTTPS URL.

---

## Academic Project Attribution

**Department of Information Science and Engineering**  
**City Engineering College, Bangalore, Karnataka, India**

- **Project Guide:** Mrs. SWATHI S B, Assistant Professor
- **Team Members:**
  - AFREEN TAJ (USN: 1CE23IS006)
  - BHAVANA N (USN: 1CE23IS018)
  - BHOOMIKA MH (USN: 1CE23IS021)

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more details.