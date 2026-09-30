#!/usr/bin/env python3
import sys

from rich.align import Align
from rich.prompt import Prompt
from rich.rule import Rule

from agents import (
    AgenteExtracaoClinica,
    AgenteOrientacao,
    AgentePreDiagnostico,
    AgenteSegurancaMedica,
    AgenteTriagem,
)
from config import console
from interface import (
    exibir_arquitetura,
    exibir_aviso_legal,
    exibir_banner,
    exibir_historico_relatorios,
    exibir_resultado_atendimento,
)
from reports import listar_relatorios, salvar_relatorio
from clinical_tools import calcular_confianca, planejar_proximos_passos
from database import atualizar_caminho_relatorio, listar_atendimentos, salvar_atendimento
from knowledge import formatar_conhecimento, recuperar_conhecimento
from memory import carregar_memoria, salvar_memoria
from observability import registrar_evento
from reviewer import revisar_relatorio
from safety import elevar_urgencia
from state import CaseState


def montar_relatorio(
    triagem: AgenteTriagem,
    analise: dict,
    recomendacoes: list,
    estado: CaseState,
    seguranca: dict,
    conhecimento: list,
    planejamento: list,
    confianca: dict,
) -> dict:
    return {
        "paciente": triagem.dados_paciente,
        "sintomas_principais": analise.get("sintomas_principais", []),
        "possiveis_causas": analise.get("possiveis_causas", []),
        "nivel_urgencia": analise.get("nivel_urgencia", "BAIXO"),
        "especialidade_sugerida": analise.get("especialidade_sugerida", "Clínico Geral"),
        "recomendacoes": recomendacoes,
        "observacoes_importantes": analise.get("observacoes", ""),
        "estado": estado.to_dict(),
        "seguranca": seguranca,
        "conhecimento": conhecimento,
        "planejamento": planejamento,
        "confianca": confianca,
    }


def executar_atendimento() -> None:
    registrar_evento("atendimento_iniciado")
    exibir_banner()
    exibir_aviso_legal()
    exibir_arquitetura()

    console.print()
    try:
        Prompt.ask("[dim]  Pressione ENTER para iniciar a triagem[/]", default="")
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)

    console.print()
    console.print(Rule("[bold cyan]  AGENTE 1 - Triagem Médica  [/]", style="cyan"))
    triagem = AgenteTriagem()
    dados_coletados = triagem.coletar()

    console.print()
    console.print(Rule("[bold blue]  AGENTE 2 - Extração Clínica  [/]", style="blue"))
    dados_estruturados = AgenteExtracaoClinica().extrair(dados_coletados, triagem.dados_paciente)
    triagem.dados_paciente.update(dados_estruturados)
    console.print("  [blue]✓[/]  Dados clínicos estruturados")

    estado = CaseState.from_triagem(triagem.dados_paciente, triagem.historico)
    textos_caso = [dados_coletados, estado.resumo_para_ia()]

    console.print()
    console.print(Rule("[bold red]  AGENTE 3 - Segurança Médica  [/]", style="red"))
    seguranca = AgenteSegurancaMedica().avaliar(dados_coletados, estado.to_dict())
    console.print("  [red]✓[/]  Segurança médica revisada")

    conhecimento = recuperar_conhecimento("\n".join(textos_caso))
    planejamento = planejar_proximos_passos(estado.to_dict(), seguranca)
    confianca = calcular_confianca(estado.to_dict(), seguranca)
    memoria = carregar_memoria()
    registrar_evento("triagem_concluida", {
        "estado": estado.to_dict(),
        "seguranca": seguranca,
        "memoria_recente": len(memoria),
    })

    contexto_agente = "\n\n".join([
        dados_coletados,
        estado.resumo_para_ia(),
        formatar_conhecimento(conhecimento),
        "PLANO DO AGENTE:\n- " + "\n- ".join(planejamento),
        f"MEMÓRIA RECENTE DISPONÍVEL: {len(memoria)} atendimento(s).",
    ])

    console.print()
    console.print(Rule("[bold yellow]  AGENTE 4 - Pré-Diagnóstico  [/]", style="yellow"))
    console.print()
    analise = AgentePreDiagnostico().analisar(contexto_agente)
    analise = elevar_urgencia(analise, seguranca)
    console.print("  [yellow]✓[/]  Análise concluída")

    console.print()
    console.print(Rule("[bold green]  AGENTE 5 - Orientação  [/]", style="green"))
    console.print()
    recomendacoes = AgenteOrientacao().orientar(analise)
    console.print("  [green]✓[/]  Recomendações geradas")

    relatorio = montar_relatorio(
        triagem,
        analise,
        recomendacoes,
        estado,
        seguranca,
        conhecimento,
        planejamento,
        confianca,
    )
    relatorio["revisao"] = revisar_relatorio(relatorio)
    salvar_memoria(relatorio)
    atendimento_id = salvar_atendimento(relatorio)
    relatorio["atendimento_id"] = atendimento_id
    registrar_evento("relatorio_gerado", {
        "atendimento_id": atendimento_id,
        "nivel_urgencia": relatorio["nivel_urgencia"],
        "confianca": confianca,
        "alertas_revisao": len(relatorio["revisao"].get("alertas", [])),
    })
    exibir_resultado_atendimento(relatorio)

    console.print()
    try:
        salvar = Prompt.ask(
            "  [bold]Salvar relatório em arquivo .txt?[/]",
            choices=["sim", "não", "s", "n"],
            default="sim",
        )
        if salvar.lower() in {"sim", "s"}:
            arquivo = salvar_relatorio(relatorio)
            atualizar_caminho_relatorio(atendimento_id, arquivo)
            console.print(f"\n  [green]✓  Relatório salvo:[/] [bold]{arquivo}[/]")
    except (KeyboardInterrupt, EOFError):
        pass

    console.print()
    console.print(Rule(style="cyan"))
    console.print(Align.center(
        "[bold cyan]⚕  Cuide-se! O Asclépio recomenda acompanhamento médico regular.  [/]"
    ))
    console.print(Rule(style="cyan"))
    console.print()


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in {"--relatorios", "--relatórios", "relatorios", "relatórios"}:
        exibir_historico_relatorios(listar_relatorios())
        return

    if len(sys.argv) > 1 and sys.argv[1] in {"--atendimentos", "atendimentos", "--banco"}:
        for item in listar_atendimentos():
            console.print(
                f"[cyan]#{item['id']}[/] {item['criado_em']} | "
                f"{item.get('nome') or 'paciente'} | "
                f"{item.get('nivel_urgencia') or 'sem urgência'} | "
                f"{item.get('queixa_principal') or 'sem queixa'}"
            )
        return
    from config import validar_api_key
    validar_api_key(obrigatorio=True)
    executar_atendimento()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]  Sessão encerrada. Cuide-se! 👋[/]\n")
    except Exception as e:
        console.print(f"\n[red bold]✖  Erro inesperado: {e}[/]")
        console.print("[dim]Verifique sua chave de API e conexão com a internet.[/]")
        sys.exit(1)
