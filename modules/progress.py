"""
Módulo de Gerenciamento de Progresso e Análise
"""
import json
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from utils.aws_client import get_aws_client
from utils.logger import log_event

logger = logging.getLogger(__name__)

class ProgressManager:
    """Gerencia progresso e resultados dos usuários"""
    
    def __init__(self):
        self.dynamodb = get_aws_client().dynamodb
        self.table = self.dynamodb.Table('cyberguard-progress')
    
    def save_answer(self, user_id: str, question_id: str, correct: bool,
                    category: str, time_spent: int = 0) -> bool:
        """Salva resposta do usuário"""
        try:
            self.table.put_item(Item={
                'userId': user_id,
                'timestamp': Decimal(str(datetime.now().timestamp())),
                'questionId': question_id,
                'correct': correct,
                'category': category,
                'time_spent': time_spent
            })
            
            log_event(logger, 'answer_submitted', user_id, {
                'question_id': question_id,
                'correct': correct,
                'category': category
            })
            
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar resposta: {e}")
            return False
    
    def get_user_progress(self, user_id: str) -> List[Dict]:
        """Obtém histórico de respostas do usuário"""
        try:
            response = self.table.query(
                KeyConditionExpression='userId = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
            
            # Ordena por timestamp decrescente
            items = sorted(
                response.get('Items', []),
                key=lambda x: x.get('timestamp', 0),
                reverse=True
            )
            
            return items
        except Exception as e:
            logger.error(f"Erro ao obter progresso: {e}")
            return []
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Obtém estatísticas de desempenho do usuário"""
        try:
            progress = self.get_user_progress(user_id)
            
            if not progress:
                return {
                    'total_answers': 0,
                    'correct_answers': 0,
                    'accuracy': 0.0,
                    'by_category': {},
                    'streak': 0,
                    'last_activity': None
                }
            
            total = len(progress)
            correct = sum(1 for p in progress if p.get('correct', False))
            accuracy = (correct / total * 100) if total > 0 else 0
            
            # Estatísticas por categoria
            by_category = {}
            for p in progress:
                cat = p.get('category', 'unknown')
                if cat not in by_category:
                    by_category[cat] = {'total': 0, 'correct': 0}
                by_category[cat]['total'] += 1
                if p.get('correct', False):
                    by_category[cat]['correct'] += 1
            
            # Calcular taxa de acerto por categoria
            for cat in by_category:
                total_cat = by_category[cat]['total']
                correct_cat = by_category[cat]['correct']
                by_category[cat]['accuracy'] = (correct_cat / total_cat * 100) if total_cat > 0 else 0
            
            # Streak atual
            streak = 0
            for p in progress:
                if p.get('correct', False):
                    streak += 1
                else:
                    break
            
            return {
                'total_answers': total,
                'correct_answers': correct,
                'accuracy': accuracy,
                'by_category': by_category,
                'streak': streak,
                'last_activity': progress[0].get('timestamp') if progress else None
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def get_recent_activity(self, user_id: str, days: int = 7) -> List[Dict]:
        """Obtém atividade recente do usuário"""
        try:
            progress = self.get_user_progress(user_id)
            cutoff = datetime.now() - timedelta(days=days)
            cutoff_timestamp = Decimal(str(cutoff.timestamp()))
            
            return [p for p in progress if p.get('timestamp', 0) >= cutoff_timestamp]
        except Exception as e:
            logger.error(f"Erro ao obter atividade: {e}")
            return []
    
    def get_leaderboard(self, limit: int = 10, category: Optional[str] = None) -> List[Dict]:
        """Obtém ranking de usuários por desempenho"""
        try:
            # Nota: Em produção, isso seria feito com GSI melhor otimizada
            response = self.table.scan()
            all_data = response.get('Items', [])
            
            # Agrupar por usuário
            user_stats = {}
            for item in all_data:
                user_id = item.get('userId')
                cat = item.get('category')
                
                if category and cat != category:
                    continue
                
                if user_id not in user_stats:
                    user_stats[user_id] = {'total': 0, 'correct': 0}
                
                user_stats[user_id]['total'] += 1
                if item.get('correct', False):
                    user_stats[user_id]['correct'] += 1
            
            # Calcular taxa de acerto e ordenar
            leaderboard = []
            for user_id, stats in user_stats.items():
                accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                leaderboard.append({
                    'user_id': user_id,
                    'accuracy': accuracy,
                    'correct': stats['correct'],
                    'total': stats['total']
                })
            
            leaderboard.sort(key=lambda x: x['accuracy'], reverse=True)
            return leaderboard[:limit]
        except Exception as e:
            logger.error(f"Erro ao obter leaderboard: {e}")
            return []
    
    def delete_user_progress(self, user_id: str) -> int:
        """Deleta todos registros de progresso do usuário"""
        try:
            progress = self.get_user_progress(user_id)
            count = 0
            
            for item in progress:
                self.table.delete_item(
                    Key={
                        'userId': user_id,
                        'timestamp': item['timestamp']
                    }
                )
                count += 1
            
            logger.info(f"Progresso deletado para usuário {user_id}: {count} registros")
            return count
        except Exception as e:
            logger.error(f"Erro ao deletar progresso: {e}")
            return 0
