# wsgi.py
"""
Ponto de entrada WSGI para produção.
Use este arquivo para rodar Gunicorn, uWSGI, etc:
    gunicorn wsgi:app
ou
    gunicorn src.main:app
"""

import os
import sys

# Adiciona o diretório 'src/' ao sys.path para facilitar imports absolutos
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "src")
    ),
)

from src import create_app

app = create_app()
