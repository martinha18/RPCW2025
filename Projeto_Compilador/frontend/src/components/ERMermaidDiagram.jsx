import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({ startOnLoad: false });

function ERMermaidDiagram({ diagram, clickMatch, onClick }) {
    const diagramRef = useRef(null);

    useEffect(() => {
        if (!diagramRef.current || !diagram) return;

        diagramRef.current.innerHTML = `<div class="mermaid">${diagram}</div>`;

        mermaid.run().then(() => {
            const svg = diagramRef.current.querySelector('svg');
            const nodes = svg.querySelectorAll('g[id^="entity-"]');

            nodes.forEach(node => {
                const id = node.id;
                const parts = id.split('-');
                const className = parts[1];

                if (!clickMatch.includes(className)) return;

                node.style.cursor = 'pointer';
                node.addEventListener('click', () => onClick(className));
            });
        });
    }, [diagram, clickMatch, onClick]);

    return (
        <div ref={diagramRef} style={{
            margin: '20px auto',
            border: '1px solid #ccc',
            padding: '10px'
        }}>
            Loading diagram...
        </div>
    );
}

export default ERMermaidDiagram;
