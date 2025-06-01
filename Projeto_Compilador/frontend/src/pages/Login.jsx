import React, {useState} from 'react';
import {useSocket} from '../SocketContext.jsx';
import {useNavigate} from "react-router-dom";
import './login.css';

const Login = () => {
    const navigate = useNavigate();

    const [username, setUsername] = useState('');
    const [code, setCode] = useState('');
    const {connectSocket} = useSocket();

    const handleLogin = () => {
        connectSocket().send('join_game', {'room_id': code, 'username': username});
    };

    return <div className="login-center">
        <div className="login-form">
            <h1>OntoQuiz</h1>
            <input
                type="text"
                placeholder="Nome de Utilizador"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <input
                type="number"
                placeholder="Código"
                value={code}
                onChange={(e) => setCode(e.target.value)}
            />
            <div>
                <button disabled={username.length === 0 || !/\d{6}/.test(code)} onClick={handleLogin}>Ligar</button>
                <button onClick={() => navigate('/admin')}>Criar</button>
            </div>
        </div>
    </div>;
};

export default Login;
