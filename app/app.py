from flask import Flask, request, session, url_for, redirect, render_template
import requests
from db import db
from models import Politica
import os
import json

api_mistra = os.getenv("MISTRAL_API_KEY")

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
    resumo = None
    objetivo = None
    if 'resumo' in session and session['id'] == id:
        resumo = session.get('resumo')
        objetivo = session.get('objetivo')
        id = session['id']
        # Limpe os dados da sessão após recuperá-los
        session.pop('resumo', None)
        session.pop('objetivo', None)
        session.pop('id', None)
    politica = Politica.query.get_or_404(id)
    return render_template('visualizar_politica.html', politica=politica, resumo=resumo, objetivo=objetivo)  

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
    Your task is to analyze and provide summaries of its main points, continuously improving the clarity, returning to 
    the user a text with the terms simplified though accurate so they can comprehend how their data is being used. 
    Consider you're speaking to brazilians and lay people that don't undertand the minimun about law, much less LGDP.
    When encountering technical terms, you should provide their meaning between parentheses, so the user can understand what it means.
    Remember to not repeat yourself.
    Your summary must be in portuguese, clear, informal but precise and follow the structure:
    1. Summary: A summary that contains the main points in a clear way. Prioritize small sentences and easy words. Make analogies when possible.
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
        else:
            print("Erro: O conteúdo não é um JSON válido.")

            session['resumo'] = "A politica pode ser muito curta ou o Mistral não conseguiu entender. Tente novamente."
            session['objetivo'] = "Erro: O conteúdo não é um JSON válido."
            session['id'] = texto.id

            return redirect(url_for('visualizar_politica', id=id))

        best_summary = content_dict.get('Best summary')
        if best_summary is None:
            session['resumo'] = "Erro: A chave 'Best summary' não foi encontrada."
            session['objetivo'] = "A politica pode ser muito curta ou o Mistral não conseguiu entender. Tente novamente."
            session['id'] = texto.id

            print("Erro: A chave 'Best summary' não foi encontrada.")
            return redirect(url_for('visualizar_politica', id=id))

        else:
            # Acesse os valores dentro de 'Best summary'
            resumo = best_summary.get('1. Summary', '1. Resumo')
            objetivo = best_summary.get('2. Objective', '2. Objetivo')
            
            # Armazenando o resultado na sessão
            session['resumo'] = resumo
            session['objetivo'] = objetivo
            session['id'] = texto.id
    
        return redirect(url_for('visualizar_politica', id=id))
    else:
        session['resumo'] = "A politica pode ser muito curta ou o Mistral não conseguiu entender. Tente novamente."
        session['objetivo'] = "Erro: Não foi possível obter a resposta do Mistral. Tente novamente."
        session['id'] = texto.id

        # Debug
        print(f"Erro: {responseRaw.status_code} - {responseRaw.text}")

        return redirect(url_for('visualizar_politica', id=id))            
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)