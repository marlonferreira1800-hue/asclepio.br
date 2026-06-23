import { escapeHtml, formatarData, listaHtml, normalizarUrgencia } from "./utils.js";

export function renderResultado(relatorio, resultadoEl, titleEl) {
  const paciente = relatorio.paciente || {};
  const urgencia = relatorio.nivel_urgencia || "BAIXO";
  const classeUrgencia = normalizarUrgencia(urgencia);
  const revisao = relatorio.revisao || {};
  const confianca = relatorio.confianca || {};
  const seguranca = relatorio.seguranca || {};

  titleEl.textContent = `Atendimento #${relatorio.atendimento_id || "-"}`;
  resultadoEl.innerHTML = `
    <div class="process-log">
      <p><span>[ok]</span> agente de IA recebeu o input clinico</p>
      <p><span>[ok]</span> agente de seguranca revisou sinais de alarme</p>
      <p><span>[ok]</span> agente de analise estruturou a resposta</p>
      <p><span>[ok]</span> memoria local registrada no SQLite</p>
    </div>

    <div class="summary-grid">
      <div class="metric">
        <span>Urgencia</span>
        <strong class="urgencia ${classeUrgencia}">${escapeHtml(urgencia)}</strong>
      </div>
      <div class="metric">
        <span>Especialidade</span>
        <strong>${escapeHtml(relatorio.especialidade_sugerida || "Clinico Geral")}</strong>
      </div>
      <div class="metric">
        <span>Confianca</span>
        <strong>${escapeHtml(confianca.classificacao || "-")}</strong>
      </div>
    </div>

    <div class="card">
      <h3>Resumo do paciente</h3>
      <p><strong>${escapeHtml(paciente.nome || "Paciente")}</strong></p>
      <p class="meta">
        ${escapeHtml(paciente.idade || "Idade nao informada")} |
        ${escapeHtml(paciente.sexo || "Sexo nao informado")} |
        ${escapeHtml(paciente.cidade || "Cidade nao informada")}
      </p>
      <p class="meta">Queixa: ${escapeHtml(paciente.queixa_principal || "-")}</p>
    </div>

    <div class="card">
      <h3>Sintomas principais</h3>
      ${listaHtml(relatorio.sintomas_principais)}
    </div>

    <div class="card">
      <h3>Possiveis causas</h3>
      ${listaHtml(relatorio.possiveis_causas)}
    </div>

    <div class="card">
      <h3>Recomendacoes</h3>
      ${listaHtml(relatorio.recomendacoes)}
    </div>

    <div class="card">
      <h3>Seguranca e revisao</h3>
      <p class="meta">Sinais detectados: ${(seguranca.sinais_detectados || []).map(escapeHtml).join(", ") || "-"}</p>
      <p class="meta">Revisao humana recomendada: ${revisao.human_in_the_loop ? "sim" : "nao"}</p>
      <p class="meta">Arquivo: ${escapeHtml(relatorio.arquivo_relatorio || "nao salvo")}</p>
    </div>

    <div class="card notice">
      <h3>Aviso</h3>
      <p class="meta">Este resultado e orientativo e nao substitui consulta medica presencial. Emergencias: SAMU 192 ou Bombeiros 193.</p>
    </div>
  `;
}

export function renderHistorico(items, historyList, historyEmpty) {
  historyList.innerHTML = "";
  historyEmpty.classList.toggle("hidden", items.length > 0);

  for (const item of items) {
    const urgencia = item.nivel_urgencia || "BAIXO";
    const classeUrgencia = normalizarUrgencia(urgencia);
    const card = document.createElement("article");
    card.className = "history-item";
    card.innerHTML = `
      <div>
        <p class="history-title">#${escapeHtml(item.id)} ${escapeHtml(item.nome || "Paciente")}</p>
        <p class="meta">${escapeHtml(formatarData(item.criado_em))}</p>
        <p class="meta">${escapeHtml(item.queixa_principal || "Sem queixa registrada")}</p>
      </div>
      <div class="history-side">
        <span class="urgencia ${classeUrgencia}">${escapeHtml(urgencia)}</span>
        <p class="meta">${escapeHtml(item.especialidade_sugerida || "Clinico Geral")}</p>
      </div>
    `;
    historyList.appendChild(card);
  }
}

export function renderErro(container, titulo, mensagem) {
  container.innerHTML = `
    <div class="card">
      <h3>${escapeHtml(titulo)}</h3>
      <p class="meta">${escapeHtml(mensagem)}</p>
    </div>
  `;
}
