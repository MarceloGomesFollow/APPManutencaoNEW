from flask import Blueprint, request, render_template, redirect, url_for, session, flash, current_app
from functools import wraps

admin_auth_bp = Blueprint('admin_auth', __name__)

def admin_required(f):
    """Decorator para verificar se o usuário está logado como administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def supervisor_required(f):
    """Decorator para verificar se o usuário está logado como supervisor"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('supervisor_logged_in'):
            return redirect(url_for('admin_auth.supervisor_login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Login do administrador"""
    if request.method == 'POST':
        password = request.form.get('password')
        
        if password == current_app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            session['user_type'] = 'admin'
            session.permanent = True
            flash('Login de administrador realizado com sucesso!', 'success')
            return redirect(url_for('admin.painel_admin'))
        else:
            flash('Senha incorreta!', 'error')
    
    return render_template('admin_login.html')

@admin_auth_bp.route('/supervisor-login', methods=['GET', 'POST'])
def supervisor_login():
    """Login do supervisor"""
    if request.method == 'POST':
        password = request.form.get('password')
        
        if password == current_app.config['SUPERVISOR_PASSWORD']:
            session['supervisor_logged_in'] = True
            session['user_type'] = 'supervisor'
            session.permanent = True
            flash('Login de supervisor realizado com sucesso!', 'success')
            return redirect(url_for('chamado.painel_supervisor'))
        else:
            flash('Senha incorreta!', 'error')
    
    return render_template('supervisor_login.html')

@admin_auth_bp.route('/admin-logout')
def admin_logout():
    """Logout do administrador"""
    session.pop('admin_logged_in', None)
    session.pop('user_type', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('chamado.index'))

@admin_auth_bp.route('/supervisor-logout')
def supervisor_logout():
    """Logout do supervisor"""
    session.pop('supervisor_logged_in', None)
    session.pop('user_type', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('chamado.index'))

@admin_auth_bp.route('/check-access')
def check_access():
    """Verifica o tipo de acesso do usuário"""
    user_type = session.get('user_type')
    admin_logged = session.get('admin_logged_in', False)
    supervisor_logged = session.get('supervisor_logged_in', False)
    
    return {
        'user_type': user_type,
        'admin_logged': admin_logged,
        'supervisor_logged': supervisor_logged,
        'has_admin_access': admin_logged,
        'has_supervisor_access': supervisor_logged
    }

