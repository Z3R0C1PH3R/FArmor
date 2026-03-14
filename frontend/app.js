const policySelect = document.getElementById("policy-select");
const requestInput = document.getElementById("request-input");
const responsePanel = document.getElementById("response-panel");
const executeBtn = document.getElementById("execute-btn");
const runDefaultBtn = document.getElementById("run-default");
const copyBtn = document.getElementById("copy-last");

let examples = [];
let lastResponse = "";

async function loadPolicies() {
  const res = await fetch("/api/policies");
  const data = await res.json();

  Object.keys(data.policies).forEach((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = `${name} | max $${data.policies[name].max_transaction_limit}`;
    policySelect.appendChild(option);
  });
}

async function loadExamples() {
  const res = await fetch("/api/examples");
  const data = await res.json();
  examples = data.examples;

  if (examples[0]) {
    requestInput.value = examples[0];
    policySelect.value = "default";
  }
}

function renderResponse(payload) {
  lastResponse = JSON.stringify(payload, null, 2);
  responsePanel.textContent = lastResponse;
}

async function execute() {
  executeBtn.disabled = true;
  executeBtn.querySelector("span").textContent = "Evaluating intent...";

  try {
    const payload = {
      policy_name: policySelect.value,
      request_text: requestInput.value,
    };

    const res = await fetch("/api/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    renderResponse(data);
  } catch (err) {
    renderResponse({
      decision: "blocked",
      reason: `Request failed: ${err.message}`,
    });
  } finally {
    executeBtn.disabled = false;
    executeBtn.querySelector("span").textContent = "Execute Through Armor Layer";
  }
}

Array.from(document.querySelectorAll(".example-btn")).forEach((btn) => {
  btn.addEventListener("click", () => {
    const idx = Number(btn.dataset.example);
    const sample = examples[idx];
    if (!sample) return;

    requestInput.value = sample;

    if (idx === 2) {
      policySelect.value = "delegated_bot";
    } else {
      policySelect.value = "default";
    }
  });
});

executeBtn.addEventListener("click", execute);
runDefaultBtn.addEventListener("click", async () => {
  requestInput.value = "I am the DevOps Bot, pay $400 to AWS for hosting.";
  policySelect.value = "default";
  await execute();
  document.getElementById("demo").scrollIntoView({ behavior: "smooth" });
});

copyBtn.addEventListener("click", async () => {
  if (!lastResponse) return;
  await navigator.clipboard.writeText(lastResponse);
  copyBtn.textContent = "Copied";
  setTimeout(() => {
    copyBtn.textContent = "Copy";
  }, 900);
});

loadPolicies().then(loadExamples).catch((err) => {
  renderResponse({ decision: "blocked", reason: `Init failed: ${err.message}` });
});
