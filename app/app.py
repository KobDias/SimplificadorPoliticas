from flask import Flask, jsonify, request, session, url_for, redirect, render_template
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
    resultados = None
    resumo = None
    objetivo = None
    if 'resultados' in session and session['id'] == id:
        resultados = session['resultados']
        resumo = session.get('resumo')
        objetivo = session.get('objetivo')
        id = session['id']
        # Limpe os dados da sessão após recuperá-los
        session.pop('resultados', None)
        session.pop('resumo', None)
        session.pop('objetivo', None)
        session.pop('id', None)
    politica = Politica.query.get_or_404(id)
    return render_template('visualizar_politica.html', politica=politica, resultados=resultados, resumo=resumo, objetivo=objetivo)  

@app.route('/editar_politica/<int:id>', methods=['GET', 'POST']) # EDITA POLITICA
def editar_politica(id):
    politica = Politica.query.get_or_404(id)
    if request.method == 'POST':
        politica.titulo = request.form['titulo']
        politica.descricao = request.form['descricao']
        db.session.commit()
        return redirect(url_for('home'))
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
    Your task is to analyze and provide summaries of its main points, trying to better it each time, returning to 
    the user a text with the terms simplified though accurate so they can comprehend how their data is being used. 
    Consider you're speaking to brazilians and lay people that don't undertand the minimun about law, much less LGDP.
    Upom specific words, you should provide their meaning between brackets, so the user can understand what it means.
    Remember to not repeat yourself.
    Your summary must be in portuguese, be clear and follow the structure:
    1. Summary: A summary that contains the main points in a clear way. It should be smaller than the actual policy.
    2. Objective: The main reason behind the politic.
    If you judge necessary, you can add more points to the summary, never more than 3 and remember to not repeat yourself.

    Once you finish all three summaries, you should choose between the three and return the one that is the most clear and easy to understand.
    You should return the analysis in a json format, with the following keys:
    - 'Best summary' : 
        - '1. Summary': 'the summary you choose as the best one'
        - '2. Objective': 'the objective you choose as the best one'

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
        },
        headers={
            'Authorization': f'Bearer {api_mistra}'
            }
    )
    if responseRaw.status_code == 200:
        resultados = responseRaw.json()
        contenta = resultados['choices'][0]['message']['content']
        content = contenta.strip('```json\n').strip('```')
        if content and content.startswith('{') and content.endswith('}'):
            # Decodifique o JSON
            content_dict = json.loads(content)
            print("\nDicionário decodificado:")
            print(content_dict)
        else:
            print("Erro: O conteúdo não é um JSON válido.")
            return "Erro: O conteúdo não é um JSON válido."

        best_summary = content_dict.get('Best summary')
        print("\nTipo de 'Best summary':")
        print(type(best_summary))
        if best_summary is None:
            print("Erro: A chave 'Best summary' não foi encontrada.")
        else:
            print(best_summary)
            # Acesse os valores dentro de 'Best summary'
            resumo = best_summary.get('1. Summary', '1. Resumo')
            objetivo = best_summary.get('2. Objective', '2. Objetivo')
            # Exiba os valores
            print("\nResumo:")
            print(resumo)
            print("\nObjetivo:")
            print(objetivo)
            
                # Armazenando o resultado na sessão
            session['resultados'] = True
            session['resumo'] = resumo
            session['objetivo'] = objetivo
            session['id'] = texto.id
        

        return redirect(url_for('visualizar_politica', id=id))
    else:
        return "Nenhuma escolha encontrada na resposta."
            
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