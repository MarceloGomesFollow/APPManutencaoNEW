# src/routes/admin.py

from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from src.models import db  # <— aqui importamos o db correto
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
        return render_template('admin/turnos.html', turnos=turnos)
    except Exception as e:
        flash(f'Erro ao carregar turnos: {e}', 'error')
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
    """Cria um novo turno via JSON"""
    try:
        data = request.get_json()
        nome = data.get('nome')
        descricao = data.get('descricao', '')
        ativo = data.get('ativo', True)
        if not nome:
            return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400
            
        turno = Turno(nome=nome, descricao=descricao, ativo=ativo)
        db.session.add(turno)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Turno criado com sucesso!', 'turno': turno.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/turnos/<int:id>', methods=['PUT'])
def atualizar_turno(id):
    """Atualiza um turno"""
    try:
        turno = Turno.query.get_or_404(id)
        data = request.get_json()
        turno.nome = data.get('nome', turno.nome)
        turno.ativo = data.get('ativo', turno.ativo)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Turno atualizado com sucesso!', 'turno': turno.to_dict()}), 200

        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/turnos/<int:id>', methods=['GET'])
def obter_turno(id):
    """Retorna os dados de um turno específico"""
    try:
        turno = Turno.query.get_or_404(id)
        return jsonify(turno.to_dict())
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/turnos/<int:id>', methods=['DELETE'])
def deletar_turno(id):
    """Desativa um turno"""
    try:
        turno = Turno.query.get_or_404(id)
        turno.ativo = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Turno desativado com sucesso!'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== UNIDADES ====================

@admin_bp.route('/unidades')
def listar_unidades():
    """Lista todas as unidades"""
    try:
        unidades = Unidade.query.filter_by(ativo=True).all()
        return render_template('admin/unidades.html', unidades=[u.to_dict() for u in unidades])
    except Exception as e:
        flash(f'Erro ao carregar unidades: {e}', 'error')
        return render_template('admin/unidades.html', unidades=[])

@admin_bp.route('/unidades/api')
def api_unidades():
    """API para listar unidades"""
    try:
        unidades = Unidade.query.filter_by(ativo=True).all()
        return jsonify([u.to_dict() for u in unidades])
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
        flash(f'Erro ao criar unidade: {e}', 'error')
        return redirect(url_for('admin.listar_unidades'))

# ==================== NÃO CONFORMIDADES ====================

@admin_bp.route('/nao-conformidades')
def listar_nao_conformidades():
    """Lista todas as não conformidades"""
    try:
        ncs = NaoConformidade.query.filter_by(ativo=True).all()
        return render_template('admin/nao_conformidades.html', nao_conformidades=[nc.to_dict() for nc in ncs])
    except Exception as e:
        flash(f'Erro ao carregar não conformidades: {e}', 'error')
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
        flash(f'Erro ao criar não conformidade: {e}', 'error')
        return redirect(url_for('admin.listar_nao_conformidades'))

# ==================== LOCAIS DE APONTAMENTO ====================

@admin_bp.route('/locais-apontamento')
def listar_locais_apontamento():
    """Lista todos os locais de apontamento"""
    try:
        locais = LocalApontamento.query.filter_by(ativo=True).all()
        return render_template('admin/locais_apontamento.html', locais=[l.to_dict() for l in locais])
    except Exception as e:
        flash(f'Erro ao carregar locais: {e}', 'error')
        return render_template('admin/locais_apontamento.html', locais=[])

@admin_bp.route('/locais-apontamento/api')
def api_locais_apontamento():
    """API para listar locais de apontamento"""
    try:
        locais = LocalApontamento.query.filter_by(ativo=True).all()
        return jsonify([l.to_dict() for l in locais])
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
        flash(f'Erro ao criar local: {e}', 'error')
        return redirect(url_for('admin.listar_locais_apontamento'))

# ==================== STATUS CHAMADO ====================

@admin_bp.route('/status-chamado')
def listar_status_chamado():
    """Lista todos os status de chamado"""
    try:
        status_list = StatusChamado.query.filter_by(ativo=True).order_by(StatusChamado.ordem).all()
        return render_template('admin/status_chamado.html', status_list=[s.to_dict() for s in status_list])
    except Exception as e:
        flash(f'Erro ao carregar status: {e}', 'error')
        return render_template('admin/status_chamado.html', status_list=[])

@admin_bp.route('/status-chamado/api')
def api_status_chamado():
    """API para listar status de chamado"""
    try:
        status_list = StatusChamado.query.filter_by(ativo=True).order_by(StatusChamado.ordem).all()
        return jsonify([s.to_dict() for s in status_list])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== PERFIS ====================

@admin_bp.route('/perfis/api')
def api_perfis():
    """API para listar perfis"""
    try:
        perfil_list = Perfil.query.filter_by(ativo=True).order_by(Perfil.nome).all()
        return jsonify([s.to_dict() for s in perfil_list])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== CONTATOS NOTIFICAÇÃO ====================

@admin_bp.route('/contatos-notificacao')
def listar_contatos_notificacao():
    """Lista todos os contatos de notificação"""
    try:
        contatos = ContatoNotificacaoManutencao.query.filter_by(ativo=True).all()
        return render_template('admin/contatos_notificacao.html', contatos=[c.to_dict() for c in contatos])
    except Exception as e:
        flash(f'Erro ao carregar contatos: {e}', 'error')
        return render_template('admin/contatos_notificacao.html', contatos=[])

@admin_bp.route('/contatos-notificacao/api')
def api_contatos_notificacao():
    """API para listar contatos de notificação"""
    try:
        contatos = ContatoNotificacaoManutencao.query.filter_by(ativo=True).all()
        return jsonify([c.to_dict() for c in contatos])
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
        flash(f'Erro ao criar contato: {e}', 'error')
        return redirect(url_for('admin.listar_contatos_notificacao'))

# ==================== PAINEL PRINCIPAL ====================

@admin_bp.route('/')
def painel_admin():
    """Painel principal de administração"""
    try:
        estatisticas = {
            'total_turnos': Turno.query.filter_by(ativo=True).count(),
            'total_unidades': Unidade.query.filter_by(ativo=True).count(),
            'total_ncs': NaoConformidade.query.filter_by(ativo=True).count(),
            'total_locais': LocalApontamento.query.filter_by(ativo=True).count(),
            'total_status': StatusChamado.query.filter_by(ativo=True).count(),
            'total_contatos': ContatoNotificacaoManutencao.query.filter_by(ativo=True).count(),
        }
        return render_template('admin/painel_admin.html', estatisticas=estatisticas)
    except Exception as e:
        flash(f'Erro ao carregar painel: {e}', 'error')
        return render_template('admin/painel_admin.html', estatisticas={})
