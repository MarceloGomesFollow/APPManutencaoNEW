# src/models/user.py
# ===============================
# Modelo de Usuário
# ===============================

from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'tb_users'
    
    # -------------------------------
    # 1) Colunas principais
    # -------------------------------
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    id_perfil = db.Column(db.Integer, db.ForeignKey('tb_perfis.id'))
    
    # -------------------------------
    # 2) Relacionamentos
    # -------------------------------
    historico_chamados = db.relationship('HistoricoChamado', backref='criado_por', foreign_keys='HistoricoChamado.id_usuario', lazy=True)
    historico_acoes = db.relationship('HistoricoChamado', foreign_keys='HistoricoChamado.id_usuario', lazy=True, back_populates="usuario")
    
    # -------------------------------
    # 3) Métodos auxiliares
    # -------------------------------
    def to_dict(self):
        """Retorna representação serializável do usuário."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }
    
    def __repr__(self):
        return f'<User {self.username}>'