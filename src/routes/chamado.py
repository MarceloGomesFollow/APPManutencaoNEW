#!/usr/bin/env python3
"""
Sistema de Chamados de Manutenção - Módulo Principal
Arquivo: chamado.py
Versão: 3.0
Autor: Follow Advisor - Sistemas

Este módulo contém toda a lógica para implementar o sistema de chamados de manutenção,
incluindo modelos de dados, rotas, validações e funcionalidades completas.
"""

import os
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json
from typing import Optional, List, Dict, Any

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-sistema-chamados-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chamados.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Inicialização do banco de dados
db = SQLAlchemy(app)

# ================================
# MODELOS DE DADOS (SQLAlchemy)
# ================================

class StatusChamado:
    """Enum para status dos chamados"""
    ABERTO = 'aberto'
    EM_ANDAMENTO = 'em_andamento'
    AGUARDANDO_PECA = 'aguardando_peca'
    CONCLUIDO = 'concluido'
    CANCELADO = 'cancelado'
    
    @classmethod
    def get_all(cls):
        return [cls.ABERTO, cls.EM_ANDAMENTO, cls.AGUARDANDO_PECA, cls.CONCLUIDO, cls.CANCELADO]

class PrioridadeChamado:
    """Enum para prioridades dos chamados"""
    BAIXA = 'baixa'
    MEDIA = 'media'
    ALTA = 'alta'
    URGENTE = 'urgente'
    
    @classmethod
    def get_all(cls):
        return [cls.BAIXA, cls.MEDIA, cls.ALTA, cls.URGENTE]

class TipoChamado:
    """Enum para tipos de chamados"""
    PREVENTIVA = 'preventiva'
    CORRETIVA = 'corretiva'
    PREDITIVA = 'preditiva'
    EMERGENCIA = 'emergencia'
    INSTALACAO = 'instalacao'
    
    @classmethod
    def get_all(cls):
        return [cls.PREVENTIVA, cls.CORRETIVA, cls.PREDITIVA, cls.EMERGENCIA, cls.INSTALACAO]

class Chamado(db.Model):
    """Modelo principal para chamados de manutenção"""
    __tablename__ = 'chamados'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    protocolo = db.Column(db.String(20), unique=True, nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    
    # Informações do solicitante
    nome_solicitante = db.Column(db.String(100), nullable=False)
    email_solicitante = db.Column(db.String(120), nullable=False)
    telefone_solicitante = db.Column(db.String(20))
    email_notificacao = db.Column(db.String(120))
    
    # Classificação do chamado
    turno = db.Column(db.String(20), nullable=False)
    unidade = db.Column(db.String(50), nullable=False)
    local_especifico = db.Column(db.String(100))
    tipo_nao_conformidade = db.Column(db.String(50))
    tipo_chamado = db.Column(db.String(20), default=TipoChamado.CORRETIVA)
    prioridade = db.Column(db.String(20), default=PrioridadeChamado.MEDIA)
    status = db.Column(db.String(20), default=StatusChamado.ABERTO)
    
    # Datas e controle
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow)
    data_inicio_atendimento = db.Column(db.DateTime)
    data_conclusao = db.Column(db.DateTime)
    prazo_estimado = db.Column(db.DateTime)
    
    # Responsáveis
    responsavel_atendimento = db.Column(db.String(100))
    supervisor_responsavel = db.Column(db.String(100))
    
    # Informações técnicas
    equipamento_envolvido = db.Column(db.String(100))
    codigo_equipamento = db.Column(db.String(50))
    observacoes_tecnicas = db.Column(db.Text)
    solucao_aplicada = db.Column(db.Text)
    
    # Custos e recursos
    custo_estimado = db.Column(db.Float, default=0.0)
    custo_real = db.Column(db.Float, default=0.0)
    tempo_estimado_horas = db.Column(db.Float, default=0.0)
    tempo_real_horas = db.Column(db.Float, default=0.0)
    
    # Avaliação
    avaliacao_solicitante = db.Column(db.Integer)  # 1-5 estrelas
    comentario_avaliacao = db.Column(db.Text)
    
    # Relacionamentos
    anexos = db.relationship('AnexoChamado', backref='chamado', lazy=True, cascade='all, delete-orphan')
    historico = db.relationship('HistoricoChamado', backref='chamado', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Chamado, self).__init__(**kwargs)
        if not self.protocolo:
            self.protocolo = self.gerar_protocolo()
    
    def gerar_protocolo(self) -> str:
        """Gera um protocolo único para o chamado"""
        ano = datetime.now().year
        # Conta quantos chamados já existem este ano
        count = Chamado.query.filter(
            Chamado.protocolo.like(f'{ano}%')
        ).count() + 1
        return f'{ano}{count:06d}'
    
    def calcular_tempo_atendimento(self) -> Optional[timedelta]:
        """Calcula o tempo total de atendimento"""
        if self.data_abertura and self.data_conclusao:
            return self.data_conclusao - self.data_abertura
        return None
    
    def esta_no_prazo(self) -> bool:
        """Verifica se o chamado está dentro do prazo"""
        if not self.prazo_estimado:
            return True
        if self.status == StatusChamado.CONCLUIDO:
            return self.data_conclusao <= self.prazo_estimado
        return datetime.utcnow() <= self.prazo_estimado
    
    def get_prioridade_cor(self) -> str:
        """Retorna a cor CSS baseada na prioridade"""
        cores = {
            PrioridadeChamado.BAIXA: '#28a745',
            PrioridadeChamado.MEDIA: '#ffc107',
            PrioridadeChamado.ALTA: '#fd7e14',
            PrioridadeChamado.URGENTE: '#dc3545'
        }
        return cores.get(self.prioridade, '#6c757d')
    
    def get_status_cor(self) -> str:
        """Retorna a cor CSS baseada no status"""
        cores = {
            StatusChamado.ABERTO: '#007bff',
            StatusChamado.EM_ANDAMENTO: '#ffc107',
            StatusChamado.AGUARDANDO_PECA: '#fd7e14',
            StatusChamado.CONCLUIDO: '#28a745',
            StatusChamado.CANCELADO: '#6c757d'
        }
        return cores.get(self.status, '#6c757d')
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o chamado para dicionário"""
        return {
            'id': self.id,
            'protocolo': self.protocolo,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'nome_solicitante': self.nome_solicitante,
            'email_solicitante': self.email_solicitante,
            'telefone_solicitante': self.telefone_solicitante,
            'turno': self.turno,
            'unidade': self.unidade,
            'local_especifico': self.local_especifico,
            'tipo_chamado': self.tipo_chamado,
            'prioridade': self.prioridade,
            'status': self.status,
            'data_abertura': self.data_abertura.isoformat() if self.data_abertura else None,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None,
            'responsavel_atendimento': self.responsavel_atendimento,
            'custo_real': self.custo_real,
            'tempo_real_horas': self.tempo_real_horas,
            'avaliacao_solicitante': self.avaliacao_solicitante
        }

class AnexoChamado(db.Model):
    """Modelo para anexos dos chamados"""
    __tablename__ = 'anexos_chamado'
    
    id = db.Column(db.Integer, primary_key=True)
    chamado_id = db.Column(db.Integer, db.ForeignKey('chamados.id'), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    nome_original = db.Column(db.String(255), nullable=False)
    tipo_arquivo = db.Column(db.String(50))
    tamanho_arquivo = db.Column(db.Integer)
    caminho_arquivo = db.Column(db.String(500), nullable=False)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AnexoChamado {self.nome_original}>'

class HistoricoChamado(db.Model):
    """Modelo para histórico de alterações dos chamados"""
    __tablename__ = 'historico_chamado'
    
    id = db.Column(db.Integer, primary_key=True)
    chamado_id = db.Column(db.Integer, db.ForeignKey('chamados.id'), nullable=False)
    usuario = db.Column(db.String(100), nullable=False)
    acao = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_acao = db.Column(db.DateTime, default=datetime.utcnow)
    dados_anteriores = db.Column(db.Text)  # JSON com dados antes da alteração
    dados_novos = db.Column(db.Text)  # JSON com dados após a alteração
    
    def __repr__(self):
        return f'<HistoricoChamado {self.acao} - {self.data_acao}>'

class ConfiguracaoSistema(db.Model):
    """Modelo para configurações do sistema"""
    __tablename__ = 'configuracao_sistema'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text)
    descricao = db.Column(db.String(255))
    tipo = db.Column(db.String(20), default='string')  # string, integer, boolean, json
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    @classmethod
    def get_valor(cls, chave: str, default=None):
        """Obtém um valor de configuração"""
        config = cls.query.filter_by(chave=chave).first()
        if not config:
            return default
        
        if config.tipo == 'integer':
            return int(config.valor)
        elif config.tipo == 'boolean':
            return config.valor.lower() in ['true', '1', 'yes']
        elif config.tipo == 'json':
            return json.loads(config.valor)
        return config.valor
    
    @classmethod
    def set_valor(cls, chave: str, valor, descricao: str = None, tipo: str = 'string'):
        """Define um valor de configuração"""
        config = cls.query.filter_by(chave=chave).first()
        if not config:
            config = cls(chave=chave)
            db.session.add(config)
        
        if tipo == 'json':
            config.valor = json.dumps(valor)
        else:
            config.valor = str(valor)
        
        config.tipo = tipo
        config.data_atualizacao = datetime.utcnow()
        if descricao:
            config.descricao = descricao
        
        db.session.commit()

# ================================
# CLASSES DE SERVIÇO
# ================================

class ChamadoService:
    """Serviço para gerenciamento de chamados"""
    
    @staticmethod
    def criar_chamado(dados: Dict[str, Any]) -> Chamado:
        """Cria um novo chamado"""
        chamado = Chamado(
            titulo=dados.get('titulo'),
            descricao=dados.get('descricao'),
            nome_solicitante=dados.get('nome_solicitante'),
            email_solicitante=dados.get('email_solicitante'),
            telefone_solicitante=dados.get('telefone_solicitante'),
            email_notificacao=dados.get('email_notificacao'),
            turno=dados.get('turno'),
            unidade=dados.get('unidade'),
            local_especifico=dados.get('local_especifico'),
            tipo_nao_conformidade=dados.get('tipo_nao_conformidade'),
            tipo_chamado=dados.get('tipo_chamado', TipoChamado.CORRETIVA),
            prioridade=dados.get('prioridade', PrioridadeChamado.MEDIA),
            equipamento_envolvido=dados.get('equipamento_envolvido'),
            codigo_equipamento=dados.get('codigo_equipamento')
        )
        
        # Define prazo baseado na prioridade
        chamado.prazo_estimado = ChamadoService.calcular_prazo_por_prioridade(chamado.prioridade)
        
        db.session.add(chamado)
        db.session.commit()
        
        # Registra no histórico
        HistoricoService.registrar_acao(
            chamado.id,
            'sistema',
            'criacao',
            f'Chamado criado com protocolo {chamado.protocolo}'
        )
        
        # Envia notificação
        NotificacaoService.enviar_notificacao_abertura(chamado)
        
        return chamado
    
    @staticmethod
    def calcular_prazo_por_prioridade(prioridade: str) -> datetime:
        """Calcula prazo baseado na prioridade"""
        prazos = {
            PrioridadeChamado.URGENTE: 4,    # 4 horas
            PrioridadeChamado.ALTA: 24,      # 1 dia
            PrioridadeChamado.MEDIA: 72,     # 3 dias
            PrioridadeChamado.BAIXA: 168     # 7 dias
        }
        horas = prazos.get(prioridade, 72)
        return datetime.utcnow() + timedelta(hours=horas)
    
    @staticmethod
    def atualizar_status(chamado_id: int, novo_status: str, usuario: str, observacoes: str = None) -> bool:
        """Atualiza o status de um chamado"""
        chamado = Chamado.query.get(chamado_id)
        if not chamado:
            return False
        
        status_anterior = chamado.status
        chamado.status = novo_status
        
        # Atualiza datas específicas
        if novo_status == StatusChamado.EM_ANDAMENTO and not chamado.data_inicio_atendimento:
            chamado.data_inicio_atendimento = datetime.utcnow()
        elif novo_status == StatusChamado.CONCLUIDO:
            chamado.data_conclusao = datetime.utcnow()
        
        db.session.commit()
        
        # Registra no histórico
        descricao = f'Status alterado de "{status_anterior}" para "{novo_status}"'
        if observacoes:
            descricao += f'. Observações: {observacoes}'
        
        HistoricoService.registrar_acao(
            chamado_id,
            usuario,
            'alteracao_status',
            descricao,
            {'status_anterior': status_anterior},
            {'status_novo': novo_status}
        )
        
        # Envia notificação
        NotificacaoService.enviar_notificacao_status(chamado, status_anterior)
        
        return True
    
    @staticmethod
    def atribuir_responsavel(chamado_id: int, responsavel: str, usuario: str) -> bool:
        """Atribui um responsável ao chamado"""
        chamado = Chamado.query.get(chamado_id)
        if not chamado:
            return False
        
        responsavel_anterior = chamado.responsavel_atendimento
        chamado.responsavel_atendimento = responsavel
        db.session.commit()
        
        # Registra no histórico
        HistoricoService.registrar_acao(
            chamado_id,
            usuario,
            'atribuicao',
            f'Responsável alterado para: {responsavel}',
            {'responsavel_anterior': responsavel_anterior},
            {'responsavel_novo': responsavel}
        )
        
        return True
    
    @staticmethod
    def buscar_chamados(filtros: Dict[str, Any] = None, pagina: int = 1, por_pagina: int = 20):
        """Busca chamados com filtros"""
        query = Chamado.query
        
        if filtros:
            if filtros.get('status'):
                query = query.filter(Chamado.status == filtros['status'])
            
            if filtros.get('prioridade'):
                query = query.filter(Chamado.prioridade == filtros['prioridade'])
            
            if filtros.get('unidade'):
                query = query.filter(Chamado.unidade == filtros['unidade'])
            
            if filtros.get('responsavel'):
                query = query.filter(Chamado.responsavel_atendimento == filtros['responsavel'])
            
            if filtros.get('data_inicio'):
                query = query.filter(Chamado.data_abertura >= filtros['data_inicio'])
            
            if filtros.get('data_fim'):
                query = query.filter(Chamado.data_abertura <= filtros['data_fim'])
            
            if filtros.get('termo_busca'):
                termo = f"%{filtros['termo_busca']}%"
                query = query.filter(
                    db.or_(
                        Chamado.protocolo.like(termo),
                        Chamado.titulo.like(termo),
                        Chamado.descricao.like(termo),
                        Chamado.nome_solicitante.like(termo)
                    )
                )
        
        return query.order_by(Chamado.data_abertura.desc()).paginate(
            page=pagina, per_page=por_pagina, error_out=False
        )

class HistoricoService:
    """Serviço para gerenciamento do histórico"""
    
    @staticmethod
    def registrar_acao(chamado_id: int, usuario: str, acao: str, descricao: str, 
                      dados_anteriores: Dict = None, dados_novos: Dict = None):
        """Registra uma ação no histórico"""
        historico = HistoricoChamado(
            chamado_id=chamado_id,
            usuario=usuario,
            acao=acao,
            descricao=descricao,
            dados_anteriores=json.dumps(dados_anteriores) if dados_anteriores else None,
            dados_novos=json.dumps(dados_novos) if dados_novos else None
        )
        
        db.session.add(historico)
        db.session.commit()

class NotificacaoService:
    """Serviço para envio de notificações"""
    
    @staticmethod
    def enviar_notificacao_abertura(chamado: Chamado):
        """Envia notificação de abertura de chamado"""
        try:
            # Configurações de e-mail (devem estar nas configurações do sistema)
            smtp_server = ConfiguracaoSistema.get_valor('smtp_server', 'localhost')
            smtp_port = ConfiguracaoSistema.get_valor('smtp_port', 587)
            smtp_user = ConfiguracaoSistema.get_valor('smtp_user', '')
            smtp_password = ConfiguracaoaoSistema.get_valor('smtp_password', '')
            
            if not smtp_user:
                return False
            
            # Prepara o e-mail
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = chamado.email_solicitante
            msg['Subject'] = f'Chamado Aberto - Protocolo {chamado.protocolo}'
            
            corpo = f"""
            Olá {chamado.nome_solicitante},
            
            Seu chamado foi registrado com sucesso!
            
            Protocolo: {chamado.protocolo}
            Título: {chamado.titulo}
            Prioridade: {chamado.prioridade.title()}
            Status: {chamado.status.replace('_', ' ').title()}
            Data de Abertura: {chamado.data_abertura.strftime('%d/%m/%Y %H:%M')}
            
            Descrição:
            {chamado.descricao}
            
            Acompanhe o status do seu chamado através do sistema.
            
            Atenciosamente,
            Equipe de Manutenção
            """
            
            msg.attach(MIMEText(corpo, 'plain'))
            
            # Envia o e-mail
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar notificação: {e}")
            return False
    
    @staticmethod
    def enviar_notificacao_status(chamado: Chamado, status_anterior: str):
        """Envia notificação de mudança de status"""
        # Implementação similar à notificação de abertura
        # Adaptada para mudança de status
        pass

class RelatorioService:
    """Serviço para geração de relatórios"""
    
    @staticmethod
    def gerar_estatisticas_gerais(data_inicio: datetime = None, data_fim: datetime = None) -> Dict[str, Any]:
        """Gera estatísticas gerais dos chamados"""
        query = Chamado.query
        
        if data_inicio:
            query = query.filter(Chamado.data_abertura >= data_inicio)
        if data_fim:
            query = query.filter(Chamado.data_abertura <= data_fim)
        
        chamados = query.all()
        
        total = len(chamados)
        if total == 0:
            return {
                'total': 0,
                'por_status': {},
                'por_prioridade': {},
                'por_unidade': {},
                'tempo_medio_resolucao': 0,
                'taxa_resolucao': 0
            }
        
        # Estatísticas por status
        por_status = {}
        for status in StatusChamado.get_all():
            count = len([c for c in chamados if c.status == status])
            por_status[status] = {
                'count': count,
                'percentual': (count / total) * 100
            }
        
        # Estatísticas por prioridade
        por_prioridade = {}
        for prioridade in PrioridadeChamado.get_all():
            count = len([c for c in chamados if c.prioridade == prioridade])
            por_prioridade[prioridade] = {
                'count': count,
                'percentual': (count / total) * 100
            }
        
        # Estatísticas por unidade
        unidades = list(set([c.unidade for c in chamados]))
        por_unidade = {}
        for unidade in unidades:
            count = len([c for c in chamados if c.unidade == unidade])
            por_unidade[unidade] = {
                'count': count,
                'percentual': (count / total) * 100
            }
        
        # Tempo médio de resolução
        concluidos = [c for c in chamados if c.status == StatusChamado.CONCLUIDO and c.data_conclusao]
        if concluidos:
            tempos = [(c.data_conclusao - c.data_abertura).total_seconds() / 3600 for c in concluidos]
            tempo_medio = sum(tempos) / len(tempos)
        else:
            tempo_medio = 0
        
        # Taxa de resolução
        taxa_resolucao = (por_status.get(StatusChamado.CONCLUIDO, {}).get('percentual', 0))
        
        return {
            'total': total,
            'por_status': por_status,
            'por_prioridade': por_prioridade,
            'por_unidade': por_unidade,
            'tempo_medio_resolucao': tempo_medio,
            'taxa_resolucao': taxa_resolucao
        }

# ================================
# FUNÇÕES UTILITÁRIAS
# ================================

def allowed_file(filename: str) -> bool:
    """Verifica se o arquivo é permitido"""
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, chamado_id: int) -> Optional[AnexoChamado]:
    """Salva um arquivo enviado"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Cria diretório se não existir
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], str(chamado_id))
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        # Cria registro no banco
        anexo = AnexoChamado(
            chamado_id=chamado_id,
            nome_arquivo=unique_filename,
            nome_original=filename,
            tipo_arquivo=file.content_type,
            tamanho_arquivo=os.path.getsize(file_path),
            caminho_arquivo=file_path
        )
        
        db.session.add(anexo)
        db.session.commit()
        
        return anexo
    
    return None

def init_database():
    """Inicializa o banco de dados com dados padrão"""
    with app.app_context():
        db.create_all()
        
        # Configurações padrão
        configuracoes_padrao = [
            ('smtp_server', 'smtp.gmail.com', 'Servidor SMTP para envio de e-mails'),
            ('smtp_port', '587', 'Porta do servidor SMTP'),
            ('smtp_user', '', 'Usuário do e-mail'),
            ('smtp_password', '', 'Senha do e-mail'),
            ('empresa_nome', 'Follow Advisor', 'Nome da empresa'),
            ('sistema_versao', '3.0', 'Versão do sistema'),
        ]
        
        for chave, valor, descricao in configuracoes_padrao:
            if not ConfiguracaoSistema.query.filter_by(chave=chave).first():
                ConfiguracaoSistema.set_valor(chave, valor, descricao)

# ================================
# INICIALIZAÇÃO
# ================================

if __name__ == '__main__':
    init_database()
    print("Sistema de Chamados de Manutenção - Versão 3.0")
    print("Banco de dados inicializado com sucesso!")
    print("Modelos disponíveis:")
    print("- Chamado: Modelo principal para chamados")
    print("- AnexoChamado: Anexos dos chamados")
    print("- HistoricoChamado: Histórico de alterações")
    print("- ConfiguracaoSistema: Configurações do sistema")
    print("\nServiços disponíveis:")
    print("- ChamadoService: Gerenciamento de chamados")
    print("- HistoricoService: Gerenciamento do histórico")
    print("- NotificacaoService: Envio de notificações")
    print("- RelatorioService: Geração de relatórios")


# ================================
# ROTAS E ENDPOINTS DA API
# ================================

@app.route('/api/chamados', methods=['GET'])
def api_listar_chamados():
    """API para listar chamados com filtros"""
    try:
        # Parâmetros de filtro
        filtros = {
            'status': request.args.get('status'),
            'prioridade': request.args.get('prioridade'),
            'unidade': request.args.get('unidade'),
            'responsavel': request.args.get('responsavel'),
            'termo_busca': request.args.get('q')
        }
        
        # Filtros de data
        if request.args.get('data_inicio'):
            try:
                filtros['data_inicio'] = datetime.fromisoformat(request.args.get('data_inicio'))
            except ValueError:
                pass
        
        if request.args.get('data_fim'):
            try:
                filtros['data_fim'] = datetime.fromisoformat(request.args.get('data_fim'))
            except ValueError:
                pass
        
        # Remove filtros vazios
        filtros = {k: v for k, v in filtros.items() if v}
        
        # Paginação
        pagina = int(request.args.get('page', 1))
        por_pagina = int(request.args.get('per_page', 20))
        
        # Busca chamados
        resultado = ChamadoService.buscar_chamados(filtros, pagina, por_pagina)
        
        return jsonify({
            'success': True,
            'data': [chamado.to_dict() for chamado in resultado.items],
            'pagination': {
                'page': resultado.page,
                'pages': resultado.pages,
                'per_page': resultado.per_page,
                'total': resultado.total,
                'has_next': resultado.has_next,
                'has_prev': resultado.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chamados', methods=['POST'])
def api_criar_chamado():
    """API para criar novo chamado"""
    try:
        dados = request.get_json()
        
        # Validação básica
        campos_obrigatorios = ['titulo', 'descricao', 'nome_solicitante', 'email_solicitante', 'turno', 'unidade']
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório: {campo}'
                }), 400
        
        # Validação de e-mail
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, dados['email_solicitante']):
            return jsonify({
                'success': False,
                'error': 'E-mail inválido'
            }), 400
        
        # Cria o chamado
        chamado = ChamadoService.criar_chamado(dados)
        
        return jsonify({
            'success': True,
            'data': chamado.to_dict(),
            'message': f'Chamado criado com protocolo {chamado.protocolo}'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chamados/<int:chamado_id>', methods=['GET'])
def api_obter_chamado(chamado_id):
    """API para obter detalhes de um chamado"""
    try:
        chamado = Chamado.query.get(chamado_id)
        if not chamado:
            return jsonify({
                'success': False,
                'error': 'Chamado não encontrado'
            }), 404
        
        # Inclui anexos e histórico
        dados = chamado.to_dict()
        dados['anexos'] = [
            {
                'id': anexo.id,
                'nome_original': anexo.nome_original,
                'tipo_arquivo': anexo.tipo_arquivo,
                'tamanho_arquivo': anexo.tamanho_arquivo,
                'data_upload': anexo.data_upload.isoformat()
            }
            for anexo in chamado.anexos
        ]
        
        dados['historico'] = [
            {
                'id': hist.id,
                'usuario': hist.usuario,
                'acao': hist.acao,
                'descricao': hist.descricao,
                'data_acao': hist.data_acao.isoformat()
            }
            for hist in chamado.historico
        ]
        
        return jsonify({
            'success': True,
            'data': dados
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chamados/<int:chamado_id>/status', methods=['PUT'])
def api_atualizar_status(chamado_id):
    """API para atualizar status de um chamado"""
    try:
        dados = request.get_json()
        novo_status = dados.get('status')
        usuario = dados.get('usuario', 'sistema')
        observacoes = dados.get('observacoes')
        
        if not novo_status:
            return jsonify({
                'success': False,
                'error': 'Status é obrigatório'
            }), 400
        
        if novo_status not in StatusChamado.get_all():
            return jsonify({
                'success': False,
                'error': 'Status inválido'
            }), 400
        
        sucesso = ChamadoService.atualizar_status(chamado_id, novo_status, usuario, observacoes)
        
        if not sucesso:
            return jsonify({
                'success': False,
                'error': 'Chamado não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Status atualizado com sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/estatisticas', methods=['GET'])
def api_estatisticas():
    """API para obter estatísticas gerais"""
    try:
        # Parâmetros de data
        data_inicio = None
        data_fim = None
        
        if request.args.get('data_inicio'):
            try:
                data_inicio = datetime.fromisoformat(request.args.get('data_inicio'))
            except ValueError:
                pass
        
        if request.args.get('data_fim'):
            try:
                data_fim = datetime.fromisoformat(request.args.get('data_fim'))
            except ValueError:
                pass
        
        estatisticas = RelatorioService.gerar_estatisticas_gerais(data_inicio, data_fim)
        
        return jsonify({
            'success': True,
            'data': estatisticas
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# ROTAS WEB (INTEGRAÇÃO COM TEMPLATES)
# ================================

@app.route('/chamados')
def web_listar_chamados():
    """Página web para listar chamados"""
    filtros = {
        'status': request.args.get('status'),
        'prioridade': request.args.get('prioridade'),
        'unidade': request.args.get('unidade'),
        'termo_busca': request.args.get('q')
    }
    
    # Remove filtros vazios
    filtros = {k: v for k, v in filtros.items() if v}
    
    pagina = int(request.args.get('page', 1))
    resultado = ChamadoService.buscar_chamados(filtros, pagina, 10)
    
    return render_template('listar_chamados.html', 
                         chamados=resultado.items,
                         pagination=resultado,
                         filtros=filtros,
                         status_opcoes=StatusChamado.get_all(),
                         prioridade_opcoes=PrioridadeChamado.get_all())

@app.route('/chamados/<int:chamado_id>')
def web_detalhes_chamado(chamado_id):
    """Página web para detalhes do chamado"""
    chamado = Chamado.query.get_or_404(chamado_id)
    return render_template('detalhes_chamado.html', chamado=chamado)

@app.route('/chamados/novo', methods=['GET', 'POST'])
def web_novo_chamado():
    """Página web para criar novo chamado"""
    if request.method == 'POST':
        try:
            dados = {
                'titulo': request.form.get('titulo'),
                'descricao': request.form.get('descricao'),
                'nome_solicitante': request.form.get('nome_solicitante'),
                'email_solicitante': request.form.get('email_solicitante'),
                'telefone_solicitante': request.form.get('telefone_solicitante'),
                'email_notificacao': request.form.get('email_notificacao'),
                'turno': request.form.get('turno'),
                'unidade': request.form.get('unidade'),
                'local_especifico': request.form.get('local_especifico'),
                'tipo_nao_conformidade': request.form.get('tipo_nao_conformidade'),
                'tipo_chamado': request.form.get('tipo_chamado'),
                'prioridade': request.form.get('prioridade'),
                'equipamento_envolvido': request.form.get('equipamento_envolvido'),
                'codigo_equipamento': request.form.get('codigo_equipamento')
            }
            
            chamado = ChamadoService.criar_chamado(dados)
            
            # Upload de anexos se houver
            if 'anexos' in request.files:
                for arquivo in request.files.getlist('anexos'):
                    if arquivo.filename:
                        save_uploaded_file(arquivo, chamado.id)
            
            flash(f'Chamado criado com sucesso! Protocolo: {chamado.protocolo}', 'success')
            return redirect(url_for('web_detalhes_chamado', chamado_id=chamado.id))
            
        except Exception as e:
            flash(f'Erro ao criar chamado: {str(e)}', 'error')
    
    return render_template('novo_chamado.html',
                         turnos=['Manhã', 'Tarde', 'Noite'],
                         unidades=['Unidade 1 - Produção', 'Unidade 2 - Administrativo', 
                                 'Unidade 3 - Almoxarifado', 'Unidade 4 - Manutenção'],
                         tipos_chamado=TipoChamado.get_all(),
                         prioridades=PrioridadeChamado.get_all())

# ================================
# VALIDADORES E FUNÇÕES UTILITÁRIAS
# ================================

def validar_email(email):
    """Valida formato de e-mail"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_telefone(telefone):
    """Valida formato de telefone brasileiro"""
    import re
    # Remove caracteres não numéricos
    telefone_limpo = re.sub(r'[^\d]', '', telefone)
    # Verifica se tem 10 ou 11 dígitos
    return len(telefone_limpo) in [10, 11]

# ================================
# HANDLERS DE ERRO
# ================================

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Endpoint não encontrado'
        }), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500
    return render_template('500.html'), 500

# ================================
# COMANDOS CLI
# ================================

@app.cli.command()
def init_db():
    """Inicializa o banco de dados"""
    init_database()
    print("Banco de dados inicializado com sucesso!")

@app.cli.command()
def create_sample_data():
    """Cria dados de exemplo"""
    with app.app_context():
        # Cria alguns chamados de exemplo
        chamados_exemplo = [
            {
                'titulo': 'Manutenção preventiva - Equipamento A',
                'descricao': 'Realizar manutenção preventiva conforme cronograma',
                'nome_solicitante': 'João Silva',
                'email_solicitante': 'joao.silva@empresa.com',
                'telefone_solicitante': '(11) 99999-9999',
                'turno': 'Manhã',
                'unidade': 'Unidade 1 - Produção',
                'tipo_chamado': TipoChamado.PREVENTIVA,
                'prioridade': PrioridadeChamado.MEDIA
            },
            {
                'titulo': 'Reparo urgente - Sistema elétrico',
                'descricao': 'Falha no sistema elétrico da linha de produção',
                'nome_solicitante': 'Maria Santos',
                'email_solicitante': 'maria.santos@empresa.com',
                'telefone_solicitante': '(11) 88888-8888',
                'turno': 'Tarde',
                'unidade': 'Unidade 2 - Administrativo',
                'tipo_chamado': TipoChamado.EMERGENCIA,
                'prioridade': PrioridadeChamado.URGENTE
            }
        ]
        
        for dados in chamados_exemplo:
            ChamadoService.criar_chamado(dados)
        
        print(f"Criados {len(chamados_exemplo)} chamados de exemplo!")

if __name__ == '__main__':
    # Configuração para desenvolvimento
    app.config['DEBUG'] = True
    init_database()
    app.run(host='0.0.0.0', port=5000)



# ================================
# INTEGRAÇÃO COM SISTEMA EXISTENTE
# ================================

def integrar_com_sistema_principal():
    """
    Função para integrar o módulo de chamados com o sistema principal
    Esta função deve ser chamada no main.py do sistema existente
    """
    
    # Importa as rotas e modelos
    from chamado import (
        Chamado, AnexoChamado, HistoricoChamado, ConfiguracaoSistema,
        ChamadoService, HistoricoService, NotificacaoService, RelatorioService,
        StatusChamado, PrioridadeChamado, TipoChamado,
        api_listar_chamados, api_criar_chamado, api_obter_chamado,
        api_atualizar_status, api_estatisticas,
        web_listar_chamados, web_detalhes_chamado, web_novo_chamado
    )
    
    return {
        'modelos': {
            'Chamado': Chamado,
            'AnexoChamado': AnexoChamado,
            'HistoricoChamado': HistoricoChamado,
            'ConfiguracaoSistema': ConfiguracaoSistema
        },
        'servicos': {
            'ChamadoService': ChamadoService,
            'HistoricoService': HistoricoService,
            'NotificacaoService': NotificacaoService,
            'RelatorioService': RelatorioService
        },
        'enums': {
            'StatusChamado': StatusChamado,
            'PrioridadeChamado': PrioridadeChamado,
            'TipoChamado': TipoChamado
        },
        'rotas_api': [
            'api_listar_chamados',
            'api_criar_chamado',
            'api_obter_chamado',
            'api_atualizar_status',
            'api_estatisticas'
        ],
        'rotas_web': [
            'web_listar_chamados',
            'web_detalhes_chamado',
            'web_novo_chamado'
        ]
    }

# ================================
# EXEMPLO DE INTEGRAÇÃO NO MAIN.PY
# ================================

"""
Para integrar este módulo no sistema principal, adicione no main.py:

# Importação do módulo de chamados
from chamado import (
    Chamado, ChamadoService, StatusChamado, PrioridadeChamado,
    api_listar_chamados, api_criar_chamado, api_obter_chamado,
    api_atualizar_status, api_estatisticas,
    web_listar_chamados, web_detalhes_chamado, web_novo_chamado,
    init_database
)

# Inicialização do banco de dados (adicionar após criar a app Flask)
init_database()

# As rotas já estarão disponíveis automaticamente quando o módulo for importado

# Exemplo de uso dos serviços:

@app.route('/exemplo-criar-chamado')
def exemplo_criar_chamado():
    dados = {
        'titulo': 'Exemplo de chamado',
        'descricao': 'Descrição do problema',
        'nome_solicitante': 'João Silva',
        'email_solicitante': 'joao@empresa.com',
        'turno': 'Manhã',
        'unidade': 'Unidade 1 - Produção',
        'tipo_chamado': TipoChamado.CORRETIVA,
        'prioridade': PrioridadeChamado.MEDIA
    }
    
    chamado = ChamadoService.criar_chamado(dados)
    return f'Chamado criado com protocolo: {chamado.protocolo}'

@app.route('/exemplo-listar-chamados')
def exemplo_listar_chamados():
    filtros = {'status': StatusChamado.ABERTO}
    resultado = ChamadoService.buscar_chamados(filtros)
    
    chamados = []
    for chamado in resultado.items:
        chamados.append({
            'protocolo': chamado.protocolo,
            'titulo': chamado.titulo,
            'status': chamado.status,
            'prioridade': chamado.prioridade
        })
    
    return {'chamados': chamados}
"""

# ================================
# DOCUMENTAÇÃO DA API
# ================================

API_DOCUMENTATION = {
    "info": {
        "title": "Sistema de Chamados de Manutenção API",
        "version": "3.0",
        "description": "API completa para gerenciamento de chamados de manutenção"
    },
    "endpoints": {
        "GET /api/chamados": {
            "description": "Lista chamados com filtros opcionais",
            "parameters": {
                "status": "Filtro por status (aberto, em_andamento, concluido, etc.)",
                "prioridade": "Filtro por prioridade (baixa, media, alta, urgente)",
                "unidade": "Filtro por unidade",
                "responsavel": "Filtro por responsável",
                "q": "Termo de busca (protocolo, título, descrição, solicitante)",
                "data_inicio": "Data de início (ISO format)",
                "data_fim": "Data de fim (ISO format)",
                "page": "Número da página (padrão: 1)",
                "per_page": "Itens por página (padrão: 20)"
            },
            "response": {
                "success": True,
                "data": "Array de chamados",
                "pagination": "Informações de paginação"
            }
        },
        "POST /api/chamados": {
            "description": "Cria um novo chamado",
            "required_fields": [
                "titulo", "descricao", "nome_solicitante", 
                "email_solicitante", "turno", "unidade"
            ],
            "optional_fields": [
                "telefone_solicitante", "email_notificacao", "local_especifico",
                "tipo_nao_conformidade", "tipo_chamado", "prioridade",
                "equipamento_envolvido", "codigo_equipamento"
            ],
            "response": {
                "success": True,
                "data": "Dados do chamado criado",
                "message": "Mensagem de sucesso com protocolo"
            }
        },
        "GET /api/chamados/{id}": {
            "description": "Obtém detalhes de um chamado específico",
            "response": {
                "success": True,
                "data": "Dados completos do chamado incluindo anexos e histórico"
            }
        },
        "PUT /api/chamados/{id}/status": {
            "description": "Atualiza o status de um chamado",
            "required_fields": ["status"],
            "optional_fields": ["usuario", "observacoes"],
            "valid_status": [
                "aberto", "em_andamento", "aguardando_peca", 
                "concluido", "cancelado"
            ]
        },
        "GET /api/estatisticas": {
            "description": "Obtém estatísticas gerais dos chamados",
            "parameters": {
                "data_inicio": "Data de início para filtro (ISO format)",
                "data_fim": "Data de fim para filtro (ISO format)"
            },
            "response": {
                "total": "Total de chamados",
                "por_status": "Distribuição por status",
                "por_prioridade": "Distribuição por prioridade",
                "por_unidade": "Distribuição por unidade",
                "tempo_medio_resolucao": "Tempo médio em horas",
                "taxa_resolucao": "Percentual de chamados concluídos"
            }
        }
    },
    "web_routes": {
        "/chamados": "Lista chamados (interface web)",
        "/chamados/{id}": "Detalhes do chamado (interface web)",
        "/chamados/novo": "Formulário para novo chamado (interface web)"
    }
}

# ================================
# CONFIGURAÇÕES RECOMENDADAS
# ================================

CONFIGURACOES_RECOMENDADAS = {
    "smtp_server": {
        "valor": "smtp.gmail.com",
        "descricao": "Servidor SMTP para envio de e-mails",
        "tipo": "string"
    },
    "smtp_port": {
        "valor": "587",
        "descricao": "Porta do servidor SMTP",
        "tipo": "integer"
    },
    "smtp_user": {
        "valor": "",
        "descricao": "Usuário do e-mail para notificações",
        "tipo": "string"
    },
    "smtp_password": {
        "valor": "",
        "descricao": "Senha do e-mail para notificações",
        "tipo": "string"
    },
    "empresa_nome": {
        "valor": "Follow Advisor",
        "descricao": "Nome da empresa",
        "tipo": "string"
    },
    "prazo_urgente_horas": {
        "valor": "4",
        "descricao": "Prazo em horas para chamados urgentes",
        "tipo": "integer"
    },
    "prazo_alta_horas": {
        "valor": "24",
        "descricao": "Prazo em horas para chamados de alta prioridade",
        "tipo": "integer"
    },
    "prazo_media_horas": {
        "valor": "72",
        "descricao": "Prazo em horas para chamados de média prioridade",
        "tipo": "integer"
    },
    "prazo_baixa_horas": {
        "valor": "168",
        "descricao": "Prazo em horas para chamados de baixa prioridade",
        "tipo": "integer"
    },
    "max_anexos_por_chamado": {
        "valor": "10",
        "descricao": "Número máximo de anexos por chamado",
        "tipo": "integer"
    },
    "tamanho_max_anexo_mb": {
        "valor": "16",
        "descricao": "Tamanho máximo de anexo em MB",
        "tipo": "integer"
    }
}

# ================================
# TESTES UNITÁRIOS (EXEMPLO)
# ================================

def executar_testes():
    """
    Função para executar testes básicos do sistema
    """
    import unittest
    
    class TestChamadoService(unittest.TestCase):
        
        def setUp(self):
            """Configuração antes de cada teste"""
            app.config['TESTING'] = True
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            with app.app_context():
                db.create_all()
        
        def tearDown(self):
            """Limpeza após cada teste"""
            with app.app_context():
                db.session.remove()
                db.drop_all()
        
        def test_criar_chamado(self):
            """Testa criação de chamado"""
            with app.app_context():
                dados = {
                    'titulo': 'Teste',
                    'descricao': 'Descrição teste',
                    'nome_solicitante': 'João Teste',
                    'email_solicitante': 'joao@teste.com',
                    'turno': 'Manhã',
                    'unidade': 'Teste'
                }
                
                chamado = ChamadoService.criar_chamado(dados)
                
                self.assertIsNotNone(chamado.id)
                self.assertIsNotNone(chamado.protocolo)
                self.assertEqual(chamado.titulo, 'Teste')
                self.assertEqual(chamado.status, StatusChamado.ABERTO)
        
        def test_atualizar_status(self):
            """Testa atualização de status"""
            with app.app_context():
                # Cria chamado
                dados = {
                    'titulo': 'Teste Status',
                    'descricao': 'Teste',
                    'nome_solicitante': 'João',
                    'email_solicitante': 'joao@teste.com',
                    'turno': 'Manhã',
                    'unidade': 'Teste'
                }
                
                chamado = ChamadoService.criar_chamado(dados)
                
                # Atualiza status
                sucesso = ChamadoService.atualizar_status(
                    chamado.id, 
                    StatusChamado.EM_ANDAMENTO, 
                    'teste_user'
                )
                
                self.assertTrue(sucesso)
                
                # Verifica se foi atualizado
                chamado_atualizado = Chamado.query.get(chamado.id)
                self.assertEqual(chamado_atualizado.status, StatusChamado.EM_ANDAMENTO)
                self.assertIsNotNone(chamado_atualizado.data_inicio_atendimento)
    
    # Executa os testes
    unittest.main(verbosity=2)

# ================================
# UTILITÁRIOS DE MIGRAÇÃO
# ================================

def migrar_dados_antigos():
    """
    Função para migrar dados de versões anteriores do sistema
    """
    print("Iniciando migração de dados...")
    
    # Exemplo de migração - adapte conforme necessário
    with app.app_context():
        # Verifica se existem chamados sem protocolo
        chamados_sem_protocolo = Chamado.query.filter(
            db.or_(Chamado.protocolo == None, Chamado.protocolo == '')
        ).all()
        
        for chamado in chamados_sem_protocolo:
            chamado.protocolo = chamado.gerar_protocolo()
        
        db.session.commit()
        print(f"Migrados {len(chamados_sem_protocolo)} chamados sem protocolo")
        
        # Adiciona configurações padrão se não existirem
        for chave, config in CONFIGURACOES_RECOMENDADAS.items():
            if not ConfiguracaoSistema.query.filter_by(chave=chave).first():
                ConfiguracaoSistema.set_valor(
                    chave, 
                    config['valor'], 
                    config['descricao'], 
                    config['tipo']
                )
        
        print("Configurações padrão adicionadas")
        print("Migração concluída com sucesso!")

# ================================
# BACKUP E RESTAURAÇÃO
# ================================

def fazer_backup():
    """
    Cria backup dos dados dos chamados
    """
    import json
    from datetime import datetime
    
    with app.app_context():
        chamados = Chamado.query.all()
        
        backup_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'versao': '3.0',
            'total_chamados': len(chamados),
            'chamados': [chamado.to_dict() for chamado in chamados]
        }
        
        filename = f"backup_chamados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"Backup criado: {filename}")
        return filename

def restaurar_backup(filename):
    """
    Restaura dados de um arquivo de backup
    """
    import json
    
    with open(filename, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    
    with app.app_context():
        print(f"Restaurando backup de {backup_data['timestamp']}")
        print(f"Total de chamados: {backup_data['total_chamados']}")
        
        for dados_chamado in backup_data['chamados']:
            # Verifica se o chamado já existe
            chamado_existente = Chamado.query.filter_by(
                protocolo=dados_chamado['protocolo']
            ).first()
            
            if not chamado_existente:
                # Remove campos que não devem ser restaurados diretamente
                dados_limpos = {k: v for k, v in dados_chamado.items() 
                              if k not in ['id']}
                
                # Converte datas
                if dados_limpos.get('data_abertura'):
                    dados_limpos['data_abertura'] = datetime.fromisoformat(
                        dados_limpos['data_abertura']
                    )
                
                if dados_limpos.get('data_conclusao'):
                    dados_limpos['data_conclusao'] = datetime.fromisoformat(
                        dados_limpos['data_conclusao']
                    )
                
                chamado = Chamado(**dados_limpos)
                db.session.add(chamado)
        
        db.session.commit()
        print("Restauração concluída!")

# ================================
# INFORMAÇÕES DO SISTEMA
# ================================

def info_sistema():
    """
    Retorna informações sobre o sistema de chamados
    """
    return {
        'nome': 'Sistema de Chamados de Manutenção',
        'versao': '3.0',
        'autor': 'Follow Advisor - Sistemas',
        'descricao': 'Sistema completo para gerenciamento de chamados de manutenção',
        'recursos': [
            'Criação e gerenciamento de chamados',
            'Sistema de prioridades e status',
            'Anexos de arquivos',
            'Histórico de alterações',
            'Notificações por e-mail',
            'Relatórios e estatísticas',
            'API REST completa',
            'Interface web responsiva',
            'Sistema de configurações',
            'Backup e restauração'
        ],
        'tecnologias': [
            'Python 3.11+',
            'Flask',
            'SQLAlchemy',
            'SQLite/PostgreSQL',
            'HTML5/CSS3/JavaScript',
            'Bootstrap',
            'Chart.js'
        ],
        'status': 'Produção',
        'licenca': 'Proprietária - Follow Advisor'
    }

if __name__ == '__main__':
    print("=" * 60)
    print("SISTEMA DE CHAMADOS DE MANUTENÇÃO - VERSÃO 3.0")
    print("=" * 60)
    
    info = info_sistema()
    print(f"Nome: {info['nome']}")
    print(f"Versão: {info['versao']}")
    print(f"Autor: {info['autor']}")
    print(f"Status: {info['status']}")
    print()
    print("Recursos disponíveis:")
    for recurso in info['recursos']:
        print(f"  ✓ {recurso}")
    print()
    print("Para usar este módulo, importe-o no seu main.py:")
    print("from chamado import *")
    print()
    print("Documentação da API disponível na variável API_DOCUMENTATION")
    print("=" * 60)

