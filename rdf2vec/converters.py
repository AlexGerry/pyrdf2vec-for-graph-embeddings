import urllib
import requests

import rdflib
from tqdm import tqdm

from rdf2vec.graph import KnowledgeGraph, Vertex


def create_kg(triples, label_predicates):
    """Creates a knowledge graph according to triples and predicates label.

    Args:
        triples (list): The triples where each item in this list must be an
            iterable (e.g., tuple, list) of three elements.
        label_predicates (list): The URI's of the predicates that have to be
            excluded from the graph to avoid leakage.

    Returns:
        graph.KnowledgeGraph: The knowledge graph.

    """
    kg = KnowledgeGraph()
    for (s, p, o) in tqdm(triples):
        if p not in label_predicates:
            s_v = Vertex(str(s))
            o_v = Vertex(str(o))
            p_v = Vertex(str(p), predicate=True, _from=s_v, _to=o_v)
            kg.add_vertex(s_v)
            kg.add_vertex(p_v)
            kg.add_vertex(o_v)
            kg.add_edge(s_v, p_v)
            kg.add_edge(p_v, o_v)
    return kg


def rdflib_to_kg(file_name, filetype=None, label_predicates=[]):
    """Converts a rdflib.Graph to a knowledge graph.

    Args:
        file_name (str): The file name that contains the rdflib.Graph.
        filetype (string): The format of the knowledge graph.
            Defaults to None.
        label_predicates (list): The predicates label.
            Defaults to [].

    Returns:
        graph.KnowledgeGraph: The knowledge graph.

    """
    g = rdflib.Graph()
    if filetype is not None:
        g.parse(file_name, format=filetype)
    else:
        g.parse(file_name)

    label_predicates = [rdflib.term.URIRef(x) for x in label_predicates]
    return create_kg(g, label_predicates)


def endpoint_to_kg(endpoint_url="http://localhost:5820/db/query?query=", 
                   label_predicates=[]):
    """Generates a knowledge graph using a SPARQL endpoint.

    endpoint_url (string): The SPARQL endpoint.
        Defaults to http://localhost:5820/db/query?query=
    label_predicates (list): The predicates label.
        Defaults to [].

    Returns:
        graph.KnowledgeGraph: The knowledge graph.

    """
    session = requests.Session()
    session.mount('http://', adapter)
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=100, pool_maxsize=100
    )

    query = urllib.parse.quote("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
    try:
        qres = r.json()['results']['bindings']
        r = session.get(
            endpoint_url + query,
            headers={"Accept": "application/sparql-results+json"},
        )
    except Exception as e:
        print(e)
        print("could not query result")
        qres = []

    triples = [
        (row["s"]["value"], row["p"]["value"], row["o"]["value"])
        for row in qres
    ]
    return create_kg(triples, label_predicates)