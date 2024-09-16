import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [dataId, setDataId] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const dataSource = document.getElementById('data-source').value;

    try {
      const response = await fetch('http://localhost:8081/index', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: dataSource }),
      });

      const result = await response.json();
      setDataId(result.request_id);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <>
      <h1>AutoPodcaster</h1>
      <hr />
      <form onSubmit={handleSubmit}>
        <input type="text" id="data-source" />
        <button type="submit">Submit</button>
      </form>
      {dataId && <p>Data ID: {dataId}</p>}
    </>
  )
}

export default App
