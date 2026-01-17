"""
Módulo para inicialização e gerenciamento de clientes AWS
"""
import boto3
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class AWSClient:
    """Cliente centralizado para serviços AWS"""
    
    _instance = None
    _dynamodb = None
    _bedrock = None
    _cognito = None
    _cloudwatch = None
    _s3 = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AWSClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa clientes AWS com cache"""
        if self._dynamodb is None:
            self._init_clients()
    
    def _init_clients(self):
        """Inicializa todos os clientes AWS"""
        try:
            self._dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            self._bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
            self._cognito = boto3.client('cognito-idp', region_name='us-east-1')
            self._cloudwatch = boto3.client('logs', region_name='us-east-1')
            self._s3 = boto3.client('s3', region_name='us-east-1')
            logger.info("✅ Clientes AWS inicializados com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar clientes AWS: {e}")
            raise
    
    @property
    def dynamodb(self):
        return self._dynamodb
    
    @property
    def bedrock(self):
        return self._bedrock
    
    @property
    def cognito(self):
        return self._cognito
    
    @property
    def cloudwatch(self):
        return self._cloudwatch
    
    @property
    def s3(self):
        return self._s3
    
    def is_healthy(self) -> bool:
        """Verifica se todos os clientes estão disponíveis"""
        return all([self._dynamodb, self._bedrock, self._cognito, self._cloudwatch, self._s3])


def get_aws_client() -> AWSClient:
    """Retorna instância singleton do cliente AWS"""
    return AWSClient()
