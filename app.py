from flask import Flask, request, render_template, send_from_directory
from flask_cors import CORS
from src.session import NewSession
import json
import os

app = Flask(__name__, 
            static_url_path='',
            static_folder='build',
            template_folder='build'
            )
CORS(app) # This will enable CORS for all routes
session = NewSession()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    '''Serve a files at src/public directory. Can be updated to run a React App'''
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route("/login/", methods=["POST"])
def login_route():
    data = request.get_json()
    cliente = session.login(data)
    
    return json.dumps(cliente)

@app.route('/search_cpf/', methods=['POST'])
def search_cpf():
    data = request.get_json()
    response = session.searchCpf(data, request=True)

    return json.dumps(response)

@app.route('/new_client/', methods=['POST'])
def new_client():
    data = request.get_json()
    # {'id_parceiro': 0, 'cliente': {'input_nome': 'Marcos Testador', 'input_telefone': '77988776655', 'input_email': 'marcos@bapka.com.br', 'input_cpf': '12345678901', 'input_senha': '123', 'input_confirmacao': '123'}}
    cliente = session.signupClient(data)

    return json.dumps(cliente)

@app.route('/modificar_cupons/', methods=['POST'])
def modificar_cupons():
    data = request.get_json()
    cliente = session.modifyCoupons(data)
    
    return json.dumps(cliente)

@app.route('/fetch_store/', methods=['POST'])
def fetch_store():
    data = request.get_json()

    parceiro = session.getParceiro(data)
    print(parceiro)
    return json.dumps(parceiro)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)