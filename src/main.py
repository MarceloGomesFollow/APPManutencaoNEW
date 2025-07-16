#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
src/main.py

Script de release: aplica migrações e insere dados iniciais.
Execute via: python -m src.main   (ou `python src/main.py` se preferir)
"""
import locale
import os
import sys
import time

from flask_migrate import upgrade
from flask import render_template
from src.models.chamado import Chamado


# ====== PYTHONPATH para execução direta ======
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
os.environ["TZ"] = "America/Sao_Paulo"
time.tzset()

# ====== Importação da Factory e DB ======
from src import create_app
from src.models import db

# ====== Função para inserir dados iniciais ======
def inserir_dados_iniciais():
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
        db.session.bulk_save_objects(perfis)

    if not StatusChamado.query.first():
        status_list = [
            StatusChamado(nome='Inicial', ordem=1),
            StatusChamado(nome='Em aberto', ordem=2),
            StatusChamado(nome='Em Andamento', ordem=3),
            StatusChamado(nome='Aguardando Material de Reparo', ordem=4),
            StatusChamado(nome='Concluído', ordem=5)
        ]
        db.session.bulk_save_objects(status_list)

    if not Turno.query.first():
        turnos = [
            Turno(nome='Manhã', descricao='8:00 às 12:00'),
            Turno(nome='Tarde', descricao='13:00 às 17:00'),
            Turno(nome='Noite', descricao='18:00 às 22:00'),
            Turno(nome='Madrugada', descricao='23:00 às 7:00')
        ]
        db.session.bulk_save_objects(turnos)

    if not Unidade.query.first():
        unidades = [
            Unidade(nome='Unidade A'),
            Unidade(nome='Unidade B'),
            Unidade(nome='Unidade C')
        ]
        db.session.bulk_save_objects(unidades)

    if not NaoConformidade.query.first():
        nao_conformidades = [
            NaoConformidade(nome='Equipamento com defeito'),
            NaoConformidade(nome='Vazamento'),
            NaoConformidade(nome='Problema elétrico'),
            NaoConformidade(nome='Limpeza necessária'),
            NaoConformidade(nome='Manutenção preventiva')
        ]
        db.session.bulk_save_objects(nao_conformidades)

    if not LocalApontamento.query.first():
        locais = [
            LocalApontamento(nome='Área de Produção'),
            LocalApontamento(nome='Escritório'),
            LocalApontamento(nome='Almoxarifado'),
            LocalApontamento(nome='Área Externa'),
            LocalApontamento(nome='Banheiros')
        ]
        db.session.bulk_save_objects(locais)

    try:
        db.session.commit()
        print("Dados iniciais inseridos com sucesso")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao inserir dados iniciais: {e}")

# ====== Função principal para rodar via terminal ======
def main():
    app = create_app()
    with app.app_context():
        try:
            upgrade()
            print("Migrações aplicadas com sucesso")
        except Exception as e:
            print(f"Erro ao aplicar migrações: {e}")
            sys.exit(1)

        inserir_dados_iniciais()

# ====== Execução direta pelo terminal ======
if __name__ == "__main__":
    main()

# ====== Exposição do app para servidores WSGI ======
from src import create_app
app = create_app()


@app.route('/relatorio')
def relatorio():
    # Obtenção das estatísticas de chamados
    total = Chamado.query.count()
    abertos = Chamado.query.filter_by(status='Em aberto').count()
    andamento = Chamado.query.filter_by(status='Em Andamento').count()
    concluidos = Chamado.query.filter_by(status='Concluído').count()

    estatisticas = {
        'total_chamados': total,
        'chamados_abertos': abertos,
        'chamados_andamento': andamento,
        'chamados_concluidos': concluidos
    }

    # Renderiza o template, passando o objeto estatísticas
    return render_template('relatorio.html', estatisticas=estatisticas)
