class AudioManager {
    constructor() {
        this.audioContext = null;
        this.currentBuffer = null;
        this.source = null;
        this.isPlaying = false;
        this.gainNode = null;
        this.tempo = 120;
        this.volume = 0.8;
        this.ambianceType = '';
    }

    async init() {
        // Initialize Web Audio API
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.gainNode = this.audioContext.createGain();
            this.gainNode.gain.value = this.volume;
            this.gainNode.connect(this.audioContext.destination);
        }
    }

    async loadLoop(ambianceType, tempo, volume) {
        try {
            // Initialize audio context if not already done
            await this.init();

            // Show loading state
            this.setLoadingState(true);

            // Create API request payload
            const payload = {
                ambiance_type: ambianceType,
                tempo: tempo,
                volume: volume
            };

            // Make request to backend API
            const response = await fetch('/api/generate-loop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Get audio data from response
            const audioData = await response.arrayBuffer();
            
            // Decode audio data
            this.currentBuffer = await this.audioContext.decodeAudioData(audioData);
            
            // Update state
            this.ambianceType = ambianceType;
            this.tempo = tempo;
            this.volume = volume;

            // Enable controls
            this.setLoadingState(false);
            return true;
        } catch (error) {
            console.error('Error loading loop:', error);
            this.setLoadingState(false);
            this.showError('Failed to generate loop. Please try again.');
            return false;
        }
    }

    async play() {
        if (!this.currentBuffer || this.isPlaying) return;

        try {
            // Initialize audio context if suspended
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }

            // Create new source
            this.source = this.audioContext.createBufferSource();
            this.source.buffer = this.currentBuffer;
            this.source.loop = true;
            this.source.connect(this.gainNode);
            
            // Start playback
            this.source.start();
            this.isPlaying = true;
            
            // Update UI
            this.updatePlayButton(true);
            
            // Start visualization
            this.startVisualization();
        } catch (error) {
            console.error('Error playing audio:', error);
        }
    }

    pause() {
        if (!this.source || !this.isPlaying) return;

        this.source.stop();
        this.source = null;
        this.isPlaying = false;
        
        // Update UI
        this.updatePlayButton(false);
        
        // Stop visualization
        this.stopVisualization();
    }

    togglePlayPause() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }

    setVolume(volume) {
        this.volume = volume;
        if (this.gainNode) {
            this.gainNode.gain.value = volume;
        }
        // Update volume display
        const volumeValue = document.getElementById('volume-value');
        if (volumeValue) {
            volumeValue.textContent = `${Math.round(volume * 100)}%`;
        }
    }

    updatePlayButton(isPlaying) {
        const playIcon = document.getElementById('play-icon');
        const pauseIcon = document.getElementById('pause-icon');
        
        if (playIcon && pauseIcon) {
            if (isPlaying) {
                playIcon.style.display = 'none';
                pauseIcon.style.display = 'block';
            } else {
                playIcon.style.display = 'block';
                pauseIcon.style.display = 'none';
            }
        }
    }

    setLoadingState(isLoading) {
        const playPauseBtn = document.getElementById('play-pause-btn');
        const downloadBtn = document.getElementById('download-btn');
        
        if (playPauseBtn) {
            playPauseBtn.disabled = isLoading;
        }
        if (downloadBtn) {
            downloadBtn.disabled = isLoading || !this.currentBuffer;
        }
    }

    startVisualization() {
        const bars = document.querySelectorAll('.bar');
        if (!bars.length) return;

        // Simple visualization effect
        this.vizInterval = setInterval(() => {
            bars.forEach(bar => {
                const scale = 0.5 + Math.random() * 0.5;
                bar.style.transform = `scaleY(${scale})`;
            });
        }, 150);
    }

    stopVisualization() {
        if (this.vizInterval) {
            clearInterval(this.vizInterval);
            this.vizInterval = null;
        }

        // Reset bars
        const bars = document.querySelectorAll('.bar');
        bars.forEach(bar => {
            bar.style.transform = 'scaleY(1)';
        });
    }

    showError(message) {
        // Create error element if it doesn't exist
        let errorEl = document.getElementById('error-message');
        if (!errorEl) {
            errorEl = document.createElement('div');
            errorEl.id = 'error-message';
            errorEl.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background-color: #e74c3c;
                color: white;
                padding: 15px 25px;
                border-radius: 5px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                z-index: 1000;
                text-align: center;
            `;
            document.body.appendChild(errorEl);
        }
        
        errorEl.textContent = message;
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorEl && errorEl.parentNode) {
                errorEl.parentNode.removeChild(errorEl);
            }
        }, 5000);
    }

    async downloadLoop() {
        if (!this.currentBuffer) return;

        try {
            // Create offline audio context to render the buffer
            const offlineContext = new OfflineAudioContext(
                this.currentBuffer.numberOfChannels,
                this.currentBuffer.length,
                this.currentBuffer.sampleRate
            );

            // Create buffer source
            const source = offlineContext.createBufferSource();
            source.buffer = this.currentBuffer;
            source.connect(offlineContext.destination);
            source.start(0);

            // Start rendering
            source.start(0);
            const renderedBuffer = await offlineContext.startRendering();

            // Convert to WAV format
            const wavBlob = this.bufferToWave(renderedBuffer);
            
            // Create download link
            const url = URL.createObjectURL(wavBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${this.ambianceType.replace('_', ' ')}-${this.tempo}bpm.wav`;
            document.body.appendChild(a);
            a.click();
            
            // Cleanup
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error downloading loop:', error);
            this.showError('Failed to download loop. Please try again.');
        }
    }

    // Convert AudioBuffer to WAV format
    bufferToWave(buffer) {
        const numOfChan = buffer.numberOfChannels;
        const length = buffer.length * numOfChan * 2 + 44;
        const arrayBuffer = new ArrayBuffer(length);
        const view = new DataView(arrayBuffer);
        const channels = [];
        let i, sample, offset = 0;

        // Extract channels
        for (i = 0; i < numOfChan; i++) {
            channels.push(buffer.getChannelData(i));
        }

        // Write WAVE header
        this.writeString(view, 0, 'RIFF');
        view.setUint32(4, length - 8, true);
        this.writeString(view, 8, 'WAVE');
        this.writeString(view, 12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, numOfChan, true);
        view.setUint32(24, buffer.sampleRate, true);
        view.setUint32(28, buffer.sampleRate * numOfChan * 2, true);
        view.setUint16(32, numOfChan * 2, true);
        view.setUint16(34, 16, true);
        this.writeString(view, 36, 'data');
        view.setUint32(40, length - 44, true);

        // Write interleaved data
        offset = 44;
        for (i = 0; i < buffer.length; i++) {
            for (let channel = 0; channel < numOfChan; channel++) {
                sample = Math.max(-1, Math.min(1, channels[channel][i]));
                sample = (0.5 + sample < 0 ? sample * 32768 : sample * 32767) | 0;
                view.setInt16(offset, sample, true);
                offset += 2;
            }
        }

        return new Blob([view], { type: 'audio/wav' });
    }

    writeString(view, offset, string) {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    }
}

// Initialize UI
document.addEventListener('DOMContentLoaded', () => {
    const audioManager = new AudioManager();
    
    // Get DOM elements
    const ambianceSelect = document.getElementById('ambiance-select');
    const tempoSlider = document.getElementById('tempo-slider');
    const tempoValue = document.getElementById('tempo-value');
    const volumeSlider = document.getElementById('volume-slider');
    const volumeValue = document.getElementById('volume-value');
    const playPauseBtn = document.getElementById('play-pause-btn');
    const downloadBtn = document.getElementById('download-btn');
    const newAmbianceBtn = document.getElementById('new-ambiance-btn');
    const modal = document.getElementById('new-ambiance-modal');
    const closeModal = document.querySelector('.close');
    const newAmbianceForm = document.getElementById('new-ambiance-form');

    // Initialize audio context on first user interaction
    const initAudioOnInteraction = async () => {
        await audioManager.init();
        document.removeEventListener('click', initAudioOnInteraction);
        document.removeEventListener('keydown', initAudioOnInteraction);
    };

    document.addEventListener('click', initAudioOnInteraction);
    document.addEventListener('keydown', initAudioOnInteraction);

    // Update tempo display
    tempoValue.textContent = `${tempoSlider.value} BPM`;

    // Tempo slider event
    tempoSlider.addEventListener('input', () => {
        tempoValue.textContent = `${tempoSlider.value} BPM`;
    });

    // Volume slider event
    volumeSlider.addEventListener('input', () => {
        const volume = parseInt(volumeSlider.value) / 100;
        volumeValue.textContent = `${volumeSlider.value}%`;
        audioManager.setVolume(volume);
    });

    // Play/Pause button event
    playPauseBtn.addEventListener('click', () => {
        audioManager.togglePlayPause();
    });

    // Download button event
    downloadBtn.addEventListener('click', () => {
        audioManager.downloadLoop();
    });

    // Ambiance selection event
    ambianceSelect.addEventListener('change', async () => {
        const selectedAmbiance = ambianceSelect.value;
        const tempo = parseInt(tempoSlider.value);
        const volume = parseInt(volumeSlider.value) / 100;

        if (selectedAmbiance) {
            const success = await audioManager.loadLoop(selectedAmbiance, tempo, volume);
            if (success) {
                downloadBtn.disabled = false;
            }
        } else {
            // Reset if no ambiance selected
            audioManager.pause();
            audioManager.currentBuffer = null;
            playPauseBtn.disabled = true;
            downloadBtn.disabled = true;
        }
    });

    // New ambiance request button
    newAmbianceBtn.addEventListener('click', () => {
        modal.style.display = 'block';
    });

    // Close modal
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Handle new ambiance form submission
    newAmbianceForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const ambianceName = document.getElementById('ambiance-name').value;
        const ambianceDescription = document.getElementById('ambiance-description').value;
        
        try {
            const response = await fetch('/api/request-ambiance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: ambianceName,
                    description: ambianceDescription
                })
            });

            if (response.ok) {
                // Show success message
                audioManager.showError('Ambiance request submitted successfully!');
                // Close modal
                modal.style.display = 'none';
                // Reset form
                newAmbianceForm.reset();
            } else {
                throw new Error('Failed to submit request');
            }
        } catch (error) {
            console.error('Error submitting ambiance request:', error);
            audioManager.showError('Failed to submit ambiance request. Please try again.');
        }
    });
});