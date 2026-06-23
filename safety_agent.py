import json
import logging

from client import client
from config import console
from prompts import PROMPT_SEGURANCA_MEDICA
from safety import avaliar_seguranca
from agent_utils import extrair_json_objeto

logger = logging.getLogger(__name__)


class AgenteSegurancaMedica:
    def avaliar(self, dados_triagem: str, dados_estruturados: dict) -> dict:
        regra_local = avaliar_seguranca(
            [dados_triagem, json.dumps(dados_estruturados, ensure_ascii=False)],
            dados_estruturados,
        )

        try:
            with console.status(
                "[red]  Agente de Segurança Médica avaliando risco imediato...[/]",
                spinner="dots2",
            ):
                raw = client.chamar(
                    prompt_sistema=PROMPT_SEGURANCA_MEDICA,
                    mensagem=json.dumps(
                        {
                            "triagem": dados_triagem,
                            "dados_estruturados": dados_estruturados,
                            "regra_local": regra_local,
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                )

            avaliacao_ia = extrair_json_objeto(raw)
            if avaliacao_ia is None:
                raise ValueError("Resposta de segurança não é JSON válido")
        except Exception as e:
            logger.error("Falha na segurança médica", exc_info=e)
            console.print(f"[yellow]Segurança por IA falhou; usando regras locais: {e}[/]")
            avaliacao_ia = {}

        sinais = set(regra_local.get("sinais_detectados", []))
        sinais.update(avaliacao_ia.get("sinais_detectados") or [])

        ordem = {"BAIXO": 0, "MODERADO": 1, "ALTO": 2, "CRITICO": 3, "CRÍTICO": 3}
        nivel_local = regra_local.get("nivel_minimo", "BAIXO").upper()
        nivel_ia = str(avaliacao_ia.get("nivel_minimo") or "BAIXO").upper()
        nivel = nivel_ia if ordem.get(nivel_ia, 0) > ordem.get(nivel_local, 0) else nivel_local

        return {
            "nivel_minimo": nivel,
            "sinais_detectados": sorted(sinais),
            "mensagens": regra_local.get("mensagens", []),
            "motivos": avaliacao_ia.get("motivos") or regra_local.get("mensagens", []),
            "orientacao_imediata": avaliacao_ia.get("orientacao_imediata"),
            "bloquear_fluxo_normal": bool(avaliacao_ia.get("bloquear_fluxo_normal")) or nivel in {"ALTO", "CRITICO", "CRÍTICO"},
            "bloqueio_tratamento_caseiro": regra_local.get("bloqueio_tratamento_caseiro", False),
        }
