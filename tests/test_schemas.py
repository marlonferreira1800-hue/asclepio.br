from schemas import (
    ConfiancaSchema,
    PacienteSchema,
    RelatorioSchema,
    RevisaoSchema,
    validar_relatorio,
)


def test_paciente_schema_criacao_valida():
    paciente = PacienteSchema(
        nome="Mariana",
        idade="28 anos",
        queixa_principal="Dor de garganta",
        sintomas_associados=["tosse"],
    )
    assert paciente.nome == "Mariana"
    assert paciente.idade == "28 anos"
    assert paciente.sintomas_associados == ["tosse"]


def test_confianca_schema_score_bounds():
    conf = ConfiancaSchema(score=1.5, classificacao="alta")
    assert conf.score == 1.0

    conf_neg = ConfiancaSchema(score=-0.2, classificacao="baixa")
    assert conf_neg.score == 0.0


def test_relatorio_schema_normalizacao_urgencia():
    rel = RelatorioSchema(
        nivel_urgencia="crítico",
        sintomas_principais=["dor de cabeça"],
        recomendacoes=["descansar"],
    )
    assert rel.nivel_urgencia == "CRITICO"

    rel_invalido = RelatorioSchema(
        nivel_urgencia="DESCONHECIDO",
        sintomas_principais=["febre"],
    )
    assert rel_invalido.nivel_urgencia == "BAIXO"


def test_validar_relatorio_completo():
    dados = {
        "paciente": {"nome": "Lucas", "idade": "35"},
        "sintomas_principais": ["tosse seca"],
        "possiveis_causas": ["Faringite viral"],
        "nivel_urgencia": "MODERADO",
        "especialidade_sugerida": "Clínico Geral",
        "recomendacoes": ["Hidratação oral", "Repouso"],
        "confianca": {"score": 0.8, "classificacao": "alta"},
        "revisao": {"aprovado": True, "alertas": []},
    }
    schema = validar_relatorio(dados)
    assert schema.paciente.nome == "Lucas"
    assert schema.nivel_urgencia == "MODERADO"
    assert schema.revisao.aprovado is True
