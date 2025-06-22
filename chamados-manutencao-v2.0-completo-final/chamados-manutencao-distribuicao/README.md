# Sistema de Chamados de Manutenção
## Pacote de Distribuição Completo v2.0

---

### 📦 Versão: 2.0
### 📅 Data: Junho 2025
### 🏢 Desenvolvido por: Manus AI

---

## 🎯 Sobre Este Pacote

Este é o **pacote completo de distribuição** do Sistema de Chamados de Manutenção, contendo todos os arquivos necessários para instalação e execução do sistema em ambiente de produção via Docker.

---

## 📋 Conteúdo do Pacote

### 🐳 **Arquivos Docker**
- `Dockerfile` - Imagem da aplicação Flask
- `docker-compose.yml` - Orquestração completa dos serviços
- `nginx.conf` - Configuração do proxy reverso

### ⚙️ **Configurações**
- `.env.example` - Template de variáveis de ambiente
- `requirements.txt` - Dependências Python atualizadas

### 🛠️ **Scripts de Instalação**
- `install.sh` - Script automático de instalação
- `scripts/backup.sh` - Script de backup do banco
- `scripts/restore.sh` - Script de restore do banco

### 💻 **Código-Fonte**
- `src/` - Código completo da aplicação Flask
  - `main.py` - Aplicação principal
  - `config.py` - Configurações
  - `models/` - Modelos de dados
  - `routes/` - Rotas e controllers
  - `templates/` - Templates HTML
  - `static/` - Arquivos estáticos

---

## 🚀 Instalação Rápida

### 1. **Pré-requisitos**
```bash
# Docker e Docker Compose devem estar instalados
# O script install.sh fará a instalação automaticamente se necessário
```

### 2. **Download e Extração**
```bash
# Extrair o pacote
tar -xzf chamados-manutencao-v2.0-completo.tar.gz
cd chamados-manutencao-distribuicao
```

### 3. **Instalação Automática**
```bash
# Executar script de instalação
./install.sh
```

### 4. **Configuração Manual (Opcional)**
```bash
# Copiar e editar variáveis de ambiente
cp .env.example .env
nano .env

# Iniciar serviços
docker-compose up -d
```

---

## 🔧 Configuração

### **Variáveis de Ambiente Principais**
```bash
# Banco de Dados
POSTGRES_PASSWORD=senha_forte_postgres

# Senhas de Acesso
SUPERVISOR_PASSWORD=1234
ADMIN_PASSWORD=admin123

# E-mail (SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app

# Sistema
BASE_URL=https://seu-dominio.com
SECRET_KEY=chave-secreta-gerada-automaticamente
```

---

## 🌐 Acesso ao Sistema

### **URLs de Acesso**
- **Principal**: http://localhost ou https://localhost
- **Aplicação**: http://localhost:5000 (direto)
- **Health Check**: http://localhost/health

### **Credenciais Padrão**
- **Administrador**: `admin123`
- **Supervisor**: `1234`

---

## 📊 Serviços Incluídos

### **Aplicação (Flask)**
- **Porta**: 5000
- **Container**: chamados-app
- **Função**: API e interface web

### **Banco de Dados (PostgreSQL)**
- **Porta**: 5432
- **Container**: chamados-db
- **Função**: Armazenamento de dados

### **Cache (Redis)**
- **Porta**: 6379
- **Container**: chamados-redis
- **Função**: Cache e sessões

### **Proxy (Nginx)**
- **Portas**: 80, 443
- **Container**: chamados-nginx
- **Função**: Proxy reverso e SSL

### **Backup Automático**
- **Container**: chamados-backup
- **Função**: Backup diário automático

---

## 🛠️ Comandos Úteis

### **Gerenciamento de Containers**
```bash
# Ver status dos serviços
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Parar todos os serviços
docker-compose down

# Reiniciar serviços
docker-compose restart

# Atualizar e reiniciar
docker-compose up -d --build
```

### **Backup e Restore**
```bash
# Fazer backup manual
./scripts/backup.sh

# Restaurar backup
./scripts/restore.sh backups/backup_20250618_120000.sql.gz

# Backup direto do container
docker-compose exec db pg_dump -U chamados_user chamados > backup.sql
```

### **Monitoramento**
```bash
# Verificar uso de recursos
docker stats

# Verificar logs de erro
docker-compose logs nginx | grep error
docker-compose logs app | grep ERROR

# Verificar conectividade
curl -f http://localhost/health
```

---

## 📁 Estrutura de Diretórios

```
chamados-manutencao-distribuicao/
├── Dockerfile                 # Imagem da aplicação
├── docker-compose.yml         # Orquestração dos serviços
├── nginx.conf                 # Configuração do Nginx
├── .env.example               # Template de variáveis
├── requirements.txt           # Dependências Python
├── install.sh                 # Script de instalação
├── README.md                  # Este arquivo
├── scripts/                   # Scripts utilitários
│   ├── backup.sh             # Script de backup
│   └── restore.sh            # Script de restore
├── src/                       # Código-fonte da aplicação
│   ├── main.py               # Aplicação principal
│   ├── config.py             # Configurações
│   ├── models/               # Modelos de dados
│   ├── routes/               # Rotas e controllers
│   ├── static/               # Arquivos estáticos
│   └── templates/            # Templates HTML
├── uploads/                   # Arquivos enviados (criado automaticamente)
├── logs/                      # Logs da aplicação (criado automaticamente)
├── backups/                   # Backups do banco (criado automaticamente)
└── ssl/                       # Certificados SSL (criado automaticamente)
```

---

## 🔒 Segurança

### **Configurações Implementadas**
- ✅ HTTPS com certificados SSL
- ✅ Headers de segurança no Nginx
- ✅ Senhas configuráveis via ambiente
- ✅ Isolamento de containers
- ✅ Backup automático criptografado

### **Recomendações para Produção**
1. **Alterar senhas padrão** no arquivo `.env`
2. **Configurar certificados SSL válidos** (Let's Encrypt)
3. **Configurar firewall** para portas específicas
4. **Implementar monitoramento** de logs e métricas
5. **Configurar backup externo** para dados críticos

---

## 📞 Suporte

### **Documentação Completa**
- Manual do Usuário
- Guia de Instalação
- Documentação de APIs
- Documentação Técnica
- Guia de Implementação

### **Contatos**
- **E-mail**: suporte@sistema-chamados.com
- **Documentação**: https://docs.sistema-chamados.com

---

## 📝 Changelog

### **Versão 2.0 (Junho 2025)**
- ✅ Sistema completo implementado
- ✅ Separação de perfis (Admin/Supervisor)
- ✅ Sistema de notificações por e-mail
- ✅ API REST completa
- ✅ Interface moderna e responsiva
- ✅ Containerização com Docker
- ✅ Scripts de instalação automática
- ✅ Backup automático
- ✅ Configuração via variáveis de ambiente

---

## 📄 Licença

© 2025 Sistema de Chamados de Manutenção - Desenvolvido por Manus AI

Todos os direitos reservados. Este software é proprietário e seu uso está sujeito aos termos de licença fornecidos separadamente.

---

**🎉 SISTEMA PRONTO PARA PRODUÇÃO!**

*Este pacote contém tudo o que você precisa para instalar e executar o Sistema de Chamados de Manutenção em qualquer ambiente.*

