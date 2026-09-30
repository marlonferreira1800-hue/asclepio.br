import os
import sqlite3
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None

# Configura ambiente de testes antes de importar módulos
os.environ["NVIDIA_API_KEY"] = "mock_test_key_12345"
os.environ["NVIDIA_MODEL"] = "meta/llama-3.3-70b-instruct"
os.environ["NVIDIA_BASE_URL"] = "https://mock.api.nvidia.com/v1"
os.environ["APP_NAME"] = "Asclépio Testes"
os.environ["ASCLEPIO_DB_PATH"] = ":memory:"


if pytest is not None:
    @pytest.fixture
    def mock_dados_paciente():
        return {
            "nome": "Carlos Silva",
            "idade": "42 anos",
            "sexo": "Masculino",
            "cidade": "São Paulo",
            "queixa_principal": "Febre e dor de cabeça há 2 dias",
            "sintomas_associados": ["moleza", "dor no corpo"],
            "sinais_alarme": [],
            "doencas_previas": ["hipertensão"],
            "alergias": ["dipirona"],
            "medicamentos_em_uso": ["losartana"],
            "contexto_especial": [],
        }

    @pytest.fixture
    def db_memoria():
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        from database import init_db
        init_db(conn)
        yield conn
        conn.close()
