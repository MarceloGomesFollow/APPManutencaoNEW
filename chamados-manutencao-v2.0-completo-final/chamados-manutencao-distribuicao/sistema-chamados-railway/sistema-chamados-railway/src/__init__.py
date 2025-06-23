# src/__init__.py

# ===============================
# 1) IMPORTS E INSTÂNCIA DO DB
# ===============================
from flask import Flask
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

    # Carrega as configurações da sua classe Config (ex: SECRET_KEY, DATABASE_URL, etc.)
    # Você pode definir uma classe em src/config.py:
    #   class Config:
    #       SECRET_KEY = os.getenv('SECRET_KEY')
    #       SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    app.config.from_object('src.config.Config')

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
    # Caso admin_bp não tenha url_prefix, defina aqui:
    # app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(admin_bp)

    # 3.3) Rotas de chamados (cliente e supervisor)
    from src.routes.chamado import chamado_bp
    app.register_blueprint(chamado_bp, url_prefix='/chamados')

    return app
