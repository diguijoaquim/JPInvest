import sqlite3

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('C:/Users/HUAWEI/AppData/Local/.jpInvest/banco.db')
cursor = conn.cursor()

# Adicionar nova coluna à tabela
cursor.execute("ALTER TABLE produtos ADD COLUMN estoquerequired TEXT")

# Salvar as mudanças e fechar a conexão
conn.commit()
conn.close()
