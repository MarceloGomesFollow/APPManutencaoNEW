from flask import Blueprint

chamado_bp = Blueprint('chamado', __name__)

@chamado_bp.route('/chamados/teste', methods=['GET'])
def teste():
    return {'mensagem': 'Rota de chamado funcionando'}

