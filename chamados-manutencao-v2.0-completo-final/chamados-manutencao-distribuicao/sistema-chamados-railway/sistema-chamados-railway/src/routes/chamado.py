from flask import Blueprint, render_template, request, session, redirect, url_for

chamado_bp = Blueprint("chamado", __name__, url_prefix="/chamados")

@chamado_bp.route("/", endpoint="index")
def index():
    return render_template("painel_chamados.html")

@chamado_bp.route("/abrir", endpoint="abrir_chamado")
def abrir_chamado():
    return render_template("abrir_chamado.html")

@chamado_bp.route("/detalhes/<string:protocolo>", endpoint="detalhes_chamado")
def detalhes_chamado(protocolo):
    return render_template("detalhes_chamado.html", protocolo=protocolo)

@chamado_bp.route("/contatos", endpoint="gerenciar_contatos")
def gerenciar_contatos():
    return render_template("gerenciar_contatos.html")

@chamado_bp.route("/relatorio", endpoint="relatorio")
def relatorio():
    return render_template("relatorio.html")

@chamado_bp.route("/admin", endpoint="painel_admin")
def painel_admin():
    return render_template("painel_admin.html")

@chamado_bp.route("/supervisor", endpoint="painel_supervisor")
def painel_supervisor():
    return render_template("painel_supervisor.html")

@chamado_bp.route("/login", endpoint="supervisor_login")
def supervisor_login():
    return render_template("supervisor_login.html")

@chamado_bp.route("/logout", endpoint="supervisor_logout")
def supervisor_logout():
    session.pop("supervisor", None)
    return redirect(url_for("chamado.index"))
