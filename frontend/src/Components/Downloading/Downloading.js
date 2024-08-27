import React from 'react';
import { useParams, useSearchParams } from "react-router-dom";
import Loading from '../Loading/Loading';
import './Downloading.css';
//import { data } from './data';


function Downloading() {
    const [text, setText] = React.useState('File is preparing');
    const [loading, setLoading] = React.useState(true);
    const [searchParams, setSearchParams] = useSearchParams();

    const downloadURL = `/api/download/` + searchParams;

    React.useEffect(() => {
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: searchParams
        };

        fetch(process.env.REACT_APP_API_URL + `/upload`, requestOptions);

        const interval = setInterval(function () {
            fetch(process.env.REACT_APP_API_URL + `/check_${type}`, requestOptions)
                .then(response => response.json())
                .then(data => {
                    if (data.status == 'ready') {
                        clearInterval(interval);

                        setTimeout(function () {
                            setText('Downloading will be started soon');
                            setLoading(false);
                            document.getElementById('download').click();
                        }, 5000)
                    }
                });
        }, 1000)
    }, [])



    return (
        <div className='downloading'>
            <h1 style={{ color: 'white', textAlign: 'center', paddingBlock: '20vh 5vh' }}>{text}</h1>
            {loading && <Loading></Loading>}
            <a id='download' href={downloadURL} download={true}></a>
        </div>
    );
}

export default Downloading;