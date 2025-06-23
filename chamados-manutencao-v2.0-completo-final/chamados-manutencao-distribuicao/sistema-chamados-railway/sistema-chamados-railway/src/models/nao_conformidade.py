# src/models/chamado.py
# ... (outras partes do arquivo permanecem iguais)

from . import db
from datetime import datetime

class Chamado(db.Model):
    """Representa um chamado de manutenção no sistema."""
    __tablename__ = 'tb_chamados'

    # ... (outras colunas permanecem iguais)

    # Chaves estrangeiras (FK)
    id_turno = db.Column(db.Integer, db.ForeignKey('tb_turnos.id'), nullable=True)
    id_unidade = db.Column(db.Integer, db.ForeignKey('tb_unidades.id'), nullable=True)
    id_nao_conformidade = db.Column(db.Integer, db.ForeignKey('tb_nao_conformidades.id'), nullable=True)
    id_local_apontamento = db.Column(db.Integer, db.ForeignKey('tb_locais_apontamento.id'), nullable=True)
    id_status = db.Column(db.Integer, db.ForeignKey('tb_status_chamado.id'), nullable=True)

    # Relacionamentos SQLAlchemy
    turno = db.relationship('Turno', backref='chamados_associados', foreign_keys=[id_turno], lazy=True)
    unidade = db.relationship('Unidade', foreign_keys=[id_unidade], lazy=True)  # Já corrigido anteriormente
    nao_conformidade = db.relationship('NaoConformidade', foreign_keys=[id_nao_conformidade], lazy=True)  # Removido backref='chamados'
    local_apontamento = db.relationship('LocalApontamento', backref='chamados', foreign_keys=[id_local_apontamento], lazy=True)
    status_chamado = db.relationship('StatusChamado', backref='chamados', foreign_keys=[id_status], lazy=True)

    # ... (restante do código permanece igual)