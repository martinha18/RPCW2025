import React, {useState} from 'react';
import {Question} from "./Question.jsx";
import {FaTrash} from "react-icons/fa6";

const DynamicInput = ({dataName, name, questionData, setQuestionData}) => {
    const initialValues = questionData[name] || [];
    const [inputs, setInputs] = useState(initialValues);

    const handleAddInput = () => {
        setInputs([...inputs, '']);
    };

    const handleRemoveInput = (index) => {
        const updatedInputs = inputs.filter((_, i) => i !== index);
        setInputs(updatedInputs);
    };

    const handleChange = (e, index) => {
        const updatedInputs = [...inputs];
        updatedInputs[index] = e.target.value;
        setInputs(updatedInputs);
    };

    const handleBlur = () => {
        setQuestionData((prev) => ({
            ...prev,
            [name]: inputs,
        }));
    };

    return (
        <div className="flex-column-1rem">
            <h3>{dataName}</h3>
            {inputs.map((inputValue, index) => (
                <div key={index} >
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => handleChange(e, index)}
                        onBlur={handleBlur}
                        placeholder={`Opção #${index + 1}`}
                        style={{marginRight: '1rem'}}
                    />
                    <button type="button" onClick={() => handleRemoveInput(index)}><FaTrash/></button>
                </div>
            ))}
            <button type="button" onClick={handleAddInput}>
                Adicionar Opção
            </button>
        </div>
    );
};

const QuestionKind = {
    TrueFalse: "TrueFalse",
    Options: "Options",
    Association: "Association",
}

const QuestionKindOptions = {
    [QuestionKind.TrueFalse]: {options: ['Verdadeiro', 'False']},
    [QuestionKind.Options]: {options: []},
    [QuestionKind.Association]: {options: [], options2: []},
}

function QuestionEditor({questionCount, onAddQuestion}) {
    const [questionKind, setQuestionKind] = useState(QuestionKind.TrueFalse);
    const [questionText, setQuestionText] = useState("");
    const [questionData, setQuestionData] = useState(QuestionKindOptions[QuestionKind.TrueFalse]);
    const [dataInserted, setDataInserted] = useState(false);

    const setQuestion = (kind) => {
        setQuestionKind(kind);
        setQuestionData(QuestionKindOptions[kind]);
    }

    const canProcede = () => {
        if (questionText === "") return false;
        if (questionData.options.length < 2) return false;
        if (questionData.options.some((o) => o.length === 0)) return false;
        if ('options2' in questionData) {
            if (questionData.options2.length !== questionData.options.length) return false;
            if (questionData.options2.some((o) => o.length === 0)) return false;
        }
        return true;
    }

    const reset = () => {
        setQuestionKind(QuestionKind.TrueFalse);
        setQuestionText("");
        setQuestionData(QuestionKindOptions[QuestionKind.TrueFalse]);
        setDataInserted(false);
    }

    if (!dataInserted) {
        return <div className="flex-column-1rem">
            <h1>Adicionar Questão</h1>

            <div style={{display: 'flex'}}>
                <button className={questionKind === QuestionKind.TrueFalse ? 'selected-button' : ''}
                        style={{borderBottomRightRadius: 0, borderTopRightRadius: 0, borderRight: 0}}
                        onClick={() => setQuestion(QuestionKind.TrueFalse)}>Verdadeiro e Falso
                </button>
                <button className={questionKind === QuestionKind.Options ? 'selected-button' : ''}
                        style={{borderRadius: 0, borderRight: 0}}
                        onClick={() => setQuestion(QuestionKind.Options)}>Opções
                </button>
                <button className={questionKind === QuestionKind.Association ? 'selected-button' : ''}
                        style={{borderBottomLeftRadius: 0, borderTopLeftRadius: 0}}
                        onClick={() => setQuestion(QuestionKind.Association)}>Associação
                </button>
            </div>

            <input type="text" value={questionText} onChange={(e) => setQuestionText(e.target.value)}
                   placeholder="Questão"/>

            {{
                [QuestionKind.TrueFalse]: null,
                [QuestionKind.Options]: <div>
                    <DynamicInput dataName="Opções" name={'options'} questionData={questionData}
                                  setQuestionData={setQuestionData}/>
                </div>,
                [QuestionKind.Association]: <div className="flex-column-1rem">
                    <DynamicInput dataName="Coluna 1" name={'options'} questionData={questionData}
                                  setQuestionData={setQuestionData}/>
                    <DynamicInput dataName="Coluna 2" name={'options2'} questionData={questionData}
                                  setQuestionData={setQuestionData}/>
                </div>,
            }[questionKind]}

            <button disabled={!canProcede()} onClick={() => setDataInserted(true)}>Continuar</button>
        </div>;
    } else {
        return <Question
            question={{question: questionText, ...questionData}}
            questionCount={questionCount}
            answered={false}
            onAnswer={(a) => {
                onAddQuestion({question: questionText, ...questionData, answer: a});
                reset();
            }}/>
    }
}

export default QuestionEditor;
