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
