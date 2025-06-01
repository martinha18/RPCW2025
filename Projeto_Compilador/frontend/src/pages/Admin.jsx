import React, {useEffect, useState} from "react";
import {Question} from "../components/Question.jsx";
import {useSocket} from "../SocketContext.jsx";
import {useNavigate} from "react-router-dom";
import {FaArrowDown, FaArrowUp, FaFileImport, FaMapLocation, FaPlay, FaShuffle, FaTrash} from "react-icons/fa6";
import './admin.css'
import QuestionEditor from "../components/QuestionEditor.jsx";

export function Admin() {
    const socket = useSocket();
    const navigate = useNavigate();

    const [ontologies, setOntologies] = useState([]);
    const [file, setFile] = useState(null);
    const [questions, setQuestions] = useState([]);

    const fetchOntologies = async () => {
        const res = await fetch('/api/');
        setOntologies(await res.json());
    };

    useEffect(() => {
        fetchOntologies();
    }, []);

    const upload = async () => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('name', file.name.replace('.ttl', ''));
        await fetch('/api/', {method: 'POST', body: formData});
        fetchOntologies();
    };

    const remove = async (filename) => {
        await fetch(`/api/${filename}`, {method: 'DELETE'});
        fetchOntologies();
    };

    const loadQuestions = async (filename) => {
        const res = await fetch(`/api/${filename}?count=1`);
        const data = await res.json();
        setQuestions(q => q.concat(data));
    };

    const moveQuestion = (index, direction) => {
        const newQuestions = [...questions];
        const target = index + direction;
        if (target < 0 || target >= newQuestions.length) return;
        [newQuestions[index], newQuestions[target]] = [newQuestions[target], newQuestions[index]];
        setQuestions(newQuestions);
    };

    const shuffleQuestions = () => {
        const shuffled = [...questions];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        setQuestions(shuffled);
    };

    const removeQuestion = (index) => {
        setQuestions(q => {
            let t = [...q];
            t.splice(index, 1)
            return t;
        });
    };

    const startGame = () => {
        socket.connectSocket().send('init_game', {questions});
        navigate('/');
    };

    return (
        <div className="adm-root">
            <div className="adm-onts">
                <h1>Ontologias</h1>
                <div>
                    <input type="file" onChange={(e) => setFile(e.target.files[0])} accept=".ttl,text/turtle"/>
                    <button onClick={upload}>Upload</button>
                </div>
                {ontologies.map((f) => (
                    <div key={f} className="adm-card">
                        <div className="adm-sub-card-space">
                            <h2>{f}</h2>
                        </div>
                        <button onClick={() => remove(f)}><FaTrash/></button>
                        <button onClick={() => loadQuestions(f)}><FaFileImport/></button>
                        <button onClick={() => navigate(f)}><FaMapLocation/></button>
                    </div>
                ))}
            </div>
            <div className="adm-questions">
                <div>
                    <div>
                        <h1>Questões</h1>
                    </div>
                    <button onClick={shuffleQuestions}><FaShuffle style={{fontSize: '1.8rem'}}/></button>
                    <button disabled={questions.length === 0} onClick={startGame}><FaPlay style={{fontSize: '1.8rem'}}/></button>
                </div>
                {questions.map((q, i) => (
                    <div key={i} className="adm-card">
                        <div className="adm-sub-card adm-sub-card-horizontal">
                            {i !== 0 &&
                                <button onClick={() => moveQuestion(i, -1)}><FaArrowUp/></button>
                            }
                            {i !== questions.length - 1 &&
                                <button onClick={() => moveQuestion(i, 1)}><FaArrowDown/></button>
                            }
                            <button onClick={() => removeQuestion(i)}><FaTrash/></button>
                        </div>
                        <div style={{overflow: 'auto'}}>
                            <Question question={q} questionCount={i + 1} answered={q.answer}/>
                        </div>
                    </div>
                ))}
                <div className="adm-card" style={{overflow: 'auto'}}>
                    <QuestionEditor questionCount={questions.length + 1}
                                    onAddQuestion={(question) => setQuestions(q => q.concat([question]))}/>
                </div>
            </div>
        </div>
    );
}
