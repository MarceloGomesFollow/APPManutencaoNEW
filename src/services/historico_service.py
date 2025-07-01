from src.models.user import db
from src.models.historico_chamado import HistoricoChamado
from datetime import datetime
import json

class HistoricoService:
    """Serviço para gerenciar o histórico e timeline dos chamados"""
    
    @staticmethod
    def adicionar_evento(id_chamado, tipo_evento, descricao, id_usuario=None, detalhes_adicionais=None):
        """
        Adiciona um evento ao histórico do chamado
        
        Args:
            id_chamado: ID do chamado
            tipo_evento: Tipo do evento ('status_change', 'response', 'notification_sent', 'comment', 'created', 'updated')
            descricao: Descrição do evento
            id_usuario: ID do usuário que executou a ação (opcional)
            detalhes_adicionais: Dados extras em formato dict (opcional)
        """
        try:
            historico = HistoricoChamado(
                id_chamado=id_chamado,
                id_usuario=id_usuario,
                tipo_evento=tipo_evento,
                descricao=descricao,
                detalhes_adicionais=json.dumps(detalhes_adicionais) if detalhes_adicionais else None
            )
            
            db.session.add(historico)
            db.session.commit()
            
            return historico
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def obter_timeline(id_chamado):
        """
        Obtém a timeline completa de um chamado
        
        Args:
            id_chamado: ID do chamado
            
        Returns:
            Lista de eventos ordenados por data
        """
        try:
            eventos = HistoricoChamado.query.filter_by(id_chamado=id_chamado)\
                                           .order_by(HistoricoChamado.data_hora.desc())\
                                           .all()
            
            timeline = []
            for evento in eventos:
                evento_dict = evento.to_dict()
                
                # Parse detalhes adicionais se existir
                if evento.detalhes_adicionais:
                    try:
                        evento_dict['detalhes_adicionais'] = json.loads(evento.detalhes_adicionais)
                    except:
                        evento_dict['detalhes_adicionais'] = evento.detalhes_adicionais
                
                timeline.append(evento_dict)
            
            return timeline
        except Exception as e:
            raise e
    
    @staticmethod
    def registrar_mudanca_status(id_chamado, status_anterior, status_novo, id_usuario=None):
        """
        Registra uma mudança de status no histórico
        
        Args:
            id_chamado: ID do chamado
            status_anterior: Status anterior
            status_novo: Novo status
            id_usuario: ID do usuário que fez a mudança
        """
        descricao = f"Status alterado de '{status_anterior}' para '{status_novo}'"
        detalhes = {
            'status_anterior': status_anterior,
            'status_novo': status_novo,
            'tipo_mudanca': 'status'
        }
        
        return HistoricoService.adicionar_evento(
            id_chamado=id_chamado,
            tipo_evento='status_change',
            descricao=descricao,
            id_usuario=id_usuario,
            detalhes_adicionais=detalhes
        )
    
    @staticmethod
    def registrar_resposta_tecnico(id_chamado, resposta, id_usuario=None):
        """
        Registra uma resposta do técnico no histórico
        
        Args:
            id_chamado: ID do chamado
            resposta: Texto da resposta
            id_usuario: ID do usuário (técnico)
        """
        descricao = "Resposta adicionada pelo técnico"
        detalhes = {
            'resposta': resposta,
            'tipo_resposta': 'tecnico'
        }
        
        return HistoricoService.adicionar_evento(
            id_chamado=id_chamado,
            tipo_evento='response',
            descricao=descricao,
            id_usuario=id_usuario,
            detalhes_adicionais=detalhes
        )
    
    @staticmethod
    def registrar_notificacao_enviada(id_chamado, tipo_notificacao, destinatario, sucesso=True, erro=None):
        """
        Registra o envio de uma notificação no histórico
        
        Args:
            id_chamado: ID do chamado
            tipo_notificacao: Tipo da notificação ('email', 'sms', 'whatsapp')
            destinatario: Destinatário da notificação
            sucesso: Se a notificação foi enviada com sucesso
            erro: Mensagem de erro se houver
        """
        if sucesso:
            descricao = f"Notificação {tipo_notificacao} enviada para {destinatario}"
        else:
            descricao = f"Falha ao enviar notificação {tipo_notificacao} para {destinatario}"
        
        detalhes = {
            'tipo_notificacao': tipo_notificacao,
            'destinatario': destinatario,
            'sucesso': sucesso,
            'erro': erro
        }
        
        return HistoricoService.adicionar_evento(
            id_chamado=id_chamado,
            tipo_evento='notification_sent',
            descricao=descricao,
            detalhes_adicionais=detalhes
        )
    
    @staticmethod
    def registrar_criacao_chamado(id_chamado, dados_chamado, id_usuario=None):
        """
        Registra a criação de um chamado no histórico
        
        Args:
            id_chamado: ID do chamado
            dados_chamado: Dados do chamado criado
            id_usuario: ID do usuário que criou (se aplicável)
        """
        descricao = f"Chamado criado: {dados_chamado.get('titulo', 'Sem título')}"
        detalhes = {
            'protocolo': dados_chamado.get('protocolo'),
            'prioridade': dados_chamado.get('prioridade'),
            'cliente_nome': dados_chamado.get('cliente_nome'),
            'tipo_evento': 'criacao'
        }
        
        return HistoricoService.adicionar_evento(
            id_chamado=id_chamado,
            tipo_evento='created',
            descricao=descricao,
            id_usuario=id_usuario,
            detalhes_adicionais=detalhes
        )
    
    @staticmethod
    def registrar_comentario(id_chamado, comentario, id_usuario=None, tipo_usuario='sistema'):
        """
        Registra um comentário no histórico
        
        Args:
            id_chamado: ID do chamado
            comentario: Texto do comentário
            id_usuario: ID do usuário
            tipo_usuario: Tipo do usuário ('admin', 'tecnico', 'cliente', 'sistema')
        """
        descricao = f"Comentário adicionado por {tipo_usuario}"
        detalhes = {
            'comentario': comentario,
            'tipo_usuario': tipo_usuario
        }
        
        return HistoricoService.adicionar_evento(
            id_chamado=id_chamado,
            tipo_evento='comment',
            descricao=descricao,
            id_usuario=id_usuario,
            detalhes_adicionais=detalhes
        )
    
    @staticmethod
    def obter_estatisticas_historico(id_chamado):
        """
        Obtém estatísticas do histórico de um chamado
        
        Args:
            id_chamado: ID do chamado
            
        Returns:
            Dict com estatísticas
        """
        try:
            eventos = HistoricoChamado.query.filter_by(id_chamado=id_chamado).all()
            
            estatisticas = {
                'total_eventos': len(eventos),
                'mudancas_status': 0,
                'respostas_tecnico': 0,
                'notificacoes_enviadas': 0,
                'comentarios': 0,
                'primeiro_evento': None,
                'ultimo_evento': None
            }
            
            for evento in eventos:
                if evento.tipo_evento == 'status_change':
                    estatisticas['mudancas_status'] += 1
                elif evento.tipo_evento == 'response':
                    estatisticas['respostas_tecnico'] += 1
                elif evento.tipo_evento == 'notification_sent':
                    estatisticas['notificacoes_enviadas'] += 1
                elif evento.tipo_evento == 'comment':
                    estatisticas['comentarios'] += 1
            
            # Primeiro e último evento
            if eventos:
                eventos_ordenados = sorted(eventos, key=lambda x: x.data_hora)
                estatisticas['primeiro_evento'] = eventos_ordenados[0].data_hora.isoformat()
                estatisticas['ultimo_evento'] = eventos_ordenados[-1].data_hora.isoformat()
            
            return estatisticas
        except Exception as e:
            raise e

