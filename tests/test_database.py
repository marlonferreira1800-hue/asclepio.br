import sqlite3
from database import init_db


def test_init_db_cria_tabelas():
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = [row[0] for row in cursor.fetchall()]
    assert "atendimentos" in tabelas
    assert "eventos" in tabelas
    conn.close()


def test_salvar_e_listar_atendimentos():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)

    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO atendimentos (
            criado_em, nome, idade, queixa_principal, nivel_urgencia,
            especialidade_sugerida, confianca_score, payload_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-09-29 22:00:00", "Ana Costa", "30", "Febre", "BAIXO", "Clínico Geral", 0.75, "{}"),
    )
    conn.commit()

    cursor.execute("SELECT * FROM atendimentos")
    linhas = cursor.fetchall()
    assert len(linhas) == 1
    assert linhas[0]["nome"] == "Ana Costa"
    assert linhas[0]["nivel_urgencia"] == "BAIXO"
    conn.close()
