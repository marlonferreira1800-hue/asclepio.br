# Frontend do Asclepio

Esta pasta contem uma tela web separada do projeto terminal.

## Instalar dependencias

Execute a partir da pasta principal do Asclepio:

```powershell
.\.venv\Scripts\python.exe -m pip install -r frontend\requirements.txt
```

## Rodar

```powershell
cd C:\Users\Marlo\Desktop\asclepio
.\asclepio_frontend.bat
```

Depois abra:

```text
http://127.0.0.1:8000
```

O terminal continua funcionando normalmente com:

```powershell
.\asclepio.bat
```

## O que a tela faz

- Envia uma nova triagem para o backend Python.
- Exibe a triagem em formato de chat, com dados extras recolhidos em uma area opcional.
- Mostra urgencia, especialidade, sintomas, possiveis causas e recomendacoes.
- Salva o atendimento no SQLite usado pelo Asclepio.
- Mostra a aba `Historico` com os atendimentos ja gravados.
- Usa uma tela inicial escura, limpa e orientada a um agente de IA clinico local.
- Deixa claro que o Asclepio e um agente Python de terminal com uma interface web por cima.
- Usa Inter via Google Fonts e Bootstrap Icons via CDN para melhorar o acabamento visual.
- O texto visual enfatiza que o Asclepio e um agente de IA com pipeline clinico.

## Estrutura

```text
frontend/
  server.py              Rotas FastAPI
  services.py            Fluxo do atendimento web
  schemas.py             Validacao da entrada da API
  static/
    assets/              Imagens
      asclepio-mascot.png Mascote visual do Asclepio
    css/                 CSS separado por responsabilidade
    js/                  JavaScript em modulos
```

O servidor tambem aplica compressao GZip e cache simples para arquivos estaticos.
