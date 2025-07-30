from ollama import chat
from ollama import ChatResponse
import random
import re

class GameGenerator:
    def __init__(self, query_function):
        self.query_function = query_function

    def query_db(self, query, prefix, include_colon=False):
        response_data = self.query_function(query, prefix)
        vars_ = response_data['head']['vars']
        binds = response_data['results']['bindings']
        results = []
        
        for binding in binds:
            obj = {}
            for v in vars_:
                if v not in binding:
                    continue
                value = binding[v]['value']
                if isinstance(value, str) and value.startswith(prefix):
                    value = value[len(prefix):]
                    if include_colon:
                        value = f':{value}'
                obj[v] = value
            results.append(obj)
        
        return results

    def query_db_representation(self, prefix):
        queries = {
            'classes': f"""
                SELECT DISTINCT ?class
                WHERE {{
                    ?class a owl:Class .
                    FILTER(strstarts(str(?class), "{prefix}"))
                }}
            """,
            'classes_inheritance': f"""
                SELECT DISTINCT ?subClass ?superClass
                WHERE {{
                    ?subClass rdfs:subClassOf ?superClass .
                    ?subClass a owl:Class .
                    ?superClass a owl:Class .
                    FILTER(strstarts(str(?subClass), "{prefix}"))
                    FILTER(strstarts(str(?superClass), "{prefix}"))
                }}
            """,
            'object_properties': f"""
                SELECT DISTINCT ?property ?domain ?range
                WHERE {{
                    ?property a owl:ObjectProperty .
                    ?property rdfs:range ?range .
                    OPTIONAL {{ ?property rdfs:domain ?domain . }}
                    OPTIONAL {{ ?subject a ?domain ; ?property ?object . }}
                    FILTER(strstarts(str(?property), "{prefix}"))
                    FILTER(strstarts(str(?domain), "{prefix}"))
                }}
            """,
            'data_properties': f"""
                SELECT DISTINCT ?property ?domain ?range
                WHERE {{
                    ?property a owl:DatatypeProperty .
                    OPTIONAL {{ ?property rdfs:range ?range . }}
                    OPTIONAL {{ ?subject a ?domain ; ?property ?object . }}
                    OPTIONAL {{
                        ?property rdfs:domain ?bnode .
                        ?bnode owl:unionOf ?list .
                        ?list (rdf:rest*/rdf:first) ?domain .
                    }}
                    OPTIONAL {{ ?property rdfs:domain ?domain . }}
                    FILTER(strstarts(str(?property), "{prefix}"))
                    FILTER(strstarts(str(?domain), "{prefix}"))
                }}
            """
        }
        
        return {key: self.query_db(q, prefix) for key, q in queries.items()}

    def _generate_db_representation(self, prefix):
        data = self.query_db_representation(prefix)
        classes = {c['class']: {'className': c['class'], 'inheritance': [], 'objectProperties': [], 'dataProperties': []} for c in data['classes']}
        
        for item in data['classes_inheritance']:
            if item['subClass'] in classes:
                classes[item['subClass']]['inheritance'].append(classes[item['superClass']])
        
        for item in data['object_properties']:
            prop = {'property': item['property'], 'range': classes.get(item['range'])}
            if item['domain'] in classes:
                classes[item['domain']]['objectProperties'].append(prop)
        
        for item in data['data_properties']:
            prop = {'property': item['property']}
            if item['domain'] in classes:
                classes[item['domain']]['dataProperties'].append(prop)
        
        return classes

    def _camel_to_spaced(self, text):
        return re.sub(r'([A-Z])', r' \1', text).lower().strip()

    def _shuffle(self, strings):
        shuffled = strings[:]
        random.shuffle(shuffled)
        return shuffled, [strings.index(s) for s in shuffled]

    def _filter_unique_pairs(self, pairs):
        if not pairs:
            return []

        keys = pairs[0].keys()
        seen_values = {key: set() for key in keys}
        filtered_pairs = []

        for pair in pairs:
            if any(pair[key] in seen_values[key] for key in keys):
                continue

            filtered_pairs.append(pair)

            for key in keys:
                seen_values[key].add(pair[key])

        return filtered_pairs

    def generate_game(self, question_count, prefix):
        db_representation = self._generate_db_representation(prefix)
        classes = [c for c in db_representation.values() if c['dataProperties'] and c['objectProperties']]
        
        questions = []
        for _ in range(question_count):
            kind = random.randint(0, 2)

            class_selected = random.choice(classes)
            data_property = random.choice(class_selected['dataProperties'])['property']
            object_property = random.choice(class_selected['objectProperties'])
            object_data_property = random.choice(object_property['range']['dataProperties'])['property']
            limit = 2 if kind == 1 else 4
            
            query = f"""
                SELECT DISTINCT ?subject ?object
                WHERE {{
                    ?sub a :{class_selected['className']} ;
                         :{data_property} ?subject ;
                         :{object_property['property']} ?obj .
                    ?obj :{object_data_property} ?object .
                }}
                ORDER BY RAND()
                LIMIT {limit}
            """
            data = self.query_db(query, prefix)
            data = self._filter_unique_pairs(data)
            
            if not data:
                continue
            
            question = {}
            class_display = self._camel_to_spaced(class_selected['className'])
            data_display = self._camel_to_spaced(data_property)
            object_display = self._camel_to_spaced(object_property['property'])
            object_class_display = self._camel_to_spaced(object_property['range']['className'])
            object_data_display = self._camel_to_spaced(object_data_property)

            model = 'gemma3:12b'
            system_prompt = '''Apenas utiliza português de Portugal.
Vai te ser passada alguma informação, a tua intenção é desenvolveres uma questão com base nessa informação.
A informação é selecionada aleatóriamente de uma ontologia, e é te indicadas as classes relações e atributos pertinentes à questão, sendo que no fim é te fornecida a questão.
Evita a terminologia de entidades, como classes, atributos ou relações.
Toda a informação fornecida TÊM de ser utilizada na questão. Apenas fornece a questão na tua reposta.
Quando te for pedida uma associação não é para desenvolveres uma pergunta, é uma questão de associação como num teste.
Exemplo: A classe "rei" com o atributo "nome" de valor "D. Pedro II" está associado através da relação "tem reinado" à classe "reinado" que contem um atributo "comeco" de valor "6 de Dezembro de 1656". Qual o valor do atributo "começo"?
Deves formular uma questão como: O reinado de D. Pedro II começou a 6 de Dezembro de 1656?
Exemplo 2: A classe "reinado" com o atributo "fim" está associado através da relação "tem monarca" à classe "monarca" que contem um atributo "nome". Associe o atributo "fim" ao atributo "nome".
Deves formular uma questão como: Associe o fim de um reinado ao monarca.
'''

            right = random.choice(data)
            'A classe "conquista" com o atributo "data" de valor "1212" está associado através da relação "tem reinado" à classe "reinado" que contem um atributo "fim". Qual o valor do atributo "fim"?'

            if kind == 0:
                response: ChatResponse = chat(model=model, messages=[
                    {
                        'role': 'system',
                        'content': system_prompt,
                    },
                    {
                        'role': 'user',
                        'content': f'A classe "{class_display}" com o atributo "{data_display}" de valor "{right["subject"]}" está associado através da relação "{object_display}" à classe "{object_class_display}" que contem um atributo "{object_data_display}". Qual o valor do atributo "{object_data_display}"?',
                    },
                ])

                question['question'] = response.message.content
                question['options'] = [d['object'] for d in data]
                question['answer'] = right['object']
            elif kind == 1:
                res = data[0]['object']

                response: ChatResponse = chat(model=model, messages=[
                    {
                        'role': 'system',
                        'content': system_prompt,
                    },
                    {
                        'role': 'user',
                        'content': f'A classe "{class_display}" com o atributo "{data_display}" de valor "{right["subject"]}" está associado através da relação "{object_display}" à classe "{object_class_display}" que contem um atributo "{object_data_display}" de valor "{res}". Esta informação é verdadeira ou falsa?',
                    },
                ])

                question['question'] = response.message.content
                question['options'] = ['Verdadeiro', 'Falso']
                question['answer'] = 'Verdadeiro' if res == right['object'] else 'Falso'
            else:
                response: ChatResponse = chat(model=model, messages=[
                    {
                        'role': 'system',
                        'content': system_prompt,
                    },
                    {
                        'role': 'user',
                        'content': f'A classe "{class_display}" com o atributo "{data_display}" está associado através da relação "{object_display}" à classe "{object_class_display}" que contem um atributo "{object_data_display}". Associe o atributo "{data_display}" ao atributo "{object_data_display}".',
                    },
                ])

                question['question'] = response.message.content
                options = [d['subject'] for d in data]
                options2 = [d['object'] for d in data]
                shuffled, index_mapping = self._shuffle(options2)
                question['options'] = options
                question['options2'] = shuffled
                question['answer'] = '/'.join(map(str, index_mapping))

            questions.append(question)
        
        return questions
