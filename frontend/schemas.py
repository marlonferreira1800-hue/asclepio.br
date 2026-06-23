from pydantic import BaseModel, Field


class AtendimentoEntrada(BaseModel):
    nome: str | None = None
    idade: int | None = Field(default=None, ge=0, le=130)
    sexo: str | None = None
    cidade: str | None = None
    sintomas: str = Field(min_length=3, max_length=4000)
    duracao: str | None = None
    intensidade: int | None = Field(default=None, ge=0, le=10)
    sintomas_associados: str | None = None
    sinais_alarme: str | None = None
    doencas_previas: str | None = None
    alergias: str | None = None
    medicamentos_em_uso: str | None = None
    contexto_especial: str | None = None
    salvar_txt: bool = True
