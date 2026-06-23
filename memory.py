import json
from pathlib import Path

from database import carregar_memoria_db

MEMORY_FILE = Path("relatorios") / "memoria_atendimentos.jsonl"


def salvar_memoria(relatorio: dict) -> None:
    MEMORY_FILE.parent.mkdir(exist_ok=True)
    registro = {
        "paciente": relatorio.get("paciente", {}),
        "nivel_urgencia": relatorio.get("nivel_urgencia"),
        "especialidade_sugerida": relatorio.get("especialidade_sugerida"),
        "confianca": relatorio.get("confianca"),
        "revisao": relatorio.get("revisao", {}),
    }
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def carregar_memoria(limite: int = 5) -> list[dict]:
    memoria_db = carregar_memoria_db(limite)
    if memoria_db:
        return memoria_db

    if not MEMORY_FILE.exists():
        return []
    linhas = MEMORY_FILE.read_text(encoding="utf-8").splitlines()[-limite:]
    memoria = []
    for linha in linhas:
        try:
            memoria.append(json.loads(linha))
        except json.JSONDecodeError:
            continue
    return memoria
