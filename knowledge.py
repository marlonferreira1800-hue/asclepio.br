BASE_CONHECIMENTO = [
    {
        "tema": "dor no peito",
        "termos": ["dor no peito", "peito", "pressão no peito"],
        "conteudo": "Dor torácica com falta de ar, suor frio, desmaio ou irradiação deve ser tratada como urgência.",
    },
    {
        "tema": "avc",
        "termos": ["paralisia", "fraqueza súbita", "fala enrolada", "confusão"],
        "conteudo": "Sinais neurológicos súbitos sugerem risco de AVC e exigem atendimento imediato.",
    },
    {
        "tema": "febre",
        "termos": ["febre", "rigidez na nuca", "manchas roxas"],
        "conteudo": "Febre alta com rigidez de nuca, confusão ou manchas deve ser avaliada com urgência.",
    },
    {
        "tema": "neonato",
        "termos": ["recém-nascido", "recem-nascido", "neonato", "amarelinha", "icterícia"],
        "conteudo": "Recém-nascidos com icterícia, febre, letargia ou recusa alimentar precisam de avaliação pediátrica imediata.",
    },
    {
        "tema": "tratamento alternativo",
        "termos": ["ozônio", "ozonio", "chá", "lavagem"],
        "conteudo": "Tratamentos caseiros ou alternativos em bebês podem ser perigosos e não substituem cuidado médico.",
    },
]


def recuperar_conhecimento(texto: str) -> list[dict]:
    low = texto.lower()
    resultados = []
    for item in BASE_CONHECIMENTO:
        if any(termo in low for termo in item["termos"]):
            resultados.append({"tema": item["tema"], "conteudo": item["conteudo"]})
    return resultados


def formatar_conhecimento(itens: list[dict]) -> str:
    if not itens:
        return "BASE DE CONHECIMENTO LOCAL: nenhum protocolo local acionado."
    linhas = ["BASE DE CONHECIMENTO LOCAL:"]
    for item in itens:
        linhas.append(f"- {item['tema']}: {item['conteudo']}")
    return "\n".join(linhas)
