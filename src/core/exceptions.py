"""Domain exceptions for Urban Road Encroachment Detection System."""


class EncroachmentSystemError(Exception):
    """Base exception for the encroachment detection system."""

    pass


class MissingReferenceDataError(EncroachmentSystemError):
    """Raised when required cadastral parcel or road ROW reference geometry is missing."""

    def __init__(self, message: str = "Missing reference geometry layer."):
        super().__init__(message)


class InvalidGeometryError(EncroachmentSystemError):
    """Raised when input polygon geometry is invalid, unclosed, or empty."""

    def __init__(self, message: str = "Invalid geometry provided."):
        super().__init__(message)


class TransformError(EncroachmentSystemError):
    """Raised when coordinate transformation matrix operation fails or is singular."""

    def __init__(self, message: str = "Coordinate transformation matrix error."):
        super().__init__(message)
