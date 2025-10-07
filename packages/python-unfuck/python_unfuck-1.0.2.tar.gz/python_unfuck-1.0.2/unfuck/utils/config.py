"""
Configuration management for unfuck.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class UnfuckConfig:
    """Configuration for unfuck."""
    # AI settings
    ai_enabled: bool = False
    ai_model: str = "llama2"
    ai_base_url: str = "http://localhost:11434"
    
    # Personality settings
    personality_mode: str = "encouraging"
    
    # Fix settings
    auto_backup: bool = True
    max_fix_attempts: int = 3
    confidence_threshold: float = 0.6
    
    # UI settings
    show_animations: bool = True
    verbose_output: bool = False
    color_output: bool = True
    
    # Learning settings
    track_fixes: bool = True
    share_anonymized_data: bool = False
    
    # Advanced settings
    custom_patterns_path: Optional[str] = None
    backup_retention_days: int = 30


class Config:
    """Configuration manager for unfuck."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or str(Path.home() / ".unfuck" / "config.json")
        self.config_dir = Path(self.config_path).parent
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self._config = self._load_config()
    
    def _load_config(self) -> UnfuckConfig:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                return UnfuckConfig(**data)
            except Exception:
                pass
        
        # Return default config
        return UnfuckConfig()
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(asdict(self._config), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return getattr(self._config, key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        if hasattr(self._config, key):
            setattr(self._config, key, value)
            self.save_config()
        else:
            raise ValueError(f"Unknown configuration key: {key}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return asdict(self._config)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self._config = UnfuckConfig()
        self.save_config()
    
    def update_from_dict(self, updates: Dict[str, Any]):
        """Update configuration from dictionary."""
        for key, value in updates.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        self.save_config()
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return any issues."""
        issues = []
        
        # Validate AI settings
        if self._config.ai_enabled:
            if not self._config.ai_model:
                issues.append("AI model not specified")
            if not self._config.ai_base_url:
                issues.append("AI base URL not specified")
        
        # Validate fix settings
        if self._config.max_fix_attempts < 1:
            issues.append("Max fix attempts must be at least 1")
        
        if not 0 <= self._config.confidence_threshold <= 1:
            issues.append("Confidence threshold must be between 0 and 1")
        
        # Validate backup settings
        if self._config.backup_retention_days < 1:
            issues.append("Backup retention days must be at least 1")
        
        return issues
    
    def get_config_summary(self) -> str:
        """Get a summary of current configuration."""
        summary = f"""
Unfuck Configuration Summary:
============================

AI Settings:
  Enabled: {self._config.ai_enabled}
  Model: {self._config.ai_model}
  Base URL: {self._config.ai_base_url}

Personality:
  Mode: {self._config.personality_mode}

Fix Settings:
  Auto Backup: {self._config.auto_backup}
  Max Attempts: {self._config.max_fix_attempts}
  Confidence Threshold: {self._config.confidence_threshold}

UI Settings:
  Animations: {self._config.show_animations}
  Verbose: {self._config.verbose_output}
  Colors: {self._config.color_output}

Learning:
  Track Fixes: {self._config.track_fixes}
  Share Data: {self._config.share_anonymized_data}

Advanced:
  Custom Patterns: {self._config.custom_patterns_path or 'None'}
  Backup Retention: {self._config.backup_retention_days} days
        """
        
        return summary.strip()
