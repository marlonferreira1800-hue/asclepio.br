# Guia de Deploy - Asclépio 🚀

Este documento fornece as instruções para hospedar o **Asclépio** em ambientes de produção e nuvem.

---

## 🌐 Deploy no Netlify (Serverless)

O Asclépio possui suporte nativo para o **Netlify** através do [`netlify.toml`](netlify.toml) e funções serverless em `netlify/functions/`:

- **Site Oficial Netlify:** [https://asclepio-br.netlify.app](https://asclepio-br.netlify.app)
- **Publish Directory:** `frontend`
- **Functions Directory:** `netlify/functions`
- **Rotas API Serverless:** `/api/status`, `/api/atendimentos`, `/api/atendimento`

### Publicando no Netlify pelo CLI ou GitHub:

1. Conecte o repositório `asclepio.br` no painel do [Netlify](https://app.netlify.com/).
2. O Netlify detectará automaticamente o arquivo `netlify.toml`.
3. (Opcional) Em **Site configuration > Environment variables**, adicione `NVIDIA_API_KEY` ou `OPENAI_API_KEY` para enriquecimento por LLM.
4. Clique em **Deploy**.

---

## ☁️ Deploy no Render (Recomendado para Python Backend Completo)

O repositório já inclui o arquivo [`render.yaml`](render.yaml) para provisionamento com IaC (Infrastructure as Code).

### Passo a Passo

1. Faça login no [Render Dashboard](https://dashboard.render.com/).
2. Clique em **New +** e selecione **Web Service**.
3. Conecte sua conta do GitHub e selecione o repositório `asclepio.br`.
4. Defina as configurações:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python site_server.py`
5. Em **Environment Variables**, adicione obrigatoriamente:
   - `NVIDIA_API_KEY`: Sua chave de API da NVIDIA NIM (ou `OPENAI_API_KEY`).
   - `NVIDIA_MODEL`: `meta/llama-3.3-70b-instruct` (opcional, padrão).
   - `ASCLEPIO_DB_PATH`: `/tmp/asclepio.db` (para armazenamento em disco de teste).
6. Clique em **Create Web Service**.

> **Health Check:** O Render utilizará o endpoint `/healthz` para checar a saúde do container.

---

## 🚂 Deploy no Railway

1. Acesse o [Railway](https://railway.app/) e clique em **New Project** -> **Deploy from GitHub repo**.
2. Selecione o repositório `asclepio.br`.
3. Configure as variáveis de ambiente em **Variables**:
   - `NVIDIA_API_KEY`: sua chave de API.
   - `PORT`: O Railway atribui essa variável automaticamente e o servidor escutará na porta correta.
4. O Railway usará o `Procfile` ou `python site_server.py` automaticamente.

---

## 🐳 Execução com Docker (Opcional)

Se preferir rodar em contêineres locais ou qualquer nuvem (AWS ECS, GCP Cloud Run, Azure App Service):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8001

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["python", "site_server.py"]
```

Comandos para build e execução:

```bash
docker build -t asclepio .
docker run -d -p 8001:8001 --env-file .env asclepio
```

---

## 💾 Persistência de Dados em Produção

- Por padrão, o banco SQLite local fica em `data/asclepio.db`.
- Em instâncias *stateless* gratuitas (como instâncias efêmeras do Render sem disco persistente acoplado), dados em `/tmp` podem ser reiniciados.
- Para produção médica crítica, recomenda-se configurar um disco persistente acoplado (Render Disk) ou conectar a um banco relacional gerenciado (PostgreSQL / Supabase / Neon).

---

## ⚕️ Isenção de Responsabilidade

O Asclépio é um sistema orientativo experimental. Não utilize para atendimento de urgência ou tomada de decisão diagnóstica definitiva sem validação humana profissional.
