import React, { useState, useRef, useEffect } from 'react';
import './MusicPlayer.css';

function MusicPlayer({ audioUrl, ambiance, allTracks = [], onTrackChange }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0);
  const audioRef = useRef(null);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleSeek = (e) => {
    const seekTime = (e.target.value / 100) * duration;
    if (audioRef.current) {
      audioRef.current.currentTime = seekTime;
      setCurrentTime(seekTime);
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = e.target.value / 100;
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const downloadAudio = () => {
    const link = document.createElement('a');
    link.href = audioUrl;
    link.download = `${ambiance?.name || 'Custom Music'}.mp3`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleTrackChange = (index) => {
    setCurrentTrackIndex(index);
    setIsPlaying(false);
    if (onTrackChange) {
      onTrackChange(index);
    }
  };

  return (
    <div className="music-player">
      <div className="player-header">
        <div>
          <h3>🎧 Lecture en cours</h3>
          <span className="ambiance-name">{ambiance?.name || 'Composition personnalisée'}</span>
        </div>
        {allTracks.length > 1 && (
          <div className="track-selector">
            <span className="track-label">Variante:</span>
            {allTracks.map((track, index) => (
              <button
                key={index}
                className={`track-button ${currentTrackIndex === index ? 'active' : ''}`}
                onClick={() => handleTrackChange(index)}
              >
                {index + 1}
              </button>
            ))}
          </div>
        )}
      </div>

      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setIsPlaying(false)}
      />

      <div className="player-controls">
        <button className="play-button" onClick={togglePlay}>
          {isPlaying ? '⏸️' : '▶️'}
        </button>

        <div className="time-controls">
          <span className="time">{formatTime(currentTime)}</span>
          <input
            type="range"
            min="0"
            max="100"
            value={(currentTime / duration) * 100 || 0}
            onChange={handleSeek}
            className="seek-bar"
          />
          <span className="time">{formatTime(duration)}</span>
        </div>

        <div className="volume-controls">
          <span>🔊</span>
          <input
            type="range"
            min="0"
            max="100"
            value={volume * 100}
            onChange={handleVolumeChange}
            className="volume-bar"
          />
        </div>

        <button className="download-button" onClick={downloadAudio}>
          ⬇️ Télécharger
        </button>
      </div>
    </div>
  );
}

export default MusicPlayer;