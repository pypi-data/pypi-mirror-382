class MayaBrewException(Exception):
    """Base class for all MayaBrew exceptions."""

    pass


class MayaBrewAttributeError(MayaBrewException, AttributeError):
    """Raised when there is an attribute-related error in MayaBrew."""

    pass
