from importlib.metadata import PackageNotFoundError, version


def getv():
    try:
        return version("tcubed")
    except PackageNotFoundError:
        return None


__version__ = getv()
