"""
Módulo de Gerenciamento de Questões
"""
import json
import uuid
import logging
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Optional
from utils.aws_client import get_aws_client

logger = logging.getLogger(__name__)

class QuestionManager:
    """Gerencia questões no DynamoDB"""
    
    def __init__(self):
        self.dynamodb = get_aws_client().dynamodb
        self.table = self.dynamodb.Table('cyberguard-questions')
    
    def get_by_category(self, category: str, shuffle_options: bool = True) -> List[Dict]:
        """Obtém questões por categoria"""
        try:
            response = self.table.query(
                IndexName='CategoryIndex',
                KeyConditionExpression='category = :cat',
                ExpressionAttributeValues={':cat': category}
            )
            questions = response.get('Items', [])
            
            # Embaralhar alternativas se solicitado
            if shuffle_options:
                import random
                for q in questions:
                    # Salvar resposta correta original
                    correct_idx = int(q['correctAnswer'])
                    correct_option = q['options'][correct_idx]
                    
                    # Criar lista de índices e embaralhar
                    indices = list(range(len(q['options'])))
                    random.shuffle(indices)
                    
                    # Reordenar opções
                    new_options = [q['options'][i] for i in indices]
                    
                    # Encontrar novo índice da resposta correta
                    new_correct_idx = new_options.index(correct_option)
                    
                    # Atualizar questão
                    q['options'] = new_options
                    q['correctAnswer'] = str(new_correct_idx)
                    
                    # Atualizar why_wrong se existir
                    if 'why_wrong' in q:
                        new_why_wrong = {}
                        for old_idx_str, explanation in q['why_wrong'].items():
                            old_idx = int(old_idx_str)
                            if old_idx < len(indices):
                                old_option_idx = indices[old_idx]
                                if old_option_idx < len(q['options']):
                                    new_idx = indices.index(old_idx)
                                    new_why_wrong[str(new_idx)] = explanation
                        q['why_wrong'] = new_why_wrong
            
            return questions
        except Exception as e:
            logger.error(f"Erro ao obter questões: {e}")
            return []
    
    def get_all(self) -> List[Dict]:
        """Obtém todas as questões"""
        try:
            response = self.table.scan()
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Erro ao obter questões: {e}")
            return []
    
    def get_by_id(self, question_id: str) -> Optional[Dict]:
        """Obtém questão pelo ID"""
        try:
            response = self.table.get_item(Key={'questionId': question_id})
            return response.get('Item')
        except Exception as e:
            logger.error(f"Erro ao obter questão: {e}")
            return None
    
    def create(self, question: str, options: List[str], correct_answer: int,
               explanation: str, category: str, difficulty: str = 'medium',
               why_wrong: Optional[Dict] = None) -> bool:
        """Cria nova questão"""
        try:
            self.table.put_item(Item={
                'questionId': str(uuid.uuid4()),
                'question': question,
                'options': options,
                'correctAnswer': str(correct_answer),
                'explanation': explanation,
                'category': category,
                'difficulty': difficulty,
                'why_wrong': why_wrong or {},
                'created_at': Decimal(str(datetime.now().timestamp()))
            })
            logger.info(f"Questão criada: {question[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar questão: {e}")
            return False
    
    def update(self, question_id: str, **kwargs) -> bool:
        """Atualiza questão"""
        try:
            update_expression = "SET " + ", ".join([f"{k}=:{k}" for k in kwargs.keys()])
            expression_values = {f":{k}": v for k, v in kwargs.items()}
            
            self.table.update_item(
                Key={'questionId': question_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            logger.info(f"Questão atualizada: {question_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar questão: {e}")
            return False
    
    def delete(self, question_id: str) -> bool:
        """Deleta questão"""
        try:
            self.table.delete_item(Key={'questionId': question_id})
            logger.info(f"Questão deletada: {question_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar questão: {e}")
            return False
    
    def delete_by_category(self, category: str) -> int:
        """Deleta todas questões de uma categoria"""
        try:
            questions = self.get_by_category(category)
            count = 0
            for q in questions:
                if self.delete(q['questionId']):
                    count += 1
            logger.info(f"{count} questões deletadas da categoria {category}")
            return count
        except Exception as e:
            logger.error(f"Erro ao deletar questões: {e}")
            return 0
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas das questões"""
        try:
            questions = self.get_all()
            
            categories = {}
            difficulties = {}
            
            for q in questions:
                cat = q.get('category', 'unknown')
                diff = q.get('difficulty', 'unknown')
                
                categories[cat] = categories.get(cat, 0) + 1
                difficulties[diff] = difficulties.get(diff, 0) + 1
            
            return {
                'total': len(questions),
                'by_category': categories,
                'by_difficulty': difficulties
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {'total': 0, 'by_category': {}, 'by_difficulty': {}}
