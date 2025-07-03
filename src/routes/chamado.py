from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from src.services.chamado_service import ChamadoService
from src.models import LocalApontamento, Turno, Unidade, NaoConformidade

# 1) Importa o modelo para usar no relatório (será carregado dentro das funções após init_app)
#    Isso garante que o SQLAlchemy já esteja inicializado.
chamado_bp = Blueprint("chamado", __name__, url_prefix="/chamados")

# 2) ROTA INDEX: lista todos os chamados e renderiza index.html
@chamado_bp.route("/", endpoint="index")
def index():
    # 1) Import dinâmico do modelo Chamado após db.init_app(app)
    from src.models.chamado import Chamado

    # Busca todos os chamados no banco
    chamados = Chamado.query.all()
    # Passa a lista para o template
    return render_template("index.html", chamados=chamados)

# 3) ROTA PARA ABRIR CHAMADO
@chamado_bp.route("/abrir", endpoint="abrir_chamado", methods=["GET", "POST"])
def abrir_chamado():
    if request.method == "POST":
        try:
            dados = {
    'cliente_nome': request.form.get('cliente_nome'),
    'cliente_email': request.form.get('cliente_email'),
    'cliente_telefone': request.form.get('cliente_telefone'),
    'email_requisitante': request.form.get('email_requisitante'),
    'telefone_requisitante': request.form.get('cliente_telefone'),  # opcional
    'titulo': request.form.get('titulo'),
    'descricao': request.form.get('descricao'),
    'prioridade': request.form.get('prioridade'),
    'turno': request.form.get('id_turno'),
    'unidade': request.form.get('id_unidade'),
    'local_especifico': request.form.get('id_local_apontamento'),
    'tipo_nao_conformidade': request.form.get('id_nao_conformidade'),
    'equipamento_envolvido': request.form.get('equipamento_envolvido'),
    'codigo_equipamento': request.form.get('codigo_equipamento'),
}
            service = ChamadoService()
            chamado = service.criar_chamado(dados)  # <-- CORRETO

            # Upload de anexos se houver
            if 'anexos' in request.files:
                for arquivo in request.files.getlist('anexos'):
                    if arquivo.filename:
                        save_uploaded_file(arquivo, chamado.id)

            flash(f'Chamado criado com sucesso! Protocolo: {chamado.protocolo}', 'success')
            return redirect(url_for('web_detalhes_chamado', chamado_id=chamado.id))

        except Exception as e:
            flash(f'Erro ao criar chamado: {str(e)}', 'error')

    # Se for GET ou erro no POST
    dados = {
        "locais_apontamento": LocalApontamento.query.filter_by(ativo=True).all(),
        "turnos": Turno.query.filter_by(ativo=True).all(),
        "unidades": Unidade.query.filter_by(ativo=True).all(),
        "nao_conformidades": NaoConformidade.query.filter_by(ativo=True).all()
    }
    return render_template("abrir_chamado.html", dados=dados)
# 4) ROTA DE DETALHES, passando o protocolo para o template
@chamado_bp.route("/detalhes/<string:protocolo>", endpoint="detalhes_chamado")
def detalhes_chamado(protocolo):
    # 1) Import dinâmico do modelo Chamado
    from src.models.chamado import Chamado

    # Busca o chamado ou retorna 404
    chamado = Chamado.query.filter_by(protocolo=protocolo).first_or_404()
    return render_template("detalhes_chamado.html", chamado=chamado)

# 5) ROTA DE CONTATOS
@chamado_bp.route("/contatos", endpoint="gerenciar_contatos")
def gerenciar_contatos():
    return render_template("gerenciar_contatos.html")

# 6) ROTA DE RELATÓRIO: calcula estatísticas e passa para o template
@chamado_bp.route("/relatorio", endpoint="relatorio")
def relatorio():
    # 1) Import dinâmico do modelo Chamado
    from src.models.chamado import Chamado

    # Conta o total de chamados no banco
    total = Chamado.query.count()
    estatisticas = {
        'total_chamados': total,
        # você pode incluir outras métricas aqui, por ex.:
        # 'abertos': Chamado.query.filter_by(status='aberto').count(),
        # 'fechados': Chamado.query.filter_by(status='fechado').count(),
    }
    # Renderiza passando o dicionário estatisticas
    return render_template("relatorio.html", estatisticas=estatisticas)

# 7) PAINEL ADMIN
@chamado_bp.route("/admin", endpoint="painel_admin")
def painel_admin():
    return render_template("painel_admin.html")

# 8) PAINEL SUPERVISOR
@chamado_bp.route("/supervisor", endpoint="painel_supervisor")
def painel_supervisor():
    # Import dinâmico do modelo Chamado
    from src.models.chamado import Chamado

    # Conta o total de chamados no banco
    total = Chamado.query.count()
    estatisticas = {
        'total_chamados': total,
        # Adicione outras métricas, se necessário, ex.:
        # 'abertos': Chamado.query.filter_by(status='aberto').count(),
        # 'fechados': Chamado.query.filter_by(status='fechado').count(),
    }
    return render_template("painel_supervisor.html", estatisticas=estatisticas)

# 9) LOGIN SUPERVISOR
@chamado_bp.route("/login", endpoint="supervisor_login", methods=["GET", "POST"])
def supervisor_login():
    if request.method == "POST":
        # Validar senha e setar session['supervisor_logged_in']
        pass
    return render_template("supervisor_login.html")

# 10) LOGOUT SUPERVISOR: limpa sessão e volta para index
@chamado_bp.route("/logout", endpoint="supervisor_logout")
def supervisor_logout():
    session.pop("supervisor_logged_in", None)
    return redirect(url_for("chamado.index"))

