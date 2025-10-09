"""
API client for integrating with job board services
"""

import requests
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

from .config import JobttyConfig
from .display import console, show_error

class JobttyAPI:
    """Unified API client for all job board integrations"""
    
    def __init__(self):
        self.config = JobttyConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Jobtty.io/1.0.0 Terminal Job Board'
        })
        
        # API endpoints
        self.endpoints = self.config.get_api_endpoints()
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 1.0  # seconds
    
    def _rate_limit(self, source: str):
        """Apply rate limiting per source"""
        if source in self.last_request_time:
            elapsed = time.time() - self.last_request_time[source]
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        
        self.last_request_time[source] = time.time()
    
    def _make_request(self, source: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated API request with error handling"""
        self._rate_limit(source)
        
        base_url = self.endpoints.get(source)
        if not base_url:
            raise ValueError(f"Unknown source: {source}")
        
        # Ensure proper URL construction
        if not base_url.endswith('/'):
            base_url += '/'
        url = urljoin(base_url, endpoint)
        
        # Add authentication if available
        headers = {}
        auth_token = self.config.get_auth_token(source)
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            json_data = response.json()
            return json_data
        
        except requests.exceptions.RequestException as e:
            console.print(f"[dim red]API Error ({source}): {str(e)}[/dim red]")
            return None
    
    def search_jobs(self, source: str, search_params: Dict) -> List[Dict]:
        """Search jobs from JobTTY API (single source of truth)"""
        
        if source != "jobtty":
            # For backward compatibility, redirect all sources to jobtty
            source = "jobtty"
        
        # Filter out None/empty values that confuse the API
        clean_params = {}
        for key, value in search_params.items():
            if value is not None and value != "" and value != []:
                # Handle special location parameter with comma-separated values
                if key == "location" and "," in str(value):
                    # For now, pass first location to backend since it doesn't support multi-location search
                    # TODO: Implement client-side filtering for multiple locations
                    locations = str(value).split(",")
                    clean_params[key] = locations[0].strip()
                else:
                    # Keep parameter as backend expects it
                    clean_params[key] = value
        
        # Use terminal/search endpoint for CLI searches
        endpoint = 'terminal/search'
        jobs_data = self._make_request(source, endpoint, clean_params)
        if jobs_data:
            jobs_array = jobs_data.get('jobs', [])
            jobs = self._normalize_jobtty_jobs(jobs_array)
            return jobs
        
        return []
    
    
    def _normalize_jobtty_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Normalize Jobtty.io job data to standard format"""
        normalized = []
        
        for job in jobs:
            # Handle company field - could be string or dict
            company = job.get('company')
            if isinstance(company, dict):
                company_name = company.get('name', 'Unknown Company')
            else:
                company_name = str(company) if company else 'Unknown Company'
            
            # Handle salary field  
            salary = job.get('salary') or job.get('salary_range', '')
            
            # Handle posted date
            posted_date = ''
            if job.get('posted_at'):
                posted_date = job.get('posted_at').split('T')[0]
            elif job.get('created_at'):
                posted_date = job.get('created_at').split('T')[0]
            
            location_value = job.get('location') or ''
            normalized.append({
                'id': job.get('id'),
                'title': job.get('title', 'Untitled Job'),
                'company': company_name,
                'location': location_value or 'N/A',
                'salary': salary,
                'salary_min': job.get('salary_min'),
                'salary_max': job.get('salary_max'),
                'type': 'Full-time',  # Default for now
                'remote': job.get('remote', False) or ('remote' in location_value.lower()),
                'posted_date': posted_date,
                'description': job.get('description', ''),
                'requirements': job.get('requirements', ''),
                'url': job.get('url', ''),
                'category': job.get('category', ''),  # Add category for client-side filtering
                # Premium fields
                'premium': job.get('premium', False),
                'featured': job.get('featured', False),
                'company_logo_ascii': job.get('company_logo_ascii', ''),
                'source_site': job.get('source_site', 'jobtty')
            })
        
        return normalized
    
    
    def get_job_details(self, job_id: int) -> Optional[Dict]:
        """Get detailed information for a specific job from JobTTY API"""
        
        response_data = self._make_request('jobtty', f'jobs/{job_id}')
        if response_data:
            # Individual job API returns job data wrapped in 'data' field
            job_data = response_data.get('data')
            if job_data:
                return self._normalize_jobtty_jobs([job_data])[0]
        
        return None
    
    def apply_to_job(self, job_id: int, application_data: Dict) -> Dict:
        """Submit job application"""
        
        if not self.config.is_authenticated():
            raise Exception("Authentication required")
        
        auth_token = self.config.get_auth_token('jobtty')
        if not auth_token:
            raise Exception("No authentication token available")
        
        # Get user profile to fill in required fields
        profile_response = requests.get(
            f'{self.endpoints["jobtty"]}/auth/profile',
            headers={'Authorization': f'Bearer {auth_token}'},
            timeout=10
        )
        
        if profile_response.status_code != 200:
            raise Exception("Could not get user profile")
        
        profile_data = profile_response.json()
        user = profile_data.get('user', {})
        
        # Check if user has CV attached to profile
        has_cv = user.get('cv_attached', False)
        
        # Ensure cover letter meets minimum length
        cover_letter = application_data.get('cover_letter', '')
        if len(cover_letter) < 50:
            cover_letter = f"{cover_letter} I am very interested in this position and believe my skills and experience make me a great fit for this role. I would love to discuss this opportunity further."
        
        # Prepare application data
        app_data = {
            'name': user.get('name', 'JobTTY User'),
            'email': user.get('email', ''),
            'cover_letter': cover_letter,
        }
        
        # Add CV based on profile status
        if has_cv:
            app_data['cv_text'] = 'Please see my CV attached to my profile'
        else:
            app_data['cv_text'] = 'Submitted via JobTTY CLI - Please contact me for my CV'
        
        try:
            response = requests.post(
                f'{self.endpoints["jobtty"]}/jobs/{job_id}/applications',
                json=app_data,
                headers={
                    'Authorization': f'Bearer {auth_token}',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                error_text = response.text if response.text else f"HTTP {response.status_code}"
                raise Exception(f"Application failed: {error_text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def get_user_applications(self) -> List[Dict]:
        """Get user's job applications"""
        if not self.config.is_authenticated():
            return []
        
        try:
            auth_token = self.config.get_auth_token('jobtty')
            response = requests.get(f'{self.endpoints["jobtty"]}/applications', 
                headers={'Authorization': f'Bearer {auth_token}'}, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError:
                    return []

                if isinstance(data, dict):
                    if isinstance(data.get('data'), list):
                        return data['data']
                    if isinstance(data.get('applications'), list):
                        return data['applications']
                return []
            else:
                return []
        except requests.exceptions.RequestException:
            return []
    
    def get_profile(self) -> Dict:
        """Get user profile information"""
        if not self.config.is_authenticated():
            raise Exception("Authentication required")
        
        auth_token = self.config.get_auth_token('jobtty')
        if not auth_token:
            raise Exception("No authentication token available")
        
        response = requests.get(
            f'{self.endpoints["jobtty"]}/auth/profile',
            headers={'Authorization': f'Bearer {auth_token}'},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get profile: {response.status_code}")
    
    def upload_cv_file(self, cv_path: str) -> Dict:
        """Upload CV file to user profile"""
        if not self.config.is_authenticated():
            raise Exception("Authentication required")
        
        auth_token = self.config.get_auth_token('jobtty')
        if not auth_token:
            raise Exception("No authentication token available")
        
        # Get user ID from profile
        profile_data = self.get_profile()
        user_id = profile_data['user']['id']
        
        # Upload CV file
        with open(cv_path, 'rb') as cv_file:
            files = {'cv': cv_file}
            response = requests.post(
                f'{self.endpoints["jobtty"]}/users/{user_id}/upload_cv',
                headers={'Authorization': f'Bearer {auth_token}'},
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"CV upload failed: {response.text}")
    
    def upload_cv_text(self, cv_text: str) -> Dict:
        """Upload CV as text to user profile"""
        if not self.config.is_authenticated():
            raise Exception("Authentication required")
        
        auth_token = self.config.get_auth_token('jobtty')
        if not auth_token:
            raise Exception("No authentication token available")
        
        # Get user ID from profile
        profile_data = self.get_profile()
        user_id = profile_data['user']['id']
        
        # Create a temporary text file and upload
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(cv_text)
            temp_file.flush()
            
            try:
                result = self.upload_cv_file(temp_file.name)
                return result
            finally:
                os.unlink(temp_file.name)
