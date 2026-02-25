(() => {
  const lower = (value) => (value || "").toLowerCase();

  const parseConstraints = (text, user) => {
    const t = lower(text);
    const focusDebt =
      t.includes("debt") ||
      t.includes("loan") ||
      t.includes("mortgage") ||
      t.includes("credit card");

    let risk = user.risk_tolerance || "medium";
    if (t.includes("low volatility") || t.includes("conservative") || t.includes("low risk")) {
      risk = "low";
    }
    if (t.includes("high return") || t.includes("aggressive") || t.includes("high risk")) {
      risk = "high";
    }

    const emergency = t.includes("emergency") ? 3 : 3;

    return {
      min_emergency_fund_months: emergency,
      focus_debt_reduction: focusDebt,
      risk_tolerance: risk,
    };
  };

  const generatePlans = (user, accounts, constraints) => {
    const disposable = Math.max(0, user.income_monthly - user.expenses_monthly);
    const baseCash = accounts.cash || 0;
    const emergencyTarget = user.expenses_monthly * constraints.min_emergency_fund_months;
    const emergencyGap = Math.max(0, emergencyTarget - baseCash);

    const plan = (name, allocations) => ({
      name,
      actions: allocations
        .filter((item) => item.amount > 0)
        .map((item) => ({
          type: item.type,
          amount: Math.round(item.amount),
          requires_human_approval: item.requires_human_approval || false,
        })),
    });

    const debtAmount = disposable * 0.5;
    const investAmount = disposable * 0.3;
    const cashAmount = disposable * 0.2;

    return [
      plan("Debt focus", [
        { type: "Emergency fund", amount: Math.min(emergencyGap, cashAmount) },
        { type: "Debt payment", amount: debtAmount, requires_human_approval: true },
        { type: "Invest", amount: investAmount, requires_human_approval: true },
      ]),
      plan("Balanced", [
        { type: "Emergency fund", amount: Math.min(emergencyGap, disposable * 0.3) },
        { type: "Debt payment", amount: disposable * 0.35, requires_human_approval: true },
        { type: "Invest", amount: disposable * 0.35, requires_human_approval: true },
      ]),
      plan("Growth focus", [
        { type: "Emergency fund", amount: Math.min(emergencyGap, disposable * 0.15) },
        { type: "Invest", amount: disposable * 0.6, requires_human_approval: true },
        { type: "Debt payment", amount: disposable * 0.25, requires_human_approval: true },
      ]),
    ];
  };

  const scorePlans = (plans, constraints) => {
    return plans.map((plan) => {
      let score = 60;
      const debt = plan.actions.find((a) => a.type === "Debt payment");
      const invest = plan.actions.find((a) => a.type === "Invest");

      if (constraints.focus_debt_reduction && debt && (!invest || debt.amount > invest.amount)) {
        score += 15;
      }

      if (constraints.risk_tolerance === "low" && invest && invest.amount > 0) {
        score -= 5;
      }

      if (constraints.risk_tolerance === "high" && invest && invest.amount > 0) {
        score += 5;
      }

      return { ...plan, score };
    });
  };

  const applyGuardrails = (plans, user, accounts, constraints) => {
    const disposable = Math.max(0, user.income_monthly - user.expenses_monthly);
    const emergencyTarget = user.expenses_monthly * constraints.min_emergency_fund_months;
    const emergencyGap = Math.max(0, emergencyTarget - (accounts.cash || 0));

    return plans.map((plan) => {
      const total = plan.actions.reduce((sum, action) => sum + action.amount, 0);
      const scale = total > disposable && total > 0 ? disposable / total : 1;

      let actions = plan.actions.map((action) => ({
        ...action,
        amount: Math.round(action.amount * scale),
      }));

      const hasEmergency = actions.some((action) => action.type === "Emergency fund");
      if (emergencyGap > 0 && !hasEmergency) {
        actions = [
          { type: "Emergency fund", amount: Math.min(emergencyGap, disposable), requires_human_approval: false },
          ...actions,
        ];
      }

      return { ...plan, actions };
    });
  };

  const explainPlansMarkdown = (plans, user, constraints) => {
    return plans
      .map((plan, index) => {
        const actions = plan.actions
          .map((action) => {
            const flag = action.requires_human_approval ? " (approval required)" : "";
            return `- ${action.type}: ${action.amount}${flag}`;
          })
          .join("\n");

        return [
          `### Plan ${index + 1} (${plan.name})`,
          `**Score:** ${plan.score}`,
          "**This month:**",
          actions,
          "**Why:**",
          `- Priority: ${constraints.focus_debt_reduction ? "debt reduction" : "balanced"}`,
          `- Risk tolerance: ${constraints.risk_tolerance}`,
          "",
        ].join("\n");
      })
      .join("\n");
  };

  const selfcheck = () => {
    try {
      const user = {
        income_monthly: 3000,
        expenses_monthly: 2000,
        risk_tolerance: "medium",
      };
      const accounts = { cash: 500 };
      const constraints = parseConstraints("Pay down debt and build emergency fund", user);
      const plans = generatePlans(user, accounts, constraints);
      const scored = scorePlans(plans, constraints);
      const guarded = applyGuardrails(scored, user, accounts, constraints);
      const markdown = explainPlansMarkdown(guarded, user, constraints);

      if (!markdown || !guarded.length) {
        return { ok: false, errors: ["Rules engine produced empty output."] };
      }

      return { ok: true, errors: [] };
    } catch (error) {
      return { ok: false, errors: [String(error)] };
    }
  };

  window.rulesEngine = {
    parseConstraints,
    generatePlans,
    scorePlans,
    applyGuardrails,
    explainPlansMarkdown,
  };
  window.__selfcheck = selfcheck;
})();
