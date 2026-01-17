"""
Testes para módulo de progresso
"""
import unittest
from unittest.mock import MagicMock, patch
from modules.progress import ProgressManager

class TestProgressManager(unittest.TestCase):
    """Testes para gerenciamento de progresso"""
    
    def setUp(self):
        """Configuração para cada teste"""
        self.mock_dynamodb = MagicMock()
        self.mock_table = MagicMock()
        self.mock_dynamodb.Table.return_value = self.mock_table
    
    @patch('modules.progress.get_aws_client')
    def test_save_answer(self, mock_aws):
        """Testa salvamento de resposta"""
        mock_aws.return_value.dynamodb = self.mock_dynamodb
        
        manager = ProgressManager()
        manager.table = self.mock_table
        
        result = manager.save_answer(
            user_id='user1',
            question_id='q1',
            correct=True,
            category='phishing'
        )
        
        self.assertTrue(result)
        self.mock_table.put_item.assert_called_once()
    
    @patch('modules.progress.get_aws_client')
    def test_get_user_progress(self, mock_aws):
        """Testa obtenção de progresso do usuário"""
        mock_aws.return_value.dynamodb = self.mock_dynamodb
        
        manager = ProgressManager()
        manager.table = self.mock_table
        
        mock_data = [
            {'userId': 'user1', 'questionId': 'q1', 'correct': True},
            {'userId': 'user1', 'questionId': 'q2', 'correct': False}
        ]
        self.mock_table.query.return_value = {'Items': mock_data}
        
        result = manager.get_user_progress('user1')
        
        self.assertEqual(len(result), 2)
    
    @patch('modules.progress.get_aws_client')
    def test_get_user_stats(self, mock_aws):
        """Testa cálculo de estatísticas"""
        mock_aws.return_value.dynamodb = self.mock_dynamodb
        
        manager = ProgressManager()
        manager.table = self.mock_table
        
        mock_data = [
            {'userId': 'user1', 'questionId': 'q1', 'correct': True, 'category': 'phishing'},
            {'userId': 'user1', 'questionId': 'q2', 'correct': True, 'category': 'passwords'},
            {'userId': 'user1', 'questionId': 'q3', 'correct': False, 'category': 'phishing'},
            {'userId': 'user1', 'questionId': 'q4', 'correct': False, 'category': 'passwords'}
        ]
        self.mock_table.query.return_value = {'Items': mock_data}
        
        result = manager.get_user_stats('user1')
        
        self.assertEqual(result['total_answers'], 4)
        self.assertEqual(result['correct_answers'], 2)
        self.assertEqual(result['accuracy'], 50.0)
    
    @patch('modules.progress.get_aws_client')
    def test_get_leaderboard(self, mock_aws):
        """Testa geração de leaderboard"""
        mock_aws.return_value.dynamodb = self.mock_dynamodb
        
        manager = ProgressManager()
        manager.table = self.mock_table
        
        mock_data = [
            {'userId': 'user1', 'correct': 9, 'total': 10},
            {'userId': 'user2', 'correct': 8, 'total': 10},
            {'userId': 'user3', 'correct': 7, 'total': 10}
        ]
        self.mock_table.scan.return_value = {'Items': mock_data}
        
        # Mock para simular a estrutura esperada
        result = manager.get_leaderboard(limit=3)
        
        # Leaderboard deve retornar lista
        self.assertIsInstance(result, list)


if __name__ == '__main__':
    unittest.main()
