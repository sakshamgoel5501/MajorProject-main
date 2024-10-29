from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
from Parser.DQL.dql_json import dql_query_to_json
from Mapper.query import create_query
from Parser.DDL.ddl_parser import ddl_parser
from Mapper.DDL_Mapper import generate_schema
from Parser.DML.DMLParser import dml_parser
from Mapper.DML_Mapper import mutation

app = Flask(__name__)
# cors = CORS(app, resources={r"/process_data/*": {"origins": "http://localhost:3000"}})
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

ddl_commands = ["CREATE TABLE", "DROP TABLE", "ALTER TABLE", "RENAME TABLE", "TRUNCATE TABLE"]
dql_commands = ["SELECT"]
dml_commands = ["UPDATE", "INSERT", "DELETE"]

def sql_to_graphql(sql):
    queries = sql.split(";")
    res_graphql = ""
    for query in queries:
        if(query == ''):
            continue
        query = query.strip()
        words = query.split(" ")
        if(words[0].upper() in dql_commands):
            dql_json = dql_query_to_json(query)
            res = create_query(dql_json)
        elif(words[0].upper() + " " + words[1].upper() in ddl_commands):
            ddl_json = ddl_parser(query)
            res = generate_schema(ddl_json)
        elif(words[0].upper() in dml_commands):
            dml_json = dml_parser(query)
            res = mutation(dml_json)
        else:
            res = "Invalid sql query"
        res_graphql = res_graphql + res + "\n" + "\n" + "\n"
    return res_graphql.strip()

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Headers', 'x-csrf-token')
    response.headers.add('Access-Control-Allow-Methods',
                                'GET, POST, OPTIONS, PUT, PATCH, DELETE')
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/process_data/', methods=['POST', 'OPTIONS'])
@cross_origin()
def process_data():
    print(request)
    origin = request.headers.get('Origin')
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', "*")
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With,observe')
        response.headers.add('Access-Control-Allow-Methods',
                                'GET, POST, OPTIONS, PUT, PATCH, DELETE')
        return response, 200
    else:
        if request.is_json:
            data = request.json 
            if 'sql' in data:
                sql = data['sql']
                graphql = sql_to_graphql(sql)
                response = jsonify({'resultant_graphql': graphql})
                # response.headers.add('Access-Control-Allow-Credentials', 'true')
                # response.headers.add('Access-Control-Allow-Origin', "http://localhost:3000/")
                # if origin:
                #     response.headers.add('Access-Control-Allow-Origin', origin)
                return response, 200
            else:
                return jsonify({'error': 'Missing sql field in JSON data'}), 400
        else:
            return jsonify({'error': 'Request data is not in JSON format'}), 400
        
    # if request.method == "OPTIONS": 
    #     print("hi")
    #     return _build_cors_preflight_response()
    # elif request.method == "POST": 
    #     print("hello")
    #     if request.is_json:
    #         data = request.json 
    #         if 'sql' in data:
    #             sql = data['sql']
    #             graphql = sql_to_graphql(sql)
    #             response = {'resultant_graphql': graphql}
    #             return _corsify_actual_response(jsonify(response))
    #         else:
    #             return jsonify({'error': 'Missing sql field in JSON data'}), 400
    #     else:
    #         return jsonify({'error': 'Request data is not in JSON format'}), 400
    # else:
    #     raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))
    

# SELECT Customer.CustomerName, Customer.CustomerAge, Customer.Country, Customer.Phone FROM Customer WHERE Customer.CustomerAge = '21' ORDER BY Customer.Country DESC LIMIT 10; 
# CREATE TABLE Student (Roll_No. Int, First_Name Varchar(20), Last_Name Varchar(20), Age Int, Marks Int); 
# UPDATE ETCH002M SET MASKING_YB = 'N' WHERE MASKING_YB = 'Y';
if __name__ == '__main__':
    app.run(debug=True, port=4000)
            

            




