import json
import re

def id(word):
    return re.sub(r"[^\w]", "", word)

def json_para_dicionario(nome_arquivo):
    dicionario = {}
    with open(nome_arquivo, 'r', encoding='utf-8') as arquivo_json:
        dados = json.load(arquivo_json)
        for doente in dados:
            sintomas = doente['sintomas']
            if doente['nome'] not in dicionario.keys():
                dicionario[doente['nome']] = sintomas
            else:
                dicionario[doente['nome']].extend(sintomas)
    return dicionario

# Exemplo de uso
nome_arquivo = 'doentes.json'  # Substitua pelo nome do seu arquivo
dict_doentes = json_para_dicionario(nome_arquivo)

instances = ""
identificador = 3
for doente, sintomas in dict_doentes.items():
    instances += f"""
:{identificador} a :Patient ;
    :exhibitsSymptom {", ".join(f":{id(v)}" for v in set(sintomas) if v)} .
"""
    identificador += 1
    
print(instances)