import React from 'react';
import { useNavigate, useParams } from "react-router-dom";
import Layout from '../Layout/Layout';
import Loading from '../Loading/Loading';
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

        fetch(process.env.REACT_APP_API_URL + '/upload_video');

        const interval = setInterval(function () {
            fetch(process.env.REACT_APP_API_URL + '/check_video', requestOptions)
                .then(response => response.json())
                .then(data => {
                    if (data.status == 'ready'){
                        clearInterval(interval);
                        navigate('/download_video/'+video_id);
                    }
                });
        }, 1000)
    }, [])



    return (
        <Layout poster={false}>
            <h1 style={{color: '#8fc3d3', textAlign: 'center', paddingBlock: '20vh 5vh'}}> Video is preparing </h1>
            <Loading></Loading>
        </Layout>
    );
}

export default Downloading;