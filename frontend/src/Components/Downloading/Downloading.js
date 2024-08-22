import React from 'react';
import { useNavigate, useParams } from "react-router-dom";
import Loading from '../Loading/Loading';
import './Downloading.css';
//import { data } from './data';


function Downloading() {
    let { video_id } = useParams();
    let navigate = useNavigate();

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
                        navigate('/api/download_video/' + video_id);
                    }
                });
        }, 1000)
    }, [])



    return (
        <>
            <h1 style={{ color: 'white', textAlign: 'center', paddingBlock: '20vh 5vh' }}> Video is preparing </h1>
            <Loading></Loading>
        </>
    );
}

export default Downloading;