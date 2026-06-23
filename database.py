import datetime
import json
import sqlite3
from pathlib import Path
from typing import Any

from schemas import validar_relatorio

DB_PATH = Path("data") / "asclepio.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection | None = None) -> None:
    owns_connection = conn is None
    if conn is None:
        DB_PATH.parent.mkdir(exist_ok=True)
        conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            criado_em TEXT NOT NULL,
            nome TEXT,
            idade TEXT,
            sexo TEXT,
            cidade TEXT,
            queixa_principal TEXT,
            nivel_urgencia TEXT,
            especialidade_sugerida TEXT,
            confianca_score REAL,
            confianca_classificacao TEXT,
            revisao_humana INTEGER NOT NULL DEFAULT 1,
            relatorio_path TEXT,
            payload_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            criado_em TEXT NOT NULL,
            evento TEXT NOT NULL,
            dados_json TEXT NOT NULL
        )
        """
    )
    conn.commit()

    if owns_connection:
        conn.close()


def salvar_atendimento(relatorio: dict[str, Any], relatorio_path: str | None = None) -> int:
    validado = validar_relatorio(relatorio)
    payload = validado.model_dump(mode="json")
    paciente = payload.get("paciente", {})
    confianca = payload.get("confianca", {})
    revisao = payload.get("revisao", {})

    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO atendimentos (
                criado_em, nome, idade, sexo, cidade, queixa_principal,
                nivel_urgencia, especialidade_sugerida, confianca_score,
                confianca_classificacao, revisao_humana, relatorio_path, payload_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.datetime.now().isoformat(timespec="seconds"),
                paciente.get("nome"),
                paciente.get("idade"),
                paciente.get("sexo"),
                paciente.get("cidade"),
                paciente.get("queixa_principal"),
                payload.get("nivel_urgencia"),
                payload.get("especialidade_sugerida"),
                confianca.get("score"),
                confianca.get("classificacao"),
                1 if revisao.get("human_in_the_loop", True) else 0,
                relatorio_path,
                json.dumps(payload, ensure_ascii=False),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def atualizar_caminho_relatorio(atendimento_id: int | None, relatorio_path: str) -> None:
    if not atendimento_id:
        return
    with _connect() as conn:
        conn.execute(
            "UPDATE atendimentos SET relatorio_path = ? WHERE id = ?",
            (relatorio_path, atendimento_id),
        )
        conn.commit()


def listar_atendimentos(limite: int = 20) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, criado_em, nome, idade, cidade, queixa_principal,
                   nivel_urgencia, especialidade_sugerida, confianca_classificacao,
                   relatorio_path
            FROM atendimentos
            ORDER BY id DESC
            LIMIT ?
            """,
            (limite,),
        ).fetchall()
    return [dict(row) for row in rows]


def carregar_memoria_db(limite: int = 5) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT payload_json FROM atendimentos ORDER BY id DESC LIMIT ?",
            (limite,),
        ).fetchall()

    memoria = []
    for row in rows:
        try:
            memoria.append(json.loads(row["payload_json"]))
        except json.JSONDecodeError:
            continue
    return memoria


def registrar_evento_db(evento: str, dados: dict[str, Any] | None = None) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO eventos (criado_em, evento, dados_json) VALUES (?, ?, ?)",
            (
                datetime.datetime.now().isoformat(timespec="seconds"),
                evento,
                json.dumps(dados or {}, ensure_ascii=False),
            ),
        )
        conn.commit()
