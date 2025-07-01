from flask_sqlalchemy import SQLAlchemy

# Instância única de SQLAlchemy para toda a aplicação
db = SQLAlchemy()

# Importa todas as models APÓS a inicialização do db
from src.models.user import User
from src.models.perfil import Perfil
from src.models.chamado import Chamado
from src.models.turno import Turno
from src.models.unidade import Unidade
from src.models.nao_conformidade import NaoConformidade
from src.models.status_chamado import StatusChamado
from src.models.contato_notificacao import ContatoNotificacaoManutencao
from src.models.historico_chamado import HistoricoChamado
from src.models.historico_notificacoes import HistoricoNotificacoes
# Importe local_apontamento por último para evitar circularidade
from src.models.local_apontamento import LocalApontamento
