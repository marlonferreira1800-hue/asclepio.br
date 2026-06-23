from __future__ import annotations

import datetime as _dt
import json
import mimetypes
import os
import sqlite3
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"
STATIC = FRONTEND / "static"
DB_PATH = Path(os.environ.get("ASCLEPIO_DB_PATH", ROOT / "data" / "asclepio.db"))
REPORTS = Path(os.environ.get("ASCLEPIO_REPORTS_DIR", ROOT / "relatorios"))


def _init_db(conn: sqlite3.Connection) -> None:
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
    existing = {row[1] for row in conn.execute("PRAGMA table_info(atendimentos)").fetchall()}
    migrations = {
        "nome": "TEXT",
        "idade": "TEXT",
        "sexo": "TEXT",
        "cidade": "TEXT",
        "queixa_principal": "TEXT",
        "nivel_urgencia": "TEXT",
        "especialidade_sugerida": "TEXT",
        "confianca_score": "REAL",
        "confianca_classificacao": "TEXT",
        "revisao_humana": "INTEGER NOT NULL DEFAULT 1",
        "relatorio_path": "TEXT",
        "payload_json": "TEXT NOT NULL DEFAULT '{}'",
    }
    for column, definition in migrations.items():
        if column not in existing:
            conn.execute(f"ALTER TABLE atendimentos ADD COLUMN {column} {definition}")
    conn.commit()


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _init_db(conn)
    return conn


def _split(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.replace(";", ",").split(",") if part.strip()]


def _urgency(payload: dict) -> tuple[str, list[str]]:
    text = " ".join(
        str(payload.get(key) or "")
        for key in ("sintomas", "sinais_alarme", "sintomas_associados", "contexto_especial")
    ).lower()
    detected = []
    critical = ["dor no peito", "falta de ar", "desmaio", "convulsao", "confusao", "sangramento"]
    high = ["febre alta", "rigidez", "fraqueza", "piora rapida", "gestante", "idoso"]
    for term in critical + high:
        if term in text:
            detected.append(term)
    intensity = payload.get("intensidade")
    try:
        intensity = int(intensity) if intensity not in (None, "") else 0
    except (TypeError, ValueError):
        intensity = 0
    if any(term in detected for term in critical) or intensity >= 9:
        return "CRITICO", detected
    if any(term in detected for term in high) or intensity >= 7:
        return "ALTO", detected
    if intensity >= 4 or payload.get("sinais_alarme"):
        return "MODERADO", detected
    return "BAIXO", detected


def _specialty(symptoms: str) -> str:
    text = symptoms.lower()
    if any(word in text for word in ("peito", "palpitacao", "pressao")):
        return "Cardiologia"
    if any(word in text for word in ("falta de ar", "tosse", "chiado")):
        return "Pneumologia"
    if any(word in text for word in ("cabeca", "tontura", "convulsao", "formigamento")):
        return "Neurologia"
    if any(word in text for word in ("barriga", "abdomen", "vomito", "diarreia")):
        return "Gastroenterologia"
    return "Clinico Geral"


def _build_report(payload: dict) -> dict:
    symptoms = str(payload.get("sintomas") or "").strip()
    if len(symptoms) < 3:
        raise ValueError("Informe os sintomas principais com pelo menos 3 caracteres.")

    urgency, detected = _urgency(payload)
    specialty = _specialty(symptoms)
    associated = _split(payload.get("sintomas_associados"))
    alarm = _split(payload.get("sinais_alarme"))
    causes = {
        "CRITICO": ["Condicao potencialmente grave", "Evento agudo que exige avaliacao imediata"],
        "ALTO": ["Quadro com sinais de alerta", "Exacerbacao de condicao clinica"],
        "MODERADO": ["Infeccao ou inflamacao", "Quadro clinico em evolucao"],
        "BAIXO": ["Quadro leve ou inicial", "Sintoma inespecifico que precisa de acompanhamento"],
    }[urgency]
    recommendations = [
        "Procure atendimento presencial para confirmacao diagnostica.",
        "Nao use medicamentos novos sem orientacao profissional.",
    ]
    if urgency in {"CRITICO", "ALTO"}:
        recommendations.insert(0, "Busque atendimento de urgencia agora. Em emergencia, acione SAMU 192.")
    else:
        recommendations.append("Observe evolucao nas proximas horas e retorne se houver piora.")

    return {
        "paciente": {
            "nome": payload.get("nome") or None,
            "idade": f"{payload.get('idade')} anos" if payload.get("idade") not in (None, "") else None,
            "sexo": payload.get("sexo") or None,
            "cidade": payload.get("cidade") or None,
            "queixa_principal": symptoms,
            "duracao": payload.get("duracao") or None,
            "intensidade": f"{payload.get('intensidade')}/10" if payload.get("intensidade") not in (None, "") else None,
            "sintomas_associados": associated,
            "sinais_alarme": alarm,
            "doencas_previas": _split(payload.get("doencas_previas")),
            "alergias": _split(payload.get("alergias")),
            "medicamentos_em_uso": _split(payload.get("medicamentos_em_uso")),
            "contexto_especial": _split(payload.get("contexto_especial")),
        },
        "sintomas_principais": [symptoms, *associated],
        "possiveis_causas": causes,
        "nivel_urgencia": urgency,
        "especialidade_sugerida": specialty,
        "recomendacoes": recommendations,
        "observacoes_importantes": "Resultado orientativo gerado localmente pelo Asclepio.",
        "seguranca": {"sinais_detectados": sorted(set(detected + alarm))},
        "confianca": {"score": 0.72, "classificacao": "moderada", "motivo": "Triagem baseada nos dados informados."},
        "revisao": {"aprovado": True, "alertas": [], "human_in_the_loop": True},
    }


def _save_report(report: dict, save_txt: bool) -> dict:
    now = _dt.datetime.now().isoformat(timespec="seconds")
    payload_json = json.dumps(report, ensure_ascii=False)
    patient = report["paciente"]
    confidence = report["confianca"]
    report_path = None

    with _connect() as conn:
        existing = {row[1] for row in conn.execute("PRAGMA table_info(atendimentos)").fetchall()}
        row = {
            "criado_em": now,
            "nome": patient.get("nome"),
            "idade": patient.get("idade"),
            "sexo": patient.get("sexo"),
            "cidade": patient.get("cidade"),
            "queixa_principal": patient.get("queixa_principal"),
            "nivel_urgencia": report.get("nivel_urgencia"),
            "especialidade_sugerida": report.get("especialidade_sugerida"),
            "confianca_score": confidence.get("score"),
            "confianca_classificacao": confidence.get("classificacao"),
            "revisao_humana": 1,
            "relatorio_path": report_path,
            "payload_json": payload_json,
            "paciente_json": json.dumps(patient, ensure_ascii=False),
            "resultado_json": payload_json,
        }
        columns = [column for column in row if column in existing]
        placeholders = ", ".join("?" for _ in columns)
        cursor = conn.execute(
            f"INSERT INTO atendimentos ({', '.join(columns)}) VALUES ({placeholders})",
            tuple(row[column] for column in columns),
        )
        report["atendimento_id"] = int(cursor.lastrowid)

        if save_txt:
            REPORTS.mkdir(exist_ok=True)
            report_path = REPORTS / f"asclepio_paciente_{_dt.datetime.now():%Y%m%d_%H%M%S}.txt"
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            conn.execute(
                "UPDATE atendimentos SET relatorio_path = ? WHERE id = ?",
                (str(report_path), report["atendimento_id"]),
            )
            report["arquivo_relatorio"] = str(report_path)

        conn.commit()
    return report


def _list_history(limit: int) -> list[dict]:
    limit = max(1, min(limit, 100))
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
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


class Handler(BaseHTTPRequestHandler):
    server_version = "AsclepioSite/1.0"

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        super().end_headers()

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")

    def _send_json(self, data: object, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404)
            return
        content = path.read_bytes()
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(content)))
        if path.is_relative_to(STATIC):
            self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            self._send_json({"status": "ok", "app": "Asclepio"})
            return
        if parsed.path == "/healthz":
            self._send_json({"ok": True})
            return
        if parsed.path == "/api/atendimentos":
            query = parse_qs(parsed.query)
            limit = int(query.get("limite", ["20"])[0] or 20)
            self._send_json(_list_history(limit))
            return
        if parsed.path == "/":
            self._send_file(FRONTEND / "index.html")
            return
        if parsed.path.startswith("/static/"):
            target = (FRONTEND / parsed.path.lstrip("/")).resolve()
            if FRONTEND.resolve() in target.parents:
                self._send_file(target)
                return
        self.send_error(404)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/atendimento":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            report = _save_report(_build_report(payload), bool(payload.get("salvar_txt", True)))
            self._send_json(report)
        except Exception as exc:
            self._send_json({"detail": str(exc)}, status=500)


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT") or os.environ.get("ASCLEPIO_PORT", "8000"))
    host = os.environ.get("HOST") or ("0.0.0.0" if os.environ.get("PORT") else "127.0.0.1")
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Asclepio site em http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
