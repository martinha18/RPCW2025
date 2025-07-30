import React from "react";

export function UserList({players, canStart, onStart}) {
    return (<div className="flex-column-1rem" style={{marginTop: '1.2rem'}}>
        <h2>Número de Jogadores: {players.length}</h2>
        <ul style={{listStyleType: 'none', gap: '1rem'}} className="flex-column-1rem">
            {players.map((p) => (<li key={p.player_id}>{p.username}</li>))}
        </ul>
        {canStart && <button style={{marginTop: '1rem', width: 'fit-content'}} onClick={onStart}>Start</button>}
    </div>);
}
