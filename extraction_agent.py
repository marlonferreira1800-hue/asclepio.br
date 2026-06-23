import logging

from client import client
from config import console
from prompts import PROMPT_EXTRACAO_CLINICA
from agent_utils import extrair_json_objeto

logger = logging.getLogger(__name__)


class AgenteExtracaoClinica:
    def extrair(self, dados_triagem: str, dados_basicos: dict | None = None) -> dict:
        try:
            with console.status(
                "[blue]  Agente de Extração Clínica estruturando os dados...[/]",
                spinner="dots2",
            ):
                raw = client.chamar(
                    prompt_sistema=PROMPT_EXTRACAO_CLINICA,
                    mensagem=dados_triagem,
                )

            data = extrair_json_objeto(raw)
            if data is None:
                raise ValueError("Resposta de extração não é JSON válido")
        except Exception as e:
            logger.error("Falha na extração clínica", exc_info=e)
            console.print(f"[yellow]Extração clínica por IA falhou; usando dados locais: {e}[/]")
            data = {}

        dados = dict(dados_basicos or {})
        for chave, valor in data.items():
            if valor not in (None, "", [], {}):
                dados[chave] = valor
        dados.setdefault("sintomas_associados", [])
        dados.setdefault("sinais_alarme", dados.get("sinais_alarme", []))
        dados.setdefault("doencas_previas", [])
        dados.setdefault("alergias", [])
        dados.setdefault("medicamentos_em_uso", [])
        dados.setdefault("contexto_especial", [])
        return dados
