"""
Testes para módulo de questões
"""
import unittest
from unittest.mock import MagicMock, patch
from modules.questions import QuestionManager

class TestQuestionManager(unittest.TestCase):
    """Testes para gerenciamento de questões"""
    
    def setUp(self):
        """Configuração para cada teste"""
        self.mock_dynamodb = MagicMock()
        self.mock_table = MagicMock()
        self.mock_dynamodb.Table.return_value = self.mock_table
    
    @patch('modules.questions.get_aws_client')
    def test_create_question(self, mock_aws):
        """Testa criação de questão"""
        mock_aws.return_value.dynamodb = self.mock_dynamodb
        
        manager = QuestionManager()
        manager.table = self.mock_table
        
        result = manager.create(
            question="Qual é a melhor senha?",
            options=["123456", "Abc@12345", "password", "admin"],
            correct_answer=1,
            explanation="Senhas fortes têm maiúsculas, minúsculas, números e símbolos",
            category="passwords"
        )
        
        self.assertTrue(result)
        self.mock_table.put_item.assert_called_once()
    
    @patch('modules.questions.get_aws_client')
    def test_get_by_category(self, mock_aws):
        """Testa busca de questões por categoria"""
        mock_aws.return_value.dynamodb = self.mock_dynamodb
        
        manager = QuestionManager()
        manager.table = self.mock_table
        
        mock_data = [{
            'questionId': 'q1',
            'question': 'Test',
            'category': 'phishing'
        }]
        self.mock_table.query.return_value = {'Items': mock_data}
        
        result = manager.get_by_category('phishing')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['category'], 'phishing')
    
    @patch('modules.questions.get_aws_client')
    def test_delete_question(self, mock_aws):
        """Testa deleção de questão"""
        mock_aws.return_value.dynamodb = self.mock_dynamodb
        
        manager = QuestionManager()
        manager.table = self.mock_table
        
        result = manager.delete('q1')
        
        self.assertTrue(result)
        self.mock_table.delete_item.assert_called_once()


class TestQuestionManagerIntegration(unittest.TestCase):
    """Testes de integração (requer AWS configurado)"""
    
    @unittest.skip("Requer AWS credentials")
    def test_full_workflow(self):
        """Testa fluxo completo de questão"""
        manager = QuestionManager()
        
        # Criar
        success = manager.create(
            question="Teste",
            options=["A", "B", "C", "D"],
            correct_answer=0,
            explanation="Explicação",
            category="test"
        )
        self.assertTrue(success)
        
        # Obter
        questions = manager.get_by_category('test')
        self.assertGreater(len(questions), 0)
        
        # Deletar
        if questions:
            success = manager.delete(questions[0]['questionId'])
            self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()
