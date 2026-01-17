"""
Módulo de Relatórios e Exportação
"""
import csv
import json
import logging
from io import StringIO, BytesIO
from datetime import datetime
from typing import List, Dict, Optional
from utils.aws_client import get_aws_client

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Gera relatórios de desempenho e dados"""
    
    def __init__(self):
        self.dynamodb = get_aws_client().dynamodb
        self.progress_table = self.dynamodb.Table('cyberguard-progress')
    
    def generate_user_report_csv(self, user_id: str) -> Optional[str]:
        """Gera relatório do usuário em CSV"""
        try:
            response = self.progress_table.query(
                KeyConditionExpression='userId = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
            
            items = response.get('Items', [])
            if not items:
                return None
            
            # Criar CSV
            output = StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=['timestamp', 'questionId', 'category', 'correct', 'time_spent']
            )
            
            writer.writeheader()
            for item in items:
                writer.writerow({
                    'timestamp': datetime.fromtimestamp(float(item['timestamp'])).isoformat(),
                    'questionId': item.get('questionId', ''),
                    'category': item.get('category', ''),
                    'correct': item.get('correct', False),
                    'time_spent': item.get('time_spent', 0)
                })
            
            logger.info(f"Relatório CSV gerado para usuário {user_id}")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório CSV: {e}")
            return None
    
    def generate_instructor_report(self, category: Optional[str] = None) -> Dict:
        """Gera relatório agregado para instrutores"""
        try:
            response = self.progress_table.scan()
            all_items = response.get('Items', [])
            
            # Filtrar por categoria se especificado
            if category:
                all_items = [item for item in all_items if item.get('category') == category]
            
            # Agregação de dados
            stats = {
                'total_responses': len(all_items),
                'total_users': len(set(item.get('userId') for item in all_items)),
                'overall_accuracy': 0.0,
                'by_category': {},
                'by_user': {},
                'timestamp': datetime.now().isoformat()
            }
            
            correct_count = sum(1 for item in all_items if item.get('correct', False))
            stats['overall_accuracy'] = (correct_count / len(all_items) * 100) if all_items else 0
            
            # Estatísticas por categoria
            for item in all_items:
                cat = item.get('category', 'unknown')
                if cat not in stats['by_category']:
                    stats['by_category'][cat] = {'total': 0, 'correct': 0}
                
                stats['by_category'][cat]['total'] += 1
                if item.get('correct', False):
                    stats['by_category'][cat]['correct'] += 1
            
            # Calcular taxa por categoria
            for cat in stats['by_category']:
                total = stats['by_category'][cat]['total']
                correct = stats['by_category'][cat]['correct']
                stats['by_category'][cat]['accuracy'] = (correct / total * 100) if total > 0 else 0
            
            # Estatísticas por usuário
            for item in all_items:
                user = item.get('userId', 'unknown')
                if user not in stats['by_user']:
                    stats['by_user'][user] = {'total': 0, 'correct': 0}
                
                stats['by_user'][user]['total'] += 1
                if item.get('correct', False):
                    stats['by_user'][user]['correct'] += 1
            
            # Calcular taxa por usuário
            for user in stats['by_user']:
                total = stats['by_user'][user]['total']
                correct = stats['by_user'][user]['correct']
                stats['by_user'][user]['accuracy'] = (correct / total * 100) if total > 0 else 0
            
            logger.info(f"Relatório de instrutor gerado")
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de instrutor: {e}")
            return {}
    
    def export_to_json(self, user_id: str) -> Optional[str]:
        """Exporta dados do usuário em JSON"""
        try:
            response = self.progress_table.query(
                KeyConditionExpression='userId = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
            
            items = response.get('Items', [])
            
            # Converter Decimal para tipos padrão JSON
            items_json = []
            for item in items:
                item_dict = {}
                for key, value in item.items():
                    if isinstance(value, type(item['timestamp'])):  # Decimal
                        item_dict[key] = float(value)
                    else:
                        item_dict[key] = value
                items_json.append(item_dict)
            
            logger.info(f"Dados exportados em JSON para usuário {user_id}")
            return json.dumps(items_json, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Erro ao exportar JSON: {e}")
            return None
    
    def generate_summary_report(self, user_id: str) -> Dict:
        """Gera relatório resumido do usuário"""
        try:
            response = self.progress_table.query(
                KeyConditionExpression='userId = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
            
            items = response.get('Items', [])
            
            if not items:
                return {'error': 'Nenhum dado disponível'}
            
            total = len(items)
            correct = sum(1 for item in items if item.get('correct', False))
            
            # Por categoria
            by_category = {}
            for item in items:
                cat = item.get('category', 'unknown')
                if cat not in by_category:
                    by_category[cat] = {'total': 0, 'correct': 0}
                by_category[cat]['total'] += 1
                if item.get('correct', False):
                    by_category[cat]['correct'] += 1
            
            # Calcular taxas
            category_stats = {}
            for cat, stats in by_category.items():
                accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                category_stats[cat] = {
                    'total': stats['total'],
                    'correct': stats['correct'],
                    'accuracy': accuracy
                }
            
            # Tempo de estudo (se disponível)
            total_time = sum(item.get('time_spent', 0) for item in items)
            
            summary = {
                'user_id': user_id,
                'total_questions': total,
                'correct_answers': correct,
                'overall_accuracy': (correct / total * 100) if total > 0 else 0,
                'by_category': category_stats,
                'total_study_time_seconds': total_time,
                'average_time_per_question': (total_time / total) if total > 0 else 0,
                'generated_at': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório resumido: {e}")
            return {}
