from typing import Dict, Any, Optional
from pydantic import BaseModel
import yaml

class ProviderConfig(BaseModel):
    type: str
    endpoint: str
    method: str = "POST"
    headers: Optional[Dict[str, str]] = {}
    body_template: Optional[str] = None
    response_path: Optional[str] = None

class Settings(BaseModel):
    providers: Dict[str, ProviderConfig] = {}

    @classmethod
    def load(cls, path: str):
        with open(path, 'r') as f:
            data = yaml.safe_load(f) or {}
        # Normalize providers
        providers = {}
        for k, v in data.get('providers', {}).items():
            providers[k] = ProviderConfig(**v)
        return cls(providers=providers)
