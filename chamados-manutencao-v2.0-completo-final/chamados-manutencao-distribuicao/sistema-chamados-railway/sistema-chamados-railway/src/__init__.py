from flask import Flask # type: ignore
def create_app():
     app = Flask(__name__, template_folder="templates", static_folder="static")
     app.secret_key = "Luiza@1980@follow"  # altere para algo forte em produção

     # importe e registre seus blueprints
     from src.routes.admin_auth import admin_auth
from src.admin          import admin_bp
from src.routes.chamado import chamado_bp

app.register_blueprint(admin_auth)    # /admin/login      :contentReference[oaicite:0]{index=0}
app.register_blueprint(admin_bp)      # /admin            
app.register_blueprint(chamado_bp)    # /chamados/...

return app
