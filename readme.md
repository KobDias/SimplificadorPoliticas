# Simplificador de Politicas

Essa é uma aplicação simples para análise e simplificação de políticas de segurança, com foco na Lei Geral de Proteção de Dados (LGPD). O objetivo é tornar as políticas mais acessíveis e compreensíveis para usuários leigos.

## Funcionalidades

No simplificador, você pode criar e excluir politicas, como também visualizar elas listadas no home.
Existe também uma tela para cada politica criada, onde é possivel fazer uma analise.
A analise consiste em uma requisição a API do Mistral.Ai que gera um resumo da politica, explicando seu significado e declarando seu objetivo. 

## Como Rodar

Siga os passos abaixo para configurar e executar a aplicação localmente:

### 1. Pré-requisitos

Certifique-se de ter instalado:
- Python 3.8 ou superior
- `pip` (gerenciador de pacotes do Python)

### 2. Clonar o Repositório

Clone o repositório para sua máquina local:

```bash
git clone https://github.com/KobDias/SimplificadorPoliticas.git
cd SimplificadorPoliticas/
```

### 3. Criar e ativar o ambiente virtual

```bash
python -m venv venv
```

Ativar:

- No Windows:
```bash
venv\Scripts\activate
```
- No macOS/Linux:
```bash
source venv/bin/activate
```
### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar variáveis de ambiente
Crie um arquivo .env na raiz do projeto e configure a chave da sua api do mistral
```bash
MISTRAL_API_KEY=sua_chave_aqui
```

### 6. Rodar!

Por fim, rode a aplicação pelo app.py ou:
```bash
cd app/
flask run
```
