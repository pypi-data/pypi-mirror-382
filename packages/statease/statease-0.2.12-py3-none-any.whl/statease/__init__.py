"""statease

A python package to connect to Stat-Ease software products.

"""

__all__ = [ "statease" ]

from .client import SEClient

def connect():
    """Creates a connection to Stat-Ease 360.

    :rtype: statease.client.SEClient

    :Example:
        >>> import statease as se
        >>> se_conn = se.connect()
    """
    return SEClient()
