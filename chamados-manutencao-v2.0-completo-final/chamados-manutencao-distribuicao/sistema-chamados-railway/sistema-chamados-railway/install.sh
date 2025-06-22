#!/bin/bash

# Script de Instalação do Sistema de Chamados de Manutenção
# Versão: 2.0
# Data: Junho 2025

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Verificar se está rodando como root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "Este script não deve ser executado como root!"
        print_error "Execute como usuário normal que tenha acesso ao Docker."
        exit 1
    fi
}

# Verificar dependências
check_dependencies() {
    print_header "Verificando Dependências"
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker não está instalado!"
        print_message "Instalando Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        sudo usermod -aG docker $USER
        print_warning "Docker instalado. Você precisa fazer logout e login novamente."
        print_warning "Ou execute: newgrp docker"
    else
        print_message "Docker encontrado: $(docker --version)"
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose não está instalado!"
        print_message "Instalando Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    else
        print_message "Docker Compose encontrado: $(docker-compose --version)"
    fi
    
    # Verificar se o usuário está no grupo docker
    if ! groups $USER | grep -q docker; then
        print_warning "Usuário não está no grupo docker. Adicionando..."
        sudo usermod -aG docker $USER
        print_warning "Você precisa fazer logout e login novamente para aplicar as mudanças."
    fi
}

# Configurar variáveis de ambiente
setup_environment() {
    print_header "Configurando Variáveis de Ambiente"
    
    if [ ! -f .env ]; then
        print_message "Criando arquivo .env a partir do .env.example..."
        cp .env.example .env
        
        # Gerar chave secreta
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i "s/sua-chave-secreta-muito-forte-aqui-mude-isso/$SECRET_KEY/" .env
        
        # Gerar senha do PostgreSQL
        POSTGRES_PASSWORD=$(openssl rand -base64 32)
        sed -i "s/senha_forte_postgres/$POSTGRES_PASSWORD/" .env
        
        print_message "Arquivo .env criado com senhas geradas automaticamente."
        print_warning "IMPORTANTE: Edite o arquivo .env para configurar:"
        print_warning "- Configurações de e-mail (MAIL_*)"
        print_warning "- URL base do sistema (BASE_URL)"
        print_warning "- Senhas de acesso (SUPERVISOR_PASSWORD, ADMIN_PASSWORD)"
    else
        print_message "Arquivo .env já existe."
    fi
}

# Criar diretórios necessários
create_directories() {
    print_header "Criando Diretórios"
    
    mkdir -p uploads
    mkdir -p logs
    mkdir -p backups
    mkdir -p ssl
    mkdir -p scripts
    
    print_message "Diretórios criados com sucesso."
}

# Configurar SSL (certificado auto-assinado para desenvolvimento)
setup_ssl() {
    print_header "Configurando SSL"
    
    if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
        print_message "Gerando certificado SSL auto-assinado..."
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
            -subj "/C=BR/ST=SP/L=São Paulo/O=Sistema Chamados/CN=localhost"
        print_message "Certificado SSL gerado."
        print_warning "Para produção, substitua por certificados válidos!"
    else
        print_message "Certificados SSL já existem."
    fi
}

# Construir e iniciar containers
build_and_start() {
    print_header "Construindo e Iniciando Containers"
    
    print_message "Construindo imagens Docker..."
    docker-compose build
    
    print_message "Iniciando serviços..."
    docker-compose up -d
    
    print_message "Aguardando serviços iniciarem..."
    sleep 30
    
    # Verificar se os serviços estão rodando
    if docker-compose ps | grep -q "Up"; then
        print_message "Serviços iniciados com sucesso!"
    else
        print_error "Erro ao iniciar serviços. Verificando logs..."
        docker-compose logs
        exit 1
    fi
}

# Inicializar banco de dados
init_database() {
    print_header "Inicializando Banco de Dados"
    
    print_message "Aguardando PostgreSQL estar pronto..."
    sleep 10
    
    print_message "Criando tabelas do banco de dados..."
    docker-compose exec app python create_db.py
    
    print_message "Banco de dados configurado com sucesso!"
}

# Verificar instalação
verify_installation() {
    print_header "Verificando Instalação"
    
    # Verificar se os containers estão rodando
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Containers não estão rodando!"
        return 1
    fi
    
    # Verificar se a aplicação responde
    print_message "Testando conectividade..."
    sleep 5
    
    if curl -f -s http://localhost:5000/ > /dev/null; then
        print_message "Aplicação respondendo na porta 5000!"
    else
        print_warning "Aplicação não responde na porta 5000. Verificando logs..."
        docker-compose logs app | tail -20
    fi
    
    if curl -f -s http://localhost/ > /dev/null; then
        print_message "Nginx respondendo na porta 80!"
    else
        print_warning "Nginx não responde na porta 80. Verificando logs..."
        docker-compose logs nginx | tail -20
    fi
}

# Mostrar informações finais
show_final_info() {
    print_header "Instalação Concluída!"
    
    echo ""
    print_message "🎉 Sistema de Chamados de Manutenção instalado com sucesso!"
    echo ""
    print_message "📋 Informações de Acesso:"
    print_message "   URL: http://localhost (ou https://localhost para SSL)"
    print_message "   Administrador: admin123"
    print_message "   Supervisor: 1234"
    echo ""
    print_message "📁 Diretórios importantes:"
    print_message "   Uploads: ./uploads"
    print_message "   Logs: ./logs"
    print_message "   Backups: ./backups"
    echo ""
    print_message "🔧 Comandos úteis:"
    print_message "   Ver logs: docker-compose logs -f"
    print_message "   Parar: docker-compose down"
    print_message "   Reiniciar: docker-compose restart"
    print_message "   Backup: docker-compose exec backup pg_dump -h db -U chamados_user chamados > backup.sql"
    echo ""
    print_warning "⚠️  Próximos passos:"
    print_warning "   1. Edite o arquivo .env com suas configurações"
    print_warning "   2. Configure certificados SSL válidos para produção"
    print_warning "   3. Configure backup automático"
    print_warning "   4. Teste todas as funcionalidades"
    echo ""
}

# Função principal
main() {
    print_header "Sistema de Chamados de Manutenção - Instalação"
    print_message "Versão 2.0 - Junho 2025"
    echo ""
    
    check_root
    check_dependencies
    setup_environment
    create_directories
    setup_ssl
    build_and_start
    init_database
    verify_installation
    show_final_info
}

# Executar instalação
main "$@"

