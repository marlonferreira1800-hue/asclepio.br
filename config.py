import logging
import os
import sys
from pathlib import Path

from rich.console import Console

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def verificar_dependencias() -> None:
    faltando = []
    try:
        import openai  # noqa: F401
    except ImportError:
        faltando.append("openai")
    try:
        import rich  # noqa: F401
    except ImportError:
        faltando.append("rich")
    try:
        import pydantic  # noqa: F401
    except ImportError:
        faltando.append("pydantic")

    if faltando:
        print("\n[ERRO] Dependencias nao encontradas. Execute:")
        print(f"\n    pip install {' '.join(faltando)}\n")
        sys.exit(1)


def _find_dotenv_path(start: Path) -> Path | None:
    for parent in [start] + list(start.parents):
        candidate = parent / ".env"
        if candidate.is_file():
            return candidate
    return None


def _read_dotenv(path: Path | None) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path:
        return values

    try:
        for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                values[key] = value
    except OSError:
        pass

    return values


verificar_dependencias()

_dotenv_path = _find_dotenv_path(Path(__file__).resolve().parent)
_dotenv = _read_dotenv(_dotenv_path)

try:
    from dotenv import load_dotenv

    if _dotenv_path:
        load_dotenv(_dotenv_path)
except Exception:
    pass

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY") or _dotenv.get("NVIDIA_API_KEY", "")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL") or _dotenv.get("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL") or _dotenv.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
APP_NAME = os.getenv("APP_NAME") or _dotenv.get("APP_NAME", "Asclépio")

PLACEHOLDER_KEYS = {"sua_chave_aqui", "seu_api_key_aqui", "your_api_key_here"}

if not NVIDIA_API_KEY or NVIDIA_API_KEY.strip().lower() in PLACEHOLDER_KEYS:
    print("\n[ERRO] NVIDIA_API_KEY nao encontrado. Verifique o arquivo .env na pasta do projeto.")
    print("Edite o .env e coloque sua chave real da NVIDIA NIM.")
    sys.exit(1)

console = Console()
