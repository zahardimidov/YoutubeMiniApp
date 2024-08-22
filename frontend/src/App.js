import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from './Components/Home/Home';
import Checking from './Components/Checking/Checking';
import Channel from './Components/Channel/Channel';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" exact={true} element={<Home />} />
        <Route path="/channel" element={<Channel />} />
        <Route path="/check/:video_id" element={<Checking />} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;