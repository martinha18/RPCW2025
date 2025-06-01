import React, {useEffect, useMemo, useRef} from 'react';
import './association.css';

const nodeRadius = 6;

export function Association({question, readOnly = false, onChangeAnswers}) {
    const canvasRef = useRef();

    const leftItems = useMemo(() => [...question.options], [question]);
    const rightItems = useMemo(() => [...question.options2], [question]);

    const mapEdgesToItems = (edges, leftNodes, rightNodes) => {
        return edges.map(([start, end]) => {
            const leftIndex = leftNodes.findIndex(n => n.x === start.x && n.y === start.y);
            const rightIndex = rightNodes.findIndex(n => n.x === end.x && n.y === end.y);
            return [leftIndex, rightIndex];
        });
    };

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        canvas.width = 200;
        canvas.height = 100;

        const rowHeight = canvas.height / leftItems.length;
        const margin = nodeRadius * 6;

        const leftNodes = leftItems.map((_, i) => ({x: margin, y: i * rowHeight + rowHeight / 2}));
        const rightNodes = rightItems.map((_, i) => ({x: canvas.width - margin, y: i * rowHeight + rowHeight / 2}));
        const nodes = [...leftNodes, ...rightNodes];

        const edges = [];

        let activeNode = null;
        let mouse = null;
        let isDragging = false;

        const equalsNode = (a, b) => a && b && a.x === b.x && a.y === b.y;
        const sameVertical = (a, b) => a && b && a.x === b.x;

        const findClosestNode = (pos, threshold = nodeRadius) =>
            nodes.find(n => Math.abs(pos.x - n.x) < threshold && Math.abs(pos.y - n.y) < threshold);

        const addEdge = (edge) => {
            const [start, end] = edge;

            for (let i = edges.length - 1; i >= 0; i--) {
                if (
                    equalsNode(edges[i][0], start) ||
                    equalsNode(edges[i][1], end) ||
                    equalsNode(edges[i][1], start) ||
                    equalsNode(edges[i][0], end)
                ) {
                    edges.splice(i, 1);
                }
            }

            edges.push(edge);

            if (edges.length === leftItems.length) {
                const readableEdges = mapEdgesToItems(edges, leftNodes, rightNodes, leftItems, rightItems);
                const ans = readableEdges.sort((a,b)  => a[0] - b[0]).map(a => a[1]).join('/');
                onChangeAnswers(ans);
            }
        };

        const getPointerPos = (e) => {
            const rect = canvas.getBoundingClientRect();
            const point = e.touches?.[0] || e.changedTouches?.[0] || e;
            return {x: point.clientX - rect.left, y: point.clientY - rect.top};
        };

        const handleStart = (e) => {
            e.preventDefault?.();
            mouse = getPointerPos(e);
            activeNode = findClosestNode(mouse);
            isDragging = true;
        };

        const handleMove = (e) => {
            e.preventDefault?.();
            mouse = getPointerPos(e);
        };

        const handleEnd = (e) => {
            e.preventDefault?.();
            isDragging = false;
            mouse = getPointerPos(e);
            const targetNode = findClosestNode(mouse, nodeRadius * 1.5);

            if (
                activeNode &&
                targetNode &&
                !equalsNode(activeNode, targetNode) &&
                !sameVertical(activeNode, targetNode)
            ) {
                const edge = [activeNode, targetNode].sort((a, b) => a.x - b.x);
                addEdge(edge);
            }

            activeNode = null;
        };

        if (readOnly && question.answer) {
            const answerArray = question.answer.split('/').map(Number);

            for (let leftIndex = 0; leftIndex < answerArray.length; leftIndex++) {
                const rightIndex = answerArray[leftIndex];

                const start = leftNodes[leftIndex];
                const end = rightNodes[rightIndex];

                if (start && end) {
                    const edge = [start, end].sort((a, b) => a.x - b.x);
                    edges.push(edge);
                }
            }
        }

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            for (const [start, end] of edges) {
                ctx.beginPath();
                ctx.lineWidth = 2;
                ctx.strokeStyle = 'black';
                ctx.moveTo(start.x, start.y);
                ctx.lineTo(end.x, end.y);
                ctx.stroke();
            }

            for (const node of nodes) {
                ctx.beginPath();
                ctx.arc(node.x, node.y, nodeRadius, 0, Math.PI * 2);
                ctx.fillStyle = equalsNode(node, activeNode) ? 'black' : 'darkgrey';
                ctx.fill();
            }

            if (isDragging && activeNode && mouse) {
                ctx.beginPath();
                ctx.setLineDash([5, 5]);
                ctx.strokeStyle = 'red';
                ctx.moveTo(activeNode.x, activeNode.y);
                ctx.lineTo(mouse.x, mouse.y);
                ctx.stroke();
                ctx.setLineDash([]);
            }

            requestAnimationFrame(animate);
        };

        if (!readOnly) {
            canvas.addEventListener('mousedown', handleStart);
            canvas.addEventListener('mousemove', handleMove);
            canvas.addEventListener('mouseup', handleEnd);

            canvas.addEventListener('touchstart', handleStart, {passive: false});
            canvas.addEventListener('touchmove', handleMove, {passive: false});
            canvas.addEventListener('touchend', handleEnd, {passive: false});
        }

        animate();

        return () => {
            canvas.removeEventListener('mousedown', handleStart);
            canvas.removeEventListener('mousemove', handleMove);
            canvas.removeEventListener('mouseup', handleEnd);

            canvas.removeEventListener('touchstart', handleStart);
            canvas.removeEventListener('touchmove', handleMove);
            canvas.removeEventListener('touchend', handleEnd);
        };
    }, [leftItems, rightItems, canvasRef, readOnly]);

    return (
        <div className="as-root">
            <div className="as-column">
                {leftItems.map((item, i) => (
                    <div key={`left-${i}`}>
                        {item}
                    </div>
                ))}
            </div>

            <canvas ref={canvasRef} className="as-lines"/>

            <div className="as-column">
                {rightItems.map((item, i) => (
                    <div key={`right-${i}`}>
                        {item}
                    </div>
                ))}
            </div>
        </div>
    );
}
