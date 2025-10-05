# Google Cloud Configuration for HealthSmart ADK Project
# Copyright 2025 Google LL - Licensed under Apache License, Version 2.0

import os
from dataclasses import dataclass, field
from typing import Dict
from google.auth import default
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get default credentials and project
credentials, project_id = default()


@dataclass
class HealthcareConfig:
    """
    Configuration for HealthSmart ADK healthcare assistant.

    Follows ADK best practices using dataclass pattern for type safety,
    validation, and better IDE support.
    """

    # Google Cloud settings
    google_cloud_project: str = field(
        default_factory=lambda: os.environ.get("GOOGLE_CLOUD_PROJECT", project_id)
    )
    google_cloud_location: str = field(
        default_factory=lambda: os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    )
    google_genai_use_vertexai: str = field(
        default_factory=lambda: os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "True")
    )

    # Gemini API Key (overrides Vertex AI if provided)
    gemini_api_key: str = field(
        default_factory=lambda: os.environ.get("GEMINI_API_KEY", "")
    )

    # Agent configuration
    default_model: str = "gemini-2.5-flash"  # Updated to stable production model
    app_name: str = "healthcare_assistant"

    # Session management
    session_timeout_minutes: int = 30
    session_cleanup_interval_minutes: int = 5

    # Data paths (legacy CSV - kept for backward compatibility)
    csv_paths: Dict[str, str] = field(default_factory=lambda: {
        'initial_use_cases': 'data/Marketplace _ Prodiges Health - Inital Use Cases.csv',
        'questions': 'data/Marketplace _ Prodiges Health - Questions.csv',
        'rpm_specific': 'data/Marketplace _ Prodiges Health - RPM Specific.csv'
    })

    # JSON rules directory
    rules_dir: str = "rules"

    # Service types
    service_types: Dict[str, str] = field(default_factory=lambda: {
        "RPM": "Remote Patient Monitoring (RPM)",
        "TELEHEALTH": "Telehealth / Virtual Primary Care",
        "INSURANCE": "Insurance Enrollment",
        "PHARMACY": "Pharmacy Savings",
        "WELLNESS": "Wellness Programs"
    })

    def __post_init__(self):
        """Post-initialization: Configure environment based on API key."""
        if self.gemini_api_key:
            # If Gemini API key is provided, use it instead of Vertex AI
            self.google_genai_use_vertexai = "False"
            # Set the API key for google-generativeai
            os.environ["GOOGLE_API_KEY"] = self.gemini_api_key
            # Also set for google-genai compatibility
            os.environ["GEMINI_API_KEY"] = self.gemini_api_key

        # Print configuration summary
        print(f"🔧 HealthSmart ADK Configuration Loaded:")
        print(f"   Project: {self.google_cloud_project}")
        print(f"   Location: {self.google_cloud_location}")
        print(f"   Using Vertex AI: {self.google_genai_use_vertexai}")
        print(f"   Model: {self.default_model}")


# Create global config instance
config = HealthcareConfig()

# ============================================================================
# BACKWARD COMPATIBILITY EXPORTS
# For existing code that imports individual variables
# ============================================================================

GOOGLE_CLOUD_PROJECT = config.google_cloud_project
GOOGLE_CLOUD_LOCATION = config.google_cloud_location
GOOGLE_GENAI_USE_VERTEXAI = config.google_genai_use_vertexai
GEMINI_API_KEY = config.gemini_api_key
DEFAULT_MODEL = config.default_model
APP_NAME = config.app_name
CSV_PATHS = config.csv_paths
SERVICE_TYPES = config.service_types


__all__ = [
    "config",
    "HealthcareConfig",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
    "GOOGLE_GENAI_USE_VERTEXAI",
    "GEMINI_API_KEY",
    "DEFAULT_MODEL",
    "APP_NAME",
    "CSV_PATHS",
    "SERVICE_TYPES"
]
