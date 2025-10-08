"""
CursorFlow - AI-guided universal testing framework

Simple data collection engine that enables Cursor to autonomously test UI 
and iterate on designs with immediate visual feedback.

Declarative Actions | Batch Execution | Universal Log Collection | Visual Development
"""

from pathlib import Path

# Main API - clean and simple
from .core.cursorflow import CursorFlow

# Core components (for advanced usage)
from .core.browser_engine import BrowserEngine
from .core.log_monitor import LogMonitor
from .core.error_correlator import ErrorCorrelator

def _get_version():
    """Get version from pyproject.toml or fallback to default"""
    try:
        # Try to read from pyproject.toml first (most reliable)
        import tomllib
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, 'rb') as f:
                data = tomllib.load(f)
                return data["project"]["version"]
    except Exception:
        pass
    
    try:
        # Try toml library as fallback (for older Python)
        import toml
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, 'r') as f:
                data = toml.load(f)
                return data["project"]["version"]
    except Exception:
        pass
    
    try:
        # Try git tag as final option
        import subprocess
        result = subprocess.run(
            ['git', 'describe', '--tags', '--exact-match'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            return result.stdout.strip().lstrip('v')
    except Exception:
        pass
    
    # Fallback version - should match pyproject.toml
    return "2.2.8"

__version__ = _get_version()
__author__ = "GeekWarrior Development"

# Simple public API
__all__ = [
    "CursorFlow",        # Main interface for Cursor
    "BrowserEngine",     # Advanced browser control
    "LogMonitor",        # Advanced log monitoring
    "ErrorCorrelator",   # Advanced correlation analysis
    "check_for_updates", # Update checking
    "update_cursorflow", # Update management
]

# Update functions (for programmatic access)
def check_for_updates(project_dir: str = "."):
    """Check for CursorFlow updates"""
    import asyncio
    from .updater import check_updates
    return asyncio.run(check_updates(project_dir))

def update_cursorflow(project_dir: str = ".", force: bool = False):
    """Update CursorFlow package and rules"""
    import asyncio
    from .updater import update_cursorflow as _update
    return asyncio.run(_update(project_dir, force=force))
