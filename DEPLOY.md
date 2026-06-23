# Deploy do Asclepio

Este projeto esta pronto para rodar em hospedagens Python como Render ou Railway.

## Render

1. Envie o projeto para um repositorio Git.
2. No Render, crie um novo Web Service a partir desse repositorio.
3. O Render pode usar o arquivo `render.yaml` automaticamente.
4. O comando de start e:

```bash
python site_server.py
```

5. O health check fica em:

```text
/healthz
```

## Railway

Use o start command:

```bash
python site_server.py
```

O servidor usa a variavel `PORT` automaticamente quando ela existir.

## Banco de dados

Por padrao local, o SQLite fica em `data/asclepio.db`.

No deploy de teste, `render.yaml` usa `/tmp/asclepio.db`. Isso funciona para demonstracao, mas pode perder dados quando a instancia reinicia.

Para uso real, troque para um banco persistente como PostgreSQL, Supabase ou Neon.

## Arquivos que nao devem subir

O `.gitignore` ja ignora:

- `.env`
- `.venv/`
- `data/`
- `relatorios/`
- `logs/`
- `*.zip`
- caches Python

## Aviso medico

O Asclepio e orientativo. Ele nao substitui consulta medica, diagnostico profissional ou atendimento de emergencia.
