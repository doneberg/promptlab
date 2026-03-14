const urlParams = new URLSearchParams(window.location.search);
const workflowId = urlParams.get("id");

const blockList = document.getElementById("blockList");
const blockForm = document.getElementById("blockForm");
const executeBtn = document.getElementById("executeBtn");
const executionStatus = document.getElementById("executionStatus");
const executionSteps = document.getElementById("executionSteps");

async function loadWorkflow() {
  const workflow = await apiRequest(`/workflows/${workflowId}`);
  document.getElementById("workflowTitle").textContent = workflow.name;
}

async function loadBlocks() {
  const blocks = await apiRequest(`/workflows/${workflowId}`);
  // Not ideal — no dedicated block list endpoint yet
  // For now rely on execution view later
}

blockForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const order_index = parseInt(document.getElementById("orderIndex").value);
  const role = document.getElementById("role").value;
  const content_template = document.getElementById("contentTemplate").value;

  await apiRequest(`/workflows/${workflowId}/blocks/`, {
    method: "POST",
    body: JSON.stringify({ order_index, role, content_template }),
  });

  blockForm.reset();
  alert("Block added.");
});

executeBtn.addEventListener("click", async () => {
  const rawVars = document.getElementById("variablesInput").value;

  let variables = {};
  try {
    variables = rawVars ? JSON.parse(rawVars) : {};
  } catch {
    alert("Invalid JSON");
    return;
  }

  const result = await apiRequest(`/executions/workflows/${workflowId}`, {
    method: "POST",
    body: JSON.stringify({ variables }),
  });

  executionStatus.textContent = "Execution started...";
  pollExecution(result.execution_id);
});

async function pollExecution(executionId) {
  const interval = setInterval(async () => {
    const execution = await apiRequest(`/executions/${executionId}`);

    executionStatus.textContent = `Status: ${execution.status}`;

    if (execution.status === "completed" || execution.status === "failed") {
      clearInterval(interval);
      renderSteps(execution.steps);
    }
  }, 1000);
}

function renderSteps(steps) {
  executionSteps.innerHTML = "";

  steps.forEach(step => {
    const div = document.createElement("div");
    div.className = "step";

    div.innerHTML = `
      <h4>Step ${step.order_index}</h4>
      <p><strong>Prompt:</strong> ${step.rendered_prompt}</p>
      <p><strong>Response:</strong> ${step.response_text}</p>
      <p><strong>Latency:</strong> ${step.latency_ms} ms</p>
      <hr/>
    `;

    executionSteps.appendChild(div);
  });
}

loadWorkflow();