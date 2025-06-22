import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from src.models.user import db
from src.routes.user import user_bp
from src.routes.chamado import chamado_bp
from src.config import Config

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Carrega configurações
app.config.from_object(Config)
Config.init_app(app)

# Registra blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(chamado_bp)

# Registra blueprint de administração
from src.routes.admin import admin_bp
app.register_blueprint(admin_bp)

# Inicializa banco de dados
db.init_app(app)

def inserir_dados_iniciais():
    """Insere dados iniciais necessários para o funcionamento do sistema"""
    from src.models.perfil import Perfil
    from src.models.status_chamado import StatusChamado
    from src.models.turno import Turno
    from src.models.unidade import Unidade
    from src.models.nao_conformidade import NaoConformidade
    from src.models.local_apontamento import LocalApontamento
    
    # Inserir perfis padrão
    if not Perfil.query.first():
        perfis = [
            Perfil(nome='Administrador', descricao='Acesso total ao sistema'),
            Perfil(nome='Manutenção', descricao='Técnicos de manutenção'),
            Perfil(nome='Requisitante', descricao='Usuários que abrem chamados')
        ]
        for perfil in perfis:
            db.session.add(perfil)
    
    # Inserir status padrão
    if not StatusChamado.query.first():
        status_list = [
            StatusChamado(nome='Inicial', ordem=1),
            StatusChamado(nome='Em aberto', ordem=2),
            StatusChamado(nome='Em Andamento', ordem=3),
            StatusChamado(nome='Aguardando Material de Reparo', ordem=4),
            StatusChamado(nome='Concluído', ordem=5)
        ]
        for status in status_list:
            db.session.add(status)
    
    # Inserir dados de exemplo para turnos
    if not Turno.query.first():
        turnos = [
            Turno(nome='Manhã'),
            Turno(nome='Tarde'),
            Turno(nome='Noite'),
            Turno(nome='Madrugada')
        ]
        for turno in turnos:
            db.session.add(turno)
    
    # Inserir dados de exemplo para unidades
    if not Unidade.query.first():
        unidades = [
            Unidade(nome='Unidade A'),
            Unidade(nome='Unidade B'),
            Unidade(nome='Unidade C')
        ]
        for unidade in unidades:
            db.session.add(unidade)
    
    # Inserir dados de exemplo para não conformidades
    if not NaoConformidade.query.first():
        nao_conformidades = [
            NaoConformidade(nome='Equipamento com defeito'),
            NaoConformidade(nome='Vazamento'),
            NaoConformidade(nome='Problema elétrico'),
            NaoConformidade(nome='Limpeza necessária'),
            NaoConformidade(nome='Manutenção preventiva')
        ]
        for nc in nao_conformidades:
            db.session.add(nc)
    
    # Inserir dados de exemplo para locais de apontamento
    if not LocalApontamento.query.first():
        locais = [
            LocalApontamento(nome='Área de Produção'),
            LocalApontamento(nome='Escritório'),
            LocalApontamento(nome='Almoxarifado'),
            LocalApontamento(nome='Área Externa'),
            LocalApontamento(nome='Banheiros')
        ]
        for local in locais:
            db.session.add(local)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao inserir dados iniciais: {e}")

with app.app_context():
    # Importa todos os modelos
    from src.models.chamado import Chamado
    from src.models.turno import Turno
    from src.models.unidade import Unidade
    from src.models.nao_conformidade import NaoConformidade
    from src.models.local_apontamento import LocalApontamento
    from src.models.status_chamado import StatusChamado
    from src.models.perfil import Perfil
    from src.models.historico_chamado import HistoricoChamado
    from src.models.contato_notificacao import ContatoNotificacaoManutencao
    from src.models.historico_notificacoes import HistoricoNotificacoes
    
    # Cria todas as tabelas
    db.create_all()
    
    # Insere dados iniciais
    inserir_dados_iniciais()

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)
@app.route('/')
def index():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

