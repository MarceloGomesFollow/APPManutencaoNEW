from flask import Blueprint, render_template
chamado_bp = Blueprint("chamado", __name__, url_prefix="/chamados")

@chamado_bp.route("/", endpoint="index")   # <--  nome da rota = chamado.index
def index():
    return render_template("painel_chamados.html")