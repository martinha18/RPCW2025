import os
import random

import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room
from game_generator import GameGenerator
from game import Game

GRAPHDB_API_URL = "http://localhost:7200"
CORS_HOSTS = ["http://localhost:5000", "http://localhost:5173"]  # TODO better cors config
ALLOWED_EXTENSIONS = {'ttl'}

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1000 * 1000

CORS(app, origins=CORS_HOSTS)

socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins=CORS_HOSTS)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_room_id():
    while True:
        room_id = str(random.randint(100000, 999999))
        if room_id not in games:
            return room_id


# Admin API
@app.route('/api/', methods=['GET'])
def list_repositories():
    try:
        response = requests.get(f"{GRAPHDB_API_URL}/rest/repositories")
        if response.status_code == 200:
            repositories = response.json()
            repositories = list(map(lambda r: r['id'], repositories))
            return jsonify(repositories), 200
        else:
            return jsonify({'error': 'Failed to fetch repositories', 'details': response.text}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'name' not in request.form:
        return jsonify({'error': 'Missing file or name'}), 400

    file = request.files['file']
    name = request.form['name']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        req = {"id":name,"params":{"queryTimeout":{"name":"queryTimeout","label":"Query timeout (seconds)","value":0},"cacheSelectNodes":{"name":"cacheSelectNodes","label":"Cache select nodes","value":"true"},"rdfsSubClassReasoning":{"name":"rdfsSubClassReasoning","label":"RDFS subClass reasoning","value":"true"},"validationEnabled":{"name":"validationEnabled","label":"Enable the SHACL validation","value":"true"},"ftsStringLiteralsIndex":{"name":"ftsStringLiteralsIndex","label":"FTS index for xsd:string literals","value":"default"},"shapesGraph":{"name":"shapesGraph","label":"Named graphs for SHACL shapes","value":"http://rdf4j.org/schema/rdf4j#SHACLShapeGraph"},"parallelValidation":{"name":"parallelValidation","label":"Run parallel validation","value":"true"},"title":{"name":"title","label":"Repository description","value":""},"checkForInconsistencies":{"name":"checkForInconsistencies","label":"Enable consistency checks","value":"false"},"performanceLogging":{"name":"performanceLogging","label":"Log the execution time per shape","value":"false"},"disableSameAs":{"name":"disableSameAs","label":"Disable owl:sameAs","value":"true"},"ftsIrisIndex":{"name":"ftsIrisIndex","label":"FTS index for full-text indexing of IRIs","value":"none"},"entityIndexSize":{"name":"entityIndexSize","label":"Entity index size","value":"10000000"},"dashDataShapes":{"name":"dashDataShapes","label":"DASH data shapes extensions","value":"true"},"queryLimitResults":{"name":"queryLimitResults","label":"Limit query results","value":0},"throwQueryEvaluationExceptionOnTimeout":{"name":"throwQueryEvaluationExceptionOnTimeout","label":"Throw exception on query timeout","value":"false"},"id":{"name":"id","label":"Repository ID","value":"repo-test"},"storageFolder":{"name":"storageFolder","label":"Storage folder","value":"storage"},"validationResultsLimitPerConstraint":{"name":"validationResultsLimitPerConstraint","label":"Validation results limit per constraint","value":1000},"enablePredicateList":{"name":"enablePredicateList","label":"Enable predicate list index","value":"true"},"transactionalValidationLimit":{"name":"transactionalValidationLimit","label":"Transactional validation limit","value":"500000"},"ftsIndexes":{"name":"ftsIndexes","label":"FTS indexes to build (comma delimited)","value":"default, iri"},"logValidationPlans":{"name":"logValidationPlans","label":"Log the executed validation plans","value":"false"},"imports":{"name":"imports","label":"Imported RDF files(';' delimited)","value":""},"inMemoryLiteralProperties":{"name":"inMemoryLiteralProperties","label":"Cache literal language tags","value":"true"},"isShacl":{"name":"isShacl","label":"Enable SHACL validation","value":"false"},"ruleset":{"name":"ruleset","label":"Ruleset","value":"rdfsplus-optimized"},"readOnly":{"name":"readOnly","label":"Read-only","value":"false"},"enableFtsIndex":{"name":"enableFtsIndex","label":"Enable full-text search (FTS) index","value":"false"},"enableLiteralIndex":{"name":"enableLiteralIndex","label":"Enable literal index","value":"true"},"enableContextIndex":{"name":"enableContextIndex","label":"Enable context index","value":"false"},"defaultNS":{"name":"defaultNS","label":"Default namespaces for imports(';' delimited)","value":""},"baseURL":{"name":"baseURL","label":"Base URL","value":"http://example.org/owlim#"},"logValidationViolations":{"name":"logValidationViolations","label":"Log validation violations","value":"false"},"globalLogValidationExecution":{"name":"globalLogValidationExecution","label":"Log every execution step of the SHACL validation","value":"false"},"entityIdSize":{"name":"entityIdSize","label":"Entity ID size","value":"32"},"repositoryType":{"name":"repositoryType","label":"Repository type","value":"file-repository"},"eclipseRdf4jShaclExtensions":{"name":"eclipseRdf4jShaclExtensions","label":"RDF4J SHACL extensions","value":"true"},"validationResultsLimitTotal":{"name":"validationResultsLimitTotal","label":"Validation results limit total","value":1000000}},"title":"","type":"graphdb","location":""}
        requests.post(f"{GRAPHDB_API_URL}/rest/repositories", json=req)
        extra = requests.get(f"{GRAPHDB_API_URL}/repositories/{name}/statements", headers={'accept': 'text/turtle'}).text
        contents = extra.encode('utf-8') + file.read()
        requests.put(f"{GRAPHDB_API_URL}/repositories/{name}/statements", data=contents, headers={"Content-Type": "text/turtle"})

        return jsonify({'message': f'Repository {name} created and data uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def game_generator_req(name, process_generator):
    try:
        response = requests.get(f"{GRAPHDB_API_URL}/repositories/{name}/namespaces", headers={'accept': 'application/sparql-results+json'})
        namespaces = response.json()

        default_prefix = None
        for ns in namespaces['results']['bindings']:
            if ns['prefix']['value'] == '':
                default_prefix = ns['namespace']['value']

        def graphdb_sparql_query(query, _prefix):
            query = f'PREFIX : <{_prefix}>\n\n' + query

            query_response = requests.post(f"{GRAPHDB_API_URL}/repositories/{name}", data=query, headers={'Content-Type': 'application/sparql-query', 'accept': 'application/sparql-results+json'})
            results = query_response.json()

            bindings = results.get("results", {}).get("bindings", [])
            vars_ = results.get("head", {}).get("vars", [])

            return {
                "head": {"vars": [str(v) for v in vars_]},
                "results": {"bindings": bindings}
            }

        generator = GameGenerator(graphdb_sparql_query)
        out = process_generator(generator, default_prefix)

        return jsonify(out), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/<name>', methods=['GET'])
def get_questions(name):
    count = int(request.args.get('count', 5))

    def process(generator, prefix):
        return generator.generate_game(count, prefix)

    return game_generator_req(name, process)


@app.route('/api/<name>/shape', methods=['GET'])
def get_shape(name):
    def process(generator, prefix):
        return generator.query_db_representation(prefix)

    return game_generator_req(name, process)


@app.route('/api/<name>/query', methods=['POST'])
def run_query(name):
    query = request.get_json().get('query')

    def process(generator, prefix):
        return generator.query_db(query, prefix, include_colon=True)

    return game_generator_req(name, process)


@app.route('/api/<name>', methods=['DELETE'])
def delete_repository(name):
    try:
        response = requests.delete(f"{GRAPHDB_API_URL}/repositories/{name}")

        if response.status_code == 204:
            return jsonify({'message': f'{name} deleted successfully'}), 204
        else:
            return jsonify({'error': 'Failed to delete repository', 'details': response.text}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Game
games = {}
sid_to_room = {}


def handle_init_game(data):
    questions = data['questions']
    adm_id = request.sid
    room_id = generate_room_id()

    def cleanup(_room_id):
        del games[_room_id]

    game = Game(socketio, room_id, questions, adm_id, cleanup)
    games[room_id] = game

    join_room(room_id)
    sid_to_room[adm_id] = room_id

    socketio.emit('game_initialized', {'room_id': room_id}, to=adm_id)


def handle_join_game(data):
    room_id = data['room_id']
    player_id = request.sid
    name = data['username']

    if room_id not in games:
        socketio.emit('error', {'message': 'Game not found'}, to=player_id)
        return

    join_room(room_id)
    sid_to_room[player_id] = room_id

    games[room_id].player_connect(player_id, name)


def handle_start_game():
    adm_id = request.sid
    room_id = sid_to_room.get(adm_id)

    if room_id and room_id in games:
        games[room_id].adm_start(adm_id)


def handle_next_question():
    adm_id = request.sid
    room_id = sid_to_room.get(adm_id)

    if room_id and room_id in games:
        games[room_id].adm_next(adm_id)


def handle_submit_answer(data):
    player_id = request.sid
    room_id = sid_to_room.get(player_id)

    if room_id and room_id in games:
        games[room_id].player_answer(player_id, data)


@socketio.on('message')
def handle_socket_message(msg, *args):
    if msg == 'init_game':
        handle_init_game(*args)
    elif msg == 'join_game':
        handle_join_game(*args)
    elif msg == 'start_game':
        handle_start_game()
    elif msg == 'next_question':
        handle_next_question()
    elif msg == 'submit_answer':
        handle_submit_answer(*args)


@socketio.on('disconnect')
def handle_disconnect():
    player_id = request.sid
    room_id = sid_to_room.pop(player_id, None)

    if room_id and room_id in games:
        leave_room(room_id)
        games[room_id].player_disconnect(player_id)


# Static webpage (client side rendering)
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def index(path):
    file_path = os.path.join('frontend/dist', path)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory('frontend/dist', path)
    else:
        return send_from_directory('frontend/dist', 'index.html')


# Main
if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)
