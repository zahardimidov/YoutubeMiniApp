import { Link, useNavigate } from 'react-router-dom';
import playSVG from '../../Assets/image/play.svg';
import './Element.css';


function Element({ data, children, ...props }) {
    let navigate = useNavigate();

    function clickVideo() {
        console.log(data);
        window.Telegram.WebApp.sendData(JSON.stringify(data));
        window.Telegram.WebApp.close();
    }

    function clickChannel() {
        navigate('/channel', {state: data});
    }

    const posterStyle = {
        backgroundImage: `url(${data.photo})`,
    }
    const firstLetter = data.title[0];

    return (
        <div className={data.type + ' element'} {...props} onClick={data.type === 'video' ? () => clickVideo() : () => clickChannel()} >
            <div className={data.type + '-poster center'} style={posterStyle}>
                {data.type === 'video' ? <img src={playSVG} alt="Video" /> : <p>{firstLetter}</p>}
            </div>
            <div className={data.type + '-info'}>
                <h3 className={data.type + '-title line2'}>{data.title}</h3>
                {data.type === 'video' ? <p className='video-channel primary line2'>@{data.channel_title}</p> : ''}
                {children}
            </div>
        </div>
    );
}

export default Element;