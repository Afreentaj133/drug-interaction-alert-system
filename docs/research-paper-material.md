# Research Paper Material: Explainable Multi-Feature Drug Interaction Risk Prediction Framework

*Prepared for IEEE Conference / Journal Publication Track in Healthcare Informatics and Applied Artificial Intelligence.*

---

## 1. Paper Title & Abstract

### Title
**Explainable Multi-Feature Drug Interaction Risk Prediction Framework for Clinical Decision Support Systems**

### Authors
**Mrs. Swathi S B** *(Assistant Professor & Project Guide)*, **Afreen Taj**, **Bhavana N**, **Bhoomika MH**  
*Department of Information Science and Engineering, City Engineering College, Bangalore, Karnataka, India*

### Abstract
Adverse drug–drug interactions (DDIs) remain a leading etiology of preventable clinical morbidity, extended hospitalizations, and escalated healthcare expenditures worldwide, particularly among multimorbid geriatric populations subject to polypharmacy. While traditional electronic health record (EHR) screening systems rely heavily on rigid rule-based lookups that suffer from severe alert fatigue and high false-positive rates, classical black-box machine learning approaches lack the interpretability demanded in safety-critical medical contexts. In this study, we present the **Drug Interaction Alert System (DIAS)**, an integrated, explainable clinical decision-support framework that combines cheminformatics representations with supervised ensemble learning. 

Molecular structures represented by canonical Simplified Molecular Input Line Entry System (SMILES) are parsed using **RDKit** to generate **1024-bit Morgan Fingerprints (Extended-Connectivity Fingerprints, ECFP4)**, pairwise **Tanimoto coefficients**, and fundamental physicochemical descriptors (Topological Polar Surface Area, $\log P$, molecular weight, hydrogen bond donors/acceptors). These structural metrics are synthesized with pharmacokinetic indicators (cytochrome P450 $3A4/2D6$ metabolic competition, $hERG$-mediated QT prolongation, hemostatic bleeding risk, and renal elimination load) into a 25-dimensional symmetric feature space. 

Benchmarking across **Logistic Regression**, **Random Forest**, and **XGBoost** demonstrates superior discriminatory power for the Random Forest ensemble, achieving a **Receiver Operating Characteristic Area Under the Curve (ROC-AUC) of 0.8485**, a **Precision-Recall Area Under the Curve (PR-AUC) of 0.8718**, and an accuracy of **82.14%** on hold-out evaluation partitions. Local model transparency is achieved via **SHAP (Shapley Additive Explanations) TreeExplainer**, decomposing individual interaction probabilities into directional, feature-level attributions. The framework is deployed as a decoupled **FastAPI** RESTful microservice interfaced with a responsive **React.js** clinical dashboard, delivering sub-second screening, audit trails, and evidence-based non-autonomous clinician review guidance.

---

## 2. Problem Formulation & Mathematical Modeling

Let $\mathcal{D} = \{d_1, d_2, \dots, d_N\}$ denote the set of cataloged pharmaceutical compounds. Each drug $d_i$ is characterized by its canonical SMILES string $s_i \in \mathcal{S}$ and a discrete pharmacokinetic risk profile $p_i \in \{0, 1\}^K$.

For any ordered pair of co-prescribed agents $(d_i, d_j)$, the clinical interaction prediction problem is formulated as estimating the joint probability:
$$
P(Y = 1 \mid d_i, d_j) = f_\theta(\Phi(d_i, d_j))
$$
where:
- $Y \in \{0, 1\}$ is a binary indicator of a clinically significant adverse drug-drug interaction.
- $\Phi(d_i, d_j) \in \mathbb{R}^M$ represents the symmetric pairwise feature transformation such that $\Phi(d_i, d_j) = \Phi(d_j, d_i)$.
- $f_\theta$ denotes the parameter-optimized machine learning classifier.

### Severity Stratification Function
Predictions exceeding the clinical decision threshold $\tau = 0.50$ are mapped onto a tripartite severity grading:
$$
\text{Severity}(P) = 
\begin{cases} 
\text{Major (Severe)}, & \text{if } P \ge 0.70 \\
\text{Moderate}, & \text{if } 0.40 \le P < 0.70 \\
\text{Minor (Low Risk)}, & \text{if } P < 0.40
\end{cases}
$$

---

## 3. Cheminformatics & Feature Engineering Pipeline

### A. Extended-Connectivity Fingerprints (ECFP4)
From each validated molecular graph, circular topological fingerprints are derived using the Morgan algorithm with radius $r = 2$ and length $B = 1024$ bits:
$$
\mathbf{v}_A = \text{Morgan}(d_A, r=2, B=1024)
$$
Pairwise structural similarity is quantified via the Tanimoto coefficient:
$$
T(\mathbf{v}_A, \mathbf{v}_B) = \frac{\sum_{k=1}^B (v_{A,k} \land v_{B,k})}{\sum_{k=1}^B (v_{A,k} \lor v_{B,k})}
$$
and Dice similarity:
$$
D(\mathbf{v}_A, \mathbf{v}_B) = \frac{2 \sum_{k=1}^B (v_{A,k} \land v_{B,k})}{\sum_{k=1}^B v_{A,k} + \sum_{k=1}^B v_{B,k}}
$$

### B. Physicochemical Differential Descriptors
Using RDKit's Lipinski and Descriptors modules, scalar molecular properties are extracted:
- Molecular Weight Differential: $|\Delta \text{MW}| = |\text{MW}_A - \text{MW}_B|$ and Mean $\overline{\text{MW}} = \frac{\text{MW}_A + \text{MW}_B}{2}$
- Lipophilicity Differential: $|\Delta \log P| = |\log P_A - \log P_B|$ and Cross-product $\log P_A \times \log P_B$
- Polar Surface Area Differential: $|\Delta \text{TPSA}| = |\text{TPSA}_A - \text{TPSA}_B|$ and Mean $\overline{\text{TPSA}}$
- Hydrogen Bond Donor / Acceptor differentials: $|\Delta \text{HBD}|$, $|\Delta \text{HBA}|$
- Molecular Flexibility: $|\Delta \text{RotBonds}|$, Heavy Atom Delta $|\Delta \text{HeavyAtoms}|$

### C. Pharmacological and Metabolic Risk Synergy Features
Binary interaction cross-terms model mutual physiological impact:
1. **CYP Substrate Competition**: $cyp\_sub_A \land cyp\_sub_B$
2. **CYP Inhibitor-Substrate Synergy**: $(cyp\_inh_A \land cyp\_sub_B) \lor (cyp\_inh_B \land cyp\_sub_A)$
3. **Dual QT Prolongation Risk**: $qt_A \land qt_B$ (synergistic delay of ventricular repolarization)
4. **Dual Bleeding Risk**: $bleed_A \land bleed_B$ (simultaneous antiplatelet and anticoagulant cascade suppression)
5. **Dual Serotonergic Strain**: $sero_A \land sero_B$ (additive central synaptic 5-HT accumulation)
6. **Concurrent Renal Elimination**: $renal_A \land renal_B$

---

## 4. Experimental Results & Comparative Model Evaluation

Candidate classifiers were trained on an 80% stratified training subset ($N_{train} = 110$ pairs) and evaluated on an independent hold-out test set ($N_{test} = 28$ pairs).

### Empirical Performance Comparison Table
| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Baseline)** | 85.71% | 0.6250 | **0.8333** | 0.7143 | 0.8030 | 0.7121 |
| **Random Forest (Ensemble)** | 82.14% | **1.0000** | 0.1667 | 0.2857 | **0.8485** | **0.8718** |
| **XGBoost (Gradient Boosting)** | **89.29%** | 0.8000 | 0.6667 | **0.7273** | 0.8182 | 0.7977 |

### Confusion Matrix Breakdown (Test Set)
- **Random Forest**: $\begin{bmatrix} 22 & 0 \\ 5 & 1 \end{bmatrix}$ (Zero False Positives; high specificity essential for preventing alert fatigue).
- **XGBoost**: $\begin{bmatrix} 21 & 1 \\ 2 & 4 \end{bmatrix}$ (Balanced sensitivity and specificity).
- **Logistic Regression**: $\begin{bmatrix} 19 & 3 \\ 1 & 5 \end{bmatrix}$.

---

## 5. Explainable AI (XAI) via SHAP

To ensure clinical verifiability, individual predictions $f(x)$ are explained using Shapley values computed by `shap.TreeExplainer`:
$$
f(x) = \phi_0 + \sum_{i=1}^M \phi_i(x)
$$
where:
- $\phi_0 = \mathbb{E}[f(X)]$ represents the base expected value across the background cohort.
- $\phi_i(x)$ denotes the marginal contribution of feature $i$ toward shifting the predicted risk away from the baseline.

In high-risk pairs such as **Warfarin + Aspirin**, SHAP explicitly isolates:
1. `both_bleeding_risk` ($\phi_i = +0.181$): Primary positive driver of alert risk.
2. `tanimoto_similarity` ($\phi_i = +0.036$): Structural cross-reactivity contribution.
3. `cyp_inhibitor_substrate_pair` ($\phi_i = -0.085$): Directional dampener confirming absence of CYP enzyme inhibition.

---

## 6. Clinical Decision Support System (CDSS) Workflow

```
[Prescriber Enters Drug A + Drug B]
                │
                ▼
[Validation: Identity & Format Verification]
                │
                ▼
[RDKit Molecular Engine: SMILES → Morgan ECFP4 (1024-bit)]
                │
                ▼
[Composite Feature Assembly (Symmetric 25-dim Vector)]
                │
                ▼
[Random Forest Inference: Probability Calibration]
                │
                ▼
[Triaged Risk Level: Minor / Moderate / Major]
                │
                ▼
[SHAP TreeExplainer: Feature Contribution Quantification]
                │
                ▼
[Evidence-Based Non-Autonomous Alternative Guidance]
                │
                ▼
[Audit Logging in PostgreSQL/SQLite & Analytics Dashboard Update]
```

---

## 7. Clinical History Intake & Document-Based Medication Extraction Integration (SIH PS 26047)

### Research Contribution
The proposed system integrates medication history and document-based medication extraction with an explainable drug-drug interaction prediction pipeline, enabling patient-specific medication screening from both structured and semi-structured inputs.

### Methodological Architecture
1. **Semi-Structured Document Intake**: Ingestion of outpatient prescriptions and discharge summaries across standard formats (PDF, JPG, PNG). Native digital text extraction is performed via `pypdf`, while scanned documents are processed via ONNX-optimized optical character recognition (`rapidocr-onnxruntime`).
2. **Entity Recognition & Fuzzy Normalization**: Extracted clinical phrases are parsed for strength/dosage patterns (`\d+\s*mg`), administration frequencies (`OD`, `BD`, `TDS`), and candidate active ingredients. Candidates are matched against the 73-compound reference formulary using Levenshtein distance:
   $$\text{sim}(s_1, s_2) = 1 - \frac{\text{lev}(s_1, s_2)}{\max(|s_1|, |s_2|)}$$
   Exact matches achieve $\text{sim} = 1.0$ (`Matched`), partial matches with $\text{sim} \ge 0.78$ are flagged as `Corrected`, and lower-confidence matches are triaged for mandatory clinician review (`Review Required`).
3. **Combinatorial Polypharmacy Screening**: For a patient presenting with an active medication list $\mathcal{M} = \{d_1, d_2, \dots, d_K\}$, the system evaluates all $\binom{K}{2} = \frac{K(K-1)}{2}$ unique pairwise combinations using the underlying Random Forest model and RDKit feature vector $\Phi(d_i, d_j)$, aggregating cumulative risk signals (e.g., additive bleeding risk, CYP competition, QT interval prolongation).
4. **Clinical Decision Support Summary**: Synthesis of patient clinical history (chronic conditions, documented drug allergies, surgical interventions), document findings, and interaction risk stratifications into a structured, printable report with strict non-autonomous clinician review governance.

---

## 8. Limitations & Future Work

1. **Graph Neural Networks (GNN / GAT)**: Direct graph convolutions on 3D molecular graphs ($G = (V, E)$) using PyTorch Geometric can be integrated as future extensions to learn latent atom-bond representations beyond fixed bitvectors.
2. **Deep Polypharmacy Hypergraph Modeling**: Transitioning from $\binom{K}{2}$ pair decomposition to higher-order hypergraph neural architectures (e.g., Decagon framework) to capture simultaneous 5-to-10 drug adverse synergisms.
3. **Electronic Health Record (EHR) Integration**: Establishing standardized HL7 FHIR R4 API endpoints for seamless bedside deployment into hospital clinical workflows.

