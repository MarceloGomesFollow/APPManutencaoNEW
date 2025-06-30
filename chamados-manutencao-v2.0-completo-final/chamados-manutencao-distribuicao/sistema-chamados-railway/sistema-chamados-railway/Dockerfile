# Dockerfile 

# 1) Imagem base leve
FROM python:3.11-slim

# 2) Diretório de trabalho
WORKDIR /app

# 3) Dependências de SO necessárias para compilar extensões
RUN apt-get update \
 && apt-get install -y gcc g++ \
 && rm -rf /var/lib/apt/lists/*

# 4) Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copiar todo o código da aplicação
COPY . .

# 6) Criar diretórios usados em runtime
RUN mkdir -p instance uploads logs backups

# 7) Garantir que "src" fique no PYTHONPATH e o Flask ache tudo
ENV PYTHONPATH=/app

# 8) Expor a porta padrão (só documentação, não define variável)
EXPOSE 5000

# 9) Usar um entrypoint script para garantir o correto tratamento de sinais e expansão de variáveis
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
