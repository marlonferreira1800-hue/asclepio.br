# Guia de Contribuição - Asclépio ⚕️

Agradecemos imensamente o seu interesse em contribuir para o **Asclépio**! Este projeto é um ecossistema de agentes inteligentes focado em triagem clínica orientativa preliminar.

---

## 🧭 Princípios Fundamentais

1. **Segurança Clínica em Primeiro Lugar:**
   - O Asclépio é estritamente **orientativo**.
   - Nunca forneça diagnósticos definitivos, nem incentive prescrições ou automedicação.
   - Sinais de alarme críticos (como dor torácica, dispneia súbita, perda de consciência) devem sempre disparar encaminhamento imediato a serviços de urgência (SAMU 192).

2. **Privacidade e Dados Sensíveis:**
   - Não armazene dados pessoais identificáveis (LGPD/HIPAA) em logs ou repositórios públicos.
   - O arquivo `.env` jamais deve ser comitado.

---

## 🛠️ Como Contribuir

### 1. Clonar e Configurar o Ambiente

```bash
# Clone o seu fork do repositório
git clone https://github.com/SEU_USUARIO/asclepio.br.git
cd asclepio.br

# Crie e ative um ambiente virtual
python -m venv .venv

# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Configurar o `.env`

Copie o modelo de ambiente:

```bash
cp .env.example .env
```

Edite o `.env` e configure sua chave da NVIDIA NIM ou OpenAI.

### 3. Criar uma Branch

Adote uma nomenclatura semântica para branches:

- `feat/nome-da-funcionalidade`
- `fix/correcao-do-problema`
- `docs/melhoria-na-documentacao`
- `test/adicao-de-testes`

```bash
git checkout -b feat/melhoria-fluxo-triagem
```

### 4. Executar os Testes

Antes de submeter sua contribuição, garanta que todos os testes passem:

```bash
python tests/run_tests.py
# ou se tiver pytest instalado:
pytest -v tests/
```

### 5. Abrir um Pull Request

1. Faça o commit das suas alterações com mensagens claras e semânticas (`feat: ...`, `fix: ...`, `docs: ...`).
2. Faça push para a sua branch no GitHub.
3. Abra um Pull Request detalhado preenchendo o modelo fornecido.

---

## 📜 Código de Conduta

Ao participar deste projeto, você concorda em seguir o nosso [Código de Conduta](CODE_OF_CONDUCT.md).
