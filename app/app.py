from flask import Flask, request, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from db import db
from models import Politica

import datetime as datatime

#configuração do app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///politicas.db'
app.config['SECRET_KEY'] = 'DEVELOPER_KEY'
db.init_app(app)

#rotas
@app.route('/') # LISTA POLITICAS
def home():
    politicas = Politica.query.all()
    return render_template('index.html', politicas=politicas)

@app.route('/nova_politica', methods=['GET', 'POST']) # CRIA POLITICA
def nova_politica():
    if request.method == 'POST':

        titulo = request.form['titulo']
        descricao = request.form['descricao']

        nova_politica = Politica(titulo=titulo, descricao=descricao)
        db.session.add(nova_politica)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('criar_politica.html')

@app.route('/visualizar_politica/<int:id>') # VISUALIZA POLITICA
def visualizar_politica(id):
    politica = Politica.query.get_or_404(id)
    return render_template('visualizar_politica.html', politica=politica)

@app.route('/editar_politica/<int:id>', methods=['GET', 'POST']) # EDITA POLITICA
def editar_politica(id):
    politica = Politica.query.get_or_404(id)
    if request.method == 'POST':
        politica.titulo = request.form['titulo']
        politica.descricao = request.form['descricao']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('editar_politica.html', politica=politica)

@app.route('/deletar_politica/<int:id>') # DELETA POLITICA
def deletar_politica(id):
    politica = Politica.query.get_or_404(id)
    db.session.delete(politica)
    db.session.commit()

@app.route('/analisar_politica/<int:id>')
def analisar_politica(id):
    politica = Politica.query.get_or_404(id)
    


    return render_template('analisar_politica.html', politica=politica)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        politicas = [
            {'id': 1, 'titulo': 'Politica 1', 'descricao': 'Descricao 1'},
            {'id': 2, 'titulo': 'Politica 2', 'descricao': 'Descricao 2'},
            {'id': 3, 'titulo': 'Politica 3', 'descricao': 'Descricao 3'},
            {'id': 4, 'titulo': 'Politica 4', 'descricao': 'Descricao 4'},
            {'id': 5, 'titulo': 'Politica 5', 'descricao': 'Descricao 5'}
        ]
        for p in politicas:
            nova_politica = Politica.query.filter_by(titulo=p['titulo']).first()
            if not nova_politica:
                nova_politica = Politica(**p)
                db.session.add(nova_politica)
        db.session.commit()
    app.run(debug=True)