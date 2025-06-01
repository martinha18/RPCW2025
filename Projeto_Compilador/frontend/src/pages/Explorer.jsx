import React, {useCallback, useEffect, useMemo, useState} from 'react';
import mermaid from 'mermaid';
import Editor from '@monaco-editor/react';
import {useParams} from "react-router-dom";
import ERMermaidDiagram from "../components/ERMermaidDiagram.jsx";

mermaid.initialize({startOnLoad: false});

function Explorer() {
    const {ont} = useParams();

    const [data, setData] = useState(null);
    const [editorValue, setEditorValue] = useState('# Write GraphQL query here');
    const [results, setResults] = useState([]);

    const diagram = useMemo(() => generateMermaidER(data), [data]);
    const matches = useMemo(() => data ? Array.from(data.classes.map(c => c.class)) : [], [data]);

    useEffect(() => {
        fetch(`/api/${ont}/shape`)
            .then(res => res.json())
            .then(setData);
    }, []);

    const handleDiagramClick = useCallback((className) => {
        const ps = Array.from(data.data_properties.filter(obj => obj.domain === className).map(obj => obj.property));
        const sampleQuery = `SELECT ${ps.map(p => '?' + p).join(' ')} WHERE {
    ?entity a :${className} .
    ${ps.map(p => `OPTIONAL { ?entity :${p} ?${p} . }`).join('\n    ')}
}
LIMIT 100`;
        setEditorValue(sampleQuery);
    }, [data]);

    const handleRunQuery = async () => {
        const res = await fetch(`/api/${ont}/query`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: editorValue})
        });
        const json = await res.json();
        setResults(json);
    };

    const isRef = (s) => s.startsWith(':');
    const queryIfRef = (s) => {
        if (isRef(s)) {
            setEditorValue(`SELECT * WHERE {
  { ${s} ?p ?o }
  UNION
  { ?s ${s} ?o }
  UNION
  { ?s ?p ${s} }
}
LIMIT 100`);
        }
    }

    const allKeys = useMemo(() => {
        const keys = new Set();
        results.forEach(row => {
            Object.keys(row).forEach(key => keys.add(key));
        });
        return Array.from(keys);
    }, [results]);

    return <div style={{maxWidth: '90%', margin: 'auto'}}>
        <ERMermaidDiagram diagram={diagram} clickMatch={matches} onClick={handleDiagramClick}/>

        <h3>GraphQL Editor</h3>
        <Editor
            height="300px"
            defaultLanguage="graphql"
            value={editorValue}
            onChange={(value) => setEditorValue(value || '')}
        />

        <button onClick={handleRunQuery} style={{marginTop: '10px'}}>
            Run
        </button>

        {results.length > 0 && (
            <table border="1" style={{marginTop: '20px', width: '100%', borderCollapse: 'collapse'}}>
                <thead>
                <tr>
                    {allKeys.map(key => (
                        <th key={key} style={{ padding: '5px' }}>{key}</th>
                    ))}
                </tr>
                </thead>
                <tbody>
                {results.map((row, i) => (
                    <tr key={i}>
                        {allKeys.map((key, j) => {
                            const val = row[key] ?? '--';
                            return (
                                <td
                                    key={j}
                                    style={{
                                        padding: '5px',
                                        color: isRef(val) ? 'blue' : 'inherit'
                                    }}
                                    onClick={() => queryIfRef(val)}
                                >
                                    {String(val)}
                                </td>
                            );
                        })}
                    </tr>
                ))}
                </tbody>
            </table>
        )}
    </div>;
}

function generateMermaidER(data) {
    if (!data) return '';

    const dataPropsMap = data.data_properties.reduce((acc, {domain, property}) => {
        acc[domain] = acc[domain] || [];
        if (!acc[domain].includes(property)) acc[domain].push(property);
        return acc;
    }, {});

    const dataPropsRangeMap = data.data_properties.reduce((acc, {property, range}) => {
        acc[property] = acc[property] || [];
        if (!range) {
            range = 'string'
        } else {
            const parts = range.split(/[#/]/);
            range = parts[parts.length - 1];
        }
        if (!acc[property].includes(range)) acc[property].push(range);
        return acc;
    }, {});

    let output = 'erDiagram\n';

    data.classes.forEach(({class: cls}) => {
        output += `    ${cls} {\n`;
        const props = dataPropsMap[cls] || [];
        props.forEach(p => {
            output += `        ${dataPropsRangeMap[p][0]} ${p}\n`;
        });
        output += `    }\n`;
    });

    data.classes_inheritance.forEach(({subClass, superClass}) => {
        output += `    ${subClass} }|..|{ ${superClass} : is_a\n`;
    });

    data.object_properties.forEach(({domain, property, range}) => {
        output += `    ${domain} ||--o{ ${range} : ${property}\n`;
    });

    return output;
}

export default Explorer;
