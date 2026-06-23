TERMOS_PROIBIDOS = ["você tem ", "diagnóstico definitivo", "tome antibiótico", "dose de"]


def revisar_relatorio(relatorio: dict) -> dict:
    textos = []
    textos.extend(relatorio.get("sintomas_principais", []))
    textos.extend(relatorio.get("possiveis_causas", []))
    textos.extend(relatorio.get("recomendacoes", []))
    textos.append(relatorio.get("observacoes_importantes", ""))
    unido = " ".join(textos).lower()

    alertas = []
    for termo in TERMOS_PROIBIDOS:
        if termo in unido:
            alertas.append(f"Evitar expressão ou orientação insegura: {termo.strip()}")

    if not relatorio.get("recomendacoes"):
        alertas.append("Relatório sem recomendações.")
    if relatorio.get("nivel_urgencia", "").upper() in {"ALTO", "CRÍTICO", "CRITICO"}:
        alertas.append("Revisão profissional recomendada pela urgência informada.")

    return {
        "aprovado": not any("insegura" in alerta for alerta in alertas),
        "alertas": alertas,
        "human_in_the_loop": True,
    }
