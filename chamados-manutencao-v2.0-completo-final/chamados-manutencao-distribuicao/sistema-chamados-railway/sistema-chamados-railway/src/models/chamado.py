# src/models/chamado.py
# ===============================
# Modelo de Chamado de Manutenção
# ===============================

from src.models import db
from datetime import datetime

class Chamado(db.Model):
    """Representa um chamado de manutenção no sistema."""

    # -------------------------------
    # 1) Definição da tabela
    # -------------------------------
    __tablename__ = 'tb_chamados'

    # -------------------------------
    # 2) Colunas principais
    # -------------------------------
    id = db.Column(db.Integer, primary_key=True)
    protocolo = db.Column(db.String(4), unique=True, nullable=True)

    # -------------------------------
    # 3) Dados do solicitante
    # -------------------------------
    cliente_nome = db.Column(db.String(100), nullable=False)
    cliente_email = db.Column(db.String(120), nullable=False)
    cliente_telefone = db.Column(db.String(20))
    email_requisitante = db.Column(db.String(120), nullable=False)
    telefone_requisitante = db.Column(db.String(20))

    # -------------------------------
    # 4) Dados do chamado
    # -------------------------------
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    prioridade = db.Column(db.String(20), nullable=False, default='media')

    # -------------------------------
    # 5) Chaves estrangeiras (FK)
    # -------------------------------
    id_turno = db.Column(db.Integer, db.ForeignKey('tb_turnos.id'), nullable=True)
    id_unidade = db.Column(db.Integer, db.ForeignKey('tb_unidades.id'), nullable=True)
    id_nao_conformidade = db.Column(db.Integer, db.ForeignKey('tb_nao_conformidades.id'), nullable=True)
    id_local_apontamento = db.Column(db.Integer, db.ForeignKey('tb_locais_apontamento.id'), nullable=True)
    id_status = db.Column(db.Integer, db.ForeignKey('tb_status_chamado.id'), nullable=True)

    # -------------------------------
    # 6) Datas de fluxo do chamado
    # -------------------------------
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_inicio_atendimento = db.Column(db.DateTime)
    data_conclusao_manutencao = db.Column(db.DateTime)
    data_aprovacao_admin = db.Column(db.DateTime)
    data_fechamento = db.Column(db.DateTime)

    # -------------------------------
    # 7) Status e histórico interno
    # -------------------------------
    status = db.Column(db.String(20), nullable=False, default='aberto')
    resposta_tecnico = db.Column(db.Text)
    anexos = db.Column(db.Text)

    # -------------------------------
    # 8) Controle de criação/atualização
    # -------------------------------
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # -------------------------------
    # 9) Relacionamentos SQLAlchemy
    # -------------------------------
    turno = db.relationship('Turno', backref='chamados', foreign_keys=[id_turno], lazy=True)
    unidade = db.relationship('Unidade', backref='chamados', foreign_keys=[id_unidade], lazy=True)
    nao_conformidade = db.relationship('NaoConformidade', backref='chamados',
                                      foreign_keys=[id_nao_conformidade], lazy=True)
    local_apontamento = db.relationship('LocalApontamento', backref='chamados',
                                        foreign_keys=[id_local_apontamento], lazy=True)
    status_chamado = db.relationship('StatusChamado', backref='chamados',
                                     foreign_keys=[id_status], lazy=True)

    # -------------------------------
    # 10) Métodos auxiliares
    # -------------------------------
    @staticmethod
    def gerar_proximo_protocolo():
        """Gera próximo protocolo no formato 0001-9999"""
        ultimo = (
            Chamado.query
            .filter(Chamado.protocolo.isnot(None))
            .order_by(Chamado.protocolo.desc())
            .first()
        )
        if not ultimo:
            return "0001"
        try:
            num = int(ultimo.protocolo)
            for i in range(num + 1, num + 10000):
                p = f"{(i % 10000):04d}"
                if not Chamado.query.filter_by(protocolo=p).first():
                    return p
        except ValueError:
            pass
        raise ValueError("Limite de protocolos atingido")

    def to_dict(self):
        """Retorna representação JSON serializável do chamado"""
        return {
            'id': self.id,
            'protocolo': self.protocolo,
            'cliente_nome': self.cliente_nome,
            'cliente_email': self.cliente_email,
            'cliente_telefone': self.cliente_telefone,
            'email_requisitante': self.email_requisitante,
            'telefone_requisitante': self.telefone_requisitante,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'prioridade': self.prioridade,
            'turno_nome': self.turno.nome if self.turno else None,
            'unidade_nome': self.unidade.nome if self.unidade else None,
            'nao_conformidade_nome': self.nao_conformidade.nome if self.nao_conformidade else None,
            'local_apontamento_nome': self.local_apontamento.nome if self.local_apontamento else None,
            'status_nome': self.status_chamado.nome if self.status_chamado else None,
            'status': self.status,
            'resposta_tecnico': self.resposta_tecnico,
            'anexos': self.anexos,
            'data_solicitacao': self.data_solicitacao.isoformat(),
            'data_conclusao': (self.data_fechamento.isoformat() if self.data_fechamento else None),
            'data_criacao': self.data_criacao.isoformat(),
            'data_atualizacao': self.data_atualizacao.isoformat()
        }

    def __repr__(self):
        return f"<Chamado {self.protocolo} - {self.titulo}>"
