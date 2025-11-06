# app.py
from flask import Flask
from flask_login import LoginManager
import logging

# Configurações
from config import config
from models import Base, Usuario

# Import da sessão do banco DA RAIZ
from database import db_session, engine

# Blueprints
from blueprints.auth import auth_bp
from blueprints.main import main_bp
from blueprints.servicos import servicos_bp
from blueprints.api import api_bp
from blueprints.chat import chat_bp
from blueprints.pagamentos import pagamentos_bp
from blueprints.agendamentos import agendamentos_bp
from blueprints.avaliacoes import avaliacoes_bp
from blueprints.notificacoes import notificacoes_bp  # ✅ NOVO - Import do blueprint de notificações

from blueprints.admin import admin_bp
from blueprints.admin_tickets import admin_tickets_bp
from blueprints.user_tickets import tickets_bp



# Configuração de Logging
logging.basicConfig(level=logging.INFO)

def create_app():
    """Factory function para criar a aplicação"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.SECRET_KEY

    # ✅ CORRIGIDO: Criar tabelas apenas se não existirem
    Base.metadata.create_all(bind=engine, checkfirst=True)

    # Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db_session.query(Usuario).get(int(user_id))
        except Exception as e:
            print(f"Erro ao carregar usuário {user_id}: {str(e)}")
            return None

    # Registrar Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(servicos_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(pagamentos_bp)
    app.register_blueprint(agendamentos_bp)
    app.register_blueprint(avaliacoes_bp)
    app.register_blueprint(notificacoes_bp)
    app.register_blueprint(admin_tickets_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp)

    # ✅ ADD THIS: Context processor para disponibilizar 'now' em todos os templates
    from datetime import datetime
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Debug routes
    @app.route('/debug-routes')
    def debug_routes():
        """Debug: mostra todas as rotas registradas"""
        routes = []
        for rule in app.url_map.iter_rules():
            if 'static' not in rule.endpoint:
                routes.append(f"{rule.endpoint}: {rule.rule} {list(rule.methods)}")
        return '<br>'.join(sorted(routes))

    # Error handlers para mostrar erros reais
    @app.errorhandler(500)
    def internal_error(error):
        import traceback
        return f"""
        <h1>500 - Erro Interno</h1>
        <pre>{traceback.format_exc()}</pre>
        """, 500

    @app.errorhandler(404)
    def not_found(error):
        return f"""
        <h1>404 - Página não encontrada</h1>
        <p>{error}</p>
        """, 404

    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 ServiçosPro - SISTEMA COMPLETO!")
    print("📍 Acesse: http://localhost:5000")
    print("🔔 Sistema de Notificações ✅")
    print("📅 Agendamentos Inteligentes ✅")
    print("👥 Dashboard Prestador ✅")
    print("🔍 Debug rotas: http://localhost:5000/debug-routes")
    print("=" * 50)
    app.run(debug=config.DEBUG, host='0.0.0.0', port=5000)