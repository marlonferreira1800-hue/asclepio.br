import logging

from client import client
from config import console
from prompts import PROMPT_PREDIAGNOSTICO
from agent_utils import extrair_json_objeto

logger = logging.getLogger(__name__)


class AgentePreDiagnostico:
    def analisar(self, dados_paciente: str) -> dict:
        try:
            with console.status(
                "[yellow]  Agente de Pré-Diagnóstico analisando seus dados...[/]",
                spinner="dots2",
            ):
                raw = client.chamar(
                    prompt_sistema=PROMPT_PREDIAGNOSTICO,
                    mensagem=dados_paciente,
                )

            data = extrair_json_objeto(raw)
            if data is None:
                raise ValueError("Resposta não é JSON válido")
            return data
        except Exception as e:
            logger.error("Falha no pré-diagnóstico", exc_info=e)
            console.print(f"[red]Erro ao gerar pré-diagnóstico: {e}[/]")
            return {
                "sintomas_principais": ["Não foi possível estruturar a análise automaticamente."],
                "possiveis_causas": ["Avaliação inconclusiva pela IA"],
                "nivel_urgencia": "MODERADO",
                "especialidade_sugerida": "Clínico Geral",
                "observacoes": (
                    "O sistema não conseguiu gerar um pré-diagnóstico confiável. "
                    "Oriente avaliação presencial, especialmente se houver piora ou sinais de alarme."
                ),
            }
