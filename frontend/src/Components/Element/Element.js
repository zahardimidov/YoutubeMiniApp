import { Link } from 'react-router-dom';
import playSVG from '../../Assets/image/play.svg';
import './Element.css';

function clickVideo(video) {
    console.log(video)

    window.Telegram.WebApp.sendData(video);

    window.Telegram.WebApp.close()
}

function Element({ data, children, ...props }) {
    const posterStyle = {
        backgroundImage: `url(${data.photo})`,
    }
    return (
        <Link className={data.type + ' element'} {...props} to={data.type === 'channel' ? '/channel' : undefined} state={data.type === 'channel' ? data : undefined} onClick={data.type === 'video' ? () => clickVideo(data) : undefined} >
            <div className={data.type + '-poster center'} style={posterStyle}>
                {data.type === 'video' ? <img src={playSVG} alt="Video" /> : ''}
            </div>
            <div className={data.type + '-info'}>
                <h3 className={data.type + '-title line2'}>{data.title}</h3>
                {data.type === 'video' ? <p className='video-channel primary line2'>@{data.channel_title}</p> : ''}
                {children}
            </div>
        </Link>
    );
}

export default Element;