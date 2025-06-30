# Dockerfile – substituir TOTALMENTE pelo texto abaixo

# 1. Base
FROM python:3.11-slim

# 2. Diretório de trabalho
WORKDIR /app

# 3. Ferramentas de compilação (gcc/g++)
RUN apt-get update \
 && apt-get install -y gcc g++ \
 && rm -rf /var/lib/apt/lists/*

# 4. Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia o seu código-fonte
COPY . .

# 6. Cria pastas usadas em runtime
RUN mkdir -p instance uploads logs backups

# 7. Ajusta o PYTHONPATH para que imports “src.*” funcionem
ENV PYTHONPATH=/app

# 8. Expõe a porta fixa que o Gunicorn usará
EXPOSE 8080

# 9. Inicia apenas o Gunicorn – sem rodar migrations aqui!
CMD ["gunicorn","--bind","0.0.0.0:8080","--workers","4","--timeout","120","src.main:app"]

