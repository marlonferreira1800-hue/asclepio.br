import datetime
import json
from pathlib import Path

from database import registrar_evento_db

LOG_FILE = Path("logs") / "asclepio.jsonl"


def registrar_evento(evento: str, dados: dict | None = None) -> None:
    registrar_evento_db(evento, dados)

    LOG_FILE.parent.mkdir(exist_ok=True)
    payload = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "evento": evento,
        "dados": dados or {},
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
