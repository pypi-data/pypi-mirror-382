import os
from typing import Dict, Any

class ConfigLoader:
    def __init__(self):
        self.config = {}
        
    def load_env(self):
        return dict(os.environ)
    
    def merge_configs(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for config in configs:
            result.update(config)
        return result
