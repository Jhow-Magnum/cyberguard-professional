# 🛡️ CyberGuard Professional v2.0

## 📌 Plataforma de Treinamento em Segurança Cibernética com IA

Plataforma completa de e-learning em segurança cibernética integrada com **Amazon AWS** (DynamoDB, Bedrock, CloudWatch) e **Streamlit**.

**Versão:** 2.0 | **Projeto:** TCC Escola da Nuvem - Grupo 02

🌐 **Demo:** [cyberguard-professional.streamlit.app](https://cyberguard-professional.streamlit.app)

---

## ✨ Funcionalidades

- 🎯 **Dashboard Completo** com métricas de desempenho
- 🏆 **Sistema de Certificados** automático (80%+ acerto)
- 🎮 **Gamificação** com badges e pontos
- 🔐 **Autenticação** preparada para Cognito
- 📊 **Relatórios** CSV/JSON exportáveis
- 📋 **Logging** centralizado CloudWatch
- 👥 **Controle de Acesso** por roles
- 🧪 **Testes Unitários** com pytest
- 🔀 **Embaralhamento** de alternativas
- 🤖 **24 Questões** com feedback IA personalizado

---

## 🏗️ Arquitetura

```
CyberGuard/
├── app_v2.py              # Aplicação principal
├── modules/               # Módulos core
│   ├── ai.py              # Feedback IA (Bedrock)
│   ├── auth.py            # Autenticação
│   ├── questions.py       # Gerenciamento questões
│   ├── progress.py        # Progresso usuários
│   ├── gamification.py    # Certificados/badges
│   └── reports.py         # Relatórios
├── utils/                 # Utilitários
│   ├── aws_client.py      # Cliente AWS
│   └── logger.py          # Logging
├── tests/                 # Testes unitários
└── setup_v2.py            # Setup inicial
```

---

## 🚀 Setup Rápido

### 1. Ambiente
```bash
git clone https://github.com/Jhow-Magnum/cyberguard-professional.git
cd cyberguard-professional
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. AWS IAM
Crie política com conteúdo de `iam-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["dynamodb:*", "bedrock:InvokeModel", "logs:*"],
    "Resource": "*"
  }]
}
```

### 3. Configuração
```bash
cp .env.example .env
# Editar .env com credenciais AWS
```

### 4. Inicialização
```bash
python3 setup_v2.py  # Cria tabelas + 24 questões
streamlit run app_v2.py  # Inicia aplicação
```

**Acesse:** http://localhost:8501

---

## 🎯 Como Usar

### Alunos
1. **Login** → Digite email
2. **Treinar** → Escolha categoria (Phishing, Senhas, Eng. Social, Malware)
3. **Responder** → Complete questões
4. **Feedback** → Receba análise IA personalizada
5. **Certificado** → Obtenha com 80%+ acerto

### Instrutores
- Dashboard de turma
- Relatórios detalhados
- Gerenciamento de questões

### Administradores
- Painel de controle completo
- Auditoria e logs
- Configurações do sistema

---

## 🤖 IA Amazon Bedrock

**Feedback Inteligente:**
- Análise contextual de respostas
- Explicações educativas personalizadas
- Fallback automático quando tokens esgotados
- Suporte completo português brasileiro

**Geração de Questões:**
```python
from modules.ai import AIQuestionGenerator
generator = AIQuestionGenerator()
question = generator.generate_question('phishing', 'medium')
```

---

## 📊 Dados e Métricas

**Tabelas DynamoDB:**
- `cyberguard-questions` - Questões e respostas
- `cyberguard-progress` - Progresso usuários
- `cyberguard-certificates` - Certificados emitidos
- `cyberguard-badges` - Sistema gamificação

**Métricas Disponíveis:**
- Taxa de acerto por categoria
- Sequência de acertos (streak)
- Ranking de usuários
- Tempo médio por questão
- Atividade recente

---

## 🏆 Gamificação

**Badges:**
- 🏆 Especialista (80% acerto)
- 👑 Perfeição (100% acerto)
- 🔥 Sequência Vitoriosa (5 seguidos)
- ⚡ Super Sequência (10 seguidos)
- 🛡️ Profissional Completo (todas categorias)

**Certificados:**
- Geração automática 80%+ acerto
- PDF com ID único
- Válido por 1 ano

---

## 🧪 Testes

```bash
pytest tests/                    # Todos os testes
pytest --cov=modules tests/      # Com cobertura
```

---

## 🔧 Troubleshooting

**AWS Service Not Available:**
- Verificar credenciais e região (us-east-1)
- Confirmar permissões IAM

**Bedrock Throttling:**
- Sistema usa fallback automático
- Tokens resetam diariamente

**Sem Dados Dashboard:**
- Complete pelo menos um treinamento
- Aguarde sincronização DynamoDB

---

## 📈 Performance

**DynamoDB:** 5 unidades read/write
**Bedrock:** amazon.nova-micro-v1:0, 200-800 tokens
**Custo Estimado:** ~$0.03 uso completo

---

## 📞 Suporte

**Projeto:** TCC Escola da Nuvem - Grupo 02
**Versão:** 2.0
**Licença:** Educacional