import './Layout.css';

function Layout({ children, poster = true }) {
    return (
        <div className='layout'>
            { poster && <div className="poster"></div> } 
            <div className='content'>
                {children}
            </div>
        </div>
    );
}

export default Layout;