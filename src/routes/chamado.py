from datetime import datetime
from uuid import uuid4

from flask import Blueprint, render_template, request, session, redirect, url_for, flash, Response, stream_with_context
from flask import jsonify
from sqlalchemy import func
from sqlalchemy.sql.functions import current_user

from src.models import LocalApontamento, Turno, Unidade, NaoConformidade, Chamado
from src.models import db
from src.services.chamado_service import ChamadoService
from src.services.cloudflare_service import upload_file_to_r2, download_file_from_r2

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
    'telefone_requisitante': request.form.get('telefone_requisitante'),
    'titulo': request.form.get('titulo'),
    'descricao': request.form.get('descricao'),
    'prioridade': request.form.get('prioridade'),
    'id_turno': request.form.get('id_turno'),
    'id_unidade': request.form.get('id_unidade'),
    'id_local_apontamento': request.form.get('id_local_apontamento'),
    'id_nao_conformidade': request.form.get('id_nao_conformidade'),
    'equipamento_envolvido': request.form.get('equipamento_envolvido'),
    'codigo_equipamento': request.form.get('codigo_equipamento'),
}
            service = ChamadoService()

            # Upload de anexos se houver
            if 'anexos' in request.files:
                for arquivo in request.files.getlist('anexos'):
                    if arquivo.filename:
                        uuid = str(uuid4())
                        arquivo.filename = f"{uuid}_{arquivo.filename}"
                        dados['anexos'] = arquivo.filename
                        upload_file_to_r2(arquivo, arquivo.filename)
                        # save_uploaded_file(arquivo, chamado.id)

            chamado = service.criar_chamado(dados)  # <-- CORRETO

            flash(f'Chamado criado com sucesso! Protocolo: {chamado.protocolo}', 'success')
            return redirect(url_for('chamado.detalhes_chamado', protocolo=chamado.protocolo))
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
    from src.models.chamado import Chamado
    from src.models.historico_chamado import HistoricoChamado
    from src.models.historico_notificacoes import HistoricoNotificacoes

    # Busca o chamado no banco
    chamado = Chamado.query.filter_by(protocolo=protocolo).first_or_404()

    # Calcula as estatísticas relacionadas ao chamado
    estatisticas = {
        "total_eventos": HistoricoChamado.query.filter_by(id_chamado=chamado.id).count(),
        "mudancas_status": HistoricoChamado.query.filter_by(id_chamado=chamado.id, tipo_evento="status").count(),
        "respostas_tecnico": HistoricoChamado.query.filter_by(id_chamado=chamado.id, tipo_evento="resposta_tecnico").count(),
        "notificacoes_enviadas": HistoricoNotificacoes.query.filter_by(id_chamado=chamado.id).count()
    }

    # Pega todo o histórico de interação (ordenado do mais recente ao mais antigo)
    historicos = HistoricoChamado.query \
        .filter_by(id_chamado=chamado.id) \
        .order_by(HistoricoChamado.data_hora.desc()) \
        .all()

    return render_template(
        "detalhes_chamado.html",
        chamado=chamado,
        estatisticas=estatisticas,
        historicos=historicos
    )

@chamado_bp.route("/download/<string:filename>", endpoint="download_anexo")
def download_anexo(filename):
    file_body, content_type = download_file_from_r2(filename)
    return Response(
        stream_with_context(file_body),
        mimetype=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@chamado_bp.route("/api", endpoint="todos_chamados", methods=["GET", ])
def todos_chamados():
    chamados = Chamado.query.all()
    return jsonify([chamado.to_dict() for chamado in chamados])

# 5) ROTA DE CONTATOS
@chamado_bp.route("/contatos", endpoint="gerenciar_contatos")
def gerenciar_contatos():
    return render_template("gerenciar_contatos.html")

# 6) ROTA DE RELATÓRIO: calcula estatísticas e passa para o template
@chamado_bp.route("/relatorio", endpoint="relatorio")
def relatorio():
    # 1) Import dinâmico do modelo Chamado
    from src.models.chamado import Chamado

    params = request.args
    data_inicio = params.get('data_inicio')
    data_fim = params.get('data_fim')
    unidade_id = params.get('unidade')

    # Conta o total de chamados no banco
    query_chamados_total = Chamado.query

    filter_status = []

    if data_inicio:
        query_chamados_total = query_chamados_total.filter(
            Chamado.data_solicitacao >= data_inicio
        )
        filter_status.append(
            Chamado.data_solicitacao >= data_inicio
        )
    if data_fim:
        query_chamados_total = query_chamados_total.filter(
            Chamado.data_solicitacao <= data_fim
        )
        filter_status.append(
            Chamado.data_solicitacao <= data_fim
        )
    if unidade_id:
        query_chamados_total = query_chamados_total.filter(
            Chamado.id_unidade == unidade_id
        )
        filter_status.append(
            Chamado.id_unidade == unidade_id
        )

    total = query_chamados_total.count()
    chamados_pendentes = query_chamados_total.filter(Chamado.status != 'concluido').count()
    chamados_concluidos = query_chamados_total.filter_by(status='concluido').count()
    # media_dias = db.session.query(
    #     func.avg(
    #         (Chamado.data_fechamento) -
    #         (Chamado.data_solicitacao)
    #     )
    # ).filter(
    #     *filter_status,
    #     Chamado.data_fechamento.isnot(None),
    #     Chamado.status == "concluido",
    # ).scalar()

    estatisticas = {
        'total_chamados': total,
        # você pode incluir outras métricas aqui, por ex.:
        'chamados_pendentes': chamados_pendentes,
        'chamados_concluidos': chamados_concluidos
    }

    dados = {
        'unidades': Unidade.query.all()
    }

    filtros = {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'unidade': unidade_id
    }

    status = db.session.query(
        *filter_status,
        func.count(Chamado.id).label('total'),
        Chamado.status
    ).group_by(Chamado.status).all()
    prioridades = db.session.query(
        func.count(Chamado.id).label('total'),
        Chamado.prioridade
    ).group_by(Chamado.prioridade).all()

    turnos = db.session.query(
        *filter_status,
        func.count(Chamado.id).label('total'),
        Chamado.id_turno,
        Turno.nome.label('turno_nome')
    ).join(
        Turno,
        Chamado.id_turno == Turno.id
    ).group_by(
        Chamado.id_turno,
        Turno.nome
    ).all()

    unidades = db.session.query(
        *filter_status,
        func.count(Chamado.id).label('total'),
        Chamado.id_unidade,
        Unidade.nome.label('unidade_nome')
    ).join(
        Unidade,
        Chamado.id_unidade == Unidade.id
    ).group_by(
        Chamado.id_unidade,
        Unidade.nome
    ).all()

    temporal = (
        db.session.query(
            func.extract('year', Chamado.data_solicitacao).label('ano'),
            func.extract('month', Chamado.data_solicitacao).label('mes'),
            Chamado.status,
            func.count(Chamado.id).label('total')
        )
        .group_by(
            func.extract('year', Chamado.data_solicitacao),
            func.extract('month', Chamado.data_solicitacao),
            Chamado.status
        )
        .order_by(
            func.extract('year', Chamado.data_solicitacao),
            func.extract('month', Chamado.data_solicitacao),
            Chamado.status
        )
        .all()
    )
    temporal_ = {

    }
    for t in temporal:
        if f'{[1]}/{[0][:2]}' not in temporal_:

            temporal_[f'{[1]}/{[0][:2]}'] = {
                'abertos': 0,
                'concluidos': 0
            }
        if t[2] == 'aberto':
            temporal_[f'{[1]}/{[0][:2]}']['abertos'] = t[3]
        elif t[2] == 'concluido':
            temporal_[f'{[1]}/{[0][:2]}']['concluidos'] = t[3]


    graficos = {
        'status': {
            s[1]: s[0] for s in status
        } if status else {},
        'prioridade': {
            p[1]: p[0] for p in prioridades
        } if prioridades else {},
        'turnos': {
            t[-1]: t[0] for t in turnos
        } if turnos else {},
        'unidades': {
            u[-1]: u[0] for u in unidades
        } if unidades else {},
        # 'temporal': {
        #     t[1]: t[0] for t in temporal
        # } if temporal else {}
    }
    chamados = Chamado.query.order_by(Chamado.id.desc()).all()
    # Renderiza passando o dicionário estatisticas
    return render_template(
        "relatorio.html",
        estatisticas=estatisticas,
        dados=dados,
        filtros=filtros,
        graficos=graficos,
        chamados=chamados
    )

# 7) PAINEL ADMIN
@chamado_bp.route("/admin", endpoint="painel_admin")
def painel_admin():
    return render_template("painel_admin.html")

# 8) PAINEL SUPERVISOR
# @login_required
@chamado_bp.route("/supervisor", endpoint="painel_supervisor")
def painel_supervisor():
    from src.models.chamado import Chamado
    from src.models.turno import Turno
    from src.models.unidade import Unidade
    if not session.get('supervisor_logged_in') and session.get('user_type') != 'supervisor':
        return redirect(url_for('admin_auth.supervisor_login'))

    # Lista todos os chamados
    chamados = Chamado.query.order_by(Chamado.id.desc()).all()

    # Estatísticas
    estatisticas = {
        'total_chamados': Chamado.query.count(),
        # 'chamados_abertos': Chamado.query.filter_by(status='aberto').count(),
        'chamados_andamento': Chamado.query.filter_by(status='em_andamento').count(),
        'chamados_concluidos': Chamado.query.filter_by(status='concluido').count()
    }

    estatisticas['chamados_abertos'] = estatisticas['total_chamados'] - estatisticas['chamados_andamento'] - estatisticas['chamados_concluidos']

    # Filtros
    turnos = Turno.query.all()
    unidades = Unidade.query.all()

    return render_template(
        "painel_supervisor.html",
        estatisticas=estatisticas,
        chamados=chamados,
        dados={
            'turnos': turnos,
            'unidades': unidades
        }
    )
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

# 11) RESPOSTA DO TECNICO

@chamado_bp.route('/resposta', methods=['POST'])
def responder_chamado():
    from src.models.chamado import Chamado
    data = request.get_json()
    chamado_id = data.get("chamado_id")
    resposta = data.get("resposta_tecnico")
    status = data.get("status")

    chamado = Chamado.query.get_or_404(chamado_id)

    if chamado:
        with db.session.no_autoflush:
            chamado.resposta_tecnico = resposta
            chamado.status = status
            chamado.data_atualizacao = datetime.now()
            db.session.commit()
        return jsonify({"success": True, "mensagem": "Resposta salva com sucesso!"})

    return jsonify({"success": False, "mensagem": "Chamado não encontrado."}), 404

# 12) ATUALIZA STATUS

@chamado_bp.route('/<int:id>/status', methods=['PUT'])
def alterar_status(id):
    from src.models.chamado import Chamado
    data = request.get_json()
    novo_status = data.get('status')

    chamado = Chamado.query.get_or_404(id)
    chamado.status = novo_status
    chamado.data_atualizacao = datetime.now()

    db.session.commit()
    return jsonify({"success": True, "mensagem": "Status atualizado com sucesso!"})


# 13) REGISTRAR AÇÃO

@chamado_bp.route('/<int:id>/acao', methods=['POST'])
def registrar_acao(id):
    from src.models.historico_chamado import HistoricoChamado
    from src import db
    from flask import request, jsonify

    dados = request.get_json()

    nova_acao = HistoricoChamado(
        id_chamado=id,
        tipo_evento='acao',
        descricao=dados.get('descricao'),
        data_hora=datetime.now()
        # Inclua mais campos se necessário
    )

    db.session.add(nova_acao)
    db.session.commit()

    return jsonify({"success": True})


