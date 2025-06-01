import React, {createContext, useContext, useState} from 'react';
import io from 'socket.io-client';

const SocketContext = createContext();

export const useSocket = () => {
    const context = useContext(SocketContext);
    if (!context) {
        throw new Error('useSocket must be used within a SocketProvider');
    }
    return context;
};

export const SocketProvider = ({children}) => {
    const [socket, setSocket] = useState(null);

    const disconnectSocket = () => {
        if (socket) socket.disconnect();
        setSocket(null);
    }

    const connectSocket = () => {
        const newSocket = io();

        setSocket(newSocket);

        newSocket.on('disconnect', disconnectSocket);

        return newSocket;
    };

    return (
        <SocketContext.Provider value={{socket, connectSocket, disconnectSocket}}>
            {children}
        </SocketContext.Provider>
    );
};
