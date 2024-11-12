import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from datetime import datetime
from random import randint
import json
from controler import calcular_totais_por_metodo

def gerar_pdf(dados):
    # Nome do arquivo PDF
    nome_pdf = f"relatorio_{str(randint(0, 10))}.pdf"
    pdf_path = os.path.expanduser("~/Documents/JP/relatorio")
    if not os.path.exists(pdf_path):
        os.makedirs(pdf_path)
    
    # Criando o documento
    doc = SimpleDocTemplate(os.path.join(pdf_path, nome_pdf), pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Cabeçalho
    content = []
    content.append(Paragraph(f"Relatório de Vendas: {dados['relatorio_id']}", styles['Title']))
    content.append(Paragraph(f"Data: {dados['data'].strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    content.append(Paragraph(f"Hora: {dados['hora']}", styles['Normal']))
    content.append(Paragraph(f"Cliente: {dados['cliente']}", styles['Normal']))
    content.append(Paragraph(f"Funcionário: {dados['funcionario']}", styles['Normal']))
    
    # Tabela de produtos
    data = [['ID', 'Nome', 'Preço', 'Quantidade', 'Total']]
    total_money = 0  # Inicializa o total a pagar
    
    for produto in dados['produtos']:
        total_money += produto['total']  # Soma o total de cada produto
        data.append([
            produto['id'],
            produto['nome'],
            f"MZN {produto['preco']:.2f}",
            str(produto['quantidade']),
            f"MZN {produto['total']:.2f}"
        ])
    
    # Criando a tabela
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(table)
    
    # Totais
    content.append(Paragraph(f"Total de Itens: {dados['total_item']}", styles['Normal']))
    content.append(Paragraph(f"Total a Pagar: MZN {total_money:.2f}", styles['Normal']))
    
    # Gerando o PDF
    doc.build(content)
    
    # Abrir o PDF após gerar
    os.startfile(os.path.join(pdf_path, nome_pdf))
    print(f"PDF {nome_pdf} gerado e aberto com sucesso.")

def gerar_relatorio_pdf(dados):
    """
    Esta função gera o relatório diário de vendas e o histórico de estoque.
    """
    total_por_metodo = calcular_totais_por_metodo(dados)
    
    # Nome do arquivo PDF
    nome_pdf = f"relatorio_{dados['nome']+str(randint(0,10))}.pdf"
    pdf_path = os.path.expanduser("~/Documents/JP/relatorio")
    if not os.path.exists(pdf_path):
        os.makedirs(pdf_path)
    
    # Criando o documento
    doc = SimpleDocTemplate(os.path.join(pdf_path, nome_pdf), pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Cabeçalho
    content = []
    content.append(Paragraph(f"Relatório de Vendas: {dados['nome']}", styles['Title']))
    content.append(Paragraph(f"Data: {dados['data']}", styles['Normal']))
    
    # Verificação de vendas disponíveis
    if dados['vendas']:
        content.append(Paragraph(f"Funcionário: {dados['vendas'][0]['caixa']}", styles['Normal']))
        
        # Tabela de vendas
        data_vendas = [['Horas', 'Produtos', 'Quantidade', 'Total', 'Cliente/Mesa', 'Caixa', 'Método']]
        
        for venda in dados['vendas']:
            data_vendas.append([
                str(venda['hora']),
                str(venda['produto_total']),
                venda['quantidade'],
                f"{venda['total']} MZN",
                str(venda['cliente']),
                str(venda['caixa']),
                str(venda['metodo'])
            ])
        
        # Criando a tabela de vendas
        table_vendas = Table(data_vendas)
        table_vendas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(table_vendas)
        
    else:
        content.append(Paragraph("Nenhuma venda registrada.", styles['Normal']))

   # Lista de todos os métodos de pagamento
    metodos_pagamento = [
        "Cash",
        "MPesa",
        "E-mola",
        "Paga Facil",
        "Ponto 24",
        "POS BIM",
        "POS BCI",
        "POS ABSA",
        "POS MOZA BANCO",
        "POS StanderBank",
        "M-Cash"
    ]

    # Totais de vendas
    content.append(Paragraph(' ', styles['Normal']))
    content.append(Paragraph(f"Total de Vendas: {dados.get('total_vendas', 'N/A')}", styles['Normal']))
    content.append(Paragraph(f"Total em Dinheiro: {dados.get('total', '0')} MZN", styles['Normal']))

    # Loop através dos métodos de pagamento para garantir que todos apareçam
    for metodo in metodos_pagamento:
        valor = total_por_metodo.get(metodo, '0')  # Usa '0' se não houver valor
        content.append(Paragraph(f"Pagamento Via {metodo}: {valor} MZN", styles['Normal']))

    # Tabela de histórico de estoque
    content.append(Paragraph("Histórico de Estoque:", styles['Title']))
    
    data_estoque = [['Produto', 'Estoque Inicial', 'Saída', 'Restante']]
    
    # Verifica se 'entrada' está definida e é uma lista
    entrada = dados.get('entrada', [])
    if not isinstance(entrada, list):
        entrada = json.loads(entrada)
    
    # Verifica se 'saida' está definida e é uma lista
    saida = dados.get('saida', [])
    if saida and not isinstance(saida, list):
        saida = json.loads(saida)
    
    # Gerar o dicionário de saídas por produto
    saida_dict = {s['nome']: s['quantidade_saida'] for s in saida} if saida else {}
    
    # Preenchendo a tabela com os dados de estoque
    for item in entrada:
        nome = item['nome']
        estoque_inicial = item['estoque']
        quantidade_saida = saida_dict.get(nome, 0)
        estoque_restante = estoque_inicial - quantidade_saida
        if quantidade_saida>0:
            data_estoque.append([
            nome,
            estoque_inicial,  # Estoque Inicial
            quantidade_saida,  # Saída
            estoque_restante  # Restante
        ])
    
    # Criando a tabela de estoque
    table_estoque = Table(data_estoque)
    table_estoque.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(table_estoque)
    
    # Gerando o PDF
    doc.build(content)
    
    # Abrir o PDF após gerar
    os.startfile(os.path.join(pdf_path, nome_pdf))
    print(f"PDF {nome_pdf} gerado e aberto com sucesso.")


def gerar_pdf_produtos(produtos):
    # Nome do arquivo PDF
    nome_pdf = f"lista_produtos_{randint(0, 100)}.pdf"
    pdf_path = os.path.expanduser("~/Documents/JP/relatorio")
    if not os.path.exists(pdf_path):
        os.makedirs(pdf_path)
    
    # Criando o documento
    doc = SimpleDocTemplate(os.path.join(pdf_path, nome_pdf), pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Cabeçalho
    content = []
    content.append(Paragraph("JP Invest - Produtos", styles['Title']))
    content.append(Paragraph(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    
    # Tabela de produtos
    data = [['ID', 'Nome', 'Preço', 'Estoque']]
    
    for produto in produtos:
        data.append([
            produto.id,
            produto.titulo,
            f"MZN {produto.preco:.2f}",
            produto.estoque
        ])
    
    # Criando a tabela
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(table)
    
    # Gerando o PDF
    doc.build(content)
    
    # Abrir o PDF após gerar
    os.startfile(os.path.join(pdf_path, nome_pdf))
