# src/config.py
# ===============================
# Configurações da aplicação Flask
# ===============================

import os
from datetime import timedelta

class Config:
    # -------------------------------
    # 1) Chave secreta
    # -------------------------------
    # Usa variável de ambiente para maior segurança, com fallback para valor padrão
    SECRET_KEY = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
    
    # -------------------------------
    # 2) Banco de dados
    # -------------------------------
    # Usa PostgreSQL via variável de ambiente DATABASE_URL fornecida pelo Railway
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -------------------------------
    # 3) Uploads
    # -------------------------------
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    UPLOAD_FOLDER = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'Uploads')
    )
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif',
        'doc', 'docx', 'mp4', 'avi', 'mov'
    }

    # -------------------------------
    # 4) Senhas de acesso
    # -------------------------------
    SUPERVISOR_PASSWORD = os.getenv('SUPERVISOR_PASSWORD', 'Manu@1234')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Arfrio@4321')

    # -------------------------------
    # 5) Sessão
    # -------------------------------
    # Expira após 1 hora, pode ser sobrescrito por SESSION_LIFETIME
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.getenv('SESSION_LIFETIME', '3600'))
    )

    @staticmethod
    def init_app(app):
        """Cria, se necessário, o diretório de uploads."""
        # Cria pasta de uploads
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)