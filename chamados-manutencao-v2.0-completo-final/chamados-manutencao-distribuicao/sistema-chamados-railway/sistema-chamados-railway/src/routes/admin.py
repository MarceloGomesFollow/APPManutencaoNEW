# src/routes/admin.py
from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from src.models.user import db 
from src.models.turno import Turno
from src.models.unidade import Unidade
from src.models.nao_conformidade import NaoConformidade
from src.models.local_apontamento import LocalApontamento
from src.models.status_chamado import StatusChamado
from src.models.perfil import Perfil
from src.models.contato_notificacao import ContatoNotificacaoManutencao

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ==================== TURNOS ====================

@admin_bp.route('/turnos')
def listar_turnos():
    """Lista todos os turnos"""
    try:
        turnos = Turno.query.filter_by(ativo=True).all()
        turnos_dict = [turno.to_dict() for turno in turnos]
        return render_template('admin/turnos.html', turnos=turnos_dict)
    except Exception as e:
        flash(f'Erro ao carregar turnos: {str(e)}', 'error')
        return render_template('admin/turnos.html', turnos=[])

@admin_bp.route('/turnos/api')
def api_turnos():
    """API para listar turnos"""
    try:
        turnos = Turno.query.filter_by(ativo=True).all()
        return jsonify([turno.to_dict() for turno in turnos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/turnos', methods=['POST'])
def criar_turno():
    """Cria um novo turno"""
    try:
        nome = request.form.get('nome')
        if not nome:
            flash('Nome é obrigatório', 'error')
            return redirect(url_for('admin.listar_turnos'))
        
        turno = Turno(nome=nome)
        db.session.add(turno)
        db.session.commit()
        
        flash('Turno criado com sucesso!', 'success')
        return redirect(url_for('admin.listar_turnos'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar turno: {str(e)}', 'error')
        return redirect(url_for('admin.listar_turnos'))

@admin_bp.route('/turnos/<int:id>', methods=['PUT'])
def atualizar_turno(id):
    """Atualiza um turno"""
    try:
        turno = Turno.query.get_or_404(id)
        data = request.get_json()
        
        turno.nome = data.get('nome', turno.nome)
        turno.ativo = data.get('ativo', turno.ativo)
        
        db.session.commit()
        return jsonify(turno.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/turnos/<int:id>', methods=['DELETE'])
def deletar_turno(id):
    """Desativa um turno"""
    try:
        turno = Turno.query.get_or_404(id)
        turno.ativo = False
        db.session.commit()
        return jsonify({'message': 'Turno desativado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== UNIDADES ====================

@admin_bp.route('/unidades')
def listar_unidades():
    """Lista todas as unidades"""
    try:
        unidades = Unidade.query.filter_by(ativo=True).all()
        unidades_dict = [unidade.to_dict() for unidade in unidades]
        return render_template('admin/unidades.html', unidades=unidades_dict)
    except Exception as e:
        flash(f'Erro ao carregar unidades: {str(e)}', 'error')
        return render_template('admin/unidades.html', unidades=[])

@admin_bp.route('/unidades/api')
def api_unidades():
    """API para listar unidades"""
    try:
        unidades = Unidade.query.filter_by(ativo=True).all()
        return jsonify([unidade.to_dict() for unidade in unidades])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/unidades', methods=['POST'])
def criar_unidade():
    """Cria uma nova unidade"""
    try:
        nome = request.form.get('nome')
        if not nome:
            flash('Nome é obrigatório', 'error')
            return redirect(url_for('admin.listar_unidades'))
        
        unidade = Unidade(nome=nome)
        db.session.add(unidade)
        db.session.commit()
        
        flash('Unidade criada com sucesso!', 'success')
        return redirect(url_for('admin.listar_unidades'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar unidade: {str(e)}', 'error')
        return redirect(url_for('admin.listar_unidades'))

# ==================== NÃO CONFORMIDADES ====================

@admin_bp.route('/nao-conformidades')
def listar_nao_conformidades():
    """Lista todas as não conformidades"""
    try:
        ncs = NaoConformidade.query.filter_by(ativo=True).all()
        ncs_dict = [nc.to_dict() for nc in ncs]
        return render_template('admin/nao_conformidades.html', nao_conformidades=ncs_dict)
    except Exception as e:
        flash(f'Erro ao carregar não conformidades: {str(e)}', 'error')
        return render_template('admin/nao_conformidades.html', nao_conformidades=[])

@admin_bp.route('/nao-conformidades/api')
def api_nao_conformidades():
    """API para listar não conformidades"""
    try:
        ncs = NaoConformidade.query.filter_by(ativo=True).all()
        return jsonify([nc.to_dict() for nc in ncs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/nao-conformidades', methods=['POST'])
def criar_nao_conformidade():
    """Cria uma nova não conformidade"""
    try:
        nome = request.form.get('nome')
        if not nome:
            flash('Nome é obrigatório', 'error')
            return redirect(url_for('admin.listar_nao_conformidades'))
        
        nc = NaoConformidade(nome=nome)
        db.session.add(nc)
        db.session.commit()
        
        flash('Não conformidade criada com sucesso!', 'success')
        return redirect(url_for('admin.listar_nao_conformidades'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar não conformidade: {str(e)}', 'error')
        return redirect(url_for('admin.listar_nao_conformidades'))

# ==================== LOCAIS DE APONTAMENTO ====================

@admin_bp.route('/locais-apontamento')
def listar_locais_apontamento():
    """Lista todos os locais de apontamento"""
    try:
        locais = LocalApontamento.query.filter_by(ativo=True).all()
        locais_dict = [local.to_dict() for local in locais]
        return render_template('admin/locais_apontamento.html', locais=locais_dict)
    except Exception as e:
        flash(f'Erro ao carregar locais: {str(e)}', 'error')
        return render_template('admin/locais_apontamento.html', locais=[])

@admin_bp.route('/locais-apontamento/api')
def api_locais_apontamento():
    """API para listar locais de apontamento"""
    try:
        locais = LocalApontamento.query.filter_by(ativo=True).all()
        return jsonify([local.to_dict() for local in locais])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/locais-apontamento', methods=['POST'])
def criar_local_apontamento():
    """Cria um novo local de apontamento"""
    try:
        nome = request.form.get('nome')
        if not nome:
            flash('Nome é obrigatório', 'error')
            return redirect(url_for('admin.listar_locais_apontamento'))
        
        local = LocalApontamento(nome=nome)
        db.session.add(local)
        db.session.commit()
        
        flash('Local de apontamento criado com sucesso!', 'success')
        return redirect(url_for('admin.listar_locais_apontamento'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar local: {str(e)}', 'error')
        return redirect(url_for('admin.listar_locais_apontamento'))

# ==================== STATUS CHAMADO ====================

@admin_bp.route('/status-chamado')
def listar_status_chamado():
    """Lista todos os status de chamado"""
    try:
        status_list = StatusChamado.query.filter_by(ativo=True).order_by(StatusChamado.ordem).all()
        status_dict = [status.to_dict() for status in status_list]
        return render_template('admin/status_chamado.html', status_list=status_dict)
    except Exception as e:
        flash(f'Erro ao carregar status: {str(e)}', 'error')
        return render_template('admin/status_chamado.html', status_list=[])

@admin_bp.route('/status-chamado/api')
def api_status_chamado():
    """API para listar status de chamado"""
    try:
        status_list = StatusChamado.query.filter_by(ativo=True).order_by(StatusChamado.ordem).all()
        return jsonify([status.to_dict() for status in status_list])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== CONTATOS NOTIFICAÇÃO ====================

@admin_bp.route('/contatos-notificacao')
def listar_contatos_notificacao():
    """Lista todos os contatos de notificação"""
    try:
        contatos = ContatoNotificacaoManutencao.query.filter_by(ativo=True).all()
        contatos_dict = [contato.to_dict() for contato in contatos]
        return render_template('admin/contatos_notificacao.html', contatos=contatos_dict)
    except Exception as e:
        flash(f'Erro ao carregar contatos: {str(e)}', 'error')
        return render_template('admin/contatos_notificacao.html', contatos=[])

@admin_bp.route('/contatos-notificacao/api')
def api_contatos_notificacao():
    """API para listar contatos de notificação"""
    try:
        contatos = ContatoNotificacaoManutencao.query.filter_by(ativo=True).all()
        return jsonify([contato.to_dict() for contato in contatos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/contatos-notificacao', methods=['POST'])
def criar_contato_notificacao():
    """Cria um novo contato de notificação"""
    try:
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        
        if not nome or not email:
            flash('Nome e email são obrigatórios', 'error')
            return redirect(url_for('admin.listar_contatos_notificacao'))
        
        contato = ContatoNotificacaoManutencao(nome=nome, email=email, telefone=telefone)
        db.session.add(contato)
        db.session.commit()
        
        flash('Contato criado com sucesso!', 'success')
        return redirect(url_for('admin.listar_contatos_notificacao'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar contato: {str(e)}', 'error')
        return redirect(url_for('admin.listar_contatos_notificacao'))

# ==================== PAINEL PRINCIPAL ====================

@admin_bp.route('/')
def painel_admin():
    """Painel principal de administração"""
    try:
        # Estatísticas básicas
        total_turnos = Turno.query.filter_by(ativo=True).count()
        total_unidades = Unidade.query.filter_by(ativo=True).count()
        total_ncs = NaoConformidade.query.filter_by(ativo=True).count()
        total_locais = LocalApontamento.query.filter_by(ativo=True).count()
        total_status = StatusChamado.query.filter_by(ativo=True).count()
        total_contatos = ContatoNotificacaoManutencao.query.filter_by(ativo=True).count()
        
        estatisticas = {
            'total_turnos': total_turnos,
            'total_unidades': total_unidades,
            'total_ncs': total_ncs,
            'total_locais': total_locais,
            'total_status': total_status,
            'total_contatos': total_contatos
        }
        
        return render_template('admin/painel_admin.html', estatisticas=estatisticas)
    except Exception as e:
        flash(f'Erro ao carregar painel: {str(e)}', 'error')
        return render_template('admin/painel_admin.html', estatisticas={})