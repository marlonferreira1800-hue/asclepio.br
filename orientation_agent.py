import json
import logging

from client import client
from config import console
from prompts import PROMPT_ORIENTACAO
from agent_utils import extrair_json_array

logger = logging.getLogger(__name__)


class AgenteOrientacao:
    def orientar(self, hipotese: dict) -> list:
        try:
            with console.status(
                "[green]  Agente de Orientação gerando recomendações...[/]",
                spinner="dots2",
            ):
                raw = client.chamar(
                    prompt_sistema=PROMPT_ORIENTACAO,
                    mensagem=json.dumps(hipotese, ensure_ascii=False, indent=2),
                )

            recs = extrair_json_array(raw)
            if recs is None:
                return ["Procure um médico para avaliação presencial com os dados desta triagem."]
            return recs
        except Exception as e:
            logger.error("Falha na orientação", exc_info=e)
            return ["Procure um médico para avaliação presencial com os dados desta triagem."]
