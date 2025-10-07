"""
LogWriter Contract for LogForge Django

Interface that all audit log writers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class LogWriter(ABC):
    """Abstract base class for audit log writers."""
    
    @abstractmethod
    def write(self, record: Dict[str, Any]) -> None:
        """Persist an audit log record."""
        pass
