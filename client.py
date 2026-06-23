from openai import OpenAI
from config import NVIDIA_API_KEY, NVIDIA_MODEL, NVIDIA_BASE_URL, console
import sys

# ──────────────────────────────────────────────────────────────
# CLIENTE NVIDIA NIM — Camada de comunicação com a API
# ──────────────────────────────────────────────────────────────
class NvidiaClient:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model

    def chamar(self, prompt_sistema: str, mensagem: str, historico: list | None = None) -> str:
        """
        Chama o modelo NVIDIA NIM com prompt de sistema, histórico e mensagem do usuário.
        Retorna o texto da resposta.
        """
        if historico is None:
            historico = []

        # Converte histórico para o formato da API de Chat da OpenAI/NVIDIA
        mensagens_api = [{"role": "system", "content": prompt_sistema}]
        
        for item in historico or []:
            role = item["role"]
            # O histórico interno usa 'model'; a API espera 'assistant'
            if role == "model":
                role = "assistant"
            mensagens_api.append({
                "role": role,
                "content": item["content"]
            })
            
        # Adiciona a mensagem atual
        mensagens_api.append({
            "role": "user",
            "content": mensagem
        })

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=mensagens_api,
                temperature=0.4,
                max_tokens=2048,
            )
        except Exception as e:
            status = getattr(e, "status_code", None)
            if status in {401, 403}:
                raise RuntimeError("A chave NVIDIA_API_KEY foi recusada. Confira o valor no arquivo .env.") from e
            if status == 429:
                raise RuntimeError("A API recusou por limite de uso. Tente novamente mais tarde.") from e
            if status and status >= 500:
                raise RuntimeError("A API da NVIDIA parece estar indisponivel no momento.") from e
            raise RuntimeError("Nao foi possivel falar com a API. Confira internet, chave e configuracao.") from e

        if not response.choices or not response.choices[0].message.content:
            raise RuntimeError("A API respondeu sem texto. Tente novamente.")

        return response.choices[0].message.content.strip()


# Instância global do cliente
try:
    client = NvidiaClient(NVIDIA_API_KEY, NVIDIA_BASE_URL, NVIDIA_MODEL)
except Exception as e:
    console.print(f"\n[red]❌ Erro ao inicializar o cliente NVIDIA: {e}[/]")
    sys.exit(1)

