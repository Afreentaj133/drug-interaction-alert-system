const drugASelect = document.getElementById("drugA");
const drugBSelect = document.getElementById("drugB");
const form = document.getElementById("interaction-form");
const loading = document.getElementById("loading");
const resultSection = document.getElementById("result-section");
const historyBody = document.getElementById("history-body");

async function loadDrugs() {
  try {
    const response = await fetch("/api/drugs");
    const data = await response.json();

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
    alert("Could not load the drug list. Is the backend running?");
  }
}

function setSeverityBadge(severity) {
  const badge = document.getElementById("severity-badge");
  badge.textContent = severity;
  badge.className = "severity-badge";

  const className = severity.toLowerCase();
  badge.classList.add(className);
}

function renderResult(result) {
  document.getElementById("pair-title").textContent =
    `${result.drug_a} + ${result.drug_b}`;

  document.getElementById("risk-score").textContent =
    `${(result.risk_probability * 100).toFixed(1)}%`;

  document.getElementById("source").textContent = result.source;
  document.getElementById("mechanism").textContent = result.mechanism;
  document.getElementById("clinical-effect").textContent = result.clinical_effect;
  document.getElementById("recommendation").textContent = result.recommendation;
  document.getElementById("alternative").textContent = result.safer_alternative;

  setSeverityBadge(result.severity);

  const explanationList = document.getElementById("explanation-list");
  explanationList.innerHTML = "";

  result.explanation.forEach((item) => {
    const listItem = document.createElement("li");
    listItem.textContent = item;
    explanationList.appendChild(listItem);
  });

  resultSection.classList.remove("hidden");
  resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function loadHistory() {
  try {
    const response = await fetch("/api/recent-alerts");
    const data = await response.json();

    historyBody.innerHTML = "";

    if (!data.alerts.length) {
      historyBody.innerHTML =
        '<tr><td colspan="5">No checks yet.</td></tr>';
      return;
    }

    data.alerts.forEach((alert) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${alert.drug_a} + ${alert.drug_b}</td>
        <td>${alert.severity}</td>
        <td>${(alert.risk_probability * 100).toFixed(1)}%</td>
        <td>${alert.source}</td>
        <td>${alert.created_at}</td>
      `;
      historyBody.appendChild(row);
    });
  } catch (error) {
    console.error("Could not load history", error);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const drugA = drugASelect.value;
  const drugB = drugBSelect.value;

  if (!drugA || !drugB) {
    alert("Please select both drugs.");
    return;
  }

  if (drugA === drugB) {
    alert("Please select two different drugs.");
    return;
  }

  loading.classList.remove("hidden");
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
      throw new Error(data.detail || "Unable to analyse this drug pair.");
    }

    renderResult(data);
    loadHistory();
  } catch (error) {
    alert(error.message);
  } finally {
    loading.classList.add("hidden");
  }
});

document.getElementById("refresh-history").addEventListener("click", loadHistory);

loadDrugs();
loadHistory();