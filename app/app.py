from flask import Flask, jsonify, request, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import requests
from db import db
from models import Politica
import os
import json

api_mistra = os.getenv("MISTRAL_API_KEY")


import datetime as datatime

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

@app.route('/criar_politica', methods=['GET', 'POST']) # CRIA POLITICA
def criar_politica():
    if request.method == 'POST':

        titulo = request.form['titulo']
        descricao = request.form['descricao']

        nova_politica = Politica(titulo=titulo, descricao=descricao)
        db.session.add(nova_politica)
        db.session.commit()
        return redirect(url_for('home'))
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
    return redirect(url_for('home'))

@app.route('/analisar_politica/<int:id>')
def analisar_politica(id):
    texto = Politica.query.get_or_404(id)

    promptResumidor = f"""You are a legal expert, mainly focused on LGPD. You'll receive the description of a policy. 
    Your task is to analyze and provide summaries of its main points, trying to better it each time, returning to the user a text with the terms simplified though accurate so they can comprehend how their data is being used. Consider you're speaking to brazilians and lay people that don't undertand the minimun about law, much less LGDP
    Your summary must follow the following structure:
    1. **Summary**: A summary that contains the main points in a clear way. It should be smaller than the actual policy.
    2. **Objective**: The main reason behind the politic.
    3. **Colected data**: Which data is being collected and its prupose behind, also how it is being used.
    5. **Data sharing**: Whenever or not the data is being shared to a third-part and if so, which data, how and why.
    6. **Security**: Safety measurements to ensure the user's data is safe.
    7. **Language**: Always be in portuguese and make sure to be clear.
    
    # Policy description:
    # {texto.descricao}"""

    responseRaw = requests.post(
        'https://api.mistral.ai/v1/chat/completions',
        json={
            "model": "mistral-large-latest",
            "temperature": 0.7,
            "messages": [
                {"role": "system", "content": promptResumidor},
                {"role": "user", "content": texto.descricao}
            ],
            "n":3,
            # prompt: "You are a legal expert, mainly focused on LGPD. You'll receive the description of a policy. Your task is to analyze and provide a summary of its main points, returning to the user a text with the terms simplified tho acurate so they can comprehend how their data is being used."
        },
        headers={
            'Authorization': f'Bearer {api_mistra}'
            }
    )
    if responseRaw.status_code == 200:
        resultado = responseRaw.json()
        respostas = [choice['message']['content'] for choice in resultado.get('choices', [])]
        return jsonify(respostas)
    else:
        return jsonify({"error": "Erro ao classificar a resposta"}), 500
    
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