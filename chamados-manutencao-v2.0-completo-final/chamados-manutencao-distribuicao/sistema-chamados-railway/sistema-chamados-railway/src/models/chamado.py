from src.models import db
from datetime import datetime
import uuid

class Chamado(db.Model):
    __tablename__ = 'tb_chamados'
    id = db.Column(db.Integer, primary_key=True)
    protocolo = db.Column(db.String(4), unique=True, nullable=True)  # Protocolo numérico 0001-9999
    
    # Dados do solicitante
    cliente_nome = db.Column(db.String(100), nullable=False)
    cliente_email = db.Column(db.String(120), nullable=False)
    cliente_telefone = db.Column(db.String(20))
    email_requisitante = db.Column(db.String(120), nullable=False)  # Para notificações
    telefone_requisitante = db.Column(db.String(20))  # Para SMS/WhatsApp
    
    # Dados do chamado
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    prioridade = db.Column(db.String(20), nullable=False, default='media')
    
    # Novos campos de relacionamento
    id_turno = db.Column(db.Integer, db.ForeignKey('tb_turnos.id'), nullable=True)
    id_unidade = db.Column(db.Integer, db.ForeignKey('tb_unidades.id'), nullable=True)
    id_nao_conformidade = db.Column(db.Integer, db.ForeignKey('tb_nao_conformidades.id'), nullable=True)
    id_local_apontamento = db.Column(db.Integer, db.ForeignKey('tb_locais_apontamento.id'), nullable=True)
    id_status = db.Column(db.Integer, db.ForeignKey('tb_status_chamado.id'), nullable=True)
    
    # Campos de data/hora
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_inicio_atendimento = db.Column(db.DateTime, nullable=True)
    data_conclusao_manutencao = db.Column(db.DateTime, nullable=True)
    data_aprovacao_admin = db.Column(db.DateTime, nullable=True)
    data_fechamento = db.Column(db.DateTime, nullable=True)
    
    # Campos existentes mantidos para compatibilidade
    status = db.Column(db.String(20), nullable=False, default='aberto')
    resposta_tecnico = db.Column(db.Text)
    anexos = db.Column(db.Text)  # JSON string com lista de arquivos
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Campos legados mantidos
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    supervisor_resposta = db.Column(db.Text, nullable=True)
    prazo_estimado = db.Column(db.DateTime, nullable=True)
    data_conclusao = db.Column(db.DateTime, nullable=True)
    acao_tomada = db.Column(db.Text, nullable=True)
    
    @staticmethod
    def gerar_proximo_protocolo():
        """Gera o próximo protocolo numérico disponível (0001-9999)"""
        # Busca o último protocolo usado
        ultimo_chamado = Chamado.query.filter(Chamado.protocolo.isnot(None)).order_by(Chamado.protocolo.desc()).first()
        
        if not ultimo_chamado:
            return "0001"
        
        try:
            ultimo_numero = int(ultimo_chamado.protocolo)
            proximo_numero = ultimo_numero + 1
            
            # Verifica se não ultrapassou 9999
            if proximo_numero > 9999:
                # Busca o primeiro número disponível (caso algum tenha sido deletado)
                for num in range(1, 10000):
                    protocolo_teste = f"{num:04d}"
                    if not Chamado.query.filter_by(protocolo=protocolo_teste).first():
                        return protocolo_teste
                # Se todos estão ocupados, retorna erro
                raise ValueError("Limite de protocolos atingido (9999)")
            
            return f"{proximo_numero:04d}"
        except (ValueError, TypeError):
            return "0001"
    
    def to_dict(self):
        return {
            'id': self.id,
            'protocolo': self.protocolo,
            'cliente_nome': self.cliente_nome,
            'cliente_email': self.cliente_email,
            'cliente_telefone': self.cliente_telefone,
            'email_requisitante': self.email_requisitante or self.cliente_email,
            'telefone_requisitante': self.telefone_requisitante or self.cliente_telefone,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'prioridade': self.prioridade,
            'id_turno': self.id_turno,
            'turno_nome': self.turno.nome if self.turno else None,
            'id_unidade': self.id_unidade,
            'unidade_nome': self.unidade.nome if self.unidade else None,
            'id_nao_conformidade': self.id_nao_conformidade,
            'nao_conformidade_nome': self.nao_conformidade.nome if self.nao_conformidade else None,
            'id_local_apontamento': self.id_local_apontamento,
            'local_apontamento_nome': self.local_apontamento.nome if self.local_apontamento else None,
            'id_status': self.id_status,
            'status_nome': self.status_chamado.nome if self.status_chamado else None,
            'status': self.status,
            'resposta_tecnico': self.resposta_tecnico,
            'anexos': self.anexos,
            'data_solicitacao': self.data_solicitacao.isoformat() if self.data_solicitacao else None,
            'data_inicio_atendimento': self.data_inicio_atendimento.isoformat() if self.data_inicio_atendimento else None,
            'data_conclusao_manutencao': self.data_conclusao_manutencao.isoformat() if self.data_conclusao_manutencao else None,
            'data_aprovacao_admin': self.data_aprovacao_admin.isoformat() if self.data_aprovacao_admin else None,
            'data_fechamento': self.data_fechamento.isoformat() if self.data_fechamento else None,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            # Campos legados
            'data_abertura': self.data_abertura.isoformat() if self.data_abertura else None,
            'supervisor_resposta': self.supervisor_resposta,
            'prazo_estimado': self.prazo_estimado.isoformat() if self.prazo_estimado else None,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None,
            'acao_tomada': self.acao_tomada
        }
    
    def calcular_tempo_aberto(self):
        """Calcula o tempo que o chamado está em aberto"""
        if self.data_fechamento:
            return self.data_fechamento - self.data_solicitacao
        else:
            return datetime.utcnow() - self.data_solicitacao
    
    def __repr__(self):
        return f'<Chamado {self.protocolo} - {self.titulo}>'

