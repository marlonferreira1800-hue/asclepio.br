function splitTexto(valor) {
  if (!valor) return [];
  return String(valor)
    .replace(/;/g, ",")
    .replace(/\n/g, ",")
    .split(",")
    .map((p) => p.trim())
    .filter(Boolean);
}

function avaliarUrgencia(payload) {
  const texto = [
    payload.sintomas || "",
    payload.sinais_alarme || "",
    payload.sintomas_associados || "",
    payload.contexto_especial || "",
  ]
    .join(" ")
    .toLowerCase();

  const criticos = [
    "dor no peito",
    "falta de ar",
    "desmaio",
    "convulsao",
    "convulsão",
    "confusao",
    "confusão",
    "sangramento intenso",
    "perda de consciência",
  ];
  const altos = [
    "febre alta",
    "rigidez na nuca",
    "rigidez de nuca",
    "fraqueza subita",
    "recém-nascido",
    "recem-nascido",
    "neonato",
    "ictericia",
    "icterícia",
    "gestante",
    "idoso",
  ];

  const detectados = [];
  for (const termo of [...criticos, ...altos]) {
    if (texto.includes(termo)) {
      detectados.push(termo);
    }
  }

  let intensidade = 0;
  try {
    intensidade = payload.intensidade ? parseInt(payload.intensidade, 10) : 0;
  } catch {
    intensidade = 0;
  }

  if (criticos.some((t) => detectados.includes(t)) || intensidade >= 9) {
    return { nivel: "CRITICO", detectados };
  }
  if (altos.some((t) => detectados.includes(t)) || intensidade >= 7) {
    return { nivel: "ALTO", detectados };
  }
  if (intensidade >= 4 || (payload.sinais_alarme && payload.sinais_alarme.trim())) {
    return { nivel: "MODERADO", detectados };
  }
  return { nivel: "BAIXO", detectados };
}

function sugerirEspecialidade(sintomas) {
  const t = (sintomas || "").toLowerCase();
  if (/peito|palpita|pressao|pressão|card/i.test(t)) return "Cardiologia";
  if (/falta de ar|tosse|chiado|pulm/i.test(t)) return "Pneumologia";
  if (/cabe[cç]a|tontura|convuls|desmaio|formiga/i.test(t)) return "Neurologia";
  if (/barriga|abd[oô]m|v[oô]mito|diarr|est[oô]m/i.test(t)) return "Gastroenterologia";
  if (/garganta|ouvido|nariz|sinus/i.test(t)) return "Otorrinolaringologia";
  if (/osso|coluna|articula|lombar|joelho/i.test(t)) return "Ortopedia";
  if (/pele|mancha|coceira|alergia/i.test(t)) return "Dermatologia";
  return "Clínico Geral";
}

export default async (request, context) => {
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json; charset=utf-8",
  };

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (request.method !== "POST") {
    return new Response(JSON.stringify({ detail: "Método não permitido" }), {
      status: 405,
      headers: corsHeaders,
    });
  }

  try {
    const payload = await request.json();
    const sintomas = String(payload.sintomas || "").trim();

    if (sintomas.length < 3) {
      return new Response(
        JSON.stringify({ detail: "Informe os sintomas principais com pelo menos 3 caracteres." }),
        { status: 400, headers: corsHeaders }
      );
    }

    const { nivel: urgency, detectados } = avaliarUrgencia(payload);
    const specialty = sugerirEspecialidade(sintomas);
    const associated = splitTexto(payload.sintomas_associados);
    const alarm = splitTexto(payload.sinais_alarme);

    const causesMap = {
      CRITICO: [
        "Condição clínica potencialmente grave com risco imediato",
        "Evento agudo que exige avaliação hospitalar em pronto-socorro",
      ],
      ALTO: [
        "Quadro com sinais de alerta relevantes",
        "Exacerbação aguda de condição pré-existente ou infecção moderada",
      ],
      MODERADO: [
        "Infecção ou inflamação de evolução clínica recente",
        "Quadro clínico em acompanhamento ambulatorial",
      ],
      BAIXO: [
        "Quadro leve, inicial ou funcional",
        "Sintoma inespecífico que requer observação e cuidados básicos",
      ],
    };

    const recommendations = [
      "Procure atendimento presencial em uma UBS ou consultório para confirmação diagnóstica.",
      "Não faça uso de medicamentos novos sem avaliação e prescrição profissional.",
    ];

    if (urgency === "CRITICO" || urgency === "ALTO") {
      recommendations.unshift(
        "Busque atendimento médico imediato em pronto-socorro. Em caso de emergência, ligue SAMU 192."
      );
    } else {
      recommendations.push(
        "Observe a evolução dos sintomas nas próximas 24-48h e busque assistência médica se houver piora."
      );
    }

    const relatorio = {
      atendimento_id: Math.floor(1000 + Math.random() * 9000),
      paciente: {
        nome: payload.nome ? String(payload.nome).trim() : null,
        idade: payload.idade ? `${payload.idade} anos` : null,
        sexo: payload.sexo ? String(payload.sexo).trim() : null,
        cidade: payload.cidade ? String(payload.cidade).trim() : null,
        queixa_principal: sintomas,
        duracao: payload.duracao ? String(payload.duracao).trim() : null,
        intensidade: payload.intensidade ? `${payload.intensidade}/10` : null,
        sintomas_associados: associated,
        sinais_alarme: alarm,
        doencas_previas: splitTexto(payload.doencas_previas),
        alergias: splitTexto(payload.alergias),
        medicamentos_em_uso: splitTexto(payload.medicamentos_em_uso),
        contexto_especial: splitTexto(payload.contexto_especial),
      },
      sintomas_principais: [sintomas, ...associated],
      possiveis_causas: causesMap[urgency] || causesMap.BAIXO,
      nivel_urgencia: urgency,
      especialidade_sugerida: specialty,
      recomendacoes: recommendations,
      observacoes_importantes:
        "Triagem orientativa preliminar gerada pelo Asclépio no Netlify. Não substitui consulta médica.",
      seguranca: {
        sinais_detectados: Array.from(new Set([...detectados, ...alarm])).sort(),
      },
      confianca: {
        score: detectados.length > 0 ? 0.65 : 0.8,
        classificacao: detectados.length > 0 ? "moderada" : "alta",
        motivo: "Triagem estruturada pelas diretrizes clínicas do Asclépio.",
      },
      revisao: {
        aprovado: true,
        alertas: [],
        human_in_the_loop: true,
      },
    };

    return new Response(JSON.stringify(relatorio), {
      status: 200,
      headers: corsHeaders,
    });
  } catch (error) {
    return new Response(JSON.stringify({ detail: error.message || "Erro no processamento" }), {
      status: 500,
      headers: corsHeaders,
    });
  }
};
