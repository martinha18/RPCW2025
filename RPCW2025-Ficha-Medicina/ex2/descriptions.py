import csv
import re

def id(word):
    return re.sub(r"[^\w]", "", word)

def csv_para_dicionario(nome_arquivo):
    dicionario = {}
    with open(nome_arquivo, newline='', encoding='utf-8') as csvfile:
        leitor = csv.reader(csvfile)
        next(leitor)
        for linha in leitor:
            if linha:  # Garante que a linha não está vazia
                chave = linha[0]
                valores = linha[1]  # Cria um conjunto com os elementos restantes
                if chave not in dicionario.keys():
                    dicionario[chave] = valores
    return dicionario

# Exemplo de uso
nome_arquivo = 'Disease_Description.csv'  # Substitua pelo nome do seu arquivo
dict = csv_para_dicionario(nome_arquivo)

instances = ":description a owl:DatatypeProperty ."
for doenca, desc in dict.items():
    desc = desc.replace('"', '\\"')  # Escapa aspas duplas
    instances += f"""
:{id(doenca)} :description "{desc}" .
"""
    
print(instances)