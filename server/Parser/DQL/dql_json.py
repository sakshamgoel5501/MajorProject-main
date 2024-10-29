import js2py

def dql_query_to_json(query):
    context = js2py.EvalJs(enable_require=True)
    f = open("Parser/DQL/dql_parser.js", "r")
    txt = f.read()
    context.eval(txt)
    json_str = context.dql_to_json(query)
    return json_str

