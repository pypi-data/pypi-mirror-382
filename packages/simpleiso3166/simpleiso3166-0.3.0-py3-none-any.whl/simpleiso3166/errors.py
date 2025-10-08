class BaseSimpleIsoError(Exception):
    """
    Base error for all errors from the library
    """


class NoCountryBestNameError(BaseSimpleIsoError):
    """
    The country has neither common_name, name nor official name
    """
