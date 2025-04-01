import csv
import re

def id(word):
    return re.sub(r"[^\w]", "", word)

def csv_para_dicionario(nome_arquivo):
    dicionario = {}
    sintomas = []
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
                sintomas.extend(valores)
    return dicionario, sintomas

# Exemplo de uso
nome_arquivo = 'Disease_Syntoms.csv'  # Substitua pelo nome do seu arquivo
dict_doencas, sintomas = csv_para_dicionario(nome_arquivo)

sint = set(sintomas) 

instances = ""
for doenca, sintomas in dict_doencas.items():
    instances += f"""
:{id(doenca)} a :Disease ;
    :hasSymptom {", ".join(f":{id(v)}" for v in set(sintomas) if v)} .
"""
    
for sintoma in sint:
    if sintoma:
        instances += f"""
    :{id(sintoma)} a :Symptom .
    """
    
print(instances)