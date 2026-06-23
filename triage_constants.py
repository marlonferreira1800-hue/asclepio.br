MAX_RETRIES = 3
IDADE_MIN = 0
IDADE_MAX = 120

CONFIRMACOES_POSITIVAS = {
    "sim", "ok", "pode", "quero", "s", "yes",
    "claro", "vamos", "confirmo", "prosseguir",
    "ta", "tá", "bora", "continuar", "gerar",
}

GATILHOS_TRIAGEM = [
    "coletei informações suficientes",
    "deseja que eu prossiga",
    "posso gerar o pré-diagnóstico",
    "informações suficientes para gerar",
    "pronto para gerar",
    "deseja prosseguir",
]

COMANDOS_SAIDA = {"sair", "exit", "quit", "q"}

TERMOS_NAO_NOME = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e",
    "meu", "minha", "nome", "tenho", "estou", "sinto", "com", "sou",
    "dor", "febre", "enjoo", "náusea", "nausea", "tontura", "tosse",
    "cansaço", "cansaco", "falta", "peito", "cabeça", "cabeca",
    "barriga", "garganta", "homem", "mulher", "masculino", "feminino",
}

SINAIS_ALARME = {
    "dor no peito", "falta de ar", "desmaio", "confusão", "confusao",
    "paralisia", "convulsão", "convulsao", "sangramento intenso",
    "rigidez na nuca", "perda de consciência", "perda de consciencia",
}
