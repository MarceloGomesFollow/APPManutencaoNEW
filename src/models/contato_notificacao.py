# src/models/contato_notificacao.py
# ===============================
# Modelo de Contato de Notificação de Manutenção
# ===============================

from src.models import db
from datetime import datetime

class ContatoNotificacaoManutencao(db.Model):
    """Representa um contato para envio de notificações de manutenção."""

    # -------------------------------
    # 1) Definição da tabela
    # -------------------------------
    __tablename__ = 'tb_contatos_notificacao_manutencao'

    # -------------------------------
    # 2) Colunas principais
    # -------------------------------
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20))

    # -------------------------------
    # 3) Status de atividade
    # -------------------------------
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    # -------------------------------
    # 4) Controle de criação/atualização
    # -------------------------------
    data_criacao = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    data_atualizacao = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # -------------------------------
    # 5) Métodos auxiliares
    # -------------------------------
    def to_dict(self):
        """Retorna representação JSON serializável do contato."""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }

    def __repr__(self):
        return f"<ContatoNotificacaoManutencao {self.nome}>"

