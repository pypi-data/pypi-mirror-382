"""
Vaultik API Client
"""

import os
import time
import requests
from typing import List, Dict, Optional, Callable, Union
from pathlib import Path

from .exceptions import (
    VaultikAPIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    JobFailedError
)


class VaultikClient:
    """Client for interacting with Vaultik AI Authentication API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.vaultik.com",
        timeout: int = 60
    ):
        """
        Initialize Vaultik API client
        
        Args:
            api_key: API key (or set VAULTIK_API_KEY env var)
            base_url: API base URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.environ.get('VAULTIK_API_KEY')
        if not self.api_key:
            raise ValueError('API key required. Provide api_key parameter or set VAULTIK_API_KEY environment variable.')
        
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = {'X-API-Key': self.api_key}
    
    def create_analysis(
        self,
        image_paths: List[Union[str, Path]],
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Create a new certificate analysis job
        
        Args:
            image_paths: List of image file paths
            metadata: Product metadata (brand, model, etc.)
        
        Returns:
            Job ID string
        
        Raises:
            AuthenticationError: Invalid API key
            ValidationError: Invalid parameters
            RateLimitError: Rate limit exceeded
            VaultikAPIError: Other API errors
        """
        files = []
        try:
            files = [('images', open(path, 'rb')) for path in image_paths]
            data = metadata or {}
            
            response = requests.post(
                f'{self.base_url}/api/certificates/analyze',
                files=files,
                data=data,
                headers=self.headers,
                timeout=self.timeout
            )
            
            self._handle_response_errors(response)
            
            result = response.json()
            return result['jobId']
        
        finally:
            # Always close file handles
            for _, file in files:
                try:
                    file.close()
                except:
                    pass
    
    def get_job_status(self, job_id: str) -> Dict:
        """
        Get the status of an analysis job
        
        Args:
            job_id: Job ID from create_analysis
        
        Returns:
            Job status dictionary
        
        Raises:
            VaultikAPIError: API error occurred
        """
        response = requests.get(
            f'{self.base_url}/api/certificates/analyze/{job_id}',
            headers=self.headers,
            timeout=30
        )
        
        self._handle_response_errors(response)
        
        return response.json()['job']
    
    def submit_additional_photos(
        self,
        job_id: str,
        image_paths: List[Union[str, Path]]
    ) -> Dict:
        """
        Submit additional photos for photo challenge
        
        Args:
            job_id: Job ID
            image_paths: List of additional image paths
        
        Returns:
            Response dictionary
        """
        files = []
        try:
            files = [('images', open(path, 'rb')) for path in image_paths]
            
            response = requests.post(
                f'{self.base_url}/api/certificates/analyze/{job_id}/additional-photos',
                files=files,
                headers=self.headers,
                timeout=self.timeout
            )
            
            self._handle_response_errors(response)
            
            return response.json()
        
        finally:
            for _, file in files:
                try:
                    file.close()
                except:
                    pass
    
    def poll_for_completion(
        self,
        job_id: str,
        on_progress: Optional[Callable[[Dict], None]] = None,
        interval: float = 5.0,
        timeout: float = 600.0
    ) -> Dict:
        """
        Poll job status until completion
        
        Args:
            job_id: Job ID to poll
            on_progress: Callback function for progress updates
            interval: Polling interval in seconds
            timeout: Maximum time to wait in seconds
        
        Returns:
            Final job result
        
        Raises:
            JobFailedError: Job failed
            TimeoutError: Polling timeout exceeded
        """
        start_time = time.time()
        
        while True:
            # Check timeout
            if time.time() - start_time > timeout:
                raise TimeoutError(f'Polling timeout exceeded ({timeout}s)')
            
            job = self.get_job_status(job_id)
            
            # Call progress callback
            if on_progress:
                on_progress(job)
            
            # Check status
            if job['status'] == 'completed':
                return job
            
            if job['status'] == 'failed':
                raise JobFailedError(job.get('error', 'Job failed'))
            
            if job['status'] == 'awaiting_additional_photos':
                return job
            
            # Wait before next poll
            time.sleep(interval)
    
    def analyze(
        self,
        image_paths: List[Union[str, Path]],
        metadata: Optional[Dict] = None,
        on_progress: Optional[Callable[[Dict], None]] = None,
        on_photo_challenge: Optional[Callable[[List], List[Union[str, Path]]]] = None
    ) -> Dict:
        """
        Complete analysis workflow with automatic handling
        
        Args:
            image_paths: Image file paths
            metadata: Product metadata
            on_progress: Progress callback
            on_photo_challenge: Photo challenge callback (returns additional image paths)
        
        Returns:
            Final certificate result
        
        Example:
            >>> client = VaultikClient(api_key='vaultik_...')
            >>> result = client.analyze(
            ...     ['watch1.jpg', 'watch2.jpg'],
            ...     {'productBrand': 'Rolex'}
            ... )
            >>> print(result['certificateId'])
        """
        # Create job
        job_id = self.create_analysis(image_paths, metadata)
        
        # Poll for completion
        result = self.poll_for_completion(job_id, on_progress=on_progress)
        
        # Handle photo challenge
        if result['status'] == 'awaiting_additional_photos':
            if on_photo_challenge:
                photo_requests = result.get('photoRequests', [])
                additional_paths = on_photo_challenge(photo_requests)
                
                # Submit additional photos
                self.submit_additional_photos(job_id, additional_paths)
                
                # Continue polling
                result = self.poll_for_completion(job_id, on_progress=on_progress)
            else:
                # No handler provided, return current state
                return result
        
        return result
    
    def health_check(self) -> bool:
        """
        Check if API is healthy
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = requests.get(
                f'{self.base_url}/api/health',
                timeout=10
            )
            return response.status_code == 200 and response.json().get('status') == 'healthy'
        except:
            return False
    
    def _handle_response_errors(self, response: requests.Response) -> None:
        """Handle HTTP errors and raise appropriate exceptions"""
        if response.status_code == 401:
            raise AuthenticationError('Invalid API key')
        elif response.status_code == 429:
            raise RateLimitError('Rate limit exceeded. Please wait before retrying.')
        elif response.status_code == 400:
            error_data = response.json() if response.content else {}
            raise ValidationError(error_data.get('message', 'Invalid request parameters'))
        elif not response.ok:
            error_data = response.json() if response.content else {}
            raise VaultikAPIError(
                error_data.get('message', f'API error: {response.status_code}'),
                status_code=response.status_code
            )
