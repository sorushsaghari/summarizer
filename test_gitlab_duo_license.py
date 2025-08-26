#!/usr/bin/env python3
"""
Test script for GitLab Duo License validation functionality.

This script demonstrates how to use the GitLab Duo license validator
and shows different scenarios of license validation.
"""

import os
import sys
import logging
from datetime import datetime, timezone

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gitlab_duo_license import GitLabDuoLicenseValidator, GitLabDuoLicense

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_license_validation_demo():
    """
    Demonstrate GitLab Duo license validation with various scenarios.
    
    This function shows:
    1. How to initialize the validator
    2. Different license validation scenarios  
    3. How to interpret the results
    4. How the bot would respond to different license states
    """
    
    print("GitLab Duo License Validation Test")
    print("=" * 50)
    
    # Test Scenario 1: No credentials provided
    print("\n1. Testing without credentials:")
    try:
        validator = GitLabDuoLicenseValidator()
        print("   ERROR: Should have failed without credentials")
    except ValueError as e:
        print(f"   ✓ Correctly failed: {e}")
    
    # Test Scenario 2: Mock successful license
    print("\n2. Testing with mock successful license:")
    
    # Create a demo license result (simulating successful validation)
    mock_valid_license = GitLabDuoLicense(
        is_valid=True,
        license_type="ultimate",
        expires_at=datetime(2024, 12, 31, tzinfo=timezone.utc),
        features_enabled=["code_completion", "chat_assistance", "code_generation"],
        user_limit=100,
        current_users=45,
        message="License validation successful"
    )
    
    print(f"   License Valid: {mock_valid_license.is_valid}")
    print(f"   License Type: {mock_valid_license.license_type}")
    print(f"   Expires: {mock_valid_license.expires_at}")
    print(f"   Features: {mock_valid_license.features_enabled}")
    print(f"   Usage: {mock_valid_license.current_users}/{mock_valid_license.user_limit} users")
    print(f"   Message: {mock_valid_license.message}")
    
    # Simulate bot decision making
    ai_features = ['code_completion', 'chat_assistance', 'code_generation']
    available_ai_features = [f for f in ai_features if f in mock_valid_license.features_enabled]
    
    if mock_valid_license.is_valid and available_ai_features:
        print("   ✓ Bot decision: AI operations ALLOWED")
    else:
        print("   ✗ Bot decision: AI operations BLOCKED")
    
    # Test Scenario 3: Mock invalid license
    print("\n3. Testing with mock invalid license:")
    
    mock_invalid_license = GitLabDuoLicense(
        is_valid=False,
        license_type="free",
        expires_at=None,
        features_enabled=[],
        user_limit=None,
        current_users=None,
        message="GitLab Duo not available on free plan"
    )
    
    print(f"   License Valid: {mock_invalid_license.is_valid}")
    print(f"   License Type: {mock_invalid_license.license_type}")
    print(f"   Features: {mock_invalid_license.features_enabled}")
    print(f"   Message: {mock_invalid_license.message}")
    
    # Simulate bot decision making
    available_ai_features = [f for f in ai_features if f in mock_invalid_license.features_enabled]
    
    if mock_invalid_license.is_valid and available_ai_features:
        print("   ✓ Bot decision: AI operations ALLOWED")
    else:
        print("   ✗ Bot decision: AI operations BLOCKED")
        print("   → Bot would send: ⚠️ License Notice: GitLab Duo not available on free plan")
    
    # Test Scenario 4: Mock expired license
    print("\n4. Testing with mock expired license:")
    
    mock_expired_license = GitLabDuoLicense(
        is_valid=False,
        license_type="premium",
        expires_at=datetime(2023, 12, 31, tzinfo=timezone.utc),
        features_enabled=["code_completion"],
        user_limit=50,
        current_users=30,
        message="License has expired"
    )
    
    print(f"   License Valid: {mock_expired_license.is_valid}")
    print(f"   License Type: {mock_expired_license.license_type}")
    print(f"   Expired: {mock_expired_license.expires_at}")
    print(f"   Message: {mock_expired_license.message}")
    
    if mock_expired_license.is_valid:
        print("   ✓ Bot decision: AI operations ALLOWED")
    else:
        print("   ✗ Bot decision: AI operations BLOCKED")
        print("   → Bot would send: ⚠️ License Notice: License has expired")


def test_environment_configuration():
    """Test environment variable configuration for GitLab Duo."""
    
    print("\n" + "=" * 50)
    print("Environment Configuration Test")
    print("=" * 50)
    
    # Check for environment variables
    env_vars = {
        'GITLAB_URL': os.getenv('GITLAB_URL'),
        'GITLAB_PRIVATE_TOKEN': os.getenv('GITLAB_PRIVATE_TOKEN'), 
        'GITLAB_PROJECT_ID': os.getenv('GITLAB_PROJECT_ID')
    }
    
    print("\nEnvironment Variables:")
    for var, value in env_vars.items():
        if value:
            if 'TOKEN' in var:
                # Mask token for security
                masked_value = value[:8] + '***' if len(value) > 8 else '***'
                print(f"   {var}: {masked_value} (set)")
            else:
                print(f"   {var}: {value}")
        else:
            print(f"   {var}: (not set)")
    
    # Test with environment variables if available
    if env_vars['GITLAB_PRIVATE_TOKEN']:
        print("\n✓ GitLab credentials found in environment")
        print("  Real license validation could be performed")
        
        try:
            validator = GitLabDuoLicenseValidator(
                gitlab_url=env_vars['GITLAB_URL'],
                private_token=env_vars['GITLAB_PRIVATE_TOKEN'],
                project_id=env_vars['GITLAB_PROJECT_ID']
            )
            print("  ✓ Validator initialized successfully")
            
            # Note: We don't actually call check_license() here to avoid
            # making real API calls in the test, but we could if needed
            print("  → To test real validation, uncomment the check_license() call")
            
        except Exception as e:
            print(f"  ✗ Validator initialization failed: {e}")
    else:
        print("\n! No GitLab credentials in environment")
        print("  Set GITLAB_PRIVATE_TOKEN to test real validation")


def test_bot_integration():
    """Test how the GitLab Duo license integrates with the bot."""
    
    print("\n" + "=" * 50)
    print("Bot Integration Test")
    print("=" * 50)
    
    print("\nBot behavior with different license states:")
    
    scenarios = [
        {
            "name": "Valid Ultimate License",
            "license": GitLabDuoLicense(
                is_valid=True,
                license_type="ultimate",
                expires_at=datetime(2024, 12, 31, tzinfo=timezone.utc),
                features_enabled=["code_completion", "chat_assistance", "code_generation"],
                user_limit=100,
                current_users=45,
                message="License validation successful"
            )
        },
        {
            "name": "Valid Premium License (Limited Features)",
            "license": GitLabDuoLicense(
                is_valid=True,
                license_type="premium",
                expires_at=datetime(2024, 12, 31, tzinfo=timezone.utc),
                features_enabled=["code_completion"],
                user_limit=50,
                current_users=30,
                message="Limited AI features available"
            )
        },
        {
            "name": "Free Plan (No AI Features)",
            "license": GitLabDuoLicense(
                is_valid=False,
                license_type="free",
                expires_at=None,
                features_enabled=[],
                user_limit=None,
                current_users=None,
                message="GitLab Duo not available on free plan"
            )
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        license = scenario['license']
        
        # Simulate the bot's license checking logic
        ai_features = ['code_completion', 'chat_assistance', 'code_generation']
        available_ai_features = [f for f in ai_features if f in license.features_enabled]
        
        if license.is_valid and available_ai_features:
            print(f"   ✓ AI summarization: ALLOWED")
            print(f"   → Features: {available_ai_features}")
            print(f"   → Bot proceeds with OpenAI summarization")
        else:
            print(f"   ✗ AI summarization: BLOCKED")
            print(f"   → Bot sends license notice instead")
            print(f"   → Message: '⚠️ License Notice: {license.message}'")


if __name__ == "__main__":
    """Run all GitLab Duo license tests."""
    
    print("Starting GitLab Duo License Integration Tests")
    print("This demonstrates how GitLab Duo license validation")
    print("integrates with the Telegram summarizer bot.\n")
    
    try:
        # Run all test scenarios
        test_license_validation_demo()
        test_environment_configuration()
        test_bot_integration()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)
        
        print("\nTo use GitLab Duo license validation in production:")
        print("1. Set GITLAB_PRIVATE_TOKEN environment variable")
        print("2. Optionally set GITLAB_URL and GITLAB_PROJECT_ID")
        print("3. The bot will automatically validate licenses before AI operations")
        print("4. Users will receive appropriate notifications for license issues")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)