from flask import Flask

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = "Luiza@1980@follow"  # altere para algo forte em produção

    # importe e registre seus blueprints
    from src.routes.admin_auth import admin_auth
    from src.routes.chamado import chamado_bp

    app.register_blueprint(admin_auth)    # /admin/login
    app.register_blueprint(chamado_bp)    # /chamados/...

    return app
