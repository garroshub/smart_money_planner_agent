const state = {
  users: [],
  accounts: [],
  goals: [],
  presets: [],
};

const elements = {};

const select = (id) => document.getElementById(id);

const fetchJson = async (path) => {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Failed to load ${path}`);
  }
  return response.json();
};

const loadData = async () => {
  const [users, accounts, goals, presets] = await Promise.all([
    fetchJson("data/mock/users.json"),
    fetchJson("data/mock/accounts.json"),
    fetchJson("data/mock/goals.json"),
    fetchJson("data/presets/preset_outputs.json"),
  ]);

  state.users = users;
  state.accounts = accounts;
  state.goals = goals;
  state.presets = presets;
};

const getAccountForUser = (userId) =>
  state.accounts.find((account) => account.user_id === userId) || { cash: 0, debts: [], investments: [] };

const getGoalsForUser = (userId) =>
  state.goals.filter((goal) => goal.user_id === userId).map((goal) => goal.goals_text);

const cleanInline = (text) =>
  String(text || "")
    .replace(/\*\*/g, "")
    .replace(/__/g, "")
    .replace(/[*_`]/g, "")
    .replace(/(\d)([A-Za-z])/g, "$1 $2")
    .replace(/([A-Za-z]),([A-Za-z])/g, "$1, $2")
    .replace(/\s+/g, " ")
    .trim();

const showResults = () => {
  elements.resultsSection.classList.remove("results-hidden");
};

const htmlEscape = (text) =>
  String(text || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

const asCurrency = (value) => `$${Math.round(value).toLocaleString()}`;

const sumDebt = (accounts) => accounts.debts.reduce((sum, item) => sum + (item.balance || 0), 0);

const sumInvestments = (accounts) => accounts.investments.reduce((sum, item) => sum + (item.balance || 0), 0);

const minPayments = (accounts) => accounts.debts.reduce((sum, item) => sum + (item.min_payment || 0), 0);

const weightedApr = (accounts) => {
  const debts = accounts.debts.filter((item) => (item.balance || 0) > 0);
  const total = debts.reduce((sum, item) => sum + (item.balance || 0), 0);
  if (!total) return 0;
  const weighted = debts.reduce((sum, item) => sum + (item.balance || 0) * (item.apr || 0), 0);
  return weighted / total;
};

const buildPlanRows = (plans, disposable) =>
  plans.map((plan) => {
    const emergency = plan.actions.find((a) => a.type === "Emergency fund")?.amount || 0;
    const debt = plan.actions.find((a) => a.type === "Debt payment")?.amount || 0;
    const invest = plan.actions.find((a) => a.type === "Invest")?.amount || 0;
    const total = emergency + debt + invest;
    const approvals = plan.actions.filter((a) => a.requires_human_approval).length;
    const utilization = disposable > 0 ? (total / disposable) * 100 : 0;
    return {
      name: plan.name,
      score: plan.score,
      emergency,
      debt,
      invest,
      total,
      utilization: Math.round(utilization * 10) / 10,
      approvals,
    };
  });

const pickRecommendation = (rows) =>
  rows
    .slice()
    .sort((a, b) =>
      b.score - a.score || b.debt - a.debt || b.emergency - a.emergency || b.invest - a.invest
    )[0];

const renderPlanTable = (rows, recommendedName) => {
  const tbody = elements.planTable.querySelector("tbody");
  tbody.innerHTML = "";
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    const isRecommended = Boolean(recommendedName && row.name === recommendedName);
    if (recommendedName && row.name === recommendedName) {
      tr.classList.add("is-recommended");
    }
    const planCell = isRecommended
      ? `<span class="plan-name">${row.name}</span><span class="badge-recommended">Recommended</span>`
      : `<span class="plan-name">${row.name}</span>`;
    tr.innerHTML = `
      <td>${planCell}</td>
      <td>${row.score}</td>
      <td>${asCurrency(row.emergency)}</td>
      <td>${asCurrency(row.debt)}</td>
      <td>${asCurrency(row.invest)}</td>
      <td>${asCurrency(row.total)}</td>
      <td>${row.utilization}%</td>
      <td>${row.approvals}</td>
    `;
    tbody.appendChild(tr);
  });
};

const renderNarrativeHtml = (rawText) => {
  const lines = String(rawText || "").split(/\r?\n/);
  const chunks = [];
  let paragraph = [];
  let bullets = [];

  const flushParagraph = () => {
    if (paragraph.length) {
      chunks.push(`<p>${htmlEscape(cleanInline(paragraph.join(" ")))}</p>`);
      paragraph = [];
    }
  };

  const flushBullets = () => {
    if (bullets.length) {
      const items = bullets
        .map((item) => `<li>${htmlEscape(cleanInline(item))}</li>`)
        .join("");
      chunks.push(`<ul>${items}</ul>`);
      bullets = [];
    }
  };

  lines.forEach((line) => {
    const trimmed = line.trim();
    if (!trimmed) {
      flushParagraph();
      flushBullets();
      return;
    }

    const headingMatch = trimmed.match(/^(#{1,3})\s+(.+)$/);
    if (headingMatch) {
      flushParagraph();
      flushBullets();
      const level = headingMatch[1].length <= 2 ? "h3" : "h4";
      chunks.push(`<${level}>${htmlEscape(cleanInline(headingMatch[2]))}</${level}>`);
      return;
    }

    const bulletMatch = trimmed.match(/^[-*]\s+(.+)$/);
    if (bulletMatch) {
      flushParagraph();
      bullets.push(bulletMatch[1]);
      return;
    }

    flushBullets();
    paragraph.push(trimmed);
  });

  flushParagraph();
  flushBullets();

  elements.narrativeOutput.innerHTML = chunks.join("") || "<p>Narrative unavailable.</p>";
};

const renderBarList = (container, rows, labelKey, valueKey, formatValue) => {
  container.innerHTML = "";
  const maxValue = rows.reduce((max, row) => Math.max(max, row[valueKey] || 0), 0) || 1;
  rows.forEach((row) => {
    const value = row[valueKey] || 0;
    const bar = document.createElement("div");
    bar.className = "bar-row";
    bar.innerHTML = `
      <div class="bar-label"><span>${row[labelKey]}</span><span>${formatValue(value)}</span></div>
      <div class="bar-track"><div class="bar-fill" style="width:${(value / maxValue) * 100}%"></div></div>
    `;
    container.appendChild(bar);
  });
};

const renderStackedAllocation = (container, rows) => {
  container.innerHTML = "";
  rows.forEach((row) => {
    const total = row.total || 1;
    const emergencyPct = (row.emergency / total) * 100;
    const debtPct = (row.debt / total) * 100;
    const investPct = (row.invest / total) * 100;
    const block = document.createElement("div");
    block.className = "bar-row";
    block.innerHTML = `
      <div class="bar-label"><span>${row.name}</span><span>${asCurrency(row.total)}</span></div>
      <div class="stack-track">
        <div class="stack-seg stack-emergency" style="width:${emergencyPct}%"></div>
        <div class="stack-seg stack-debt" style="width:${debtPct}%"></div>
        <div class="stack-seg stack-invest" style="width:${investPct}%"></div>
      </div>
    `;
    container.appendChild(block);
  });
};

const renderDashboard = ({ mode, user, accounts, constraints, plans, markdown }) => {
  showResults();
  const income = user.income_monthly || 0;
  const expenses = user.expenses_monthly || 0;
  const disposable = income - expenses;
  const debtTotal = sumDebt(accounts);
  const investTotal = sumInvestments(accounts);
  const minPaymentTotal = minPayments(accounts);
  const emergencyTarget = expenses * (constraints?.min_emergency_fund_months || 3);
  const emergencyProgress = emergencyTarget ? (accounts.cash / emergencyTarget) * 100 : 100;
  const netWorth = accounts.cash + investTotal - debtTotal;

  elements.traceOutput.textContent =
    mode === "rules"
      ? "Mode: rules | Provider: rules | Parser: RuleGoalParser | Explainer: RulePlanExplainer"
      : "Mode: agent | Provider: preset | Parser: Agent (preset) | Explainer: Agent (preset)";

  elements.kpiNetWorth.textContent = asCurrency(netWorth);
  elements.kpiCashFlow.textContent = asCurrency(disposable);
  elements.kpiEmergencyTarget.textContent = asCurrency(emergencyTarget);
  elements.kpiEmergencyProgress.textContent = `${Math.round(emergencyProgress)}%`;
  elements.kpiDebtTotal.textContent = asCurrency(debtTotal);
  elements.kpiWeightedApr.textContent = `${(weightedApr(accounts) * 100).toFixed(2)}%`;
  elements.kpiCaption.textContent = `Minimum monthly debt payments: ${asCurrency(minPaymentTotal)} | Risk tolerance: ${constraints?.risk_tolerance || "unknown"}`;

  const rows = buildPlanRows(plans || [], disposable);
  const recommendation = pickRecommendation(rows);
  renderPlanTable(rows, recommendation?.name);
  renderStackedAllocation(elements.allocationChart, rows);
  renderBarList(
    elements.balanceChart,
    [
      { label: "Cash", amount: accounts.cash || 0 },
      { label: "Investments", amount: investTotal },
      { label: "Debt", amount: debtTotal },
    ],
    "label",
    "amount",
    asCurrency
  );

  const debtRows = accounts.debts.map((item) => ({
    label: item.type,
    amount: item.balance || 0,
  }));
  if (debtRows.length) {
    renderBarList(elements.debtChart, debtRows, "label", "amount", asCurrency);
  } else {
    elements.debtChart.innerHTML = "<p>No active debt accounts.</p>";
  }

  if (recommendation) {
    elements.recommendationOutput.innerHTML = `
      <h4><span class="badge-recommended">Recommended</span> Plan: ${recommendation.name} (score ${recommendation.score})</h4>
      <ul>
        <li>Highest composite score with ${asCurrency(recommendation.total)} allocation.</li>
        <li>Debt: ${asCurrency(recommendation.debt)}, Emergency: ${asCurrency(recommendation.emergency)}, Invest: ${asCurrency(recommendation.invest)}.</li>
        <li>Review approval-required actions, then confirm execution order.</li>
      </ul>
    `;
  } else {
    elements.recommendationOutput.textContent = "No plans were generated for this input.";
  }

  renderNarrativeHtml(markdown || "");
};

const renderPersonas = () => {
  elements.personaSelect.innerHTML = "";
  state.users.forEach((user) => {
    const option = document.createElement("option");
    option.value = user.id;
    option.textContent = `${user.id} (${user.region}, ${user.risk_tolerance})`;
    elements.personaSelect.appendChild(option);
  });
};

const renderPresets = () => {
  const mode = elements.modeSelect.value;
  const persona = elements.personaSelect.value;
  const presets = state.presets.filter((preset) => preset.mode === mode && preset.user_id === persona);

  elements.presetSelect.innerHTML = "";
  if (!presets.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No preset available";
    elements.presetSelect.appendChild(option);
    return;
  }

  presets.forEach((preset) => {
    const option = document.createElement("option");
    option.value = preset.id;
    option.textContent = preset.label;
    elements.presetSelect.appendChild(option);
  });
};

const updateGoalInput = () => {
  const persona = elements.personaSelect.value;
  const goals = getGoalsForUser(persona);
  elements.goalInput.value = goals[0] || "";
};

const updateModeHint = () => {
  const mode = elements.modeSelect.value;
  if (mode === "rules") {
    elements.modeHint.textContent = "Rules mode runs in your browser.";
    elements.presetNotice.textContent = "";
  } else {
    elements.modeHint.textContent = "Agent mode uses preset outputs.";
    elements.presetNotice.textContent = "Agent mode uses the selected preset output. Custom goals text is for drafting only.";
  }
};

const runRules = () => {
  const persona = elements.personaSelect.value;
  const user = state.users.find((item) => item.id === persona);
  const accounts = getAccountForUser(persona);
  const goalsText = elements.goalInput.value;

  const constraints = window.rulesEngine.parseConstraints(goalsText, user);
  const plans = window.rulesEngine.generatePlans(user, accounts, constraints);
  const scored = window.rulesEngine.scorePlans(plans, constraints);
  const guarded = window.rulesEngine.applyGuardrails(scored, user, accounts, constraints);
  const markdown = window.rulesEngine.explainPlansMarkdown(guarded, user, constraints);

  renderDashboard({ mode: "rules", user, accounts, constraints, plans: guarded, markdown });
};

const runPreset = () => {
  const presetId = elements.presetSelect.value;
  const preset = state.presets.find((item) => item.id === presetId);

  if (!preset) {
    elements.recommendationOutput.textContent = "Preset unavailable. Use rules mode.";
    elements.narrativeOutput.innerHTML = "<p>Preset narrative unavailable.</p>";
    return;
  }

  renderDashboard({
    mode: "agent",
    user: state.users.find((item) => item.id === preset.user_id) || {},
    accounts: getAccountForUser(preset.user_id),
    constraints: preset.constraints || null,
    plans: preset.plans || [],
    markdown: preset.markdown_output,
  });
};

const runDemo = () => {
  const mode = elements.modeSelect.value;
  if (mode === "rules") {
    runRules();
  } else {
    runPreset();
  }
};

const boot = async () => {
  elements.modeSelect = select("modeSelect");
  elements.personaSelect = select("personaSelect");
  elements.presetSelect = select("presetSelect");
  elements.goalInput = select("goalInput");
  elements.runBtn = select("runBtn");
  elements.resultsSection = select("resultsSection");
  elements.narrativeOutput = select("narrativeOutput");
  elements.modeHint = select("modeHint");
  elements.presetNotice = select("presetNotice");
  elements.traceOutput = select("traceOutput");
  elements.kpiNetWorth = select("kpiNetWorth");
  elements.kpiCashFlow = select("kpiCashFlow");
  elements.kpiEmergencyTarget = select("kpiEmergencyTarget");
  elements.kpiEmergencyProgress = select("kpiEmergencyProgress");
  elements.kpiDebtTotal = select("kpiDebtTotal");
  elements.kpiWeightedApr = select("kpiWeightedApr");
  elements.kpiCaption = select("kpiCaption");
  elements.planTable = select("planTable");
  elements.allocationChart = select("allocationChart");
  elements.balanceChart = select("balanceChart");
  elements.debtChart = select("debtChart");
  elements.recommendationOutput = select("recommendationOutput");

  if (window.__selfcheck) {
    console.log("Rules engine selfcheck:", window.__selfcheck());
  }

  try {
    await loadData();
  } catch (error) {
    elements.modeHint.textContent = "Failed to load demo data.";
    return;
  }

  renderPersonas();
  renderPresets();
  updateGoalInput();
  updateModeHint();

  elements.modeSelect.addEventListener("change", () => {
    renderPresets();
    updateModeHint();
    if (elements.modeSelect.value === "agent" && elements.presetSelect.value) {
      runPreset();
    }
  });

  elements.personaSelect.addEventListener("change", () => {
    renderPresets();
    updateGoalInput();
    if (elements.modeSelect.value === "agent" && elements.presetSelect.value) {
      runPreset();
    }
  });

  elements.presetSelect.addEventListener("change", () => {
    if (elements.modeSelect.value !== "rules") {
      runPreset();
    }
  });

  elements.runBtn.addEventListener("click", runDemo);
};

window.addEventListener("DOMContentLoaded", boot);
