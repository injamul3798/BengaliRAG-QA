from typing import Dict, Any
from pathlib import Path
import json
import os

def load_config() -> Dict[str, Any]:
    """Load configuration from config file."""
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

def ensure_data_directory():
    """Ensure data directory exists."""
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir(parents=True)

def setup_logging():
    """Setup logging configuration."""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)
