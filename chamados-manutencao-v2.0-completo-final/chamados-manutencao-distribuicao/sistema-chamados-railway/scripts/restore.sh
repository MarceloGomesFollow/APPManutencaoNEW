#!/bin/bash

# Script de Restore do Sistema de Chamados
# Versão: 2.0

set -e

if [ $# -eq 0 ]; then
    echo "Uso: $0 <arquivo_backup.sql.gz>"
    echo "Exemplo: $0 backups/backup_20250618_120000.sql.gz"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Erro: Arquivo de backup não encontrado: $BACKUP_FILE"
    exit 1
fi

echo "Restaurando backup: $BACKUP_FILE"

# Parar aplicação
echo "Parando aplicação..."
docker-compose stop app

# Descomprimir se necessário
if [[ $BACKUP_FILE == *.gz ]]; then
    TEMP_FILE="/tmp/restore_temp.sql"
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
else
    TEMP_FILE="$BACKUP_FILE"
fi

# Restaurar banco
echo "Restaurando banco de dados..."
docker-compose exec -T db psql -U chamados_user -d chamados < "$TEMP_FILE"

# Limpar arquivo temporário
if [[ $BACKUP_FILE == *.gz ]]; then
    rm "$TEMP_FILE"
fi

# Reiniciar aplicação
echo "Reiniciando aplicação..."
docker-compose start app

echo "Restore concluído com sucesso!"

