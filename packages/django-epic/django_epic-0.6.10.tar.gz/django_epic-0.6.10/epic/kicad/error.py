class Error(Exception):
    """Used for exceptions raised by the kicad package."""


class UnknownFlavorsError(Error):
    """Receives two argumets: a list of unknown flavors and a list of
    detected flavors."""
