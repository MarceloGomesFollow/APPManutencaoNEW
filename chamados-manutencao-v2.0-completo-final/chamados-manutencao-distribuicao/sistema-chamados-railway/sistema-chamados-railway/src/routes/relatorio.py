from flask import Blueprint, render_template

routes = Blueprint('routes', __name__)

@routes.route('/relatorio')
def relatorio():
    return render_template('relatorio.html')