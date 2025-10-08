from .utils import extract_function_call_json, evaluate_function_call
import json
from pathlib import Path
from typing import no_type_check


class ToolExecutionError(Exception):
    """Base exception for tool execution errors."""


class ValidationError(Exception):
    """Exception raised when input validation fails."""


class AuthenticationError(Exception):
    """Exception raised when authentication fails."""


class RateLimitError(Exception):
    """Exception raised when API rate limit is exceeded."""


class BaseTool:
    def __init__(self, tool_config):
        self.tool_config = self._apply_defaults(tool_config)

    @classmethod
    def get_default_config_file(cls):
        """
        Get the path to the default configuration file for this tool type.

        This method uses a robust path resolution strategy that works across
        different installation scenarios:

        1. Installed packages: Uses importlib.resources for proper package
           resource access
        2. Development mode: Falls back to file-based path resolution
        3. Legacy Python: Handles importlib.resources and importlib_resources

        Override this method in subclasses to specify a custom defaults file.

        Returns:
            Path or resource object pointing to the defaults file
        """
        tool_type = cls.__name__

        # Use importlib.resources for robust path resolution across different
        # installation methods
        try:
            import importlib.resources as pkg_resources
        except ImportError:
            # Fallback for Python < 3.9
            import importlib_resources as pkg_resources

        try:
            # Try to use package resources first (works with installed
            # packages). Use the newer files() API
            data_files = pkg_resources.files("tooluniverse.data")
            defaults_file = data_files / f"{tool_type.lower()}_defaults.json"

            # For compatibility, convert to a regular Path if possible
            if hasattr(defaults_file, "resolve"):
                return defaults_file.resolve()
            else:
                # For older Python versions or special cases, return resource
                # path
                return defaults_file

        except (FileNotFoundError, ModuleNotFoundError, AttributeError):
            # Fallback to file-based path resolution for development/local use
            current_dir = Path(__file__).parent
            defaults_file = current_dir / "data" / f"{tool_type.lower()}_defaults.json"
            return defaults_file

    @classmethod
    def load_defaults_from_file(cls):
        """Load defaults from the configuration file"""
        defaults_file = cls.get_default_config_file()

        # Handle both regular Path objects and importlib resource objects
        try:
            # Check if it's a regular Path object
            if hasattr(defaults_file, "exists") and not defaults_file.exists():
                return {}

            # Try to read the file (works for both Path and resource objects)
            if hasattr(defaults_file, "read_text"):
                # Resource object with read_text method
                content = defaults_file.read_text(encoding="utf-8")
                data = json.loads(content)
            else:
                # Regular file path
                with open(defaults_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

            # Look for defaults under the tool type key
            tool_type = cls.__name__
            return data.get(f"{tool_type.lower()}_defaults", {})

        except (FileNotFoundError, json.JSONDecodeError):
            # File doesn't exist or invalid JSON, return empty defaults
            return {}
        except Exception as e:
            print(f"Warning: Could not load defaults for {cls.__name__}: {e}")
            return {}

    def _apply_defaults(self, tool_config):
        """Apply default configuration to the tool config"""
        # Load defaults from file
        defaults = self.load_defaults_from_file()

        if not defaults:
            # No defaults available, return original config
            return tool_config

        # Create merged configuration by starting with defaults
        merged_config = defaults.copy()

        # Override with tool-specific configuration
        merged_config.update(tool_config)

        return merged_config

    @no_type_check
    def run(self, arguments=None):
        """Execute the tool.

        The default BaseTool implementation accepts an optional arguments
        mapping to align with most concrete tool implementations which expect
        a dictionary of inputs.
        """

    def check_function_call(self, function_call_json):
        if isinstance(function_call_json, str):
            function_call_json = extract_function_call_json(function_call_json)
        if function_call_json is not None:
            return evaluate_function_call(self.tool_config, function_call_json)
        else:
            return False, "Invalid JSON string of function call"

    def get_required_parameters(self):
        """
        Retrieve required parameters from the endpoint definition.
        Returns:
        list: List of required parameters for the given endpoint.
        """
        required_params = []
        parameters = self.tool_config.get("parameter", {}).get("properties", {})

        # Check each parameter to see if it is required
        for param, details in parameters.items():
            if details.get("required", False):
                required_params.append(param.lower())

        return required_params
