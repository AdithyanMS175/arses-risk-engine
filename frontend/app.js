const API_BASE = "http://localhost:8000";

const els = {
  form: document.getElementById("riskForm"),
  userId: document.getElementById("userId"),
  amount: document.getElementById("amount"),
  locationRisk: document.getElementById("locationRisk"),
  locationRiskValue: document.getElementById("locationRiskValue"),
  activity: document.getElementById("activity"),
  evaluateBtn: document.getElementById("evaluateBtn"),
  statusText: document.getElementById("statusText"),
  errorBox: document.getElementById("errorBox"),

  riskScore: document.getElementById("riskScore"),
  riskLevel: document.getElementById("riskLevel"),
  confidenceValue: document.getElementById("confidenceValue"),
  confidenceBar: document.getElementById("confidenceBar"),

  metaBtn: document.getElementById("metaTooltipBtn"),
  metaTooltip: document.getElementById("metaTooltip"),
  metaModel: document.getElementById("metaModel"),
  metaTimestamp: document.getElementById("metaTimestamp"),
  metaCompleteness: document.getElementById("metaCompleteness"),

  statTotal: document.getElementById("statTotal"),
  statAvg: document.getElementById("statAvg"),
  statLow: document.getElementById("statLow"),
  statMedium: document.getElementById("statMedium"),
  statHigh: document.getElementById("statHigh"),

  apiBase: document.getElementById("apiBase"),
};

els.apiBase.textContent = API_BASE;

const results = [];

function setError(message) {
  if (!message) {
    els.errorBox.classList.add("hidden");
    els.errorBox.textContent = "";
    return;
  }
  els.errorBox.textContent = message;
  els.errorBox.classList.remove("hidden");
}

function setLoading(isLoading, text = "") {
  els.evaluateBtn.disabled = isLoading;
  els.statusText.textContent = text;
}

function riskColor(level) {
  if (level === "LOW") return { text: "text-emerald-300", bar: "bg-emerald-500" };
  if (level === "MEDIUM") return { text: "text-amber-300", bar: "bg-amber-500" };
  if (level === "HIGH") return { text: "text-rose-300", bar: "bg-rose-500" };
  return { text: "text-slate-200", bar: "bg-slate-500" };
}

function renderStats() {
  els.statTotal.textContent = String(results.length);
  if (results.length === 0) {
    els.statAvg.textContent = "—";
    els.statLow.textContent = "0";
    els.statMedium.textContent = "0";
    els.statHigh.textContent = "0";
    return;
  }
  const sum = results.reduce((acc, r) => acc + r.risk_score, 0);
  const avg = Math.round((sum / results.length) * 10) / 10;
  els.statAvg.textContent = String(avg);

  const counts = { LOW: 0, MEDIUM: 0, HIGH: 0 };
  for (const r of results) counts[r.risk_level] = (counts[r.risk_level] || 0) + 1;
  els.statLow.textContent = String(counts.LOW || 0);
  els.statMedium.textContent = String(counts.MEDIUM || 0);
  els.statHigh.textContent = String(counts.HIGH || 0);
}

function renderResult(res) {
  els.riskScore.textContent = String(res.risk_score);
  els.riskLevel.textContent = res.risk_level;
  els.confidenceValue.textContent = `${res.metadata.confidence}%`;

  const colors = riskColor(res.risk_level);
  els.riskLevel.classList.remove("text-emerald-300", "text-amber-300", "text-rose-300", "text-slate-200");
  els.riskLevel.classList.add(colors.text);

  els.confidenceBar.style.width = `${res.metadata.confidence}%`;
  els.confidenceBar.classList.remove("bg-emerald-500", "bg-amber-500", "bg-rose-500", "bg-slate-500");
  els.confidenceBar.classList.add(colors.bar);

  els.metaModel.textContent = res.metadata.model_version;
  els.metaTimestamp.textContent = new Date(res.metadata.timestamp).toISOString();
  els.metaCompleteness.textContent = `${res.metadata.data_completeness}%`;
}

async function evaluateRisk(payload) {
  const resp = await fetch(`${API_BASE}/evaluate-risk`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  let data;
  try {
    data = await resp.json();
  } catch {
    data = null;
  }

  if (!resp.ok) {
    const detail = data?.detail ? String(data.detail) : `HTTP ${resp.status}`;
    throw new Error(detail);
  }
  return data;
}

els.locationRisk.addEventListener("input", () => {
  els.locationRiskValue.textContent = Number(els.locationRisk.value).toFixed(2);
});

els.metaBtn.addEventListener("mouseenter", () => {
  els.metaTooltip.classList.remove("hidden");
});
els.metaBtn.addEventListener("mouseleave", () => {
  els.metaTooltip.classList.add("hidden");
});

els.form.addEventListener("submit", async (e) => {
  e.preventDefault();
  setError("");

  const payload = {
    user_id: els.userId.value.trim(),
    transaction_amount: Number(els.amount.value),
    location_risk: Number(els.locationRisk.value),
    activity_type: els.activity.value,
  };

  if (!payload.user_id) {
    setError("User ID is required.");
    return;
  }
  if (!Number.isFinite(payload.transaction_amount) || payload.transaction_amount < 0) {
    setError("Transaction Amount must be a valid non-negative number.");
    return;
  }
  if (!Number.isFinite(payload.location_risk) || payload.location_risk < 0 || payload.location_risk > 1) {
    setError("Location Risk must be between 0 and 1.");
    return;
  }

  try {
    setLoading(true, "Evaluating…");
    const res = await evaluateRisk(payload);
    renderResult(res);
    results.push(res);
    renderStats();
    setLoading(false, "Done");
    setTimeout(() => {
      if (els.statusText.textContent === "Done") els.statusText.textContent = "";
    }, 1200);
  } catch (err) {
    setLoading(false, "");
    setError(
      `Request failed. Make sure the backend is running at ${API_BASE}. Details: ${err?.message || err}`
    );
  }
});

renderStats();

