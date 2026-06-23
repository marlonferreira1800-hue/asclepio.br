import { carregarAtendimentos, checarStatusApi, enviarAtendimento } from "./api.js";
import { renderErro, renderHistorico, renderResultado } from "./views.js";

const form = document.querySelector("#form-atendimento");
const statusEl = document.querySelector("#status");
const resultadoEl = document.querySelector("#resultado");
const emptyEl = document.querySelector("#empty");
const loadingEl = document.querySelector("#loading");
const titleEl = document.querySelector("#result-title");
const submitEl = document.querySelector("#submit");
const intensidade = document.querySelector('input[name="intensidade"]');
const intensidadeLabel = document.querySelector("#intensidade-label");
const tabs = document.querySelectorAll(".tab");
const views = document.querySelectorAll(".view");
const historyList = document.querySelector("#history-list");
const historyEmpty = document.querySelector("#history-empty");
const historyLoading = document.querySelector("#history-loading");
const refreshHistory = document.querySelector("#refresh-history");
const viewLinks = document.querySelectorAll("[data-open-view]");

function setView(nome) {
  tabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.view === nome);
  });
  views.forEach((view) => {
    view.classList.toggle("active", view.id === `view-${nome}`);
  });
  if (nome === "historico") carregarHistorico();
}

async function carregarHistorico() {
  historyLoading.classList.remove("hidden");
  historyEmpty.classList.add("hidden");
  try {
    const items = await carregarAtendimentos(50);
    renderHistorico(items, historyList, historyEmpty);
  } catch (error) {
    renderErro(historyList, "Erro no historico", error.message);
  } finally {
    historyLoading.classList.add("hidden");
  }
}

async function checarStatus() {
  try {
    await checarStatusApi();
    statusEl.textContent = "online";
    statusEl.classList.add("ok");
  } catch {
    statusEl.textContent = "offline";
    statusEl.classList.remove("ok");
  }
}

function montarPayload() {
  const dados = new FormData(form);
  const payload = Object.fromEntries(dados.entries());
  payload.salvar_txt = dados.get("salvar_txt") === "on";
  payload.idade = payload.idade ? Number(payload.idade) : null;
  payload.intensidade = payload.intensidade ? Number(payload.intensidade) : null;
  return payload;
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => setView(tab.dataset.view));
});

viewLinks.forEach((link) => {
  link.addEventListener("click", () => setView(link.dataset.openView));
});

refreshHistory.addEventListener("click", carregarHistorico);

intensidade.addEventListener("input", () => {
  intensidadeLabel.textContent = `${intensidade.value}/10`;
});

form.addEventListener("reset", () => {
  setTimeout(() => {
    intensidadeLabel.textContent = "5/10";
    titleEl.textContent = "Aguardando execucao";
    resultadoEl.classList.add("hidden");
    emptyEl.classList.remove("hidden");
    loadingEl.classList.add("hidden");
  }, 0);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  submitEl.disabled = true;
  emptyEl.classList.add("hidden");
  resultadoEl.classList.add("hidden");
  loadingEl.classList.remove("hidden");
  titleEl.textContent = "Processando";

  try {
    const relatorio = await enviarAtendimento(montarPayload());
    renderResultado(relatorio, resultadoEl, titleEl);
    resultadoEl.classList.remove("hidden");
    carregarHistorico();
  } catch (error) {
    titleEl.textContent = "Erro no atendimento";
    renderErro(resultadoEl, "Nao foi possivel concluir", error.message);
    resultadoEl.classList.remove("hidden");
  } finally {
    loadingEl.classList.add("hidden");
    submitEl.disabled = false;
  }
});

checarStatus();
