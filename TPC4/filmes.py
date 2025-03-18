import json
import requests
from query import query_graphdb

our_movies = []
with open("filmes_wanted.json", "r") as f:
    our_movies = json.load(f)

endpoint = "https://dbpedia.org/sparql"

filmes = []
atores = []

for m in our_movies:

    filmes_query = f"""
    select distinct ?title ?abs ?r ?c where {{
        <{m}> dbp:name ?title .
        optional {{
            <{m}> dbo:abstract ?abs .
            <{m}> dbo:director ?r .
            <{m}> dbo:country ?c . 
        }}         
    }}
    """
    filmes_info = query_graphdb(endpoint, filmes_query)

    atores_filme_query = f"""
    select ?a where {{
        <{m}> dbo:starring ?a .
    }} LIMIT 5
    """
    atores_filme_info = query_graphdb(endpoint, atores_filme_query)

    if atores_filme_info['results']['bindings']:

        elenco = []
        for a in atores_filme_info['results']['bindings']:
            a=a['a']['value']
            #Se não existir o ator no dataset de atores, adiciona-se
            if not any(at['id'] == a for at in atores):
                atores_query = f"""
                select ?nome ?dn ?origem where {{
                    optional{{
                        <{a}> dbp:name ?nome .
                        <{a}> dbo:birthDate ?dn .
                        <{a}> dbp:birthPlace ?origem .
                    }}
                }}
                """
                atores_info = query_graphdb(endpoint, atores_query)
                if atores_info['results']['bindings']:
                    atores.append(
                        {
                            "id": a,
                            "nome": atores_info['results']['bindings'][0]['nome']['value'] if 'nome' in atores_info['results']['bindings'][0] else None,
                            "origem": atores_info['results']['bindings'][0]['origem']['value'] if 'origem' in atores_info['results']['bindings'][0] else None,
                            "dataNascimento": atores_info['results']['bindings'][0]['dn']['value'] if 'dn' in atores_info['results']['bindings'][0] else None
                        }
                    )
                else:
                    atores.append(
                        {
                            "id": a
                        }
                    )
            elenco.append(a)
        if not filmes_info['results']['bindings']:
            filmes.append(
                {
                    "id": m
                }
            )
        else:
            filmes.append(
                {
                    "id": m,
                    "título": filmes_info['results']['bindings'][0]['title']['value'] if 'title' in filmes_info['results']['bindings'][0] else None,
                    "realizador": filmes_info['results']['bindings'][0]['r']['value'] if 'r' in filmes_info['results']['bindings'][0] else None,
                    "descrição": filmes_info['results']['bindings'][0]['abs']['value'] if 'abs' in filmes_info['results']['bindings'][0] else None,
                    "país": filmes_info['results']['bindings'][0]['c']['value'] if 'c' in filmes_info['results']['bindings'][0] else None,
                    "elenco": elenco,
                }
            )

with open("filmes.json", "w") as fout:
    json.dump(filmes, fout, indent=4, ensure_ascii=False)

with open("atores.json", "w") as fout:
    json.dump(atores, fout, indent=4, ensure_ascii=False)