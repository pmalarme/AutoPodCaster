import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [results, setResults] = useState([]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const dataText = document.getElementById('data-text').value;

    // Split the dataText by newlines. 
    // And recombine the entries not starting with http, make sure to push the first entry and new entry when previous entry does starts with http
    // example
    // input: line 1. This article is about the history of the internet. 
    //        line 2. It describes the beginnings of the internet and the people who helped create it.
    //        line 3. https://en.wikipedia.org/wiki/History_of_the_Internet
    //        line 4. And this article is about LLMs
    //        line 5. https://en.wikipedia.org/wiki/Large_language_model
    // output: array of 4 elements: [line1+2, line3, line4, line5]

    const dataTextArray = [];
    for (const entry of dataText.split('\n')) {
      if (entry.toLowerCase().startsWith('http')) {
        dataTextArray.push(entry);
      } 
      else {
        if (dataTextArray.length === 0 || dataTextArray[dataTextArray.length - 1].toLowerCase().startsWith('http')) {
              dataTextArray.push(entry);
            } else {
              dataTextArray[dataTextArray.length - 1] += '\n' + entry;
            }
        }
    }

    // store the results
    const resultsArray = [];

    // post each entry to the server
    for (const entry of dataTextArray) {
      try {
        const response = await fetch('http://localhost:8081/index', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ input: entry }),
        });

        const result = await response.json();
        console.log('Success:', 'Request ID:', result.request_id, 'for', entry);
        resultsArray.push(result.request_id + '|' + entry);
      } catch (error) {
        console.error('Error:', error);
      }
    };

    setResults(resultsArray);
  }


  const handleInput = (event) => {
    const textarea = event.target;
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 10 * 24)}px`; // 24px is the approximate height of one row
  };

  return (
    <>
      <h1>AutoPodcaster</h1>
      <hr />
      <h2>My Knowledge Space</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          id="data-text"
          rows="2"
          cols="75"
          placeholder="Paste URL or text here... One URL per line"
          onInput={handleInput}
          style={{ overflow: 'hidden', maxHeight: '240px' }} // 10 rows * 24px
        ></textarea>
        <br />
        <div>or</div>
        <button type="submit">Add to my knowledge space</button>
      </form>
      <hr />
      {results.length > 0 && (
        <table>
          <tr>
            <th>Status</th>
            <th>Request ID</th>
            <th>Entry</th>
          </tr>
          {results.map((result, index) => (
            <tr>
              <td><div class="text-left-align">Queued</div></td>
              <td><div class="text-left-align">{result.split('|')[0]}</div></td>
              <td><div class="single-line-ellipsis">{result.split('|')[1]}</div></td>
            </tr>
          ))}
        </table>
      )}
    </>
  )
}

export default App
