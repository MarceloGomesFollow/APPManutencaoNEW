# Dockerfile otimizado para Railway

FROM python:3.11-slim

# 1) Diretório de trabalho
WORKDIR /app

# 2) Dependências do SO (compiladores)
RUN apt-get update \
 && apt-get install -y gcc g++ \
 && rm -rf /var/lib/apt/lists/*

# 3) Instalação de dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copia todo o código
COPY . .

# 5) Cria pastas usadas em runtime
RUN mkdir -p instance uploads logs backups

# 6) Ajusta PYTHONPATH para “src.*” funcionar
ENV PYTHONPATH=/app

# 7) Expõe porta fixa que o Gunicorn usará
EXPOSE 8080

# 8) Somente inicia o servidor WSGI
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "src.main:app"]
