__all__ = ['__version__', 'version_info']


def _fetchVersion():
    import json
    import os

    HERE = os.path.abspath(os.path.dirname(__file__))

    for d, _, _ in os.walk(HERE):
        try:
            with open(os.path.join(d, 'package.json')) as f:
                return json.load(f)['version']
        except FileNotFoundError:
            pass

    raise FileNotFoundError('Could not find package.json under dir {}'.format(HERE))


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


__version__ = _fetchVersion()
version_info = _to_version_info(__version__)
