# Dockerfile 

# 1) Imagem base leve
FROM python:3.11-slim

# 2) Diretório de trabalho
WORKDIR /app

# 3) Dependências do sistema (gcc, g++)
RUN apt-get update \
 && apt-get install -y gcc g++ \
 && rm -rf /var/lib/apt/lists/*

# 4) Copia e instala as libs Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copia todo o seu código-fonte
COPY . .

# 6) Cria diretórios usados em runtime
RUN mkdir -p instance uploads logs backups

# 7) Ajusta PYTHONPATH para que imports "src.*" funcionem
ENV PYTHONPATH=/app

# 8) Expõe a porta que o Gunicorn vai usar
EXPOSE 8080

# 9) Comando final: apenas inicia o Gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 src.main:app
