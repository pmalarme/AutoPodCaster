import React, { useRef } from 'react';

function FileUpload({ dragging, setDragging, uploading, uploadFile }) {
  const fileInputRef = useRef();

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
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

  const handleClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div>
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
          backgroundColor: uploading ? '#f0f0f0' : '#ffffff',
          cursor: 'pointer',
        }}
      >
        {uploading ? 'Uploading...' : dragging ? 'Drop the PDF or Word file here...' : 'Drag and drop a PDF or Word file here, or click to select a file'}
      </div>
      <input
        ref={fileInputRef}
        type="file"
        style={{ display: 'none' }}
        onChange={handleFileSelect}
      />
    </div>
  );
}

export default FileUpload;
