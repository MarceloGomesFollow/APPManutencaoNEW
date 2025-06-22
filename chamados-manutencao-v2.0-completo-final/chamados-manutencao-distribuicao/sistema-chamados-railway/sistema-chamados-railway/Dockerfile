# Dockerfile otimizado para Railway
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para cache de layers
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p instance uploads logs backups

# Definir variáveis de ambiente
ENV FLASK_APP=src.main:app
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Criar banco de dados com contexto Flask adequado
RUN python create_db.py

# Expor porta
EXPOSE $PORT

# Comando para iniciar a aplicação
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 src.main:app

