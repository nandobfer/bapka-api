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
            self.database.connect()
            user = self.database.run(sql, dict_cursor = True)[0]

        except Exception as error:
            self.database.disconnect()
            print(error)
            return {'error': 'Usuário não encontrado'}
        
        if data['password'] == user['senha']:
            user.update({'error': None})
            history = self.getHistory(user_id=user['id'], user_type=history_type, quantity=3)
            user.update({'historico': history})
            self.database.disconnect()
            return user
        else:
            self.database.disconnect()
            return {'error': 'Senha inválida'}
        
    def getHistory(self, user_id:int, user_type:str, quantity = 0, disconnect=True):
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
           
        if data: 
            data[-1].update({'last': True})
            
        print(data)
        return data
        
    def searchCpf(self, data:dict, request = False):
        id = data['id']
        cpf = data['cpf']
        
        if request:
            self.database.connect()

        sql = f'SELECT * FROM clientes WHERE cpf = {cpf}'
        try:
            cliente = self.database.run(sql, True)[0]
        except:
            if request:
                self.database.disconnect()
            return {'error': 'Cliente não cadastrado.', 'error_code': 1}
            
        sql = f'SELECT * FROM parceiro_{id} WHERE id_cliente = {cliente["id"]}'
        print(sql)
        try:
            response = self.database.run(sql, True)[0]
            print(response)
            cliente.update({'cupons': response["cupons"]})

            history = self.getHistory(user_id=cliente['id'], user_type='parceiro', quantity=3)
            cliente.update({'historico': history})
            
            if request:
                self.database.disconnect()
            return cliente
        except:
            if request:
                self.database.disconnect()
            cliente.update({'error': 'Cliente não cadastrado nessa loja', 'error_code': 2})
            return cliente

    def signupClient(self, data):
        # check if client is already signed
        sql = f"SELECT * FROM clientes WHERE cpf = {data['cliente']['input_cpf']};"
        try:
            self.database.connect()
            cliente = self.database.run(sql, True)[0]

            sql = f"""UPDATE clientes SET 
            telefone= '{data['cliente']['input_telefone']}', 
            email= '{data['cliente']['input_email']}', 
            {f"senha= '{data['cliente']['input_senha']}'," if data['cliente']['input_senha'] else ''} 
            
                """
            print(sql)
            self.database.run(sql)
            
        # signup new client
        except Exception as error:
            print(error)
            # getting new client id
            sql = f'SELECT * FROM clientes'
            id = len(self.database.run(sql))

            # inserting client into general CLIENTES tançe
            sql = f"""INSERT INTO clientes
                (id, nome, cpf, telefone, senha, email) 
                VALUES ({id}, '{data['cliente']['input_nome']}', '{data['cliente']['input_cpf']}', '{data['cliente']['input_telefone']}', 
                '{data['cliente']['input_senha']}', '{data['cliente']['input_email']}');
            """
            print(sql)
            self.database.run(sql)

        finally:
            # getting new client id on current store
            sql = f'SELECT * FROM parceiro_{data["id_parceiro"]};'
            id2 = len(self.database.run(sql))

            # inserting client into current store
            sql = f"""INSERT INTO parceiro_{data['id_parceiro']}
                (id, id_cliente, cupons) VALUES ({id2}, {id}, 0);
            """
            self.database.run(sql)
            
            # getting standardized client
            cliente = self.searchCpf({'id': data['id_parceiro'], 'cpf': data['cliente']['input_cpf']})
            
            self.database.disconnect()
            return cliente
        
    def modifyCoupons(self, data):
        # add coupon into current store db
        sql = f"""UPDATE parceiro_{data['id_parceiro']} 
                SET cupons = {data['total']}
                WHERE id_cliente = {data['id_cliente']};
        """
        print(sql)
        self.database.connect()
        self.database.run(sql)
        
        # log the modification
        sql = f"""INSERT INTO historicos
        (id, id_parceiro, nome_parceiro, id_cliente, nome_cliente
        data, hora, quantidade, pedido)
        """
        
        cliente = self.searchCpf({'id': data['id_parceiro'], 'cpf': data['cpf']})

        self.database.disconnect()
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