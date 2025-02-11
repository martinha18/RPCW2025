import json

def json_to_ttl(data_json):
    ttl_output = ""
    seen_modalities = set()
    seen_people = set()
    clubs_modalities = {}

    for data in data_json:
        athlete_id = f"{data['nome']['primeiro'].lower()}-{data['nome']['último'].lower()}".replace(" ", "")
        club_id = data['clube'].lower().replace(" ", "")
        modality_id = data['modalidade'].lower().replace(" ", "")
        exam_id = f"emd{data['_id']}".replace(" ", "")
        practice_id = f"pd{data['_id']}".replace(" ", "")

        # Exame
        ttl_output += f"""
###  http://www.semanticweb.org/marta/ontologies/2025/emd#{exam_id}
:{exam_id} rdf:type owl:NamedIndividual ,
           :Exame ;
           :realizadoPor :{athlete_id} ;
           :relativoA :{modality_id} ;
           :temData "{data['dataEMD']}T00:00:00"^^xsd:dateTime ;
           :temResultado "{str(data['resultado']).lower()}"^^xsd:boolean .

"""
        
        # Atleta
        if athlete_id not in seen_people:
            ttl_output += f"""
###  http://www.semanticweb.org/marta/ontologies/2025/emd#{athlete_id}
:{athlete_id} rdf:type owl:NamedIndividual ,
               :Atleta ;
               :realizou :{exam_id} ;
               :temApelido "{data['nome']['último']}" ;
               :temEmail "{data['email']}" ;
               :temGenero "{data['género']}" ;
               :temIdade {data['idade']} ;
               :temMorada "{data['morada']}" ;
               :temPrimeiroNome "{data['nome']['primeiro']}" .

"""
            seen_people.add(athlete_id)
        
        # Modalidade
        if modality_id not in seen_modalities:
            ttl_output += f"""
###  http://www.semanticweb.org/marta/ontologies/2025/emd#{modality_id}
:{modality_id} rdf:type owl:NamedIndividual ,
               :Modalidade ;
               :temNome "{data['modalidade']}" .

"""
            seen_modalities.add(modality_id)
        
        # Armazena modalidades associadas ao clube
        if club_id not in clubs_modalities:
            clubs_modalities[data['clube']] = set()
        clubs_modalities[data['clube']].add(modality_id)
        
        # Prática Desportiva
        ttl_output += f"""
###  http://www.semanticweb.org/marta/ontologies/2025/emd#{practice_id}
:{practice_id} rdf:type owl:NamedIndividual ,
               :PráticaDesportiva ;
               :comExame :{exam_id} ;
               :naModalidade :{modality_id} ;
               :noClube :{club_id} ;
               :peloAtleta :{athlete_id} ;
               :éFederada "{str(data['federado']).lower()}"^^xsd:boolean .

"""
    
    # Processar clubes no final
    for club_name, modalities in clubs_modalities.items():
        club_id = club_name.lower().replace(" ", "")
        modalities_ttl = " , ".join(f":{mod}" for mod in modalities)
        ttl_output += f"""
###  http://www.semanticweb.org/marta/ontologies/2025/emd#{club_id}
:{club_id} rdf:type owl:NamedIndividual ,
           :Clube ;
           :apresenta {modalities_ttl} ;
           :temNome "{club_name}" .

"""
    
    return ttl_output.strip()




with open("emd.json", "r", encoding="utf-8") as file:
    data_json = json.load(file)

ttl_output = json_to_ttl(data_json)

with open("output.txt", "w", encoding="utf-8") as output_file:
    output_file.write(ttl_output)

print("Conversão concluída. Resultado salvo em output.txt")
