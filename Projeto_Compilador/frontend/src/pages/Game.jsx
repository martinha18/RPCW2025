import React, {useEffect, useRef, useState} from "react";
import {useSocket} from "../SocketContext.jsx";
import {Leaderboard} from "../components/Leaderboard.jsx";
import {UserList} from "../components/UserList.jsx";
import {Question} from "../components/Question.jsx";
import './game.css';

function Game() {
    const [isAdmin, setIsAdmin] = useState(false);
    const [code, setCode] = useState('');

    const [players, setPlayers] = useState([]);
    const [question, setQuestion] = useState(null);
    const [playersRemaining, setPlayersRemaining] = useState(new Set());
    const [stageOver, setStageOver] = useState(false);
    const [questionCount, setQuestionCount] = useState(0);
    const [leaderBoard, setLeaderBoard] = useState(null);
    const {socket, disconnectSocket} = useSocket();

    const handleAdminInitialization = (p) => {
        setIsAdmin(true);
        setCode(p.room_id);
    };

    const handlePlayerJoin = (p) => {
        setPlayers(p);
    };

    const removePlayer = (p) => {
        setPlayersRemaining(prevPlayersRemaining =>
            new Set(
                [...prevPlayersRemaining].filter(player => player !== p.player_id)
            )
        );
    };

    const handlePlayerLeft = (p) => {
        setPlayers(pl => pl.filter(player => player.player_id !== p.player_id));
        removePlayer(p);
    };

    const handlePlayerAnswer = (p) => {
        removePlayer(p);
    }

    const handleEndQuestion = () => {
        setStageOver(true);
    };

    const handleGameTerminated = (lb) => {
        setQuestion(null);
        setStageOver(false);
        setQuestionCount(0);
        setLeaderBoard(lb);
    };

    const playersRef = useRef(players);

    useEffect(() => {
        playersRef.current = players;
    }, [players]);

    const handleQuestion = (q) => {
        setQuestion(q);
        setStageOver(false);
        setPlayersRemaining(new Set(Array.from(playersRef.current.map(p => p.player_id))));
        setQuestionCount((q) => q + 1);
        setLeaderBoard(null);
    };

    useEffect(() => {
        socket.on("game_initialized", handleAdminInitialization);
        socket.on("player_joined", handlePlayerJoin);
        socket.on("player_left", handlePlayerLeft);
        socket.on("player_answered", handlePlayerAnswer);
        socket.on("game_stage_terminated", handleEndQuestion);
        socket.on("game_terminated", handleGameTerminated);
        socket.on("new_question", handleQuestion);

        return () => {
            socket.off("game_initialized", handleAdminInitialization);
            socket.off("player_joined", handlePlayerJoin);
            socket.off("player_left", handlePlayerLeft);
            socket.off("player_answered", handlePlayerAnswer);
            socket.off("game_stage_terminated", handleEndQuestion);
            socket.off("game_terminated", handleGameTerminated);
            socket.off("new_question", handleQuestion);
        };

        // TODO error
    }, [socket]);

    if (leaderBoard !== null) {
        return <div className="game">
            <Leaderboard leaderBoard={leaderBoard} onContinue={disconnectSocket}/>
        </div>;
    }

    if (question !== null) {
        return <div className="game">
            {!stageOver &&
                <div className="game-remaining">
                    <h1>Remaining {playersRemaining.size}</h1>
                    <div className="game-timer-container">
                        <div className="game-timer-bar"></div>
                    </div>
                </div>}
            <Question key={questionCount} questionCount={questionCount} question={question}
                      answered={stageOver || isAdmin}
                      onAnswer={(a) => {
                          socket.send("submit_answer", a);
                          setStageOver(true);
                      }}/>
            {stageOver && isAdmin && <button onClick={() => {
                socket.send("next_question");
            }}>Próxima Questão</button>}
        </div>;
    }

    return <div className="game">
        {isAdmin && <h1>Código: {code}</h1>}
        <UserList players={players} onStart={() => {
            socket.send("start_game");
        }} canStart={isAdmin}/>
    </div>;
}

export default Game;
