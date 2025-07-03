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


from src.models import Chamado
from datetime import datetime

class ChamadoService:
    def __init__(self):
        pass

    def criar_chamado(self, titulo, descricao, local_id):
        chamado = Chamado(
            titulo=titulo,
            descricao=descricao,
            local_especifico=local_id,
            status="Aberto",
            data_criacao=datetime.utcnow(),
            protocolo=self.gerar_protocolo()
        )

        db.session.add(chamado)
        db.session.commit()
        return chamado

    def gerar_protocolo(self):
        
        from uuid import uuid4
        return str(uuid4())[:8].upper()
