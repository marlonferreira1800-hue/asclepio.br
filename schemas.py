from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

NivelUrgencia = Literal["BAIXO", "MODERADO", "ALTO", "CRITICO", "CRÍTICO"]


class PacienteSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    nome: str | None = None
    idade: str | None = None
    sexo: str | None = None
    cidade: str | None = None
    queixa_principal: str | None = None
    duracao: str | None = None
    intensidade: str | None = None
    sintomas_associados: list[str] = Field(default_factory=list)
    sinais_alarme: list[str] = Field(default_factory=list)
    doencas_previas: list[str] = Field(default_factory=list)
    alergias: list[str] = Field(default_factory=list)
    medicamentos_em_uso: list[str] = Field(default_factory=list)
    contexto_especial: list[str] = Field(default_factory=list)


class ConfiancaSchema(BaseModel):
    score: float | None = None
    classificacao: str | None = None
    motivo: str | None = None

    @field_validator("score")
    @classmethod
    def score_entre_zero_e_um(cls, value: float | None) -> float | None:
        if value is None:
            return value
        return max(0.0, min(1.0, value))


class RevisaoSchema(BaseModel):
    aprovado: bool = True
    alertas: list[str] = Field(default_factory=list)
    human_in_the_loop: bool = True


class RelatorioSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    paciente: PacienteSchema = Field(default_factory=PacienteSchema)
    sintomas_principais: list[str] = Field(default_factory=list)
    possiveis_causas: list[str] = Field(default_factory=list)
    nivel_urgencia: NivelUrgencia = "BAIXO"
    especialidade_sugerida: str | None = "Clínico Geral"
    recomendacoes: list[str] = Field(default_factory=list)
    observacoes_importantes: str | None = ""
    confianca: ConfiancaSchema = Field(default_factory=ConfiancaSchema)
    revisao: RevisaoSchema = Field(default_factory=RevisaoSchema)

    @field_validator("nivel_urgencia", mode="before")
    @classmethod
    def normalizar_urgencia(cls, value: Any) -> str:
        if not value:
            return "BAIXO"
        normalized = str(value).strip().upper()
        if normalized == "CRÍTICO":
            return "CRITICO"
        if normalized not in {"BAIXO", "MODERADO", "ALTO", "CRITICO"}:
            return "BAIXO"
        return normalized


def validar_relatorio(relatorio: dict[str, Any]) -> RelatorioSchema:
    return RelatorioSchema.model_validate(relatorio)
