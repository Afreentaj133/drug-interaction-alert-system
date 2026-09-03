const drugASelect = document.getElementById("drugA");
const drugBSelect = document.getElementById("drugB");
const form = document.getElementById("interaction-form");
const loading = document.getElementById("loading");
const resultSection = document.getElementById("result-section");
const historyBody = document.getElementById("history-body");
const submitButton = document.getElementById("analyze-button");
const refreshHistoryButton = document.getElementById("refresh-history");


function formatRiskScore(probability) {
  const numericProbability = Number(probability);

  if (Number.isNaN(numericProbability)) {
    return "0.0%";
  }

  return `${(numericProbability * 100).toFixed(1)}%`;
}


function getSeverityClass(severity) {
  return String(severity || "Not Assessed")
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "-");
}


function setSeverityBadge(severity) {
  const badge = document.getElementById("severity-badge");
  const normalizedSeverity = severity || "Not Assessed";

  badge.textContent = normalizedSeverity;
  badge.className = `severity-badge ${getSeverityClass(normalizedSeverity)}`;
}


function setInteractionStatus(interactionDetected) {
  const statusElement = document.getElementById("interaction-status");

  if (interactionDetected) {
    statusElement.textContent = "Potential interaction detected";
    statusElement.className = "interaction-status detected";
  } else {
    statusElement.textContent =
      "No significant interaction predicted by this prototype";
    statusElement.className = "interaction-status no-alert";
  }
}


function updateRiskMeter(probability) {
  const numericProbability = Number(probability);
  const percentage = Number.isNaN(numericProbability)
    ? 0
    : Math.min(Math.max(numericProbability * 100, 0), 100);

  document.getElementById("risk-meter-value").textContent =
    `${percentage.toFixed(1)}%`;

  document.getElementById("risk-fill").style.width =
    `${percentage}%`;
}


function clearDrugOptions() {
  drugASelect.innerHTML = '<option value="">Select Drug A</option>';
  drugBSelect.innerHTML = '<option value="">Select Drug B</option>';
}


async function loadDrugs() {
  try {
    const response = await fetch("/api/drugs");

    if (!response.ok) {
      throw new Error("Unable to load the prototype drug database.");
    }

    const data = await response.json();

    if (!Array.isArray(data.drugs)) {
      throw new Error("The backend returned an invalid drug list.");
    }

    clearDrugOptions();

    data.drugs.forEach((drug) => {
      const optionA = document.createElement("option");
      optionA.value = drug;
      optionA.textContent = drug;
      drugASelect.appendChild(optionA);

      const optionB = document.createElement("option");
      optionB.value = drug;
      optionB.textContent = drug;
      drugBSelect.appendChild(optionB);
    });
  } catch (error) {
    console.error("Could not load drugs:", error);
    alert(
      "Could not load the drug list. Please confirm that the backend is running."
    );
  }
}


function renderExplanation(explanation) {
  const explanationList = document.getElementById("explanation-list");
  explanationList.innerHTML = "";

  const items = Array.isArray(explanation)
    ? explanation
    : ["No feature-level explanation was returned by the prototype."];

  items.forEach((item) => {
    const listItem = document.createElement("li");
    listItem.textContent = item;
    explanationList.appendChild(listItem);
  });
}


function renderResult(result) {
  const riskScore = formatRiskScore(result.risk_probability);

  document.getElementById("pair-title").textContent =
    `${result.drug_a} + ${result.drug_b}`;

  document.getElementById("risk-score").textContent = riskScore;

  document.getElementById("source").textContent =
    result.source || "Machine-learning prototype";

  document.getElementById("mechanism").textContent =
    result.mechanism || "No mechanism information available.";

  document.getElementById("clinical-effect").textContent =
    result.clinical_effect || "No clinical-effect information available.";

  document.getElementById("recommendation").textContent =
    result.recommendation || "Clinical review is recommended.";

  document.getElementById("alternative").textContent =
    result.safer_alternative ||
    "No alternative information is available in the prototype dataset.";

  setSeverityBadge(result.severity);
  setInteractionStatus(Boolean(result.interaction_detected));
  updateRiskMeter(result.risk_probability);
  renderExplanation(result.explanation);

  resultSection.classList.remove("hidden");

  resultSection.scrollIntoView({
    behavior: "smooth",
    block: "start"
  });
}


function createTableCell(value) {
  const cell = document.createElement("td");
  cell.textContent = value;
  return cell;
}


function createSeverityCell(severity) {
  const cell = document.createElement("td");
  const badge = document.createElement("span");

  badge.textContent = severity || "Not Assessed";
  badge.className = `severity-badge ${getSeverityClass(severity)}`;

  cell.appendChild(badge);
  return cell;
}


async function loadHistory() {
  try {
    const response = await fetch("/api/recent-alerts");

    if (!response.ok) {
      throw new Error("Unable to load alert history.");
    }

    const data = await response.json();
    const alerts = Array.isArray(data.alerts) ? data.alerts : [];

    historyBody.innerHTML = "";

    if (alerts.length === 0) {
      const row = document.createElement("tr");
      const cell = document.createElement("td");

      cell.colSpan = 5;
      cell.textContent = "No checks have been saved yet.";

      row.appendChild(cell);
      historyBody.appendChild(row);
      return;
    }

    alerts.forEach((alert) => {
      const row = document.createElement("tr");

      row.appendChild(
        createTableCell(`${alert.drug_a} + ${alert.drug_b}`)
      );

      row.appendChild(createSeverityCell(alert.severity));

      row.appendChild(
        createTableCell(formatRiskScore(alert.risk_probability))
      );

      row.appendChild(
        createTableCell(alert.source || "Prototype prediction")
      );

      row.appendChild(
        createTableCell(alert.created_at || "Not available")
      );

      historyBody.appendChild(row);
    });
  } catch (error) {
    console.error("Could not load history:", error);

    historyBody.innerHTML = "";

    const row = document.createElement("tr");
    const cell = document.createElement("td");

    cell.colSpan = 5;
    cell.textContent =
      "Could not load alert history. Please refresh and try again.";

    row.appendChild(cell);
    historyBody.appendChild(row);
  }
}


function setLoadingState(isLoading) {
  if (isLoading) {
    loading.classList.remove("hidden");
    submitButton.disabled = true;
    submitButton.textContent = "Analysing Interaction...";
    return;
  }

  loading.classList.add("hidden");
  submitButton.disabled = false;
  submitButton.textContent = "Check Interaction";
}


form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const drugA = drugASelect.value.trim();
  const drugB = drugBSelect.value.trim();

  if (!drugA || !drugB) {
    alert("Please select both Drug A and Drug B.");
    return;
  }

  if (drugA.toLowerCase() === drugB.toLowerCase()) {
    alert("Please select two different drugs.");
    return;
  }

  setLoadingState(true);
  resultSection.classList.add("hidden");

  try {
    const response = await fetch("/api/check-interaction", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        drug_a: drugA,
        drug_b: drugB
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Unable to analyse this drug pair."
      );
    }

    renderResult(data);
    await loadHistory();
  } catch (error) {
    console.error("Prediction request failed:", error);
    alert(error.message || "Something went wrong while analysing the drug pair.");
  } finally {
    setLoadingState(false);
  }
});


refreshHistoryButton.addEventListener("click", async () => {
  refreshHistoryButton.disabled = true;
  refreshHistoryButton.textContent = "Refreshing...";

  try {
    await loadHistory();
  } finally {
    refreshHistoryButton.disabled = false;
    refreshHistoryButton.textContent = "↻ Refresh";
  }
});


loadDrugs();
loadHistory();