#!/bin/bash

# Script de Backup do Sistema de Chamados
# Versão: 2.0

set -e

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_$DATE.sql"

echo "Iniciando backup do banco de dados..."

# Criar backup
docker-compose exec -T db pg_dump -U chamados_user chamados > "$BACKUP_DIR/$BACKUP_FILE"

# Comprimir backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

echo "Backup criado: $BACKUP_DIR/$BACKUP_FILE.gz"

# Limpar backups antigos (manter últimos 7 dias)
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete

echo "Backup concluído com sucesso!"

