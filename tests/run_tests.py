"""
Executor de testes integrado para o Asclépio.
Executa todos os testes unitários sem depender obrigatoriamente do pytest.
"""
import inspect
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Garante que a raiz do projeto esteja no sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Importa módulos de teste
from tests import (
    test_clinical_tools,
    test_database,
    test_reviewer,
    test_safety,
    test_schemas,
)

MODULES = [
    ("Segurança Clínica (safety.py)", test_safety),
    ("Esquemas Pydantic (schemas.py)", test_schemas),
    ("Ferramentas Clínicas (clinical_tools.py)", test_clinical_tools),
    ("Revisor Médico (reviewer.py)", test_reviewer),
    ("Banco de Dados SQLite (database.py)", test_database),
]


def run_all() -> bool:
    total_passed = 0
    total_failed = 0
    start_time = time.time()

    print("=" * 65)
    print("⚕️  SUÍTE DE TESTES UNITÁRIOS - ASCLÉPIO")
    print("=" * 65)

    for group_name, module in MODULES:
        print(f"\n📁 Módulo: {group_name}")
        functions = [
            (name, func)
            for name, func in inspect.getmembers(module, inspect.isfunction)
            if name.startswith("test_")
        ]

        for name, func in functions:
            try:
                func()
                print(f"  ✅ [PASS] {name}")
                total_passed += 1
            except AssertionError as e:
                print(f"  ❌ [FAIL] {name}: Asserção falhou -> {e}")
                total_failed += 1
            except Exception as e:
                print(f"  💥 [ERR]  {name}: Exceção -> {e}")
                total_failed += 1

    elapsed = time.time() - start_time
    print("\n" + "=" * 65)
    print(f"Resultado: {total_passed} passaram, {total_failed} falharam ({elapsed:.2f}s)")
    print("=" * 65)

    return total_failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
