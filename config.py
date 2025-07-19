import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    """Central configuration for InsurIQ system"""

    # API Configuration
    API_KEYS = {
        "FEMA": os.getenv("FEMA_API_KEY"),
        "ATTOM": os.getenv("ATTOM_API_KEY"),
        "HAZARDHUB": os.getenv("HAZARDHUB_TOKEN"),
        "SNOWFLAKE": os.getenv("SNOWFLAKE_PASSWORD")
    }

    # Snowflake Configuration
    SNOWFLAKE_CONFIG = {
        # "user": os.getenv("SNOWFLAKE_USER"),
        # "password": API_KEYS["SNOWFLAKE"],
        # "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        # "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        # "database": os.getenv("SNOWFLAKE_DATABASE"),
        # "schema": os.getenv("SNOWFLAKE_SCHEMA")
        "user": "",
        "password": "",
        "account": "",
        "warehouse": "",
        "database": "",
        "schema": ""
    }

    # Risk Calculation Parameters
    RISK_WEIGHTS = {
        "fire": 0.25,
        "flood": 0.30,
        "windstorm": 0.20,
        "earthquake": 0.10,
        "construction": 0.10,
        "claims": 0.05
    }

    @classmethod
    def validate(cls):
        """Validate all required configurations are present"""
        missing = [k for k, v in cls.API_KEYS.items() if not v]
        if missing:
            raise ValueError(f"Missing API keys for: {', '.join(missing)}")

# Validate on import
Config.validate()