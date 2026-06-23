import datetime
import re
from pathlib import Path

from schemas import validar_relatorio

REPORTS_DIR = Path("relatorios")


def _safe_filename_name(name: str | None) -> str:
    base = name or "paciente"
    clean = re.sub(r"[^A-Za-z0-9_-]+", "_", base.lower()).strip("_")
    return clean or "paciente"


def salvar_relatorio(relatorio: dict) -> str:
    """Salva o relatório de atendimento em relatorios/*.txt."""
    relatorio = validar_relatorio(relatorio).model_dump(mode="json")
    p = relatorio.get("paciente", {})
    nome = _safe_filename_name(p.get("nome"))
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    REPORTS_DIR.mkdir(exist_ok=True)
    arquivo = REPORTS_DIR / f"asclepio_{nome}_{ts}.txt"

    separador = "=" * 60

    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(f"{separador}\n")
        f.write("  ASCLÉPIO - RESULTADO DO ATENDIMENTO\n")
        f.write(f"{separador}\n\n")
        f.write(f"Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")

        f.write("DADOS DO PACIENTE\n")
        f.write("-" * 30 + "\n")
        f.write(f"Nome:   {p.get('nome', '---')}\n")
        f.write(f"Idade:  {p.get('idade', '---')}\n")
        f.write(f"Sexo:   {p.get('sexo', '---')}\n")
        f.write(f"Cidade: {p.get('cidade', '---')}\n")
        f.write(f"Queixa principal: {p.get('queixa_principal', '---')}\n")
        f.write(f"Duração: {p.get('duracao', '---')}\n")
        f.write(f"Intensidade: {p.get('intensidade', '---')}\n")
        sinais = p.get("sinais_alarme") or []
        f.write(f"Sinais de alarme: {', '.join(sinais) if sinais else '---'}\n\n")

        f.write(f"NÍVEL DE URGÊNCIA: {relatorio.get('nivel_urgencia', '---')}\n\n")

        f.write("HIPÓTESE INICIAL - SINTOMAS PRINCIPAIS\n")
        f.write("-" * 30 + "\n")
        for sintoma in relatorio.get("sintomas_principais", []):
            f.write(f"- {sintoma}\n")

        f.write("\nPOSSÍVEIS CAUSAS\n")
        f.write("-" * 30 + "\n")
        for i, causa in enumerate(relatorio.get("possiveis_causas", []), 1):
            f.write(f"{i}. {causa}\n")

        f.write(f"\nESPECIALIDADE SUGERIDA: {relatorio.get('especialidade_sugerida', '---')}\n")

        f.write("\nORIENTAÇÃO - RECOMENDAÇÕES\n")
        f.write("-" * 30 + "\n")
        for recomendacao in relatorio.get("recomendacoes", []):
            f.write(f"- {recomendacao}\n")

        if relatorio.get("observacoes_importantes"):
            f.write(f"\nOBSERVAÇÕES: {relatorio['observacoes_importantes']}\n")

        estado = relatorio.get("estado", {})
        seguranca = relatorio.get("seguranca", {})
        confianca = relatorio.get("confianca", {})
        revisao = relatorio.get("revisao", {})

        f.write("\nCONTROLE DO AGENTE\n")
        f.write("-" * 30 + "\n")
        f.write(f"Qualidade dos dados: {estado.get('qualidade_dados', '---')}\n")
        f.write(f"Dados faltantes: {', '.join(estado.get('dados_faltantes', [])) or '---'}\n")
        f.write(f"Confiança: {confianca.get('classificacao', '---')} ({confianca.get('score', '---')})\n")
        f.write(f"Sinais de segurança: {', '.join(seguranca.get('sinais_detectados', [])) or '---'}\n")
        f.write(f"Revisão humana recomendada: {'sim' if revisao.get('human_in_the_loop') else 'nao'}\n")
        if revisao.get("alertas"):
            f.write("Alertas da revisão:\n")
            for alerta in revisao["alertas"]:
                f.write(f"- {alerta}\n")

        f.write(f"\n{separador}\n")
        f.write("AVISO: Documento gerado por IA. Caráter ORIENTATIVO.\n")
        f.write("Não substitui consulta médica presencial.\n")
        f.write("Emergências: SAMU 192 | Bombeiros 193\n")
        f.write(f"{separador}\n")

    return str(arquivo)


def listar_relatorios() -> list[Path]:
    """Retorna relatórios salvos, do mais recente para o mais antigo."""
    if not REPORTS_DIR.exists():
        return []
    return sorted(REPORTS_DIR.glob("asclepio_*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
