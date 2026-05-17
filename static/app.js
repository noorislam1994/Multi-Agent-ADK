const agents = [
  ["english", "EN", "English Teacher Agent", "Grammar, essays, comprehension, literature", "#2563eb"],
  ["maths", "MA", "Maths Teacher Agent", "Arithmetic, algebra, geometry, statistics", "#b45309"],
  ["science", "SC", "Science Teacher Agent", "Biology, chemistry, physics, experiments", "#16803c"],
  ["history", "HI", "History Teacher Agent", "Events, timelines, civilizations, sources", "#c2410c"],
  ["geography", "GE", "Geography Teacher Agent", "Maps, climate, hazards, population", "#0891b2"],
  ["computer_science", "CS", "Computer Science Teacher Agent", "Programming, algorithms, networks, data", "#7c3aed"],
];

const agentList = document.querySelector("#agentList");
const messages = document.querySelector("#messages");
const chatForm = document.querySelector("#chatForm");
const messageInput = document.querySelector("#messageInput");
const memoryList = document.querySelector("#memoryList");
const modelState = document.querySelector("#modelState");
const refreshMemory = document.querySelector("#refreshMemory");

function renderAgents(activeSubject) {
  agentList.innerHTML = agents
    .map(([key, short, name, description, color]) => `
      <div class="agent-card ${activeSubject === key ? "active" : ""}">
        <div class="agent-icon" style="background:${color}">${short}</div>
        <div>
          <strong>${name}</strong>
          <p>${description}</p>
        </div>
      </div>
    `)
    .join("");
}

function addMessage(role, content, meta = "") {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  article.innerHTML = `
    <div class="bubble">
      ${meta ? `<div class="meta">${escapeHtml(meta)}</div>` : ""}
      ${escapeHtml(content)}
    </div>
  `;
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function loadMemory() {
  const response = await fetch("/api/memory");
  const data = await response.json();
  memoryList.innerHTML = data.messages.length
    ? data.messages
        .slice()
        .reverse()
        .map((item) => `
          <div class="memory-item">
            <strong>${escapeHtml(item.role)}${item.subject ? ` / ${escapeHtml(item.subject.replace("_", " "))}` : ""}</strong>
            ${escapeHtml(item.content).slice(0, 180)}
          </div>
        `)
        .join("")
    : `<div class="memory-item"><strong>Empty</strong>No saved messages yet.</div>`;
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) return;

  messageInput.value = "";
  addMessage("user", message);
  addMessage("assistant", "Routing request through the School Coordinator...");

  const pending = messages.lastElementChild;
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();
    pending.remove();
    renderAgents(data.subject);
    modelState.textContent = data.usedModel
      ? "Gemini model active through API key"
      : "Offline fallback active until GOOGLE_API_KEY is set";
    const toolMeta = data.toolResult?.status === "success" ? ` | calculator: ${data.toolResult.result}` : "";
    addMessage("assistant", data.response, `${data.agent}${toolMeta}`);
    await loadMemory();
  } catch (error) {
    pending.remove();
    addMessage("assistant", `Request failed: ${error.message}`);
  }
});

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    chatForm.requestSubmit();
  }
});

refreshMemory.addEventListener("click", loadMemory);

renderAgents();
loadMemory().catch(() => {
  memoryList.innerHTML = `<div class="memory-item"><strong>Unavailable</strong>Memory could not be loaded.</div>`;
});
modelState.textContent = "Ready. Set GOOGLE_API_KEY for live Gemini responses.";

