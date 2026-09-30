from reviewer import revisar_relatorio


def test_revisar_relatorio_aprovado():
    relatorio = {
        "sintomas_principais": ["tosse", "coriza"],
        "possiveis_causas": ["Resfriado comum"],
        "recomendacoes": ["Procurar uma UBS para avaliação caso persista"],
        "observacoes_importantes": "Manter repouso e hidratação.",
        "nivel_urgencia": "BAIXO",
    }
    resultado = revisar_relatorio(relatorio)
    assert resultado["aprovado"] is True
    assert resultado["human_in_the_loop"] is True


def test_revisar_relatorio_rejeita_diagnostico_definitivo():
    relatorio = {
        "sintomas_principais": ["dor de garganta"],
        "possiveis_causas": ["você tem amigdalite bacteriana"],
        "recomendacoes": ["tome antibiótico por 7 dias"],
        "observacoes_importantes": "diagnóstico definitivo confirmado.",
        "nivel_urgencia": "BAIXO",
    }
    resultado = revisar_relatorio(relatorio)
    assert resultado["aprovado"] is False
    assert len(resultado["alertas"]) >= 2
    assert any("Evitar expressão ou orientação insegura" in a for a in resultado["alertas"])


def test_revisar_relatorio_sem_recomendacoes():
    relatorio = {
        "sintomas_principais": ["dor nas costas"],
        "possiveis_causas": ["Lombalgia"],
        "recomendacoes": [],
        "nivel_urgencia": "BAIXO",
    }
    resultado = revisar_relatorio(relatorio)
    assert any("sem recomendações" in a.lower() for a in resultado["alertas"])
