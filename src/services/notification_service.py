from typing import Dict, Any, List
from datetime import datetime, timedelta
from src.services.email_service import email_service
from src.services.email_templates import email_templates
from src.models.chamado import Chamado
from src.models.user import db
import os

class NotificationService:
    """Serviço principal para gerenciamento de notificações"""
    
    def __init__(self):
        self.base_url = os.getenv('BASE_URL', 'http://localhost:5001')
        self.notificacoes_ativas = os.getenv('NOTIFICACOES_ATIVAS', 'true').lower() == 'true'
    
    def notificar_chamado_aberto(self, chamado_id: int) -> bool:
        """
        Envia notificação quando um chamado é aberto
        
        Args:
            chamado_id: ID do chamado
            
        Returns:
            bool: True se enviado com sucesso
        """
        if not self.notificacoes_ativas:
            return True
            
        try:
            chamado = Chamado.query.get(chamado_id)
            if not chamado:
                return False
            
            # Prepara dados para o template
            dados = self._preparar_dados_chamado(chamado)
            dados['link_chamado'] = f"{self.base_url}/chamado/{chamado.id}/detalhes"
            
            # Gera o e-mail
            email_data = email_templates.chamado_aberto(dados)
            
            # Obtém destinatários
            destinatarios = self._obter_destinatarios_manutencao(chamado.unidade_id)
            
            if not destinatarios:
                print(f"Nenhum destinatário encontrado para notificação do chamado {chamado_id}")
                return False
            
            # Envia e-mail
            sucesso = email_service.enviar_email(
                destinatarios=destinatarios,
                assunto=email_data['assunto'],
                corpo_html=email_data['html'],
                corpo_texto=email_data['texto']
            )
            
            # Registra no histórico
            email_service.registrar_notificacao(
                chamado_id=chamado_id,
                tipo_notificacao='abertura',
                destinatarios=destinatarios,
                assunto=email_data['assunto'],
                sucesso=sucesso
            )
            
            return sucesso
            
        except Exception as e:
            print(f"Erro ao notificar abertura do chamado {chamado_id}: {str(e)}")
            return False
    
    def notificar_chamado_atualizado(self, chamado_id: int, tipo_atualizacao: str, dados_extras: Dict[str, Any] = None) -> bool:
        """
        Envia notificação quando um chamado é atualizado
        
        Args:
            chamado_id: ID do chamado
            tipo_atualizacao: Tipo da atualização (status, resposta, acao)
            dados_extras: Dados adicionais para a notificação
            
        Returns:
            bool: True se enviado com sucesso
        """
        if not self.notificacoes_ativas:
            return True
            
        try:
            chamado = Chamado.query.get(chamado_id)
            if not chamado:
                return False
            
            # Prepara dados para o template
            dados = self._preparar_dados_chamado(chamado)
            dados['link_chamado'] = f"{self.base_url}/chamado/{chamado.id}/detalhes"
            dados['tipo_atualizacao'] = tipo_atualizacao
            
            # Adiciona dados extras se fornecidos
            if dados_extras:
                dados.update(dados_extras)
            
            # Gera o e-mail
            email_data = email_templates.chamado_atualizado(dados)
            
            # Obtém destinatários (cliente + equipe de manutenção)
            destinatarios = [chamado.cliente_email]
            destinatarios.extend(self._obter_destinatarios_manutencao(chamado.unidade_id))
            
            # Remove duplicatas
            destinatarios = list(set(destinatarios))
            
            # Envia e-mail
            sucesso = email_service.enviar_email(
                destinatarios=destinatarios,
                assunto=email_data['assunto'],
                corpo_html=email_data['html'],
                corpo_texto=email_data['texto']
            )
            
            # Registra no histórico
            email_service.registrar_notificacao(
                chamado_id=chamado_id,
                tipo_notificacao=f'atualizacao_{tipo_atualizacao}',
                destinatarios=destinatarios,
                assunto=email_data['assunto'],
                sucesso=sucesso
            )
            
            return sucesso
            
        except Exception as e:
            print(f"Erro ao notificar atualização do chamado {chamado_id}: {str(e)}")
            return False
    
    def notificar_chamado_concluido(self, chamado_id: int) -> bool:
        """
        Envia notificação quando um chamado é concluído
        
        Args:
            chamado_id: ID do chamado
            
        Returns:
            bool: True se enviado com sucesso
        """
        if not self.notificacoes_ativas:
            return True
            
        try:
            chamado = Chamado.query.get(chamado_id)
            if not chamado:
                return False
            
            # Prepara dados para o template
            dados = self._preparar_dados_chamado(chamado)
            dados['link_chamado'] = f"{self.base_url}/chamado/{chamado.id}/detalhes"
            dados['link_avaliacao'] = f"{self.base_url}/chamado/{chamado.id}/avaliar"
            
            # Calcula tempo de resolução
            if chamado.data_conclusao and chamado.data_abertura:
                tempo_resolucao = chamado.data_conclusao - chamado.data_abertura
                dados['tempo_resolucao'] = f"{tempo_resolucao.days} dias, {tempo_resolucao.seconds // 3600} horas"
            
            # Gera o e-mail
            email_data = email_templates.chamado_concluido(dados)
            
            # Envia principalmente para o cliente
            destinatarios = [chamado.cliente_email]
            
            # Envia e-mail
            sucesso = email_service.enviar_email(
                destinatarios=destinatarios,
                assunto=email_data['assunto'],
                corpo_html=email_data['html'],
                corpo_texto=email_data['texto']
            )
            
            # Registra no histórico
            email_service.registrar_notificacao(
                chamado_id=chamado_id,
                tipo_notificacao='conclusao',
                destinatarios=destinatarios,
                assunto=email_data['assunto'],
                sucesso=sucesso
            )
            
            return sucesso
            
        except Exception as e:
            print(f"Erro ao notificar conclusão do chamado {chamado_id}: {str(e)}")
            return False
    
    def enviar_lembretes_pendentes(self) -> int:
        """
        Envia lembretes para chamados pendentes há muito tempo
        
        Returns:
            int: Número de lembretes enviados
        """
        if not self.notificacoes_ativas:
            return 0
            
        try:
            # Busca chamados pendentes há mais de 24 horas
            limite_tempo = datetime.now() - timedelta(hours=24)
            
            chamados_pendentes = Chamado.query.filter(
                Chamado.status.in_(['aberto', 'em_andamento']),
                Chamado.data_abertura < limite_tempo
            ).all()
            
            lembretes_enviados = 0
            
            for chamado in chamados_pendentes:
                # Verifica se já foi enviado lembrete nas últimas 12 horas
                if self._ja_enviou_lembrete_recente(chamado.id):
                    continue
                
                # Prepara dados para o template
                dados = self._preparar_dados_chamado(chamado)
                dados['link_chamado'] = f"{self.base_url}/chamado/{chamado.id}/detalhes"
                
                # Calcula tempo em aberto
                tempo_aberto = datetime.now() - chamado.data_abertura
                dados['tempo_aberto'] = f"{tempo_aberto.days} dias, {tempo_aberto.seconds // 3600} horas"
                
                # Gera o e-mail
                email_data = email_templates.lembrete_pendente(dados)
                
                # Obtém destinatários da equipe de manutenção
                destinatarios = self._obter_destinatarios_manutencao(chamado.unidade_id)
                
                if destinatarios:
                    # Envia e-mail
                    sucesso = email_service.enviar_email(
                        destinatarios=destinatarios,
                        assunto=email_data['assunto'],
                        corpo_html=email_data['html'],
                        corpo_texto=email_data['texto']
                    )
                    
                    # Registra no histórico
                    email_service.registrar_notificacao(
                        chamado_id=chamado.id,
                        tipo_notificacao='lembrete',
                        destinatarios=destinatarios,
                        assunto=email_data['assunto'],
                        sucesso=sucesso
                    )
                    
                    if sucesso:
                        lembretes_enviados += 1
            
            return lembretes_enviados
            
        except Exception as e:
            print(f"Erro ao enviar lembretes: {str(e)}")
            return 0
    
    def _preparar_dados_chamado(self, chamado: Chamado) -> Dict[str, Any]:
        """Prepara dados do chamado para os templates"""
        return {
            'protocolo': chamado.protocolo,
            'titulo': chamado.titulo,
            'descricao': chamado.descricao,
            'cliente_nome': chamado.cliente_nome,
            'cliente_email': chamado.cliente_email,
            'cliente_telefone': chamado.cliente_telefone,
            'prioridade': chamado.prioridade,
            'status': chamado.status,
            'data_abertura': chamado.data_abertura.strftime('%d/%m/%Y às %H:%M') if chamado.data_abertura else '',
            'data_conclusao': chamado.data_conclusao.strftime('%d/%m/%Y às %H:%M') if chamado.data_conclusao else '',
            'unidade_nome': chamado.unidade.nome if chamado.unidade else 'Não informado',
            'turno_nome': chamado.turno.nome if chamado.turno else 'Não informado',
            'local_nome': chamado.local_apontamento.nome if chamado.local_apontamento else 'Não informado',
            'nao_conformidade_nome': chamado.nao_conformidade.nome if chamado.nao_conformidade else None,
            'resposta_tecnico': chamado.resposta_tecnico,
            'acao_tomada': chamado.acao_tomada,
            'solucao_aplicada': chamado.acao_tomada  # Alias para template de conclusão
        }
    
    def _obter_destinatarios_manutencao(self, unidade_id: int = None) -> List[str]:
        """Obtém lista de e-mails da equipe de manutenção"""
        return email_service.obter_contatos_notificacao(unidade_id)
    
    def _ja_enviou_lembrete_recente(self, chamado_id: int) -> bool:
        """Verifica se já foi enviado lembrete nas últimas 12 horas"""
        from src.models.historico_notificacoes import HistoricoNotificacoes
        
        limite_tempo = datetime.now() - timedelta(hours=12)
        
        lembrete_recente = HistoricoNotificacoes.query.filter(
            HistoricoNotificacoes.chamado_id == chamado_id,
            HistoricoNotificacoes.tipo_notificacao == 'lembrete',
            HistoricoNotificacoes.data_envio > limite_tempo,
            HistoricoNotificacoes.sucesso == True
        ).first()
        
        return lembrete_recente is not None

# Instância global do serviço
notification_service = NotificationService()

