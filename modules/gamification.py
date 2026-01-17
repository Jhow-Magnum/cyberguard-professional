"""
Módulo de Certificados e Gamificação
"""
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional
from utils.aws_client import get_aws_client

logger = logging.getLogger(__name__)

class CertificateManager:
    """Gerencia geração e armazenamento de certificados"""
    
    def __init__(self):
        self.dynamodb = get_aws_client().dynamodb
        self.s3 = get_aws_client().s3
        self.table = self.dynamodb.Table('cyberguard-certificates')
        self.bucket = 'cyberguard-certificates'
    
    def check_eligibility(self, accuracy: float, total_questions: int) -> Dict:
        """Verifica elegibilidade para certificado"""
        return {
            'eligible': accuracy >= 80 and total_questions >= 8,
            'accuracy': accuracy,
            'required_accuracy': 80,
            'required_questions': 8,
            'status': 'Qualificado para certificado' if accuracy >= 80 and total_questions >= 8 else 'Não qualificado'
        }
    
    def generate_certificate(self, user_id: str, user_name: str,
                            category: str, accuracy: float,
                            total_questions: int) -> Optional[Dict]:
        """Gera certificado para usuário"""
        try:
            eligibility = self.check_eligibility(accuracy, total_questions)
            
            if not eligibility['eligible']:
                return {'success': False, 'message': 'Usuário não atende critérios mínimos'}
            
            certificate_id = f"{user_id}_{category}_{int(datetime.now().timestamp())}"
            
            certificate_data = {
                'certificateId': certificate_id,
                'userId': user_id,
                'userName': user_name,
                'category': category,
                'accuracy': Decimal(str(accuracy)),
                'total_questions': total_questions,
                'issued_at': Decimal(str(datetime.now().timestamp())),
                'valid_until': Decimal(str((datetime.now().timestamp()) + (365 * 24 * 60 * 60)))
            }
            
            # Salvar no DynamoDB
            self.table.put_item(Item=certificate_data)
            
            # Gerar PDF (simulado - em produção usaria reportlab)
            pdf_content = self._generate_pdf_content(certificate_data)
            
            # Salvar no S3
            key = f"certificates/{user_id}/{certificate_id}.pdf"
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=pdf_content,
                ContentType='application/pdf'
            )
            
            logger.info(f"Certificado gerado: {certificate_id}")
            
            return {
                'success': True,
                'certificate_id': certificate_id,
                's3_url': f"s3://{self.bucket}/{key}",
                'issued_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar certificado: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_pdf_content(self, certificate_data: Dict) -> bytes:
        """Gera conteúdo PDF do certificado (simulado)"""
        # Em produção, usar reportlab para gerar PDF real
        content = f"""
CERTIFICADO DE CONCLUSÃO
CYBERGUARD PROFESSIONAL TRAINING

Certificado para: {certificate_data['userName']}
Categoria: {certificate_data['category']}
Taxa de Acerto: {certificate_data['accuracy']}%
Data de Emissão: {datetime.now().strftime('%d/%m/%Y')}

ID do Certificado: {certificate_data['certificateId']}

Este certificado atesta a conclusão bem-sucedida do treinamento em
segurança cibernética na plataforma CyberGuard Professional.
"""
        return content.encode('utf-8')
    
    def get_user_certificates(self, user_id: str) -> list:
        """Obtém certificados do usuário"""
        try:
            response = self.table.query(
                KeyConditionExpression='userId = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Erro ao obter certificados: {e}")
            return []
    
    def verify_certificate(self, certificate_id: str) -> Optional[Dict]:
        """Verifica autenticidade de certificado"""
        try:
            response = self.table.scan(
                FilterExpression='certificateId = :cid',
                ExpressionAttributeValues={':cid': certificate_id}
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except Exception as e:
            logger.error(f"Erro ao verificar certificado: {e}")
            return None


class GamificationManager:
    """Gerencia sistema de gamificação e badges"""
    
    BADGES = {
        'first_correct': {'name': 'Primeiro Acerto', 'icon': '🎯', 'requirement': 'Acertar primeira questão'},
        'streak_5': {'name': 'Sequência Vitoriosa', 'icon': '🔥', 'requirement': '5 acertos seguidos'},
        'streak_10': {'name': 'Super Sequência', 'icon': '⚡', 'requirement': '10 acertos seguidos'},
        'accuracy_80': {'name': 'Especialista', 'icon': '🏆', 'requirement': '80% de acerto'},
        'accuracy_100': {'name': 'Perfeição', 'icon': '👑', 'requirement': '100% de acerto'},
        'allrounder': {'name': 'Profissional Completo', 'icon': '🛡️', 'requirement': 'Treinar em todas categorias'},
        'speedster': {'name': 'Rápido', 'icon': '⚡', 'requirement': 'Responder em menos de 30 segundos'},
        'persistent': {'name': 'Dedicado', 'icon': '💪', 'requirement': '30+ questões respondidas'},
        'champion': {'name': 'Campeão', 'icon': '🥇', 'requirement': 'Top 3 do ranking'},
    }
    
    def __init__(self):
        self.dynamodb = get_aws_client().dynamodb
        self.badges_table = self.dynamodb.Table('cyberguard-badges')
    
    def unlock_badge(self, user_id: str, badge_id: str) -> bool:
        """Desbloqueia badge para usuário"""
        try:
            if badge_id not in self.BADGES:
                return False
            
            badge_data = {
                'userId': user_id,
                'badgeId': badge_id,
                'unlockedAt': Decimal(str(datetime.now().timestamp())),
                'badge_info': json.dumps(self.BADGES[badge_id])
            }
            
            self.badges_table.put_item(Item=badge_data)
            logger.info(f"Badge desbloqueado: {badge_id} para {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao desbloquear badge: {e}")
            return False
    
    def get_user_badges(self, user_id: str) -> list:
        """Obtém badges desbloqueados do usuário"""
        try:
            response = self.badges_table.query(
                KeyConditionExpression='userId = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Erro ao obter badges: {e}")
            return []
    
    def get_user_points(self, accuracy: float, streak: int, questions_count: int) -> int:
        """Calcula pontos do usuário baseado em performance"""
        points = 0
        
        # Pontos por acurácia
        points += int(accuracy * 10)  # Até 1000 pontos
        
        # Bônus por sequência
        points += min(streak * 50, 500)  # Até 500 pontos
        
        # Bônus por volume
        points += min(questions_count * 10, 300)  # Até 300 pontos
        
        return points
    
    def check_badge_eligibility(self, user_id: str, stats: Dict) -> list:
        """Verifica e retorna badges elegíveis para desbloquear"""
        unlocked = set(b['badgeId'] for b in self.get_user_badges(user_id))
        eligible = []
        
        # Verificar elegibilidade para cada badge
        if 'accuracy_80' not in unlocked and stats.get('accuracy', 0) >= 80:
            eligible.append('accuracy_80')
        
        if 'accuracy_100' not in unlocked and stats.get('accuracy', 0) >= 99:
            eligible.append('accuracy_100')
        
        if 'streak_5' not in unlocked and stats.get('streak', 0) >= 5:
            eligible.append('streak_5')
        
        if 'streak_10' not in unlocked and stats.get('streak', 0) >= 10:
            eligible.append('streak_10')
        
        if 'persistent' not in unlocked and stats.get('total_answers', 0) >= 30:
            eligible.append('persistent')
        
        return eligible
