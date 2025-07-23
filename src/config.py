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
    SECRET_KEY = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
    
    # -------------------------------
    # 2) Banco de dados
    # -------------------------------
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'instance', 'app.db').replace('\\', '/'))
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
    SUPERVISOR_PASSWORD = os.getenv('SUPERVISOR_PASSWORD', 'Manu@12345')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Arfrio@4321')

    R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID', '123')
    R2_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY', 'dfsdf13d52f1sdf')
    R2_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL', 'https://fdfsdfs.r2.cloudflarestorage.com')
    R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'app-manutencao-test')



    # -------------------------------
    # 5) Sessão
    # -------------------------------
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.getenv('SESSION_LIFETIME', '3600'))
    )

    # -------------------------------
    # 6) Time Zone
    # -------------------------------
    TIMEZONE = os.getenv('TIMEZONE', 'America/Sao_Paulo')

    @staticmethod
    def init_app(app):
        """Cria, se necessário, o diretório de uploads."""
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
