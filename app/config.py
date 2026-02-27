"""
Configuration management for My Rights Keeper application.
Centralizes all configuration settings and environment variables.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class."""

    # API Configuration
    LAW_API_ID: str = os.getenv("LAW_API_ID", "tjr001136")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    # API URLs
    LAW_SEARCH_URL: str = "http://www.law.go.kr/DRF/lawSearch.do"
    LAW_SERVICE_URL: str = "http://www.law.go.kr/DRF/lawService.do"

    # API Parameters
    LAW_API_TARGET: str = "moelCgmExpc"
    LAW_API_TYPE: str = "JSON"
    DEFAULT_DISPLAY_COUNT: int = 20
    MAX_DISPLAY_COUNT: int = 100

    # Request Configuration
    REQUEST_TIMEOUT: int = 30  # seconds
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1  # seconds

    # LLM Configuration
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5

    # Streamlit Configuration
    PAGE_TITLE: str = "My Rights Keeper"
    PAGE_ICON: str = "⚖️"
    LAYOUT: str = "wide"

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration is present.

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        if not cls.LAW_API_ID:
            print("Error: LAW_API_ID is not set in environment variables.")
            return False

        if not cls.GOOGLE_API_KEY:
            print("Error: GOOGLE_API_KEY is not set in environment variables.")
            return False

        return True

    @classmethod
    def get_law_api_params(cls, query: str, display: Optional[int] = None) -> dict:
        """
        Get standard parameters for law API requests.

        Args:
            query: Search query string
            display: Number of results to display (default: DEFAULT_DISPLAY_COUNT)

        Returns:
            dict: API request parameters
        """
        return {
            "OC": cls.LAW_API_ID,
            "target": cls.LAW_API_TARGET,
            "type": cls.LAW_API_TYPE,
            "query": query,
            "display": display or cls.DEFAULT_DISPLAY_COUNT,
        }

    @classmethod
    def get_law_service_params(cls, interpretation_id: str) -> dict:
        """
        Get standard parameters for law service API requests.

        Args:
            interpretation_id: Legal interpretation ID

        Returns:
            dict: API request parameters
        """
        return {
            "OC": cls.LAW_API_ID,
            "target": cls.LAW_API_TARGET,
            "type": cls.LAW_API_TYPE,
            "ID": interpretation_id,
        }


# Create a singleton instance
config = Config()
