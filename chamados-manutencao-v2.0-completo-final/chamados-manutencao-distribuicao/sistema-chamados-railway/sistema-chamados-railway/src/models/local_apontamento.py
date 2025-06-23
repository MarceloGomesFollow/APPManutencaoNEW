## src/models/local_apontamento.py
# ===============================
# Modelo de Local de Apontamento
# ===============================

from models import db  # import absoluto para instância SQLAlchemy
from datetime import datetime

class LocalApontamento(db.Model):
    """Representa um local de apontamento para os chamados de manutenção."""

    # -------------------------------
    # 1) Definição da tabela
    # -------------------------------
    __tablename__ = 'tb_locais_apontamento'
    __table_args__ = {'extend_existing': True}

    # -------------------------------
    # 2) Colunas principais
    # -------------------------------
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    data_atualizacao = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # -------------------------------
    # 3) Relacionamentos
    # -------------------------------
    chamados = db.relationship(
        'Chamado',
        backref='local_apontamento',
        lazy='selectin'
    )

    # -------------------------------
    # 4) Métodos auxiliares
    # -------------------------------
    def to_dict(self):
        """Retorna representação serializável do local de apontamento."""
        return {
            'id': self.id,
            'nome': self.nome,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }

    def __repr__(self):
        return f"<LocalApontamento {self.nome}>"
