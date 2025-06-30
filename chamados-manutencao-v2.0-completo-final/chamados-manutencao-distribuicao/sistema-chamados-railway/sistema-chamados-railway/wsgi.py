# wsgi.py

import os
import sys

# Insere o diretório 'src/' no início do path de módulos
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "src")
    ),
)

from src import create_app

app = create_app()
