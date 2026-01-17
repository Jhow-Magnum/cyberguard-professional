"""
Arquivo de configuração e constantes da aplicação
"""

# Categorias de Treinamento
TRAINING_CATEGORIES = {
    'phishing': {
        'name': '🎣 Phishing',
        'description': 'Identificação de emails maliciosos e ataques de phishing',
        'color': '#FF6B6B'
    },
    'passwords': {
        'name': '🔐 Senhas',
        'description': 'Criação e gerenciamento seguro de senhas',
        'color': '#4ECDC4'
    },
    'social_engineering': {
        'name': '🎭 Engenharia Social',
        'description': 'Táticas de manipulação e engenharia social',
        'color': '#FFE66D'
    },
    'malware': {
        'name': '🦠 Malware',
        'description': 'Prevenção e detecção de malware',
        'color': '#95E1D3'
    }
}

# Níveis de Dificuldade
DIFFICULTY_LEVELS = {
    'easy': {'name': '🟢 Fácil', 'points': 10},
    'medium': {'name': '🟡 Médio', 'points': 25},
    'hard': {'name': '🔴 Difícil', 'points': 50}
}

# Certificação
CERTIFICATION_REQUIREMENTS = {
    'min_accuracy': 80.0,  # 80% de acertos mínimo
    'min_questions': 8,    # Pelo menos 8 questões
    'validity_days': 365   # Válido por 1 ano
}

# Gamificação
GAMIFICATION = {
    'accuracy_80': {'points': 100, 'name': 'Especialista'},
    'accuracy_100': {'points': 500, 'name': 'Perfeição'},
    'streak_5': {'points': 50, 'name': 'Sequência Vitoriosa'},
    'streak_10': {'points': 200, 'name': 'Super Sequência'},
    'persistent': {'points': 150, 'name': 'Dedicado'},
    'speedster': {'points': 75, 'name': 'Rápido'},
    'allrounder': {'points': 300, 'name': 'Profissional Completo'},
    'champion': {'points': 500, 'name': 'Campeão'}
}

# AWS Configuration
AWS_REGION = 'us-east-1'
DYNAMODB_TABLES = {
    'questions': 'cyberguard-questions',
    'progress': 'cyberguard-progress',
    'certificates': 'cyberguard-certificates',
    'badges': 'cyberguard-badges'
}

BEDROCK_CONFIG = {
    'model_id': 'amazon.nova-micro-v1:0',
    'max_tokens_feedback': 800,
    'max_tokens_question': 500,
    'temperature_feedback': 0.7,
    'temperature_question': 0.9
}

# Logging
LOG_LEVEL = 'INFO'
LOG_GROUP = '/cyberguard/app'

# Streamlit
STREAMLIT_CONFIG = {
    'page_title': 'CyberGuard Professional v2.0',
    'page_icon': '🛡️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Paginação
PAGINATION = {
    'questions_per_page': 10,
    'results_per_page': 20,
    'leaderboard_size': 10
}

# Timeouts
TIMEOUTS = {
    'bedrock_invoke': 60,
    'dynamodb_query': 5,
    'session_timeout': 3600  # 1 hora
}
