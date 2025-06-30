# Dockerfile otimizado para Railway
FROM python:3.11-slim

WORKDIR /app

# Dependências de SO necessárias (compiladores)
RUN apt-get update && apt-get install -y \
    gcc g++ \
  && rm -rf /var/lib/apt/lists/*

# Instala as libs Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

# Cria pastas utilizadas pela app
RUN mkdir -p instance uploads logs backups

# Define o PYTHONPATH para que imports src.* funcionem
ENV PYTHONPATH=/app

# Expõe a porta fixa que o Railway usará
EXPOSE 8080

# No runtime, o Railway usará seu Procfile para a fase de release,
# e este CMD apenas inicia o Gunicorn para servir o app:
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "src.main:app"]
