from _typeshed import Incomplete

logger: Incomplete

def load_local_env(override: bool = True) -> None:
    """Load .env from the current working directory or its parents.

    Args:
        override: Whether to override existing environment variables.
    """
