from burgos.session import Session, Connection
import json


class NewSession(Session):
    def __init__(self):
        login_table = None
        database_auth = config['database']
        super().__init__(database_auth, login_table)
        
    def reconnectIfNeeded(self):
        try:
            if not self.database.connection.is_connected():
                self.reconnectDatabase()
        except:
            pass
        
    def login(self, data:dict):
        self.reconnectIfNeeded()
        
        if data['type'] == 'cliente':
            login_table = config['database']['table_clientes']
            login_column = 'telefone'
        elif data['type'] == 'parceiro':
            login_table = config['database']['table_parceiros']
            login_column = 'email'
            
        data = normalizeUser(data)

        sql = f"SELECT * FROM {login_table} WHERE {login_column} = '{data['user']}'"
        try:
            user = self.database.run(sql, dict_cursor = True)[0]

        except Exception as error:
            return {'error': 'Usuário não encontrado'}
        
        if data['password'] == user['senha']:
            user.update({'error': None})
            return user
        else:
            return {'error': 'Senha inválida'}
            
def normalizeUser(data):
    new_data = {}
    if data['type'] == 'cliente':
        new_data.update({'user': data['user_cliente']})   
        new_data.update({'password': data['password_cliente']})   

    elif data['type'] == 'parceiro':
        new_data.update({'user': data['user_parceiro']})   
        new_data.update({'password': data['password_parceiro']})   
        
    for key in data:
        if key == list(data)[0] or key == list(data)[1]:
            continue
        new_data.update({key: data[key]})
        
    return new_data
    
config = json.load(open('config.json'))