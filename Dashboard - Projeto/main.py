from models import BancoDeDados


db = BancoDeDados()

db.inserir_transacao("receitas", "Salário", 2500.00, "2025.05.20", "Salário Mensal")

transacoes = db.listar_transacoes()
for t in transacoes:
    print (t)
    db.fechar()