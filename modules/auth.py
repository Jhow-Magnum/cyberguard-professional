"""
Módulo de Autenticação com AWS Cognito
"""
import streamlit as st
import hmac
import hashlib
import logging
from datetime import datetime
from utils.aws_client import get_aws_client
from utils.logger import log_event

logger = logging.getLogger(__name__)

class CognitoAuth:
    """Gerencia autenticação com AWS Cognito"""
    
    def __init__(self, user_pool_id: str, client_id: str):
        self.cognito = get_aws_client().cognito
        self.user_pool_id = user_pool_id
        self.client_id = client_id
    
    def sign_up(self, email: str, password: str, name: str) -> dict:
        """Registra novo usuário"""
        try:
            response = self.cognito.sign_up(
                ClientId=self.client_id,
                Username=email,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'name', 'Value': name}
                ]
            )
            logger.info(f"Novo usuário registrado: {email}")
            return {'success': True, 'user_sub': response['UserSub']}
        except self.cognito.exceptions.UsernameExistsException:
            return {'success': False, 'error': 'Email já registrado'}
        except Exception as e:
            logger.error(f"Erro ao registrar: {e}")
            return {'success': False, 'error': str(e)}
    
    def authenticate(self, email: str, password: str) -> dict:
        """Autentica usuário"""
        try:
            response = self.cognito.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            
            auth_result = response.get('AuthenticationResult', {})
            logger.info(f"Usuário autenticado: {email}")
            
            return {
                'success': True,
                'access_token': auth_result.get('AccessToken'),
                'id_token': auth_result.get('IdToken'),
                'refresh_token': auth_result.get('RefreshToken')
            }
        except self.cognito.exceptions.NotAuthorizedException:
            return {'success': False, 'error': 'Email ou senha inválidos'}
        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            return {'success': False, 'error': 'Erro ao autenticar'}
    
    def get_user(self, access_token: str) -> dict:
        """Obtém informações do usuário autenticado"""
        try:
            response = self.cognito.get_user(AccessToken=access_token)
            
            user_data = {'username': response['Username']}
            for attr in response.get('UserAttributes', []):
                if attr['Name'] in ['email', 'name', 'email_verified']:
                    user_data[attr['Name']] = attr['Value']
            
            return {'success': True, 'user': user_data}
        except Exception as e:
            logger.error(f"Erro ao obter usuário: {e}")
            return {'success': False, 'error': str(e)}
    
    def confirm_sign_up(self, email: str, code: str) -> dict:
        """Confirma registro de novo usuário"""
        try:
            self.cognito.confirm_sign_up(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=code
            )
            logger.info(f"Email confirmado: {email}")
            return {'success': True}
        except Exception as e:
            logger.error(f"Erro ao confirmar email: {e}")
            return {'success': False, 'error': str(e)}


class SessionManager:
    """Gerencia sessões de usuário no Streamlit"""
    
    @staticmethod
    def init_session():
        """Inicializa session state"""
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'access_token' not in st.session_state:
            st.session_state.access_token = None
        if 'user_role' not in st.session_state:
            st.session_state.user_role = 'student'
        if 'questions' not in st.session_state:
            st.session_state.questions = []
        if 'index' not in st.session_state:
            st.session_state.index = 0
        if 'answered' not in st.session_state:
            st.session_state.answered = False
    
    @staticmethod
    def set_user(user_id: str, access_token: str, role: str = 'student'):
        """Define usuário logado"""
        st.session_state.user_id = user_id
        st.session_state.access_token = access_token
        st.session_state.user_role = role
    
    @staticmethod
    def logout():
        """Faz logout do usuário"""
        st.session_state.user_id = None
        st.session_state.access_token = None
        st.session_state.user_role = 'student'
    
    @staticmethod
    def is_logged_in() -> bool:
        """Verifica se usuário está logado"""
        return st.session_state.user_id is not None
    
    @staticmethod
    def get_user_role() -> str:
        """Obtém role do usuário logado"""
        return st.session_state.user_role
    
    @staticmethod
    def require_login():
        """Decorator para requerer login"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not SessionManager.is_logged_in():
                    st.error("❌ Você precisa estar logado")
                    st.stop()
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def require_role(required_role: str):
        """Decorator para requerer role específico"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not SessionManager.is_logged_in():
                    st.error("❌ Você precisa estar logado")
                    st.stop()
                
                user_role = SessionManager.get_user_role()
                role_hierarchy = {'admin': 3, 'instructor': 2, 'student': 1}
                
                if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
                    st.error(f"❌ Permissão negada. Role necessário: {required_role}")
                    st.stop()
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
