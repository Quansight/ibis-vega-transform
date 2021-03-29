# Constants
def _to_version_info(version):
    """Convert a version string to a number and string tuple."""
    parts = []
    for part in version.split("."):
        try:
            part = int(part)
        except ValueError:
            pass

        parts.append(part)

    return tuple(parts)


__version__ = "5.2.2"
version_info = _to_version_info(__version__)
