export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

export function listaHtml(items) {
  const lista = Array.isArray(items) ? items : [];
  if (!lista.length) return '<p class="meta">Sem itens registrados.</p>';
  return `<ul>${lista.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

export function normalizarUrgencia(valor) {
  return String(valor || "BAIXO")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

export function formatarData(valor) {
  if (!valor) return "-";
  const data = new Date(valor);
  if (Number.isNaN(data.getTime())) return valor;
  return data.toLocaleString("pt-BR");
}
