# src/models/__init__.py

from flask_sqlalchemy import SQLAlchemy

# Instância única de SQLAlchemy para toda a aplicação
db = SQLAlchemy()

# Importa todas as models para registrar no metadata antes de operações de ORM
from src.models.user import User
from src.models.perfil import Perfil
from src.models.chamado import Chamado
from src.models.turno import Turno
from src.models.unidade import Unidade
from src.models.local_apontamento import LocalApontamento
from src.models.nao_conformidade import NaoConformidade
from src.models.status_chamado import StatusChamado
from src.models.contato_notificacao import ContatoNotificacaoManutencao
from src.models.historico_chamado import HistoricoChamado
from src.models.historico_notificacoes import HistoricoNotificacoes
# ... importe outras models conforme necessário

