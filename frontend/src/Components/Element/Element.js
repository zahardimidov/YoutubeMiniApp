import { Link, useNavigate } from 'react-router-dom';
import playSVG from '../../Assets/image/play.svg';
import './Element.css';

function clickVideo(video) {
    console.log(video)

    window.Telegram.WebApp.sendData(video);

    window.Telegram.WebApp.close()
}

function clickChannel(channel) {
    let navigate = useNavigate();
    navigate('/channel', state = channel);
}

function Element({ data, children, ...props }) {
    const posterStyle = {
        backgroundImage: `url(${data.photo})`,
    }
    return (
        <div className={data.type + ' element'} {...props} onClick={data.type === 'video' ? () => clickVideo(data) : () => clickChannel(data)} >
            <div className={data.type + '-poster center'} style={posterStyle}>
                {data.type === 'video' ? <img src={playSVG} alt="Video" /> : ''}
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