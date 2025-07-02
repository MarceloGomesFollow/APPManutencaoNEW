# src/services/chamado_service.py

class ChamadoService:
    def __init__(self):
        # Pode receber db, config, etc
        pass

    def criar_chamado(self, titulo, descricao, local_id):
        # Aqui vai a lógica real (ex: salvar no banco)
        # No exemplo, só printa os dados
        print(f"Chamado criado: Título={titulo}, Descrição={descricao}, Local={local_id}")
        return {"status": "sucesso", "mensagem": "Chamado criado com sucesso"}
