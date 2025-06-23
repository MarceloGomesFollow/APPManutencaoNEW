from src.models import db
from datetime import datetime

class HistoricoNotificacoes(db.Model):
    __tablename__ = 'tb_historico_notificacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    id_chamado = db.Column(db.Integer, db.ForeignKey('tb_chamados.id'), nullable=True)
    tipo_notificacao = db.Column(db.String(20), nullable=False)  # 'email', 'sms', 'whatsapp'
    destinatario = db.Column(db.String(120), nullable=False)
    assunto = db.Column(db.String(200))
    mensagem = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status_envio = db.Column(db.String(20), nullable=False, default='pendente')  # 'enviado', 'falha', 'pendente'
    detalhes_erro = db.Column(db.Text)
    
    # Relacionamento
    chamado = db.relationship('Chamado', backref='notificacoes', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_chamado': self.id_chamado,
            'tipo_notificacao': self.tipo_notificacao,
            'destinatario': self.destinatario,
            'assunto': self.assunto,
            'mensagem': self.mensagem,
            'data_envio': self.data_envio.isoformat() if self.data_envio else None,
            'status_envio': self.status_envio,
            'detalhes_erro': self.detalhes_erro
        }
    
    def __repr__(self):
        return f'<HistoricoNotificacoes {self.id} - {self.tipo_notificacao}>'

