import csv
import re

def id(word):
    return re.sub(r"[^\w]", "", word)

def csv_para_dicionario(nome_arquivo):
    dicionario = {}
    tratamentos = []
    with open(nome_arquivo, newline='', encoding='utf-8') as csvfile:
        leitor = csv.reader(csvfile)
        next(leitor)  # Ignora o cabeçalho
        for linha in leitor:
            if linha:  # Garante que a linha não está vazia
                chave = linha[0]
                valores = linha[1:]  # Cria um conjunto com os elementos restantes
                if chave not in dicionario.keys():
                    dicionario[chave] = valores
                else:
                    dicionario[chave].extend(valores)
                tratamentos.extend(valores)
    return dicionario, tratamentos

# Exemplo de uso
nome_arquivo = 'Disease_Treatment.csv'  # Substitua pelo nome do seu arquivo
dict_doencas, tratamentos = csv_para_dicionario(nome_arquivo)

trat = set(tratamentos) 

instances = ""
for doenca, tratamentos in dict_doencas.items():
    instances += f"""
:{id(doenca)} a :Disease ;
    :hasTreatment {", ".join(f":{id(v)}" for v in set(tratamentos) if v)} .
"""
    
for t in trat:
    if t:
        instances += f"""
    :{id(t)} a :Treatment .
    """
    
print(instances)