# Um jogo sobre a história de Portugal
# 2025-02-24 jcr
#
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
import random
import requests

app = Flask(__name__)
app.secret_key = 'História de Portugal'
CORS(app)

# Retrieve info from GraphDB
def query_graphdb(endpoint_url, sparql_query):
    headers = {
        'Accept': 'application/json', 
    }
    response = requests.get(endpoint_url, params={'query': sparql_query}, headers=headers)
    if response.status_code == 200:
        return response.json() 
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")


# Queries
endpoint = "http://localhost:7200/repositories/HistoriaPT"

sparql_query_reis = """
PREFIX historia: <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?n ?o
    WHERE {
        ?s a :Rei.
    	?s :nome ?n .
    	?s :nascimento ?o.
    }
"""

sparql_query_dinastias = """
PREFIX historia: <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
select ?n ?dnome
where {
    ?s rdf:type :Rei .
    ?s :nome ?n .
    ?r :dinastia ?d .
    ?r :temMonarca ?s .
    ?d :nome ?dnome .
}
"""
sparql_query_dinastias2 = """
PREFIX historia: <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
select distinct ?dnome
where {
    ?r rdf:type :Reinado .
    ?r :dinastia ?d .
    ?d :nome ?dnome .
}
"""


sparql_query_presidentes = """
PREFIX historia: <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
select ?n ?np
where {
    ?s rdf:type :Presidente .
    ?s :nome ?n .
    ?part :nome ?np .
    ?part :temMilitante ?s .
}
"""
sparql_query_partidos = """
PREFIX historia: <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
select distinct ?pnome
where {
    ?p rdf:type :Partido .
    ?p :nome ?pnome .
}
"""


# Getting the wanted information from the data
result_reis = query_graphdb(endpoint, sparql_query_reis)
listaReis = []
for r in result_reis['results']['bindings']:
    t = {
            'nome': r['n']['value'].split('#')[-1], 
            'dataNasc': r['o']['value'].split('#')[-1]
    }
    listaReis.append(t)


result_dinastias = query_graphdb(endpoint, sparql_query_dinastias)
listaDinastias = []
for r in result_dinastias['results']['bindings']:
    t = {
            'nome': r['n']['value'].split('#')[-1], 
            'dinastia': r['dnome']['value'].split('#')[-1]
    }
    listaDinastias.append(t)

result_dinastias2 = query_graphdb(endpoint, sparql_query_dinastias2)
listaDinastias2 = []
for r in result_dinastias2['results']['bindings']:
    listaDinastias2.append(r['dnome']['value'].split('#')[-1])


result_presidentes = query_graphdb(endpoint, sparql_query_presidentes)
listaPresidentes = []
for r in result_presidentes['results']['bindings']:
    t = {
            'nome': r['n']['value'].split('#')[-1], 
            'partido': r['np']['value'].split('#')[-1]
    }
    listaPresidentes.append(t)

result_partidos = query_graphdb(endpoint, sparql_query_partidos)
listaPartidos = []
for r in result_partidos['results']['bindings']:
    listaPartidos.append(r['pnome']['value'].split('#')[-1])


# Routing
@app.route('/')
def home():
    session['score'] = 0
    session['questions'] = 0
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET'])
def generate_question():
    type = random.randint(1,6)
    question = None
    match type:
        case 1:
            reis = random.choices(listaReis, k=4)
            reiSel = reis[random.randrange(0,4)]
            question = {
                "question": f"Quando nasceu o rei {reiSel['nome']}?",
                "options": [reis[0]['dataNasc'], reis[1]['dataNasc'], reis[2]['dataNasc'], reis[3]['dataNasc']],
                "answer": reiSel['dataNasc']
            }

        case 2:
            dinastias = random.choices(listaDinastias, k=4)
            dinastiaSel = dinastias[random.randrange(0,4)]
            question = {
                "question": f"Em que dinastia reinou o rei {dinastiaSel['nome']}?",
                "options": listaDinastias2,
                "answer": dinastiaSel['dinastia']
            }

        case 3:
            presidentes = random.choices(listaPresidentes, k=4)
            presidenteSel = presidentes[random.randrange(0,4)]
            listaRestante = [partido for partido in listaPartidos if partido != presidenteSel['partido']]
            opt = (random.sample(listaRestante, 3) + [presidenteSel['partido']])
            random.shuffle(opt)
            question = {
                "question": f"Qual o partido político do presidente {presidenteSel['nome']}?",
                "options": opt,
                "answer": presidenteSel['partido']
            }

        case 4:
            rei = random.choice(listaReis)
            sel = random.randint(0,1)
            if sel == 0:
                question = {
                    "question": f"O {rei['nome']} nasceu em {rei['dataNasc']}.",
                    "options": ["Verdadeiro", "Falso"],
                    "answer": "Verdadeiro"
                }
            else:
                fake_date = random.choice([r['dataNasc'] for r in listaReis if r['dataNasc'] != rei['dataNasc']])
                question = {
                    "question": f"O {rei['nome']} nasceu em {fake_date}.",
                    "options": ["Verdadeiro", "Falso"],
                    "answer": "Falso"
                }

        case 5:
            dinastia = random.choice(listaDinastias)
            sel = random.randint(0,1)
            if sel == 0:
                question = {
                    "question": f"O rei {dinastia['nome']} reinou na {dinastia['dinastia']}.",
                    "options": ["Verdadeiro", "Falso"],
                    "answer": "Verdadeiro"
                }
            else:
                fake_dinastia = random.choice([d for d in listaDinastias2 if d != dinastia['dinastia']])
                question = {
                    "question": f"O rei {dinastia['nome']} reinou na {fake_dinastia}.",
                    "options": ["Verdadeiro", "Falso"],
                    "answer": "Falso"
                }

        case 6:
            presidente = random.choice(listaPresidentes)
            sel = random.randint(0,1)
            if sel == 0:
                question = {
                    "question": f"O presidente {presidente['nome']} pertenceu ao partido {presidente['partido']}.",
                    "options": ["Verdadeiro", "Falso"],
                    "answer": "Verdadeiro"
                }
            else:
                fake_partido = random.choice([p for p in listaPartidos if p != presidente['partido']])
                question = {
                    "question": f"O presidente {presidente['nome']} pertenceu ao partido {fake_partido}.",
                    "options": ["Verdadeiro", "Falso"],
                    "answer": "Falso"
                }

        case _:
            print("Opção inválida")
    
    return render_template('quiz.html', question=question)

@app.route('/quiz', methods=['POST'])
def quiz():
    user_answer = request.form.get('answer')
    answer_correct = request.form.get('answerCorrect')
    correct = answer_correct == user_answer
    session['score'] = session.get('score', 0) + (1 if correct else 0)
    session['questions'] = session.get('questions', 0) + 1
    return render_template('result.html', correct=correct, correct_answer=answer_correct, score=session['score'], questions=session['questions'])

@app.route('/score')
def score():
    return render_template('score.html', score=session.get('score', 0), questions=session.get('questions', 0))

if __name__ == '__main__':
    app.run(debug=True)
