from helper import *
import streamlit as st
from streamlit_agraph import agraph, Config
from streamlit_agraph.node import Node
from streamlit_agraph.edge import Edge
from rdflib import Graph, Literal
from rdflib.namespace import RDF, XSD
# from SPARQLWrapper import SPARQLWrapper, JSON
import json
from rdflib import Graph, Namespace


def generate_graph(model):
    with open(f"{model}_filter.json") as f:
        triplets = json.load(f)

    with open(f'{model}_ontology.json') as f:
        allKeys = json.load(f)
        entityOnto = allKeys['entities']
        relationOnto = allKeys['relation']

    cryptoBaseUri = "http://crypto.org/"
    allNameSpace = {}
    graph = Graph()
    nm = graph.namespace_manager

    for s, p, o in triplets[:20]:
        subjClass = entityOnto[s]
        predClass = relationOnto[p]
        predClass = "_".join(predClass.split()) if len(
            predClass.split()) > 1 else predClass
        objClass = entityOnto[o]
        subjUri = cryptoBaseUri+subjClass+"/"
        predUri = cryptoBaseUri+predClass+"/"
        objUri = cryptoBaseUri+objClass+"/"
        if subjUri not in allNameSpace:
            allNameSpace[subjUri] = Namespace(subjUri)
            prefixSub = subjClass
            nm.bind(prefixSub, allNameSpace[subjUri])

        if objUri not in allNameSpace:
            allNameSpace[objUri] = Namespace(objUri)
            prefixObj = objClass
            nm.bind(prefixObj, allNameSpace[objUri])

        if predUri not in allNameSpace:
            allNameSpace[predUri] = Namespace(predUri)
            prefixPred = predClass
            nm.bind(prefixPred, allNameSpace[predUri])

        if len(s.split()) > 1:
            s = "_".join(s.split())
        if len(o.split()) > 1:
            o = "_".join(o.split())
        if len(p.split()) > 1:
            p = "_".join(p.split())
        s = allNameSpace[subjUri][s]
        o = allNameSpace[objUri][o]
        p = allNameSpace[predUri][p]
        graph.add((s, p, o))
        graph.add((s, RDF.type, (Literal(subjClass, datatype=XSD.string))))
        graph.add((p, RDF.type, (Literal(predClass, datatype=XSD.string))))
        graph.add((o, RDF.type, (Literal(objClass, datatype=XSD.string))))
    return graph


st.set_page_config(page_title="KG", page_icon=":tada:", layout="wide")

# ---- HEADER -----
st.subheader("Columbia DSI and Accenture")
st.title("Knowledge Graph for Crypto Papers")
st.write("----")
st.subheader("Query")
text_input = st.text_input(
    "Enter some text 👇",
    placeholder="This is a placeholder",
)
if text_input:
    with st.spinner('Wait for it...'):
        gen_sparql = query_to_sparql(text_input)

    # server = sparql.SPARQLServer('http://localhost:9999/blazegraph/sparql')
    # result = server.query(gen_sparql)
    # triplets = result['results']['bindings']

    st.success('Done!')
    st.write(f"Converted:\n{gen_sparql}")
    st.write("##")
    st.subheader("Visualized Graph")

    nodes_set = set()
    edges_set = set()
    nodes = []
    edges = []

    # sample graph
    # graph = Graph()
    # graph.parse("http://www.w3.org/People/Berners-Lee/card")

    model_name = st.radio(
        "Which model do you want to use?",
        ('Stanford Open IE', 'AllenNLP'))
    filename = {
        'Stanford Open IE': "stanfordopenie",
        'AllenNLP': "allennlp",
    }
    graph = generate_graph(filename[model_name])

    # graph = [("A", "has", "B"), ("B", "is_part_of", "C")]

    for subj, pred, obj in graph:
        src, trg = Node(id=str(subj), label=str(subj)), Node(
            id=str(obj), label=str(obj))
        edge = Edge(source=src.id, target=trg.id, title=pred, label=pred)
        if src.id not in nodes_set:
            nodes_set.add(src.id)
            nodes.append(src)
        if trg.id not in nodes_set:
            nodes_set.add(trg.id)
            nodes.append(trg)
        if edge.title not in edges_set:
            edges_set.add(edge.title)
            edges.append(edge)

    config = Config(width=1600,
                    height=800)

    # for debug
    # a = [x.to_dict() for x in nodes]
    # for i in a:
    #     print(i)

    return_value = agraph(nodes=list(nodes),
                          edges=list(edges),
                          config=config)
