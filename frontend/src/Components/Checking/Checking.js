import React from 'react';
import { useNavigate, useParams } from "react-router-dom";
import Layout from '../Layout/Layout';
import Loading from '../Loading/Loading';
//import { data } from './data';


function Checking() {
    let { video_id } = useParams();
    let navigate = useNavigate();

    React.useEffect(() => {
        const interval = setInterval(function () {
            const requestOptions = {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video_id: video_id })
            };
            fetch(process.env.REACT_APP_API_URL + '/check_video', requestOptions)
                .then(response => response.json())
                .then(data => {
                    if (data.status == 'ready'){
                        navigate('/download/'+video_id);
                    }
                });
        }, 1000)
    }, [])



    return (
        <Layout poster={false}>
            <h1> Video is preparing </h1>
            <Loading></Loading>
        </Layout>
    );
}

export default Checking;