# Asclepio

Asclepio e um agente de triagem medica orientativa com interface web local.
Ele conversa com o paciente, organiza sintomas, gera hipoteses orientativas e apresenta recomendacoes seguras.

> Aviso: o Asclepio nao substitui consulta medica presencial e nao deve ser usado para diagnostico definitivo.

## Requisitos

- Python 3.10+
- Navegador moderno

## Como rodar o site local

No PowerShell, entre na pasta do projeto:

```powershell
cd C:\Users\Marlo\Desktop\asclepio
```

Use o atalho:

```powershell
.\asclepio_frontend.bat
```

Depois abra:

```text
http://127.0.0.1:8001
```

Tambem e possivel rodar diretamente:

```powershell
python site_server.py 8001
```

## Como rodar no terminal

O agente original de terminal continua disponivel:

```powershell
.\asclepio.bat
```

Relatorios salvos ficam na pasta `relatorios/`.

## Deploy online

O projeto esta preparado para hospedagens Python como Render ou Railway.

Arquivos incluidos para deploy:

- `site_server.py`: servidor web leve, sem framework externo.
- `Procfile`: comando web para plataformas que usam Procfile.
- `render.yaml`: configuracao pronta para Render.
- `runtime.txt`: versao sugerida do Python.
- `.gitignore`: evita publicar `.env`, banco local, ZIPs, logs e ambiente virtual.

O servidor usa a variavel `PORT` automaticamente quando ela existir.

Comando de start:

```bash
python site_server.py
```

Health check:

```text
/healthz
```

Veja o passo a passo em `DEPLOY.md`.

## Banco de dados

Localmente, o SQLite fica em:

```text
data/asclepio.db
```

Em deploy de teste, o `render.yaml` usa:

```text
/tmp/asclepio.db
```

Isso e suficiente para demonstracao, mas pode perder dados quando a instancia reiniciar. Para uso real, prefira um banco persistente como PostgreSQL, Supabase ou Neon.

## Fluxo do agente

```text
Triagem -> Extracao Clinica -> Seguranca Medica -> Pre-Diagnostico -> Orientacao -> Revisao -> Relatorio
```
