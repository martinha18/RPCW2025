import React, {useState} from "react";
import {Association} from "./Association";
import './question.css'

export function Question({question, questionCount, answered, onAnswer}) {
    const [answer, setAnswer] = useState('');

    return (
        <div className="qs-root">
            <h2>Questão {questionCount}: {question.question}</h2>

            {'options2' in question
                ? <div key={`${questionCount}`}>
                    <Association question={question} readOnly={answered} onChangeAnswers={setAnswer}/>
                    {!answered &&
                        <button disabled={answer === ''} style={{marginTop: '1rem'}}
                                onClick={() => onAnswer(answer)}>Submeter</button>
                    }
                </div>
                : <div className="qs-answers">
                    {question.options.map(option => (
                        <button
                            className={
                                answered && option === question.answer
                                    ? 'selected-button'
                                    : ''
                            }
                            disabled={answered}
                            key={`${questionCount}-${option}`}
                            onClick={() => onAnswer(option)}>
                            {option}
                        </button>
                    ))}
                </div>
            }
        </div>
    );
}
