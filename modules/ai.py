"""
Módulo de Feedback e Análise com IA Bedrock
"""
import json
import logging
from typing import Dict
from utils.aws_client import get_aws_client

logger = logging.getLogger(__name__)

class FeedbackGenerator:
    """Gera feedback inteligente com Amazon Bedrock"""
    
    def __init__(self):
        self.bedrock = get_aws_client().bedrock
    
    def generate_feedback(self, question: str, user_answer: str,
                         correct_answer: str, is_correct: bool,
                         category: str) -> str:
        """Gera feedback personalizado usando IA - ÚNICO E DETALHADO POR QUESTÃO"""
        try:
            if not self.bedrock:
                return self._get_default_feedback(is_correct, user_answer, correct_answer)
            
            # Prompt específico e único para cada questão
            status = "✅ CORRETA" if is_correct else "❌ INCORRETA"
            
            if is_correct:
                prompt = f"""Você é um instrutor especialista em segurança cibernética.

QUESTÃO: {question}
RESPOSTA DO ALUNO: {user_answer}
STATUS: ✅ CORRETA

Gere um feedback BREVE E ESPECÍFICO (máximo 150 palavras) que:
1. Parabenize a resposta correta
2. Explique POR QUE esta é a resposta correta
3. Cite o conceito de segurança envolvido
4. Recomende próximos passos ou aprofundamento

Use português brasileiro, seja específico DESTA questão, não genérico."""
            else:
                prompt = f"""Você é um instrutor especialista em segurança cibernética.

QUESTÃO: {question}
RESPOSTA INCORRETA DO ALUNO: {user_answer}
RESPOSTA CORRETA: {correct_answer}
CATEGORIA: {category}

Gere um feedback DETALHADO (máximo 250 palavras) que:

1. **PORQUE ERROU**: Explique ESPECIFICAMENTE por que "{user_answer}" está ERRADA em relação a esta questão
2. **PORQUE ESTÁ CERTA**: Explique POR QUE "{correct_answer}" é a resposta CORRETA
3. **CONCEITO**: Ensine o conceito de segurança cibernética envolvido
4. **DIFERENÇA PRÁTICA**: Cite exemplos práticos mostrando a diferença entre a resposta errada e a correta

Seja MUITO ESPECÍFICO sobre ESTA questão e ESTA resposta. Não use frases genéricas.
Use português brasileiro."""
            
            response = self.bedrock.invoke_model(
                modelId='amazon.nova-micro-v1:0',
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {"max_new_tokens": 800, "temperature": 0.8}
                })
            )
            
            result = json.loads(response['body'].read())
            feedback = result['output']['message']['content'][0]['text']
            
            logger.info(f"Feedback gerado para questão: {question[:50]}...")
            return feedback
            
        except Exception as e:
            error_msg = str(e)
            if "ThrottlingException" in error_msg or "Too many tokens" in error_msg:
                logger.warning(f"Limite diário do Bedrock atingido")
                # Retornar feedback informativo sobre limite
                return f"""⚠️ **Limite Diário de IA Atingido**

🤖 O feedback personalizado da IA Amazon Bedrock não está disponível no momento devido ao limite diário do Free Tier.

📅 **Volte amanhã** para receber análises detalhadas da IA!

💡 **Enquanto isso:**
- Continue praticando as questões
- Revise as explicações das respostas
- Consulte materiais de estudo em segurança cibernética

✅ **Sua resposta foi {'correta' if is_correct else 'incorreta'}**
{f'Resposta correta: {correct_answer}' if not is_correct else ''}

🔄 **O sistema continua funcionando normalmente!**"""
            else:
                logger.error(f"Erro ao gerar feedback: {e}")
            return self._get_default_feedback(is_correct, user_answer, correct_answer)
    
    def _get_default_feedback(self, is_correct: bool, user_answer: str = "", correct_answer: str = "") -> str:
        """Retorna feedback padrão quando IA não está disponível"""
        if is_correct:
            return f"""✅ **Parabéns! Você acertou!**

Sua resposta **"{user_answer}"** demonstra correta compreensão deste conceito de segurança cibernética.
Continue praticando para aprofundar ainda mais seus conhecimentos."""
        else:
            return f"""❌ **Sua resposta estava incorreta.**

**Por que essa resposta é errada:**
- Sua resposta: **"{user_answer}"**
- Esta opção não reflete a melhor prática ou o conceito correto de segurança.

**Por que a resposta correta é melhor:**
- Resposta correta: **"{correct_answer}"**
- Esta é a abordagem recomendada pelos especialistas em segurança cibernética.

**Próximas vezes:**
Revise este conceito e tente novamente. A prática contínua ajuda a solidificar o aprendizado em segurança."""
    
    def generate_report_feedback(self, category: str, accuracy: float) -> str:
        """Gera feedback geral sobre desempenho em uma categoria"""
        try:
            if not self.bedrock:
                return f"Sua taxa de acerto foi {accuracy:.1f}%. Continue praticando!"
            
            performance_level = (
                "excelente" if accuracy >= 80
                else "bom" if accuracy >= 60
                else "satisfatório" if accuracy >= 40
                else "precisa melhorar"
            )
            
            prompt = f"""Você é um mentor em segurança cibernética.

Um aluno completou um treinamento em {category} com taxa de acerto de {accuracy:.1f}%.
Desempenho: {performance_level}

Forneça um comentário motivador e construtivo em 4-5 linhas que:
1. Reconheça o esforço (1 linha)
2. Elogie ou sugira melhorias específicas (2 linhas)
3. Recomende próximos passos (1-2 linhas)

Use tom amigável e motivador. Português brasileiro."""
            
            response = self.bedrock.invoke_model(
                modelId='amazon.nova-micro-v1:0',
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {"max_new_tokens": 300, "temperature": 0.8}
                })
            )
            
            result = json.loads(response['body'].read())
            return result['output']['message']['content'][0]['text']
            
        except Exception as e:
            error_msg = str(e)
            if "ThrottlingException" in error_msg or "Too many tokens" in error_msg:
                logger.warning(f"Limite diário do Bedrock atingido para relatório")
                return f"📅 Feedback detalhado da IA estará disponível amanhã. Sua taxa de acerto foi {accuracy:.1f}% - {'Excelente!' if accuracy >= 80 else 'Continue praticando!'}"
            else:
                logger.error(f"Erro ao gerar feedback de relatório: {e}")
            return f"Parabéns por sua taxa de acerto de {accuracy:.1f}%! Continue praticando."


class AIQuestionGenerator:
    """Gera questões com Amazon Bedrock IA"""
    
    def __init__(self):
        self.bedrock = get_aws_client().bedrock
    
    def generate_question(self, category: str, difficulty: str = 'medium',
                         topic: str = '') -> Dict:
        """Gera uma questão completa com IA"""
        try:
            if not self.bedrock:
                return None
            
            category_topics = {
                'phishing': 'identificação de emails maliciosos e ataques de phishing',
                'passwords': 'criação e gerenciamento seguro de senhas',
                'social_engineering': 'táticas de manipulação e engenharia social',
                'malware': 'prevenção e detecção de malware'
            }
            
            topic = topic or category_topics.get(category, 'segurança cibernética')
            
            prompt = f"""Crie uma questão de múltipla escolha sobre segurança cibernética.

Tópico: {topic}
Categoria: {category}
Dificuldade: {difficulty}

Retorne APENAS um JSON válido neste exato formato:
{{
  "question": "Pergunta clara em português BR (máx. 100 caracteres)",
  "options": ["Opção A realista", "Opção B realista", "Opção C realista", "Opção D realista"],
  "correctAnswer": 1,
  "explanation": "Explicação de por que esta resposta está correta (50 palavras máximo)",
  "why_wrong": {{
    "0": "Por que opção A está errada (25 palavras)",
    "2": "Por que opção C está errada (25 palavras)",
    "3": "Por que opção D está errada (25 palavras)"
  }}
}}

Crie apenas JSON válido, sem explicações adicionais."""
            
            response = self.bedrock.invoke_model(
                modelId='amazon.nova-micro-v1:0',
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {"max_new_tokens": 500, "temperature": 0.9}
                })
            )
            
            result = json.loads(response['body'].read())
            response_text = result['output']['message']['content'][0]['text']
            
            # Parse JSON da resposta
            question_data = json.loads(response_text)
            logger.info(f"Questão gerada: {question_data['question'][:50]}...")
            
            return question_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao fazer parse da resposta IA: {e}")
            return None
        except Exception as e:
            error_msg = str(e)
            if "ThrottlingException" in error_msg or "Too many tokens" in error_msg:
                logger.warning(f"Limite diário do Bedrock atingido para geração de questões")
                return None  # Retorna None para indicar que não foi possível gerar
            else:
                logger.error(f"Erro ao gerar questão: {e}")
            return None
