import { useNavigate } from "react-router-dom";
import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import Element from '../Element/Element';
import Layout from '../Layout/Layout';
import List from '../List/List';
import Loading from '../Loading/Loading';
//import { data } from './data';


function Channel() {
    let { state } = useLocation();
    let navigate = useNavigate(); 

    const [loading, setLoading] = useState(true);
    const [foundElements, setElements] = useState([]);

    window.Telegram.WebApp.BackButton.show();

    window.Telegram.WebApp.onEvent('backButtonClicked', () => {
        window.Telegram.WebApp.BackButton.hide();
        navigate('/');
    })
    
    React.useEffect(() => {
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ channel_id: state.id })
          };
          fetch(process.env.REACT_APP_API_URL + '/channel_videos', requestOptions)
            .then(response => response.json())
            .then(data => {
                setElements(data);
                setLoading(false);
            });
    }, [])

    return (
        <Layout>
            <Element style={{height: '80px', pointerEvents: 'none'}} data={state}><p className='line2 channel-description'>{state.description}</p></Element>
            {loading && <Loading></Loading>}
            <List
                elements={foundElements}
                emptyHeading={`No videos found”`} />
        </Layout>
    );
}

export default Channel;