import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
from typing import List, Optional
from src.models.user import db
from src.models.historico_notificacoes import HistoricoNotificacoes
from src.models.contato_notificacao import ContatoNotificacaoManutencao

class EmailService:
    """Serviço para envio de e-mails e notificações"""
    
    def __init__(self):
        # Configurações de e-mail (podem vir de variáveis de ambiente)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER', 'sistema.chamados@empresa.com')
        self.email_password = os.getenv('EMAIL_PASSWORD', 'senha_app')
        self.email_from_name = os.getenv('EMAIL_FROM_NAME', 'Sistema de Chamados')
    
    def enviar_email(self, 
                    destinatarios: List[str], 
                    assunto: str, 
                    corpo_html: str, 
                    corpo_texto: str = None,
                    anexos: List[str] = None) -> bool:
        """
        Envia e-mail para uma lista de destinatários
        
        Args:
            destinatarios: Lista de e-mails dos destinatários
            assunto: Assunto do e-mail
            corpo_html: Corpo do e-mail em HTML
            corpo_texto: Corpo do e-mail em texto simples (opcional)
            anexos: Lista de caminhos para arquivos anexos (opcional)
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        try:
            # Cria a mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.email_from_name} <{self.email_user}>"
            msg['To'] = ', '.join(destinatarios)
            msg['Subject'] = assunto
            
            # Adiciona corpo em texto simples se fornecido
            if corpo_texto:
                part_texto = MIMEText(corpo_texto, 'plain', 'utf-8')
                msg.attach(part_texto)
            
            # Adiciona corpo em HTML
            part_html = MIMEText(corpo_html, 'html', 'utf-8')
            msg.attach(part_html)
            
            # Adiciona anexos se fornecidos
            if anexos:
                for arquivo in anexos:
                    if os.path.exists(arquivo):
                        with open(arquivo, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(arquivo)}'
                        )
                        msg.attach(part)
            
            # Conecta ao servidor SMTP e envia
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar e-mail: {str(e)}")
            return False
    
    def registrar_notificacao(self, 
                            chamado_id: int, 
                            tipo_notificacao: str,
                            destinatarios: List[str], 
                            assunto: str, 
                            sucesso: bool,
                            erro: str = None):
        """
        Registra o histórico de notificação no banco de dados
        
        Args:
            chamado_id: ID do chamado
            tipo_notificacao: Tipo da notificação (abertura, resposta, conclusao, etc.)
            destinatarios: Lista de destinatários
            assunto: Assunto da notificação
            sucesso: Se o envio foi bem-sucedido
            erro: Mensagem de erro se houver
        """
        try:
            historico = HistoricoNotificacoes(
                chamado_id=chamado_id,
                tipo_notificacao=tipo_notificacao,
                destinatarios=', '.join(destinatarios),
                assunto=assunto,
                data_envio=datetime.now(),
                sucesso=sucesso,
                erro=erro
            )
            
            db.session.add(historico)
            db.session.commit()
            
        except Exception as e:
            print(f"Erro ao registrar notificação: {str(e)}")
            db.session.rollback()
    
    def obter_contatos_notificacao(self, unidade_id: int = None) -> List[str]:
        """
        Obtém lista de contatos para notificação de manutenção
        
        Args:
            unidade_id: ID da unidade (opcional, se None retorna todos)
            
        Returns:
            List[str]: Lista de e-mails para notificação
        """
        try:
            query = ContatoNotificacaoManutencao.query.filter_by(ativo=True)
            
            if unidade_id:
                query = query.filter_by(unidade_id=unidade_id)
            
            contatos = query.all()
            return [contato.email for contato in contatos]
            
        except Exception as e:
            print(f"Erro ao obter contatos: {str(e)}")
            return []

# Instância global do serviço
email_service = EmailService()

