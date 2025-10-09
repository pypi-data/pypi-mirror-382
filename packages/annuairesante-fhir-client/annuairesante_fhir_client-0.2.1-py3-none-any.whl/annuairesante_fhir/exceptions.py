"""Exceptions for Annuaire Santé FHIR client."""


class AnnuaireSanteError(Exception):
    """Base exception for Annuaire Santé client."""

    pass


class AuthenticationError(AnnuaireSanteError):
    """Raised when authentication fails."""

    pass


class NotFoundError(AnnuaireSanteError):
    """Raised when a resource is not found (HTTP 404)."""

    pass


class ValidationError(AnnuaireSanteError):
    """Raised when request validation fails (HTTP 400)."""

    pass


class RateLimitError(AnnuaireSanteError):
    """Raised when rate limit is exceeded (HTTP 429)."""

    pass


class ServerError(AnnuaireSanteError):
    """Raised when server returns 5xx error."""

    pass


class FHIRError(AnnuaireSanteError):
    """Raised when FHIR resource parsing/validation fails."""

    pass
