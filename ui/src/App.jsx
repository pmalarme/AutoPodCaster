import React, { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

const baseURL = 'http://localhost:8081/';

class knowledgeBaseEntry {
  constructor(entry, request_id = '', status = '', type = '') {
    this.entry = entry;
    this.request_id = request_id;
    this.status = status;
    this.type = type;
  }
}

function App() {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [knowledgeBaseEntries, setKnowledgeBaseEntries] = useState([]);

  useEffect(() => {
    // Retrieve the array from local storage when the component mounts
    const storedItems = localStorage.getItem('knowledgeBaseEntries');
    if (storedItems) {
      setKnowledgeBaseEntries(JSON.parse(storedItems));
    }
  }, []);

  const addKnowledgeBaseEntry = (newKnowledgeBaseEntries) => {
    const tmpArray = [...knowledgeBaseEntries, ...newKnowledgeBaseEntries];
    // Store the updated array in local storage
    localStorage.setItem('knowledgeBaseEntries', JSON.stringify(tmpArray));
    setKnowledgeBaseEntries(tmpArray);
  };

  const handleSubmit = async (event) => {   
    event.preventDefault();
    const dataText = document.getElementById('data-text').value;

    if (dataText.length === 0) {
      return;
    }

    document.getElementById('data-text').disabled = true;
    document.getElementById('data-text').value = 'loading...';

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

    // post each entry to the server
    const resultEntries = [];
    for (const entry of dataTextArray) {
      if (entry.length > 0) {
        try {
          const response = await fetch(baseURL + 'index', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ input: entry }),
          });

          const result = await response.json();
          if (!result.error) {
            console.log('Success:', 'Request ID:', result.request_id, 'for', entry);
            resultEntries.push(new knowledgeBaseEntry(entry, result.request_id, 'Queued', 'Text'));
          } else {
            console.error('Error:', result.error);
          }
        } catch (error) {
          console.error('Error:', error);
        }
      }
    };
    document.getElementById('data-text').disabled = false;
    document.getElementById('data-text').value = '';

    console.log('number of resultEntries:', resultEntries.length);
    if (resultEntries.length > 0) {
      addKnowledgeBaseEntry(resultEntries);
    }
  }

  const handleInput = (event) => {
    const textarea = event.target;
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 10 * 24)}px`; // 24px is the approximate height of one row
  };

  const handleFileDrop = async (event) => {
    event.preventDefault();
    setDragging(false);
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      await uploadFile(files[0]);
    }
  };

  const handleFileSelect = async (event) => {
    const files = event.target.files;
    if (files.length > 0) {
      await uploadFile(files[0]);
    }
  };

  const uploadFile = async (file) => {

    document.getElementById('file-drop-zone').enabled = false;
    document.getElementById('file-drop-zone').style.backgroundColor = '#f0f0f0';
    setUploading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(baseURL + 'index_file', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      const resultEntries = [];
      if (!result.error) {
        console.log('File upload success:', result);
        resultEntries.push(new knowledgeBaseEntry(file.name, result.request_id, 'Queued', 'File'));
        addKnowledgeBaseEntry(resultEntries);
      } else {
        console.error('File upload error:', result.error);
      }
    } catch (error) {
      console.error('File upload error:', error);
    }

    document.getElementById('file-drop-zone').enabled = true;
    document.getElementById('file-drop-zone').style.backgroundColor = '#ffffff';
    setUploading(false);
  }

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleClick = () => {
    document.getElementById('file-input').click();
  };

  return (
    <>
      <h1>AutoPodcaster</h1>
      <hr />
      <h2>My Knowledge Space</h2>
      <form onSubmit={handleSubmit}>
        <div
          id='file-drop-zone'
          onDrop={handleFileDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={handleClick}
          style={{
            border: dragging ? '2px dashed #000' : '2px dashed #ccc',
            padding: '20px',
            marginTop: '10px',
            textAlign: 'center',
          }}
        >
          {uploading ? 'Uploading...' : dragging ? 'Drop the PDF or Word file here...' : 'Drag and drop a PDF or Word file here, or click to select a file'}
        </div>
        <input
          id="file-input"
          type="file"
          style={{ display: 'none' }}
          onChange={handleFileSelect}
        />
        or<br />
        <textarea
          id="data-text"
          rows="2"
          cols="75"
          placeholder="Paste URL or text here... One URL per line"
          onInput={handleInput}
          style={{ overflow: 'hidden', maxHeight: '240px' }} // 10 rows * 24px
        ></textarea>
        <br />
        <button type="submit">Add to my knowledge space</button>
      </form>
      <hr />
      {knowledgeBaseEntries.length > 0 && (
        <table>
          <thead>
            <tr>
              <td>Status</td>
              <td>Request ID</td>
              <td>Entry</td>
              <td>Type</td>
            </tr>
          </thead>
          <tbody>
          {knowledgeBaseEntries.map((result, index) => (
            <tr key={result.request_id}>
              <td><div className="text-left-align">{result.status}</div></td>
              <td><div className="text-left-align">{result.request_id}</div></td>
              <td><div className="single-line-ellipsis">{result.entry}</div></td>
              <td><div className="text-left-align">{result.type}</div></td>
            </tr>
          ))}
          </tbody>
        </table>
      )}
    </>
  )
}

export default App
