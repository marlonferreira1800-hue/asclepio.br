from __future__ import annotations

from typing import Any

from frontend.schemas import AtendimentoEntrada


def _split_texto(valor: str | None) -> list[str]:
    if not valor:
        return []
    partes = valor.replace(";", ",").replace("\n", ",").split(",")
    return [parte.strip() for parte in partes if parte.strip()]


def _montar_dados_paciente(entrada: AtendimentoEntrada) -> dict[str, Any]:
    dados: dict[str, Any] = {
        "queixa_principal": entrada.sintomas.strip(),
        "sintomas_associados": _split_texto(entrada.sintomas_associados),
        "sinais_alarme": _split_texto(entrada.sinais_alarme),
        "doencas_previas": _split_texto(entrada.doencas_previas),
        "alergias": _split_texto(entrada.alergias),
        "medicamentos_em_uso": _split_texto(entrada.medicamentos_em_uso),
        "contexto_especial": _split_texto(entrada.contexto_especial),
    }
    if entrada.nome:
        dados["nome"] = entrada.nome.strip()
    if entrada.idade is not None:
        dados["idade"] = f"{entrada.idade} anos"
    if entrada.sexo:
        dados["sexo"] = entrada.sexo.strip()
    if entrada.cidade:
        dados["cidade"] = entrada.cidade.strip()
    if entrada.duracao:
        dados["duracao"] = entrada.duracao.strip()
    if entrada.intensidade is not None:
        dados["intensidade"] = f"{entrada.intensidade}/10"
    return dados


def _montar_texto_triagem(entrada: AtendimentoEntrada, dados: dict[str, Any]) -> str:
    linhas = ["DADOS COLETADOS NA TRIAGEM MEDICA:", ""]
    if dados.get("nome"):
        linhas.append(f"Nome: {dados['nome']}")
    if dados.get("idade"):
        linhas.append(f"Idade: {dados['idade']}")
    if dados.get("sexo"):
        linhas.append(f"Sexo: {dados['sexo']}")
    if dados.get("cidade"):
        linhas.append(f"Cidade: {dados['cidade']}")
    linhas.append(f"Queixa principal: {entrada.sintomas.strip()}")
    if dados.get("duracao"):
        linhas.append(f"Duracao: {dados['duracao']}")
    if dados.get("intensidade"):
        linhas.append(f"Intensidade: {dados['intensidade']}")

    for chave, rotulo in [
        ("sintomas_associados", "Sintomas associados"),
        ("sinais_alarme", "Sinais de alarme"),
        ("doencas_previas", "Doencas previas"),
        ("alergias", "Alergias"),
        ("medicamentos_em_uso", "Medicamentos em uso"),
        ("contexto_especial", "Contexto especial"),
    ]:
        valores = dados.get(chave) or []
        if valores:
            linhas.append(f"{rotulo}: {', '.join(valores)}")

    return "\n".join(linhas)


def executar_atendimento_web(entrada: AtendimentoEntrada) -> dict[str, Any]:
    from asclepio import montar_relatorio
    from clinical_tools import calcular_confianca, planejar_proximos_passos
    from database import atualizar_caminho_relatorio, salvar_atendimento
    from extraction_agent import AgenteExtracaoClinica
    from knowledge import formatar_conhecimento, recuperar_conhecimento
    from memory import carregar_memoria, salvar_memoria
    from observability import registrar_evento
    from orientation_agent import AgenteOrientacao
    from prediagnosis_agent import AgentePreDiagnostico
    from reports import salvar_relatorio
    from reviewer import revisar_relatorio
    from safety import elevar_urgencia
    from safety_agent import AgenteSegurancaMedica
    from state import CaseState
    from triage_agent import AgenteTriagem

    registrar_evento("atendimento_web_iniciado")
    dados_paciente = _montar_dados_paciente(entrada)
    dados_coletados = _montar_texto_triagem(entrada, dados_paciente)

    triagem = AgenteTriagem()
    triagem.dados_paciente.update(dados_paciente)
    triagem.historico.append({"role": "user", "content": dados_coletados})

    dados_estruturados = AgenteExtracaoClinica().extrair(dados_coletados, triagem.dados_paciente)
    triagem.dados_paciente.update(dados_estruturados)

    estado = CaseState.from_triagem(triagem.dados_paciente, triagem.historico)
    seguranca = AgenteSegurancaMedica().avaliar(dados_coletados, estado.to_dict())
    conhecimento = recuperar_conhecimento("\n".join([dados_coletados, estado.resumo_para_ia()]))
    planejamento = planejar_proximos_passos(estado.to_dict(), seguranca)
    confianca = calcular_confianca(estado.to_dict(), seguranca)
    memoria = carregar_memoria()

    contexto_agente = "\n\n".join(
        [
            dados_coletados,
            estado.resumo_para_ia(),
            formatar_conhecimento(conhecimento),
            "PLANO DO AGENTE:\n- " + "\n- ".join(planejamento),
            f"MEMORIA RECENTE DISPONIVEL: {len(memoria)} atendimento(s).",
        ]
    )

    analise = AgentePreDiagnostico().analisar(contexto_agente)
    analise = elevar_urgencia(analise, seguranca)
    recomendacoes = AgenteOrientacao().orientar(analise)

    relatorio = montar_relatorio(
        triagem=triagem,
        analise=analise,
        recomendacoes=recomendacoes,
        estado=estado,
        seguranca=seguranca,
        conhecimento=conhecimento,
        planejamento=planejamento,
        confianca=confianca,
    )
    relatorio["revisao"] = revisar_relatorio(relatorio)
    salvar_memoria(relatorio)
    atendimento_id = salvar_atendimento(relatorio)
    relatorio["atendimento_id"] = atendimento_id

    if entrada.salvar_txt:
        arquivo = salvar_relatorio(relatorio)
        atualizar_caminho_relatorio(atendimento_id, arquivo)
        relatorio["arquivo_relatorio"] = arquivo

    registrar_evento(
        "atendimento_web_concluido",
        {
            "atendimento_id": atendimento_id,
            "nivel_urgencia": relatorio.get("nivel_urgencia"),
        },
    )
    return relatorio
