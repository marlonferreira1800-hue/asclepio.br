import logging
import re
import sys

from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from client import client
from config import APP_NAME, console
from prompts import PROMPT_TRIAGEM
from triage_constants import (
    COMANDOS_SAIDA,
    CONFIRMACOES_POSITIVAS,
    GATILHOS_TRIAGEM,
    IDADE_MAX,
    IDADE_MIN,
    MAX_RETRIES,
    SINAIS_ALARME,
    TERMOS_NAO_NOME,
)

logger = logging.getLogger(__name__)


def _nome_valido(candidato: str) -> bool:
    palavras = candidato.strip().split()
    if not 1 <= len(palavras) <= 4:
        return False
    if any(p.lower() in TERMOS_NAO_NOME for p in palavras):
        return False
    return all(re.fullmatch(r"[A-Za-zÀ-ÿ'-]+", p) for p in palavras)


class AgenteTriagem:
    def __init__(self):
        self.historico: list = []
        self.dados_paciente: dict = {}
        self._tentativas_confirmacao = 0

    def _chamar_ia(self, mensagem_usuario: str) -> str:
        try:
            resposta = client.chamar(
                prompt_sistema=PROMPT_TRIAGEM,
                mensagem=mensagem_usuario,
                historico=self.historico,
            )
            self.historico.append({"role": "user", "content": mensagem_usuario})
            self.historico.append({"role": "model", "content": resposta})
            return resposta
        except Exception as e:
            logger.error("Erro ao chamar IA de triagem", exc_info=e)
            console.print(f"[red]Erro de comunicação com a IA: {e}[/]")
            return "Desculpe, ocorreu um erro. Pode repetir?"

    def _extrair_dados(self, texto: str):
        texto_limpo = texto.strip()
        low = texto_limpo.lower()

        m = re.search(r"\b(\d{1,3})\s*anos?\b", texto_limpo, re.IGNORECASE)
        if m and "idade" not in self.dados_paciente:
            idade = int(m.group(1))
            if IDADE_MIN <= idade <= IDADE_MAX:
                self.dados_paciente["idade"] = f"{idade} anos"

        if "sexo" not in self.dados_paciente:
            if re.search(r"\b(masculino|homem|masc|male)\b", low):
                self.dados_paciente["sexo"] = "Masculino"
            elif re.search(r"\b(feminino|mulher|fem|female)\b", low):
                self.dados_paciente["sexo"] = "Feminino"
            elif re.search(r"\b(não-binário|nao-binario|non-binary|outro)\b", low):
                self.dados_paciente["sexo"] = "Outro"

        if "cidade" not in self.dados_paciente:
            cidade_match = re.search(
                r"(?:moro em|sou de|cidade(?: é|:)?|estou em)\s+([A-Za-zÀ-ÿ\s'-]{2,40})",
                texto_limpo,
                re.IGNORECASE,
            )
            if cidade_match:
                cidade = re.split(r"[,.;]|\s+e\s+", cidade_match.group(1).strip())[0]
                if cidade:
                    self.dados_paciente["cidade"] = cidade.title()

        if "nome" not in self.dados_paciente:
            nome_match = re.search(
                r"(?:meu nome é|me chamo|chamo-me|eu sou|sou o|sou a)\s+([A-Za-zÀ-ÿ'-]+(?:\s+[A-Za-zÀ-ÿ'-]+){0,3})",
                texto_limpo,
                re.IGNORECASE,
            )
            if not nome_match:
                nome_match = re.match(
                    r"^\s*([A-Za-zÀ-ÿ'-]+(?:\s+[A-Za-zÀ-ÿ'-]+){0,2})\s*,?\s+tenho\s+\d{1,3}\s*anos?",
                    texto_limpo,
                    re.IGNORECASE,
                )

            if nome_match:
                candidato = re.split(
                    r"[,.;]|\s+(?:tenho|estou|sinto|com|e|mas|porque)\s+",
                    nome_match.group(1).strip(),
                    maxsplit=1,
                    flags=re.IGNORECASE,
                )[0].strip()
                if _nome_valido(candidato):
                    self.dados_paciente["nome"] = " ".join(candidato.split()[:4]).title()

        if "intensidade" not in self.dados_paciente:
            intensidade = re.search(
                r"\b(?:dor|desconforto|intensidade)?\s*(?:nota|nível|nivel)?\s*(\d{1,2})\s*(?:/|de)\s*10\b",
                low,
            )
            if intensidade:
                valor = int(intensidade.group(1))
                if 0 <= valor <= 10:
                    self.dados_paciente["intensidade"] = f"{valor}/10"

        if "duracao" not in self.dados_paciente:
            duracao = re.search(
                r"(?:há|ha|faz|desde)\s+([0-9]+|\w+)\s+(minutos?|horas?|dias?|semanas?|meses?)",
                low,
            )
            if duracao:
                self.dados_paciente["duracao"] = duracao.group(0)

        if "queixa_principal" not in self.dados_paciente:
            queixa = re.search(r"(?:estou com|sinto|tenho)\s+([^,.!?]{3,80})", texto_limpo, re.IGNORECASE)
            if queixa:
                valor = queixa.group(1).strip()
                if not re.fullmatch(r"\d{1,3}\s*anos?", valor, re.IGNORECASE):
                    self.dados_paciente["queixa_principal"] = valor

        sinais = [s for s in SINAIS_ALARME if s in low]
        if sinais:
            atuais = set(self.dados_paciente.get("sinais_alarme", []))
            self.dados_paciente["sinais_alarme"] = sorted(atuais.union(sinais))

    def _e_confirmacao(self, texto: str) -> bool:
        return any(p in texto.lower() for p in CONFIRMACOES_POSITIVAS)

    def _triagem_concluida(self, resposta_ia: str) -> bool:
        return any(g in resposta_ia.lower() for g in GATILHOS_TRIAGEM)

    def _montar_resumo(self) -> str:
        resumo = "DADOS COLETADOS NA TRIAGEM MÉDICA:\n\n"
        resumo += "Respostas do paciente durante a anamnese:\n"
        for item in self.historico:
            if item["role"] == "user":
                resumo += f"• {item['content']}\n"

        if self.dados_paciente:
            resumo += "\nDados estruturados identificados:\n"
            for k, v in self.dados_paciente.items():
                resumo += f"• {k.capitalize()}: {v}\n"
        return resumo

    def coletar(self) -> str:
        console.print()
        with console.status("[cyan]Agente de Triagem iniciando...[/]", spinner="dots"):
            resposta = self._chamar_ia("Olá, iniciar atendimento")
        self._renderizar_ia(resposta)

        triagem_pronta = False
        while not triagem_pronta:
            console.print()
            try:
                entrada = Prompt.ask("[bold cyan]  Você[/]")
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]  Encerrando... Cuide-se! 👋[/]")
                sys.exit(0)

            entrada = entrada.strip()
            if not entrada:
                continue
            if entrada.lower() in COMANDOS_SAIDA:
                console.print("\n[yellow]  Encerrando Asclépio. Cuide-se! 👋[/]")
                sys.exit(0)

            self._extrair_dados(entrada)
            with console.status("[cyan]  Processando...[/]", spinner="dots"):
                resposta = self._chamar_ia(entrada)
            self._renderizar_ia(resposta)

            if self._triagem_concluida(resposta):
                triagem_pronta = True
                console.print()
                while True:
                    try:
                        confirmacao = Prompt.ask("[bold cyan]  Você[/]", default="sim")
                    except (KeyboardInterrupt, EOFError):
                        sys.exit(0)

                    if self._e_confirmacao(confirmacao):
                        break

                    self._tentativas_confirmacao += 1
                    if self._tentativas_confirmacao >= MAX_RETRIES:
                        console.print("[yellow]Máximo de tentativas atingido. Prosseguindo mesmo assim...[/]")
                        break

                    console.print("[yellow]Entendido. Continuando a coleta de informações...[/]")
                    with console.status("[cyan]  Processando...[/]", spinner="dots"):
                        resposta = self._chamar_ia(confirmacao)
                    self._renderizar_ia(resposta)
                    triagem_pronta = False
                    break

        return self._montar_resumo()

    def _renderizar_ia(self, mensagem: str):
        console.print()
        console.print(Panel(
            Text(mensagem, justify="left"),
            title=f"[bold cyan]⚕  {APP_NAME} - Agente de Triagem[/]",
            border_style="cyan",
            padding=(1, 2),
        ))
