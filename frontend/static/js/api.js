export async function checarStatusApi() {
  const resposta = await fetch("/api/status");
  if (!resposta.ok) throw new Error("offline");
  return resposta.json();
}

export async function carregarAtendimentos(limite = 50) {
  const resposta = await fetch(`/api/atendimentos?limite=${limite}`);
  if (!resposta.ok) throw new Error("Nao foi possivel carregar o historico");
  return resposta.json();
}

export async function enviarAtendimento(payload) {
  const resposta = await fetch("/api/atendimento", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const corpo = await resposta.json();
  if (!resposta.ok) {
    throw new Error(corpo.detail || "Falha no atendimento");
  }
  return corpo;
}
