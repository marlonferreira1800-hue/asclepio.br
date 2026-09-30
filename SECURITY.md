# Política de Segurança e Divulgação Responsável 🛡️

## ⚕️ Isenção de Responsabilidade Médica e de Uso

1. **Finalidade Educacional e Orientativa:**
   - O **Asclépio** é um sistema demonstrativo de IA voltado para triagem médica orientativa preliminar.
   - **NÃO é um dispositivo médico regulamentado** e não fornece diagnósticos nem prescreve medicamentos.
   - Em qualquer situação de urgência ou emergência, os usuários devem acionar imediatamente os serviços de emergência (no Brasil: SAMU 192 ou Bombeiros 193).

2. **Privacidade do Paciente:**
   - Por padrão, a aplicação armazena dados em banco SQLite local (`data/asclepio.db`).
   - Não recomendamos expor este serviço publicamente sem camadas adequadas de autenticação, criptografia (HTTPS/TLS) e conformidade com a LGPD (Lei Geral de Proteção de Dados) e HIPAA.

---

## 🔒 Reportando Vulnerabilidades de Segurança

Levamos a segurança do Asclépio muito a sério. Se você descobrir uma vulnerabilidade de segurança, siga as seguintes diretrizes:

1. **NÃO crie uma Issue pública** para reportar vulnerabilidades de segurança ou vazamento de chaves.
2. Envie um e-mail confidencial detalhando a vulnerabilidade para os mantenedores do projeto ou utilize o canal de segurança privado do GitHub (**Security Advisory**).
3. Inclua informações detalhadas:
   - Passos para reproduzir o problema;
   - Possível impacto ou vetor de ataque;
   - Correção sugerida, caso possua.

Responderemos em até 48 horas úteis com um plano de mitigação e agradecimentos pela divulgação responsável.
