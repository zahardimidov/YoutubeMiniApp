import './SearchInput.css';

function SearchInput({ value, onChange, onClick, onKeyDown }) {
    return (
        <div className='s-input'>
            <div className="search-input-wrapper primary">
                <input className='search-input' value={value} onChange={onChange} onKeyDown={onKeyDown} placeholder='Поиск' id='search'></input>
            </div>
            <div className='search-input-img' onClick={onClick}>
                <svg width="1em" height="1em" viewBox="0 0 20 20"><path d="M14.386 14.386l4.0877 4.0877-4.0877-4.0877c-2.9418 2.9419-7.7115 2.9419-10.6533 0-2.9419-2.9418-2.9419-7.7115 0-10.6533 2.9418-2.9419 7.7115-2.9419 10.6533 0 2.9419 2.9418 2.9419 7.7115 0 10.6533z" stroke="currentColor" fill="none" strokeWidth="2" fillRule="evenodd" strokeLinecap="round" strokeLinejoin="round"></path></svg>
            </div>
        </div>
    );
}

export default SearchInput;