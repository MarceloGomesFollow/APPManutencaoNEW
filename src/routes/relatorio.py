from flask import Flask, render_template
from src.models.chamado import Chamado

app = Flask(__name__)

@app.route('/relatorio')
def relatorio():
    return render_template('relatorio.html')
