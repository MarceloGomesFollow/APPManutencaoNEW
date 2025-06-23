# src/__init__.py
from flask import Flask  # type: ignore

def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )
    app.secret_key = "Luiza@1980@follow"  # em produção, use VAR de ambiente

    # importe e registre seus blueprints DENTRO do create_app
    from src.routes.admin_auth import admin_auth
    from src.admin          import admin_bp
    from src.routes.chamado import chamado_bp

    app.register_blueprint(admin_auth)    # /admin/login
    app.register_blueprint(admin_bp)      # /admin/…
    app.register_blueprint(chamado_bp)    # /chamados/…

    return app
