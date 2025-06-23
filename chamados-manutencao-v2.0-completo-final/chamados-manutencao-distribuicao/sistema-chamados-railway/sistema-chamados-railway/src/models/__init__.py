# src/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

# 1) instância única de DB para toda a app
db = SQLAlchemy()

# 2) importe aqui **TODAS** as suas models,
#    para que o SQLAlchemy as conheça antes de criar os relacionamentos.
from src.models.user import User
from src.models.perfil import Perfil
from src.models.chamado import Chamado
from src.models.turno import Turno
from src.models.unidade import Unidade
from src.models.local_apontamento import LocalApontamento
from src.models.nao_conformidade import NaoConformidade
from src.models.status_chamado import StatusChamado
from src.models.contato_notificacao import ContatoNotificacaoManutencao
# … importe outras models conforme necessário
