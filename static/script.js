const drugASelect = document.getElementById("drugA");
const drugBSelect = document.getElementById("drugB");
const form = document.getElementById("interaction-form");
const loading = document.getElementById("loading");
const resultSection = document.getElementById("result-section");
const historyBody = document.getElementById("history-body");
const submitButton = form.querySelector('button[type="submit"]');


async function loadDrugs() {
  try {
    const response = await fetch("/api/drugs");

    if (!response.ok) {
      throw new Error("Unable to load the drug list.");
    }

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
    console.error(error);
  }
}


function setSeverityBadge(severity) {
  const badge = document.getElementById("severity-badge");

  const severityClass = severity
    .toLowerCase()
    .replace(/\s+/g, "-");

  badge.textContent = severity;
  badge.className = `severity-badge ${severityClass}`;
}


function setInteractionStatus(interactionDetected) {
  const statusElement = document.getElementById("interaction-status");

  if (!statusElement) {
    return;
  }

  if (interactionDetected) {
    statusElement.textContent = "Potential interaction detected";
    statusElement.className = "interaction-status detected";
  } else {
    statusElement.textContent =
      "No significant interaction predicted by this prototype";
    statusElement.className = "interaction-status no-alert";
  }
}


function renderResult(result) {
  document.getElementById("pair-title").textContent =
    `${result.drug_a} + ${result.drug_b}`;

  document.getElementById("risk-score").textContent =
    `${(result.risk_probability * 100).toFixed(1)}%`;

  document.getElementById("source").textContent = result.source;
  document.getElementById("mechanism").textContent = result.mechanism;
  document.getElementById("clinical-effect").textContent =
    result.clinical_effect;
  document.getElementById("recommendation").textContent =
    result.recommendation;
  document.getElementById("alternative").textContent =
    result.safer_alternative;

  setSeverityBadge(result.severity);
  setInteractionStatus(result.interaction_detected);

  const explanationList = document.getElementById("explanation-list");
  explanationList.innerHTML = "";

  result.explanation.forEach((item) => {
    const listItem = document.createElement("li");
    listItem.textContent = item;
    explanationList.appendChild(listItem);
  });

  resultSection.classList.remove("hidden");
  resultSection.scrollIntoView({
    behavior: "smooth",
    block: "start"
  });
}


function createCell(value) {
  const cell = document.createElement("td");
  cell.textContent = value;
  return cell;
}


async function loadHistory() {
  try {
    const response = await fetch("/api/recent-alerts");

    if (!response.ok) {
      throw new Error("Unable to load alert history.");
    }

    const data = await response.json();
    historyBody.innerHTML = "";

    if (!data.alerts.length) {
      historyBody.innerHTML =
        '<tr><td colspan="5">No checks yet.</td></tr>';
      return;
    }

    data.alerts.forEach((alert) => {
      const row = document.createElement("tr");

      row.appendChild(
        createCell(`${alert.drug_a} + ${alert.drug_b}`)
      );
      row.appendChild(createCell(alert.severity));
      row.appendChild(
        createCell(`${(alert.risk_probability * 100).toFixed(1)}%`)
      );
      row.appendChild(createCell(alert.source));
      row.appendChild(createCell(alert.created_at));

      historyBody.appendChild(row);
    });
  } catch (error) {
    console.error("Could not load history.", error);
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
  submitButton.disabled = true;
  submitButton.textContent = "Analyzing...";

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
        data.detail || "Unable to analyze this drug pair."
      );
    }

    renderResult(data);
    await loadHistory();
  } catch (error) {
    alert(error.message);
    console.error(error);
  } finally {
    loading.classList.add("hidden");
    submitButton.disabled = false;
    submitButton.textContent = "Check Interaction";
  }
});


document
  .getElementById("refresh-history")
  .addEventListener("click", loadHistory);


loadDrugs();
loadHistory();