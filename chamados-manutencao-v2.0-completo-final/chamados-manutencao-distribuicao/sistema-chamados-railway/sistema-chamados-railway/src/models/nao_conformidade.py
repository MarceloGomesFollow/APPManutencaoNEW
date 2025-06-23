# src/models/nao_conformidade.py
# ===============================
# Modelo de Não Conformidade
# ===============================

from . import db
from datetime import datetime

class NaoConformidade(db.Model):
    """Representa uma não conformidade associada aos chamados de manutenção."""

    # -------------------------------
    # 1) Definição da tabela
    # -------------------------------
    __tablename__ = 'tb_nao_conformidades'
    
    # -------------------------------
    # 2) Colunas principais
    # -------------------------------
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # -------------------------------
    # 3) Relacionamento com chamados
    # -------------------------------
    chamados = db.relationship('Chamado', backref='nao_conformidade', lazy=True)
    
    # -------------------------------
    # 4) Métodos auxiliares
    # -------------------------------
    def to_dict(self):
        """Retorna representação serializável da não conformidade."""
        return {
            'id': self.id,
            'nome': self.nome,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }
    
    def __repr__(self):
        return f'<NaoConformidade {self.nome}>'