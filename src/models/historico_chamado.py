# src/models/historico_chamado.py
# ===============================
# Modelo de Histórico de Chamado
# ===============================

from . import db
from datetime import datetime

class HistoricoChamado(db.Model):
    """Representa um registro de histórico de ações ou eventos em um chamado."""
    
    # -------------------------------
    # 1) Definição da tabela
    # -------------------------------
    __tablename__ = 'tb_historico_chamado'
    
    # -------------------------------
    # 2) Colunas principais
    # -------------------------------
    id = db.Column(db.Integer, primary_key=True)
    id_chamado = db.Column(db.Integer, db.ForeignKey('tb_chamados.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('tb_users.id'), nullable=True)

    anexos = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=True, default='aberto')
    
    # -------------------------------
    # 3) Detalhes do evento
    # -------------------------------
    tipo_evento = db.Column(db.String(50), nullable=False)  # 'status_change', 'response', etc.
    descricao = db.Column(db.Text, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    detalhes_adicionais = db.Column(db.Text)  # JSON string para dados extras
    
    # -------------------------------
    # 4) Relacionamentos
    # -------------------------------
    chamado = db.relationship(
        'Chamado',
        foreign_keys=[id_chamado],
        lazy=True,
        overlaps="historico"
    )
    usuario = db.relationship(
        'User',
        foreign_keys=[id_usuario],
        lazy=True,
        back_populates="historico_acoes",
        overlaps="criado_por,historico_chamados"
    )
    
    # -------------------------------
    # 5) Métodos auxiliares
    # -------------------------------
    def to_dict(self):
        """Retorna representação serializável do histórico."""
        return {
            'id': self.id,
            'id_chamado': self.id_chamado,
            'id_usuario': self.id_usuario,
            'usuario_nome': self.usuario.username if self.usuario else 'Sistema',
            'tipo_evento': self.tipo_evento,
            'descricao': self.descricao,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'detalhes_adicionais': self.detalhes_adicionais
        }
    
    def __repr__(self):
        return f'<HistoricoChamado {self.id} - {self.tipo_evento}>'