import React from 'react';
import KnowledgeSpace from './components/KnowledgeSpace';
import SubjectSpace from './components/SubjectSpace';
import './App.css';

function App() {
  return (
    <>
      <img src="src/assets/autopodcaster.png" alt="AutoPodcaster logo" style={{ width: '40%' }} />
      <SubjectSpace />
      <hr />
      <KnowledgeSpace />
    </>
  );
}

export default App;
