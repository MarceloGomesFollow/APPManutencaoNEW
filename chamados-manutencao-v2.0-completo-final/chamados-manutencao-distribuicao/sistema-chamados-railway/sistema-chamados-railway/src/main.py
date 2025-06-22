import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import CORS
from src.config import Config
from src.models.user import db

# Importar apenas modelos que existem
try:
    from src.models.chamado import Chamado
except ImportError:
    Chamado = None

try:
    from src.models.turno import Turno
except ImportError:
    Turno = None

try:
    from src.models.unidade import Unidade
except ImportError:
    Unidade = None

try:
    from src.models.local_apontamento import LocalApontamento
except ImportError:
    LocalApontamento = None

try:
    from src.models.nao_conformidade import NaoConformidade
except ImportError:
    NaoConformidade = None

try:
    from src.models.status_chamado import StatusChamado
except ImportError:
    StatusChamado = None

try:
    from src.models.perfil import Perfil
except ImportError:
    Perfil = None

try:
    from src.models.historico_chamado import HistoricoChamado
except ImportError:
    HistoricoChamado = None

try:
    from src.models.contato_notificacao import ContatoNotificacao
except ImportError:
    ContatoNotificacao = None

try:
    from src.models.historico_notificacoes import HistoricoNotificacoes
except ImportError:
    HistoricoNotificacoes = None

# Importar blueprints com tratamento de erro
try:
    from src.routes.chamado import chamado_bp
except ImportError:
    chamado_bp = None

try:
    from src.routes.admin import admin_bp
except ImportError:
    admin_bp = None

try:
    from src.routes.auth import admin_auth
except ImportError:
    admin_auth = None

try:
    from src.routes.notificacao import notificacao_bp
except ImportError:
    notificacao_bp = None

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configurar CORS
    CORS(app)
    
    # Inicializar banco de dados
    db.init_app(app)
    
    # Registrar blueprints apenas se existirem
    if chamado_bp:
        app.register_blueprint(chamado_bp)
    
    if admin_bp:
        app.register_blueprint(admin_bp, url_prefix='/admin')
    
    if admin_auth:
        app.register_blueprint(admin_auth)
    
    if notificacao_bp:
        app.register_blueprint(notificacao_bp, url_prefix='/notificacoes')
    
    # Rota básica para teste
    @app.route('/')
    def index():
        return render_template('index.html') if os.path.exists('src/templates/index.html') else "Sistema de Chamados - Em funcionamento!"
    
    # Rota de saúde para Railway
    @app.route('/health')
    def health():
        return {"status": "ok", "message": "Sistema funcionando"}
    
    # Criar tabelas se necessário
    with app.app_context():
        try:
            db.create_all()
            print("✅ Banco de dados inicializado")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar banco: {e}")
    
    return app

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

