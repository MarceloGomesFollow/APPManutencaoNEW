# src/services/chamado_service.py

#class ChamadoService:
    #def __init__(self):
        # Pode receber db, config, etc
      #  pass

  #  def criar_chamado(self, titulo, descricao, local_id):
        # Aqui vai a lógica real (ex: salvar no banco)
        # No exemplo, só printa os dados
     #   print(f"Chamado criado: Título={titulo}, Descrição={descricao}, Local={local_id}")
      #  return {"status": "sucesso", "mensagem": "Chamado criado com sucesso"}


# src/services/chamado_service.py

from src.models import db
from src.models.chamado import Chamado
from datetime import datetime


class ChamadoService:
    def __init__(self):
        pass

    def criar_chamado(self, dados: dict):
        """Cria um novo chamado de manutenção a partir de um dicionário de dados."""
        chamado = Chamado(
            protocolo=Chamado.gerar_proximo_protocolo(),
            cliente_nome=dados.get('nome_solicitante'),
            cliente_email=dados.get('email_solicitante'),
            cliente_telefone=dados.get('telefone_solicitante'),
            email_requisitante=dados.get('email_notificacao'),
            telefone_requisitante=dados.get('telefone_solicitante'),

            titulo=dados.get('titulo'),
            descricao=dados.get('descricao'),
            prioridade=dados.get('prioridade'),

            id_turno=dados.get('turno'),
            id_unidade=dados.get('unidade'),
            id_nao_conformidade=dados.get('tipo_nao_conformidade'),
            id_local_apontamento=dados.get('local_especifico'),
            id_status=1,  # status inicial (se você usa 1 como "aberto")

            data_solicitacao=datetime.utcnow(),
            status="aberto"
        )

        db.session.add(chamado)
        db.session.commit()
        return chamado
