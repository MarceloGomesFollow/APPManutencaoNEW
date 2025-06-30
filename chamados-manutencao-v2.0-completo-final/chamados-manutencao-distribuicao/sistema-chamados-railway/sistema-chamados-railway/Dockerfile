# Dockerfile otimizado para Railway
FROM python:3.11-slim

# 1. Definir diretório de trabalho
WORKDIR /app

# 2. Instalar dependências do SO (compiladores)
RUN apt-get update \
 && apt-get install -y gcc g++ \
 && rm -rf /var/lib/apt/lists/*

# 3. Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar todo o código da aplicação
COPY . .

# 5. Criar pastas usadas em runtime
RUN mkdir -p instance uploads logs backups

# 6. Ajustar PYTHONPATH para imports “src.*”
ENV PYTHONPATH=/app

# 7. Expor a porta fixa que o Gunicorn usa
EXPOSE 8080

# 8. Comando padrão: apenas sobe o Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "src.main:app"]

