import React, { useState, useEffect } from 'react';
import { GoEyeClosed } from "react-icons/go";
import { RxEyeOpen } from "react-icons/rx";

const indexerURL = 'http://localhost:8081/';

function KnowledgeSpace() {
  const [knowledgeItems, setKnowledgeItems] = useState([]);
  const [isOpen, setIsOpen] = useState(true);
  const [showDetails, setShowDetails] = useState(false);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const savedItems = localStorage.getItem('knowledgeItems');
    if (savedItems) {
      setKnowledgeItems(JSON.parse(savedItems));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('knowledgeItems', JSON.stringify(knowledgeItems));
  }, [knowledgeItems]);

  const handleFileUpload = async (file) => {
    setIsLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${indexerURL}index_file`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      setKnowledgeItems(prev => [...prev, {
        id: data.request_id,
        type: 'File',
        name: file.name,
        status: 'Processing',
        timestamp: new Date().toISOString()
      }]);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${indexerURL}index`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: inputText })
      });

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      setKnowledgeItems(prev => [...prev, {
        id: data.request_id,
        type: 'Text',
        name: inputText,
        status: 'Processing',
        timestamp: new Date().toISOString()
      }]);

      setInputText('');
      
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const checkStatus = async (id) => {
    try {
      const response = await fetch(`${indexerURL}status/${id}`);
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      setKnowledgeItems(prev => 
        prev.map(item => 
          item.id === id ? { ...item, status: data.status } : item
        )
      );
      
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h2 onClick={() => setIsOpen(!isOpen)} style={{ cursor: 'pointer' }}>
        Knowledge Space {isOpen ? <RxEyeOpen /> : <GoEyeClosed />}
      </h2>

      <div style={{
        maxHeight: isOpen ? '10000px' : '0',
        overflow: 'hidden',
        transition: 'max-height 0.5s ease-out',
      }}>
        <div style={{ 
          border: '2px dashed #ccc',
          padding: '20px',
          marginBottom: '20px',
          textAlign: 'center'
        }}>
          <input
            type="file"
            onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
            style={{ display: 'none' }}
            id="file-upload"
          />
          <label htmlFor="file-upload" style={{ cursor: 'pointer' }}>
            {isLoading ? 'Uploading...' : 'Upload a file'}
          </label>
        </div>

        <form onSubmit={handleTextSubmit}>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Enter text or paste URL..."
            style={{ width: '100%', padding: '10px', marginBottom: '10px', boxSizing: 'border-box' }}
            rows={3}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputText.trim()}
          >
            {isLoading ? 'Processing...' : 'Submit'}
          </button>
        </form>

        {error && (
          <div style={{ color: 'red', padding: '10px', marginTop: '10px' }}>
            {error}
          </div>
        )}

        <div style={{ margin: '20px 0' }}>  {/* Add spacing between buttons */}
          <button onClick={() => setShowDetails(!showDetails)}>
            {showDetails ? 'Hide' : 'Show'} Details
          </button>
        </div>

        {showDetails && knowledgeItems.length > 0 && (
          <table className="styled-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Entry</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {knowledgeItems.map((item, index) => (
                <tr key={item.id} className={index % 2 === 0 ? 'even-row' : 'odd-row'}>
                  <td><div className="text-left-align">{item.type}</div></td>
                  <td><div className="single-line-ellipsis">{item.name}</div></td>
                  <td><div className="text-left-align">{item.status}</div></td>
                  <td>
                    <button onClick={() => checkStatus(item.id)}>
                      Check Status
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default KnowledgeSpace;