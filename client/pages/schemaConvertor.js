import { useRef, useState } from 'react'
import Editor from "@monaco-editor/react"
import styles from '@/styles/Editor.module.css'
import PlayCircleIcon from '@mui/icons-material/PlayCircle';

export default function Home() {
    const editorRef = useRef(null);
    var result;
    const url = "http://127.0.0.1:4000/process_data/";
    const [graphQL_default, set_graphQL_default] = useState("Converted GraphQL Schema will be shown here");

    function handleEditorDidMount(editor, monaco) {
        editorRef.current = editor;
    }

    async function getEditorValue() {
        await fetch(url, {
            method: "POST",
            mode: "cors",
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "http://127.0.0.1:4000",
                'Access-Control-Allow-Credentials': 'true'
            },
            body: JSON.stringify({ sql: editorRef.current.getValue() }),
        })
        .then((response) => response = response.json())
        .then((response) => result = response["resultant_graphql"])
        // graphQL_default = response.json()
        console.log(result);
        set_graphQL_default(result);
        // return graphQL_default;
        // alert(editorRef.current.getValue());
    }

    return (
        <main>
            <div className={styles.main}>
                <div className={styles.sql}>
                    <Editor
                        theme="vs-dark"
                        onMount={handleEditorDidMount}
                        defaultLanguage="sql"
                        defaultValue="CREATE TABLE Student (Roll_No. Int, First_Name Varchar(20), Last_Name Varchar(20), Age Int, Marks Int);"
                        autoClosingBrackets="always"
                        autoIndent="always"
                    />
                </div>

                <PlayCircleIcon className={styles.runButton} onClick={() => getEditorValue()} style={{ fontSize: '72px' }} />

                <div className={styles.graphQL}>
                    <Editor
                        theme="vs-dark"
                        defaultLanguage="graphQL"
                        // defaultValue="Converted GraphQL Schema will be shown here"
                        value={graphQL_default}
                        autoClosingBrackets="always"
                        autoIndent="always"
                        readOnly="true"
                    />
                </div>
            </div>
        </main>
    )
}















