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
            user = self.database.run(sql, dict_cursor = True, disconnect=False)[0]

        except Exception as error:
            self.database.disconnect()
            print(error)
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
        
    def searchCpf(self, data:dict):
        id = data['id']
        cpf = data['cpf']

        sql = f'SELECT * FROM clientes WHERE cpf = {cpf}'
        try:
            cliente = self.database.run(sql, True, disconnect=False)[0]
        except:
            self.database.disconnect()
            return {'error': 'Cliente não cadastrado.', 'error_code': 1}
            
        sql = f'SELECT * FROM parceiro_{id} WHERE id_cliente = {cliente["id"]}'
        print(sql)
        try:
            response = self.database.run(sql, True)[0]
            print(response)
            cliente.update({'cupons': response["cupons"]})
            return cliente
        except:
            self.database.disconnect()
            cliente.update({'error': 'Cliente não cadastrado nessa loja', 'error_code': 2})
            return cliente

    def signupClient(self, data):
        # check if client is already signed
        sql = f"SELECT * FROM clientes WHERE cpf = {data['cliente']['input_cpf']};"
        try:
            cliente = self.database.run(sql, True, disconnect=False)[0]

            sql = f"""UPDATE clientes SET 
            telefone= '{data['cliente']['input_telefone']}', 
            email= '{data['cliente']['input_email']}', 
            {f"senha= '{data['cliente']['input_senha']}'," if data['cliente']['input_senha'] else ''} 
            
                """
            print(sql)
            self.database.run(sql, disconnect=False)
            
        # signup new client
        except Exception as error:
            print(error)
            # getting new client id
            sql = f'SELECT * FROM clientes'
            id = len(self.database.run(sql, disconnect=False))

            # inserting client into general CLIENTES tançe
            sql = f"""INSERT INTO clientes
                (id, nome, cpf, telefone, senha, email, lojas) 
                VALUES ({id}, '{data['cliente']['input_nome']}', '{data['cliente']['input_cpf']}', '{data['cliente']['input_telefone']}', 
                '{data['cliente']['input_senha']}', '{data['cliente']['input_email']}', '[{data['id_parceiro']}]');
            """
            print(sql)
            self.database.run(sql, disconnect=False)

        finally:
            # getting new client id on current store
            sql = f'SELECT * FROM parceiro_{data["id_parceiro"]};'
            id2 = len(self.database.run(sql, disconnect=False))

            # inserting client into current store
            sql = f"""INSERT INTO parceiro_{data['id_parceiro']}
                (id, id_cliente, cupons) VALUES ({id2}, {id}, 0);
            """
            self.database.run(sql, disconnect=False)
            
            # getting standardized client
            cliente = self.searchCpf({'id': data['id_parceiro'], 'cpf': data['cliente']['input_cpf']})
            
            return cliente

            
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