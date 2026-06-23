import datetime

from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from config import APP_NAME, console


def exibir_banner():
    console.clear()
    console.print(Rule(style="cyan"))
    console.print(Align.center(f"[bold cyan]⚕ {APP_NAME}[/]"))
    console.print(Align.center("[bold white]Agente de Pré-Diagnóstico com Inteligência Artificial[/]"))
    console.print(Align.center("[dim]Sistema Multi-Agente • NVIDIA NIM • Python Terminal[/]"))
    console.print(Rule(style="cyan"))


def exibir_aviso_legal():
    console.print()
    console.print(Panel(
        f"O {APP_NAME} é um sistema de [bold]pré-diagnóstico orientativo[/] baseado em IA.\n"
        "[bold red]NÃO substitui consulta médica presencial.[/]\n\n"
        "[dim]• Em emergências: ligue [bold]192[/] (SAMU) ou [bold]193[/] (Bombeiros)\n"
        "• As hipóteses geradas são apenas indicativas\n"
        "• Sempre consulte um profissional de saúde habilitado[/]",
        title="[bold yellow]⚠  AVISO MÉDICO-LEGAL[/]",
        border_style="yellow",
        padding=(1, 3),
    ))


def exibir_arquitetura():
    console.print()
    console.print(Rule("[bold cyan]  Arquitetura Multi-Agente  [/]", style="cyan"))
    console.print()

    tabela = Table(box=box.ROUNDED, border_style="cyan", show_header=True, padding=(0, 2))
    tabela.add_column("Agente", style="bold", width=26)
    tabela.add_column("Função", style="dim", width=42)
    tabela.add_column("Tecnologia", style="cyan", width=18)

    tabela.add_row("1. AgenteTriagem", "Anamnese conversacional com o paciente", "NVIDIA NIM")
    tabela.add_row("2. AgenteExtracaoClinica", "Converte conversa em dados estruturados", "NVIDIA NIM + JSON")
    tabela.add_row("3. AgenteSegurancaMedica", "Avalia risco imediato e sinais de alarme", "NVIDIA NIM + regras")
    tabela.add_row("4. AgentePreDiagnostico", "Análise clínica e hipóteses diagnósticas", "NVIDIA NIM + JSON")
    tabela.add_row("5. AgenteOrientacao", "Recomendações personalizadas", "NVIDIA NIM + JSON")

    console.print(tabela)
    console.print()
    console.print(Rule(style="cyan"))


def exibir_resultado_atendimento(relatorio: dict):
    console.print()
    console.print(Rule("[bold white]  RESULTADO DO ATENDIMENTO  [/]", style="bright_cyan"))

    p = relatorio.get("paciente", {})
    tabela_pac = Table(box=box.SIMPLE, show_header=False, padding=(0, 2), border_style="dim")
    tabela_pac.add_column("Campo", style="dim", width=12)
    tabela_pac.add_column("Valor", style="bold white", width=38)
    tabela_pac.add_row("Nome", p.get("nome", "—"))
    tabela_pac.add_row("Idade", p.get("idade", "—"))
    tabela_pac.add_row("Sexo", p.get("sexo", "—"))
    tabela_pac.add_row("Cidade", p.get("cidade", "—"))
    tabela_pac.add_row("Queixa", p.get("queixa_principal", "—"))
    tabela_pac.add_row("Duração", p.get("duracao", "—"))
    tabela_pac.add_row("Intensidade", p.get("intensidade", "—"))
    sinais = p.get("sinais_alarme") or []
    tabela_pac.add_row("Alarmes", ", ".join(sinais) if sinais else "—")
    tabela_pac.add_row("Data", datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))

    console.print(Panel(
        tabela_pac,
        title="[bold cyan]Paciente[/]",
        border_style="cyan",
        padding=(0, 1),
    ))
    console.print()

    urg = relatorio.get("nivel_urgencia", "BAIXO").upper().replace("Í", "I")
    urgencia_map = {
        "BAIXO": ("green", "URGÊNCIA BAIXA", "Consulta de rotina recomendada"),
        "MODERADO": ("yellow", "URGÊNCIA MODERADA", "Consulte um médico em 1 a 3 dias"),
        "ALTO": ("orange1", "URGÊNCIA ALTA", "Busque atendimento médico HOJE"),
        "CRITICO": ("red", "URGÊNCIA CRÍTICA", "VÁ AO PRONTO-SOCORRO AGORA"),
        "CRÍTICO": ("red", "URGÊNCIA CRÍTICA", "VÁ AO PRONTO-SOCORRO AGORA"),
    }

    cor, nivel_txt, urg_desc = urgencia_map.get(urg, urgencia_map["BAIXO"])
    console.print(Panel(
        f"[{cor} bold]{nivel_txt}[/]\n\n[{cor}]{urg_desc}[/]",
        border_style=cor,
        padding=(1, 3),
    ))
    console.print()

    sintomas = relatorio.get("sintomas_principais", [])
    console.print(Panel(
        "\n".join(f"  • {s}" for s in sintomas) or "  —",
        title="[bold]Sintomas Principais[/]",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()

    causas = relatorio.get("possiveis_causas", [])
    causas_txt = "\n".join(f"  {i}. {causa}" for i, causa in enumerate(causas, 1))
    console.print(Panel(
        causas_txt or "  —",
        title="[bold]Possíveis Causas[/]",
        border_style="blue",
        padding=(1, 2),
    ))
    console.print()

    especialidade = relatorio.get("especialidade_sugerida", "Clínico Geral")
    console.print(Panel(
        f"\n  [bold cyan]{especialidade}[/]\n",
        title="[bold]Especialidade Sugerida[/]",
        border_style="cyan",
        padding=(0, 2),
    ))
    console.print()

    recs = relatorio.get("recomendacoes", [])
    recs_txt = "\n".join(f"  → {r}" for r in recs) or "  —"
    console.print(Panel(
        recs_txt,
        title="[bold]Orientação - Recomendações[/]",
        border_style="green",
        padding=(1, 2),
    ))
    console.print()

    obs = relatorio.get("observacoes_importantes", "")
    if obs:
        console.print(Panel(
            f"  {obs}",
            title="[bold]Observações Clínicas[/]",
            border_style="dim",
            padding=(1, 2),
        ))
        console.print()

    confianca = relatorio.get("confianca") or {}
    seguranca = relatorio.get("seguranca") or {}
    revisao = relatorio.get("revisao") or {}
    contexto_txt = (
        f"Confiança: {confianca.get('classificacao', '—')} ({confianca.get('score', '—')})\n"
        f"Qualidade dos dados: {relatorio.get('estado', {}).get('qualidade_dados', '—')}\n"
        f"Dados faltantes: {', '.join(relatorio.get('estado', {}).get('dados_faltantes', [])) or '—'}\n"
        f"Sinais detectados: {', '.join(seguranca.get('sinais_detectados', [])) or '—'}\n"
        f"Revisão humana recomendada: {'sim' if revisao.get('human_in_the_loop') else 'não'}"
    )
    console.print(Panel(
        contexto_txt,
        title="[bold]Controle do Agente[/]",
        border_style="magenta",
        padding=(1, 2),
    ))
    console.print()

    alertas = revisao.get("alertas") or []
    if alertas:
        console.print(Panel(
            "\n".join(f"  • {alerta}" for alerta in alertas),
            title="[bold yellow]Revisão de Segurança[/]",
            border_style="yellow",
            padding=(1, 2),
        ))
        console.print()

    console.print(Panel(
        f"[yellow]⚠ Este relatório foi gerado por Inteligência Artificial ({APP_NAME}).\n"
        "Tem caráter [bold]ORIENTATIVO[/bold] e [bold]NÃO substitui[/bold] consulta médica presencial.\n"
        "Em emergências: [bold red]SAMU 192[/bold red] | [bold red]Bombeiros 193[/bold red][/]",
        border_style="yellow",
        padding=(0, 2),
    ))


def exibir_historico_relatorios(relatorios: list):
    console.print()
    console.print(Rule("[bold cyan]  Relatórios Salvos  [/]", style="cyan"))

    if not relatorios:
        console.print(Panel(
            "Nenhum relatório salvo ainda.",
            border_style="yellow",
            padding=(1, 2),
        ))
        return

    tabela = Table(box=box.SIMPLE, border_style="cyan", show_header=True, padding=(0, 1))
    tabela.add_column("#", style="dim", width=4)
    tabela.add_column("Arquivo", style="bold white")
    tabela.add_column("Modificado em", style="cyan", width=18)

    for i, arquivo in enumerate(relatorios, 1):
        modificado = datetime.datetime.fromtimestamp(arquivo.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
        tabela.add_row(str(i), arquivo.name, modificado)

    console.print(tabela)
