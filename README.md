# Musical Loop Generation Application

This application generates musical loops based on ambiance types using external AI music generation APIs. It provides a web interface for users to select ambiance types and generate corresponding instrumental loops.

## 1. Prerequisites and Dependencies

Before setting up the application, ensure you have the following prerequisites installed:

### System Requirements
- Python 3.8 or higher
- Node.js (for frontend development, optional)
- Git (for cloning the repository)

### Python Dependencies
The application requires the following Python packages:
- Flask (web framework)
- aiohttp (asynchronous HTTP client)
- python-dotenv (environment variable management)
- pytest (testing framework)

Install the required Python packages using pip:
```bash
pip install flask aiohttp python-dotenv pytest
```

### External API Services
The application integrates with three external music generation APIs:
- Suno AI
- Udio
- Stable Audio

You'll need to obtain API keys from these services to use the full functionality.

## 2. Environment Setup

### Clone the Repository
```bash
git clone https://github.com/your-username/musical-loop-generator.git
cd musical-loop-generator
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configure Environment Variables
Copy the example configuration file and update it with your API keys:

```bash
cp config/app_config.json config/app_config.json
```

Edit the `config/app_config.json` file to add your API keys:

```json
{
  "api_keys": {
    "suno": "your_suno_api_key_here",
    "udio": "your_udio_api_key_here",
    "stable_audio": "your_stable_audio_api_key_here"
  },
  "api_endpoints": {
    "suno": "https://api.suno.ai/v1/music",
    "udio": "https://api.udio.com/v1/generate",
    "stable_audio": "https://api.stableaudio.com/v1/sound"
  }
}
```

## 3. API Key Configuration

To configure API keys for the external services:

1. **Suno API**:
   - Visit [Suno AI](https://www.suno.ai/) and create an account
   - Navigate to your account settings to generate an API key
   - Add the key to the `api_keys.suno` field in `config/app_config.json`

2. **Udio API**:
   - Visit [Udio](https://www.udio.com/) and create an account
   - Access the developer portal to generate an API key
   - Add the key to the `api_keys.udio` field in `config/app_config.json`

3. **Stable Audio**:
   - Visit [Stable Audio](https://stableaudio.com/) and create an account
   - Navigate to the API section to generate an API key
   - Add the key to the `api_keys.stable_audio` field in `config/app_config.json`

**Security Note**: Never commit your API keys to version control. The `config/app_config.json` file is included in `.gitignore` by default.

## 4. Launching the Application

The application consists of a Flask backend server and a frontend interface. Both need to be running.

### Start the Flask Server
```bash
python app.py
```

The server will start on `http://localhost:5000` by default.

### Start the Frontend Server
In a separate terminal, navigate to the project root and start the frontend server:
```bash
python -m http.server 8000
```

Alternatively, you can open `src/ui/index.html` directly in your browser.

### Access the Application
Open your web browser and navigate to:
- Frontend: `http://localhost:8000/src/ui/index.html`
- API Endpoint: `http://localhost:5000`

## 5. Using the Application Interface

Once the application is running, you can use the web interface to generate musical loops:

1. **Select Ambiance Type**:
   - Use the dropdown menu to select from available ambiance types
   - Current options include: Mysterious Forest, Cyberpunk in the Rain, Medieval Castle, and Sports Fans Chanting

2. **Adjust Parameters**:
   - **Tempo**: Use the slider to adjust the beats per minute (BPM)
   - **Volume**: Control the overall volume of the generated loop

3. **Generate and Play**:
   - Click the play button to generate and play the musical loop
   - The first generation may take several seconds as it calls external APIs
   - Subsequent generations with the same parameters will be faster due to caching

4. **Download**:
   - Click the "Download Loop" button to save the generated audio as a WAV file
   - The filename will include the ambiance type and tempo

5. **Request New Ambiance**:
   - Click the "Request New Ambiance" button to submit a request for a new ambiance type
   - Fill out the form with the desired ambiance name and description
   - This feature allows users to suggest new ambiance types for future implementation

## 6. Adding New Ambiance Types

To add a new ambiance type to the application:

### Step 1: Create an Ambiance Configuration File
Create a new JSON file in the `assets/ambiance_configs/` directory with a descriptive name (use snake_case):

```bash
touch assets/ambiance_configs/new_ambiance.json
```

### Step 2: Define the Ambiance Configuration
Edit the JSON file with the following structure:

```json
{
  "tempo": 72,
  "instruments": [
    {
      "name": "instrument_name",
      "volume": -6,
      "effects": ["reverb", "delay"],
      "pattern": "random_interval"
    }
  ],
  "effects_chain": ["reverb", "low_pass_filter"],
  "description": "A description of the ambiance and mood"
}
```

Key configuration options:
- `tempo`: BPM for the generated music
- `instruments`: Array of instruments to include
  - `name`: Instrument identifier
  - `volume`: Volume level in dB
  - `effects`: Array of audio effects to apply
  - `pattern`: Generation pattern (e.g., "random_interval", "steady_beat")
- `effects_chain`: Order of effects to apply to the final mix

### Step 3: Add Instrument Samples (Optional)
For custom instruments, add WAV files to `assets/audio_samples/` with the naming convention:
```
[ambiance]_[instrument]_[variation].wav
```

For example: `forest_birds_01.wav`

### Step 4: Verify the New Ambiance
Restart the application server and check that your new ambiance appears in the dropdown menu.

## 7. Running Unit Tests

The application includes a comprehensive test suite to ensure functionality and prevent regressions.

### Run All Tests
```bash
python -m pytest tests/
```

### Run Specific Test Files
```bash
# Test ambiance manager
python -m pytest tests/test_ambiance_manager.py

# Test audio generation
python -m pytest tests/test_audio_generation.py

# Test application core
python -m pytest tests/test_application.py
```

### Run Tests with Coverage
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

This will generate a coverage report in the `htmlcov/` directory.

### Test Structure
The test suite is organized as follows:
- `tests/test_ambiance_manager.py`: Tests for ambiance configuration loading and validation
- `tests/test_audio_generation.py`: Tests for audio generation service and API integration
- `tests/test_application.py`: Tests for the main application controller

Each test file contains unit tests that verify the functionality of the corresponding module, including edge cases and error handling.

## Troubleshooting

### Common Issues
1. **API Keys Not Working**:
   - Verify that your API keys are correctly entered in `config/app_config.json`
   - Check that the API services are operational
   - Ensure you have sufficient credits/quotas with the service providers

2. **CORS Errors**:
   - Make sure the frontend and backend are running on the correct ports
   - The Flask server (port 5000) serves as the API endpoint for the frontend

3. **Audio Generation Failures**:
   - Check the application logs for error messages
   - Verify internet connectivity
   - Try a different ambiance type or parameters

4. **Missing Ambiance Types**:
   - Ensure configuration files are in the correct directory (`assets/ambiance_configs/`)
   - Verify JSON files are valid and contain required fields

For additional support, please contact the development team or consult the project documentation.
