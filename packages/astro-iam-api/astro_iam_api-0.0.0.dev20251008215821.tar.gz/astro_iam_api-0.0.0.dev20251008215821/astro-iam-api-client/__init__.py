"""A client library for accessing Astro Identity and Access Management (IAM) API"""

from .client import AuthenticatedClient, Client

__all__ = (
    "AuthenticatedClient",
    "Client",
)
