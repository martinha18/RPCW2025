from rdflib import Graph, Namespace

n = Namespace("http://www.semanticweb.org/marta/ontologies/2025/geografia#")
g = Graph()
g.parse("geografia.ttl")

rm = [n.área, n.comprimento, n.éParteDe, n.temMar]

for s, p, o in list(g):
    if s in rm or p in rm:
        g.remove((s, p, o))

g.serialize('geografia-trim.ttl', format="turtle")
