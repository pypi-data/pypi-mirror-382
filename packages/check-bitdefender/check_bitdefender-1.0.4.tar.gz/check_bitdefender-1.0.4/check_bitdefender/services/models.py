"""Data models for check_bitdefender."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class OnboardingStatus(Enum):
    """Onboarding status enumeration."""

    ONBOARDED = 0
    INSUFFICIENT_INFO = 1
    UNKNOWN = 2


@dataclass
class Endpoint:
    """Endpoint data model."""

    id: str
    computer_dns_name: str
    last_seen: Optional[datetime] = None
    onboarding_status: Optional[OnboardingStatus] = None


@dataclass
class Vulnerability:
    """Vulnerability data model."""

    id: str
    severity: str
    title: str
    description: Optional[str] = None


@dataclass
class VulnerabilityScore:
    """Vulnerability score calculation."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0

    @property
    def total_score(self) -> int:
        """Calculate total weighted score."""
        return self.critical * 100 + self.high * 10 + self.medium * 5 + self.low * 1
