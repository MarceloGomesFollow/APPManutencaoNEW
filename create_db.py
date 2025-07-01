#!/usr/bin/env python3
"""
Script de verificação e preparação do ambiente para Railway
Evita criação direta do banco no build, delegando a main.py com Flask-Migrate
"""

import os
import sys

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🔧 Iniciando verificação do ambiente...")

# Verificar se estamos no ambiente da Railway
is_railway = os.environ.get('RAILWAY_ENVIRONMENT') == 'production'

if is_railway:
    print("📋 Executando em ambiente Railway - verificação de variáveis...")
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("⚠️ Variável DATABASE_URL não encontrada. Certifique-se de que está configurada.")
    else:
        print(f"✅ DATABASE_URL encontrada: {database_url[:10]}... (parcial por segurança)")
else:
    print("📋 Modo local detectado - verificação de arquivos SQLite...")
    possible_paths = [
        "instance/app.db",
        "instance/database.db",
        "app.db",
        "database.db"
    ]
    db_exists = any(os.path.exists(path) for path in possible_paths)
    if db_exists:
        print("✅ Banco de dados SQLite encontrado - pulando criação")
    else:
        print("⚠️ Nenhum banco SQLite encontrado localmente.")

# Verificar se o Start Command está configurado (apenas aviso)
start_command = os.environ.get('RAILWAY_START_COMMAND', '')
if not start_command or 'flask db upgrade' not in start_command.lower():
    print("⚠️ Atenção: Start Command não configurado ou não inclui 'flask db upgrade'. Certifique-se de configurá-lo como 'flask db upgrade && python main.py' na Railway.")

print("🎯 Script finalizado - delegando criação/atualização do banco ao runtime com Flask-Migrate.")
sys.exit(0)