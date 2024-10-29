const sqlParser = require('js-sql-parser');

function dql_to_json(query) {
    var ast = sqlParser.parse(query);
    return JSON.stringify(ast, null, 2);
};
