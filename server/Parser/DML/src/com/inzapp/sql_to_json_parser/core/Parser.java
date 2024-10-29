package com.inzapp.sql_to_json_parser.core;

import com.inzapp.sql_to_json_parser.config.JsonKey;
import com.inzapp.sql_to_json_parser.core.json.JsonManager;
import net.sf.jsqlparser.expression.Alias;
import net.sf.jsqlparser.expression.Expression;
import net.sf.jsqlparser.expression.ExpressionVisitorAdapter;
import net.sf.jsqlparser.expression.operators.relational.ExpressionList;
import net.sf.jsqlparser.parser.CCJSqlParserUtil;
import net.sf.jsqlparser.schema.Column;
import net.sf.jsqlparser.schema.Table;
import net.sf.jsqlparser.statement.Statement;
import net.sf.jsqlparser.statement.StatementVisitorAdapter;
import net.sf.jsqlparser.statement.delete.Delete;
import net.sf.jsqlparser.statement.insert.Insert;
import net.sf.jsqlparser.statement.select.*;
import net.sf.jsqlparser.statement.update.Update;
import org.json.JSONObject;

import java.util.List;

public class Parser extends JsonManager {
    /**
     * parse sql string to org.json.JSONObject
     *
     * @param sql read from file in com.inzapp.sqlToJsonParser.SqlToJsonParser.readFromFile()
     * @return org.json.JSONObject()
     * converted json object
     * return null if conversion failed
     */
    public JSONObject parse(String sql) {
        try {
            Statement statement = CCJSqlParserUtil.parse(sql);
            statement.accept(statementVisitor);
            return this.json;
        } catch (Exception e) {
            // sql parse failure
            e.printStackTrace();
            return null;
        }
    }

    private final StatementVisitorAdapter statementVisitor = new StatementVisitorAdapter() {
        /**
         * insert
         * @param insert visitor event listened
         */
        @Override
        public void visit(Insert insert) {
            // crud
            putToJson(JsonKey.CRUD, JsonKey.INSERT);

            // table
            Table table = insert.getTable();
            if (table != null) {
                putToJson(JsonKey.FROM, table.toString());
                table.accept(fromItemVisitor);
            }

            // columns
            List<Column> columns = insert.getColumns();
            if (columns != null)
                columns.forEach(column -> column.accept(expressionVisitor));

            // values
            List<Expression> expressions = ((ExpressionList) insert.getItemsList()).getExpressions();
            if (expressions != null)
                expressions.forEach(expression -> putToJson(JsonKey.VALUE, expression.toString()));

            super.visit(insert);
        }

        /**
         * select
         * @param select visitor event listened
         */
        @Override
        public void visit(Select select) {
            // crud
            putToJson(JsonKey.CRUD, JsonKey.SELECT);
            select.getSelectBody().accept(selectVisitorAdapter);
            super.visit(select);
        }

        /**
         * update
         * @param update visitor event listened
         */
        @Override
        public void visit(Update update) {
            // crud
            putToJson(JsonKey.CRUD, JsonKey.UPDATE);

            // columns
            List<Column> columns = update.getColumns();
            if (columns != null)
                columns.forEach(column -> column.accept(expressionVisitor));

            // tables
            List<Table> tables = update.getTables();
            if (tables != null) {
                tables.forEach(table -> putToJson(JsonKey.FROM, table.toString()));
                tables.forEach(table -> table.accept(fromItemVisitor));
            }

            // values
            List<Expression> expressions = update.getExpressions();
            if (expressions != null)
                expressions.forEach(expression -> putToJson(JsonKey.VALUE, expression.toString()));

            // where
            Expression whereExpression = update.getWhere();
            if (whereExpression != null)
                putToJson(JsonKey.WHERE, whereExpression.toString());

            super.visit(update);
        }

        /**
         * delete
         * @param delete visitor event listened
         */
        @Override
        public void visit(Delete delete) {
            // crud
            putToJson(JsonKey.CRUD, JsonKey.DELETE);

            // table
            Table table = delete.getTable();
            if (table != null) {
                putToJson(JsonKey.FROM, table.toString());
                table.accept(fromItemVisitor);
            }

            // where
            Expression whereExpression = delete.getWhere();
            if (whereExpression != null) {
                putToJson(JsonKey.WHERE, whereExpression.toString());
                whereExpression.accept(whereExpressionVisitor);
            }

            super.visit(delete);
        }
    };

    private final SelectVisitorAdapter selectVisitorAdapter = new SelectVisitorAdapter() {
        /**
         * most select query is processed as plain select
         * @param plainSelect visitor event listened
         */
        @Override
        public void visit(PlainSelect plainSelect) {
            // distinct
            Distinct distinct = plainSelect.getDistinct();
            if (distinct != null)
                putToJson(JsonKey.DISTINCT, "TRUE");

            // column
            List<SelectItem> selectItems = plainSelect.getSelectItems();
            if (selectItems != null)
                selectItems.forEach(selectItem -> putToJson(JsonKey.COLUMN, selectItem.toString()));

            // table
            FromItem fromItem = plainSelect.getFromItem();
            if (fromItem != null) {
                putToJson(JsonKey.FROM, fromItem.toString());
                Alias alias = fromItem.getAlias();
                if (alias != null) {
                    String aliasName = alias.getName();
                    putToJson(JsonKey.FROM_ALIAS, aliasName);

                    // remove table alias from table query
                    fromItem.getAlias().setUseAs(false);
                    fromItem.setAlias(null);
                }
                fromItem.accept(fromItemVisitor);
            }

            // where
            Expression whereExpression = plainSelect.getWhere();
            if (whereExpression != null) {
                putToJson(JsonKey.WHERE, whereExpression.toString());
                whereExpression.accept(whereExpressionVisitor);
            }

            // group by
            GroupByElement groupByElement = plainSelect.getGroupBy();
            if (groupByElement != null)
                groupByElement.accept(groupByVisitor);

            // order by
            List<OrderByElement> orderByElements = plainSelect.getOrderByElements();
            if (orderByElements != null)
                orderByElements.forEach(orderByElement -> orderByElement.accept(orderByVisitor));

            // joins
            List<Join> joins = plainSelect.getJoins();
            if (joins != null) {
                joins.forEach(join -> {
                    putToJson(JsonKey.JOIN, 1, join.toString());
                    Alias joinAlias = join.getRightItem().getAlias();
                    if (joinAlias != null) {
                        String joinAliasName = joinAlias.getName();
                        putToJson(JsonKey.JOIN_ALIAS, 1, joinAliasName);

                        // remove join alias in join query
                        joinAlias.setUseAs(false);
                        join.getRightItem().setAlias(null);
                    }
                });
            }
        }

        /**
         * select including union(and etc...)
         * @param setOperationList visitor event listened
         */
        @Override
        public void visit(SetOperationList setOperationList) {
            // union
            List<SelectBody> selectBodies = setOperationList.getSelects();
            List<SetOperation> setOperations = setOperationList.getOperations();

            for (int i = 0; i < selectBodies.size(); ++i) {
                if (i == 0)
                    injectJson(new Parser().parse(selectBodies.get(i).toString()));

                if (i < setOperations.size()) {
                    String setOperationKey = String.format("%s %d", setOperations.get(i), i + 1); // ex) UNION 1, UNION ALL 1 ...
                    String setOperationAnalyseKey = String.format("%s %d", setOperations.get(i) + " ANALYSE", i + 1); // ex) UNION ANALYSE 1, UNION ALL ANALYSE 1 ...
                    putToJson(setOperationKey, selectBodies.get(i + 1).toString());
                    putToJson(setOperationAnalyseKey, new Parser().parse(selectBodies.get(i + 1).toString()));
                } else break;
            }
        }
    };

    private final FromItemVisitorAdapter fromItemVisitor = new FromItemVisitorAdapter() {
        /**
         * search sub query in from statement
         * @param subSelect visitor event listened
         */
        @Override
        public void visit(SubSelect subSelect) {
            putToJson(JsonKey.FROM_SUB_QUERY, 1, subSelect.toString());
            putToJson(JsonKey.FROM_SUB_QUERY_ANALYSE, 1, new Parser().parse(subSelect.toString()));
            super.visit(subSelect);
        }

        // do not override table visit method
    };

    private final ExpressionVisitorAdapter expressionVisitor = new ExpressionVisitorAdapter() {
        /**
         * search sub query in where statement
         * @param subSelect visitor event listened
         */
        @Override
        public void visit(SubSelect subSelect) {
            putToJson(JsonKey.WHERE_SUB_QUERY, 1, subSelect.toString());
            putToJson(JsonKey.WHERE_SUB_QUERY_ANALYSE, 1, new Parser().parse(subSelect.toString()));
            super.visit(subSelect);
        }

        /**
         * column for select, set
         * @param column visitor event listened
         */
        @Override
        public void visit(Column column) {
            putToJson(JsonKey.COLUMN, column.toString());
            super.visit(column);
        }
    };

    private final ExpressionVisitorAdapter whereExpressionVisitor = new ExpressionVisitorAdapter() {
        /**
         * used for only where expression (need no where column)
         * @param subSelect visitor event listened
         */
        @Override
        public void visit(SubSelect subSelect) {
            putToJson(JsonKey.WHERE_SUB_QUERY, 1, subSelect.toString());
            putToJson(JsonKey.WHERE_SUB_QUERY_ANALYSE, 1, new Parser().parse(subSelect.toString()));
            super.visit(subSelect);
        }

        // do not override column visit method here
    };

    private GroupByVisitor groupByVisitor = new GroupByVisitor() {
        /**
         * search group by
         * @param groupByElement visitor event listened
         */
        @Override
        public void visit(GroupByElement groupByElement) {
            List<Expression> groupByExpressions = groupByElement.getGroupByExpressions();
            groupByExpressions.forEach(groupByExpression -> {
                // warning for duplicating json key
                putToJson(JsonKey.GROUP_BY, groupByExpression.toString());
            });

        }
    };

    private final OrderByVisitorAdapter orderByVisitor = new OrderByVisitorAdapter() {
        /**
         * search order by
         * @param orderBy visitor event listened
         */
        @Override
        public void visit(OrderByElement orderBy) {
            putToJson(JsonKey.ORDER_BY, orderBy.toString());
            super.visit(orderBy);
        }
    };
}