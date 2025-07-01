from flask import Blueprint, render_template
from src.models import Perfil  # Ajuste o import conforme sua estrutura

routes = Blueprint('routes', __name__)

@routes.route('/admin/perfis')
def listar_perfis():
    perfis = Perfil.query.all()
    return render_template('perfis.html', perfis=perfis)