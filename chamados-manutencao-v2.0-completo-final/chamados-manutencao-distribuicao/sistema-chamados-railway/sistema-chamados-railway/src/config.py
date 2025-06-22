import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    # Configurações básicas
    SECRET_KEY = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Configurações do banco de dados
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'txt,pdf,png,jpg,jpeg,gif,doc,docx,mp4,avi,mov').split(','))
    
    # Configurações de segurança
    SUPERVISOR_PASSWORD = os.getenv('SUPERVISOR_PASSWORD', '1234')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Configurações de e-mail
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@sistema-chamados.com')
    
    # Configurações de notificações
    NOTIFICACOES_ATIVAS = os.getenv('NOTIFICACOES_ATIVAS', 'False').lower() == 'true'
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # Configurações de logs
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    @staticmethod
    def init_app(app):
        # Cria pasta de uploads se não existir
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Cria pasta de logs se não existir
        log_folder = os.path.join(os.path.dirname(__file__), '..', 'logs')
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

