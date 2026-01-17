"""
Script de setup melhorado com suporte a tabelas adicionais
Inclui fallback para questões pré-geradas quando Bedrock não está disponível
"""

import boto3
import json
import uuid
import time
import logging
import sys
from decimal import Decimal
from datetime import datetime
from pregenerated_questions import PREGERATED_QUESTIONS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("🚀 CyberGuard v2.0 - Setup Completo com IA e Analytics")
print("=" * 70)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
client = boto3.client('dynamodb', region_name='us-east-1')

# 1. DELETAR TABELAS ANTIGAS
print("\n🗑️  Deletando tabelas antigas...")
for table_name in [
    'cyberguard-questions',
    'cyberguard-progress',
    'cyberguard-certificates',
    'cyberguard-badges'
]:
    try:
        table = dynamodb.Table(table_name)
        table.delete()
        print(f"   ✅ Deletada: {table_name}")
        print(f"   ⏳ Aguardando exclusão...")
        waiter = client.get_waiter('table_not_exists')
        waiter.wait(TableName=table_name, WaiterConfig={'Delay': 5, 'MaxAttempts': 30})
    except client.exceptions.ResourceNotFoundException:
        print(f"   ℹ️  {table_name} não existe")
    except Exception as e:
        print(f"   ⚠️  Erro: {e}")

# 2. CRIAR TABELAS NOVAS
print("\n📦 Criando tabelas...")

# Tabela de questões
print("   Criando: cyberguard-questions")
table = dynamodb.create_table(
    TableName='cyberguard-questions',
    KeySchema=[{'AttributeName': 'questionId', 'KeyType': 'HASH'}],
    AttributeDefinitions=[
        {'AttributeName': 'questionId', 'AttributeType': 'S'},
        {'AttributeName': 'category', 'AttributeType': 'S'}
    ],
    GlobalSecondaryIndexes=[{
        'IndexName': 'CategoryIndex',
        'KeySchema': [{'AttributeName': 'category', 'KeyType': 'HASH'}],
        'Projection': {'ProjectionType': 'ALL'},
        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 2}
    }],
    ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 2}
)

# Tabela de progresso
print("   Criando: cyberguard-progress")
table = dynamodb.create_table(
    TableName='cyberguard-progress',
    KeySchema=[
        {'AttributeName': 'userId', 'KeyType': 'HASH'},
        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'userId', 'AttributeType': 'S'},
        {'AttributeName': 'timestamp', 'AttributeType': 'N'}
    ],
    ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
)

# Tabela de certificados
print("   Criando: cyberguard-certificates")
table = dynamodb.create_table(
    TableName='cyberguard-certificates',
    KeySchema=[
        {'AttributeName': 'userId', 'KeyType': 'HASH'},
        {'AttributeName': 'certificateId', 'KeyType': 'RANGE'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'userId', 'AttributeType': 'S'},
        {'AttributeName': 'certificateId', 'AttributeType': 'S'}
    ],
    ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 2}
)

# Tabela de badges
print("   Criando: cyberguard-badges")
table = dynamodb.create_table(
    TableName='cyberguard-badges',
    KeySchema=[
        {'AttributeName': 'userId', 'KeyType': 'HASH'},
        {'AttributeName': 'badgeId', 'KeyType': 'RANGE'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'userId', 'AttributeType': 'S'},
        {'AttributeName': 'badgeId', 'AttributeType': 'S'}
    ],
    ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 2}
)

print("\n⏳ Aguardando tabelas ficarem ativas (30 segundos)...")
time.sleep(30)

# 3. GERAR QUESTÕES COM IA
print("\n🤖 Gerando questões com Amazon Bedrock IA...\n")

CATEGORIES = {
    'phishing': 'identificação de emails maliciosos e ataques de phishing',
    'passwords': 'criação e gerenciamento seguro de senhas',
    'social_engineering': 'táticas de manipulação e engenharia social',
    'malware': 'prevenção e detecção de malware'
}

DIFFICULTIES = ['easy', 'medium']

def generate_question_with_ai(category, difficulty, topic):
    """Gera questão com Bedrock"""
    prompt = f"""Crie uma questão de múltipla escolha sobre segurança cibernética.

Tópico: {topic}
Categoria: {category}
Dificuldade: {difficulty}

Retorne APENAS um JSON válido neste formato:
{{
  "question": "Pergunta clara em português (máximo 100 caracteres)",
  "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
  "correctAnswer": 1,
  "explanation": "Explicação de por que a resposta correta está certa (50 palavras máximo)",
  "why_wrong": {{
    "0": "Por que opção A está errada (25 palavras)",
    "2": "Por que opção C está errada (25 palavras)",
    "3": "Por que opção D está errada (25 palavras)"
  }}
}}

Crie apenas JSON válido, sem explicações adicionais."""
    
    try:
        response = bedrock.invoke_model(
            modelId='amazon.nova-micro-v1:0',
            body=json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"max_new_tokens": 500, "temperature": 0.9}
            })
        )
        
        result = json.loads(response['body'].read())
        response_text = result['output']['message']['content'][0]['text']
        
        # Tentar fazer parse do JSON
        try:
            question_data = json.loads(response_text)
            return question_data
        except json.JSONDecodeError:
            # Tentar extrair JSON da resposta
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                question_data = json.loads(json_match.group())
                return question_data
            return None
    except Exception as e:
        logger.error(f"Erro ao gerar questão: {e}")
        return None

# Gerar ou carregar questões
questions_table = dynamodb.Table('cyberguard-questions')
total_generated = 0

print("\n🤖 Processando questões...\n")

# Primeiro, tentar usar as questões pré-geradas (mais confiável)
print("📝 Usando questões pré-geradas como base...")

for question_data in PREGERATED_QUESTIONS:
    try:
        question_id = str(uuid.uuid4())
        item = {
            'questionId': question_id,
            'question': question_data.get('question', ''),
            'options': question_data.get('options', []),
            'correctAnswer': str(question_data.get('correctAnswer', 0)),
            'explanation': question_data.get('explanation', ''),
            'category': question_data.get('category', ''),
            'difficulty': question_data.get('difficulty', ''),
            'why_wrong': question_data.get('why_wrong', {}),
            'created_at': Decimal(str(datetime.now().timestamp()))
        }
        
        questions_table.put_item(Item=item)
        total_generated += 1
        print(f"   ✅ {question_data.get('category')} ({question_data.get('difficulty')}): {question_data.get('question')[:50]}...")
    except Exception as e:
        print(f"   ❌ Erro ao inserir questão: {e}")
        
    time.sleep(0.1)  # Pequeno delay

print(f"\n✅ Total de questões carregadas: {total_generated}")

# Tentar gerar mais questões com IA se disponível
print("\n🤖 Tentando gerar questões adicionais com Amazon Bedrock...\n")
bedrock_generated = 0
bedrock_failed = 0

for category, topic in CATEGORIES.items():
    print(f"📝 Gerando questões extras para: {category.upper()}")
    
    for difficulty in DIFFICULTIES:
        for i in range(1):  # Apenas 1 questão extra por dificuldade
            print(f"   Gerando {difficulty} #{i+1}...", end=" ", flush=True)
            
            try:
                question_data = generate_question_with_ai(category, difficulty, topic)
                
                if question_data:
                    question_id = str(uuid.uuid4())
                    item = {
                        'questionId': question_id,
                        'question': question_data.get('question', ''),
                        'options': question_data.get('options', []),
                        'correctAnswer': str(question_data.get('correctAnswer', 0)),
                        'explanation': question_data.get('explanation', ''),
                        'category': category,
                        'difficulty': difficulty,
                        'why_wrong': question_data.get('why_wrong', {}),
                        'created_at': Decimal(str(datetime.now().timestamp()))
                    }
                    
                    questions_table.put_item(Item=item)
                    print("✅")
                    bedrock_generated += 1
                else:
                    print("⏭️  (Skipped)")
                    bedrock_failed += 1
            except Exception as e:
                if "ThrottlingException" in str(e) or "Too many tokens" in str(e):
                    print("⚠️  (Bedrock limit reached)")
                else:
                    print(f"❌ ({str(e)[:30]}...)")
                bedrock_failed += 1
            
            if bedrock_failed >= 2:
                print("\n⚠️  Bedrock limit reached. Usando apenas questões pré-geradas.")
                break
    
    if bedrock_failed >= 2:
        break

print(f"\n✅ Total de questões carregadas: {total_generated}")
if bedrock_generated > 0:
    print(f"✅ Questões extras geradas com IA: {bedrock_generated}")
if bedrock_failed > 0:
    print(f"⚠️  Falhas na geração com IA: {bedrock_failed} (limite de Bedrock)")

print("\n" + "=" * 70)
print("🎉 Setup concluído com sucesso!")
print("=" * 70)

if total_generated == 0:
    print("\n❌ ERRO: Nenhuma questão foi carregada!")
    print("Verifique se pregenerated_questions.py está no diretório raiz.")
    sys.exit(1)

print(f"\n✅ Total de questões na base de dados: {total_generated + bedrock_generated}")
print("\n📚 Próximos passos:")
print("   1. Copie seu arquivo .env: cp .env.example .env")
print("   2. Configure as variáveis de ambiente")
print("   3. Execute a aplicação: streamlit run app_v2.py")
print("\n💡 Dica: Se precisar gerar mais questões com IA depois,")
print("   aguarde algumas horas e execute este script novamente.")
print("\n")
