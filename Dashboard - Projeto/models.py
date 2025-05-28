import sqlite3
import os

class BancoDeDados:
    def __init__(self, nome_banco="dashboard.db"):
        self.conn = sqlite3.connect(nome_banco)
        self.criar_tabela()
        
    def criar_tabela(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                valor REAL NOT NULL,
                data TEXT NOT NULL,
                descricao TEXT
            )
        """)
        self.conn.commit()

    def inserir_transacao(self, tipo, categoria, valor, data, descricao=""):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transacoes (tipo, categoria, valor, data, descricao)
            VALUES (?, ?, ?, ?, ?)
        """, (tipo, categoria, valor, data, descricao))
        self.conn.commit()

    def listar_transacoes(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM transacoes ORDER BY data DESC")
        return cursor.fetchall()
    
    def fechar(self):
        self.conn.close()

    def totais_por_categoria(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT categoria, SUM(valor) 
        FROM transacoes 
        GROUP BY categoria
    """)
        return cursor.fetchall()
