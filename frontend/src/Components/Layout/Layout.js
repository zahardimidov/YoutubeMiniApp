import './Layout.css';

function Layout({ children }) {
    return (
        <div className='layout'>
            <div className="poster"></div>
            <div className='content'>
                {children}
            </div>
        </div>
    );
}

export default Layout;