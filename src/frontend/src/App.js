import React from 'react';

import "bootstrap/dist/css/bootstrap.min.css";
import "shards-ui/dist/css/shards.min.css"
import MainNavbar from './MainNavBar';
import MainContent from './MainContent';

function App() {
  return (
    <div className="App">
      <MainNavbar />
      <MainContent />
    </div>
  );
}

export default App;
