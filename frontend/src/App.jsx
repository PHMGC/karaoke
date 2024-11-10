import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import VideoPage from './VideoPage';
import HomePage from './HomePage';
import SelectionPage from './SelectionPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/video" element={<VideoPage />} />
        <Route path="/videos" element={<SelectionPage />} />
      </Routes>
    </Router>
  );
}

export default App;
