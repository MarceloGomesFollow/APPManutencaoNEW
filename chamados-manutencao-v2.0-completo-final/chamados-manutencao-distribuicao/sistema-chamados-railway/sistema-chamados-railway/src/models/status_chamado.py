from . import db
from datetime import datetime

class StatusChamado(db.Model):
    __tablename__ = 'tb_status_chamado'
    
    # -------------------------------
    # 1) Colunas principais
    # -------------------------------
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    ordem = db.Column(db.Integer, nullable=False, default=0)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # -------------------------------
    # 2) Relacionamento com chamados
    # -------------------------------
    chamados = db.relationship('Chamado', foreign_keys='Chamado.id_status', lazy=True)  # Removido backref='status_chamado'
    
    # -------------------------------
    # 3) Métodos auxiliares
    # -------------------------------
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'ordem': self.ordem,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }
    
    def __repr__(self):
        return f'<StatusChamado {self.nome}>'