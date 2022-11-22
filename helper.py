import time


def query_to_sparql(query):
    time.sleep(.5)
    return f"""{query.lower()}"""
    # return """
    #     select * where { <http://blazegraph.com/blazegraph> ?p ?o }
    # """
