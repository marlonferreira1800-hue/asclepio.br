from safety import avaliar_seguranca, elevar_urgencia


def test_avaliar_seguranca_critico_dor_no_peito():
    textos = ["Estou sentindo uma forte dor no peito e suor frio"]
    resultado = avaliar_seguranca(textos)
    assert resultado["nivel_minimo"] == "CRÍTICO"
    assert "dor no peito" in resultado["sinais_detectados"]
    assert any("pronto-socorro" in msg for msg in resultado["mensagens"])


def test_avaliar_seguranca_alto_recem_nascido_ictericia():
    textos = ["Meu recém-nascido de 5 dias está com icterícia e sonolento"]
    resultado = avaliar_seguranca(textos)
    assert resultado["nivel_minimo"] == "ALTO"
    assert any("pediátrica" in msg.lower() for msg in resultado["mensagens"])


def test_avaliar_seguranca_baixo_sintomas_leves():
    textos = ["Estou com coriza leve e espirros há um dia"]
    resultado = avaliar_seguranca(textos)
    assert resultado["nivel_minimo"] == "BAIXO"
    assert resultado["sinais_detectados"] == []


def test_bloqueio_tratamento_caseiro():
    textos = ["Gostaria de saber se posso fazer ozônio ou tomar chá para curar"]
    resultado = avaliar_seguranca(textos)
    assert resultado["bloqueio_tratamento_caseiro"] is True


def test_elevar_urgencia_quando_necessario():
    analise = {"nivel_urgencia": "BAIXO", "observacoes": ""}
    seguranca = {"nivel_minimo": "CRÍTICO"}
    resultado = elevar_urgencia(analise, seguranca)
    assert resultado["nivel_urgencia"] == "CRÍTICO"
    assert "Urgência elevada por regra determinística" in resultado["observacoes"]


def test_nao_rebaixar_urgencia():
    analise = {"nivel_urgencia": "CRÍTICO", "observacoes": ""}
    seguranca = {"nivel_minimo": "BAIXO"}
    resultado = elevar_urgencia(analise, seguranca)
    assert resultado["nivel_urgencia"] == "CRÍTICO"
