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
    def criar_chamado(self, dados: dict):
        chamado = Chamado(
            protocolo=Chamado.gerar_proximo_protocolo(),
            cliente_nome=dados.get('cliente_nome'),       # mudou aqui
            cliente_email=dados.get('cliente_email'),
            cliente_telefone=dados.get('cliente_telefone'),
            email_requisitante=dados.get('email_requisitante'),
            telefone_requisitante=dados.get('telefone_requisitante'),

            titulo=dados.get('titulo'),
            descricao=dados.get('descricao'),
            prioridade=dados.get('prioridade'),

            id_turno=int(dados.get('id_turno')) if dados.get('id_turno') else None,
            id_unidade=int(dados.get('id_unidade')) if dados.get('id_unidade') else None,
            id_nao_conformidade=int(dados.get('id_nao_conformidade')) if dados.get('id_nao_conformidade') else None,
            id_local_apontamento=int(dados.get('id_local_apontamento')) if dados.get('id_local_apontamento') else None,
            id_status=1,

            data_solicitacao=datetime.utcnow(),
            status="aberto"
        )

        db.session.add(chamado)
        db.session.commit()
        return chamado
