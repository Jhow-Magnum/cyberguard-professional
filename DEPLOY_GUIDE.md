# 🚀 Guia de Deploy - CyberGuard Professional

## Opção 1: Streamlit Community Cloud (GRATUITO) ⭐

### Passo 1: Preparar Repositório Git

```bash
cd "/home/jhowmagnum/Documents/TCC - IA AWS"

# Criar .gitignore
cat > .gitignore << 'EOF'
venv/
__pycache__/
*.pyc
.env
*.log
.pytest_cache/
EOF

# Inicializar Git
git init
git add .
git commit -m "Initial commit - CyberGuard v2.0"
```

### Passo 2: Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. Nome: `cyberguard-professional`
3. Descrição: `Plataforma de Treinamento em Segurança Cibernética com IA`
4. Público ou Privado (sua escolha)
5. Criar repositório

```bash
# Conectar ao GitHub
git remote add origin https://github.com/SEU_USUARIO/cyberguard-professional.git
git branch -M main
git push -u origin main
```

### Passo 3: Deploy no Streamlit Cloud

1. Acesse: https://share.streamlit.io
2. Faça login com GitHub
3. Clique em **"New app"**
4. Selecione:
   - Repository: `cyberguard-professional`
   - Branch: `main`
   - Main file: `app_v2.py`
5. Clique em **"Advanced settings"**
6. Adicione secrets:

```toml
# .streamlit/secrets.toml
AWS_ACCESS_KEY_ID = "AKIA..."
AWS_SECRET_ACCESS_KEY = "..."
AWS_DEFAULT_REGION = "us-east-1"
```

7. Clique em **"Deploy"**

**URL:** `https://seu-usuario-cyberguard-professional.streamlit.app`

---

## Opção 2: AWS EC2 (Controle Total)

### Passo 1: Criar Instância EC2

1. **AWS Console → EC2 → Launch Instance**
2. Configurações:
   - Nome: `cyberguard-server`
   - AMI: Ubuntu Server 22.04 LTS
   - Tipo: t2.micro (Free Tier)
   - Key pair: Criar nova ou usar existente
   - Security Group: Permitir portas 22 (SSH) e 8501 (Streamlit)

### Passo 2: Conectar e Configurar

```bash
# Conectar via SSH
ssh -i sua-chave.pem ubuntu@SEU_IP_PUBLICO

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install python3-pip python3-venv git -y

# Clonar repositório
git clone https://github.com/SEU_USUARIO/cyberguard-professional.git
cd cyberguard-professional

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
nano .env
# Adicionar:
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...
# AWS_DEFAULT_REGION=us-east-1
```

### Passo 3: Executar com PM2 (Manter rodando)

```bash
# Instalar Node.js e PM2
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
sudo npm install -g pm2

# Criar script de inicialização
cat > start.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
streamlit run app_v2.py --server.port 8501 --server.address 0.0.0.0
EOF

chmod +x start.sh

# Iniciar com PM2
pm2 start start.sh --name cyberguard
pm2 save
pm2 startup
```

**Acessar:** `http://SEU_IP_PUBLICO:8501`

### Passo 4: Configurar Domínio (Opcional)

1. Comprar domínio (ex: cyberguard.com.br)
2. Configurar DNS apontando para IP da EC2
3. Instalar Nginx como proxy reverso:

```bash
sudo apt install nginx -y

# Configurar Nginx
sudo nano /etc/nginx/sites-available/cyberguard

# Adicionar:
server {
    listen 80;
    server_name cyberguard.com.br;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}

# Ativar configuração
sudo ln -s /etc/nginx/sites-available/cyberguard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Instalar SSL (HTTPS)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d cyberguard.com.br
```

**Acessar:** `https://cyberguard.com.br`

---

## Opção 3: AWS Elastic Beanstalk (Escalável)

### Passo 1: Preparar Aplicação

```bash
# Criar Procfile
echo "web: streamlit run app_v2.py --server.port=8501 --server.address=0.0.0.0" > Procfile

# Criar .ebextensions/python.config
mkdir .ebextensions
cat > .ebextensions/python.config << 'EOF'
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app_v2.py
  aws:elasticbeanstalk:application:environment:
    STREAMLIT_SERVER_PORT: 8501
EOF
```

### Passo 2: Deploy

```bash
# Instalar EB CLI
pip install awsebcli

# Inicializar
eb init -p python-3.9 cyberguard --region us-east-1

# Criar ambiente
eb create cyberguard-env

# Deploy
eb deploy

# Abrir no navegador
eb open
```

---

## 🔒 Segurança

### Configurar Autenticação (Opcional)

Para restringir acesso, adicione autenticação:

```python
# No app_v2.py, adicionar no início:
import streamlit_authenticator as stauth

# Configurar usuários permitidos
names = ['Admin', 'Instrutor']
usernames = ['admin', 'instrutor']
passwords = ['senha123', 'senha456']  # Use hash em produção

authenticator = stauth.Authenticate(
    names, usernames, passwords,
    'cyberguard', 'abcdef', cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if not authentication_status:
    st.stop()
```

### Variáveis de Ambiente Seguras

Nunca commite `.env` no Git! Use:
- Streamlit Cloud: Secrets
- EC2: AWS Systems Manager Parameter Store
- Elastic Beanstalk: Environment Properties

---

## 📊 Monitoramento

### CloudWatch (AWS)

```bash
# Instalar CloudWatch Agent na EC2
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

### Logs

```bash
# Ver logs em tempo real
pm2 logs cyberguard

# Logs do Streamlit
tail -f ~/.streamlit/logs/streamlit.log
```

---

## 💰 Custos Estimados

| Opção | Custo Mensal | Free Tier |
|-------|--------------|-----------|
| Streamlit Cloud | $0 | ✅ Sim |
| EC2 t2.micro | $0-10 | ✅ 12 meses |
| Elastic Beanstalk | $10-30 | ✅ Parcial |
| DynamoDB | $0-5 | ✅ 25GB |
| Bedrock | $0-10 | ✅ Limitado |

**Total:** $0-20/mês (com Free Tier)

---

## 🎯 Recomendação Final

**Para TCC/Apresentação:** Use **Streamlit Community Cloud**
- ✅ Gratuito
- ✅ Rápido (5 minutos)
- ✅ Profissional
- ✅ HTTPS automático
- ✅ Fácil de compartilhar

**Para Produção:** Use **AWS EC2 + Nginx + SSL**
- ✅ Controle total
- ✅ Escalável
- ✅ Domínio próprio
- ✅ Seguro

---

## 📞 Suporte

Dúvidas? Consulte:
- Streamlit Docs: https://docs.streamlit.io/streamlit-community-cloud
- AWS EC2: https://docs.aws.amazon.com/ec2/
- GitHub: https://docs.github.com/
