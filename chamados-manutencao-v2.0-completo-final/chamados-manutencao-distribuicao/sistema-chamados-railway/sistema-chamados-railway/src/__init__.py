from flask import Flask

def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )
    app.config.from_object('src.config.Config')  # ou defina SECRET_KEY aqui

    # 1) Login/Logout de admin e supervisor (em src/routes/auth.py)
    from src.routes.auth   import admin_auth_bp
    # 2) Painel + CRUDs administrativos (em src/routes/admin.py)
    from src.routes.admin  import admin_bp
    # 3) Chamados (em src/routes/chamado.py)
    from src.routes.chamado import chamado_bp

    # Registre os blueprints **dentro** do create_app():
    app.register_blueprint(admin_auth_bp)             # rotas: /admin-login, /supervisor-login
    app.register_blueprint(admin_bp,    url_prefix='/admin')   # rotas: /admin/, /admin/turnos, etc.
    app.register_blueprint(chamado_bp,  url_prefix='/chamados')# rotas: /chamados/…

    return app
