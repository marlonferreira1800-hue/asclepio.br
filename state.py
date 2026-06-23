from dataclasses import dataclass, field


@dataclass
class CaseState:
    paciente: dict = field(default_factory=dict)
    historico: list = field(default_factory=list)
    sinais_alarme: list = field(default_factory=list)
    dados_faltantes: list = field(default_factory=list)
    qualidade_dados: str = "baixa"

    @classmethod
    def from_triagem(cls, dados_paciente: dict, historico: list) -> "CaseState":
        obrigatorios = {
            "idade": "idade",
            "sexo": "sexo",
            "queixa_principal": "queixa principal",
            "duracao": "duração",
            "intensidade": "intensidade",
        }
        faltantes = [rotulo for campo, rotulo in obrigatorios.items() if not dados_paciente.get(campo)]
        sinais = dados_paciente.get("sinais_alarme") or []

        if len(faltantes) <= 1:
            qualidade = "alta"
        elif len(faltantes) <= 3:
            qualidade = "moderada"
        else:
            qualidade = "baixa"

        return cls(
            paciente=dict(dados_paciente),
            historico=list(historico),
            sinais_alarme=list(sinais),
            dados_faltantes=faltantes,
            qualidade_dados=qualidade,
        )

    def to_dict(self) -> dict:
        return {
            "paciente": self.paciente,
            "sinais_alarme": self.sinais_alarme,
            "dados_faltantes": self.dados_faltantes,
            "qualidade_dados": self.qualidade_dados,
            "sintomas_associados": self.paciente.get("sintomas_associados", []),
            "alergias": self.paciente.get("alergias", []),
            "medicamentos_em_uso": self.paciente.get("medicamentos_em_uso", []),
            "doencas_previas": self.paciente.get("doencas_previas", []),
            "contexto_especial": self.paciente.get("contexto_especial", []),
            "mensagens": len(self.historico),
        }

    def resumo_para_ia(self) -> str:
        linhas = ["ESTADO ESTRUTURADO DO CASO:"]
        for chave, valor in self.paciente.items():
            linhas.append(f"- {chave}: {valor}")
        linhas.append(f"- qualidade_dados: {self.qualidade_dados}")
        if self.dados_faltantes:
            linhas.append(f"- dados_faltantes: {', '.join(self.dados_faltantes)}")
        if self.sinais_alarme:
            linhas.append(f"- sinais_alarme: {', '.join(self.sinais_alarme)}")
        return "\n".join(linhas)
