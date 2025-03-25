import json
import re

def id(word):
    return re.sub(r"[^\w]", "", word)

with open('movies.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)


output = "" 


for g in dataset["allgénero"]:
    output += f"""
        ###  http://www.semanticweb.org/marta/ontologies/2025/cinema#{g}
        :{g} rdf:type owl:NamedIndividual ,
                :Género .
        """

for l in dataset["allLanguages"]:
    output += f"""
        ###  http://www.semanticweb.org/marta/ontologies/2025/cinema#{l}
        :{l} rdf:type owl:NamedIndividual ,
                 :Língua .
        """ 

for c in dataset["allCountries"]:
    output += f"""
        ###  http://www.semanticweb.org/marta/ontologies/2025/cinema#{c}
        :{c} rdf:type owl:NamedIndividual ,
                   :País .
        """ 

for i, p in dataset["allPeople"].items():
    nome = id(p)
    output += f"""
        ###  http://www.semanticweb.org/marta/ontologies/2025/cinema#{nome}
        :{nome} rdf:type owl:NamedIndividual ,
                          :Pessoa .
        """


for filme in dataset["movies"]:
    
    if filme["género"] == None or len(filme["género"]) == 0:
        generos = ""
    else:
        generos = ":temGénero"
        for g in filme["género"]:
            generos += f" :{g} ,"
        generos = generos[:-1] + ";"


    if filme["pessoasRelacionadas"] == None or len(filme["pessoasRelacionadas"]) == 0:
        pessoas = ""
    else:
        pessoas = ":temAtor"
        for p in filme["pessoasRelacionadas"]:
            name = id(p["name"])
            pessoas += f" :{name} ,"
        pessoas = pessoas[:-1] + ";"

        
    nome = id(filme["tituloOriginal"])
        
    output += f"""
    ###  http://www.semanticweb.org/marta/ontologies/2025/cinema#{nome}
    :{nome} rdf:type owl:NamedIndividual ,
                       :Filme ;
              :temLíngua :{filme["linguaOriginal"]};
              :temPaísOrigem :{filme["PaisOrigem"]} ;
              {generos}
              {pessoas}
              :data "{filme["ano"]}" ;
              :duração "{filme["duração"]}"^^xsd:int .
    """


    
with open("out.txt", "w", encoding="utf-8") as f:
    f.write(output)
      
   