# src/__init__.py
# ===============================
# 1) IMPORTS E CONFIGURAÇÃO DO DB
# ===============================
from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from src.models import db
from src.config import Config

# ===============================
# 2) FACTORY DE APLICATIVO
# ===============================
def create_app():
    """Cria e configura a aplicação Flask."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # Carrega as configurações da classe Config
    app.config.from_object(Config)
    Config.init_app(app)

    # Inicializa o SQLAlchemy com a instância importada de src.models
    db.init_app(app)
    Migrate(app, db)

    # Importar modelos apenas se necessário (evitar redefinição)
    with app.app_context():
        from src.models.user import User
        from src.models.perfil import Perfil
        from src.models.chamado import Chamado
        from src.models.turno import Turno
        from src.models.unidade import Unidade
        from src.models.nao_conformidade import NaoConformidade
        from src.models.status_chamado import StatusChamado
        from src.models.contato_notificacao import ContatoNotificacaoManutencao
        from src.models.historico_chamado import HistoricoChamado
        from src.models.historico_notificacoes import HistoricoNotificacoes
        from src.models.local_apontamento import LocalApontamento

    # ===============================
    # 3) REGISTRO DOS BLUEPRINTS
    # ===============================
    from src.routes.auth import admin_auth_bp
    app.register_blueprint(admin_auth_bp)

    from src.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from src.routes.chamado import chamado_bp
    app.register_blueprint(chamado_bp, url_prefix='/chamados')

    # ===============================
    # 4) ROTA RAIZ (redirect para chamados)
    # ===============================
    @app.route('/')
    def root():
        return redirect(url_for('chamado.index'))
    # ===============================
    # 5) HEALTHCHECK (200 OK puro)
    # ===============================
    @app.route('/health', methods=['GET'])
    def health_check():
        return 'OK', 200
    
    return app