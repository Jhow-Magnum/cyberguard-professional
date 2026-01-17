"""
Módulo de Feedback e Análise com IA Bedrock
"""
import json
import logging
from typing import Dict
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from utils.aws_client import get_aws_client

logger = logging.getLogger(__name__)

class FeedbackGenerator:
    """Gera feedback inteligente com Amazon Bedrock - VERSÃO ROBUSTA"""
    
    def __init__(self):
        try:
            self.bedrock = get_aws_client().bedrock
        except:
            self.bedrock = None
    
    def generate_feedback(self, question: str, user_answer: str,
                         correct_answer: str, is_correct: bool,
                         category: str) -> str:
        """Gera feedback com IA - VERSÃO ROBUSTA COM FALLBACK GARANTIDO"""
        # Sempre tentar feedback local primeiro se não tiver Bedrock
        if not self.bedrock:
            return self._get_local_feedback(is_correct, user_answer, correct_answer)
        
        try:
            # Tentar IA com timeout rápido
            prompt = self._build_prompt(question, user_answer, correct_answer, is_correct)
            
            response = self.bedrock.invoke_model(
                modelId='amazon.nova-micro-v1:0',
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {"max_new_tokens": 200, "temperature": 0.7}
                })
            )
            
            result = json.loads(response['body'].read())
            ai_feedback = result['output']['message']['content'][0]['text']
            
            # Retornar feedback da IA se sucesso
            return f"🤖 **Feedback da IA:**\n\n{ai_feedback}"
            
        except Exception as e:
            # SEMPRE retornar feedback local em caso de erro
            logger.warning(f"Bedrock falhou, usando local: {e}")
            return self._get_local_feedback(is_correct, user_answer, correct_answer)
    
    def _build_prompt(self, question: str, user_answer: str, correct_answer: str, is_correct: bool) -> str:
        """Constrói prompt otimizado"""
        if is_correct:
            return f"Parabéns! Explique em 50 palavras por que '{user_answer}' é a resposta correta para: {question}"
        else:
            return f"Explique em 80 palavras por que '{correct_answer}' é melhor que '{user_answer}' para: {question}"
    
    def _get_local_feedback(self, is_correct: bool, user_answer: str, correct_answer: str) -> str:
        """Feedback local sempre funcional"""
        if is_correct:
            return f"✅ **Excelente!** Sua resposta '{user_answer}' está correta! Você demonstra boa compreensão dos conceitos de segurança cibernética."
        else:
            return f"❌ **Resposta incorreta.** Sua resposta '{user_answer}' não é a ideal. A resposta correta '{correct_answer}' representa a melhor prática em segurança. Continue estudando!"
    
    def _call_bedrock_feedback_simple(self, question: str, user_answer: str, 
                              correct_answer: str, is_correct: bool, category: str) -> str:
        """Chama o Bedrock de forma simples sem threading"""
        try:
            logger.info("Iniciando chamada Bedrock simples")
            
            if is_correct:
                prompt = f"Parabéns! Sua resposta '{user_answer}' para a questão '{question}' está correta. Explique brevemente por que em 50 palavras."
            else:
                prompt = f"Sua resposta '{user_answer}' para '{question}' está incorreta. A correta é '{correct_answer}'. Explique a diferença em 100 palavras."
            
            response = self.bedrock.invoke_model(
                modelId='amazon.nova-micro-v1:0',
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {"max_new_tokens": 300, "temperature": 0.7}
                })
            )
            
            result = json.loads(response['body'].read())
            feedback = result['output']['message']['content'][0]['text']
            
            logger.info("Feedback Bedrock gerado com sucesso")
            return feedback
            
        except Exception as e:
            logger.error(f"Erro na chamada Bedrock simples: {e}")
            raise e
    
    def _get_quota_exceeded_feedback(self, is_correct: bool, user_answer: str = "", correct_answer: str = "") -> str:
        """Feedback quando limite de tokens é atingido"""
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
    
    def _get_timeout_feedback(self, is_correct: bool, user_answer: str = "", correct_answer: str = "") -> str:
        """Feedback quando há timeout na chamada"""
        return f"""⏱️ **Timeout na Geração de Feedback**

A IA está demorando para responder. Usando feedback local:

{'✅ Parabéns! Você acertou!' if is_correct else '❌ Resposta incorreta.'}

{f'Sua resposta: {user_answer}' if user_answer else ''}
{f'Resposta correta: {correct_answer}' if not is_correct and correct_answer else ''}

🔄 **Tente novamente em alguns minutos para feedback da IA.**"""
    
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
            
            # Usar timeout para evitar travamento
            with ThreadPoolExecutor() as executor:
                future = executor.submit(self._call_bedrock_report, category, accuracy)
                try:
                    return future.result(timeout=8)  # 8 segundos timeout
                except TimeoutError:
                    logger.warning("Timeout na geração de relatório - usando feedback local")
                    return f"⏱️ Timeout na IA. Sua taxa de acerto foi {accuracy:.1f}% - {'Excelente!' if accuracy >= 80 else 'Continue praticando!'}"
            
        except Exception as e:
            error_msg = str(e)
            if "ThrottlingException" in error_msg or "Too many tokens" in error_msg or "ServiceQuotaExceededException" in error_msg:
                logger.warning(f"Limite diário do Bedrock atingido para relatório")
                return f"📅 Feedback detalhado da IA estará disponível amanhã. Sua taxa de acerto foi {accuracy:.1f}% - {'Excelente!' if accuracy >= 80 else 'Continue praticando!'}"
            else:
                logger.error(f"Erro ao gerar feedback de relatório: {e}")
            return f"Parabéns por sua taxa de acerto de {accuracy:.1f}%! Continue praticando."
    
    def _call_bedrock_report(self, category: str, accuracy: float) -> str:
        """Chama o Bedrock para relatório de forma isolada"""
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


class AIQuestionGenerator:
    """Gera questões - DESABILITADO TEMPORARIAMENTE"""
    
    def __init__(self):
        # DESABILITADO: self.bedrock = get_aws_client().bedrock
        self.bedrock = None  # Forçar None para evitar chamadas
    
    def generate_question(self, category: str, difficulty: str = 'medium',
                         topic: str = '') -> Dict:
        """DESABILITADO - Retorna None sempre"""
        return None  # Sempre retorna None - IA desabilitada
    
    def _call_bedrock_question(self, category: str, difficulty: str, topic: str) -> Dict:
        """Chama o Bedrock para geração de questão de forma isolada"""
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
        
        try:
            # Parse JSON da resposta
            question_data = json.loads(response_text)
            logger.info(f"Questão gerada: {question_data['question'][:50]}...")
            return question_data
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao fazer parse da resposta IA: {e}")
            raise e
