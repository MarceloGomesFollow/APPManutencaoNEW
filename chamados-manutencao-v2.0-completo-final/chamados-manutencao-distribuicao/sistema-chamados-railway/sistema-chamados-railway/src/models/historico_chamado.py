from src.models import db
from datetime import datetime

class HistoricoChamado(db.Model):
    __tablename__ = 'tb_historico_chamado'
    
    id = db.Column(db.Integer, primary_key=True)
    id_chamado = db.Column(db.Integer, db.ForeignKey('tb_chamados.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('tb_users.id'), nullable=True)
    tipo_evento = db.Column(db.String(50), nullable=False)  # 'status_change', 'response', 'notification_sent', 'comment'
    descricao = db.Column(db.Text, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    detalhes_adicionais = db.Column(db.Text)  # JSON string para dados extras
    
    # Relacionamentos
    chamado = db.relationship('Chamado', backref='historico', lazy=True)
    usuario = db.relationship('User', backref='historico_acoes', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_chamado': self.id_chamado,
            'id_usuario': self.id_usuario,
            'usuario_nome': self.usuario.name if self.usuario else 'Sistema',
            'tipo_evento': self.tipo_evento,
            'descricao': self.descricao,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'detalhes_adicionais': self.detalhes_adicionais
        }
    
    def __repr__(self):
        return f'<HistoricoChamado {self.id} - {self.tipo_evento}>'

