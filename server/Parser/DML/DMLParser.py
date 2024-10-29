from subprocess import PIPE, Popen
import json

def dml_parser(query_txt):
    with open("Parser/DML/input.txt", "w") as text_file:
        text_file.write(query_txt)
    process = Popen(['java', '-jar', 'sql-to-json-parser.jar', 'Parser/DML/input.txt', 'Parser/DML/output.json'], stdout=PIPE, stderr=PIPE)
    process.communicate()
    json_file =open('Parser/DML/output.json')
    json_str = json_file.read()
    json_data = json.loads(json_str)
    return json_data
    # print(result[0].decode('utf-8'))