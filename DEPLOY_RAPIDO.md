# 🚀 Deploy Rápido - 3 Passos

## Pré-requisitos
- Conta no GitHub (criar em: https://github.com/signup)
- Git instalado

## Passo 1: Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. Nome do repositório: `cyberguard-professional`
3. Descrição: `Plataforma de Treinamento em Segurança Cibernética com IA - AWS + Streamlit`
4. Público
5. Clique em "Create repository"

## Passo 2: Fazer Upload do Código

Execute estes comandos no terminal:

```bash
cd "/home/jhowmagnum/Documents/TCC - IA AWS"

# Inicializar Git
git init
git add .
git commit -m "CyberGuard Professional v2.0 - Initial commit"

# Conectar ao GitHub (SUBSTITUA SEU_USUARIO pelo seu username do GitHub)
git remote add origin https://github.com/SEU_USUARIO/cyberguard-professional.git
git branch -M main
git push -u origin main
```

Quando pedir usuário e senha:
- Usuário: seu username do GitHub
- Senha: use um Personal Access Token (criar em: https://github.com/settings/tokens)

## Passo 3: Deploy no Streamlit Cloud

1. Acesse: https://share.streamlit.io
2. Clique em "Sign in with GitHub"
3. Autorize o Streamlit
4. Clique em "New app"
5. Selecione:
   - Repository: `cyberguard-professional`
   - Branch: `main`
   - Main file path: `app_v2.py`
6. Clique em "Advanced settings"
7. Cole no campo "Secrets":

```toml
AWS_ACCESS_KEY_ID = "AKIA..."
AWS_SECRET_ACCESS_KEY = "..."
AWS_DEFAULT_REGION = "us-east-1"
```

8. Clique em "Deploy!"

## ✅ Pronto!

Sua aplicação estará online em:
`https://SEU_USUARIO-cyberguard-professional.streamlit.app`

Compartilhe este link com quem quiser!

---

## 🔧 Atualizar Aplicação

Sempre que fizer mudanças:

```bash
git add .
git commit -m "Descrição da mudança"
git push
```

O Streamlit Cloud atualiza automaticamente!

---

## ❓ Problemas?

### Erro ao fazer push
- Verifique se criou o Personal Access Token
- Use o token como senha, não sua senha do GitHub

### App não inicia
- Verifique se os secrets AWS estão corretos
- Veja os logs no painel do Streamlit Cloud

### Limite do Bedrock
- Normal! Aguarde 24h para resetar
- App continua funcionando com feedback local
