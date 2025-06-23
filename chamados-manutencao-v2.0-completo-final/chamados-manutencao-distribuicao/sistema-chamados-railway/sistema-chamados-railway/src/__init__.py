# src/__init__.py
# ===============================
# 1) IMPORTS E CONFIGURAÇÃO DO DB
# ===============================
from flask import Flask, redirect, url_for
# Importa a instância única de SQLAlchemy definida em src/models/__init__.py
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

    # (Opcional) Cria automaticamente as tabelas no banco ao subir a app
    with app.app_context():
        db.create_all()

    # ===============================
    # 3) REGISTRO DOS BLUEPRINTS
    # ===============================

    # 3.1) Rotas de autenticação (admin + supervisor)
    from src.routes.auth import admin_auth_bp
    app.register_blueprint(admin_auth_bp)  # /admin/login, /admin/logout, etc.

    # 3.2) CRUDs administrativos (turnos, unidades, etc.)
    from src.routes.admin import admin_bp
    app.register_blueprint(admin_bp)       # /admin/*

    # 3.3) Rotas de chamados (cliente e supervisor)
    from src.routes.chamado import chamado_bp
    app.register_blueprint(chamado_bp, url_prefix='/chamados')  # /chamados/*

    # ===============================
    # 4) ROTA RAIZ (redirect para chamados)
    # ===============================
    @app.route('/')
    def root():
        return redirect(url_for('chamado.index'))

    return app
