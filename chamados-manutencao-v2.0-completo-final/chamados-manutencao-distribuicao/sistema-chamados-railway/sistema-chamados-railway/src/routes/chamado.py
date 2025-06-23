from flask import Blueprint, render_template, request, session, redirect, url_for
from src.models.chamado import Chamado  # 1) Importa o modelo para usar no relatorio

chamado_bp = Blueprint("chamado", __name__, url_prefix="/chamados")

# 2) ROTA INDEX: lista todos os chamados e renderiza index.html
@chamado_bp.route("/", endpoint="index")
def index():
    # Busca todos os chamados no banco
    chamados = Chamado.query.all()
    # Passa a lista para o template
    return render_template("index.html", chamados=chamados)

# 3) ROTA PARA ABRIR CHAMADO
@chamado_bp.route("/abrir", endpoint="abrir_chamado")
def abrir_chamado():
    return render_template("abrir_chamado.html")

# 4) ROTA DE DETALHES, passando o protocolo para o template
@chamado_bp.route("/detalhes/<string:protocolo>", endpoint="detalhes_chamado")
def detalhes_chamado(protocolo):
    # Aqui você poderia buscar Chamado.query.filter_by(protocolo=protocolo).first()
    return render_template("detalhes_chamado.html", protocolo=protocolo)

# 5) ROTA DE CONTATOS
@chamado_bp.route("/contatos", endpoint="gerenciar_contatos")
def gerenciar_contatos():
    return render_template("gerenciar_contatos.html")

# 6) ROTA DE RELATÓRIO: calcula estatísticas e passa para o template
@chamado_bp.route("/relatorio", endpoint="relatorio")
def relatorio():
    # Conta o total de chamados no banco
    total = Chamado.query.count()
    estatisticas = {
        'total_chamados': total,
        # você pode incluir outras métricas aqui, por ex.:
        # 'abertos': Chamado.query.filter_by(status='aberto').count(),
        # 'fechados': Chamado.query.filter_by(status='fechado').count(),
    }
    # renderiza passando o dicionário estatisticas
    return render_template("relatorio.html", estatisticas=estatisticas)

# 7) PAINEL ADMIN
@chamado_bp.route("/admin", endpoint="painel_admin")
def painel_admin():
    return render_template("painel_admin.html")

# 8) PAINEL SUPERVISOR
@chamado_bp.route("/supervisor", endpoint="painel_supervisor")
def painel_supervisor():
    return render_template("painel_supervisor.html")

# 9) LOGIN SUPERVISOR
@chamado_bp.route("/login", endpoint="supervisor_login")
def supervisor_login():
    return render_template("supervisor_login.html")

# 10) LOGOUT SUPERVISOR: limpa sessão e volta para index
@chamado_bp.route("/logout", endpoint="supervisor_logout")
def supervisor_logout():
    session.pop("supervisor", None)
    return redirect(url_for("chamado.index"))

