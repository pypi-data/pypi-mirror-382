from typing import Dict, Any
import yaml
import json
from snapqrpy.utils.logger import Logger

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.logger = Logger("ConfigManager")
        self.config: Dict[str, Any] = {}
        
    def load_yaml(self, path: str) -> Dict[str, Any]:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def load_json(self, path: str) -> Dict[str, Any]:
        with open(path, 'r') as f:
            return json.load(f)
    
    def save_yaml(self, data: Dict[str, Any], path: str):
        with open(path, 'w') as f:
            yaml.dump(data, f)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
