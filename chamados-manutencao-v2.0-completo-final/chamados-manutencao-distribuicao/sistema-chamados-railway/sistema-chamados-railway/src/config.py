import os

class Config:
    # Configurações básicas
    SECRET_KEY = 'asdf#FGSgvasgf$5$WGT'
    
    # Configurações do banco de dados
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de upload - caminho absoluto
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'mp4', 'avi', 'mov'}
    
    # Configurações de segurança
    SUPERVISOR_PASSWORD = '1234'  # Senha do supervisor
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    @staticmethod
    def init_app(app):
        # Cria pasta de uploads se não existir
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            try:
                os.makedirs(upload_folder, exist_ok=True)
                print(f"Diretório de uploads criado: {upload_folder}")
            except Exception as e:
                print(f"Erro ao criar diretório de uploads: {e}")
        
        # Cria pasta do banco de dados se não existir
        db_folder = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        if not os.path.exists(db_folder):
            try:
                os.makedirs(db_folder, exist_ok=True)
                print(f"Diretório do banco criado: {db_folder}")
            except Exception as e:
                print(f"Erro ao criar diretório do banco: {e}")

