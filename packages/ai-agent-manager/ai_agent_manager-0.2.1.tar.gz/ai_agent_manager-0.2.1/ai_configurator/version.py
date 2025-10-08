"""Project version and metadata."""
from pathlib import Path
import sys

# Use tomllib for Python 3.11+, tomli for older versions
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


def get_project_metadata():
    """Read project metadata from pyproject.toml.
    
    Returns:
        dict with 'name' and 'version' keys
    """
    if tomllib is None:
        # No TOML parser available
        return {"name": "AI Agent Manager", "version": "0.2.0"}
    
    try:
        # Find pyproject.toml (should be in package parent directory)
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        
        if not pyproject_path.exists():
            # Fallback for installed package
            return {"name": "AI Agent Manager", "version": "0.2.0"}
        
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            
        project = data.get("project", {})
        name = project.get("name", "ai-agent-manager").replace("-", " ").title()
        version = project.get("version", "0.0.0")
        
        return {"name": name, "version": version}
    except Exception:
        # Fallback if anything goes wrong
        return {"name": "AI Agent Manager", "version": "0.2.0"}


# Module-level constants
_metadata = get_project_metadata()
__version__ = _metadata["version"]
__title__ = f"{_metadata['name']} v{_metadata['version']}"
