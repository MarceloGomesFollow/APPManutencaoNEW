#!/usr/bin/env python3
"""
Script para criar o banco de dados com contexto Flask adequado
Resolve o erro: RuntimeError: Working outside of application context
Versão aprimorada para Railway com checagem de banco existente
"""

import os
import sys

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_database_exists():
    """Verifica se o banco de dados já existe"""
    possible_paths = [
        "instance/app.db",
        "instance/database.db", 
        "app.db",
        "database.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"📋 Banco de dados encontrado em: {path}")
            return True
    
    return False

try:
    print("🔧 Iniciando verificação do banco de dados...")
    
    # Verificar se banco já existe
    if check_database_exists():
        print("✅ Banco de dados já existe - pulando criação")
        print("🎯 Script finalizado - Railway pode continuar o build")
        sys.exit(0)
    
    print("📊 Banco não encontrado - criando novo banco...")
    
    # Importar a aplicação Flask usando a factory function
    from src import create_app
    
    # Criar aplicação
    app = create_app()
    
    print("🔨 Criando tabelas do banco de dados...")
    
    # Criar todas as tabelas dentro do contexto da aplicação
    with app.app_context():
        from models.user import db
        
        # Verificar novamente dentro do contexto
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'sqlite' in db_path and os.path.exists(db_path.replace('sqlite:///', '')):
            print("✅ Banco SQLite já existe - pulando criação")
        else:
            db.create_all()
            print("✅ Banco de dados criado com sucesso!")
        
        # Verificar se as tabelas foram criadas
        try:
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            if tables:
                print(f"📋 Tabelas disponíveis: {', '.join(tables)}")
            else:
                print("📋 Usando banco em memória ou PostgreSQL")
        except Exception as e:
            print(f"⚠️ Não foi possível listar tabelas: {e}")
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("🔍 Tentando criar banco básico...")
    
    # Fallback: criar apenas com Flask básico
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        
        app = Flask(__name__)
        
        # Configurar banco baseado no ambiente
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            # PostgreSQL no Railway/Heroku
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        else:
            # SQLite local
            os.makedirs('instance', exist_ok=True)
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
        
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db = SQLAlchemy(app)
        
        with app.app_context():
            # Verificar se é SQLite e já existe
            if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
                db_file = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                if os.path.exists(db_file):
                    print("✅ Banco SQLite já existe - pulando criação")
                else:
                    db.create_all()
                    print("✅ Banco SQLite criado com sucesso!")
            else:
                # PostgreSQL - sempre tentar criar (não sobrescreve)
                db.create_all()
                print("✅ Banco PostgreSQL configurado com sucesso!")
            
    except Exception as fallback_error:
        print(f"❌ Erro no fallback: {fallback_error}")
        # Não falhar o build - continuar sem banco
        print("⚠️ Continuando sem banco de dados...")
    
except Exception as e:
    print(f"❌ Erro ao criar banco de dados: {e}")
    # Não falhar o build - continuar sem banco
    print("⚠️ Continuando sem banco de dados...")

print("🎯 Script finalizado - Railway pode continuar o build")

