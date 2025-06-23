# src/__init__.py

# ===============================
# 1) IMPORTS E INSTÂNCIA DO DB
# ===============================
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Cria a instância do SQLAlchemy — será inicializada em create_app()
db = SQLAlchemy()


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
    app.config.from_object('src.config.Config')
    # Se houver init_app na Config, chame-a
    try:
        from src.config import Config
        Config.init_app(app)
    except ImportError:
        pass

    # Inicializa o SQLAlchemy
    db.init_app(app)

    # (Opcional) Cria automaticamente as tabelas no banco ao subir a app
    with app.app_context():
        db.create_all()

    # ===============================
    # 3) REGISTRO DOS BLUEPRINTS
    # ===============================

    # 3.1) Rotas de autenticação (admin + supervisor)
    from src.routes.auth import admin_auth_bp
    # Blueprint já definido em auth.py com url_prefix='/admin'
    app.register_blueprint(admin_auth_bp)

    # 3.2) CRUDs administrativos (turnos, unidades, etc.)
    from src.routes.admin import admin_bp
    # Blueprint já definido com url_prefix='/admin'
    app.register_blueprint(admin_bp)

    # 3.3) Rotas de chamados (cliente e supervisor)
    from src.routes.chamado import chamado_bp
    app.register_blueprint(chamado_bp, url_prefix='/chamados')

    # ===============================
    # 4) ROTA RAIZ
    # ===============================
    @app.route('/')
    def index():
        """Redireciona a raiz para a página de chamados."""
        return redirect(url_for('chamado.index'))

    return app
