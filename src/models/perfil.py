# src/models/perfil.py
from . import db          # ← instancia correta
from src.models.user import User   # ← importa a classe para registrar no registry
from datetime import datetime

class Perfil(db.Model):
    __tablename__ = 'tb_perfis'
    
    id              = db.Column(db.Integer, primary_key=True)
    nome            = db.Column(db.String(50),  nullable=False, unique=True)
    descricao       = db.Column(db.String(200))
    ativo           = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao    = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao= db.Column(db.DateTime, default=datetime.utcnow,
                                 onupdate=datetime.utcnow, nullable=False)
    
    # relacionamento: já existe a classe User no registry
    usuarios = db.relationship(
        User,                    # referenciando a classe diretamente
        backref='perfil',
        lazy=True
    )

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'ativo': self.ativo,
            'data_criacao': (self.data_criacao.isoformat()
                             if self.data_criacao else None),
            'data_atualizacao': (self.data_atualizacao.isoformat()
                                 if self.data_atualizacao else None)
        }
    
    def __repr__(self):
        return f'<Perfil {self.nome}>'
