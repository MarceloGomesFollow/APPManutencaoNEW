# Dockerfile otimizado para Railway

# 1. Imagem base
FROM python:3.11-slim

# 2. Definir diretório de trabalho
WORKDIR /app

# 3. Instalar ferramentas de compilação (gcc/g++)
RUN apt-get update \
 && apt-get install -y gcc g++ \
 && rm -rf /var/lib/apt/lists/*

# 4. Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar todo o código da aplicação
COPY . .

# 6. Criar pastas usadas em runtime
RUN mkdir -p instance uploads logs backups

# 7. Ajustar PYTHONPATH para que `src.*` funcione
ENV PYTHONPATH=/app

# 8. Expor a porta fixa utilizada
EXPOSE 8080

# 9. Comando final: apenas sobe o Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "src.main:app"]

# 10. Variável de ambiente para o Flask
ENV FLASK_ENV=production
# 11. Variável de ambiente para o Gunicorn
ENV GUNICORN_CMD_ARGS="--access-logfile - --error-logfile -"
# 12. Variável de ambiente para o Railway
ENV RAILWAY_STATIC_DIR=/app/static
# 13. Variável de ambiente para o diretório de uploads
ENV UPLOAD_FOLDER=/app/uploads
# 14. Variável de ambiente para o diretório de logs
ENV LOG_FOLDER=/app/logs
# 15. Variável de ambiente para o diretório de backups
ENV BACKUP_FOLDER=/app/backups      
# 16. Variável de ambiente para o diretório de instância
ENV INSTANCE_FOLDER=/app/instance           
# 17. Variável de ambiente para o diretório de templates
ENV TEMPLATES_FOLDER=/app/templates
# 18. Variável de ambiente para o diretório de estáticos
ENV STATIC_FOLDER=/app/static       
# 19. Variável de ambiente para o diretório de uploads
ENV UPLOAD_FOLDER=/app/uploads
# 20. Variável de ambiente para o diretório de logs
ENV LOG_FOLDER=/app/logs
# 21. Variável de ambiente para o diretório de backups
ENV BACKUP_FOLDER=/app/backups          
# 22. Variável de ambiente para o diretório de instância
ENV INSTANCE_FOLDER=/app/instance
# 23. Variável de ambiente para o diretório de templates
ENV TEMPLATES_FOLDER=/app/templates
# 24. Variável de ambiente para o diretório de estáticos
ENV STATIC_FOLDER=/app/static
# 25. Variável de ambiente para o diretório de uploads
ENV UPLOAD_FOLDER=/app/uploads
