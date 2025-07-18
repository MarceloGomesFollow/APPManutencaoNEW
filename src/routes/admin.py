# src/routes/admin.py

from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session
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
        data = request.get_json()
        nome = data.get('nome')
        if not nome:
            flash('Nome é obrigatório', 'error')
            return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400

        unidade = Unidade(nome=nome)
        db.session.add(unidade)
        db.session.commit()
        flash('Unidade criada com sucesso!', 'success')
        return jsonify({'success': True, 'message': 'Unidade criado com sucesso!', 'unidade': unidade.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar unidade: {e}', 'error')
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/unidades/<int:id>', methods=['PUT'])
def atualizar_unidade(id):
    """Atualiza um turno"""
    try:
        unidade = Unidade.query.get_or_404(id)
        data = request.get_json()
        unidade.nome = data.get('nome', unidade.nome)
        unidade.ativo = data.get('ativo', unidade.ativo)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Unidade atualizado com sucesso!', 'unidade': unidade.to_dict()}), 200


    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/unidades/<int:id>', methods=['GET'])
def obter_unidade(id):
    """Retorna os dados de um Unidad específico"""
    try:
        turno = Unidade.query.get_or_404(id)
        return jsonify(turno.to_dict())
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/unidades/<int:id>', methods=['DELETE'])
def deletar_unidade(id):
    """Desativa um unidade"""
    try:
        unidade = Unidade.query.get_or_404(id)
        unidade.ativo = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Unidade desativado com sucesso!'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

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
        data = request.get_json()
        nome = data.get('nome')
        if not nome:
            flash('Nome é obrigatório', 'error')
            return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400

        nao_conformidade = NaoConformidade(nome=nome)
        db.session.add(nao_conformidade)
        db.session.commit()
        flash('Não conformidade criada com sucesso!', 'success')
        return jsonify({'success': True, 'message': 'Não conformidade criado com sucesso!', 'naoConformidades': nao_conformidade.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar não conformidade: {e}', 'error')
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/nao-conformidades/<int:id>', methods=['PUT'])
def atualizar_nao_conformidades(id):
    """Atualiza um turno"""
    try:
        nao_conformidade = NaoConformidade.query.get_or_404(id)
        data = request.get_json()
        nao_conformidade.nome = data.get('nome', nao_conformidade.nome)
        nao_conformidade.ativo = data.get('ativo', nao_conformidade.ativo)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Local de apontamento atualizado com sucesso!', 'naoConformidades': nao_conformidade.to_dict()}), 200


    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/nao-conformidades/<int:id>', methods=['GET'])
def obter_nao_conformidades(id):
    """Retorna os dados de um Local de Apontamento específico"""
    try:
        nao_conformidade = NaoConformidade.query.get_or_404(id)
        return jsonify(nao_conformidade.to_dict())
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/nao-conformidades/<int:id>', methods=['DELETE'])
def deletar_nao_conformidades(id):
    """Desativa um unidade"""
    try:
        nao_conformidade = NaoConformidade.query.get_or_404(id)
        nao_conformidade.ativo = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Nao conformidade desativado com sucesso!'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

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
        data = request.get_json()
        nome = data.get('nome')
        if not nome:
            flash('Nome é obrigatório', 'error')
            return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400

        local = LocalApontamento(nome=nome)
        db.session.add(local)
        db.session.commit()
        flash('Local de apontamento criado com sucesso!', 'success')
        return jsonify({'success': True, 'message': 'Unidade criado com sucesso!', 'unidade': local.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar local: {e}', 'error')
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/locais-apontamento/<int:id>', methods=['PUT'])
def atualizar_local_apontamento(id):
    """Atualiza um turno"""
    try:
        local = LocalApontamento.query.get_or_404(id)
        data = request.get_json()
        local.nome = data.get('nome', local.nome)
        local.ativo = data.get('ativo', local.ativo)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Local de apontamento atualizado com sucesso!', 'local': local.to_dict()}), 200


    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/locais-apontamento/<int:id>', methods=['GET'])
def obter_local_apontamento(id):
    """Retorna os dados de um Local de Apontamento específico"""
    try:
        local = LocalApontamento.query.get_or_404(id)
        return jsonify(local.to_dict())
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/locais-apontamento/<int:id>', methods=['DELETE'])
def deletar_local_apontamento(id):
    """Desativa um unidade"""
    try:
        local = LocalApontamento.query.get_or_404(id)
        local.ativo = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Local desativado com sucesso!'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

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

@admin_bp.route('/status-chamado', methods=['POST'])
def criar_status_chamado():
    """Cria um novo status de chamado"""
    try:
        data = request.get_json()
        nome = data.get('nome')
        if not nome:
            flash('Nome é obrigatório', 'error')
            return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400

        status_chamado = StatusChamado(nome=nome)
        db.session.add(status_chamado)
        db.session.commit()
        flash('Status de chamado criado com sucesso!', 'success')
        return jsonify({'success': True, 'message': 'Unidade criado com sucesso!', 'status': status_chamado.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar status de chamado: {e}', 'error')
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/status-chamado/<int:id>', methods=['PUT'])
def atualizar_status_chamado(id):
    """Atualiza um Status de Chamado"""
    try:
        status_chamado = StatusChamado.query.get_or_404(id)
        data = request.get_json()
        status_chamado.nome = data.get('nome', status_chamado.nome)
        status_chamado.ativo = data.get('ativo', status_chamado.ativo)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Status de chamado atualizado com sucesso!', 'local': status_chamado.to_dict()}), 200


    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/status-chamado/<int:id>', methods=['GET'])
def obter_status_chamado(id):
    """Retorna os dados de um Status de Chamado específico"""
    try:
        status_chamado = StatusChamado.query.get_or_404(id)
        return jsonify(status_chamado.to_dict())
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/status-chamado/<int:id>', methods=['DELETE'])
def deletar_status_chamado(id):
    """Desativa um Status de Chamado"""
    try:
        status_chamado = StatusChamado.query.get_or_404(id)
        status_chamado.ativo = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Status de chamado desativado com sucesso!'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== PERFIS ====================

@admin_bp.route('/perfis/api')
def api_perfis():
    """API para listar perfis"""
    try:
        perfil_list = Perfil.query.filter_by(ativo=True).order_by(Perfil.nome).all()
        return jsonify([s.to_dict() for s in perfil_list])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/perfis', methods=['POST'])
def criar_perfis():
    """Cria um novo Perfil Usuario"""
    try:
        data = request.get_json()
        nome = data.get('nome')
        descricao = data.get('descricao')
        if not nome:
            flash('Nome é obrigatório', 'error')
            return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400

        perfil = Perfil(nome=nome, descricao=descricao)
        db.session.add(perfil)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Unidade criado com sucesso!', 'perfil': perfil.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar status de chamado: {e}', 'error')
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/perfis/<int:id>', methods=['PUT'])
def atualizar_perfis(id):
    """Atualiza um Perfil Usuario"""
    try:
        perfil = Perfil.query.get_or_404(id)
        data = request.get_json()
        perfil.nome = data.get('nome', perfil.nome)
        perfil.ativo = data.get('ativo', perfil.ativo)
        perfil.descricao = data.get('descricao', perfil.descricao)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Perfil de Usuario atualizado com sucesso!', 'local': perfil.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/perfis/<int:id>', methods=['GET'])
def obter_perfis(id):
    """Retorna os dados de um Perfil Usuario específico"""
    try:
        perfil = Perfil.query.get_or_404(id)
        return jsonify(perfil.to_dict())
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/perfis/<int:id>', methods=['DELETE'])
def deletar_perfis(id):
    """Desativa um Perfil Usuario"""
    try:
        perfil = Perfil.query.get_or_404(id)
        perfil.ativo = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Perfil Usuario desativado com sucesso!'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

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
    if not session.get('admin_logged_in') and session.get('user_type') != 'admin':
        return redirect(url_for('admin_auth.admin_login'))
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
