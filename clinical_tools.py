def calcular_confianca(estado: dict, seguranca: dict) -> dict:
    qualidade = estado.get("qualidade_dados", "baixa")
    base = {"alta": 0.8, "moderada": 0.55, "baixa": 0.35}.get(qualidade, 0.35)
    if seguranca.get("sinais_detectados"):
        base = min(base, 0.65)
    return {
        "score": round(base, 2),
        "classificacao": "alta" if base >= 0.75 else "moderada" if base >= 0.5 else "baixa",
        "motivo": f"Qualidade dos dados: {qualidade}.",
    }


def planejar_proximos_passos(estado: dict, seguranca: dict) -> list[str]:
    passos = []
    if seguranca.get("nivel_minimo") in {"ALTO", "CRÍTICO", "CRITICO"}:
        passos.append("Priorizar orientação de atendimento médico imediato.")
    if estado.get("dados_faltantes"):
        passos.append("Registrar dados faltantes antes de confiar na análise.")
    passos.append("Gerar hipóteses orientativas sem diagnóstico definitivo.")
    passos.append("Revisar segurança antes de exibir recomendações.")
    return passos
