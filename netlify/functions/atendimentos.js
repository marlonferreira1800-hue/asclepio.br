// Armazenamento em memória para demonstração serverless
const historicoRecente = [
  {
    id: 1,
    criado_em: new Date(Date.now() - 3600000).toISOString().replace("T", " ").substring(0, 19),
    nome: "Exemplo Clínico",
    idade: "35 anos",
    cidade: "São Paulo",
    queixa_principal: "Cefaleia e febre leve há 1 dia",
    nivel_urgencia: "MODERADO",
    especialidade_sugerida: "Clínico Geral",
    confianca_score: 0.8,
    confianca_classificacao: "alta",
    revisao_humana: 1,
    payload: {},
  },
];

export default async (request, context) => {
  const url = new URL(request.url);
  const limite = parseInt(url.searchParams.get("limite") || "20", 10);
  const itens = historicoRecente.slice(0, Math.min(limite, 50));

  return new Response(JSON.stringify(itens), {
    status: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Access-Control-Allow-Origin": "*",
    },
  });
};
