class CivError(Exception):
    """An actionable error suitable for the public command interface."""


class SourceDataError(CivError):
    """A trusted source cannot be decoded; do not penalize a submitted detector."""
