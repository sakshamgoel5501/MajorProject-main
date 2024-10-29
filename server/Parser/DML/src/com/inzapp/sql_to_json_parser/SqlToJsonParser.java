package com.inzapp.sql_to_json_parser;

import com.inzapp.sql_to_json_parser.config.Config;
import com.inzapp.sql_to_json_parser.core.Parser;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.FileReader;

public class SqlToJsonParser {
    /**
     * main method
     * used for executable jar
     *
     * @param args [0] : specified input file name
     *             [1] : specified output file name
     */
    public static void main(String[] args) {
        String inputFileName = Config.INPUT_FILE_NAME;
        String outputFileName = Config.OUTPUT_FILE_NAME;
        if (args != null && args.length == 2) {
            inputFileName = args[0];
            outputFileName = args[1];
        }

        SqlToJsonParser sqlToJsonParser = new SqlToJsonParser();
        Parser parser = new Parser();
        try {
            String sql = sqlToJsonParser.readSqlFromFile(inputFileName);
            if (sql == null)
                throw new Exception("input file does not exist");

            JSONObject json = parser.parse(sql);
            if (json == null)
                throw new Exception("sql syntax error");

            String jsonString = json.toString(4);
            System.out.println("input sql\n\n" + sql);
            System.out.println("output json\n\n" + jsonString);

            sqlToJsonParser.saveFile(jsonString, outputFileName);
            System.out.println("parse success");
        } catch (Exception e) {
            sqlToJsonParser.saveFile(Config.SQL_SYNTAX_ERROR, outputFileName);
            System.out.println(e.getMessage());
        }
    }

    /**
     * used for java code
     *
     * @param sql raw sql query
     * @return parsed json string
     * return null if exception was caught
     */
    public String parse(String sql) {
        try {
            return new Parser().parse(sql).toString(4);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * read sql from com.inzapp.SqlToJsonParser.config.Config.INPUT_FILE_NAME
     * used for executable jar
     *
     * @param fileName main methods first args, user specified input file name
     * @return sql from file
     * return null if not exist file
     */
    private String readSqlFromFile(String fileName) {
        try {
            BufferedReader br = new BufferedReader(new FileReader(fileName));
            StringBuilder sb = new StringBuilder();
            while (true) {
                String line = br.readLine();
                if (line == null)
                    break;
                sb.append(line.trim()).append("\n");
            }
            return sb.toString();
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * save json string as specified file name
     *
     * @param jsonString org.json.JSONObject().toString()
     *                   parsed json object
     * @param fileName   main methods second args, user specified output file name
     */
    private void saveFile(String jsonString, String fileName) {
        try {
            FileOutputStream fos = new FileOutputStream(fileName);
            fos.write(jsonString.getBytes());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}