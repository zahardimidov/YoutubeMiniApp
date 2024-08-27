import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from './Components/Home/Home';
import Downloading from './Components/Downloading/Downloading';
import Channel from './Components/Channel/Channel';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" exact={true} element={<Home />} />
        <Route path="/channel" element={<Channel />} />
        <Route path="/download" element={<Downloading />} />
        <Route path="/check_audio/:video_id/:format_id" element={<Downloading type='audio'/>} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;