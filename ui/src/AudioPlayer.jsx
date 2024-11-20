import React from 'react';

const AudioPlayer = ({ url, title }) => {
  if (!url) return null;
  
  return (
    <div className="w-full max-w-xl mx-auto my-4 p-4 border rounded-lg shadow-sm">
      <h3 className="text-lg font-medium mb-2">{title || 'Podcast Player'}</h3>
      <audio 
        controls 
        className="w-full"
        preload="metadata"
      >
        <source src={url} type="audio/wav" />
        Your browser does not support the audio element.
      </audio>
    </div>
  );
};

export default AudioPlayer;