from datetime import datetime
from typing import Dict, Any

class EmailTemplates:
    """Templates de e-mail para diferentes tipos de notificação"""
    
    @staticmethod
    def get_base_template() -> str:
        """Template base para todos os e-mails"""
        return """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sistema de Chamados</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background-color: white;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #007bff;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #007bff;
                    margin: 0;
                    font-size: 24px;
                }}
                .protocolo {{
                    background-color: #007bff;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 25px;
                    display: inline-block;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .status {{
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    display: inline-block;
                    margin: 5px 0;
                }}
                .status.aberto {{ background-color: #28a745; color: white; }}
                .status.em_andamento {{ background-color: #17a2b8; color: white; }}
                .status.aguardando_material {{ background-color: #ffc107; color: #212529; }}
                .status.concluido {{ background-color: #28a745; color: white; }}
                .prioridade {{
                    padding: 5px 12px;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 12px;
                    display: inline-block;
                }}
                .prioridade.alta {{ background-color: #dc3545; color: white; }}
                .prioridade.media {{ background-color: #ffc107; color: #212529; }}
                .prioridade.baixa {{ background-color: #28a745; color: white; }}
                .info-box {{
                    background-color: #f8f9fa;
                    border-left: 4px solid #007bff;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    color: #6c757d;
                    font-size: 12px;
                }}
                .btn {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .btn:hover {{
                    background-color: #0056b3;
                }}
                .timeline-item {{
                    border-left: 3px solid #007bff;
                    padding-left: 15px;
                    margin: 10px 0;
                    padding-bottom: 10px;
                }}
                .timeline-item:last-child {{
                    border-left-color: transparent;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔧 Sistema de Chamados de Manutenção</h1>
                </div>
                {content}
                <div class="footer">
                    <p>Este é um e-mail automático do Sistema de Chamados de Manutenção.</p>
                    <p>Data/Hora: {data_envio}</p>
                    <p>Não responda este e-mail. Em caso de dúvidas, entre em contato com a equipe de manutenção.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def chamado_aberto(dados: Dict[str, Any]) -> Dict[str, str]:
        """Template para notificação de chamado aberto"""
        content = f"""
        <h2>🆕 Novo Chamado Aberto</h2>
        
        <div class="protocolo">#{dados.get('protocolo', 'N/A')}</div>
        
        <div class="info-box">
            <h3>📋 Detalhes do Chamado</h3>
            <p><strong>Título:</strong> {dados.get('titulo', '')}</p>
            <p><strong>Cliente:</strong> {dados.get('cliente_nome', '')}</p>
            <p><strong>E-mail:</strong> {dados.get('cliente_email', '')}</p>
            <p><strong>Telefone:</strong> {dados.get('cliente_telefone', 'Não informado')}</p>
            <p><strong>Prioridade:</strong> <span class="prioridade {dados.get('prioridade', 'media')}">{dados.get('prioridade', 'Média').upper()}</span></p>
            <p><strong>Status:</strong> <span class="status {dados.get('status', 'aberto')}">{dados.get('status', 'Aberto').replace('_', ' ').title()}</span></p>
        </div>
        
        <div class="info-box">
            <h3>🏢 Localização</h3>
            <p><strong>Unidade:</strong> {dados.get('unidade_nome', 'Não informado')}</p>
            <p><strong>Local:</strong> {dados.get('local_nome', 'Não informado')}</p>
            <p><strong>Turno:</strong> {dados.get('turno_nome', 'Não informado')}</p>
        </div>
        
        <div class="info-box">
            <h3>📝 Descrição</h3>
            <p>{dados.get('descricao', '')}</p>
        </div>
        
        {f'<div class="info-box"><h3>⚠️ Não Conformidade</h3><p>{dados.get("nao_conformidade_nome", "")}</p></div>' if dados.get('nao_conformidade_nome') else ''}
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{dados.get('link_chamado', '#')}" class="btn">Ver Chamado Completo</a>
        </div>
        """
        
        html = EmailTemplates.get_base_template().format(
            content=content,
            data_envio=datetime.now().strftime('%d/%m/%Y às %H:%M')
        )
        
        return {
            'assunto': f"🆕 Novo Chamado #{dados.get('protocolo', 'N/A')} - {dados.get('titulo', '')}",
            'html': html,
            'texto': f"Novo chamado aberto: #{dados.get('protocolo', 'N/A')} - {dados.get('titulo', '')}\n\nCliente: {dados.get('cliente_nome', '')}\nDescrição: {dados.get('descricao', '')}"
        }
    
    @staticmethod
    def chamado_atualizado(dados: Dict[str, Any]) -> Dict[str, str]:
        """Template para notificação de chamado atualizado"""
        content = f"""
        <h2>🔄 Chamado Atualizado</h2>
        
        <div class="protocolo">#{dados.get('protocolo', 'N/A')}</div>
        
        <div class="info-box">
            <h3>📋 Informações do Chamado</h3>
            <p><strong>Título:</strong> {dados.get('titulo', '')}</p>
            <p><strong>Cliente:</strong> {dados.get('cliente_nome', '')}</p>
            <p><strong>Status Anterior:</strong> <span class="status {dados.get('status_anterior', '')}">{dados.get('status_anterior', '').replace('_', ' ').title()}</span></p>
            <p><strong>Status Atual:</strong> <span class="status {dados.get('status', '')}">{dados.get('status', '').replace('_', ' ').title()}</span></p>
        </div>
        
        {f'<div class="info-box"><h3>💬 Resposta Técnica</h3><p>{dados.get("resposta_tecnico", "")}</p></div>' if dados.get('resposta_tecnico') else ''}
        
        {f'<div class="info-box"><h3>🔧 Ação Realizada</h3><p>{dados.get("acao_tomada", "")}</p></div>' if dados.get('acao_tomada') else ''}
        
        <div class="info-box">
            <h3>📅 Timeline</h3>
            <div class="timeline-item">
                <strong>Atualização:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M')}<br>
                <em>{dados.get('tipo_atualizacao', 'Status alterado')}</em>
            </div>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{dados.get('link_chamado', '#')}" class="btn">Ver Chamado Completo</a>
        </div>
        """
        
        html = EmailTemplates.get_base_template().format(
            content=content,
            data_envio=datetime.now().strftime('%d/%m/%Y às %H:%M')
        )
        
        return {
            'assunto': f"🔄 Atualização Chamado #{dados.get('protocolo', 'N/A')} - {dados.get('status', '').replace('_', ' ').title()}",
            'html': html,
            'texto': f"Chamado atualizado: #{dados.get('protocolo', 'N/A')}\n\nStatus: {dados.get('status', '').replace('_', ' ').title()}\n\n{dados.get('resposta_tecnico', dados.get('acao_tomada', ''))}"
        }
    
    @staticmethod
    def chamado_concluido(dados: Dict[str, Any]) -> Dict[str, str]:
        """Template para notificação de chamado concluído"""
        content = f"""
        <h2>✅ Chamado Concluído</h2>
        
        <div class="protocolo">#{dados.get('protocolo', 'N/A')}</div>
        
        <div class="info-box">
            <h3>📋 Resumo do Atendimento</h3>
            <p><strong>Título:</strong> {dados.get('titulo', '')}</p>
            <p><strong>Cliente:</strong> {dados.get('cliente_nome', '')}</p>
            <p><strong>Data Abertura:</strong> {dados.get('data_abertura', '')}</p>
            <p><strong>Data Conclusão:</strong> {dados.get('data_conclusao', '')}</p>
            <p><strong>Tempo Total:</strong> {dados.get('tempo_resolucao', 'N/A')}</p>
        </div>
        
        {f'<div class="info-box"><h3>🔧 Solução Aplicada</h3><p>{dados.get("solucao_aplicada", "")}</p></div>' if dados.get('solucao_aplicada') else ''}
        
        <div class="info-box">
            <h3>📊 Avaliação do Atendimento</h3>
            <p>Gostaríamos de saber sua opinião sobre o atendimento recebido.</p>
            <div style="text-align: center; margin: 20px 0;">
                <a href="{dados.get('link_avaliacao', '#')}" class="btn">Avaliar Atendimento</a>
            </div>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{dados.get('link_chamado', '#')}" class="btn">Ver Detalhes Completos</a>
        </div>
        """
        
        html = EmailTemplates.get_base_template().format(
            content=content,
            data_envio=datetime.now().strftime('%d/%m/%Y às %H:%M')
        )
        
        return {
            'assunto': f"✅ Chamado Concluído #{dados.get('protocolo', 'N/A')} - {dados.get('titulo', '')}",
            'html': html,
            'texto': f"Chamado concluído: #{dados.get('protocolo', 'N/A')} - {dados.get('titulo', '')}\n\nData conclusão: {dados.get('data_conclusao', '')}\nTempo total: {dados.get('tempo_resolucao', 'N/A')}"
        }
    
    @staticmethod
    def lembrete_pendente(dados: Dict[str, Any]) -> Dict[str, str]:
        """Template para lembrete de chamado pendente"""
        content = f"""
        <h2>⏰ Lembrete - Chamado Pendente</h2>
        
        <div class="protocolo">#{dados.get('protocolo', 'N/A')}</div>
        
        <div class="info-box">
            <h3>⚠️ Atenção Necessária</h3>
            <p><strong>Título:</strong> {dados.get('titulo', '')}</p>
            <p><strong>Cliente:</strong> {dados.get('cliente_nome', '')}</p>
            <p><strong>Status:</strong> <span class="status {dados.get('status', '')}">{dados.get('status', '').replace('_', ' ').title()}</span></p>
            <p><strong>Prioridade:</strong> <span class="prioridade {dados.get('prioridade', 'media')}">{dados.get('prioridade', 'Média').upper()}</span></p>
            <p><strong>Tempo em Aberto:</strong> {dados.get('tempo_aberto', 'N/A')}</p>
        </div>
        
        <div class="info-box">
            <h3>📝 Descrição Original</h3>
            <p>{dados.get('descricao', '')}</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{dados.get('link_chamado', '#')}" class="btn">Atender Chamado</a>
        </div>
        """
        
        html = EmailTemplates.get_base_template().format(
            content=content,
            data_envio=datetime.now().strftime('%d/%m/%Y às %H:%M')
        )
        
        return {
            'assunto': f"⏰ Lembrete - Chamado #{dados.get('protocolo', 'N/A')} pendente há {dados.get('tempo_aberto', 'N/A')}",
            'html': html,
            'texto': f"Lembrete: Chamado #{dados.get('protocolo', 'N/A')} pendente\n\nTempo em aberto: {dados.get('tempo_aberto', 'N/A')}\nPrioridade: {dados.get('prioridade', 'Média')}"
        }

# Instância global dos templates
email_templates = EmailTemplates()

