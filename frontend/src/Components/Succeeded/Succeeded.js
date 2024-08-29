import React from 'react';
import coolGIF from '../../Assets/gif/cool.gif'

function Succeeded() {
    return (
        <div className='succeeded' style={{ color: 'white', textAlign: 'center', paddingBlock: '25vh' }}>
            <h1>Платеж выполнен успешно</h1>
            <h3 style={{ marginTop: '15px' }}>Теперь вы можете наслаждаться возможностью подписки в боте</h3>

            <div className='center gif'>
                <img src={coolGIF} alt="succeeded"></img>
            </div>
        </div>
    );
}

export default Succeeded;