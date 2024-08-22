import React from 'react';
import { useParams } from "react-router-dom";
import Loading from '../Loading/Loading';
import './Downloading.css';
//import { data } from './data';


function Downloading() {
    const [text, setText] = React.useState('File is preparing');
    let { video_id } = useParams();
    const downloadURL = '/api/download_video/' + video_id;

    React.useEffect(() => {
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_id: video_id })
        };

        fetch(process.env.REACT_APP_API_URL + '/upload_video', requestOptions);

        const interval = setInterval(function () {
            fetch(process.env.REACT_APP_API_URL + '/check_video', requestOptions)
                .then(response => response.json())
                .then(data => {
                    if (data.status == 'ready') {
                        clearInterval(interval);

                        setTimeout(function () {
                            setText('File is downloading');
                            document.getElementById('download').click();
                        }, 5000)
                    }
                });
        }, 1000)
    }, [])



    return (
        <>
            <h1 style={{ color: 'white', textAlign: 'center', paddingBlock: '20vh 5vh' }}>{text}</h1>
            <Loading></Loading>
            <a id='download' href={downloadURL} download={true}></a>
        </>
    );
}

export default Downloading;