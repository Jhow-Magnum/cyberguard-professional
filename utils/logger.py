"""
Módulo de logging centralizado com CloudWatch
"""
import logging
import json
from datetime import datetime
from typing import Any, Optional
from utils.aws_client import get_aws_client

class CloudWatchHandler(logging.Handler):
    """Handler customizado para enviar logs ao CloudWatch"""
    
    def __init__(self):
        super().__init__()
        self.cloudwatch = get_aws_client().cloudwatch
        self.log_group = '/cyberguard/app'
        self.log_stream = f'app-{datetime.now().strftime("%Y-%m-%d")}'
        self._ensure_log_group()
    
    def _ensure_log_group(self):
        """Garante que o log group e stream existem"""
        try:
            self.cloudwatch.create_log_group(logGroupName=self.log_group)
        except self.cloudwatch.exceptions.ResourceAlreadyExistsException:
            pass
        except Exception as e:
            logging.error(f"Erro ao criar log group: {e}")
        
        try:
            self.cloudwatch.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
        except self.cloudwatch.exceptions.ResourceAlreadyExistsException:
            pass
        except Exception as e:
            logging.error(f"Erro ao criar log stream: {e}")
    
    def emit(self, record: logging.LogRecord):
        """Envia registro de log ao CloudWatch"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': self.format(record),
                'extra': getattr(record, 'extra', {})
            }
            
            self.cloudwatch.put_log_events(
                logGroupName=self.log_group,
                logStreamName=self.log_stream,
                logEvents=[{
                    'timestamp': int(datetime.now().timestamp() * 1000),
                    'message': json.dumps(log_entry, ensure_ascii=False)
                }]
            )
        except Exception as e:
            logging.error(f"Erro ao enviar log ao CloudWatch: {e}")


def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """Configura logger com suporte a CloudWatch"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para CloudWatch
    try:
        cloudwatch_handler = CloudWatchHandler()
        cloudwatch_handler.setFormatter(formatter)
        logger.addHandler(cloudwatch_handler)
    except Exception as e:
        logger.warning(f"CloudWatch não disponível: {e}")
    
    return logger


def log_event(logger: logging.Logger, event_type: str, user_id: str, details: dict):
    """Log estruturado de eventos da aplicação"""
    event_data = {
        'event_type': event_type,
        'user_id': user_id,
        'timestamp': datetime.now().isoformat(),
        **details
    }
    logger.info(f"Event: {event_type}", extra={'extra': event_data})
