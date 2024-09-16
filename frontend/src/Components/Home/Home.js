import { useState } from 'react';
import Layout from '../Layout/Layout';
import Loading from '../Loading/Loading';
import List from '../List/List';
import SearchInput from '../SearchInput/SearchInput';


function Home() {
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [foundElements, setElements] = useState([])

  const [value, setValue] = useState('');

  function search(){
    setLoading(true);
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchText })
      };
      fetch(process.env.REACT_APP_API_URL + '/search', requestOptions)
        .then(response => response.json())
        .then(data => {
          setElements(data);
          setLoading(false);
          setValue(searchText);
        });
  }

  function filterElements(e) {
    if (e.key === 'Enter') {
      search()
    }
  }

  return (
    <Layout>
      <SearchInput
        value={searchText}
        onChange={e => setSearchText(e.target.value)}
        onClick={e => search()}
        onKeyDown={e => filterElements(e)} />
      {loading && <Loading></Loading>}
      <List
        elements={foundElements}
        emptyHeading={`Ничего не найдено по запросу “${value}”`} />
    </Layout>
  );
}

export default Home;