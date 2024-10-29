import json

# SELECT Customer.CustomerName, Customer.CustomerAge, Customer.Country, Customer.Phone
# FROM Customer
# WHERE Customer.CustomerAge = '21'
# ORDER BY Customer.Country DESC
# LIMIT 10;

def extract_select(select_data):
    select_items = {}
    column_alias_mapping = {}
    for i in range(len(select_data)):
        curr = select_data[i]
        cur = curr['value']
        t,c = cur.split('.')
        if(select_items.get(t) == None):
            select_items[t] = []
        select_items[t].append(c)
        if(curr['hasAs']):
            column_alias_mapping[curr['alias']] = curr['value']
    return select_items, column_alias_mapping


def extract_tables(table_data, tables, table_alias_mapping): 
    if table_data["type"] == "TableFactor":
        if(table_data["hasAs"]):
            table_alias_mapping[table_data["alias"]] = table_data["value"]["value"]
        tables.append(table_data["value"]["value"])
    if table_data["type"] == "TableReference":
        tables, table_alias_mapping = extract_tables(table_data["value"], tables, table_alias_mapping)
    return tables, table_alias_mapping

def extract_orderBy(order_data, query):
    if(order_data != None):
        field = order_data[0]["value"]["value"].split('.')
        sort_opt = order_data[0]["sortOpt"]
        direction = "ASC" if sort_opt is None else sort_opt.upper()
        if(query != ""):
            query += ", "
        query += "orderBy: { %s: %s }" % (field[1], direction)
    return query

def extract_limit(limit_data, query):
    if(limit_data != None):
        if(query != ""):
            query += ", "
        query += "limit: " + str(limit_data['value'])
    return query

# costPerUser: Number # matches all fields with exact value
# costPerUser_not: Number # matches all fields with different value
# costPerUser_in: [Number!] # matches all fields with value in the passed list
# costPerUser_not_in: [Number!] # matches all fields with value not in the passed list
# costPerUser_lt: Number # matches all fields with lesser value
# costPerUser_lte: Number # matches all fields with lesser or equal value
# costPerUser_gt: Number # matches all fields with greater value
# costPerUser_gte: Number # matches all fields with greater or equal value

def extract_where(where_data):
    conditions = {}
    if(where_data != None):
        m = {'=': "", '<': "lt", '>': "gt", "<=": "lte", ">=": "gte", "!=": "not"}
        if(where_data['type'] == "ComparisonBooleanPrimary"):
            t,c = where_data['left']['value'].split('.')
            if(conditions.get(t) == None):
                conditions[t] = []
            if(where_data['operator'] != '='):
                s = c + "_" + m[where_data['operator']] + ": "+  where_data['right']['value']
            else:
                s = c + ": "+  where_data['right']['value']
            conditions[t].append(s)
        elif(where_data['type'] == "InExpressionListPredicate"):
            t,c = where_data['left']['value'].split('.')
            if(conditions.get(t) == None):
                conditions[t] = []
            l = where_data['right']['value']
            l = [i['value'] for i in l]
            if(where_data['hasNot'] == None):
                s = c + "_in: " + l
            else:
                s = c + "_not_in: " + l
            conditions[t].append(s)    
    return conditions

def create_query(json_data, query_name = ""):
    if query_name == "":
        query = "query "
    else:
        query = "query {} ".format(query_name)
    json_data = json.loads(json_data)
    data = json_data['value']
    sent = ""
    sent = extract_orderBy(data['orderBy']['value'], sent)
    sent = extract_limit(data['limit'], sent)
    if(sent != "") :
        query += "(" + sent + ")"
    query += "{"
    select_items, column_alias_mapping = extract_select(data['selectItems']['value'])
    where_conditions = extract_where(data['where'])
    select_table = list(select_items.keys())
    for i in range(len(select_table)):
        if where_conditions.get(select_table[i]) != None:
            wc = where_conditions[select_table[i]]
            wcs = ""
            for x in range(len(wc)):
                wcs += " " + wc[x]
            ex = "(filter: {" + wcs + "})"
            query += "\n  "+ select_table[i] + ex + " {"
        else:
            query += "\n  "+ select_table[i] +" {"
        co = select_items[select_table[i]]
        for j in range(len(co)):
            if(j == len(co)-1):
                query += "\n        " + co[j]
            else:
                query += "\n        " + co[j] + ","
        if i == len(select_table)-1:
            query += "\n    }"
        else :
            query += "\n    },"
    table_data = data['from']['value']
    tables = []
    table_alias_mapping = {}
    for i in range(len(table_data)):
        tables, table_alias_mapping = extract_tables(table_data[i], tables, table_alias_mapping)
    query += "\n}"
    return query


# json_file =open('sample.json')
# json_str = json_file.read()
# json_data = json.loads(json_str)
# # print(json_data)
# res = create_query(json_data)
# print(res)

