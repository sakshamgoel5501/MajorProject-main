from subprocess import PIPE, Popen
import os
import json
def dml_parser(query):
    if os.path.exists("input.txt"):
        os.remove("input.txt")
    else:
        print("File does not exists. File needs to be created.")

    f = open("input.txt", "w+")
    f.write(f"{query}")


    f.close()
    process = Popen(['java', '-jar', 'sql-to-json-parser.jar', 'input.txt', 'output.json'], stdout=PIPE, stderr=PIPE)
    result = process.communicate()
    print(result[0].decode('utf-8'))
    f = open('output.json')
    data = json.load(f)
    return data

dml_parser("UPDATE employees SET salary = 5000 , last_name = 'Doe' , first_name = 'John' WHERE employee_id = 1000")
print(dml_parser("UPDATE employees SET salary = 5000 , last_name = 'Doe' , first_name = 'John' WHERE employee_id = 1000"))