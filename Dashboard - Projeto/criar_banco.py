import sqlite3

# Cria (ou abre) o banco de dados chamado 'dashboard.db'
conn = sqlite3.connect('dashboard.db')

# Cria um cursor para executar comandos SQL
cursor = conn.cursor()

# Cria uma tabela chamada 'gastos' se ela ainda não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS gastos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT NOT NULL,
    valor REAL NOT NULL,
    data TEXT NOT NULL
)
''')

# Salva e fecha a conexão
conn.commit()
conn.close()

print("Banco de dados criado com sucesso!")
