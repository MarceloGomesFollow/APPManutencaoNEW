from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'tb_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    id_perfil = db.Column(db.Integer, db.ForeignKey('tb_perfis.id'))
    
    # Relacionamento com HistoricoChamado (se aplicável)
    historico_chamados = db.relationship('HistoricoChamado', backref='criado_por', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }
    
    def __repr__(self):
        return f'<User {self.username}>'