const API_URL = 'http://localhost:5000/api';

// Elements
const promptInput = document.getElementById('prompt');
const durationSlider = document.getElementById('duration');
const temperatureSlider = document.getElementById('temperature');
const durationValue = document.getElementById('durationValue');
const temperatureValue = document.getElementById('temperatureValue');
const generateBtn = document.getElementById('generateBtn');
const resultCard = document.getElementById('resultCard');
const errorCard = document.getElementById('errorCard');
const audioPlayer = document.getElementById('audioPlayer');
const downloadBtn = document.getElementById('downloadBtn');
const newGenerationBtn = document.getElementById('newGenerationBtn');
const errorMessage = document.getElementById('errorMessage');

let currentDownloadUrl = '';

// Update slider values
durationSlider.addEventListener('input', (e) => {
    durationValue.textContent = e.target.value;
});

temperatureSlider.addEventListener('input', (e) => {
    temperatureValue.textContent = parseFloat(e.target.value).toFixed(1);
});

// Example tags click
document.querySelectorAll('.tag').forEach(tag => {
    tag.addEventListener('click', () => {
        promptInput.value = tag.textContent;
        promptInput.focus();
    });
});

// Generate audio
generateBtn.addEventListener('click', async () => {
    const prompt = promptInput.value.trim();
    
    if (!prompt) {
        showError('Veuillez entrer une description pour l\'ambiance sonore');
        return;
    }
    
    // Hide previous results
    resultCard.style.display = 'none';
    errorCard.style.display = 'none';
    
    // Show loading state
    generateBtn.disabled = true;
    document.querySelector('.btn-text').style.display = 'none';
    document.querySelector('.loader').style.display = 'block';
    
    try {
        const response = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                duration: parseInt(durationSlider.value),
                temperature: parseFloat(temperatureSlider.value)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentDownloadUrl = `${API_URL}/download/${data.filename}`;
            audioPlayer.src = currentDownloadUrl;
            resultCard.style.display = 'block';
            
            // Scroll to result
            resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            showError(data.error || 'Une erreur est survenue');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError('Impossible de se connecter au serveur. Vérifiez que le backend est démarré.');
    } finally {
        // Reset button state
        generateBtn.disabled = false;
        document.querySelector('.btn-text').style.display = 'block';
        document.querySelector('.loader').style.display = 'none';
    }
});

// Download audio
downloadBtn.addEventListener('click', () => {
    if (currentDownloadUrl) {
        window.open(currentDownloadUrl, '_blank');
    }
});

// New generation
newGenerationBtn.addEventListener('click', () => {
    resultCard.style.display = 'none';
    promptInput.focus();
});

// Show error
function showError(message) {
    errorMessage.textContent = message;
    errorCard.style.display = 'block';
    errorCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    setTimeout(() => {
        errorCard.style.display = 'none';
    }, 5000);
}

// Check API health on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        console.log('API Status:', data);
    } catch (error) {
        console.warn('Backend not available:', error);
    }
});
