"""
Data models for the SofaScore scraper library
"""
from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class FormatOptions:
    """Options for formatting and saving API responses"""
    format_type: Literal["json", "csv"] = "json"
    save_to_file: bool = False
    filename: str = "output"


@dataclass
class SofascrapeConfig:
    """Configuration options for the Sofascrape client"""
    base_url: str = "https://www.sofascore.com"
    headless: bool = True
    timeout: int = 30000  # 30 seconds timeout
    user_agent: Optional[str] = None
    max_retries: int = 3
    delay_between_retries: float = 1.0