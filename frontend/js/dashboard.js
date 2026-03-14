const list = document.getElementById("workflowList");

async function loadWorkflows() {
  const workflows = await apiRequest("/workflows/");

  list.innerHTML = "";

  workflows.forEach(w => {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${w.name}</strong><br/><small>${w.description || ""}</small>`;
    li.onclick = () => {
      window.location.href = `workflow.html?id=${w.id}`;
    };
    list.appendChild(li);
  });
}

loadWorkflows();

document.getElementById("createWorkflow").addEventListener("click", async () => {
  const name = prompt("Workflow name:");
  if (!name) return;

  const workflow = await apiRequest("/workflows/", {
    method: "POST",
    body: JSON.stringify({
      name,
      description: ""
    })
  });

  window.location.href = `workflow.html?id=${workflow.id}`;
});