class ConfigError(Exception):
    """Base config loader error."""


class EnvVarNotSetError(ConfigError):
    """Raised when an expected env var is not set and no default provided."""


class InvalidURLError(ConfigError):
    """Raised when a provided value is not a valid URL."""
