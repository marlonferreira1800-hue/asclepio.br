REGRAS_URGENCIA = [
    {
        "nivel": "CRÍTICO",
        "termos": ["dor no peito", "falta de ar", "desmaio", "convulsão", "confusão mental"],
        "mensagem": "Sinais potencialmente graves. Oriente pronto-socorro imediatamente.",
    },
    {
        "nivel": "ALTO",
        "termos": ["sangramento intenso", "rigidez na nuca", "perda de consciência", "paralisia"],
        "mensagem": "Sinais de alarme exigem avaliação médica no mesmo dia.",
    },
    {
        "nivel": "ALTO",
        "termos": ["recém-nascido", "recem-nascido", "neonato", "amarelinha", "icterícia"],
        "mensagem": "Recém-nascidos com icterícia ou sinais sistêmicos exigem avaliação pediátrica imediata.",
    },
]

ORDEM_URGENCIA = {"BAIXO": 0, "MODERADO": 1, "ALTO": 2, "CRÍTICO": 3, "CRITICO": 3}


def avaliar_seguranca(textos: list[str], estado: dict | None = None) -> dict:
    conteudo = " ".join(textos).lower()
    encontrados = []
    nivel = "BAIXO"
    mensagens = []

    for regra in REGRAS_URGENCIA:
        termos_presentes = [termo for termo in regra["termos"] if termo in conteudo]
        if termos_presentes:
            encontrados.extend(termos_presentes)
            mensagens.append(regra["mensagem"])
            if ORDEM_URGENCIA[regra["nivel"]] > ORDEM_URGENCIA[nivel]:
                nivel = regra["nivel"]

    if estado:
        for sinal in estado.get("sinais_alarme", []):
            if sinal not in encontrados:
                encontrados.append(sinal)
        if estado.get("sinais_alarme") and ORDEM_URGENCIA[nivel] < ORDEM_URGENCIA["ALTO"]:
            nivel = "ALTO"

    return {
        "nivel_minimo": nivel,
        "sinais_detectados": sorted(set(encontrados)),
        "mensagens": sorted(set(mensagens)),
        "bloqueio_tratamento_caseiro": any(t in conteudo for t in ["ozônio", "ozonio", "chá", "lavagem"]),
    }


def elevar_urgencia(analise: dict, seguranca: dict) -> dict:
    atual = analise.get("nivel_urgencia", "BAIXO").upper()
    minimo = seguranca.get("nivel_minimo", "BAIXO").upper()
    if ORDEM_URGENCIA.get(minimo, 0) > ORDEM_URGENCIA.get(atual, 0):
        analise["nivel_urgencia"] = minimo
        observacao = "Urgência elevada por regra determinística de segurança clínica."
        analise["observacoes"] = f"{analise.get('observacoes', '')} {observacao}".strip()
    return analise
