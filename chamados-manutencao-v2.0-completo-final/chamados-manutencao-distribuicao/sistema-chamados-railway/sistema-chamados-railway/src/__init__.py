from src.models import db

def create_app():
    app = Flask(...)
    # suas configurações aqui
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///...'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # INICIALIZA o SQLAlchemy com esta app
    db.init_app(app)

    # se quiser criar as tabelas automaticamente (opcional)
    with app.app_context():
        db.create_all()

    # agora os blueprints
    app.register_blueprint(...)
    return app

