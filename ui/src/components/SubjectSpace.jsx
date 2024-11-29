import React, { useState, useEffect } from 'react';
import { GoEyeClosed } from "react-icons/go";
import { RxEyeOpen } from "react-icons/rx";

function SubjectSpace() {
  const [isOpen, setIsOpen] = useState(true);
  const [subjects, setSubjects] = useState([]);
  const [newSubject, setNewSubject] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    const savedSubjects = localStorage.getItem('subjects');
    if (savedSubjects) {
      setSubjects(JSON.parse(savedSubjects));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('subjects', JSON.stringify(subjects));
  }, [subjects]);

  const handleAddSubject = (e) => {
    e.preventDefault();
    if (!newSubject.trim()) return;

    if (subjects.some(subject => subject.name.toLowerCase() === newSubject.toLowerCase())) {
      setError('This subject already exists');
      return;
    }

    setSubjects(prev => [...prev, {
      id: Date.now().toString(),
      name: newSubject.trim(),
      timestamp: new Date().toISOString()
    }]);
    setNewSubject('');
    setError(null);
  };

  const handleDeleteSubject = (id) => {
    setSubjects(prev => prev.filter(subject => subject.id !== id));
  };

  return (
    <div>
      <h2 onClick={() => setIsOpen(!isOpen)} style={{ cursor: 'pointer' }}>
        Subject Space {isOpen ? <RxEyeOpen /> : <GoEyeClosed />}
      </h2>

      <div style={{
        maxHeight: isOpen ? '10000px' : '0',
        overflow: 'hidden',
        transition: 'max-height 0.5s ease-out',
      }}>
        <form onSubmit={handleAddSubject}>
          <input
            type="text"
            value={newSubject}
            onChange={(e) => setNewSubject(e.target.value)}
            placeholder="Enter new subject..."
            style={{ width: '100%', padding: '10px', marginBottom: '15px', boxSizing: 'border-box' }}
          />
          <button
            type="submit"
            disabled={!newSubject.trim()}
            style={{ marginBottom: '20px' }}  // Added margin bottom to the submit button
          >
            Add Subject
          </button>
        </form>

        {error && (
          <div style={{ color: 'red', padding: '10px', marginTop: '10px' }}>
            {error}
          </div>
        )}

        {subjects.length > 0 && (
          <table className="styled-table">
            <thead>
              <tr>
                <th>Subject</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {subjects.map((subject, index) => (
                <tr key={subject.id} className={index % 2 === 0 ? 'even-row' : 'odd-row'}>
                  <td><div className="text-left-align">{subject.name}</div></td>
                  <td>
                    <button onClick={() => handleDeleteSubject(subject.id)}>
                      Delete
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

export default SubjectSpace;