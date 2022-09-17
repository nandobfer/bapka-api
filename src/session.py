from burgos.session import Session, Connection
import json


class NewSession(Session):
    def __init__(self):
        login_table = None
        database_auth = config['database']
        super().__init__(database_auth, login_table)
        self.history_table = config['database']['table_historicos']
        
    def login(self, data:dict):
        if data['type'] == 'cliente':
            login_table = config['database']['table_clientes']
            login_column = 'telefone'
            history_type = 'parceiro'
        elif data['type'] == 'parceiro':
            login_table = config['database']['table_parceiros']
            login_column = 'email'
            history_type = 'cliente'
            
        data = normalizeUser(data)

        sql = f"SELECT * FROM {login_table} WHERE {login_column} = '{data['user']}'"
        try:
            user = self.database.run(sql, dict_cursor = True)[0]

        except Exception as error:
            return {'error': 'Usuário não encontrado'}
        
        if data['password'] == user['senha']:
            user.update({'error': None})
            history = self.getHistory(user_id=user['id'], user_type=history_type, quantity=3)
            user.update({'historico': history})
            return user
        else:
            return {'error': 'Senha inválida'}
        
    def getHistory(self, user_id:int, user_type:str, quantity = 0):
        sql = f'SELECT id_{user_type}, nome_{user_type}, data, hora, quantidade FROM {self.history_table} WHERE id_{user_type} = {user_id} ORDER BY id DESC {f"LIMIT {quantity}" if quantity > 0 else ""};'
        print(sql)
        data = self.database.run(sql, True)

        for history in data:
            history.update({'alvo': user_type.capitalize()})
            
            history.update({'id': history[f'id_{user_type}']})
            history.update({'nome': history[f'nome_{user_type}'].split()[0]})
            history.pop(f'id_{user_type}')
            history.pop(f'nome_{user_type}')
            
            if history['quantidade'] < 0:
                history.update({'operacao': 'Removido'})
            else:
                history.update({'operacao': 'Adicionado'})
            
        data[-1].update({'last': True})
            
        print(data)
        return data
        
    def searchCpf(self, data):
        id = data['id']
        cpf = data['cpf']

        sql = f'SELECT * FROM clientes WHERE cpf = {cpf}'
        try:
            response = self.database.run(sql, True)[0]
        except:
            return {'error': 'Cliente não cadastrado.'}
            
        lojas = eval(response['lojas'])
        if id in lojas:
            return response

        else:
            return {'error': 'Cliente não cadastrado nessa loja'}
            
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