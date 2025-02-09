import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// import StudyKitchen from './components/StudyKitchen';
import LandingPage from './components/LandingPage';
import FocusRoast from './components/FocusRoast';
import TranquiliTea from './components/Tranquilitea';
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/focus-roast" element={<FocusRoast />} />
        <Route path="/tranquilitea" element={<TranquiliTea />} />
      </Routes>
    </Router>
  );
}

export default App;
