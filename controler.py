import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models.modelos import Base,Produto,Usuario,ProdutoVenda,RelatorioVenda,ContasAbertas,ProdutosConta
from datetime import datetime
import re
import json
import os
from sqlalchemy import or_


info= {
    "app":"JP Invest",
    "data":{
        "nome":"JP Invest",
        "localizacao":"",
        "cidade":"Lichinga",
        "nuit":1667287375365,
        "valor":30000,
        "validade":"17-05-2020",
        "pago":True,
        "tipo":"Farmacia",
        "contacto":877136613,
        "codigo_fatura":"0786",
        "logo":"/assets/logo.png",
        "email":"admin@gmail.com"
    },
    "admin":{
        "nome":"Miguel",
        "apelido":"Araujo",
        "email":"admin@gmail.com",
        "contacto":877136613,
        "username":"admin",
        "password":"1234"
    }

}
# Verifica se está congelado (executável) ou rodando como script


# Cria a engine do SQLAlchemy
# Define o caminho do banco de dados
db_path = os.path.join(os.getenv("LOCALAPPDATA"), ".jpInvest", "banco.db")
db_directory = os.path.dirname(db_path)

# Verifica se a pasta existe e, se não, cria
if not os.path.exists(db_directory):
    os.makedirs(db_directory)


# Cria a engine do SQLAlchemy
engine = sqlalchemy.create_engine(f"sqlite:///{db_path}", echo=False)
ano=datetime.now().year
mes=datetime.now().month
date=datetime.now().day

_validade_software=info['data']['validade']

#vamos verificar se a validade so software e menor que o ano atual
def AnoValido():
    #vamos dividir a string da data
    validade_software=re.split("-",_validade_software)
    print(mes)
    print(int(validade_software[1]))


    if(ano>int(validade_software[2])):
        print("ja expirou ")
        return False
    elif(ano==int(validade_software[2]) and mes<int(validade_software[1])):
        print("vai expirar este ano")
        return True
    elif(ano==int(validade_software[2]) and mes>int(validade_software[1])):
        print("Ja espirou")
        return False
    else:
        print("Ainda Nao espirou ")
        return True

#vamos criar as tabelas dos segintes modelos,"Produto e Usuario"
def CriarTabelas():
    Base.metadata.create_all(engine) 

#criar uma sessao  db
Session=sessionmaker(bind=engine)

db=Session()
def isDataBase():
    try:
        db.query(Usuario).all()
        return True
    except:
        CriarTabelas()
        CadastrarUsuario(n=info['admin']['nome'], 
                         c="admin",
                         u=info['admin']['username'],
                         s_=info['admin']['password']
                         )
        return False
#essas funcoes podem ser importadas em quarquer class

def CadastrarUsuario(n,c,u,s_):
    novoUsuario=Usuario(nome=n,cargo=c,username=u,senha=s_)
    db.add(novoUsuario)
    db.commit()
    print(f"O usuario {n} Foi Cadastrado com sucesso")

def CadastrarProduto(titulo,barcode,categoria, preco, estoque, image):
    if titulo != "" and preco is not None and estoque != "" and image != "":
        novoProduto = Produto(titulo=titulo,barcode=barcode,categoria=categoria, preco=preco, estoque=estoque, image=image)
        db.add(novoProduto)
        db.commit()
        print(f"O Produto {titulo} foi cadastrado com sucesso")
    else:

        print("Complete todos os campos")

def AtualisarProduto(id,data):
    produto=db.query(Produto).filter_by(id=data.id).first()
    produto.titulo=data.titulo
    produto.preco=data.preco
    produto.estoque=data.estoque
    db.commit()
    print(f"O produto {data.titulo} foi atualizado com sucesso")
#funcoes para estoque

def addConta(c):
    """
    adicionar contas clente/mesa
    """
    conta=ContasAbertas(cliente=c)
    db.add(conta)
    db.commit()

def addItemConta(items,conta_id):
    """
    Adicionar produto à conta
    """
    produto = ProdutosConta(items=items,conta_id=conta_id)
    db.add(produto)
    db.commit()

def serialize(obj):
    """Converte objetos que não são serializáveis em JSON para strings."""
    if isinstance(obj, datetime):
        return obj.isoformat()  # Converte datetime para string no formato ISO 8601
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def default_serializer(obj):
    """Função para serializar objetos que não são diretamente serializáveis para JSON."""
    if isinstance(obj, datetime):
        return obj.isoformat()  # Converte datetime para string no formato ISO 8601
    raise TypeError(f"Tipo {type(obj)} não é serializável para JSON")

def ContaInfoToVenda(id=1):
    banco=sessionmaker(bind=engine)
    bb=banco()
    
    pedidos = bb.query(ProdutosConta).filter_by(conta_id=id).all()
    
    # Converte a lista de pedidos em dicionários
    pedidos_json = [pedido.__dict__ for pedido in pedidos]
    
    # Calcule os totais diretamente dos pedidos
    return pedidos_json
   


def ContaInfo(id=1):
    banco=sessionmaker(bind=engine)
    bb=banco()
    pedidos = bb.query(ProdutosConta).filter_by(conta_id=id).all()
    
    # Converte a lista de pedidos em dicionários
    pedidos_json = [pedido.__dict__ for pedido in pedidos]
    
    # Remove o campo SQLAlchemy _sa_instance_state
    for pedido in pedidos_json:
        pedido.pop('_sa_instance_state', None)
    print(pedidos)
    # Retorna a lista de pedidos diretamente para calcular os totais
    return calcular_totais(pedidos_json)  # Passa diretamente a lista de pedidos

def calcular_totais(dados):
    # Se 'dados' já for um dicionário de totais, retorne-o diretamente
    if isinstance(dados, dict) and 'total_dinheiro' in dados:
        return dados

    # Caso contrário, continuamos com a lógica padrão para calcular os totais
    total_dinheiro = 0.0
    total_produtos = 0
    total_pedidos = len(dados)  # Total de pedidos é o comprimento da lista

    for pedido in dados:
        # Para cada pedido, somamos o total de dinheiro e total de produtos
        for item in pedido['items']:
            total_dinheiro += item['total']
            total_produtos += item['quantidade']
    
    return {
        "total_dinheiro": total_dinheiro,
        "total_produtos": total_produtos,
        "total_pedidos": total_pedidos
    }


def getContas():
    try:
        contas = db.query(ContasAbertas).all() 
        return contas
    except:
        return [] 
    
def incrementarStoque(id_produto,qtd):
    produto=db.query(Produto).filter_by(id=id_produto).first()
    if(produto):
        p=produto.estoque
        produto.estoque=produto.estoque+qtd
        db.commit()
        print(f"Estoque atualizado d {p} para {produto.estoque}")
    else:
        print("O produto nao foi encontrado")
def decrementarStoque(id_produto,qtd):
    produto=db.query(Produto).filter_by(id=id_produto).first()
    if(produto):
        p=produto.estoque
        produto.estoque=produto.estoque-qtd
        db.commit()
        print(f"Estoque atualizado d {p} para {produto.estoque}")
    else:
        print("O produto nao foi encontrado")
def deduceStockCart(carrinho):
    for i in carrinho:
        #achar o produto no banco
        produto=db.query(Produto).filter_by(titulo=i['nome']).first()
        #reduzir o estoque com a funcao abaixo, para cada item
        if i['categoria']!="Servicos de lavagem":
            decrementarStoque(produto.id,i['quantidade'])

def checkCartStock(carrinho):
    #ir no banco verificar se o estoque e suficiente para a venda
    for i in carrinho:
        resultado={}
        produto=db.query(Produto).filter_by(titulo=i['nome']).first()
        #print(produto.estoque)
        #se o produto.estoque for maior que quantidade de item retorna True
        if produto.categoria=="Servicos de lavagem":
            return {"msg":"O estoque e suficiente","resultado":True}
        if produto.estoque>i['quantidade']:
            print("estoque e suficiente")
            resultado={"msg":"O estoque e suficiente","resultado":True}
        else:
            resultado={"msg":"O estoque nao e suficiente","resultado":False,"produto":i['nome']}
        return resultado

def verProdutos():
    return db.query(Produto).all()

def pegarporCategoria(categoria: str):
    return db.query(Produto).filter_by(categoria=categoria).all()

def pesquisaProduto(query):
    return db.query(Produto).filter(
    or_(
        Produto.titulo.like(f"%{query}%"),
        Produto.categoria.like(f"%{query}%")
    )
).all()
def todosUsers():
    return db.query(Usuario).all()
def verCaixa():
    return db.query(Usuario).filter_by(cargo="Caixa").all()
def acharUmProduto(id):
    return db.query(Produto).filter_by(id=id).first()

def acharUmProduto_barcode(barcode):
    return db.query(Produto).filter_by(barcode=barcode).first()
    
def deletarProduto(id):
    p=db.query(Produto).filter_by(id=id).first()
    db.delete(p)
    db.commit()
    print(f"O produto {p.titulo} foi deletado com sucesso!")

def addVenda(venda):
    db.add(venda)
    db.commit()
    print("Venda Feita")

def verVendas():
    return db.query(ProdutoVenda).all()

def addRelatorio(day,entrada):

    relatorio=RelatorioVenda(nome=f"relatorio{day}",data=day,caixa="admin",entrada=entrada)
    db.add(relatorio)
    db.commit()
    print("Relatorio Cadastrado")

def RemoveRelatorio(day):
    relatorio=db.query(RelatorioVenda).filter_by(data=day).first()
    db.delete(relatorio)
    db.commit()
    print("Relatorio Deletado")


def getRelatorios():
    return db.query(RelatorioVenda).all()

def getRelatorioUnico(day):
    return db.query(RelatorioVenda).filter_by(data=day).first()

def getRelatorioUnicoByID(id):
    return db.query(RelatorioVenda).filter_by(id=id).first()

def totalRelatorioMoney(day):
    total=0.00
    for v in getRelatorioUnico(day).vendas:
        total+=v.total_money  
    return total
def deletarRelatorio(id):
    p=db.query(RelatorioVenda).filter_by(id=id).first()
    db.delete(p)
    db.commit()

def deletarVendas(id):
    p=db.query(ProdutoVenda).filter_by(id=id).first()
    db.delete(p)
    db.commit()

def totalVendaMoney(id):
    produto=db.query(ProdutoVenda).filter_by(id=id).first()
    total=0.00
    for i in produto.produtos:
        total+=i['total']   
    return total

def totalVendaMoneyRelatorio(day):
    relatorio=db.query(RelatorioVenda).filter_by(data=day).first()
    total=0.00
    for venda in relatorio.vendas:
        total+=totalVendaMoney(venda.id)
    money=f"{total:,.2f}".replace(",", " ").replace(".", ",")
    return money

def totalVendaProdutos(id):
    produto=db.query(ProdutoVenda).filter_by(id=id).first()
    total=0
    for i in produto.produtos:
        total+=1   
    return total

def getTotalMoneyCart(carrinho):
    total=0.00
    for i in carrinho:
        total+=i['total']
    return total


def getTotalTipoCart(carinho):
    tipo=0
    for i in carinho:
        tipo+=1
    return tipo

def getTotalQuantCart(carrinho):
    quant=0
    for i in carrinho:
        quant+=i["quantidade"]
    return quant

def itensListsimple(id):
    venda=db.query(ProdutoVenda).filter_by(id=id).first()
    
    produtos=[]
    for i in venda.produtos:
        produtos.append(f"{i['nome']}-{i['quantidade']}")
    novas_string=", ".join(produtos)
    return novas_string
def formatToMoney(data):
    money=f"{data:,.2f}".replace(",", " ").replace(".", ",")
    return money
def getOneSale(id):
    return db.query(ProdutoVenda).filter_by(id=id).first(

    )
def StartLogin(username,senha):
    user=db.query(Usuario).filter_by(username=username,senha=senha).first()
    if user != None:

        return user
    else:
        return False
    

def loged():
    return ''
def changePassword(user,nova):
    user.senha=nova
    db.commit()
    print("senha foi modificada com sucesso")
def getFuncionarios():
    funcionarios=db.query(Usuario).all()
    return funcionarios

def excluir_funcionario(id):
    funcionario=db.query(Usuario).filter_by(id=id).first()
    db.delete(funcionario)
    print(funcionario)
    db.commit()
def userUpdate(data):
    user=loged()
    can=False
    if data['nome'] != "":
        user.nome=data['nome']
        can=True
    if data['apelido'] != "":    
        user.apelido=data['apelido']
        can=True
    if data['telefone'] != "":
        user.telefone=data["telefone"]
        can=True
    if data['email'] != "":
        user.email=data['email']
        can=True
    if data['username'] != "":
        user.username=data['username']
        can=True
    if can:
        db.commit()
        print("dados atualizados")
    else:
        print("Formaulario esta")


def formatar_dados(dados):
    import json

    # Verifica se 'dados' é uma string e precisa ser convertido
    if isinstance(dados, str):
        print(dados)
        dados = json.loads(dados)

    
    # Cria uma lista para armazenar as linhas da string de retorno
    linhas = []
    
    # Adiciona os dados formatados à lista
    linhas.append("-------RESTAURANTE MUTXUTXU------")
    linhas.append(f"Data: ")
    linhas.append("--------------------------")
    linhas.append("Produtos:")
    
    for produto in dados['produtos']:
        linhas.append(f"  Nome: {produto['nome']}")
        linhas.append(f"  Preço: {produto['preco']:.2f} MT")
        linhas.append(f"  Quantidade: {produto['quantidade']}")
        linhas.append("--------------------------")
        
    linhas.append(f"Subtotal: {dados['subtotal']:.2f} MT")
    linhas.append(f"IVA: {dados['iva']:.2f} MT")
    linhas.append(f"Total: {dados['total']:.2f} MT")
    linhas.append("-------by--gulamo--devs-------")
    
    # Junta todas as linhas em uma única string
    return "\n".join(linhas)
def calcular_totais_por_metodo(relatorio):
    # Inicializar um dicionário para armazenar o total por método de pagamento
    totais_por_metodo = {
        'Cash': 0.0,
        'MPesa': 0.0,
        'E-mola': 0.0,
        'Izi': 0.0,
        'Paga Facil': 0.0,
        'Ponto 24': 0.0,
        'POS BIM': 0.0,
        'POS BCI': 0.0,
        'POS ABSA': 0.0,
        'POS MOZA BANCO': 0.0,
        'POS StanderBank': 0.0,
        'M-Cash': 0.0
    }
    
    # Iterar sobre as vendas no relatório
    for venda in relatorio['vendas']:
        metodo = venda['metodo']
        total = float(venda['total'].replace(',', '.'))  # Converter o total para numérico
        
        # Somar o total para o método de pagamento existente
        if metodo in totais_por_metodo:
            totais_por_metodo[metodo] += total
        else:
            totais_por_metodo[metodo] = total  # Adiciona novos métodos, caso apareçam
    
    return totais_por_metodo
