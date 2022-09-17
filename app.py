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
    id = data['id']
    cpf = data['cpf']

    sql = f'SELECT * FROM clientes WHERE cpf = {cpf}'
    response = session.database.run(sql, True)[0]
    lojas = eval(response['lojas'])
    print(lojas)
    if id in lojas:
        return json.dumps(response)

    else:
        return json.dumps({'error': 'Cliente não cadastro nessa loja'})        


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)