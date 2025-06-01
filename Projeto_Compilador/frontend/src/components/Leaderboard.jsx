import React, {useMemo} from "react";

export function Leaderboard({leaderBoard, onContinue}) {
    const sortedLeaderBoard = useMemo(() => {
        return Object.entries(leaderBoard)
            .sort((a, b) => b[1].score - a[1].score)
            .map(([player, info], index) => ({
                rank: index + 1,
                username: info.username,
                score: info.score,
            }));
    }, [leaderBoard]);

    const downloadCSV = () => {
        const csvRows = [];
        csvRows.push(["Lugar", "Jogador", "Pontuação"]);

        sortedLeaderBoard.forEach(({rank, username, score}) => {
            csvRows.push([rank, username, score]);
        });

        const csvString = csvRows.map(row => row.join(";")).join("\n");

        const blob = new Blob([csvString], {type: "text/csv"});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "leaderboard.csv";
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div>
            <h2>Resultados</h2>
            <table>
                <thead>
                <tr>
                    <th>Lugar</th>
                    <th>Jogador</th>
                    <th>Pontuação</th>
                </tr>
                </thead>
                <tbody>
                {sortedLeaderBoard.map(({rank, username, score}) => (
                    <tr key={username}>
                        <td>{rank}</td>
                        <td>{username}</td>
                        <td>{score}</td>
                    </tr>
                ))}
                </tbody>
            </table>
            <button style={{marginTop: "1rem"}} onClick={onContinue}>
                Continuar
            </button>
            <button
                style={{marginTop: "1rem", marginLeft: "1rem"}}
                onClick={downloadCSV}
            >
                Descarregar CSV
            </button>
        </div>
    );
}
