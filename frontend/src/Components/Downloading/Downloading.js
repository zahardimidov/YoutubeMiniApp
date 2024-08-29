import React from 'react';
import { useSearchParams } from "react-router-dom";
import Loading from '../Loading/Loading';
import './Downloading.css';
import loadGIF from '../../Assets/gif/load.gif'
import waitGIF from '../../Assets/gif/wait.gif'
import problemGIF from '../../Assets/gif/problem.gif'


function Downloading() {
    const [text, setText] = React.useState('Файл подготавливается');
    const [loading, setLoading] = React.useState(true);
    const [searchParams, setSearchParams] = useSearchParams();
    const [gif, setGif] = React.useState(loadGIF);

    const downloadURL = `/api/download/?` + searchParams;

    React.useEffect(() => {
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(Object.fromEntries(new URLSearchParams(searchParams)))
        };

        fetch(process.env.REACT_APP_API_URL + `/upload`, requestOptions);

        const interval = setInterval(function () {
            fetch(process.env.REACT_APP_API_URL + `/download`, requestOptions)
                .then(response => response.json())
                .then(data => {
                    if (data.status == 'ready') {
                        clearInterval(interval);
                        setLoading(false);
                        setGif(waitGIF);

                        setText('Скачивание скоро начнется');
                        document.getElementById('download').click();
                    }
                    if (data.status == 'subscribe') {
                        clearInterval(interval);
                        setLoading(false);
                        setGif(problemGIF);

                        setText('Подписка не активна, вернитесь в бот и оплатите подписку !!!');
                    }
                });
        }, 3000)
    }, [])



    return (
        <div className='downloading'>
            <h1 style={{ color: 'white', textAlign: 'center', paddingBlock: '20vh 5vh' }}>{text}</h1>
            {loading && <Loading></Loading>}
            <a id='download' href={downloadURL} download={true}></a>

            <img src={gif} alt="state"></img>
        </div>
    );
}

export default Downloading;