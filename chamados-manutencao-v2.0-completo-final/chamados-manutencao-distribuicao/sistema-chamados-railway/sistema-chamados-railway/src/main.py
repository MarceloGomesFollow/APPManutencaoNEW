#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
src/main.py

Script de release: aplica migrações e insere dados iniciais.
Execute via: python -m src.main   (ou `python src/main.py` se preferir)
"""

import os
import sys
from flask_migrate import upgrade

# Se você for chamar com `python src/main.py`, garante que o projeto raiz esteja no PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importa a factory de app
from src import create_app  # :contentReference[oaicite:0]{index=0}
from src.models import db   # importa a instância de SQLAlchemy

def inserir_dados_iniciais():
    """Insere perfis, status, turnos, unidades, não conformidades e locais de apontamento"""
    from src.models.perfil import Perfil
    from src.models.status_chamado import StatusChamado
    from src.models.turno import Turno
    from src.models.unidade import Unidade
    from src.models.nao_conformidade import NaoConformidade
    from src.models.local_apontamento import LocalApontamento

    # === PERFIS ===
    if not Perfil.query.first():
        perfis = [
            Perfil(nome='Administrador', descricao='Acesso total ao sistema'),
            Perfil(nome='Manutenção', descricao='Técnicos de manutenção'),
            Perfil(nome='Requisitante', descricao='Usuários que abrem chamados')
        ]
        db.session.bulk_save_objects(perfis)

    # === STATUS DE CHAMADO ===
    if not StatusChamado.query.first():
        status_list = [
            StatusChamado(nome='Inicial', ordem=1),
            StatusChamado(nome='Em aberto', ordem=2),
            StatusChamado(nome='Em Andamento', ordem=3),
            StatusChamado(nome='Aguardando Material de Reparo', ordem=4),
            StatusChamado(nome='Concluído', ordem=5)
        ]
        db.session.bulk_save_objects(status_list)

    # === TURNOS ===
    if not Turno.query.first():
        turnos = [
            Turno(nome='Manhã', descricao='8:00 às 12:00'),
            Turno(nome='Tarde', descricao='13:00 às 17:00'),
            Turno(nome='Noite', descricao='18:00 às 22:00'),
            Turno(nome='Madrugada', descricao='23:00 às 7:00')
        ]
        db.session.bulk_save_objects(turnos)

    # === UNIDADES ===
    if not Unidade.query.first():
        unidades = [
            Unidade(nome='Unidade A'),
            Unidade(nome='Unidade B'),
            Unidade(nome='Unidade C')
        ]
        db.session.bulk_save_objects(unidades)

    # === NÃO CONFORMIDADES ===
    if not NaoConformidade.query.first():
        nao_conformidades = [
            NaoConformidade(nome='Equipamento com defeito'),
            NaoConformidade(nome='Vazamento'),
            NaoConformidade(nome='Problema elétrico'),
            NaoConformidade(nome='Limpeza necessária'),
            NaoConformidade(nome='Manutenção preventiva')
        ]
        db.session.bulk_save_objects(nao_conformidades)

    # === LOCAIS DE APONTAMENTO ===
    if not LocalApontamento.query.first():
        locais = [
            LocalApontamento(nome='Área de Produção'),
            LocalApontamento(nome='Escritório'),
            LocalApontamento(nome='Almoxarifado'),
            LocalApontamento(nome='Área Externa'),
            LocalApontamento(nome='Banheiros')
        ]
        db.session.bulk_save_objects(locais)

    # Confirma as mudanças
    try:
        db.session.commit()
        print("Dados iniciais inseridos com sucesso")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao inserir dados iniciais: {e}")

def main():
    """Entry-point do script de release"""
    app = create_app()
    with app.app_context():
        # === MIGRAÇÕES ===
        try:
            upgrade()  # aplica todas as migrations pendentes
            print("Migrações aplicadas com sucesso")
        except Exception as e:
            print(f"Erro ao aplicar migrações: {e}")
            sys.exit(1)

        # === SEED DE DADOS ===
        inserir_dados_iniciais()

if __name__ == "__main__":
    main()
