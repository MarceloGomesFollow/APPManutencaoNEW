from flask import render_template

@app.route('/relatorio')
def relatorio():
    return render_template('relatorio.html')