import re

clauses = ["CREATE TABLE", "DROP TABLE", "ALTER TABLE", "RENAME TABLE", "TRUNCATE TABLE"]
data_type = {'varchar': 'String', 'text': 'String', 'char': 'String', 'datetime': 'String', 'decimal': 'Float', 'float': 'Float', 'int': 'Int', 'bigint': 'Int', 'numeric': 'Int', 'real': 'Int', 'tinyint': 'Boolean'}
alter = ['ADD', 'DROP', 'RENAME', 'MODIFY']

def perform_clause(prev_clause, prev_table, tables, q):
    if prev_clause == "CREATE TABLE":
        tables[prev_table] = []
    elif prev_clause == "DROP TABLE":
        try:
            del tables[prev_table]
        except:
            print("Table not found")
    elif prev_clause == "TRUNCATE TABLE":
        try:
            tables[prev_table] = []
        except:
            print("Table not found")
    elif prev_clause == "RENAME TABLE":
        try:
            res = tables[prev_table]
            if q[4][-1] == ";":
                q[4] = q[4][:-1]
            tables[q[4]] = res
            del tables[prev_table]
        except:
            print("Table not found or Invalid syntax")
    elif prev_clause == "ALTER TABLE":
        try:
            res = tables[prev_table]
        except:
            print("Table not found")

def check_not_null(s):
    for i in range(len(s)-1):
        if (s[i].upper() == "NOT" and s[i+1].upper() == "NULL"):
            return True
    return False

def get_datatype(s):
    s = s.split('(')[0]
    s = s.split(')')[0]
    s = s.split(';')[0]
    s = s.lower()
    return s

def check_foreign_key(s):
    fr = r"FOREIGN KEY\s+\w+ REFERENCES \w+\(\w+"
    s = ' '.join(s)
    v = re.findall(fr, s, re.DOTALL)
    if v != []:
        l = v[0].split()
        f = l[2]
        rt, rk = l[4].split('(')
        return [f, rt, rk]
    return None

def checkKey(dic, key): 
    if key in dic:
        return True
    else:
        return False

def perform_operation(prev_clause, prev_table, prev_alter, tables, s):
    if prev_clause == "CREATE TABLE":
        fk = check_foreign_key(s)
        if fk == None:
            tables[prev_table].append({'name': s[0], 'data_type': data_type[get_datatype(s[1])], 'not_null': check_not_null(s)})
        else:
            tables[prev_table].append({'foreign_key': fk[0], 'reference_table': fk[1], 'reference_key': fk[2]})
    elif prev_clause == "ALTER TABLE":
        curr_alter = ""
        if s[0].upper() in alter:
            curr_alter = s[0].upper()
            i = 1
        else:
            curr_alter = prev_alter
            i=0
        if curr_alter == "ADD":
            fk = check_foreign_key(s)
            if fk == None:
                tables[prev_table].append({'name': s[i], 'data_type': data_type[get_datatype(s[i+1])], 'not_null': check_not_null(s)})
            else:
                tables[prev_table].append({'foreign_key': fk[0], 'reference_table': fk[1], 'reference_key': fk[2]})
            return "ADD"
        elif curr_alter == "DROP":
            l = tables[prev_table]
            l = [id for id in l if checkKey(id, 'name') and (not id['name'] == s[i])]
            tables[prev_table] = l
            return "DROP"
        elif curr_alter == "RENAME":
            l = tables[prev_table]
            for id in l:
                if checkKey(id, 'name') and id['name'] == s[i]:
                    d = id['data_type']
                    nn = id['not_null']
                    break
            l = [id for id in l if checkKey(id, 'name') and (not id['name'] == s[i])]
            l.append({'name': s[i+2], 'data_type': d, 'not_null': nn})
            tables[prev_table] = l
            return "RENAME"
        elif curr_alter == "MODIFY":
            l = tables[prev_table]
            for id in l:
                if checkKey(id, 'name') and id['name'] == s[i]:
                    id['data_type'] = data_type[get_datatype(s[i+1])]
                    break
            return "MODIFY"

def ddl_parser(query_text):
    
    query_list = query_text.split('\n') 

    prev_clause = ""
    prev_table = ""
    prev_alter = ""

    tables = {}

    for query in query_list:
        if(query == "(" or query == ""):
            continue
        elif(query == ");" or query == ")" or query ==";"):
            prev_clause = ""
            prev_table = ""
            continue
        else:
            query = query.strip()
            q = query.split()
            fs = q[0].upper() + " " + q[1].upper()
            
            if fs in clauses:
                prev_clause = fs
                idk = q[2].split("(")
                if len(idk) > 1:
                    prev_table = idk[0]
                    if(idk[1] != ""):
                        q.insert(3, idk[1])
                elif q[2][-1] == ';':
                    prev_table = q[2][:-1]
                else:
                    prev_table = q[2]
                perform_clause(prev_clause, prev_table, tables, q)
                i = 3
            else:
                i = 0
            while(i < len(q)):
                if(q[i] == "("):
                    i += 1
                    continue
                elif(q[i] == ");" or q[i] == ")" or q[i] ==";"):
                    prev_clause = ""
                    prev_table = ""
                    i += 1
                    continue
                else:
                    s = []
                    while(i < len(q) and len(q[i].split(',')) == 1):
                        idk = q[i]
                        if q[i][0] == "(":
                            q[i] = q[i][1:]
                        if q[i][-1] == ";" or q[i][-1] == ")":
                            q[i] = q[i][:-1]
                        s.append(q[i])
                        i = i+1 
                    if(i<len(q) and len(q[i].split(',')) > 1):
                        if q[i][0] == "(":
                            q[i] = q[i][1:]
                        if q[i][-1] == ";" or q[i][-1] == ")":
                            q[i] = q[i][:-1]
                        x = q[i].split(',')
                        if(x[0] == ""):
                            s.append(x[1])
                        else:
                            s.append(x[0])
                    prev_alter = perform_operation(prev_clause, prev_table, prev_alter, tables, s)
                    i += 1    

    return tables   
                

# query_text = """
# CREATE TABLE Customer (
#     CustomerID INT PRIMARY KEY,
#     CustomerName VARCHAR(50) NOT NULL,
#     LastName VARCHAR(50),
#     Country VARCHAR(50),
#     Age int(2),
#     Phone int(10),
#     FOREIGN KEY (PersonID) REFERENCES Persons(PersonID)
# );
# query_text = """CREATE TABLE Student(Roll_No. Int, First_Name Varchar(20), Last_Name Varchar(20), Age Int, Marks Int);"""

# ALTER TABLE Student ADD a Int, b Varchar, c char;
# ALTER TABLE Student MODIFY Age Varchar;
# RENAME TABLE Student TO Student_Details;
# DROP TABLE Student_Detail;   
# """
# tables = ddl_parser(query_text)
# print(tables)


