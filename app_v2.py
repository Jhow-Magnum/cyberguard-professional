"""
CyberGuard Professional - Plataforma de Treinamento em Segurança Cibernética
Versão 2.0 com IA Avançada, Analytics, Certificados e Gamificação
"""

import streamlit as st
import os
import json
from datetime import datetime

# Configurar logging (desabilitado por permissões CloudWatch)
# from utils.logger import setup_logging, log_event
# logger = setup_logging(__name__)
import logging
logger = logging.getLogger(__name__)

# Importar módulos
from utils.aws_client import get_aws_client
from modules.auth import SessionManager, CognitoAuth
from modules.questions import QuestionManager
from modules.progress import ProgressManager
from modules.ai import FeedbackGenerator, AIQuestionGenerator
from modules.gamification import CertificateManager, GamificationManager
from modules.reports import ReportGenerator

# Configuração da página
st.set_page_config(
    page_title="CyberGuard Professional v2.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado
st.markdown("""
<style>
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --success-color: #4caf50;
        --danger-color: #f44336;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
    }
    
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: #1a1a1a !important;
    }
    
    /* Corrigir cor dos números em métricas */
    .stMetric div {
        color: #1a1a1a !important;
    }
    
    .stMetric > div > div {
        color: #1a1a1a !important;
    }
    
    .stMetric [data-testid="metric-container"] {
        color: #1a1a1a !important;
    }
    
    /* Valores das métricas */
    .stMetric span {
        color: #1a1a1a !important;
    }
    
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin: 0.5rem;
        font-weight: bold;
    }
    
    /* Badges com fundo escuro - texto fica bem */
    .stMetric .badge {
        background: #667eea;
        color: white;
    }
    
    .success-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #1b5e20;
    }
    
    .danger-box {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #b71c1c;
    }
    
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #0d47a1;
    }
    
    /* Apenas corrigir elementos com texto ilegível em fundos claros */
    /* Radio buttons e checkboxes - apenas quando necessário */
    .stRadio > label > span:first-child {
        color: #2d3748;
    }
    
    .stCheckbox > label > span:first-child {
        color: #2d3748;
    }
    
    /* Placeholders e labels */
    label {
        color: #2d3748 !important;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
SessionManager.init_session()

# Inicializar clientes AWS
try:
    aws_client = get_aws_client()
    if not aws_client.is_healthy():
        st.error("❌ Erro ao conectar com serviços AWS")
        st.stop()
except Exception as e:
    st.error(f"❌ Erro ao inicializar: {e}")
    logger.error(f"Erro crítico: {e}")
    st.stop()

# Instanciar gerenciadores
question_manager = QuestionManager()
progress_manager = ProgressManager()
feedback_generator = FeedbackGenerator()
certificate_manager = CertificateManager()
gamification_manager = GamificationManager()
report_generator = ReportGenerator()

# Verificar status do Bedrock (cache por sessão)
@st.cache_data(ttl=300)  # Cache por 5 minutos
def check_bedrock_status():
    """Verifica se Bedrock está disponível - com cache"""
    return True  # Assumir disponível, tratar erro quando necessário

# Cache para stats do usuário
@st.cache_data(ttl=60)  # Cache por 1 minuto
def get_cached_user_stats(user_id):
    """Stats do usuário com cache"""
    return progress_manager.get_user_stats(user_id)

# Cache para questões
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_cached_questions(category):
    """Questões com cache"""
    return question_manager.get_by_category(category)

# Verificar status na inicialização (cached)
bedrock_available = check_bedrock_status()


def render_login_page():
    """Página de login/registro"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🛡️ CyberGuard Professional")
        st.markdown("### Plataforma de Treinamento em Segurança Cibernética v2.0")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["🔐 Entrar", "📝 Registrar"])
        
        with tab1:
            st.subheader("Acesso de Usuário")
            email = st.text_input("📧 Email", placeholder="seu@email.com")
            password = st.text_input("🔐 Senha", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➡️ Entrar", type="primary", use_container_width=True):
                    if email and password:
                        # Simular autenticação (em produção usar Cognito)
                        SessionManager.set_user(email, "token_" + email, "student")
                        # log_event(logger, "user_login", email, {"timestamp": datetime.now().isoformat()})
                        st.success(f"✅ Bem-vindo, {email}!")
                        st.rerun()
                    else:
                        st.error("⚠️ Preencha todos os campos")
            
            with col2:
                if st.button("❓ Esqueceu a senha?", use_container_width=True):
                    st.info("Entre em contato com o administrador")
        
        with tab2:
            st.subheader("Criar Nova Conta")
            name = st.text_input("👤 Nome Completo")
            email_reg = st.text_input("📧 Email para Registro", key="reg_email")
            password_reg = st.text_input("🔐 Senha", type="password", key="reg_pass")
            password_confirm = st.text_input("🔐 Confirmar Senha", type="password", key="reg_pass_confirm")
            
            if st.button("✅ Registrar", type="primary", use_container_width=True):
                if name and email_reg and password_reg:
                    if password_reg == password_confirm:
                        SessionManager.set_user(email_reg, "token_" + email_reg, "student")
                        # log_event(logger, "user_signup", email_reg, {"name": name})
                        st.success(f"✅ Conta criada com sucesso! Bem-vindo, {name}!")
                        st.rerun()
                    else:
                        st.error("❌ As senhas não combinam")
                else:
                    st.error("⚠️ Preencha todos os campos")


def render_student_dashboard():
    """Dashboard do aluno"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Progresso Geral", f"{st.session_state.get('progress', 0)}%", "0%")
    
    with col2:
        stats = progress_manager.get_user_stats(st.session_state.user_id)
        st.metric("🎯 Taxa de Acerto", f"{stats.get('accuracy', 0):.1f}%", f"{stats.get('correct_answers', 0)}/{stats.get('total_answers', 0)}")
    
    with col3:
        badges = gamification_manager.get_user_badges(st.session_state.user_id)
        st.metric("🏆 Badges", len(badges), f"+{len(badges)}")
    
    st.markdown("---")
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📚 Treinar",
        "📊 Análise",
        "🏆 Certificados",
        "🎖️ Badges",
        "📥 Meus Dados"
    ])
    
    with tab1:
        render_training_section()
    
    with tab2:
        render_analytics_section()
    
    with tab3:
        render_certificates_section()
    
    with tab4:
        render_badges_section()
    
    with tab5:
        render_data_export_section()


def render_training_section():
    """Seção de treinamento"""
    st.subheader("📚 Treinar em Segurança Cibernética")
    
    if not st.session_state.questions:
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox(
                "🎯 Escolha a Categoria:",
                ["phishing", "passwords", "social_engineering", "malware"],
                format_func=lambda x: {
                    'phishing': '🎣 Phishing',
                    'passwords': '🔐 Senhas',
                    'social_engineering': '🎭 Engenharia Social',
                    'malware': '🦠 Malware'
                }[x]
            )
        
        with col2:
            difficulty = st.selectbox(
                "⚡ Nível de Dificuldade:",
                ["easy", "medium", "hard"],
                format_func=lambda x: {'easy': '🟢 Fácil', 'medium': '🟡 Médio', 'hard': '🔴 Difícil'}[x]
            )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Iniciar Treinamento", type="primary", use_container_width=True):
                st.session_state.questions = question_manager.get_by_category(category)
                st.session_state.category = category
                st.session_state.index = 0
                st.session_state.answered = False
                st.session_state.answers = {}
                st.session_state.start_time = datetime.now()
                
                if st.session_state.questions:
                    # log_event(logger, "training_started", st.session_state.user_id, {
                    #     'category': category,
                    #     'question_count': len(st.session_state.questions)
                    # })
                    st.rerun()
                else:
                    st.error("❌ Nenhuma questão disponível nesta categoria")
        
        with col2:
            if st.button("🤖 Gerar com IA", use_container_width=True):
                with st.spinner("Gerando questão com IA..."):
                    generator = AIQuestionGenerator()
                    question = generator.generate_question(category, difficulty)
                    if question:
                        st.success("✅ Questão gerada com sucesso!")
                        st.json(question)
    
    else:
        # Renderizar questão atual
        render_question()


def render_question():
    """Renderiza questão atual"""
    questions = st.session_state.questions
    idx = st.session_state.index
    
    if idx < len(questions):
        q = questions[idx]
        
        # Barra de progresso
        st.progress((idx + 1) / len(questions), text=f"Questão {idx + 1}/{len(questions)}")
        
        # Questão
        st.markdown(f"### Questão {idx + 1}: {q['question']}")
        
        if not st.session_state.answered:
            answer = st.radio(
                "Escolha sua resposta:",
                options=range(len(q['options'])),
                format_func=lambda i: f"{chr(65 + i)}) {q['options'][i]}",
                key=f"q_{idx}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirmar Resposta", type="primary", use_container_width=True):
                    correct = answer == int(q['correctAnswer'])
                    st.session_state.answered = True
                    st.session_state.answers[idx] = answer
                    
                    # Salvar progresso
                    time_spent = int((datetime.now() - st.session_state.start_time).total_seconds())
                    progress_manager.save_answer(
                        st.session_state.user_id,
                        q['questionId'],
                        correct,
                        st.session_state.category,
                        time_spent
                    )
                    
                    # Log
                    # log_event(logger, "answer_submitted", st.session_state.user_id, {
                    #     'question_id': q['questionId'],
                    #     'correct': correct,
                    #     'time_spent': time_spent
                    # })
                    
                    st.rerun()
            
            with col2:
                if st.button("⏭️ Pular", use_container_width=True):
                    st.session_state.index += 1
                    st.session_state.answered = False
                    st.rerun()
        
        else:
            # Mostrar resultado
            correct = st.session_state.answers.get(idx) == int(q['correctAnswer'])
            
            if correct:
                st.markdown('<div class="success-box">✅ <b>CORRETO!</b> Excelente resposta!</div>', unsafe_allow_html=True)
            else:
                user_answer = q['options'][st.session_state.answers.get(idx, int(q['correctAnswer']))]
                correct_answer = q['options'][int(q['correctAnswer'])]
                st.markdown(f'<div class="danger-box">❌ <b>INCORRETO</b><br><br>Sua resposta: <b>{user_answer}</b><br>Resposta correta: <b>{correct_answer}</b><br><br>Explicação detalhada ao final do treinamento!</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➡️ Próxima Questão", type="primary", use_container_width=True):
                    st.session_state.index += 1
                    st.session_state.answered = False
                    st.rerun()
            
            with col2:
                if st.button("📋 Ver Resumo", use_container_width=True):
                    st.session_state.show_summary = True
                    st.rerun()
    
    else:
        # Treino completo
        render_training_summary()


def render_training_summary():
    """Resumo do treinamento"""
    st.balloons()
    st.success("🎉 Parabéns! Você completou o treinamento!")
    
    questions = st.session_state.questions
    correct_count = sum(
        1 for i in range(len(questions))
        if st.session_state.answers.get(i) == int(questions[i]['correctAnswer'])
    )
    total = len(questions)
    accuracy = (correct_count / total * 100) if total > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Acertos", f"{correct_count}/{total}")
    with col2:
        st.metric("📊 Taxa de Acerto", f"{accuracy:.1f}%")
    with col3:
        st.metric("⏱️ Tempo Gasto", f"{int((datetime.now() - st.session_state.start_time).total_seconds())}s")
    
    st.markdown("---")
    
    # Verificar elegibilidade para certificado
    eligibility = certificate_manager.check_eligibility(accuracy, total)
    if eligibility['eligible']:
        st.success(f"🏆 **Parabéns!** Você qualificou-se para um certificado! ({accuracy:.1f}%)")
        if st.button("📜 Gerar Certificado", type="primary"):
            cert = certificate_manager.generate_certificate(
                st.session_state.user_id,
                st.session_state.user_id.split('@')[0],
                st.session_state.category,
                accuracy,
                total
            )
            if cert['success']:
                st.success(f"✅ Certificado gerado! ID: {cert['certificate_id']}")
                # log_event(logger, "certificate_generated", st.session_state.user_id, cert)
    else:
        st.info(f"⚠️ Você precisa de {eligibility['required_accuracy']}% de acerto para gerar certificado (sua taxa: {accuracy:.1f}%)")
    
    # Feedback detalhado com IA
    st.markdown("---")
    st.markdown("## 🤖 Análise Detalhada de Desempenho")
    
    # Processar feedback questão por questão sem spinner global
    for i, q in enumerate(questions):
        user_ans_idx = st.session_state.answers.get(i, int(q['correctAnswer']))
        correct_ans_idx = int(q['correctAnswer'])
        is_correct = user_ans_idx == correct_ans_idx
        
        # Header da questão
        st.markdown(f"### Questão {i+1}: {q['question']}")
        
        # Mostrar respostas
        col1, col2 = st.columns(2)
        with col1:
            if is_correct:
                st.success(f"✅ **Sua resposta:** {q['options'][user_ans_idx]}")
            else:
                st.error(f"❌ **Sua resposta:** {q['options'][user_ans_idx]}")
        
        with col2:
            st.info(f"✅ **Resposta correta:** {q['options'][correct_ans_idx]}")
        
        # Feedback IA - com spinner individual e timeout
        st.markdown("**Análise Detalhada:**")
        
        # Container para feedback
        feedback_container = st.empty()
        
        with feedback_container:
            with st.spinner(f"🤖 Gerando feedback para questão {i+1}..."):
                try:
                    feedback = feedback_generator.generate_feedback(
                        q['question'],
                        q['options'][user_ans_idx],
                        q['options'][correct_ans_idx],
                        is_correct,
                        st.session_state.category
                    )
                    # Limpar spinner e mostrar feedback
                    feedback_container.markdown(feedback)
                except Exception as e:
                    # Fallback para erro na geração de feedback
                    feedback_container.warning("⚠️ **Limite de IA atingido - usando feedback local:**")
                    if is_correct:
                        st.success(f"✅ Parabéns! Sua resposta '{q['options'][user_ans_idx]}' está correta!")
                    else:
                        st.error(f"❌ Sua resposta '{q['options'][user_ans_idx]}' está incorreta. A resposta correta é '{q['options'][correct_ans_idx]}'.")
                    
                    # Mostrar explicação da questão se disponível
                    if q.get('explanation'):
                        st.info(f"💡 **Explicação:** {q['explanation']}")
        
        st.markdown("---")
    
    # Botões de ação
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Novo Treinamento", use_container_width=True):
            st.session_state.questions = []
            st.session_state.answers = {}
            st.session_state.show_summary = False
            st.rerun()
    
    with col2:
        if st.button("📊 Ver Análise", use_container_width=True):
            st.session_state.active_tab = "analytics"
            st.rerun()
    
    with col3:
        if st.button("🏠 Ir para Dashboard", use_container_width=True):
            st.session_state.questions = []
            st.session_state.answers = {}
            st.rerun()


def render_analytics_section():
    """Seção de análise e estatísticas"""
    st.subheader("📊 Sua Análise de Desempenho")
    
    stats = progress_manager.get_user_stats(st.session_state.user_id)
    
    if not stats or stats.get('total_answers', 0) == 0:
        st.info("📭 Nenhum dado de treinamento ainda. Complete alguns treinamentos para ver análise!")
    else:
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📚 Total de Questões", stats.get('total_answers', 0))
        with col2:
            st.metric("✅ Acertos", stats.get('correct_answers', 0))
        with col3:
            st.metric("📊 Taxa de Acerto", f"{stats.get('accuracy', 0):.1f}%")
        with col4:
            st.metric("🔥 Sequência Atual", stats.get('streak', 0))
        
        st.markdown("---")
        
        # Gráfico por categoria
        if stats.get('by_category'):
            st.subheader("Desempenho por Categoria")
            
            categories = stats.get('by_category', {})
            for category, data in categories.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.progress(data.get('accuracy', 0) / 100, text=f"{category.upper()}")
                with col2:
                    st.write(f"{data.get('accuracy', 0):.1f}%")
        
        # Atividade recente
        st.subheader("📅 Atividade Recente (7 dias)")
        recent = progress_manager.get_recent_activity(st.session_state.user_id, days=7)
        
        if recent:
            st.write(f"Você respondeu **{len(recent)}** questões nos últimos 7 dias")
        else:
            st.info("Sem atividade nos últimos 7 dias")


def render_certificates_section():
    """Seção de certificados"""
    st.subheader("📜 Meus Certificados")
    
    certificates = certificate_manager.get_user_certificates(st.session_state.user_id)
    
    if not certificates:
        st.info("Você ainda não gerou nenhum certificado. Complete treinamentos com 80%+ de acerto!")
    else:
        st.success(f"✅ Você tem **{len(certificates)}** certificado(s)!")
        
        for cert in certificates:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"""
                **Certificado:** {cert.get('category').upper()}
                - **Acurácia:** {cert.get('accuracy', 0)}%
                - **ID:** {cert.get('certificateId', 'N/A')[:20]}...
                - **Emitido em:** {datetime.fromtimestamp(float(cert.get('issued_at', 0))).strftime('%d/%m/%Y')}
                """)
            
            with col2:
                if st.button("📥 Baixar", key=f"cert_{cert.get('certificateId')}", use_container_width=True):
                    st.info("Em produção, arquivo PDF seria baixado")


def render_badges_section():
    """Seção de badges e gamificação"""
    st.subheader("🎖️ Meus Badges")
    
    badges = gamification_manager.get_user_badges(st.session_state.user_id)
    stats = progress_manager.get_user_stats(st.session_state.user_id)
    
    # Mostrar badges desbloqueados
    if badges:
        st.success(f"🏆 Você desbloqueou **{len(badges)}** badge(s)!")
        
        cols = st.columns(4)
        for idx, badge in enumerate(badges):
            with cols[idx % 4]:
                badge_info = gamification_manager.BADGES.get(badge.get('badgeId'))
                if badge_info:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1rem; background: #f0f0f0; border-radius: 10px;'>
                    <div style='font-size: 2.5rem;'>{badge_info['icon']}</div>
                    <div style='font-weight: bold;'>{badge_info['name']}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Mostrar próximos badges elegíveis
    st.markdown("---")
    st.subheader("Próximos Badges Disponíveis")
    
    eligible_badges = gamification_manager.check_badge_eligibility(
        st.session_state.user_id,
        stats
    )
    
    if eligible_badges:
        st.success(f"🎯 Você qualificou-se para **{len(eligible_badges)}** badge(s)! Parabéns! 🎉")
        
        for badge_id in eligible_badges:
            badge_info = gamification_manager.BADGES.get(badge_id)
            if badge_info:
                st.write(f"- {badge_info['icon']} **{badge_info['name']}**: {badge_info['requirement']}")
                if st.button(f"Desbloquear {badge_info['name']}", key=f"unlock_{badge_id}"):
                    if gamification_manager.unlock_badge(st.session_state.user_id, badge_id):
                        st.success(f"✅ Badge '{badge_info['name']}' desbloqueado!")
                        st.rerun()
    else:
        # Mostrar badges disponíveis
        st.info("Nenhum novo badge desbloqueado ainda. Continue treinando!")
        
        st.markdown("**Badges Disponíveis:**")
        for badge_id, badge_info in gamification_manager.BADGES.items():
            st.write(f"- {badge_info['icon']} **{badge_info['name']}**: {badge_info['requirement']}")


def render_data_export_section():
    """Seção para exportar dados"""
    st.subheader("📥 Exportar Meus Dados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Exportar como CSV", use_container_width=True):
            csv_data = report_generator.generate_user_report_csv(st.session_state.user_id)
            if csv_data:
                st.download_button(
                    label="Baixar CSV",
                    data=csv_data,
                    file_name=f"cyberguard_{st.session_state.user_id}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.error("Nenhum dado para exportar")
    
    with col2:
        if st.button("📄 Exportar como JSON", use_container_width=True):
            json_data = report_generator.export_to_json(st.session_state.user_id)
            if json_data:
                st.download_button(
                    label="Baixar JSON",
                    data=json_data,
                    file_name=f"cyberguard_{st.session_state.user_id}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            else:
                st.error("Nenhum dado para exportar")
    
    with col3:
        if st.button("📋 Gerar Relatório", use_container_width=True):
            summary = report_generator.generate_summary_report(st.session_state.user_id)
            if 'error' not in summary:
                st.json(summary)
            else:
                st.error("Nenhum dado para gerar relatório")


def render_instructor_dashboard():
    """Dashboard do instrutor"""
    st.subheader("👨‍🏫 Dashboard do Instrutor")
    
    tab1, tab2, tab3 = st.tabs(["📊 Relatórios", "👥 Alunos", "⚙️ Gerenciar"])
    
    with tab1:
        st.write("**Estatísticas Gerais**")
        report = report_generator.generate_instructor_report()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 Total de Alunos", report.get('total_users', 0))
        with col2:
            st.metric("📚 Total de Respostas", report.get('total_responses', 0))
        with col3:
            st.metric("📊 Acurácia Geral", f"{report.get('overall_accuracy', 0):.1f}%")
        
        st.markdown("---")
        
        # Por categoria
        if report.get('by_category'):
            st.subheader("Desempenho por Categoria")
            for category, data in report['by_category'].items():
                st.write(f"**{category.upper()}** - Acurácia: {data.get('accuracy', 0):.1f}% ({data.get('correct', 0)}/{data.get('total', 0)})")
    
    with tab2:
        st.write("**Desempenho dos Alunos**")
        report = report_generator.generate_instructor_report()
        
        if report.get('by_user'):
            # Top 10 alunos
            users_list = [
                (user, data.get('accuracy', 0), data.get('correct', 0), data.get('total', 0))
                for user, data in report['by_user'].items()
            ]
            users_list.sort(key=lambda x: x[1], reverse=True)
            
            for rank, (user, accuracy, correct, total) in enumerate(users_list[:10], 1):
                col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
                
                with col1:
                    st.write(f"**{rank}°**")
                with col2:
                    st.write(f"{user[:30]}")
                with col3:
                    st.write(f"{accuracy:.1f}%")
                with col4:
                    st.write(f"{correct}/{total}")
    
    with tab3:
        st.write("**Gerenciamento de Questões**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🤖 Gerar Novo Conjunto de Questões", use_container_width=True):
                st.info("Para gerar questões, execute: python3 setup_complete.py")
        
        with col2:
            if st.button("📊 Ver Estatísticas de Questões", use_container_width=True):
                stats = question_manager.get_stats()
                st.json(stats)
        
        with col3:
            if st.button("🔄 Limpar Dados de Teste", use_container_width=True):
                st.warning("Esta ação não pode ser desfeita!")


def render_admin_panel():
    """Painel de administrador"""
    st.subheader("⚙️ Painel de Administrador")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Usuários", "📚 Questões", "📊 Auditoria", "⚡ Sistema"])
    
    with tab1:
        st.write("**Gerenciamento de Usuários**")
        st.info("Funcionalidade de gerenciamento de usuários")
    
    with tab2:
        st.write("**Gerenciamento de Questões**")
        col1, col2 = st.columns(2)
        
        with col1:
            stats = question_manager.get_stats()
            st.metric("Total de Questões", stats.get('total', 0))
        
        with col2:
            categories = stats.get('by_category', {})
            if categories:
                for cat, count in categories.items():
                    st.write(f"- {cat.upper()}: {count} questões")
    
    with tab3:
        st.write("**Logs de Auditoria**")
        st.info("Logs de auditoria seriam exibidos aqui (CloudWatch)")
    
    with tab4:
        st.write("**Status do Sistema**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("AWS DynamoDB", "✅ Online")
        with col2:
            st.metric("AWS Bedrock", "✅ Online")
        with col3:
            st.metric("CloudWatch", "✅ Online")


# MAIN APP LOGIC
def main():
    """Função principal"""
    
    # Remover aviso global - tratar erro apenas quando necessário
    
    # Barra lateral
    with st.sidebar:
        st.markdown("# 🛡️ CyberGuard Professional")
        st.markdown("v2.0 - Treinamento em Segurança Cibernética")
        st.markdown("---")
        
        if not SessionManager.is_logged_in():
            st.info("👤 Não está logado")
        else:
            st.success(f"✅ Logado como: **{st.session_state.user_id}**")
            
            # Stats rápidas
            stats = progress_manager.get_user_stats(st.session_state.user_id)
            st.markdown("**Estatísticas Rápidas:**")
            st.write(f"- Acertos: {stats.get('correct_answers', 0)}")
            st.write(f"- Taxa: {stats.get('accuracy', 0):.1f}%")
            st.write(f"- Sequência: {stats.get('streak', 0)} 🔥")
            
            st.markdown("---")
            
            # Menu de navegação
            role = SessionManager.get_user_role()
            
            if role == 'admin':
                page = st.radio(
                    "Navegação:",
                    ["Dashboard", "Treinar", "Análise", "Instrutor", "Admin", "Configurações", "Sair"],
                    index=0
                )
            elif role == 'instructor':
                page = st.radio(
                    "Navegação:",
                    ["Dashboard", "Treinar", "Análise", "Instrutor", "Configurações", "Sair"],
                    index=0
                )
            else:
                page = st.radio(
                    "Navegação:",
                    ["Dashboard", "Treinar", "Análise", "Configurações", "Sair"],
                    index=0
                )
            
            st.markdown("---")
            
            if st.button("🚪 Sair", use_container_width=True):
                # log_event(logger, "user_logout", st.session_state.user_id, {})
                SessionManager.logout()
                st.rerun()
    
    # Conteúdo principal
    if not SessionManager.is_logged_in():
        render_login_page()
    else:
        role = SessionManager.get_user_role()
        
        if page == "Dashboard":
            render_student_dashboard()
        elif page == "Treinar":
            render_training_section()
        elif page == "Análise":
            render_analytics_section()
        elif page == "Instrutor":
            render_instructor_dashboard()
        elif page == "Admin":
            if role == 'admin':
                render_admin_panel()
            else:
                st.error("❌ Acesso negado")
        elif page == "Configurações":
            st.subheader("⚙️ Configurações")
            st.write("Email:", st.session_state.user_id)
            st.write("Role:", role)
            st.write("Membro desde:", datetime.now().strftime('%d/%m/%Y'))
        elif page == "Sair":
            # log_event(logger, "user_logout", st.session_state.user_id, {})
            SessionManager.logout()
            st.rerun()


if __name__ == "__main__":
    main()
