from app import app

from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Siffran'}
    return render_template('app.html', title='Home', user=user)