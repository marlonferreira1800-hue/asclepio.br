from clinical_tools import calcular_confianca, planejar_proximos_passos


def test_calcular_confianca_alta_qualidade():
    estado = {"qualidade_dados": "alta"}
    seguranca = {"sinais_detectados": []}
    res = calcular_confianca(estado, seguranca)
    assert res["score"] == 0.8
    assert res["classificacao"] == "alta"


def test_calcular_confianca_com_sinais_alarme():
    estado = {"qualidade_dados": "alta"}
    seguranca = {"sinais_detectados": ["dor no peito"]}
    res = calcular_confianca(estado, seguranca)
    # Quando há sinais de alarme, deve limitar a 0.65
    assert res["score"] == 0.65
    assert res["classificacao"] == "moderada"


def test_calcular_confianca_baixa_qualidade():
    estado = {"qualidade_dados": "baixa"}
    seguranca = {"sinais_detectados": []}
    res = calcular_confianca(estado, seguranca)
    assert res["score"] == 0.35
    assert res["classificacao"] == "baixa"


def test_planejar_proximos_passos_urgente():
    estado = {"dados_faltantes": ["alergias"]}
    seguranca = {"nivel_minimo": "CRÍTICO"}
    passos = planejar_proximos_passos(estado, seguranca)
    assert any("atendimento médico imediato" in p.lower() for p in passos)
    assert any("dados faltantes" in p.lower() for p in passos)


def test_planejar_proximos_passos_rotina():
    estado = {"dados_faltantes": []}
    seguranca = {"nivel_minimo": "BAIXO"}
    passos = planejar_proximos_passos(estado, seguranca)
    assert not any("imediato" in p.lower() for p in passos)
    assert any("sem diagnóstico definitivo" in p.lower() for p in passos)
