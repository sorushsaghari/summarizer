# src/gitlab_duo_license.py
"""
GitLab Duo License Validation Module

This module provides functionality to check GitLab Duo license status
and ensure AI-powered features are used within licensing constraints.

GitLab Duo is GitLab's suite of AI-powered features that includes:
- Code completion
- Chat assistance  
- Code generation
- Security scanning
- And other AI-enhanced capabilities

License validation ensures proper usage rights before accessing AI features.
"""

import os
import requests
from typing import Dict, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


@dataclass
class GitLabDuoLicense:
    """Represents GitLab Duo license information."""
    is_valid: bool
    license_type: str
    expires_at: Optional[datetime]
    features_enabled: list
    user_limit: Optional[int]
    current_users: Optional[int]
    message: str


class GitLabDuoLicenseValidator:
    """
    Validates GitLab Duo license status through GitLab API.
    
    This class provides methods to check if GitLab Duo features
    can be used based on current license status.
    """
    
    def __init__(self, gitlab_url: str = None, private_token: str = None, project_id: str = None):
        """
        Initialize GitLab Duo License Validator.
        
        Args:
            gitlab_url: GitLab instance URL (e.g., 'https://gitlab.com' or self-hosted)
            private_token: GitLab personal access token with API access
            project_id: GitLab project ID for license validation
        """
        self.gitlab_url = gitlab_url or os.getenv('GITLAB_URL', 'https://gitlab.com')
        self.private_token = private_token or os.getenv('GITLAB_PRIVATE_TOKEN')
        self.project_id = project_id or os.getenv('GITLAB_PROJECT_ID')
        
        if not self.private_token:
            raise ValueError("GitLab private token is required for license validation")
            
        self.headers = {
            'Authorization': f'Bearer {self.private_token}',
            'Content-Type': 'application/json'
        }
    
    def check_license(self) -> GitLabDuoLicense:
        """
        Check GitLab Duo license status.
        
        Returns:
            GitLabDuoLicense: License validation result
        """
        try:
            # Check instance license for SaaS/self-hosted
            license_info = self._get_instance_license()
            
            if license_info:
                return self._parse_license_response(license_info)
            else:
                # Fallback: Check project-level features if instance check fails
                return self._check_project_features()
                
        except Exception as e:
            logger.error(f"Failed to validate GitLab Duo license: {e}")
            return GitLabDuoLicense(
                is_valid=False,
                license_type="unknown",
                expires_at=None,
                features_enabled=[],
                user_limit=None,
                current_users=None,
                message=f"License validation failed: {str(e)}"
            )
    
    def _get_instance_license(self) -> Optional[Dict]:
        """Get license information from GitLab instance."""
        try:
            # Try to get license info (requires admin access)
            url = f"{self.gitlab_url}/api/v4/license"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                logger.warning("No admin access to check instance license, trying alternative methods")
                return None
            else:
                logger.warning(f"Failed to get license info: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request failed when checking license: {e}")
            return None
    
    def _check_project_features(self) -> GitLabDuoLicense:
        """Check available features at project level."""
        try:
            if not self.project_id:
                return GitLabDuoLicense(
                    is_valid=False,
                    license_type="unknown",
                    expires_at=None,
                    features_enabled=[],
                    user_limit=None,
                    current_users=None,
                    message="Project ID not provided for feature checking"
                )
            
            # Get project information to check available features
            url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                project_data = response.json()
                return self._analyze_project_features(project_data)
            else:
                return GitLabDuoLicense(
                    is_valid=False,
                    license_type="unknown",
                    expires_at=None,
                    features_enabled=[],
                    user_limit=None,
                    current_users=None,
                    message=f"Failed to access project: {response.status_code}"
                )
                
        except requests.RequestException as e:
            logger.error(f"Failed to check project features: {e}")
            return GitLabDuoLicense(
                is_valid=False,
                license_type="unknown",
                expires_at=None,
                features_enabled=[],
                user_limit=None,
                current_users=None,
                message=f"Project feature check failed: {str(e)}"
            )
    
    def _parse_license_response(self, license_data: Dict) -> GitLabDuoLicense:
        """Parse GitLab license API response."""
        try:
            # Extract license information
            is_valid = license_data.get('active', False)
            license_type = license_data.get('plan', 'unknown')
            
            # Parse expiration date
            expires_at = None
            if 'expires_at' in license_data and license_data['expires_at']:
                try:
                    expires_at = datetime.fromisoformat(
                        license_data['expires_at'].replace('Z', '+00:00')
                    )
                except ValueError:
                    logger.warning("Failed to parse license expiration date")
            
            # Check for GitLab Duo specific features
            duo_features = self._extract_duo_features(license_data)
            
            # User limits
            user_limit = license_data.get('user_limit')
            current_users = license_data.get('active_users')
            
            message = "License validation successful"
            if not is_valid:
                message = "License is not active"
            elif expires_at and expires_at < datetime.now(timezone.utc):
                message = "License has expired"
                is_valid = False
            
            return GitLabDuoLicense(
                is_valid=is_valid,
                license_type=license_type,
                expires_at=expires_at,
                features_enabled=duo_features,
                user_limit=user_limit,
                current_users=current_users,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Failed to parse license response: {e}")
            return GitLabDuoLicense(
                is_valid=False,
                license_type="unknown",
                expires_at=None,
                features_enabled=[],
                user_limit=None,
                current_users=None,
                message=f"License parsing failed: {str(e)}"
            )
    
    def _analyze_project_features(self, project_data: Dict) -> GitLabDuoLicense:
        """Analyze project data to determine available Duo features."""
        # This is a simplified check based on project tier/features
        # In practice, you'd check specific feature flags or endpoints
        
        namespace = project_data.get('namespace', {})
        plan = namespace.get('plan', 'free').lower()
        
        # GitLab Duo is typically available in Premium/Ultimate tiers
        duo_available = plan in ['premium', 'ultimate', 'gold', 'silver']
        
        features = []
        if duo_available:
            # These would be actual feature checks in a real implementation
            features = ['code_completion', 'chat_assistance', 'code_generation']
        
        return GitLabDuoLicense(
            is_valid=duo_available,
            license_type=plan,
            expires_at=None,  # Project-level checks don't usually have expiration
            features_enabled=features,
            user_limit=None,
            current_users=None,
            message=f"Project-level validation: {'GitLab Duo available' if duo_available else 'GitLab Duo not available'} on {plan} plan"
        )
    
    def _extract_duo_features(self, license_data: Dict) -> list:
        """Extract GitLab Duo specific features from license data."""
        features = []
        
        # Check for AI/ML related features in license
        # This would need to be updated based on actual GitLab API responses
        license_features = license_data.get('features', {})
        
        duo_feature_mapping = {
            'code_suggestions': 'code_completion',
            'ai_assist': 'chat_assistance', 
            'code_generation': 'code_generation',
            'security_ai': 'security_scanning',
            'vulnerability_ai': 'vulnerability_detection'
        }
        
        for gitlab_feature, duo_feature in duo_feature_mapping.items():
            if license_features.get(gitlab_feature, False):
                features.append(duo_feature)
        
        return features
    
    def can_use_ai_features(self) -> bool:
        """
        Quick check if AI features can be used.
        
        Returns:
            bool: True if GitLab Duo features are available
        """
        license = self.check_license()
        return license.is_valid and len(license.features_enabled) > 0


def validate_gitlab_duo_license(gitlab_url: str = None, 
                                private_token: str = None, 
                                project_id: str = None) -> GitLabDuoLicense:
    """
    Convenience function to validate GitLab Duo license.
    
    Args:
        gitlab_url: GitLab instance URL
        private_token: GitLab private access token
        project_id: GitLab project ID
        
    Returns:
        GitLabDuoLicense: License validation result
    """
    validator = GitLabDuoLicenseValidator(gitlab_url, private_token, project_id)
    return validator.check_license()


# Example usage and demonstration
if __name__ == "__main__":
    """
    Example usage of GitLab Duo License Validator.
    
    To use this module:
    1. Set environment variables:
       - GITLAB_URL (optional, defaults to https://gitlab.com)
       - GITLAB_PRIVATE_TOKEN (required)
       - GITLAB_PROJECT_ID (optional, for project-level checks)
    
    2. Create validator and check license:
       validator = GitLabDuoLicenseValidator()
       license_info = validator.check_license()
       
    3. Use license information to control AI feature access:
       if license_info.is_valid:
           # Proceed with AI-powered operations
           pass
       else:
           # Handle license validation failure
           print(f"License issue: {license_info.message}")
    """
    
    # Demo with mock data (since we don't have real GitLab credentials)
    print("GitLab Duo License Validator Demo")
    print("=" * 40)
    
    try:
        # This would normally use real environment variables
        validator = GitLabDuoLicenseValidator(
            gitlab_url="https://gitlab.com",
            private_token="demo_token",  # This would be a real token
            project_id="demo_project"
        )
        
        print("Note: This is a demo. Real usage requires valid GitLab credentials.")
        print("\nTo use in production:")
        print("1. Set GITLAB_PRIVATE_TOKEN environment variable")
        print("2. Optionally set GITLAB_URL and GITLAB_PROJECT_ID")
        print("3. Call validator.check_license() before AI operations")
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nDemo GitLabDuoLicense object:")
        
        # Show what a license object looks like
        demo_license = GitLabDuoLicense(
            is_valid=True,
            license_type="ultimate",
            expires_at=datetime(2024, 12, 31, tzinfo=timezone.utc),
            features_enabled=["code_completion", "chat_assistance", "code_generation"],
            user_limit=100,
            current_users=45,
            message="License validation successful"
        )
        
        print(f"  Valid: {demo_license.is_valid}")
        print(f"  Type: {demo_license.license_type}")
        print(f"  Expires: {demo_license.expires_at}")
        print(f"  Features: {demo_license.features_enabled}")
        print(f"  Users: {demo_license.current_users}/{demo_license.user_limit}")
        print(f"  Message: {demo_license.message}")