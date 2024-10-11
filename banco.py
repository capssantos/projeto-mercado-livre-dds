import psycopg2
from psycopg2.extras import DictCursor

class PostgreSQLConnection:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'cursor_factory': DictCursor
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.conn_params)
            print("Connected to PostgreSQL")
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from PostgreSQL")

    def create_table(self, table_name, table_schema, sequece_name):
        with self.connection:
            with self.connection.cursor() as cursor:
                try:
                    cursor.execute(f'DROP TABLE IF EXISTS {table_name};')
                    cursor.execute(f'DROP SEQUENCE IF EXISTS {sequece_name} CASCADE;')
                    cursor.execute(table_schema)
                    print(f'Table {table_name} created successfully')
                except psycopg2.Error as e:
                    print(f'Error creating table {table_name}: {e}')

    def create_sequence(self, table_name, sequence_schema):
        with self.connection:
            with self.connection.cursor() as cursor:
                try:
                    cursor.execute(sequence_schema)
                    print(f'Sequence {table_name} created successfully')
                except psycopg2.Error as e:
                    print(f'Error creating Sequence {table_name}: {e}')

    def execute_query(self, sql, values='', operacao=False):
        try:
            with self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute(sql, values)
                    print("Query executed successfully")
                    if 'SELECT' in sql and not operacao:
                        return cursor.fetchall()
                    else:
                        return cursor.fetchone() 
        except psycopg2.Error as e:
            print(f"Error executing query: {e}")
            return None
        
class DBConfig:
    def __init__(self, connection) -> None:
        self.connection = connection

    def create_tables(self):
        self.connection.connect()
        self.create_table_produtos()
        self.connection.disconnect()

    def create_table_produtos(self):
        table_schema = '''
            CREATE TABLE IF NOT EXISTS PRODUTOS(
                ID_PRODUTO SERIAL PRIMARY KEY NOT NULL,
                EMPRESA VARCHAR(255) NOT NULL,
                NOME VARCHAR(255) NOT NULL,
                PRECO FLOAT NOT NULL,
                IMAGEM TEXT NOT NULL,
                URL TEXT NOT NULL,
                CREATED_AT TIMESTAMP DEFAULT NOW(),
                HABILITADO BOOLEAN DEFAULT TRUE
            )
        '''
        sequence_schema = '''
            CREATE SEQUENCE PRODUTOS_SEQUENCE
            START 1000
            INCREMENT 1
            MINVALUE 1000
            OWNED BY PRODUTOS.ID_PRODUTO;
        '''
        self.connection.create_table('PRODUTOS', table_schema, 'PRODUTOS_SEQUENCE')
        self.connection.create_sequence('PRODUTOS', sequence_schema)

class Produto:
    def __init__(self, connection) -> None:
        self.connection = connection

    def insert_produto(self, empresa, nome, preco, imagem, url):
        sql = '''
            INSERT INTO PRODUTOS (ID_PRODUTO, EMPRESA, NOME, PRECO, IMAGEM, URL)
            VALUES (NEXTVAL('PRODUTOS_SEQUENCE'), %s, %s, %s, %s, %s)
            RETURNING *;
        '''
        values = (empresa, nome, preco, imagem, url)
        self.connection.connect()
        produto = self.connection.execute_query(sql, values)
        self.connection.disconnect()
        return {'data': dict(produto) if produto else None}

    def update_produto(self, id_produto, **kwargs):
        set_values = ', '.join([f"{key} = %s" for key in kwargs.keys()])
        values = tuple(kwargs.values()) + (id_produto,)
        sql = f'''
            UPDATE PRODUTOS
            SET {set_values}
            WHERE ID_PRODUTOS = %s
            RETURNING *;
        '''
        self.connection.connect()
        produto = self.connection.execute_query(sql, values)
        self.connection.disconnect()

        return {'data': dict(produto) if produto else None}

    def produtos(self, where=None, values=''):
        sql = 'SELECT * FROM PRODUTOS'
        if where:
            sql += where
        self.connection.connect()
        produtos = self.connection.execute_query(sql, values)
        
        self.connection.disconnect()
        return {'data': [[index, dict(produto)] if produto else None for index, produto in enumerate(produtos, start=1)]}
   