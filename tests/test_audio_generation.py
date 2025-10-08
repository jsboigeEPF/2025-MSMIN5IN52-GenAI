import unittest
import os
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path
from src.audio.generation_service import AudioGenerationService, AudioGenerationConfig, AudioResult

class TestAudioGenerationService(unittest.TestCase):
    """Test cases for AudioGenerationService class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = {
            'api': {
                'base_url': 'http://localhost:8000',
                'timeout': 30
            },
            'cache': {
                'enabled': True,
                'directory': 'cache/audio',
                'ttl': 3600
            },
            'api_endpoints': {
                'suno': 'https://api.suno.ai/v1/music',
                'udio': 'https://api.udio.com/v1/generate',
                'stable_audio': 'https://api.stableaudio.com/v1/sound'
            },
            'api_keys': {
                'suno': 'test_suno_key',
                'udio': 'test_udio_key',
                'stable_audio': 'test_stable_audio_key'
            },
            'audio': {
                'loop_duration': 30,
                'max_concurrent_requests': 3
            }
        }
        self.ambiance_config = {
            'name': 'test_ambiance',
            'description': 'Test ambiance description',
            'tags': ['test'],
            'parameters': {
                'bpm': 120,
                'scale': 'C major',
                'instruments': ['piano', 'strings']
            }
        }
        self.service = AudioGenerationService(self.config)

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        # Clean up any test cache files
        cache_dir = Path('cache/audio')
        if cache_dir.exists():
            for file in cache_dir.glob('*.wav'):
                file.unlink(missing_ok=True)

    def test_initialization(self):
        """Test that the service initializes correctly with configuration."""
        self.assertIsNotNone(self.service.config)
        self.assertIsNotNone(self.service.cache_dir)
        self.assertEqual(self.service.cache_ttl, 3600)
        self.assertEqual(self.service.max_concurrent_requests, 3)
        self.assertIsNotNone(self.service.request_semaphore)
        self.assertIsNone(self.service.session)
        
        # Test API keys are properly set
        self.assertEqual(self.service.api_keys['suno'], 'test_suno_key')
        self.assertEqual(self.service.api_keys['udio'], 'test_udio_key')
        self.assertEqual(self.service.api_keys['stable_audio'], 'test_stable_audio_key')
        
        # Test API endpoints are properly set
        self.assertEqual(self.service.api_endpoints['suno'], 'https://api.suno.ai/v1/music')
        self.assertEqual(self.service.api_endpoints['udio'], 'https://api.udio.com/v1/generate')
        self.assertEqual(self.service.api_endpoints['stable_audio'], 'https://api.stableaudio.com/v1/sound')

    def test_initialization_with_missing_config(self):
        """Test initialization with minimal configuration."""
        service = AudioGenerationService({})
        self.assertIsNotNone(service.config)
        self.assertEqual(service.cache_ttl, 3600)  # Default value
        self.assertEqual(service.max_concurrent_requests, 3)  # Default value

    def test_validate_api_keys_with_missing_keys(self):
        """Test API key validation with missing keys."""
        # Create service with missing API keys
        config = self.config.copy()
        config['api_keys']['suno'] = ''
        service = AudioGenerationService(config)
        
        # The service should not raise an exception but log a warning
        # We can't easily test the log message, but we can verify the service still works
        self.assertEqual(service.api_keys['suno'], '')

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    def test_initialize_creates_session(self, mock_session_class):
        """Test that initialize method creates an HTTP session."""
        # Create a mock session
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session
        
        # Test initialize creates session
        asyncio.run(self.service.initialize())
        self.assertIsNotNone(self.service.session)
        mock_session_class.assert_called_once()

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    def test_cleanup_closes_session(self, mock_session_class):
        """Test that cleanup method closes the HTTP session."""
        # Create and initialize session
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session
        asyncio.run(self.service.initialize())
        
        # Test cleanup closes session
        asyncio.run(self.service.cleanup())
        mock_session.close.assert_called_once()
        self.assertIsNone(self.service.session)

    def test_generate_cache_key(self):
        """Test that cache keys are generated correctly."""
        config = AudioGenerationConfig(
            prompt="test prompt",
            duration=30,
            model="test_model"
        )
        
        # Generate cache key
        cache_key = self.service._generate_cache_key(config)
        
        # Verify it's a valid MD5 hash (32 characters, hexadecimal)
        self.assertEqual(len(cache_key), 32)
        self.assertTrue(all(c in '0123456789abcdef' for c in cache_key))
        
        # Verify same config produces same key
        same_config = AudioGenerationConfig(
            prompt="test prompt",
            duration=30,
            model="test_model"
        )
        same_key = self.service._generate_cache_key(same_config)
        self.assertEqual(cache_key, same_key)
        
        # Verify different config produces different key
        different_config = AudioGenerationConfig(
            prompt="different prompt",
            duration=30,
            model="test_model"
        )
        different_key = self.service._generate_cache_key(different_config)
        self.assertNotEqual(cache_key, different_key)

    def test_get_cache_file_path(self):
        """Test that cache file paths are generated correctly."""
        test_key = "abcdef1234567890"
        cache_file = self.service._get_cache_file_path(test_key)
        
        expected_path = Path('cache/audio') / f"{test_key}.wav"
        self.assertEqual(cache_file, expected_path)

    @patch('src.audio.generation_service.Path')
    def test_check_cache_returns_none_when_file_does_not_exist(self, mock_path):
        """Test that check_cache returns None when cache file does not exist."""
        # Mock the path object
        mock_file = Mock()
        mock_file.exists.return_value = False
        mock_path.return_value = mock_file
        
        # Test check_cache returns None
        result = asyncio.run(self.service._check_cache("test_key"))
        self.assertIsNone(result)
        mock_file.exists.assert_called_once()

    @patch('src.audio.generation_service.Path')
    @patch('src.audio.generation_service.datetime')
    def test_check_cache_returns_none_when_expired(self, mock_datetime, mock_path):
        """Test that check_cache returns None when cache is expired."""
        # Mock file that exists
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_file.stat.return_value.st_mtime = 1000  # Old timestamp
        mock_path.return_value = mock_file
        
        # Mock datetime to be well past the TTL
        mock_now = Mock()
        mock_now.fromtimestamp.return_value = datetime.fromtimestamp(5000)
        mock_datetime.now.return_value = datetime.fromtimestamp(5000)
        mock_datetime.fromtimestamp = datetime.fromtimestamp
        
        # Set TTL to 3600 seconds (1 hour)
        self.service.cache_ttl = 3600
        
        # Test check_cache returns None (expired)
        result = asyncio.run(self.service._check_cache("test_key"))
        self.assertIsNone(result)
        mock_file.unlink.assert_called_once()  # File should be deleted

    @patch('src.audio.generation_service.Path')
    @patch('src.audio.generation_service.datetime')
    def test_check_cache_returns_audio_result_when_valid(self, mock_datetime, mock_path):
        """Test that check_cache returns AudioResult when cache is valid."""
        # Mock file that exists and is not expired
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_file.stat.return_value.st_mtime = 4000  # Recent timestamp
        mock_file.read_bytes.return_value = b'test audio data'
        mock_path.return_value = mock_file
        
        # Mock datetime
        mock_now = Mock()
        mock_now.fromtimestamp.return_value = datetime.fromtimestamp(5000)
        mock_datetime.now.return_value = datetime.fromtimestamp(5000)
        mock_datetime.fromtimestamp = datetime.fromtimestamp
        
        # Set TTL to 3600 seconds (1 hour)
        self.service.cache_ttl = 3600
        
        # Test check_cache returns AudioResult
        result = asyncio.run(self.service._check_cache("test_key"))
        self.assertIsNotNone(result)
        self.assertIsInstance(result, AudioResult)
        self.assertEqual(result.audio_data, b'test audio data')
        self.assertEqual(result.api_used, 'cache')
        self.assertTrue(result.cache_hit)
        self.assertEqual(result.generation_time, 0)

    @patch('src.audio.generation_service.Path')
    def test_check_cache_returns_none_on_read_error(self, mock_path):
        """Test that check_cache returns None when there's an error reading the file."""
        # Mock file that exists but raises an exception when read
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_file.stat.return_value.st_mtime = 4000
        mock_file.read_bytes.side_effect = Exception("Read error")
        mock_path.return_value = mock_file
        
        # Mock datetime
        with patch('src.audio.generation_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.fromtimestamp(5000)
            mock_datetime.fromtimestamp = datetime.fromtimestamp
            
            # Test check_cache returns None
            result = asyncio.run(self.service._check_cache("test_key"))
            self.assertIsNone(result)

    @patch('src.audio.generation_service.Path')
    def test_save_to_cache(self, mock_path):
        """Test that save_to_cache saves audio data to the correct file."""
        # Mock the path object
        mock_file = Mock()
        mock_path.return_value = mock_file
        
        # Test save_to_cache
        asyncio.run(self.service._save_to_cache("test_key", b'test audio data'))
        
        # Verify the file was written
        mock_file.write_bytes.assert_called_once_with(b'test audio data')

    @patch('src.audio.generation_service.Path')
    def test_save_to_cache_handles_write_error(self, mock_path):
        """Test that save_to_cache handles write errors gracefully."""
        # Mock the path object to raise an exception
        mock_file = Mock()
        mock_file.write_bytes.side_effect = Exception("Write error")
        mock_path.return_value = mock_file
        
        # Test save_to_cache doesn't raise an exception
        try:
            asyncio.run(self.service._save_to_cache("test_key", b'test audio data'))
        except Exception as e:
            self.fail(f"save_to_cache raised {type(e).__name__} unexpectedly!")

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_make_api_request_success(self, mock_session_class):
        """Test that make_api_request handles successful API responses."""
        # Create mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"result": "success"}
        
        # Create mock session
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create service with initialized session
        service = AudioGenerationService(self.config)
        service.session = mock_session
        
        # Test make_api_request
        result = await service._make_api_request(
            "test_api",
            "https://api.test.com/v1/test",
            {"test": "data"},
            {"Content-Type": "application/json"}
        )
        
        self.assertEqual(result, {"result": "success"})
        mock_session.post.assert_called_once()

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_make_api_request_rate_limiting(self, mock_session_class):
        """Test that make_api_request handles rate limiting with retry."""
        # Create mock responses - first 429, then 200
        mock_response_429 = AsyncMock()
        mock_response_429.status = 429
        mock_response_429.headers = {'Retry-After': '1'}
        
        mock_response_200 = AsyncMock()
        mock_response_200.status = 200
        mock_response_200.json.return_value = {"result": "success"}
        
        # Create mock session that returns 429 then 200
        mock_session = AsyncMock()
        mock_session.post.side_effect = [
            mock_response_429,
            mock_response_200
        ]
        mock_session_class.return_value = mock_session
        
        # Create service with initialized session
        service = AudioGenerationService(self.config)
        service.session = mock_session
        
        # Test make_api_request retries after rate limit
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await service._make_api_request(
                "test_api",
                "https://api.test.com/v1/test",
                {"test": "data"},
                {"Content-Type": "application/json"}
            )
            
            self.assertEqual(result, {"result": "success"})
            mock_sleep.assert_called_once_with(1)  # Retry-After value

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_make_api_request_server_error(self, mock_session_class):
        """Test that make_api_request raises exception for server errors."""
        # Create mock response with 500 status
        mock_response = AsyncMock()
        mock_response.status = 500
        
        # Create mock session
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create service with initialized session
        service = AudioGenerationService(self.config)
        service.session = mock_session
        
        # Test make_api_request raises exception for server error
        with self.assertRaises(Exception) as context:
            await service._make_api_request(
                "test_api",
                "https://api.test.com/v1/test",
                {"test": "data"},
                {"Content-Type": "application/json"}
            )
        
        self.assertIn("API server error", str(context.exception))

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_make_api_request_client_error(self, mock_session_class):
        """Test that make_api_request raises exception for client errors."""
        # Create mock session that raises ClientError
        mock_session = AsyncMock()
        mock_session.post.side_effect = Exception("Client error")
        mock_session_class.return_value = mock_session
        
        # Create service with initialized session
        service = AudioGenerationService(self.config)
        service.session = mock_session
        
        # Test make_api_request raises exception for client error
        with self.assertRaises(Exception) as context:
            await service._make_api_request(
                "test_api",
                "https://api.test.com/v1/test",
                {"test": "data"},
                {"Content-Type": "application/json"}
            )
        
        self.assertIn("Network error", str(context.exception))

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_generate_with_suno_success(self, mock_session_class):
        """Test successful audio generation with Suno API."""
        # Create mock responses
        mock_post_response = AsyncMock()
        mock_post_response.status = 200
        mock_post_response.json.return_value = {
            "audio_url": "https://audio.suno.ai/test.mp3"
        }
        
        mock_get_response = AsyncMock()
        mock_get_response.status = 200
        mock_get_response.read.return_value = b"audio data"
        
        # Create mock session
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_post_response
        mock_session.get.return_value.__aenter__.return_value = mock_get_response
        mock_session_class.return_value = mock_session
        
        # Create service with initialized session
        service = AudioGenerationService(self.config)
        service.session = mock_session
        
        # Test generate_with_suno
        config = AudioGenerationConfig(
            prompt="test prompt",
            duration=30
        )
        
        result = await service._generate_with_suno(config)
        
        # Verify result
        self.assertIsInstance(result, AudioResult)
        self.assertEqual(result.audio_data, b"audio data")
        self.assertEqual(result.api_used, "suno")
        self.assertGreater(result.generation_time, 0)
        self.assertIn("suno", result.metadata["source"])

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_generate_with_suno_missing_api_config(self):
        """Test generate_with_suno raises exception when API config is missing."""
        # Create service without Suno API config
        config = self.config.copy()
        config['api_endpoints']['suno'] = ''
        service = AudioGenerationService(config)
        
        # Test generate_with_suno raises exception
        config = AudioGenerationConfig(prompt="test prompt")
        with self.assertRaises(Exception) as context:
            await service._generate_with_suno(config)
        
        self.assertIn("SUNO API configuration missing", str(context.exception))

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_generate_with_suno_no_audio_url(self, mock_session_class):
        """Test generate_with_suno raises exception when no audio URL is returned."""
        # Create mock response without audio_url
        mock_post_response = AsyncMock()
        mock_post_response.status = 200
        mock_post_response.json.return_value = {"result": "success"}  # No audio_url
        
        # Create mock session
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_post_response
        mock_session_class.return_value = mock_session
        
        # Create service with initialized session
        service = AudioGenerationService(self.config)
        service.session = mock_session
        
        # Test generate_with_suno raises exception
        config = AudioGenerationConfig(prompt="test prompt")
        with self.assertRaises(Exception) as context:
            await service._generate_with_suno(config)
        
        self.assertIn("No audio URL returned from Suno API", str(context.exception))

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_generate_with_udio_success(self, mock_session_class):
        """Test successful audio generation with Udio API."""
        # Create mock responses
        mock_post_response = AsyncMock()
        mock_post_response.status = 200
        mock_post_response.json.return_value = {
            "clips": [
                {"audio_url": "https://audio.udio.com/test.mp3"}
            ]
        }
        
        mock_get_response = AsyncMock()
        mock_get_response.status = 200
        mock_get_response.read.return_value = b"audio data"
        
        # Create mock session
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_post_response
        mock_session.get.return_value.__aenter__.return_value = mock_get_response
        mock_session_class.return_value = mock_session
        
        # Create service with initialized session
        service = AudioGenerationService(self.config)
        service.session = mock_session
        
        # Test generate_with_udio
        config = AudioGenerationConfig(
            prompt="test prompt",
            duration=30
        )
        
        result = await service._generate_with_udio(config)
        
        # Verify result
        self.assertIsInstance(result, AudioResult)
        self.assertEqual(result.audio_data, b"audio data")
        self.assertEqual(result.api_used, "udio")
        self.assertGreater(result.generation_time, 0)
        self.assertIn("udio", result.metadata["source"])

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_generate_with_udio_no_clips(self, mock_session_class):
        """Test generate_with_udio raises exception when no clips are returned."""
        # Create mock response without clips
        mock_post_response = AsyncMock()
        mock_post_response.status = 200
        mock_post_response.json.return_value = {"result": "success"}  # No clips
        
        # Create mock session
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_post_response
        mock_session_class.return_value = mock_session
        
        # Create service with initialized session
        service = AudioGenerationService(self.config)
        service.session = mock_session
        
        # Test generate_with_udio raises exception
        config = AudioGenerationConfig(prompt="test prompt")
        with self.assertRaises(Exception) as context:
            await service._generate_with_udio(config)
        
        self.assertIn("No audio clips returned from Udio API", str(context.exception))

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_generate_with_stable_audio_success(self, mock_session_class):
        """Test successful audio generation with Stable Audio API."""
        # Create mock responses
        mock_post_response = AsyncMock()
        mock_post_response.status = 200
        mock_post_response.json.return_value = {
            "audio_url": "https://audio.stableaudio.com/test.mp3"
        }
        
        mock_get_response = AsyncMock()
        mock_get_response.status = 200
        mock_get_response.read.return_value = b"audio data"
        
        # Create mock session
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_post_response
        mock_session.get.return_value.__aenter__.return_value = mock_get_response
        mock_session_class.return_value = mock_session
        
        # Create service with initialized session
        service = AudioGenerationService(self.config)
        service.session = mock_session
        
        # Test generate_with_stable_audio
        config = AudioGenerationConfig(
            prompt="test prompt",
            duration=30
        )
        
        result = await service._generate_with_stable_audio(config)
        
        # Verify result
        self.assertIsInstance(result, AudioResult)
        self.assertEqual(result.audio_data, b"audio data")
        self.assertEqual(result.api_used, "stable_audio")
        self.assertGreater(result.generation_time, 0)
        self.assertIn("stable_audio", result.metadata["source"])

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_generate_with_stable_audio_missing_api_config(self):
        """Test generate_with_stable_audio raises exception when API config is missing."""
        # Create service without Stable Audio API config
        config = self.config.copy()
        config['api_endpoints']['stable_audio'] = ''
        service = AudioGenerationService(config)
        
        # Test generate_with_stable_audio raises exception
        config = AudioGenerationConfig(prompt="test prompt")
        with self.assertRaises(Exception) as context:
            await service._generate_with_stable_audio(config)
        
        self.assertIn("STABLE_AUDIO API configuration missing", str(context.exception))

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_generate_audio_uses_cache_when_available(self, mock_session_class):
        """Test that generate_audio uses cache when available."""
        # Create mock session
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session
        
        # Create service with initialized session
        service = AudioGenerationService(self.config)
        service.session = mock_session
        
        # Mock _check_cache to return a cached result
        with patch.object(service, '_check_cache', new_callable=AsyncMock) as mock_check_cache:
            mock_check_cache.return_value = AudioResult(
                audio_data=b"cached audio data",
                metadata={"cached": True},
                api_used="cache",
                generation_time=0,
                cache_hit=True
            )
            
            # Mock _save_to_cache to avoid file operations
            with patch.object(service, '_save_to_cache', new_callable=AsyncMock) as mock_save_to_cache:
                # Test generate_audio
                result = await service.generate_audio("test ambiance")
                
                # Verify result came from cache
                self.assertEqual(result.audio_data, b"cached audio data")
                self.assertEqual(result.api_used, "cache")
                self.assertTrue(result.cache_hit)
                
                # Verify methods were called correctly
                mock_check_cache.assert_called_once()
                mock_save_to_cache.assert_not_called()  # Should not save since it's a cache hit

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_generate_audio_uses_first_successful_api(self, mock_session_class):
        """Test that generate_audio tries APIs in order and uses the first successful one."""
        # Create mock responses
        mock_post_response = AsyncMock()
        mock_post_response.status = 200
        mock_post_response.json.return_value = {
            "audio_url": "https://audio.suno.ai/test.mp3"
        }
        
        mock_get_response = AsyncMock()
        mock_get_response.status = 200
        mock_get_response.read.return_value = b"audio data"
        
        # Create mock session
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_post_response
        mock_session.get.return_value.__aenter__.return_value = mock_get_response
        mock_session_class.return_value = mock_session
        
        # Create service with initialized session
        service = AudioGenerationService(self.config)
        service.session = mock_session
        
        # Mock _check_cache to return None (no cache)
        with patch.object(service, '_check_cache', new_callable=AsyncMock) as mock_check_cache:
            mock_check_cache.return_value = None
            
            # Mock _save_to_cache to avoid file operations
            with patch.object(service, '_save_to_cache', new_callable=AsyncMock) as mock_save_to_cache:
                # Test generate_audio
                result = await service.generate_audio("test ambiance")
                
                # Verify result came from Suno (first API)
                self.assertEqual(result.api_used, "suno")
                
                # Verify methods were called correctly
                mock_check_cache.assert_called_once()
                mock_save_to_cache.assert_called_once()

    @patch('src.audio.generation_service.aiohttp.ClientSession')
    async def test_generate_audio_fails_when_all_apis_fail(self, mock_session_class):
        """Test that generate_audio raises exception when all APIs fail."""
        # Create mock session that raises exceptions for all API calls
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session
        
        # Create service with initialized session
        service = AudioGenerationService(self.config)
        service.session = mock_session
        
        # Mock all API methods to raise exceptions
        with patch.object(service, '_generate_with_suno', new_callable=AsyncMock) as mock_suno:
            mock_suno.side_effect = Exception("Suno failed")
            
            with patch.object(service, '_generate_with_udio', new_callable=AsyncMock) as mock_udio:
                mock_udio.side_effect = Exception("Udio failed")
                
                with patch.object(service, '_generate_with_stable_audio', new_callable=AsyncMock) as mock_stable:
                    mock_stable.side_effect = Exception("Stable Audio failed")
                    
                    # Mock _check_cache to return None (no cache)
                    with patch.object(service, '_check_cache', new_callable=AsyncMock) as mock_check_cache:
                        mock_check_cache.return_value = None
                        
                        # Test generate_audio raises exception
                        with self.assertRaises(Exception) as context:
                            await service.generate_audio("test ambiance")
                        
                        self.assertIn("Suno failed", str(context.exception))

    def test_generate_audio_creates_session_if_needed(self):
        """Test that generate_audio creates a session if one doesn't exist."""
        # Create service without session
        service = AudioGenerationService(self.config)
        self.assertIsNone(service.session)
        
        # Mock the initialize method
        with patch.object(service, 'initialize', new_callable=AsyncMock) as mock_initialize:
            # Mock _check_cache to return None (no cache)
            with patch.object(service, '_check_cache', new_callable=AsyncMock) as mock_check_cache:
                mock_check_cache.return_value = None
                
                # Mock API generation to avoid actual HTTP calls
                with patch.object(service, '_generate_with_suno', new_callable=AsyncMock) as mock_suno:
                    mock_suno.return_value = AudioResult(
                        audio_data=b"audio data",
                        metadata={"test": "data"},
                        api_used="suno",
                        generation_time=0.1
                    )
                    
                    # Mock _save_to_cache to avoid file operations
                    with patch.object(service, '_save_to_cache', new_callable=AsyncMock) as mock_save_to_cache:
                        # Test generate_audio
                        result = asyncio.run(service.generate_audio("test ambiance"))
                        
                        # Verify session was created
                        mock_initialize.assert_called_once()
                        self.assertIsNotNone(service.session)
                        
                        # Verify result
                        self.assertIsInstance(result, AudioResult)
                        self.assertEqual(result.api_used, "suno")

if __name__ == '__main__':
    unittest.main()