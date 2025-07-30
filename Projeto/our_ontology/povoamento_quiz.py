import requests
import re
from rdflib import Graph, Namespace, URIRef, RDF, OWL, Literal


# prepare the SPARQL endpoint and headers
endpoint_url = "https://query.wikidata.org/sparql"

headers = {
    "Accept": "application/sparql-results+json"
}

# prepare the namespace and graph
n = Namespace("http://www.semanticweb.org/marta/ontologies/2025/geografia#")
g = Graph()
g.parse("geo_base.ttl")



# --------------------------------------------------------------------
#------------------- Continentes, Países e Capitais ------------------
# --------------------------------------------------------------------

continentes = {}
paises = {}
capitais = {}

#prepare id verification
def is_id(value):
    return re.match(r'^Q\d+$', value) is not None

query_locais = """
SELECT ?pais ?paisLabel ?capital ?capitalLabel ?continente ?continenteLabel
WHERE {
  ?pais wdt:P31 wd:Q6256.             # País
  ?pais wdt:P36 ?capital.             # Capital
  ?pais wdt:P30 ?continente.          # Continente

  SERVICE wikibase:label { bd:serviceParam wikibase:language "pt". }
}
"""

response = requests.get(endpoint_url, params={'query': query_locais}, headers=headers)
data = response.json()

for item in data["results"]["bindings"]:
    id_pais = item["pais"]["value"]
    id_capital = item["capital"]["value"]
    id_continente = item["continente"]["value"]
    pais = item["paisLabel"]["value"]
    capital = item["capitalLabel"]["value"]
    continente = item["continenteLabel"]["value"]

    if id_pais not in paises:
        paisURI = URIRef(f"{n}Pais_{len(paises)}")
        paises[id_pais] = paisURI
        g.add((paisURI, RDF.type, OWL.NamedIndividual))
        g.add((paisURI, RDF.type, n.País))
        g.add((paisURI, RDF.type, n.DivisãoTerritorial))
        g.add((paisURI, n.nome, Literal(pais)))

        if continente not in continentes:
            continenteURI = URIRef(f"{n}Continente_{len(continentes)}")
            continentes[continente] = continenteURI
            g.add((continenteURI, RDF.type, OWL.NamedIndividual))
            g.add((continenteURI, RDF.type, n.Continente))
            g.add((continenteURI, RDF.type, n.DivisãoTerritorial))
            g.add((continenteURI, n.nome, Literal(continente)))
        else:
            continenteURI = continentes[continente]

        if id_capital not in capitais:
            if is_id(capital):
                #print(capital)
                query_aux = f"""
                SELECT ?itemLabel WHERE {{
                    VALUES ?item {{wd:{capital}}}
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                }}
                """
                response = requests.get(endpoint_url, params={'query': query_aux}, headers=headers)
                #print(response)
                data = response.json()
                capital = data["results"]["bindings"][0]["itemLabel"]["value"]

            capitalURI = URIRef(f"{n}Capital_{len(capitais)}")
            capitais[id_capital] = capitalURI
            g.add((capitalURI, RDF.type, OWL.NamedIndividual))
            g.add((capitalURI, RDF.type, n.Capital))
            g.add((capitalURI, RDF.type, n.Cidade))
            g.add((capitalURI, RDF.type, n.DivisãoTerritorial))
            g.add((capitalURI, n.nome, Literal(capital)))
        else:
            capitalURI = capitais[id_capital]
    
        g.add((paisURI, n.temComoCapital, capitalURI))
        g.add((paisURI, n.localizadoEm, continenteURI))
        g.add((capitalURI, n.éCapitalDe, paisURI))
        g.add((capitalURI, n.localizadoEm, paisURI))
        g.add((continenteURI, n.temPaís, paisURI))
        g.add((paisURI, n.temCidade, capitalURI))


# --------------------------------------------------------------------
#--------------------- Fronteiras Terrestres -------------------------
# --------------------------------------------------------------------


query_fronteiras_terrestres = """
SELECT ?pais1 ?pais2 WHERE {
  ?pais1 wdt:P47 ?pais2. # faz fronteira com
  ?pais1 wdt:P31 wd:Q6256.
  ?pais2 wdt:P31 wd:Q6256.
}
"""

response = requests.get(endpoint_url, params={'query': query_fronteiras_terrestres}, headers=headers)
data = response.json()

for item in data["results"]["bindings"]:
    pais1 = item["pais1"]["value"]
    pais2 = item["pais2"]["value"]

    if pais1 not in paises or pais2 not in paises:
        continue  # Skip if the country is not in our data

    pais1URI = paises[pais1]
    pais2URI = paises[pais2]

    g.add((pais1URI, n.fazFronteiraCom, pais2URI))
    g.add((pais2URI, n.fazFronteiraCom, pais1URI))


# --------------------------------------------------------------------
#-------------------------- Oceanos e Mares --------------------------
# --------------------------------------------------------------------

oceanos = {}
mares = {}

def add_mar(id_mar, mar, area):
    if id_mar not in mares:
        marURI = URIRef(f"{n}Mar_{len(mares)}")
        mares[id_mar] = marURI
        g.add((marURI, RDF.type, OWL.NamedIndividual))
        g.add((marURI, RDF.type, n.Mar))
        g.add((marURI, RDF.type, n.CorpoDeÁgua))
        g.add((marURI, RDF.type, n.CorpoDeÁguaSalgada))
        g.add((marURI, n.nome, Literal(mar)))
        if area:
            g.add((marURI, n.área, Literal(area)))
    else:
        marURI = mares[id_mar]
    return marURI


query_oceanos = """
SELECT ?oceano ?oceanoLabel WHERE {
  ?oceano wdt:P31 wd:Q9430. # instância de oceano
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "pt".
  }
}
LIMIT 5
"""

response = requests.get(endpoint_url, params={'query': query_oceanos}, headers=headers)
data = response.json()

for item in data["results"]["bindings"]:
    id_oceano = item["oceano"]["value"]
    oceano = item["oceanoLabel"]["value"]

    if id_oceano not in oceanos:
        oceanoURI = URIRef(f"{n}Oceano_{len(oceanos)}")
        oceanos[id_oceano] = oceanoURI
        g.add((oceanoURI, RDF.type, OWL.NamedIndividual))
        g.add((oceanoURI, RDF.type, n.Oceano))
        g.add((oceanoURI, RDF.type, n.CorpoDeÁguaSalgada))
        g.add((oceanoURI, RDF.type, n.CorpoDeÁgua))
        g.add((oceanoURI, n.nome, Literal(oceano)))


# --------------------------------------------------------------------
#-------------------- Fronteiras entre terra e mar -------------------
# --------------------------------------------------------------------


query_fronteiras_oceano = """
SELECT ?pais ?oceano WHERE {
  ?pais wdt:P31 wd:Q6256.
  ?pais wdt:P206 ?oceano.
  ?oceano wdt:P31 wd:Q9430.
}
"""

response = requests.get(endpoint_url, params={'query': query_fronteiras_oceano}, headers=headers)
data = response.json()

for item in data["results"]["bindings"]:
    id_pais = item["pais"]["value"]
    id_oceano = item["oceano"]["value"]

    if id_pais not in paises or id_oceano not in oceanos:
        continue  # Skip if the country or ocean is not in our data

    paisURI = paises[id_pais]
    oceanoURI = oceanos[id_oceano]

    g.add((paisURI, n.fazFronteiraCom, oceanoURI))
    g.add((oceanoURI, n.fazFronteiraCom, paisURI))


query_fronteiras_mar = """
SELECT ?pais ?mar ?marLabel WHERE {
  ?pais wdt:P31 wd:Q6256.         # instância de país
  ?pais wdt:P206 ?mar.           # faz fronteira com corpo de água
  ?mar wdt:P31 wd:Q165.

  ?mar rdfs:label ?marLabel.
  FILTER(LANG(?marLabel) = "pt")
}
"""
response = requests.get(endpoint_url, params={'query': query_fronteiras_mar}, headers=headers)
data = response.json()

for item in data["results"]["bindings"]:
    id_pais = item["pais"]["value"]
    id_mar = item["mar"]["value"]
    mar = item["marLabel"]["value"]

    if id_pais not in paises:
        continue  # Skip if the country or sea is not in our data

    paisURI = paises[id_pais]

    marURI = add_mar(id_mar, mar, None)

    g.add((paisURI, n.fazFronteiraCom, marURI))
    g.add((marURI, n.fazFronteiraCom, paisURI))


# --------------------------------------------------------------------
# ---------------------------- Rios ----------------------------------
# --------------------------------------------------------------------

rios_ids = {}
rios = {}
desagua_ids = {}

query_rios = """
SELECT ?rio ?rioLabel ?pais ?desagua ?desaguaLabel WHERE {
  ?rio wdt:P31 wd:Q4022.
  ?rio wdt:P17 ?pais.
  ?rio wdt:P403 ?desagua.

  ?rio rdfs:label ?rioLabel.
  FILTER(LANG(?rioLabel) = "pt")

  ?pais rdfs:label ?paisLabel.
  FILTER(LANG(?paisLabel) = "pt")

  ?desagua rdfs:label ?desaguaLabel.
  FILTER(LANG(?desaguaLabel) = "pt")
}
"""

response = requests.get(endpoint_url, params={'query': query_rios}, headers=headers)
data = response.json()


for item in data["results"]["bindings"]:
    id_rio = item["rio"]["value"]
    if id_rio not in rios_ids:
        rioURI = URIRef(f"{n}Rio_{len(rios_ids)}")
        rios_ids[id_rio] = rioURI

for item in data["results"]["bindings"]:
    id_rio = item["rio"]["value"]
    rio = item["rioLabel"]["value"]
    id_pais = item["pais"]["value"]
    id_desagua = item["desagua"]["value"]
    desagua = item["desaguaLabel"]["value"]
    

    if id_pais not in paises:
        continue  # Skip if the river's country or mouth is not in our data

    paisURI = paises[id_pais]

    if id_desagua in oceanos:
        desaguaURI = oceanos[id_desagua]
    elif id_desagua in mares:
        desaguaURI = mares[id_desagua]
    elif id_desagua in rios_ids:
        desaguaURI = rios_ids[id_desagua]
    else:
        desaguaURI = URIRef(f"{n}Desagua_{len(desagua_ids)}")
        desagua_ids[id_desagua] = desaguaURI
        g.add((desaguaURI, RDF.type, OWL.NamedIndividual))
        g.add((desaguaURI, RDF.type, n.CorpoDeÁgua))
        g.add((desaguaURI, n.nome, Literal(desagua)))


    if id_rio not in rios:
        rioURI = rios_ids[id_rio]
        rios[id_rio] = rioURI
        g.add((rioURI, RDF.type, OWL.NamedIndividual))
        g.add((rioURI, RDF.type, n.Rio))
        g.add((rioURI, RDF.type, n.CorpoDeÁgua))
        g.add((rioURI, RDF.type, n.CorpoDeÁguaDoce))
        g.add((rioURI, n.nome, Literal(rio)))
    else:
        rioURI = rios[id_rio]

    g.add((rioURI, n.passaPor, paisURI))
    g.add((rioURI, n.desaguaEm, desaguaURI))
    g.add((paisURI, n.atravessadoPor, rioURI))
    g.add((desaguaURI, n.recebeRio, rioURI))


# --------------------------------------------------------------------
# ------------------------- Serialização -----------------------------
# --------------------------------------------------------------------

rm = [n.área, n.comprimento, n.população, n.éParteDe, n.temMar]

for s, p, o in list(g):
    if s in rm or p in rm:
        g.remove((s, p, o))
    
final_ttl = g.serialize(format="turtle")
open("geografia_quiz.ttl", "w").write(final_ttl)