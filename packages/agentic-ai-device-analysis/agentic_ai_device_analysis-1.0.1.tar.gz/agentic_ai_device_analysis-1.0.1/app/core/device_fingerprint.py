from typing import Dict, Optional, List, Any
from user_agents import parse
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib
import json

class DeviceFingerprint(BaseModel):
    user_agent: str
    ip_address: str
    screen_resolution: Optional[str] = None
    color_depth: Optional[int] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    platform: Optional[str] = None
    plugins: Optional[list] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    session_id: Optional[str] = None
    
    # Enhanced attributes for AI analysis
    canvas_fingerprint: Optional[str] = None
    webgl_fingerprint: Optional[str] = None
    fonts: Optional[List[str]] = None
    connection_type: Optional[str] = None
    battery_level: Optional[float] = None
    touch_support: Optional[bool] = None
    hardware_concurrency: Optional[int] = None
    device_memory: Optional[int] = None
    do_not_track: Optional[bool] = None
    ad_block: Optional[bool] = None
    
    # Behavioral attributes
    time_on_page: Optional[float] = None
    scroll_patterns: Optional[List[Dict[str, float]]] = None
    click_patterns: Optional[List[Dict[str, Any]]] = None
    form_fill_speed: Optional[float] = None
    
    # Security attributes
    is_vpn: Optional[bool] = None
    is_tor: Optional[bool] = None
    is_proxy: Optional[bool] = None
    threat_score: Optional[float] = Field(None, ge=0.0, le=1.0)

    def parse_user_agent(self) -> Dict:
        """Parse user agent string to extract device information."""
        ua = parse(self.user_agent)
        return {
            "browser": {
                "family": ua.browser.family,
                "version": ua.browser.version_string
            },
            "os": {
                "family": ua.os.family,
                "version": ua.os.version_string
            },
            "device": {
                "family": ua.device.family,
                "brand": ua.device.brand,
                "model": ua.device.model
            },
            "is_mobile": ua.is_mobile,
            "is_tablet": ua.is_tablet,
            "is_pc": ua.is_pc
        }
    
    def generate_fingerprint_hash(self) -> str:
        """Generate a unique hash based on device attributes."""
        # Create a subset of attributes that are stable across sessions
        stable_attributes = {
            "user_agent": self.user_agent,
            "screen_resolution": self.screen_resolution,
            "color_depth": self.color_depth,
            "timezone": self.timezone,
            "language": self.language,
            "platform": self.platform,
            "canvas_fingerprint": self.canvas_fingerprint,
            "webgl_fingerprint": self.webgl_fingerprint,
            "fonts": self.fonts,
            "hardware_concurrency": self.hardware_concurrency,
            "device_memory": self.device_memory
        }
        
        # Convert to JSON string and hash
        attributes_json = json.dumps(stable_attributes, sort_keys=True)
        return hashlib.sha256(attributes_json.encode()).hexdigest()
    
    def calculate_uniqueness_score(self) -> float:
        """Calculate how unique this device fingerprint is (0-1 scale)."""
        # Count how many identifying attributes are present
        attributes = [
            self.screen_resolution,
            self.color_depth,
            self.timezone,
            self.language,
            self.platform,
            self.plugins,
            self.canvas_fingerprint,
            self.webgl_fingerprint,
            self.fonts,
            self.hardware_concurrency,
            self.device_memory
        ]
        
        # Count non-None attributes
        present_attributes = sum(1 for attr in attributes if attr is not None)
        
        # Calculate score based on number of attributes present
        # More attributes = more unique fingerprint
        return min(1.0, present_attributes / 10)

    def to_dict(self) -> Dict:
        """Convert fingerprint to dictionary format with parsed user agent info and additional metrics."""
        base_dict = self.model_dump()
        base_dict["parsed_user_agent"] = self.parse_user_agent()
        base_dict["fingerprint_hash"] = self.generate_fingerprint_hash()
        base_dict["uniqueness_score"] = self.calculate_uniqueness_score()
        return base_dict