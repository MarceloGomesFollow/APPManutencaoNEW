# src/routes/auth.py
from flask import Blueprint, request, render_template, redirect, url_for, session, flash, current_app
from functools import wraps

# 1) Blueprint com prefixo /admin
admin_auth_bp = Blueprint(
    'admin_auth',
    __name__,
    url_prefix='/admin'
)

# Decorator para checar login de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator para checar login de supervisor
def supervisor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('supervisor_logged_in'):
            return redirect(url_for('admin_auth.supervisor_login'))
        return f(*args, **kwargs)
    return decorated_function

# 2) Rota de login de administrador em /admin/login
@admin_auth_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == current_app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            session['user_type'] = 'admin'
            flash('Login de administrador realizado com sucesso!', 'success')
            return redirect(url_for('admin.painel_admin'))
        flash('Senha incorreta!', 'error')
    return render_template('admin_login.html')

# 2) Rota de login de supervisor em /admin/supervisor-login
@admin_auth_bp.route('/supervisor-login', methods=['GET', 'POST'])
def supervisor_login():
    if request.method == 'POST':
        password = request.form.get('senha')
        if password == current_app.config['SUPERVISOR_PASSWORD']:
            session['supervisor_logged_in'] = True
            session['user_type'] = 'supervisor'
            flash('Login de supervisor realizado com sucesso!', 'success')
            return redirect(url_for('chamado.painel_supervisor'))
        flash('Senha incorreta!', 'error')
    return render_template('supervisor_login.html')

# 3) Logout de administrador em /admin/logout
@admin_auth_bp.route('/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('user_type', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('chamado.index'))

# 3) Logout de supervisor em /admin/supervisor-logout
@admin_auth_bp.route('/supervisor-logout')
def supervisor_logout():
    session.pop('supervisor_logged_in', None)
    session.pop('user_type', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('chamado.index'))

# 4) Rota opcional para checar acesso via JSON
@admin_auth_bp.route('/check-access')
def check_access():
    return {
        'user_type': session.get('user_type'),
        'admin_logged': session.get('admin_logged_in', False),
        'supervisor_logged': session.get('supervisor_logged_in', False)
    }
