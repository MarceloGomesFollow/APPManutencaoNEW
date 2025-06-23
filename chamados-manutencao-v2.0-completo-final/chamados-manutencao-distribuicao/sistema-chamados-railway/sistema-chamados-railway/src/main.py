import os
import sys
from flask_migrate import upgrade

# Ajuste o sys.path para incluir o diretório raiz do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importa create_app de forma absoluta
from src import create_app

app = create_app()

with app.app_context():
    # Aplica migrações antes de inserir dados
    try:
        upgrade()  # Executa a migração mais recente
        print("Migrações aplicadas com sucesso")
    except Exception as e:
        print(f"Erro ao aplicar migrações: {e}")
        raise  # Para depuração, falha se a migração falhar

    # Insere dados iniciais apenas se não existirem
    def inserir_dados_iniciais(db):
        from src.models.perfil import Perfil
        from src.models.status_chamado import StatusChamado
        from src.models.turno import Turno
        from src.models.unidade import Unidade
        from src.models.nao_conformidade import NaoConformidade
        from src.models.local_apontamento import LocalApontamento
        
        if not Perfil.query.first():
            perfis = [
                Perfil(nome='Administrador', descricao='Acesso total ao sistema'),
                Perfil(nome='Manutenção', descricao='Técnicos de manutenção'),
                Perfil(nome='Requisitante', descricao='Usuários que abrem chamados')
            ]
            for perfil in perfis:
                db.session.add(perfil)
        
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
        
        if not Turno.query.first():
            turnos = [
                Turno(nome='Manhã', descricao='8:00 às 12:00'),
                Turno(nome='Tarde', descricao='13:00 às 17:00'),
                Turno(nome='Noite', descricao='18:00 às 22:00'),
                Turno(nome='Madrugada', descricao='23:00 às 7:00')
            ]
            for turno in turnos:
                db.session.add(turno)
        
        if not Unidade.query.first():
            unidades = [
                Unidade(nome='Unidade A'),
                Unidade(nome='Unidade B'),
                Unidade(nome='Unidade C')
            ]
            for unidade in unidades:
                db.session.add(unidade)
        
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
            print("Dados iniciais inseridos com sucesso")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao inserir dados iniciais: {e}")

    # Chama a função de inserção de dados, passando o db
    inserir_dados_iniciais(db)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)