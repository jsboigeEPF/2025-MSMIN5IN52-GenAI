
"""
Audio generation service for the musical loop generation application.
Handles connections to external audio generation APIs (Suno, Udio, Stable Audio)
and provides methods for generating instrumental loops based on ambiance descriptions.
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union

import aiohttp
from src.core.config import Config

logger = logging.getLogger(__name__)

@dataclass
class AudioGenerationConfig:
    """Configuration for audio generation."""
    prompt: str
    duration: int = 30
    model: str = "default"
    temperature: float = 0.7
    top_p: float = 0.9
    guidance_scale: float = 3.0

@dataclass
class AudioResult:
    """Result of audio generation."""
    audio_data: bytes
    metadata: Dict[str, any]
    api_used: str
    generation_time: float
    cache_hit: bool = False

class AudioGenerationService:
    """
    Service class for generating instrumental loops using external APIs.
    
    This service handles connections to Suno, Udio, and Stable Audio APIs,
    manages authentication, rate limiting, caching, and audio validation.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the audio generation service.
        
        Args:
            config: Configuration object. If not provided, uses default config.
        """
        self.config = config or Config()
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache_dir = Path(self.config.get("cache.directory", "cache/audio"))
        self.cache_ttl = self.config.get("cache.ttl_seconds", 3600)
        self.max_concurrent_requests = self.config.get("audio.max_concurrent_requests", 3)
        self.request_semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        # API endpoints from config
        self.api_endpoints = self.config.get("api_endpoints", {})
        self.api_keys = {
            "suno": self.config.get("api_keys.suno", ""),
            "udio": self.config.get("api_keys.udio", ""),
            "stable_audio": self.config.get("api_keys.stable_audio", "")
        }
        
        # Validate API keys
        self._validate_api_keys()
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Audio generation service initialized with Suno, Udio, and Stable Audio APIs")
    
    def _validate_api_keys(self):
        """Validate that required API keys are present."""
        missing_keys = []
        for api_name, api_key in self.api_keys.items():
            if not api_key.strip():
                missing_keys.append(api_name)
        
        if missing_keys:
            logger.warning(f"Missing API keys for: {', '.join(missing_keys)}. "
                          f"Functionality will be limited.")
    
    async def initialize(self):
        """Initialize the service by creating HTTP session."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=300)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.debug("HTTP session created for audio generation service")
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.debug("HTTP session closed for audio generation service")
    
    def _generate_cache_key(self, config: AudioGenerationConfig) -> str:
        """
        Generate a cache key based on the generation configuration.
        
        Args:
            config: Audio generation configuration
            
        Returns:
            MD5 hash of the configuration as cache key
        """
        cache_data = {
            "prompt": config.prompt,
            "duration": config.duration,
            "model": config.model
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """
        Get the file path for a cached audio file.
        
        Args:
            cache_key: Cache key for the audio
            
        Returns:
            Path to the cache file
        """
        return self.cache_dir / f"{cache_key}.wav"
    
    async def _check_cache(self, cache_key: str) -> Optional[AudioResult]:
        """
        Check if audio is available in cache and not expired.
        
        Args:
            cache_key: Cache key to look up
            
        Returns:
            AudioResult if found and valid, None otherwise
        """
        cache_file = self._get_cache_file_path(cache_key)
        
        if not cache_file.exists():
            return None
            
        # Check if cache is expired
        file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - file_mtime > timedelta(seconds=self.cache_ttl):
            logger.debug(f"Cache expired for {cache_key}")
            cache_file.unlink(missing_ok=True)
            return None
        
        try:
            audio_data = cache_file.read_bytes()
            metadata = {
                "cached_at": file_mtime.isoformat(),
                "cache_key": cache_key
            }
            logger.debug(f"Cache hit for {cache_key}")
            return AudioResult(
                audio_data=audio_data,
                metadata=metadata,
                api_used="cache",
                generation_time=0,
                cache_hit=True
            )
        except Exception as e:
            logger.warning(f"Error reading cache file {cache_file}: {e}")
            return None
    
    async def _save_to_cache(self, cache_key: str, audio_data: bytes):
        """
        Save audio data to cache.
        
        Args:
            cache_key: Cache key for the audio
            audio_data: Audio data to cache
        """
        cache_file = self._get_cache_file_path(cache_key)
        try:
            cache_file.write_bytes(audio_data)
            logger.debug(f"Saved audio to cache: {cache_key}")
        except Exception as e:
            logger.warning(f"Error saving to cache {cache_file}: {e}")
    
    async def _make_api_request(
        self,
        api_name: str,
        endpoint: str,
        payload: Dict,
        headers: Dict
    ) -> Dict:
        """
        Make an API request with rate limiting and error handling.
        
        Args:
            api_name: Name of the API
            endpoint: API endpoint URL
            payload: Request payload
            headers: Request headers
            
        Returns:
            JSON response from API
            
        Raises:
            Exception: If API request fails
        """
        async with self.request_semaphore:  # Limit concurrent requests
            start_time = time.time()
            logger.debug(f"Making {api_name} API request to {endpoint}")
            
            try:
                async with self.session.post(endpoint, json=payload, headers=headers) as response:
                    response_time = time.time() - start_time
                    logger.debug(f"{api_name} API request completed in {response_time:.2f}s - Status: {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        return result
                    elif response.status == 429:
                        # Rate limited - implement exponential backoff
                        retry_after = int(response.headers.get('Retry-After', 1))
                        logger.warning(f"{api_name} API rate limited. Retrying after {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                        # Retry the request
                        return await self._make_api_request(api_name, endpoint, payload, headers)
                    elif response.status >= 500:
                        logger.error(f"{api_name} API server error: {response.status}")
                        raise Exception(f"API server error: {response.status}")
                    else:
                        error_text = await response.text()
                        logger.error(f"{api_name} API request failed: {response.status} - {error_text}")
                        raise Exception(f"API request failed: {response.status} - {error_text}")
            except aiohttp.ClientError as e:
                logger.error(f"Network error during {api_name} API request: {str(e)}")
                raise
            except asyncio.TimeoutError:
                logger.error(f"Timeout during {api_name} API request")
                raise Exception("API request timed out")
            except Exception as e:
                logger.error(f"Unexpected error during {api_name} API request: {str(e)}")
                raise

    async def _generate_with_suno(self, config: AudioGenerationConfig) -> AudioResult:
        """
        Generate audio using the Suno API.
        
        Args:
            config: Audio generation configuration
            
        Returns:
            AudioResult containing the generated audio
        """
        api_name = "suno"
        endpoint = self.api_endpoints.get(api_name)
        api_key = self.api_keys.get(api_name)
        
        if not endpoint or not api_key:
            raise Exception(f"{api_name.upper()} API configuration missing")
        
        # Prepare payload for Suno API
        payload = {
            "prompt": config.prompt,
            "duration": config.duration,
            "instrumental": True,
            "model": config.model,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "guidance_scale": config.guidance_scale
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        response_data = await self._make_api_request(api_name, endpoint, payload, headers)
        
        # Extract audio URL and metadata from response
        audio_url = response_data.get("audio_url")
        if not audio_url:
            raise Exception("No audio URL returned from Suno API")
        
        # Download the audio file
        async with self.session.get(audio_url) as audio_response:
            if audio_response.status == 200:
                audio_data = await audio_response.read()
                generation_time = time.time() - start_time
                
                return AudioResult(
                    audio_data=audio_data,
                    metadata={
                        "api_response": response_data,
                        "generation_time": generation_time,
                        "source": "suno"
                    },
                    api_used="suno",
                    generation_time=generation_time
                )
            else:
                raise Exception(f"Failed to download audio from {audio_url}: {audio_response.status}")

    async def _generate_with_udio(self, config: AudioGenerationConfig) -> AudioResult:
        """
        Generate audio using the Udio API.
        
        Args:
            config: Audio generation configuration
            
        Returns:
            AudioResult containing the generated audio
        """
        api_name = "udio"
        endpoint = self.api_endpoints.get(api_name)
        api_key = self.api_keys.get(api_name)
        
        if not endpoint or not api_key:
            raise Exception(f"{api_name.upper()} API configuration missing")
        
        # Prepare payload for Udio API
        payload = {
            "prompt": config.prompt,
            "duration_secs": config.duration,
            "is_instrumental": True,
            "model": config.model,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "cfg_scale": config.guidance_scale
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        response_data = await self._make_api_request(api_name, endpoint, payload, headers)
        
        # Extract audio URL and metadata from response
        clips = response_data.get("clips", [])
        if not clips:
            raise Exception("No audio clips returned from Udio API")
        
        # Use the first clip (main generation)
        clip = clips[0]
        audio_url = clip.get("audio_url")
        if not audio_url:
            raise Exception("No audio URL in clip from Udio API")
        
        # Download the audio file
        async with self.session.get(audio_url) as audio_response:
            if audio_response.status == 200:
                audio_data = await audio_response.read()
                generation_time = time.time() - start_time
                
                return AudioResult(
                    audio_data=audio_data,
                    metadata={
                        "api_response": response_data,
                        "clip_info": clip,
                        "generation_time": generation_time,
                        "source": "udio"
                    },
                    api_used="udio",
                    generation_time=generation_time
                )
            else:
                raise Exception(f"Failed to download audio from {audio_url}: {audio_response.status}")

    async def _generate_with_stable_audio(self, config: AudioGenerationConfig) -> AudioResult:
        """
        Generate audio using the Stable Audio API.
        
        Args:
            config: Audio generation configuration
            
        Returns:
            AudioResult containing the generated audio
        """
        api_name = "stable_audio"
        endpoint = self.api_endpoints.get(api_name)
        api_key = self.api_keys.get(api_name)
        
        if not endpoint or not api_key:
            raise Exception(f"{api_name.upper()} API configuration missing")
        
        # Prepare payload for Stable Audio API
        payload = {
            "prompt": config.prompt,
            "duration": config.duration,
            "is_instrumental": True,
            "model": config.model,
            "preset": "instrumental",
            "lucky": True
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        response_data = await self._make_api_request(api_name, endpoint, payload, headers)
        
        # Extract audio URL and metadata from response
        audio_url = response_data.get("audio_url")
        if not audio_url:
            raise Exception("No audio URL returned from Stable Audio API")
        
        # Download the audio file
        async with self.session.get(audio_url) as audio_response:
            if audio_response.status == 200:
                audio_data = await audio_response.read()
                generation_time = time.time() - start_time
                
                return AudioResult(
                    audio_data=audio_data,
                    metadata={
                        "api_response": response_data,
                        "generation_time": generation_time,
                        "source": "stable_audio"
                    },
                    api_used="stable_audio",
                    generation_time=generation_time
                )
            else:
                raise Exception(f"Failed to download audio from {audio_url}: {audio_response.status}")

    async def generate_audio(self, ambiance_description: str) -> AudioResult:
        """
        Generate an instrumental loop based on an ambiance description.
        
        Args:
            ambiance_description: Description of the ambiance (e.g., "mysterious forest")
            
        Returns:
            AudioResult containing the generated audio
        """
        # Create generation config
        config = AudioGenerationConfig(
            prompt=f"Instrumental music for a {ambiance_description} ambiance",
            duration=self.config.get("audio.loop_duration", 30)
        )
        
        # Generate cache key
        cache_key = self._generate_cache_key(config)
        
        # Check cache first
        cached_result = await self._check_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Initialize session if needed
        if not self.session:
            await self.initialize()
        
        # Try each API in sequence until one succeeds
        apis_to_try = ["suno", "udio", "stable_audio"]
        last_exception = None
        
        for api_name in apis_to_try:
            try:
                logger.info(f"Attempting to generate audio using {api_name.upper()} API")
                
                if api_name == "suno":
                    result = await self._generate_with_suno(config)
                elif api_name == "udio":
                    result = await self._generate_with_udio(config)
                elif api_name == "stable_audio":
                    result = await self._generate_with_stable_audio(config)
                else:
                    continue
                
                # Save to cache
                await self._save_to_cache(cache_key, result.audio_data)
                
                logger.info(f"Successfully generated audio using {api_name.upper()} API")
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Failed to generate audio using {api_name.upper()} API: {str(e)}")
                continue
        
        # If all APIs failed, raise the last exception
        if last_exception:
            raise last_exception
        else:
            raise Exception("No APIs configured for audio generation")