import os
from datetime import timedelta

class Config:
    # 1) SECRET_KEY permanece hard-coded conforme solicitado
    SECRET_KEY = 'asdf#FGSgvasgf$5$WGT'
    
    # 2) Banco de dados SQLite local
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3) Uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    UPLOAD_FOLDER = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'uploads')
    )
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif',
        'doc', 'docx', 'mp4', 'avi', 'mov'
    }

    # 4) Senhas de acesso
    SUPERVISOR_PASSWORD = os.getenv('SUPERVISOR_PASSWORD', 'Manu@1234')
    ADMIN_PASSWORD      = os.getenv('ADMIN_PASSWORD',      'Arfrio@4321')

    # 5) Sessão — expira após 1 hora (pode ser sobrescrito por SESSION_LIFETIME env var)
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.getenv('SESSION_LIFETIME', '3600'))
    )

    @staticmethod
    def init_app(app):
        """Cria, se necessário, os diretórios de uploads e do banco."""
        # Cria pasta de uploads
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Cria pasta do arquivo SQLite
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

