from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from src.models import db
from src.models.historico_notificacoes import HistoricoNotificacoes
from src.models.contato_notificacao import ContatoNotificacaoManutencao
from src.models.unidade import Unidade
from src.services.notification_service import notification_service
from datetime import datetime, timedelta
import json

notificacao_bp = Blueprint('notificacao', __name__)

@notificacao_bp.route('/notificacoes/historico')
def historico_notificacoes():
    """Página com histórico de notificações enviadas"""
    try:
        # Filtros
        chamado_id = request.args.get('chamado_id', type=int)
        tipo = request.args.get('tipo', '')
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        sucesso = request.args.get('sucesso', '')
        
        # Query base
        query = HistoricoNotificacoes.query
        
        # Aplica filtros
        if chamado_id:
            query = query.filter(HistoricoNotificacoes.chamado_id == chamado_id)
        
        if tipo:
            query = query.filter(HistoricoNotificacoes.tipo_notificacao == tipo)
        
        if data_inicio:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(HistoricoNotificacoes.data_envio >= data_inicio_dt)
        
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            query = query.filter(HistoricoNotificacoes.data_envio <= data_fim_dt)
        
        if sucesso:
            query = query.filter(HistoricoNotificacoes.sucesso == (sucesso == 'true'))
        
        # Ordena por data mais recente
        notificacoes = query.order_by(HistoricoNotificacoes.data_envio.desc()).limit(100).all()
        
        # Converte para dicionários
        notificacoes_dict = []
        for notif in notificacoes:
            notificacoes_dict.append({
                'id': notif.id,
                'chamado_id': notif.chamado_id,
                'protocolo': notif.chamado.protocolo if notif.chamado else 'N/A',
                'tipo_notificacao': notif.tipo_notificacao,
                'destinatarios': notif.destinatarios,
                'assunto': notif.assunto,
                'data_envio': notif.data_envio.strftime('%d/%m/%Y %H:%M'),
                'sucesso': notif.sucesso,
                'erro': notif.erro
            })
        
        # Estatísticas
        total_notificacoes = HistoricoNotificacoes.query.count()
        notificacoes_sucesso = HistoricoNotificacoes.query.filter_by(sucesso=True).count()
        notificacoes_erro = HistoricoNotificacoes.query.filter_by(sucesso=False).count()
        
        # Últimas 24 horas
        ontem = datetime.now() - timedelta(days=1)
        notificacoes_24h = HistoricoNotificacoes.query.filter(
            HistoricoNotificacoes.data_envio >= ontem
        ).count()
        
        estatisticas = {
            'total': total_notificacoes,
            'sucesso': notificacoes_sucesso,
            'erro': notificacoes_erro,
            'ultimas_24h': notificacoes_24h,
            'taxa_sucesso': round((notificacoes_sucesso / total_notificacoes * 100) if total_notificacoes > 0 else 0, 1)
        }
        
        return render_template('historico_notificacoes.html', 
                             notificacoes=notificacoes_dict,
                             estatisticas=estatisticas,
                             filtros={
                                 'chamado_id': chamado_id,
                                 'tipo': tipo,
                                 'data_inicio': data_inicio,
                                 'data_fim': data_fim,
                                 'sucesso': sucesso
                             })
        
    except Exception as e:
        flash(f'Erro ao carregar histórico: {str(e)}', 'error')
        return render_template('historico_notificacoes.html', 
                             notificacoes=[],
                             estatisticas={},
                             filtros={})

@notificacao_bp.route('/notificacoes/contatos')
def gerenciar_contatos():
    """Página para gerenciar contatos de notificação"""
    try:
        contatos = ContatoNotificacaoManutencao.query.all()
        unidades = Unidade.query.filter_by(ativo=True).all()
        
        # Converte para dicionários
        contatos_dict = []
        for contato in contatos:
            contatos_dict.append({
                'id': contato.id,
                'nome': contato.nome,
                'email': contato.email,
                'telefone': contato.telefone,
                'unidade_nome': contato.unidade.nome if contato.unidade else 'Todas',
                'unidade_id': contato.unidade_id,
                'ativo': contato.ativo,
                'data_criacao': contato.data_criacao.strftime('%d/%m/%Y')
            })
        
        unidades_dict = [{'id': u.id, 'nome': u.nome} for u in unidades]
        
        return render_template('gerenciar_contatos.html', 
                             contatos=contatos_dict,
                             unidades=unidades_dict)
        
    except Exception as e:
        flash(f'Erro ao carregar contatos: {str(e)}', 'error')
        return render_template('gerenciar_contatos.html', contatos=[], unidades=[])

@notificacao_bp.route('/notificacoes/contatos/adicionar', methods=['POST'])
def adicionar_contato():
    """Adiciona novo contato de notificação"""
    try:
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()
        unidade_id = request.form.get('unidade_id', type=int)
        
        if not nome or not email:
            flash('Nome e e-mail são obrigatórios', 'error')
            return redirect(url_for('notificacao.gerenciar_contatos'))
        
        # Verifica se e-mail já existe
        contato_existente = ContatoNotificacaoManutencao.query.filter_by(email=email).first()
        if contato_existente:
            flash('E-mail já cadastrado', 'error')
            return redirect(url_for('notificacao.gerenciar_contatos'))
        
        # Cria novo contato
        contato = ContatoNotificacaoManutencao(
            nome=nome,
            email=email,
            telefone=telefone,
            unidade_id=unidade_id if unidade_id else None,
            ativo=True,
            data_criacao=datetime.now()
        )
        
        db.session.add(contato)
        db.session.commit()
        
        flash('Contato adicionado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao adicionar contato: {str(e)}', 'error')
    
    return redirect(url_for('notificacao.gerenciar_contatos'))

@notificacao_bp.route('/notificacoes/contatos/<int:contato_id>/editar', methods=['POST'])
def editar_contato(contato_id):
    """Edita contato de notificação"""
    try:
        contato = ContatoNotificacaoManutencao.query.get_or_404(contato_id)
        
        contato.nome = request.form.get('nome', '').strip()
        contato.email = request.form.get('email', '').strip()
        contato.telefone = request.form.get('telefone', '').strip()
        contato.unidade_id = request.form.get('unidade_id', type=int) or None
        contato.ativo = request.form.get('ativo') == 'on'
        
        if not contato.nome or not contato.email:
            flash('Nome e e-mail são obrigatórios', 'error')
            return redirect(url_for('notificacao.gerenciar_contatos'))
        
        db.session.commit()
        flash('Contato atualizado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar contato: {str(e)}', 'error')
    
    return redirect(url_for('notificacao.gerenciar_contatos'))

@notificacao_bp.route('/notificacoes/contatos/<int:contato_id>/excluir', methods=['POST'])
def excluir_contato(contato_id):
    """Exclui contato de notificação"""
    try:
        contato = ContatoNotificacaoManutencao.query.get_or_404(contato_id)
        
        db.session.delete(contato)
        db.session.commit()
        
        flash('Contato excluído com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir contato: {str(e)}', 'error')
    
    return redirect(url_for('notificacao.gerenciar_contatos'))

@notificacao_bp.route('/notificacoes/teste', methods=['POST'])
def enviar_teste():
    """Envia e-mail de teste"""
    try:
        email_destino = request.form.get('email', '').strip()
        
        if not email_destino:
            return jsonify({'success': False, 'message': 'E-mail é obrigatório'})
        
        # Dados de teste
        dados_teste = {
            'protocolo': '9999',
            'titulo': 'Teste do Sistema de Notificações',
            'cliente_nome': 'Usuário Teste',
            'cliente_email': email_destino,
            'cliente_telefone': '(11) 99999-9999',
            'prioridade': 'media',
            'status': 'aberto',
            'unidade_nome': 'Unidade Teste',
            'turno_nome': 'Teste',
            'local_nome': 'Local Teste',
            'descricao': 'Este é um e-mail de teste do sistema de notificações. Se você recebeu esta mensagem, o sistema está funcionando corretamente.',
            'link_chamado': f"{request.url_root}#teste"
        }
        
        from src.services.email_templates import email_templates
        from src.services.email_service import email_service
        
        # Gera e-mail de teste
        email_data = email_templates.chamado_aberto(dados_teste)
        
        # Envia e-mail
        sucesso = email_service.enviar_email(
            destinatarios=[email_destino],
            assunto=f"[TESTE] {email_data['assunto']}",
            corpo_html=email_data['html'],
            corpo_texto=email_data['texto']
        )
        
        if sucesso:
            return jsonify({'success': True, 'message': 'E-mail de teste enviado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao enviar e-mail de teste'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@notificacao_bp.route('/notificacoes/lembretes/enviar', methods=['POST'])
def enviar_lembretes():
    """Envia lembretes para chamados pendentes"""
    try:
        lembretes_enviados = notification_service.enviar_lembretes_pendentes()
        
        if lembretes_enviados > 0:
            flash(f'{lembretes_enviados} lembrete(s) enviado(s) com sucesso!', 'success')
        else:
            flash('Nenhum lembrete foi enviado (não há chamados pendentes ou já foram enviados recentemente)', 'info')
        
    except Exception as e:
        flash(f'Erro ao enviar lembretes: {str(e)}', 'error')
    
    return redirect(url_for('notificacao.historico_notificacoes'))

@notificacao_bp.route('/api/notificacoes/estatisticas')
def api_estatisticas_notificacoes():
    """API para estatísticas de notificações"""
    try:
        # Últimos 30 dias
        inicio = datetime.now() - timedelta(days=30)
        
        # Notificações por dia
        notificacoes_por_dia = db.session.query(
            db.func.date(HistoricoNotificacoes.data_envio).label('data'),
            db.func.count(HistoricoNotificacoes.id).label('total'),
            db.func.sum(db.case([(HistoricoNotificacoes.sucesso == True, 1)], else_=0)).label('sucesso'),
            db.func.sum(db.case([(HistoricoNotificacoes.sucesso == False, 1)], else_=0)).label('erro')
        ).filter(
            HistoricoNotificacoes.data_envio >= inicio
        ).group_by(
            db.func.date(HistoricoNotificacoes.data_envio)
        ).order_by('data').all()
        
        # Notificações por tipo
        notificacoes_por_tipo = db.session.query(
            HistoricoNotificacoes.tipo_notificacao,
            db.func.count(HistoricoNotificacoes.id).label('total')
        ).filter(
            HistoricoNotificacoes.data_envio >= inicio
        ).group_by(
            HistoricoNotificacoes.tipo_notificacao
        ).all()
        
        return jsonify({
            'por_dia': [
                {
                    'data': item.data.strftime('%Y-%m-%d'),
                    'total': int(item.total),
                    'sucesso': int(item.sucesso or 0),
                    'erro': int(item.erro or 0)
                }
                for item in notificacoes_por_dia
            ],
            'por_tipo': [
                {
                    'tipo': item.tipo_notificacao,
                    'total': int(item.total)
                }
                for item in notificacoes_por_tipo
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

