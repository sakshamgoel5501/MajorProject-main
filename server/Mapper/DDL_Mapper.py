# parser_input={'Customer': [{'name': 'CustomerID', 'data_type': 'Int', 'not_null': False}, {'name': 'CustomerName', 'data_type': 'String', 'not_null': True}, {'name': 'LastName', 'data_type': 'String', 'not_null': False}, {'name': 'Country', 'data_type': 'String', 'not_null': False}, {'name': 'Age', 'data_type': 'Int', 'not_null': False}, {'name': 'Phone', 'data_type': 'Int', 'not_null': False}, {'foreign_key': 'PersonID', 'reference_table': 'Persons', 'reference_key': 'PersonID'}], 'Student_Details': [{'name': 'Roll_No.', 'data_type': 'Int', 'not_null': False}, {'name': 'First_Name', 'data_type': 'String', 'not_null': False}, {'name': 'Last_Name', 'data_type': 'String', 'not_null': False}, {'name': 'Age', 'data_type': 'String', 'not_null': False}, {'name': 'Marks', 'data_type': 'Int', 'not_null': False}, {'name': 'a', 'data_type': 'Int', 'not_null': False}, {'name': 'b', 'data_type': 'String', 'not_null': False}, {'name': 'c', 'data_type': 'String', 'not_null': False}]}

def generate_schema(parser_input):
    s=''
    for key in parser_input.keys():
        
        s=s+ (f"type {key} \n")
        s=s+ ('{\n')
        #print(f"type {key} ")
        #print("{")
        for attribute in parser_input[key]:
            for curr in attribute.keys():
                if curr=='name' and attribute['not_null'] :
                    #print(f"\t{attribute[curr]} : {attribute['data_type']} !")
                    s=s+ (f"\t{attribute[curr]} : {attribute['data_type']} !\n")
                    break
                elif curr=='name' and not attribute['not_null'] :
                    #print(f"\t{attribute[curr]} : {attribute['data_type']}")
                    s=s+ (f"\t{attribute[curr]} : {attribute['data_type']}\n")
                    break
        #print("} \n")
        s=s+ ("}\n")
    return s
# a=generate_schema(parser_input)
# print(a)

