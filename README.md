# 🛡️ CyberGuard Professional v2.0

## 📌 Plataforma de Treinamento em Segurança Cibernética com IA

Uma plataforma completa de e-learning em segurança cibernética, integrada com **Amazon AWS** (DynamoDB, Bedrock, CloudWatch) e **Streamlit**.

**Versão:** 2.0 (Melhorada com Analytics, Certificados, Gamificação e Controle de Acesso)

🌐 **Demo Online:** [cyberguard-professional.streamlit.app](https://cyberguard-professional.streamlit.app)

---

## ✨ Principais Melhorias v2.0

### 🎯 Novas Funcionalidades
- ✅ **Dashboard Completo** com métricas de desempenho
- ✅ **Sistema de Certificados** automático (80%+ de acerto)
- ✅ **Gamificação** com badges e pontos
- ✅ **Autenticação Robusta** preparada para Cognito
- ✅ **Relatórios e Exportação** (CSV, JSON)
- ✅ **Logging Centralizado** com CloudWatch
- ✅ **Controle de Acesso** por roles (Admin, Instrutor, Aluno)
- ✅ **Testes Unitários** com pytest
- ✅ **Arquitetura Modularizada** e escalável
- ✅ **Embaralhamento de Alternativas** para evitar decoração
- ✅ **24 Questões** (6 por categoria) com feedback IA personalizado

### 🏗️ Arquitetura
```
CyberGuard/
├── app_v2.py              # Aplicação principal (nova versão)
├── modules/               # Módulos principais
│   ├── auth.py            # Autenticação e sessões
│   ├── questions.py       # Gerenciamento de questões
│   ├── progress.py        # Rastreamento de progresso
│   ├── ai.py              # Feedback e geração com IA
│   ├── gamification.py    # Certificados e badges
│   └── reports.py         # Relatórios e exportação
├── utils/                 # Utilitários
│   ├── aws_client.py      # Cliente AWS centralizado
│   └── logger.py          # Logging com CloudWatch
├── tests/                 # Testes unitários
│   ├── test_questions.py
│   ├── test_auth.py
│   └── test_progress.py
└── setup_v2.py            # Setup melhorado
```

---

## 🚀 SETUP (4 PASSOS)

### 1️⃣ Clonar/Preparar Ambiente

```bash
cd /home/jhowmagnum/Documents/TCC\ -\ IA\ AWS/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Configurar AWS e Políticas IAM

**Console AWS → IAM → Policies → Editar CyberGuardPolicy**

Cole o conteúdo de `iam-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:*",
        "bedrock:InvokeModel",
        "logs:*",
        "s3:*",
        "cognito-idp:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3️⃣ Configurar Variáveis de Ambiente

```bash
cp .env.example .env
# Editar .env com suas configurações
```

### 4️⃣ Gerar Questões e Estrutura do Banco

```bash
python3 setup_v2.py
```

Isso cria:
- ✅ Tabela `cyberguard-questions` (questões)
- ✅ Tabela `cyberguard-progress` (progresso dos usuários)
- ✅ Tabela `cyberguard-certificates` (certificados)
- ✅ Tabela `cyberguard-badges` (gamificação)
- ✅ **16 questões geradas com IA** (4 categorias × 2 dificuldades × 2 questões)

### 5️⃣ Executar a Aplicação

```bash
streamlit run app_v2.py
```

Acesse: **http://localhost:8501**

---

## 📚 Como Usar

### 👨‍🎓 Para Alunos

1. **Login/Registro** - Crie sua conta
2. **Escolher Categoria** - Selecione o tópico (Phishing, Senhas, Engenharia Social, Malware)
3. **Treinar** - Responda questões de múltipla escolha
4. **Receber Feedback** - IA analisa e explica cada resposta
5. **Ver Análise** - Dashboard com estatísticas pessoais
6. **Gerar Certificado** - Qualifique-se com 80%+ de acerto
7. **Desbloquear Badges** - Ganhe reconhecimento por achievements
8. **Exportar Dados** - Download CSV/JSON de seu progresso

### 👨‍🏫 Para Instrutores

1. **Dashboard de Turma** - Ver desempenho geral dos alunos
2. **Relatórios Detalhados** - Análise por categoria e aluno
3. **Gerenciar Questões** - Regenerar, deletar ou adicionar
4. **Gerar Novos Conjuntos** - Criar questões com IA

### 🔐 Para Administradores

1. **Painel de Controle** - Gerenciar toda plataforma
2. **Auditoria** - Logs de todas as ações (CloudWatch)
3. **Configurações** - Sistema e integrações
4. **Backups e Dados** - Exportar/importar dados

---

## 🤖 Funcionalidades de IA (Amazon Bedrock)

### Geração de Questões
```python
from modules.ai import AIQuestionGenerator

generator = AIQuestionGenerator()
question = generator.generate_question(
    category='phishing',
    difficulty='medium'
)
```

Retorna:
```json
{
  "question": "Como identificar um email de phishing?",
  "options": ["A", "B", "C", "D"],
  "correctAnswer": 1,
  "explanation": "...",
  "why_wrong": {"0": "...", "2": "...", "3": "..."}
}
```

### Feedback Inteligente
- Análise contextual de respostas erradas
- Explicações educativas personalizadas
- Recomendações de estudo baseadas em performance
- Suporte completo em português brasileiro

---

## 📊 Análise e Relatórios

### Métricas Disponíveis
- 📈 Taxa de Acerto (por categoria e geral)
- 📊 Sequência de Acertos (streak)
- 📅 Atividade Recente
- 🏆 Ranking de Usuários
- ⏱️ Tempo Médio por Questão

### Exportação de Dados
```python
from modules.reports import ReportGenerator

reporter = ReportGenerator()

# CSV
csv = reporter.generate_user_report_csv(user_id)

# JSON
json = reporter.export_to_json(user_id)

# Relatório Resumido
summary = reporter.generate_summary_report(user_id)
```

---

## 🏆 Sistema de Gamificação

### Badges Disponíveis
| Badge | Ícone | Requisito |
|-------|-------|-----------|
| Especialista | 🏆 | 80% de acerto |
| Perfeição | 👑 | 100% de acerto |
| Sequência Vitoriosa | 🔥 | 5 acertos seguidos |
| Super Sequência | ⚡ | 10 acertos seguidos |
| Profissional Completo | 🛡️ | Treinar todas categorias |
| Campeão | 🥇 | Top 3 do ranking |
| Dedicado | 💪 | 30+ questões |

### Certificados
- Gerado automaticamente após atingir 80% em qualquer categoria
- PDF com ID único para validação
- Armazenado no S3
- Válido por 1 ano

---

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
pytest tests/

# Com cobertura
pytest --cov=modules tests/

# Teste específico
pytest tests/test_questions.py::TestQuestionManager::test_create_question
```

### Estrutura de Testes
```
tests/
├── test_auth.py          # Autenticação e sessões
├── test_questions.py     # Gerenciamento de questões
└── test_progress.py      # Progresso e estatísticas
```

---

## 📋 Logging com CloudWatch

### Eventos Registrados
- ✅ Login/Logout
- ✅ Início/Fim de Treinamento
- ✅ Submissão de Respostas
- ✅ Geração de Certificados
- ✅ Erros e Exceções

### Acesso aos Logs

```bash
# Via AWS CLI
aws logs tail /cyberguard/app --follow

# Ou no Console AWS → CloudWatch → Log Groups
```

---

## 🔐 Controle de Acesso

### Roles e Permissões

| Recurso | Student | Instructor | Admin |
|---------|---------|-----------|-------|
| Treinar | ✅ | ✅ | ✅ |
| Ver Progresso | ✅ Pessoal | ✅ Turma | ✅ Todos |
| Gerar Certificado | ✅ | ✅ | ✅ |
| Gerenciar Questões | ❌ | ✅ | ✅ |
| Ver Auditoria | ❌ | ❌ | ✅ |
| Admin Panel | ❌ | ❌ | ✅ |

---

## 📁 Estrutura de Dados

### Tabela: cyberguard-questions
```
{
  questionId: string (UUID),
  question: string,
  options: array[4],
  correctAnswer: number,
  explanation: string,
  category: string (phishing|passwords|social_engineering|malware),
  difficulty: string (easy|medium|hard),
  why_wrong: object,
  created_at: timestamp
}
```

### Tabela: cyberguard-progress
```
{
  userId: string (email),
  timestamp: number,
  questionId: string,
  correct: boolean,
  category: string,
  time_spent: number (segundos)
}
```

### Tabela: cyberguard-certificates
```
{
  certificateId: string (UUID),
  userId: string,
  category: string,
  accuracy: number,
  issued_at: timestamp,
  valid_until: timestamp
}
```

### Tabela: cyberguard-badges
```
{
  userId: string,
  badgeId: string,
  unlockedAt: timestamp
}
```

---

## 🐛 Troubleshooting

### Erro: "AWS Service Not Available"
```
✅ Verificar credenciais AWS
✅ Verificar permissões IAM
✅ Verificar região (us-east-1)
```

### Erro: "Failed to Generate Question"
```
✅ Verificar se Amazon Bedrock está ativado
✅ Verificar limite de chamadas da API
✅ Aguarde alguns segundos e tente novamente
```

### Sem Dados no Dashboard
```
✅ Complete pelo menos um treinamento
✅ Aguarde alguns segundos para o banco atualizar
✅ Recarregue a página (F5)
```

---

## 📈 Métricas de Desempenho

### DynamoDB
- Read Capacity: 5 unidades
- Write Capacity: 5 unidades
- GSI para otimizar queries por categoria

### Bedrock
- Modelo: `amazon.nova-micro-v1:0`
- Max tokens: 800 (feedback), 500 (questões)
- Temperature: 0.7-0.9

---

## 🔄 Atualizações Futuras

- [ ] Integração completa com Cognito (SSO)
- [ ] Sistema de fórum comunitário
- [ ] Recomendações personalizadas com ML
- [ ] Certificação com blockchain
- [ ] Aplicativo mobile (React Native)
- [ ] Proctoring automático para provas
- [ ] Integração com LMS (Canvas, Moodle)

---

## 📞 Suporte

**Desenvolvido para:** Projeto TCC - Escola da Nuvem
**Versão:** 2.0
**Data:** Janeiro/2026

---

## 📄 Licença

Este projeto é fornecido como está, para fins educacionais.

---

## 👥 Equipe

Grupo 02 - Escola da Nuvem
CyberGuard Professional Training Platform

### Avaliação (Bedrock):
- Analisa resposta do usuário
- Gera feedback personalizado
- Sugere materiais de estudo

---

## 📁 ARQUIVOS

- `setup_complete.py` - Setup completo com IA
- `app.py` - Aplicação Streamlit
- `iam-policy.json` - Política IAM atualizada
- `README.md` - Este arquivo

---

## 💰 CUSTO

- Geração: ~$0.02 (8 questões)
- Avaliação: ~$0.01 por 10 respostas
- **Total:** ~$0.03 para uso completo

---

## ✅ CHECKLIST

- [ ] Política IAM atualizada (com DeleteItem)
- [ ] Executou `python3 setup_complete.py`
- [ ] Aguardou geração das 8 questões
- [ ] Executou `streamlit run app.py`

---

**Status:** ✅ IA GERA E AVALIA TUDO!
