import {useSocket} from "../SocketContext.jsx";
import Game from "./Game.jsx";
import Login from "./Login.jsx";
import React from "react";

export const Home = () => {
    const {socket} = useSocket();

    return (
        <>
            {socket
                ? <Game/>
                : <Login/>
            }
        </>
    );
};
