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
    # GET
    return render_template('criar_politica.html')

@app.route('/visualizar_politica/<int:id>') # VISUALIZA POLITICA
def visualizar_politica(id):
    # Limpando os dados
    resumo = None
    objetivo = None

    # Verifica se há dados na sessão
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
    if api_mistra is None:
        print("Erro: A chave da API do Mistral não está definida.")
        session['resumo'] = "Crie um arquivo .env na raiz do projeto e adicione a chave da api do Mistr"
        session['objetivo'] = "Erro: A chave da API do Mistral não está definida."
        session['id'] = id

        return redirect(url_for('visualizar_politica', id=id))
    else:
        texto = Politica.query.get_or_404(id) # receber a descrição da política pelo id

        # definindo o prompt para o Mistral
        promptResumidor = f"""
        You are a legal expert specialized in LGPD (Brazilian General Data Protection Law). You will receive the description of a data policy. 

        Your task is to:
        - Analyze the policy and provide a simplified summary in Brazilian Portuguese, using informal and clear language.
        - Explain any legal or technical terms by placing their meaning in parentheses, right after the term.
        - Avoid repeating information or stating the obvious.
        - Always return the result as a valid JSON object, using the structure below:

        {{
        "Best summary": {{
            "1. Summary": "Your simplified summary here, in Portuguese.",
            "2. Objective": "The main purpose of the policy, in Portuguese."
        }}
        }}

        If the policy text is too short or does not contain enough information to summarize, return this exact JSON:

        {{
        "Best summary": {{
            "1. Summary": "Não há informação suficiente no texto para uma análise.",
            "2. Objective": "O texto é muito curto para ser resumido."
        }}
        }}

        # Policy description:
        \"\"\"{texto.descricao}\"\"\"
        """


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
        if responseRaw.status_code == 200: # se requisição for bem sucedida
            resultados = responseRaw.json()
            contenta = resultados['choices'][0]['message']['content']
            content = contenta.strip('```json\n').strip('```') # limpa a estrutura do json
            if content and content.startswith('{') and content.endswith('}'): # se json valido
                content_dict = json.loads(content) # converte o json para dicionario
            else:
                # debug
                print("Erro: O conteúdo não é um JSON válido.")
                print(f"Conteúdo: {content}")

                # armazenando resultado
                session['resumo'] = "A politica pode ser muito curta ou o Mistral não conseguiu entender. Tente novamente."
                session['objetivo'] = "Erro: O conteúdo não é um JSON válido."
                session['id'] = texto.id

                return redirect(url_for('visualizar_politica', id=id))

            best_summary = content_dict.get('Best summary') # acessa o dicionario dentro do json

            if best_summary is None: # se não encontrar a chave 'Best summary'
                session['resumo'] = "Erro: A chave 'Best summary' não foi encontrada."
                session['objetivo'] = "A politica pode ser muito curta ou o Mistral não conseguiu entender. Tente novamente."
                session['id'] = texto.id

                print("Erro: A chave 'Best summary' não foi encontrada.")
                return redirect(url_for('visualizar_politica', id=id))
            else:
                # acessa os valores dentro de 'Best summary'
                resumo = best_summary.get('1. Summary', '1. Resumo')
                objetivo = best_summary.get('2. Objective', '2. Objetivo')
                
                # armazenando resultado
                session['resumo'] = resumo
                session['objetivo'] = objetivo
                session['id'] = texto.id
        
            return redirect(url_for('visualizar_politica', id=id))
        else: # requisição falhou
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