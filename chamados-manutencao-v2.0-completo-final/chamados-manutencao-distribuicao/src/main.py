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
from src.models.chamado import Chamado
from src.models.turno import Turno
from src.models.unidade import Unidade
from src.models.local_apontamento import LocalApontamento
from src.models.nao_conformidade import NaoConformidade
from src.models.status_chamado import StatusChamado
from src.models.perfil import Perfil
from src.models.historico_chamado import HistoricoChamado
from src.models.contato_notificacao import ContatoNotificacao
from src.models.historico_notificacoes import HistoricoNotificacoes

# Importar blueprints
from src.routes.chamado import chamado_bp
from src.routes.admin import admin_bp
from src.routes.auth import admin_auth
from src.routes.notificacao import notificacao_bp

def create_app():
    app = Flask(__name__, 
                static_folder=os.path.join(os.path.dirname(__file__), 'static'),
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    
    # Configurar aplicação
    app.config.from_object(Config)
    Config.init_app(app)
    
    # Habilitar CORS
    CORS(app)
    
    # Inicializar banco de dados
    db.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(chamado_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(admin_auth)
    app.register_blueprint(notificacao_bp)
    
    # Criar tabelas do banco
    with app.app_context():
        db.create_all()
        
        # Criar dados iniciais se não existirem
        if not Turno.query.first():
            turnos = [
                Turno(nome='Manhã', descricao='Turno da manhã (06:00 - 14:00)'),
                Turno(nome='Tarde', descricao='Turno da tarde (14:00 - 22:00)'),
                Turno(nome='Noite', descricao='Turno da noite (22:00 - 06:00)')
            ]
            for turno in turnos:
                db.session.add(turno)
        
        if not Unidade.query.first():
            unidades = [
                Unidade(nome='Unidade A', descricao='Unidade de produção A'),
                Unidade(nome='Unidade B', descricao='Unidade de produção B'),
                Unidade(nome='Escritório', descricao='Área administrativa')
            ]
            for unidade in unidades:
                db.session.add(unidade)
        
        if not StatusChamado.query.first():
            status = [
                StatusChamado(nome='Aberto', descricao='Chamado recém criado'),
                StatusChamado(nome='Em Andamento', descricao='Chamado sendo executado'),
                StatusChamado(nome='Aguardando', descricao='Aguardando peças/informações'),
                StatusChamado(nome='Concluído', descricao='Chamado finalizado'),
                StatusChamado(nome='Cancelado', descricao='Chamado cancelado')
            ]
            for st in status:
                db.session.add(st)
        
        if not LocalApontamento.query.first():
            locais = [
                LocalApontamento(nome='Linha 1', descricao='Linha de produção 1'),
                LocalApontamento(nome='Linha 2', descricao='Linha de produção 2'),
                LocalApontamento(nome='Estoque', descricao='Área de estoque'),
                LocalApontamento(nome='Manutenção', descricao='Oficina de manutenção')
            ]
            for local in locais:
                db.session.add(local)
        
        if not NaoConformidade.query.first():
            ncs = [
                NaoConformidade(nome='Equipamento Parado', descricao='Equipamento fora de operação'),
                NaoConformidade(nome='Vazamento', descricao='Vazamento de fluidos'),
                NaoConformidade(nome='Ruído Anormal', descricao='Ruído fora do padrão'),
                NaoConformidade(nome='Superaquecimento', descricao='Temperatura acima do normal')
            ]
            for nc in ncs:
                db.session.add(nc)
        
        if not Perfil.query.first():
            perfis = [
                Perfil(nome='Operador', descricao='Operador de produção'),
                Perfil(nome='Técnico', descricao='Técnico de manutenção'),
                Perfil(nome='Supervisor', descricao='Supervisor de área'),
                Perfil(nome='Gerente', descricao='Gerente de produção')
            ]
            for perfil in perfis:
                db.session.add(perfil)
        
        db.session.commit()
    
    # Rota principal
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'version': '2.0'}), 200
    
    return app

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)

